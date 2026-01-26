"""
Configuration file for Rhythmic Semantic Visualization Experiment
==================================================================

Modify this file to easily change concepts, timing, and experimental parameters.

Base Protocol: Adapted from Alberto Tates' successful "Ours rhythm" protocol
(see examples/rhytmic_experiment.py and Tates et al., IEEE TNSRE, 2025)

Author: Dr. Joshua Podmore
BCI-NE Lab, University of Essex

For complete parameter justifications with citations, see docs/config_justification.md
"""

# =============================================================================
# CONCEPT LISTS
# =============================================================================

# Define your concept categories here
# You can add as many categories as needed

# Category 1: Body Parts
BODY_PARTS_FULL = [
    'hand', 'foot', 'elbow', 'knee', 
    'shoulder', 'wrist', 'ankle', 'thumb',
    'finger', 'toe', 'arm', 'leg'
]

# Category 2: Fruits
FRUITS = [
    'apple', 'banana', 'orange', 'grape',
    'strawberry', 'lemon', 'peach', 'cherry',
    'pear', 'mango', 'kiwi', 'plum'
]

# Category 3: Vegetables
VEGETABLES = [
    'carrot', 'tomato', 'broccoli', 'cucumber',
    'pepper', 'lettuce', 'onion', 'potato',
    'corn', 'pumpkin', 'celery', 'radish'
]

# Category 4: Tools
TOOLS = [
    'hammer', 'screwdriver', 'wrench', 'saw',
    'drill', 'pliers', 'chisel', 'clamp'
]

# Category 5: Animals
ANIMALS = [
    'dog', 'cat', 'bird', 'fish',
    'rabbit', 'horse', 'elephant', 'lion'
]

# =============================================================================
# EXPERIMENT DESIGN OPTIONS
# =============================================================================

# --- Option 1: Two-Category Design (most common for BCI) ---
# Select 4-6 items from each category for balanced design
DESIGN_1_CATEGORY_A = BODY_PARTS_FULL[:6]  # ['hand', 'foot', 'elbow', 'knee', 'shoulder', 'wrist']
DESIGN_1_CATEGORY_B = FRUITS[:6]           # ['apple', 'banana', 'orange', 'grape', 'strawberry', 'lemon']

# --- Option 2: Body Parts vs Vegetables ---
DESIGN_2_CATEGORY_A = BODY_PARTS_FULL[:5]
DESIGN_2_CATEGORY_B = VEGETABLES[:5]

# --- Option 3: Tools vs Fruits ---
DESIGN_3_CATEGORY_A = TOOLS[:5]
DESIGN_3_CATEGORY_B = FRUITS[:5]

# --- Option 4: Single concept pair (like your speech paradigm) ---
DESIGN_4_CATEGORY_A = ['hand']
DESIGN_4_CATEGORY_B = ['apple']

# --- Option 5: Multiple pairs ---
DESIGN_5_CATEGORY_A = ['hand', 'foot']
DESIGN_5_CATEGORY_B = ['apple', 'banana']

# =============================================================================
# SELECT ACTIVE DESIGN
# =============================================================================

# Change this to switch between designs
ACTIVE_DESIGN = 1  # 1, 2, 3, 4, or 5

if ACTIVE_DESIGN == 1:
    CONCEPTS_CATEGORY_A = DESIGN_1_CATEGORY_A
    CONCEPTS_CATEGORY_B = DESIGN_1_CATEGORY_B
elif ACTIVE_DESIGN == 2:
    CONCEPTS_CATEGORY_A = DESIGN_2_CATEGORY_A
    CONCEPTS_CATEGORY_B = DESIGN_2_CATEGORY_B
elif ACTIVE_DESIGN == 3:
    CONCEPTS_CATEGORY_A = DESIGN_3_CATEGORY_A
    CONCEPTS_CATEGORY_B = DESIGN_3_CATEGORY_B
elif ACTIVE_DESIGN == 4:
    CONCEPTS_CATEGORY_A = DESIGN_4_CATEGORY_A
    CONCEPTS_CATEGORY_B = DESIGN_4_CATEGORY_B
elif ACTIVE_DESIGN == 5:
    CONCEPTS_CATEGORY_A = DESIGN_5_CATEGORY_A
    CONCEPTS_CATEGORY_B = DESIGN_5_CATEGORY_B

# =============================================================================
# TIMING PARAMETERS (seconds)
# =============================================================================

# Based on successful rhythmic protocols from paradigm paper and email correspondence:
# - Alberto's successful protocol ("Ours rhythm"): 0.8s intervals, 100 trials per class
# - BCI Competition (100% success): 2s intervals, 70 trials per class
# - Nguyen (80%+ success): 1s intervals, 100 trials per class
# - Tec (rhythmic): 1.4s intervals, 30 trials per class
#
# Email: "I used 0.8 seconds to try and enclose the time signature"
# Email: "only when I managed each repetition as a single trial did I get better results"
# This means: Each beep = one repetition = one analysis trial
#
# Research summary: Shorter time windows (up to 2s) most favorable
FIXATION_DURATION = 2.0      # Initial fixation cross (standard for BCI paradigms)
PROMPT_DURATION = 2.0        # How long to show the concept word (sufficient for reading/initiation)
BEEP_INTERVAL = 0.8          # Time between beeps (SOA) - matches Alberto's successful "Ours rhythm" protocol
N_BEEPS = 8                  # Number of rhythmic beeps per concept presentation
                              # Each beep = one repetition = one analysis trial
                              # 8 beeps × 0.8s = 6.4s visualization period per concept
                              # Total analysis trials = N_TRIALS × N_BEEPS
POST_CONCEPT_PAUSE = 1.0     # Pause after concept disappears, before beeps start
REST_DURATION = 1.0          # Blank screen after trial (standard rest period)
INTER_TRIAL_INTERVAL = 0.5   # Break between trials (prevents fatigue)

# =============================================================================
# JITTER SETTINGS
# =============================================================================

# Jitter range as fraction (0.1 = ±10%, 0.15 = ±15%, etc.)
# All timing parameters will be jittered by this amount
# Example: 1.0s base duration with 0.1 jitter = 0.9-1.1s actual duration
USE_JITTER = True            # Enable/disable jittering
JITTER_RANGE = 0.1           # ±10% jitter by default

# Calculate total trial duration
# Note: Actual duration will vary due to jittering if enabled
TRIAL_DURATION = (FIXATION_DURATION + PROMPT_DURATION + POST_CONCEPT_PAUSE + 
                  (BEEP_INTERVAL * N_BEEPS) + REST_DURATION)

# =============================================================================
# EXPERIMENT STRUCTURE
# =============================================================================

# Based on successful rhythmic protocols from paradigm paper:
# - BCI Competition: 70 trials per class (140 total)
# - Nguyen: 100 trials per class (200 total)  
# - Ours rhythm: 100 trials per class (200 total) - Alberto's successful protocol
# - Tec: 30 trials per class (60 total)
#
# For full experiment, use 100-200 total trials (50-100 per category)
# For testing/pilot, 40-60 trials is acceptable
N_TRIALS = 100               # Total number of concept presentations (50 per category)
                              # Each presentation has N_BEEPS repetitions (8) = 800 total analysis trials
                              # Set to 40-60 for pilot testing, 100-200 for full experiment
N_BLOCKS = 1                 # Number of blocks (with breaks between)
TRIALS_PER_BLOCK = N_TRIALS // N_BLOCKS

# Randomization
RANDOMIZE_CONCEPTS = True    # Randomly select concepts within categories
SHUFFLE_CATEGORIES = False   # Shuffle A/B order (vs. strict alternation)

# =============================================================================
# INSTRUCTIONS
# =============================================================================

INSTRUCTION_TEXT = """
Semantic Visualization Task

You will see words representing different concepts.

Your task: VISUALIZE each concept as vividly as possible.
- See it in your mind's eye
- Imagine its appearance, shape, color
- Think about its characteristics

After the word disappears, a rhythm will be marked with beeps.
Each beep is a cue to perform the same visualization again.

Visualize the concept each time you hear a beep.

Press SPACE to begin.
"""

BLOCK_BREAK_TEXT = """
Break Time

Take a moment to rest.

Press SPACE when ready to continue.
"""

# =============================================================================
# VISUAL PARAMETERS
# =============================================================================

WINDOW_SIZE = (1024, 768)
FULLSCREEN = False           # Set to True for actual experiments
TEXT_HEIGHT = 0.08           # Height of concept text
FIXATION_HEIGHT = 0.1        # Height of fixation cross
TEXT_COLOR = 'white'
BACKGROUND_COLOR = 'black'
BOLD_TEXT = True

# =============================================================================
# AUDIO PARAMETERS
# =============================================================================

BEEP_FREQUENCY = 440         # Hz (A4 note, or try 1000 for different tone)
BEEP_DURATION = 0.1          # Duration of each beep (seconds)

# =============================================================================
# DATA COLLECTION
# =============================================================================

SAVE_TRIAL_DATA = True       # Save trial timing data to file
OUTPUT_FILENAME = 'semantic_viz_trial_data.npy'

# =============================================================================
# EXPERIMENTAL NOTES
# =============================================================================

"""
DESIGN CONSIDERATIONS:

1. CONCEPT SELECTION:
   - Choose concepts that are easily visualizable
   - Ensure semantic distance between categories (body parts vs fruits is good)
   - Consider familiarity - all participants should know the concepts
   - Avoid ambiguous terms

2. TIMING (Based on successful studies):
   - 0.8s beep interval matches Alberto's successful "Ours rhythm" protocol
   - Also matches Nguyen (1s) and BCI Competition (2s) - all successful rhythmic protocols
   - 8 beeps = 6.4s visualization period per concept presentation
   - Each beep = one repetition = one analysis trial (per email: "each repetition as a single trial")
   - Research shows shorter windows (up to 2s) most favorable - our 0.8s is optimal

3. TRIAL COUNT (Based on paradigm paper Table I):
   - Successful studies: 60-200 total trials (30-100 per category)
   - BCI Competition: 140 total (70 per class) - 100% success rate
   - Nguyen: 200 total (100 per class) - 80%+ success rate
   - Ours rhythm: 200 total (100 per class) - 80%+ success rate (Alberto's protocol)
   - Tec: 60 total (30 per class) - rhythmic protocol
   - Current default: 100 total (50 per category) - good balance
   - For pilot testing: 40-60 trials acceptable
   - For full experiment: 100-200 trials recommended
   - Total analysis trials = N_TRIALS × N_BEEPS (e.g., 100 × 8 = 800 repetitions)

4. CONTROLS TO CONSIDER:
   - Add a "rest" or "relax" condition (passive baseline)
   - Include catch trials to verify attention
   - Consider counterbalancing category order across participants

5. INSTRUCTIONS:
   - Emphasize sustained visualization
   - Discourage verbal/motor strategies
   - Practice trials may be helpful

6. EEG CONSIDERATIONS:
   - Fixation cross reduces eye movements
   - Blank screen during beeps minimizes visual ERPs
   - Rhythmic structure may enhance signal quality (as per your paper!)
"""
