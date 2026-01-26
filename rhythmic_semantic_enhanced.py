"""
Enhanced Rhythmic Semantic Visualization Paradigm
==================================================
Full-featured version with EEG triggers, logging, and experimental controls.

Author: A. Tates (JP)
BCI-NE Lab, University of Essex
Date: January 26, 2026
"""

from psychopy import visual, core, sound, event, parallel
import numpy as np
import json
from datetime import datetime
from pathlib import Path

# Try to import experiment_config if available
try:
    from experiment_config import *
    print("Loaded configuration from experiment_config.py")
except ImportError:
    print("experiment_config.py not found. Using default parameters.")
    # Default parameters
    CONCEPTS_CATEGORY_A = ['hand', 'foot', 'elbow', 'knee']
    CONCEPTS_CATEGORY_B = ['apple', 'banana', 'carrot', 'tomato']
    FIXATION_DURATION = 2.0
    PROMPT_DURATION = 2.0
    BEEP_INTERVAL = 0.8
    N_BEEPS = 8
    REST_DURATION = 1.0
    INTER_TRIAL_INTERVAL = 0.5
    N_TRIALS = 20
    WINDOW_SIZE = (1024, 768)
    FULLSCREEN = False
    SAVE_TRIAL_DATA = True
    OUTPUT_FILENAME = 'semantic_viz_trial_data.npy'

# =============================================================================
# EEG TRIGGER CONFIGURATION
# =============================================================================

# Set to True if you have parallel port for EEG triggers
USE_EEG_TRIGGERS = False  
PARALLEL_PORT_ADDRESS = 0x0378  # Standard LPT1 address (change if needed)

# Trigger codes (adjust based on your EEG system)
TRIGGER_CODES = {
    'fixation': 1,
    'concept_category_a': 10,
    'concept_category_b': 20,
    'beep_start': 30,
    'beep': 31,
    'trial_end': 40,
    'block_start': 50,
    'block_end': 51
}

# =============================================================================
# EXPERIMENTAL CLASS
# =============================================================================

class SemanticVisualizationExperiment:
    """
    Main experiment class handling all aspects of the paradigm.
    """
    
    def __init__(self, participant_id='test', session_id=1, use_triggers=False):
        """
        Initialize the experiment.
        
        Parameters
        ----------
        participant_id : str
            Unique identifier for participant
        session_id : int
            Session number
        use_triggers : bool
            Whether to use EEG triggers
        """
        self.participant_id = participant_id
        self.session_id = session_id
        self.use_triggers = use_triggers
        
        # Initialize trigger system
        if self.use_triggers:
            try:
                self.parallel_port = parallel.ParallelPort(address=PARALLEL_PORT_ADDRESS)
                print(f"Parallel port initialized at {hex(PARALLEL_PORT_ADDRESS)}")
            except:
                print("Warning: Could not initialize parallel port. Triggers disabled.")
                self.use_triggers = False
                self.parallel_port = None
        else:
            self.parallel_port = None
        
        # Create window
        self.win = visual.Window(
            size=WINDOW_SIZE,
            color=BACKGROUND_COLOR,
            units='height',
            fullscr=FULLSCREEN
        )
        
        # Create stimuli
        self._create_stimuli()
        
        # Create clocks
        self.clock = core.Clock()
        self.experiment_clock = core.Clock()
        
        # Data storage
        self.trial_data = []
        self.metadata = {
            'participant_id': participant_id,
            'session_id': session_id,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': datetime.now().strftime('%H:%M:%S'),
            'concepts_category_a': CONCEPTS_CATEGORY_A,
            'concepts_category_b': CONCEPTS_CATEGORY_B,
            'n_trials': N_TRIALS,
            'timing': {
                'fixation': FIXATION_DURATION,
                'prompt': PROMPT_DURATION,
                'beep_interval': BEEP_INTERVAL,
                'n_beeps': N_BEEPS,
                'rest': REST_DURATION
            }
        }
    
    def _create_stimuli(self):
        """Create all visual and auditory stimuli."""
        # Visual stimuli
        self.fixation = visual.TextStim(
            self.win,
            text='+',
            height=FIXATION_HEIGHT,
            color=TEXT_COLOR
        )
        
        self.concept_text = visual.TextStim(
            self.win,
            text='',
            height=TEXT_HEIGHT,
            color=TEXT_COLOR,
            bold=BOLD_TEXT
        )
        
        self.instruction_text = visual.TextStim(
            self.win,
            text=INSTRUCTION_TEXT,
            height=0.04,
            color=TEXT_COLOR,
            wrapWidth=0.8
        )
        
        # Progress indicator
        self.progress_text = visual.TextStim(
            self.win,
            text='',
            height=0.03,
            color='gray',
            pos=(0, -0.4)
        )
        
        # Audio stimulus
        try:
            self.beep = sound.Sound(value=BEEP_FREQUENCY, secs=BEEP_DURATION)
        except:
            print("Using default sound 'A'")
            self.beep = sound.Sound('A', octave=4, secs=BEEP_DURATION)
    
    def send_trigger(self, trigger_code):
        """
        Send EEG trigger and log timestamp.
        
        Parameters
        ----------
        trigger_code : int
            Trigger code to send
        """
        timestamp = self.clock.getTime()
        
        if self.use_triggers and self.parallel_port:
            try:
                self.parallel_port.setData(trigger_code)
                core.wait(0.01)  # Hold trigger for 10ms
                self.parallel_port.setData(0)  # Reset
            except:
                print(f"Warning: Failed to send trigger {trigger_code}")
        
        return timestamp
    
    def create_trial_sequence(self):
        """
        Create balanced trial sequence.
        
        Returns
        -------
        trials : list of dict
            List of trial specifications
        """
        trials = []
        
        for trial_idx in range(N_TRIALS):
            # Alternate between categories
            if trial_idx % 2 == 0:
                category = 'A'
                concepts = CONCEPTS_CATEGORY_A
            else:
                category = 'B'
                concepts = CONCEPTS_CATEGORY_B
            
            # Select concept (randomly or sequentially)
            if hasattr(self, 'RANDOMIZE_CONCEPTS') and RANDOMIZE_CONCEPTS:
                concept = np.random.choice(concepts)
            else:
                concept = concepts[trial_idx // 2 % len(concepts)]
            
            trials.append({
                'trial_num': trial_idx + 1,
                'concept': concept,
                'category': category
            })
        
        return trials
    
    def show_instructions(self):
        """Display instructions and wait for spacebar."""
        self.instruction_text.draw()
        self.win.flip()
        
        keys = event.waitKeys(keyList=['space', 'escape'])
        if 'escape' in keys:
            self.quit()
        
        core.wait(0.5)
    
    def run_practice_trial(self, concept='practice', category='A'):
        """
        Run a practice trial with on-screen guidance.
        
        Parameters
        ----------
        concept : str
            Concept to visualize
        category : str
            Category label
        """
        # Show practice label
        practice_label = visual.TextStim(
            self.win,
            text='PRACTICE TRIAL',
            height=0.05,
            color='yellow',
            pos=(0, 0.4)
        )
        
        # Fixation
        self.fixation.draw()
        practice_label.draw()
        self.win.flip()
        core.wait(FIXATION_DURATION)
        
        # Concept
        self.concept_text.text = concept
        self.concept_text.draw()
        practice_label.draw()
        self.win.flip()
        core.wait(PROMPT_DURATION)
        
        # Beeps with countdown
        for beep_idx in range(N_BEEPS):
            countdown_text = visual.TextStim(
                self.win,
                text=f'Visualizing... {N_BEEPS - beep_idx}',
                height=0.05,
                color='gray',
                pos=(0, 0)
            )
            countdown_text.draw()
            practice_label.draw()
            self.win.flip()
            
            self.beep.stop()
            self.beep.play()
            core.wait(BEEP_INTERVAL)
        
        # Rest
        practice_label.draw()
        self.win.flip()
        core.wait(REST_DURATION)
    
    def run_trial(self, trial_spec):
        """
        Run a single experimental trial.
        
        Parameters
        ----------
        trial_spec : dict
            Trial specification with concept, category, trial_num
        
        Returns
        -------
        trial_data : dict
            Complete trial data with all timestamps
        """
        concept = trial_spec['concept']
        category = trial_spec['category']
        trial_num = trial_spec['trial_num']
        
        trial_data = {
            'trial_num': trial_num,
            'concept': concept,
            'category': category,
            'timestamps': {}
        }
        
        print(f"\nTrial {trial_num}/{N_TRIALS}: {concept} (Category {category})")
        
        # 1. FIXATION
        self.fixation.draw()
        self.win.flip()
        trial_data['timestamps']['fixation'] = self.send_trigger(TRIGGER_CODES['fixation'])
        core.wait(FIXATION_DURATION)
        
        # 2. CONCEPT PRESENTATION
        self.concept_text.text = concept
        self.concept_text.draw()
        
        # Optional: Show progress
        if hasattr(self, 'show_progress') and self.show_progress:
            self.progress_text.text = f"Trial {trial_num}/{N_TRIALS}"
            self.progress_text.draw()
        
        self.win.flip()
        
        # Send category-specific trigger
        if category == 'A':
            trial_data['timestamps']['concept'] = self.send_trigger(TRIGGER_CODES['concept_category_a'])
        else:
            trial_data['timestamps']['concept'] = self.send_trigger(TRIGGER_CODES['concept_category_b'])
        
        core.wait(PROMPT_DURATION)
        
        # 3. RHYTHMIC BEEP SEQUENCE
        self.win.flip()  # Clear screen
        trial_data['timestamps']['beep_start'] = self.send_trigger(TRIGGER_CODES['beep_start'])
        trial_data['timestamps']['beeps'] = []
        
        for beep_idx in range(N_BEEPS):
            beep_time = self.send_trigger(TRIGGER_CODES['beep'])
            trial_data['timestamps']['beeps'].append(beep_time)
            
            self.beep.stop()
            self.beep.play()
            
            print(f"  Beep {beep_idx + 1}/{N_BEEPS} at {beep_time:.3f}s")
            core.wait(BEEP_INTERVAL)
        
        # 4. REST PERIOD
        self.win.flip()
        trial_data['timestamps']['rest'] = self.send_trigger(TRIGGER_CODES['trial_end'])
        core.wait(REST_DURATION)
        
        return trial_data
    
    def run_experiment(self, n_practice_trials=2):
        """
        Run the complete experiment.
        
        Parameters
        ----------
        n_practice_trials : int
            Number of practice trials before main experiment
        """
        # Instructions
        self.show_instructions()
        
        # Practice trials
        if n_practice_trials > 0:
            practice_text = visual.TextStim(
                self.win,
                text=f"Let's do {n_practice_trials} practice trial(s) first.\n\nPress SPACE to continue.",
                height=0.05,
                color=TEXT_COLOR
            )
            practice_text.draw()
            self.win.flip()
            event.waitKeys(keyList=['space'])
            
            for i in range(n_practice_trials):
                concept = CONCEPTS_CATEGORY_A[0] if i % 2 == 0 else CONCEPTS_CATEGORY_B[0]
                category = 'A' if i % 2 == 0 else 'B'
                self.run_practice_trial(concept, category)
                
                if i < n_practice_trials - 1:
                    core.wait(1.0)
        
        # Ready screen
        ready_text = visual.TextStim(
            self.win,
            text="Practice complete!\n\nThe main experiment will now begin.\n\nPress SPACE when ready.",
            height=0.05,
            color=TEXT_COLOR
        )
        ready_text.draw()
        self.win.flip()
        event.waitKeys(keyList=['space'])
        
        # Create trial sequence
        trials = self.create_trial_sequence()
        
        # Start experiment
        print("\n" + "="*60)
        print("STARTING MAIN EXPERIMENT")
        print("="*60)
        
        self.experiment_clock.reset()
        self.send_trigger(TRIGGER_CODES['block_start'])
        
        # Run all trials
        for trial_spec in trials:
            trial_data = self.run_trial(trial_spec)
            self.trial_data.append(trial_data)
            
            # Inter-trial interval
            if trial_spec['trial_num'] < N_TRIALS:
                core.wait(INTER_TRIAL_INTERVAL)
            
            # Check for escape
            keys = event.getKeys(keyList=['escape'])
            if 'escape' in keys:
                print("\nExperiment terminated by user.")
                break
        
        self.send_trigger(TRIGGER_CODES['block_end'])
        
        # End screen
        end_text = visual.TextStim(
            self.win,
            text="Experiment Complete!\n\nThank you for participating.\n\nPress SPACE to finish.",
            height=0.06,
            color=TEXT_COLOR
        )
        end_text.draw()
        self.win.flip()
        event.waitKeys(keyList=['space'])
        
        # Save data
        self.save_data()
        
        return self.trial_data
    
    def save_data(self):
        """Save trial data and metadata to files."""
        if not SAVE_TRIAL_DATA:
            return
        
        # Create output directory
        output_dir = Path('experiment_data')
        output_dir.mkdir(exist_ok=True)
        
        # Generate filenames with participant info
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_filename = f"sub-{self.participant_id}_ses-{self.session_id}_{timestamp}"
        
        # Save trial data
        trial_data_file = output_dir / f"{base_filename}_trials.json"
        with open(trial_data_file, 'w') as f:
            json.dump({
                'metadata': self.metadata,
                'trials': self.trial_data
            }, f, indent=2)
        
        print(f"\nData saved to: {trial_data_file}")
        
        # Also save as numpy for easy loading
        np_file = output_dir / f"{base_filename}_trials.npy"
        np.save(np_file, self.trial_data, allow_pickle=True)
        
        # Print summary
        print("\n" + "="*60)
        print("EXPERIMENT SUMMARY")
        print("="*60)
        total_duration = self.experiment_clock.getTime()
        print(f"Participant: {self.participant_id}")
        print(f"Session: {self.session_id}")
        print(f"Total duration: {total_duration:.2f}s ({total_duration/60:.2f}min)")
        print(f"Trials completed: {len(self.trial_data)}/{N_TRIALS}")
    
    def quit(self):
        """Clean shutdown."""
        self.win.close()
        core.quit()

# =============================================================================
# MAIN EXECUTION
# =============================================================================

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
