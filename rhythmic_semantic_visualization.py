"""
Rhythmic Semantic Visualization Paradigm
=========================================
Adaptation of rhythmic speech imagery paradigm for semantic processing.
Instead of imagined speech, participants visualize concepts (body parts, fruits/vegetables).

Author: A. Tates (JP)
BCI-NE Lab, University of Essex
Date: January 26, 2026
"""

from psychopy import visual, core, sound
import random
import numpy as np

# =============================================================================
# CONFIGURATION
# =============================================================================

# --- Concept Lists ---
# You can easily modify these lists or add more categories
BODY_PARTS = ['hand', 'foot', 'elbow', 'knee', 'shoulder', 'wrist', 'ankle', 'thumb']
FRUITS_VEGETABLES = ['apple', 'banana', 'carrot', 'tomato', 'broccoli', 'orange', 'grape', 'cucumber']

# For balanced design, you can mix categories or keep them separate
# Option 1: Separate categories (easier to analyze)
CONCEPTS_CATEGORY_A = BODY_PARTS[:4]  # e.g., ['hand', 'foot', 'elbow', 'knee']
CONCEPTS_CATEGORY_B = FRUITS_VEGETABLES[:4]  # e.g., ['apple', 'banana', 'carrot', 'tomato']

# Option 2: Mixed list for variety
# CONCEPTS_CATEGORY_A = ['hand', 'foot', 'apple', 'banana']
# CONCEPTS_CATEGORY_B = ['elbow', 'knee', 'carrot', 'tomato']

# --- Timing Parameters (in seconds) ---
FIXATION_DURATION = 2.0      # Initial fixation cross
PROMPT_DURATION = 2.0        # Concept presentation
BEEP_INTERVAL = 0.8          # Stimulus Onset Asynchrony (SOA) for rhythmic beeps
N_BEEPS = 8                  # Number of beeps during visualization
REST_DURATION = 1.0          # Blank screen after trial
INTER_TRIAL_INTERVAL = 0.5   # Short break between trials

# --- Experiment Structure ---
N_TRIALS = 20                # Total number of trials
INSTRUCTION_TEXT = """
Semantic Visualization Task

You will see words representing objects or body parts.
Your task is to VISUALIZE or IMAGINE each concept as vividly as possible.

- See the object/body part in your mind
- Imagine its shape, color, texture
- Think about what it looks like from different angles

A series of beeps will play - use them to maintain your focus.

Press SPACE to begin.
"""

# --- Visual Parameters ---
WINDOW_SIZE = (1024, 768)
TEXT_HEIGHT = 0.08
FIXATION_HEIGHT = 0.1

# --- Audio Parameters ---
BEEP_FREQUENCY = 440  # Hz (A4 note)
BEEP_DURATION = 0.1   # seconds

# =============================================================================
# STIMULUS SETUP
# =============================================================================

# Create a window
win = visual.Window(
    size=WINDOW_SIZE, 
    color='black', 
    units='height',
    fullscr=False  # Set to True for actual experiments
)

# Create visual stimuli
fixation = visual.TextStim(
    win, 
    text='+', 
    height=FIXATION_HEIGHT, 
    color='white'
)

concept_text = visual.TextStim(
    win, 
    text='', 
    height=TEXT_HEIGHT, 
    color='white',
    bold=True
)

instruction_screen = visual.TextStim(
    win,
    text=INSTRUCTION_TEXT,
    height=0.04,
    color='white',
    wrapWidth=0.8
)

# Create beep sound
try:
    beep = sound.Sound(value=BEEP_FREQUENCY, secs=BEEP_DURATION)
except:
    print("Warning: Could not create sound with frequency. Using default 'A' note.")
    beep = sound.Sound('A', octave=4, secs=BEEP_DURATION)

# Create a clock for timing
clock = core.Clock()
experiment_clock = core.Clock()

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def create_trial_sequence(n_trials, concepts_a, concepts_b, randomize=True):
    """
    Create a balanced trial sequence.
    
    Parameters
    ----------
    n_trials : int
        Number of trials to generate
    concepts_a : list
        Concepts from category A
    concepts_b : list
        Concepts from category B
    randomize : bool
        Whether to randomize concept order within categories
    
    Returns
    -------
    trial_list : list of tuples
        Each tuple contains (concept, category_label)
    """
    trial_list = []
    
    # Create balanced sequence alternating between categories
    for trial_idx in range(n_trials):
        if trial_idx % 2 == 0:
            # Category A
            concept = random.choice(concepts_a) if randomize else concepts_a[trial_idx % len(concepts_a)]
            trial_list.append((concept, 'A'))
        else:
            # Category B
            concept = random.choice(concepts_b) if randomize else concepts_b[trial_idx % len(concepts_b)]
            trial_list.append((concept, 'B'))
    
    return trial_list

def show_instructions():
    """Display instruction screen and wait for spacebar."""
    instruction_screen.draw()
    win.flip()
    
    # Wait for spacebar
    keys = None
    while keys != ['space']:
        keys = visual.event.getKeys(keyList=['space', 'escape'])
        if 'escape' in keys:
            win.close()
            core.quit()
    
    core.wait(0.5)

def run_trial(concept, category, trial_num, total_trials):
    """
    Run a single trial of the semantic visualization task.
    
    Parameters
    ----------
    concept : str
        The concept to visualize
    category : str
        Category label ('A' or 'B')
    trial_num : int
        Current trial number
    total_trials : int
        Total number of trials
    
    Returns
    -------
    trial_data : dict
        Dictionary containing trial information and timing
    """
    trial_data = {
        'trial': trial_num,
        'concept': concept,
        'category': category,
        'fixation_onset': None,
        'concept_onset': None,
        'beep_onsets': [],
        'trial_offset': None
    }
    
    print(f"\nTrial {trial_num}/{total_trials}: {concept} (Category {category})")
    
    # 1. Fixation cross
    fixation.draw()
    win.flip()
    trial_data['fixation_onset'] = clock.getTime()
    core.wait(FIXATION_DURATION)
    
    # 2. Concept presentation
    concept_text.text = concept
    concept_text.draw()
    win.flip()
    trial_data['concept_onset'] = clock.getTime()
    print(f"  Concept displayed at {trial_data['concept_onset']:.3f}s")
    core.wait(PROMPT_DURATION)
    
    # 3. Rhythmic beep sequence (blank screen with audio cues)
    win.flip()  # Clear screen before beeps
    
    for beep_idx in range(N_BEEPS):
        beep_onset = clock.getTime()
        trial_data['beep_onsets'].append(beep_onset)
        
        # Play beep
        beep.stop()
        beep.play()
        
        print(f"  Beep {beep_idx + 1}/{N_BEEPS} at {beep_onset:.3f}s")
        
        # Wait for next beep (SOA)
        core.wait(BEEP_INTERVAL)
    
    # 4. Rest period (blank screen)
    win.flip()
    core.wait(REST_DURATION)
    trial_data['trial_offset'] = clock.getTime()
    
    return trial_data

# =============================================================================
# MAIN EXPERIMENT
# =============================================================================

def run_experiment():
    """Main experimental loop."""
    
    # Show instructions
    show_instructions()
    
    # Create trial sequence
    print("\n" + "="*60)
    print("CREATING TRIAL SEQUENCE")
    print("="*60)
    
    trial_sequence = create_trial_sequence(
        N_TRIALS, 
        CONCEPTS_CATEGORY_A, 
        CONCEPTS_CATEGORY_B,
        randomize=True
    )
    
    # Print trial plan
    print(f"\nTotal trials: {N_TRIALS}")
    print(f"Category A concepts: {CONCEPTS_CATEGORY_A}")
    print(f"Category B concepts: {CONCEPTS_CATEGORY_B}")
    print("\nTrial sequence:")
    for idx, (concept, category) in enumerate(trial_sequence, 1):
        print(f"  Trial {idx}: {concept} (Category {category})")
    
    # Start experiment
    print("\n" + "="*60)
    print("STARTING EXPERIMENT")
    print("="*60)
    
    experiment_clock.reset()
    all_trial_data = []
    
    for trial_idx, (concept, category) in enumerate(trial_sequence, 1):
        # Run trial
        trial_data = run_trial(concept, category, trial_idx, N_TRIALS)
        all_trial_data.append(trial_data)
        
        # Inter-trial interval (except after last trial)
        if trial_idx < N_TRIALS:
            core.wait(INTER_TRIAL_INTERVAL)
        
        # Check for escape key
        keys = visual.event.getKeys(keyList=['escape'])
        if 'escape' in keys:
            print("\nExperiment terminated by user.")
            break
    
    # End screen
    end_text = visual.TextStim(
        win,
        text="Experiment Complete!\n\nThank you for participating.",
        height=0.06,
        color='white'
    )
    end_text.draw()
    win.flip()
    core.wait(2.0)
    
    return all_trial_data

# =============================================================================
# RUN EXPERIMENT
# =============================================================================

if __name__ == "__main__":
    try:
        trial_data = run_experiment()
        
        # Print summary
        print("\n" + "="*60)
        print("EXPERIMENT SUMMARY")
        print("="*60)
        total_duration = experiment_clock.getTime()
        print(f"Total duration: {total_duration:.2f} seconds ({total_duration/60:.2f} minutes)")
        print(f"Trials completed: {len(trial_data)}")
        
        # You could save trial_data here if needed
        # np.save('trial_data.npy', trial_data)
        
    finally:
        # Always close the window
        win.close()
        core.quit()
