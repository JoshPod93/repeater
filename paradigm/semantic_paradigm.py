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
        
        # 3. RHYTHMIC BEEP SEQUENCE
        self.display.clear_screen()
        timestamp, _ = self.trigger_handler.send_trigger(
            TRIGGER_CODES['beep_start'],
            event_name='beep_start'
        )
        trial_data['timestamps']['beep_start'] = timestamp
        trial_data['timestamps']['beeps'] = []
        
        n_beeps = self.config.get('N_BEEPS', 8)
        beep_interval = self.config.get('BEEP_INTERVAL', 0.8)  # NO JITTER - critical rhythmic timing
        
        for beep_idx in range(n_beeps):
            timestamp, _ = self.trigger_handler.send_trigger(
                TRIGGER_CODES['beep'],
                event_name=f'beep_{beep_idx + 1}_{n_beeps}'
            )
            trial_data['timestamps']['beeps'].append(timestamp)
            
            # Play beep using utility function
            play_beep(self.beep, stop_first=True)
            
            print(f"  Beep {beep_idx + 1}/{n_beeps} at {timestamp:.3f}s")
            core.wait(beep_interval)  # Fixed interval - critical for rhythmic protocol
        
        # 4. REST PERIOD
        self.display.clear_screen()
        timestamp, _ = self.trigger_handler.send_trigger(
            TRIGGER_CODES['trial_end'],
            event_name='trial_end'
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
    
    def run_practice_trial(self, concept: str = 'practice', category: str = 'A'):
        """Run a practice trial with visual feedback."""
        use_jitter = self.config.get('USE_JITTER', True)
        jitter_range = self.config.get('JITTER_RANGE', 0.1)
        
        # Show practice label
        self.display.show_text('PRACTICE TRIAL', height=0.05, color='yellow')
        core.wait(0.5)
        
        # Fixation (NO JITTER - important timing)
        self.display.show_fixation()
        core.wait(self.config.get('FIXATION_DURATION', 2.0))
        
        # Concept (NO JITTER - important timing)
        self.display.show_concept(concept)
        core.wait(self.config.get('PROMPT_DURATION', 2.0))
        
        # Clear concept and pause before beeps (JITTERED - pause event)
        self.display.clear_screen()
        post_concept_pause = self.config.get('POST_CONCEPT_PAUSE', 1.0)
        core.wait(jittered_wait(post_concept_pause, jitter_range) if use_jitter else post_concept_pause)
        
        # Beeps with countdown (NO JITTER - critical rhythmic timing)
        n_beeps = self.config.get('N_BEEPS', 8)
        beep_interval = self.config.get('BEEP_INTERVAL', 0.8)  # Fixed - critical for rhythm
        
        for beep_idx in range(n_beeps):
            countdown = f'Visualizing... {n_beeps - beep_idx}'
            self.display.show_text(countdown, height=0.05, color='gray')
            
            # Play beep using utility function
            play_beep(self.beep, stop_first=True)
            
            # Fixed interval - NO JITTER (critical for rhythmic protocol)
            core.wait(beep_interval)
        
        # Rest (JITTERED - pause event)
        self.display.clear_screen()
        rest_duration = self.config.get('REST_DURATION', 1.0)
        core.wait(jittered_wait(rest_duration, jitter_range) if use_jitter else rest_duration)
    
    def run_experiment(self, n_practice_trials: int = 2):
        """Run the complete experiment."""
        # Show warning and countdown
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
            
            self.display.show_text(f"Starting in {count}...", height=0.08, color='white')
            core.wait(1.0)
        
        # Practice trials
        if n_practice_trials > 0:
            concepts_a = self.config.get('CONCEPTS_CATEGORY_A', [])
            concepts_b = self.config.get('CONCEPTS_CATEGORY_B', [])
            
            for i in range(n_practice_trials):
                # Check for escape
                keys = event.getKeys(keyList=['escape'])
                if 'escape' in keys:
                    print("\n[EXIT] Experiment terminated by user (Escape key)")
                    self.quit()
                    return
                
                concept = concepts_a[0] if i % 2 == 0 else concepts_b[0]
                category = 'A' if i % 2 == 0 else 'B'
                self.run_practice_trial(concept, category)
                
                if i < n_practice_trials - 1:
                    # Jittered wait
                    use_jitter = self.config.get('USE_JITTER', True)
                    jitter_range = self.config.get('JITTER_RANGE', 0.1)
                    wait_duration = jittered_wait(1.0, jitter_range) if use_jitter else 1.0
                    core.wait(wait_duration)
        
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
        self.trigger_handler.send_trigger(
            TRIGGER_CODES['block_start'],
            event_name='block_start'
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
        
        self.trigger_handler.send_trigger(
            TRIGGER_CODES['block_end'],
            event_name='block_end'
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
        exp.run_experiment(n_practice_trials=2)
    except Exception as e:
        print(f"\nError during experiment: {e}")
        import traceback
        traceback.print_exc()
    finally:
        exp.quit()
