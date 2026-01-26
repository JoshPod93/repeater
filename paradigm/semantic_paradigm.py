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
    create_balanced_sequence, validate_trial_sequence
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
        
        # Initialize trigger handler
        port_address = self.config.get('PARALLEL_PORT_ADDRESS', 0x0378)
        self.trigger_handler = create_trigger_handler(
            port_address=port_address,
            use_triggers=use_triggers
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
        
        # Create audio stimulus
        try:
            # Try creating sound with frequency
            self.beep = sound.Sound(
                value=self.config.get('BEEP_FREQUENCY', 440),
                secs=self.config.get('BEEP_DURATION', 0.1)
            )
        except Exception as e:
            # Fallback to note-based sound
            try:
                self.beep = sound.Sound('A', octave=4, secs=self.config.get('BEEP_DURATION', 0.1))
            except Exception as e2:
                # Last resort: create minimal sound or None
                print(f"Warning: Sound creation failed: {e}, {e2}")
                self.beep = None
        
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
        
        # 1. FIXATION
        self.display.show_fixation()
        timestamp, _ = self.trigger_handler.send_trigger(TRIGGER_CODES['fixation'])
        trial_data['timestamps']['fixation'] = timestamp
        core.wait(self.config.get('FIXATION_DURATION', 2.0))
        
        # 2. CONCEPT PRESENTATION
        progress_text = f"Trial {trial_num}/{self.config.get('N_TRIALS', 20)}"
        self.display.show_concept(concept, show_progress=True, progress_text=progress_text)
        
        # Send category-specific trigger
        trigger_code = (TRIGGER_CODES['concept_category_a'] if category == 'A' 
                       else TRIGGER_CODES['concept_category_b'])
        timestamp, _ = self.trigger_handler.send_trigger(trigger_code)
        trial_data['timestamps']['concept'] = timestamp
        
        core.wait(self.config.get('PROMPT_DURATION', 2.0))
        
        # 3. RHYTHMIC BEEP SEQUENCE
        self.display.clear_screen()
        timestamp, _ = self.trigger_handler.send_trigger(TRIGGER_CODES['beep_start'])
        trial_data['timestamps']['beep_start'] = timestamp
        trial_data['timestamps']['beeps'] = []
        
        n_beeps = self.config.get('N_BEEPS', 8)
        beep_interval = self.config.get('BEEP_INTERVAL', 0.8)
        
        for beep_idx in range(n_beeps):
            timestamp, _ = self.trigger_handler.send_trigger(TRIGGER_CODES['beep'])
            trial_data['timestamps']['beeps'].append(timestamp)
            
            if self.beep is not None:
                self.beep.stop()
                self.beep.play()
            
            print(f"  Beep {beep_idx + 1}/{n_beeps} at {timestamp:.3f}s")
            core.wait(beep_interval)
        
        # 4. REST PERIOD
        self.display.clear_screen()
        timestamp, _ = self.trigger_handler.send_trigger(TRIGGER_CODES['trial_end'])
        trial_data['timestamps']['rest'] = timestamp
        core.wait(self.config.get('REST_DURATION', 1.0))
        
        return trial_data
    
    def run_practice_trial(self, concept: str = 'practice', category: str = 'A'):
        """Run a practice trial with visual feedback."""
        # Show practice label
        self.display.show_text('PRACTICE TRIAL', height=0.05, color='yellow')
        core.wait(0.5)
        
        # Fixation
        self.display.show_fixation()
        core.wait(self.config.get('FIXATION_DURATION', 2.0))
        
        # Concept
        self.display.show_concept(concept)
        core.wait(self.config.get('PROMPT_DURATION', 2.0))
        
        # Beeps with countdown
        n_beeps = self.config.get('N_BEEPS', 8)
        beep_interval = self.config.get('BEEP_INTERVAL', 0.8)
        
        for beep_idx in range(n_beeps):
            countdown = f'Visualizing... {n_beeps - beep_idx}'
            self.display.show_text(countdown, height=0.05, color='gray')
            
            if self.beep is not None:
                self.beep.stop()
                self.beep.play()
            core.wait(beep_interval)
        
        # Rest
        self.display.clear_screen()
        core.wait(self.config.get('REST_DURATION', 1.0))
    
    def run_experiment(self, n_practice_trials: int = 2):
        """Run the complete experiment."""
        # Instructions
        self.display.show_instructions()
        keys = event.waitKeys(keyList=['space', 'escape'])
        if 'escape' in keys:
            self.quit()
        core.wait(0.5)
        
        # Practice trials
        if n_practice_trials > 0:
            self.display.show_text(
                f"Let's do {n_practice_trials} practice trial(s) first.\n\nPress SPACE to continue.",
                height=0.05
            )
            event.waitKeys(keyList=['space'])
            
            concepts_a = self.config.get('CONCEPTS_CATEGORY_A', [])
            concepts_b = self.config.get('CONCEPTS_CATEGORY_B', [])
            
            for i in range(n_practice_trials):
                concept = concepts_a[0] if i % 2 == 0 else concepts_b[0]
                category = 'A' if i % 2 == 0 else 'B'
                self.run_practice_trial(concept, category)
                
                if i < n_practice_trials - 1:
                    core.wait(1.0)
        
        # Ready screen
        self.display.show_text(
            "Practice complete!\n\nThe main experiment will now begin.\n\nPress SPACE when ready.",
            height=0.05
        )
        event.waitKeys(keyList=['space'])
        
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
        self.trigger_handler.send_trigger(TRIGGER_CODES['block_start'])
        
        # Run all trials
        for trial_spec in trials:
            trial_data = self.run_trial(trial_spec)
            self.trial_data.append(trial_data)
            
            # Inter-trial interval
            if trial_spec['trial_num'] < self.config.get('N_TRIALS', 20):
                core.wait(self.config.get('INTER_TRIAL_INTERVAL', 0.5))
            
            # Check for escape
            keys = event.getKeys(keyList=['escape'])
            if 'escape' in keys:
                print("\nExperiment terminated by user.")
                break
        
        self.trigger_handler.send_trigger(TRIGGER_CODES['block_end'])
        
        # End screen
        self.display.show_text(
            "Experiment Complete!\n\nThank you for participating.\n\nPress SPACE to finish.",
            height=0.06
        )
        event.waitKeys(keyList=['space'])
        
        # Save data
        self.save_data()
        
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
