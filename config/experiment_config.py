"""
Configuration file for Rhythmic Semantic Visualization Experiment
==================================================================

Modify this file to easily change concepts, timing, and experimental parameters.

Author: A. Tates (JP)
BCI-NE Lab, University of Essex
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

# These are based on your rhythmic paradigm timing
FIXATION_DURATION = 2.0      # Initial fixation cross
PROMPT_DURATION = 2.0        # How long to show the concept word
BEEP_INTERVAL = 0.8          # Time between beeps (SOA)
N_BEEPS = 8                  # Number of rhythmic beeps
REST_DURATION = 1.0          # Blank screen after trial
INTER_TRIAL_INTERVAL = 0.5   # Break between trials

# Calculate total trial duration
TRIAL_DURATION = FIXATION_DURATION + PROMPT_DURATION + (BEEP_INTERVAL * N_BEEPS) + REST_DURATION

# =============================================================================
# EXPERIMENT STRUCTURE
# =============================================================================

N_TRIALS = 40                # Total number of trials (should be even for balanced design)
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

2. TIMING:
   - The 0.8s beep interval matches your speech paradigm
   - 8 beeps = 6.4s of sustained visualization
   - This should be enough for stable EEG patterns
   - Adjust if you find participants can't maintain focus

3. TRIAL COUNT:
   - 40 trials = 20 per category (good for initial testing)
   - Scale up to 100-200 for actual BCI experiments
   - Balance recording time vs participant fatigue

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
