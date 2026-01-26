"""
Paradigm timing analysis based on email description.

Email description:
"first, participants were prompted with the class to imagine; 
then, a rhythm was marked with a beep at each interval (t), 
instructing them to perform the same class each time they heard it."

Key points:
1. Prompt FIRST (show the class/concept)
2. THEN play beeps at intervals
3. Each beep = cue to perform the same class again
4. Each repetition (beep) should be treated as separate trial for analysis

Current implementation matches this:
- Fixation (2s) - prepares participant
- Concept prompt (2s) - shows what to visualize
- Clear screen
- Beep sequence (8 beeps at 0.8s intervals) - each beep cues repetition
- Rest (1s)

This matches the example code structure exactly.
"""

# Timing breakdown per trial:
# Fixation: 2.0s
# Prompt: 2.0s  
# Beep sequence: 8 × 0.8s = 6.4s
# Rest: 1.0s
# Total: ~11.4s per trial

# For analysis: Each beep can be treated as a separate "repetition trial"
# This gives 8 repetitions per concept presentation
# Total repetitions = N_TRIALS × N_BEEPS
