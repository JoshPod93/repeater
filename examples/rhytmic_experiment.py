from psychopy import visual, core, sound
import random

# --- Setup ---
# Create a window
win = visual.Window(size=(800, 600), color='black', units='height')

# Create stimuli
fixation = visual.TextStim(win, text='+', height=0.1, color='white')
prompt = visual.TextStim(win, text='', height=0.08, color='white')

# Create a beep sound (A note, 0.1s duration)
# Note: 'A' requires 'sounddevice' or 'ptb' backend.
# If this fails, try using value='C' or a specific frequency like value=440
beep = sound.Sound('A', octave=4, secs=0.1)

# Define words to alternate
words = ['pinch', 'stop']
n_trials = 5

# Create a clock to track time
clock = core.Clock()

# --- Main Experiment Loop ---
for trial in range(n_trials):
    # Determine which word to show
    word_index = trial % len(words)
    current_word = words[word_index]

    # 1. Fixation cross for 2 seconds
    fixation.draw()
    win.flip()
    core.wait(2.0)

    # 2. Prompt for 2 seconds
    prompt.text = f'innerly say "{current_word}"'
    prompt.draw()
    win.flip()
    core.wait(2.0)

    # 3. Beep loop (4 beeps, one every 0.8 seconds)
    n_beeps = 8
    for beep_count in range(n_beeps):
        # Clear screen (black background)
        win.flip()

        # Force stop before playing to ensure it triggers every time
        beep.stop()
        beep.play()

        # Log time for debugging (Optional)
        print(f"Trial {trial}, Beep {beep_count} at {clock.getTime():.3f}")

        # Wait for the full interval (SOA)
        core.wait(0.8)
    # 4. Blank screen for rest period (1 second)
    win.flip()
    core.wait(1.0)

    # Optional: Short break between trials
    if trial < n_trials - 1:
        win.flip()
        core.wait(0.5)

# Close the window
win.close()
core.quit()