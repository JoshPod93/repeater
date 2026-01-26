"""
Semantic Visualization Paradigm - Main Experiment Script

Full-featured BCI experiment for semantic visualization using rhythmic protocols.
Refactored to use modular utilities following best practices.

Author: A. Tates (JP)
BCI-NE Lab, University of Essex
Date: January 26, 2026
"""

from psychopy import core, sound, event
from pathlib import Path
from datetime import datetime
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import load_config
from paradigm.utils import (
    TriggerHandler, TRIGGER_CODES, create_trigger_handler,
    get_trial_start_code, get_trial_end_code,
    get_block_start_code, get_block_end_code,
    get_beep_code, get_beep_codes,
    DisplayManager, create_window,
    create_metadata, create_trial_data_dict, save_trial_data, print_experiment_summary,
    create_balanced_sequence, validate_trial_sequence,
    create_beep_sound, play_beep,
    jittered_wait
)


class SemanticVisualizationExperiment:
    """
    Main experiment class for semantic visualization paradigm.
    
    Uses modular utilities for triggers, display, data, and randomization.
    """
    
    def __init__(self, participant_id: str = 'test', session_id: int = 1, 
                 use_triggers: bool = False, config_path: Path = None):
        """
        Initialize experiment.
        
        Parameters
        ----------
        participant_id : str
            Participant identifier
        session_id : int
            Session number
        use_triggers : bool
            Whether to use EEG triggers
        config_path : Path, optional
            Path to config file (default: config/experiment_config.py)
        """
        self.participant_id = participant_id
        self.session_id = session_id
        
        # Load configuration
        if config_path is None:
            config_path = Path(__file__).parent.parent / 'config' / 'experiment_config.py'
        self.config = load_config(str(config_path))
        
        # Initialize trigger handler with CSV logging
        port_address = self.config.get('PARALLEL_PORT_ADDRESS', 0x0378)
        
        # Set up CSV log path for trigger mirror logging
        csv_log_dir = Path(__file__).parent.parent / 'data' / 'triggers'
        csv_log_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_log_path = csv_log_dir / f"sub-{participant_id}_ses-{session_id}_{timestamp}_triggers.csv"
        
        self.trigger_handler = create_trigger_handler(
            port_address=port_address,
            use_triggers=use_triggers,
            csv_log_path=csv_log_path
        )
        
        # Create window
        self.win = create_window(
            size=self.config.get('WINDOW_SIZE', (1024, 768)),
            color=self.config.get('BACKGROUND_COLOR', 'black'),
            fullscreen=self.config.get('FULLSCREEN', False)
        )
        
        # Create display manager
        display_config = {
            'fixation_height': self.config.get('FIXATION_HEIGHT', 0.1),
            'text_height': self.config.get('TEXT_HEIGHT', 0.08),
            'text_color': self.config.get('TEXT_COLOR', 'white'),
            'bold_text': self.config.get('BOLD_TEXT', True),
            'instruction_text': self.config.get('INSTRUCTION_TEXT', '')
        }
        self.display = DisplayManager(self.win, display_config)
        
        # Create clocks
        self.clock = core.Clock()
        self.experiment_clock = core.Clock()
        
        # Create audio stimulus using utility function
        self.beep = create_beep_sound(
            frequency=self.config.get('BEEP_FREQUENCY', 440),
            duration=self.config.get('BEEP_DURATION', 0.1),
            fallback_note='A',
            octave=4
        )
        if self.beep is None:
            print("Warning: Could not create beep sound. Audio will be silent.")
        
        # Data storage
        self.trial_data = []
        self.metadata = create_metadata(
            participant_id=participant_id,
            session_id=session_id,
            config=self.config
        )
    
    def run_trial(self, trial_spec: dict) -> dict:
        """
        Run a single experimental trial.
        
        Parameters
        ----------
        trial_spec : dict
            Trial specification with 'concept', 'category', 'trial_num'
        
        Returns
        -------
        dict
            Complete trial data with timestamps
        """
        concept = trial_spec['concept']
        category = trial_spec['category']
        trial_num = trial_spec['trial_num']
        
        # Create trial data structure
        trial_data = create_trial_data_dict(trial_num, concept, category)
        
        print(f"\nTrial {trial_num}/{self.config.get('N_TRIALS', 20)}: {concept} (Category {category})")
        
        # Send trial start trigger (unique code for this trial number)
        trial_start_code = get_trial_start_code(trial_num)
        timestamp, _ = self.trigger_handler.send_trigger(
            trial_start_code,
            event_name=f'trial_{trial_num}_start'
        )
        trial_data['timestamps']['trial_start'] = timestamp
        
        # 1. FIXATION (NO JITTER - important timing)
        self.display.show_fixation()
        timestamp, _ = self.trigger_handler.send_trigger(
            TRIGGER_CODES['fixation'],
            event_name='fixation'
        )
        trial_data['timestamps']['fixation'] = timestamp
        core.wait(self.config.get('FIXATION_DURATION', 2.0))
        
        # 2. CONCEPT PRESENTATION
        progress_text = f"Trial {trial_num}/{self.config.get('N_TRIALS', 20)}"
        self.display.show_concept(concept, show_progress=True, progress_text=progress_text)
        
        # Send category-specific trigger
        trigger_code = (TRIGGER_CODES['concept_category_a'] if category == 'A' 
                       else TRIGGER_CODES['concept_category_b'])
        event_name = f'concept_{concept}_category_{category}'
        timestamp, _ = self.trigger_handler.send_trigger(trigger_code, event_name=event_name)
        trial_data['timestamps']['concept'] = timestamp
        
        core.wait(self.config.get('PROMPT_DURATION', 2.0))
        
        # Clear concept display
        self.display.clear_screen()
        
        # PAUSE AFTER CONCEPT DISAPPEARS (before beeps start)
        use_jitter = self.config.get('USE_JITTER', True)
        jitter_range = self.config.get('JITTER_RANGE', 0.1)
        post_concept_pause = self.config.get('POST_CONCEPT_PAUSE', 1.0)
        
        if use_jitter:
            pause_duration = jittered_wait(post_concept_pause, jitter_range)
        else:
            pause_duration = post_concept_pause
        
        core.wait(pause_duration)
        
        # Show fixation cross (stays on during beeps)
        self.display.show_fixation()
        
        # 3. RHYTHMIC BEEP SEQUENCE (fixation stays on screen)
        timestamp, _ = self.trigger_handler.send_trigger(
            TRIGGER_CODES['beep_start'],
            event_name='beep_start'
        )
        trial_data['timestamps']['beep_start'] = timestamp
        trial_data['timestamps']['beeps'] = []
        
        n_beeps = self.config.get('N_BEEPS', 8)
        beep_interval = self.config.get('BEEP_INTERVAL', 0.8)  # NO JITTER - critical rhythmic timing
        
        # Get beep trigger codes dynamically based on n_beeps
        beep_trigger_codes = get_beep_codes(n_beeps, max_beeps=8)
        
        for beep_idx in range(n_beeps):
            # Redraw fixation (keeps it visible during beeps)
            self.display.show_fixation()
            
            # Use dynamic beep code
            trigger_code = beep_trigger_codes[beep_idx]
            timestamp, _ = self.trigger_handler.send_trigger(
                trigger_code,
                event_name=f'beep_{beep_idx + 1}_{n_beeps}'
            )
            trial_data['timestamps']['beeps'].append(timestamp)
            
            # Play beep using utility function
            play_beep(self.beep, stop_first=True)
            
            print(f"  Beep {beep_idx + 1}/{n_beeps} (trigger {trigger_code}) at {timestamp:.3f}s")
            
            # Fixed interval - critical for rhythmic protocol
            # 0.8s interval provides sufficient buffer time between triggers
            core.wait(beep_interval)
        
        # 4. REST PERIOD
        self.display.clear_screen()
        
        # Send trial end trigger (unique code for this trial number)
        trial_end_code = get_trial_end_code(trial_num)
        timestamp, _ = self.trigger_handler.send_trigger(
            trial_end_code,
            event_name=f'trial_{trial_num}_end'
        )
        trial_data['timestamps']['rest'] = timestamp
        
        # Jittered rest duration
        use_jitter = self.config.get('USE_JITTER', True)
        jitter_range = self.config.get('JITTER_RANGE', 0.1)
        rest_duration = self.config.get('REST_DURATION', 1.0)
        
        if use_jitter:
            wait_duration = jittered_wait(rest_duration, jitter_range)
        else:
            wait_duration = rest_duration
        
        core.wait(wait_duration)
        
        return trial_data
    
    def run_experiment(self):
        """Run the complete experiment."""
        # Clear screen and show warning
        self.display.clear_screen()
        core.wait(0.1)  # Brief pause to ensure screen is cleared
        warning_text = "WARNING: Experiment starting soon.\n\nPlease remain still and focus.\n\nPress ESCAPE to exit."
        self.display.show_text(warning_text, height=0.05, color='yellow')
        core.wait(2.0)  # Show warning for 2 seconds
        
        # Countdown from 3
        for count in [3, 2, 1]:
            # Check for escape during countdown
            keys = event.getKeys(keyList=['escape'])
            if 'escape' in keys:
                print("\n[EXIT] Experiment terminated by user (Escape key)")
                self.quit()
                return
            
            # Clear screen before showing countdown
            self.display.clear_screen()
            core.wait(0.1)  # Brief pause to ensure screen is cleared
            self.display.show_text(f"Starting in {count}...", height=0.08, color='white')
            core.wait(1.0)
        
        # Clear screen before experiment starts
        self.display.clear_screen()
        core.wait(0.1)
        
        # Create trial sequence
        trials = create_balanced_sequence(
            n_trials=self.config.get('N_TRIALS', 20),
            concepts_a=self.config.get('CONCEPTS_CATEGORY_A', []),
            concepts_b=self.config.get('CONCEPTS_CATEGORY_B', []),
            randomize=self.config.get('RANDOMIZE_CONCEPTS', True)
        )
        
        # Validate sequence
        is_valid, error_msg = validate_trial_sequence(
            trials,
            self.config.get('CONCEPTS_CATEGORY_A', []),
            self.config.get('CONCEPTS_CATEGORY_B', [])
        )
        if not is_valid:
            print(f"Warning: {error_msg}")
        
        # Start experiment
        print("\n" + "="*60)
        print("STARTING MAIN EXPERIMENT")
        print("="*60)
        
        self.experiment_clock.reset()
        
        # Send block start trigger (unique code for block number)
        block_num = 1  # Currently single block, but supports multiple
        block_start_code = get_block_start_code(block_num)
        self.trigger_handler.send_trigger(
            block_start_code,
            event_name=f'block_{block_num}_start'
        )
        
        # Run all trials
        for trial_spec in trials:
            trial_data = self.run_trial(trial_spec)
            self.trial_data.append(trial_data)
            
            # Inter-trial interval (jittered)
            if trial_spec['trial_num'] < self.config.get('N_TRIALS', 20):
                use_jitter = self.config.get('USE_JITTER', True)
                jitter_range = self.config.get('JITTER_RANGE', 0.1)
                inter_trial_interval = self.config.get('INTER_TRIAL_INTERVAL', 0.5)
                
                wait_duration = jittered_wait(inter_trial_interval, jitter_range) if use_jitter else inter_trial_interval
                core.wait(wait_duration)
            
            # Check for escape
            keys = event.getKeys(keyList=['escape'])
            if 'escape' in keys:
                print("\nExperiment terminated by user.")
                break
        
        # Send block end trigger (unique code for block number)
        block_num = 1  # Currently single block, but supports multiple
        block_end_code = get_block_end_code(block_num)
        self.trigger_handler.send_trigger(
            block_end_code,
            event_name=f'block_{block_num}_end'
        )
        
        # Save data
        self.save_data()
        
        # End screen (brief display, then auto-quit)
        self.display.show_text(
            "Experiment Complete!\n\nThank you for participating.",
            height=0.06
        )
        core.wait(2.0)  # Show completion message for 2 seconds
        
        return self.trial_data
    
    def save_data(self):
        """Save trial data and metadata."""
        if not self.config.get('SAVE_TRIAL_DATA', True):
            return
        
        output_dir = Path(__file__).parent.parent / 'data' / 'results'
        
        saved_files = save_trial_data(
            metadata=self.metadata,
            trial_data=self.trial_data,
            output_dir=output_dir,
            participant_id=self.participant_id,
            session_id=self.session_id
        )
        
        total_duration = self.experiment_clock.getTime()
        print_experiment_summary(
            metadata=self.metadata,
            trial_data=self.trial_data,
            total_duration=total_duration,
            saved_files=saved_files
        )
    
    def quit(self):
        """Clean shutdown."""
        self.trigger_handler.close()
        self.win.close()
        core.quit()


if __name__ == "__main__":
    # Get participant info
    print("="*60)
    print("SEMANTIC VISUALIZATION EXPERIMENT")
    print("="*60)
    
    participant_id = input("Enter participant ID (or press Enter for 'test'): ").strip()
    if not participant_id:
        participant_id = 'test'
    
    session_id = input("Enter session number (or press Enter for '1'): ").strip()
    if not session_id:
        session_id = 1
    else:
        session_id = int(session_id)
    
    use_triggers = input("Use EEG triggers? (y/n, default=n): ").strip().lower() == 'y'
    
    # Create and run experiment
    exp = SemanticVisualizationExperiment(
        participant_id=participant_id,
        session_id=session_id,
        use_triggers=use_triggers
    )
    
    try:
        exp.run_experiment()
    except Exception as e:
        print(f"\nError during experiment: {e}")
        import traceback
        traceback.print_exc()
    finally:
        exp.quit()
