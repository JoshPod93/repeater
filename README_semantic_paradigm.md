# Rhythmic Semantic Visualization Paradigm

**Adaptation of Speech Imagery BCI paradigm for semantic processing tasks**

Author: A. Tates (JP)  
BCI-NE Lab, University of Essex  
Date: January 26, 2026

---

## Overview

This paradigm adapts the rhythmic speech imagery protocol to study **semantic visualization** instead of imagined speech. Instead of silently articulating words, participants visualize concepts (body parts, fruits, vegetables, tools, etc.).

Based on findings from "Consolidating the Speech Imagery Paradigm" showing that **rhythmic protocols drive superior decoding accuracy**, this adaptation maintains the temporal structure while changing the cognitive task from motor speech planning to semantic concept visualization.

---

## Files Included

### 1. `rhythmic_semantic_visualization.py`
**Simple, standalone version**
- Easy to read and modify
- All parameters in one file
- Good for quick testing
- No external dependencies beyond PsychoPy

**Use this if:** You want a straightforward script to get started quickly

### 2. `experiment_config.py`
**Configuration file**
- Centralized parameter management
- Multiple pre-defined designs
- Easy concept list customization
- Detailed documentation

**Use this:** To easily change experimental parameters without touching main code

### 3. `rhythmic_semantic_enhanced.py`
**Full-featured version**
- Loads config from `experiment_config.py`
- EEG trigger support (parallel port)
- Practice trials
- Progress indicators
- Automatic data saving (JSON + NumPy)
- Participant ID management
- Comprehensive logging

**Use this:** For actual EEG experiments with proper data collection

---

## Quick Start Guide

### Minimal Setup (Testing)

```bash
# Run the simple version
python rhythmic_semantic_visualization.py
```

### Full Experiment Setup

```bash
# 1. Edit experiment_config.py to set your concepts
# 2. Run the enhanced version
python rhythmic_semantic_enhanced.py

# Enter participant info when prompted
# Data automatically saved to experiment_data/
```

---

## Experimental Design

### Paradigm Structure

Each trial consists of:

1. **Fixation cross** (2s)
   - Reduces eye movements
   - Prepares participant

2. **Concept presentation** (2s)
   - Word displayed on screen
   - Participant begins visualization

3. **Rhythmic beep sequence** (6.4s)
   - 8 beeps at 0.8s intervals (SOA)
   - Blank screen
   - Participant maintains visualization
   - **Key insight from your paper:** Rhythmic structure drives superior decoding

4. **Rest period** (1s)
   - Blank screen
   - Cognitive reset

**Total trial duration:** ~11.4 seconds

### Timing Rationale

- **0.8s beep interval:** Matches your successful speech imagery protocol
- **8 beeps (6.4s):** Sufficient for stable EEG patterns
- **2s concept display:** Enough to read and initiate visualization
- **2s fixation:** Standard for BCI paradigms

### Default Concept Sets

**Option 1: Body Parts vs. Fruits**
- Category A: hand, foot, elbow, knee, shoulder, wrist
- Category B: apple, banana, orange, grape, strawberry, lemon

**Option 2: Body Parts vs. Vegetables**
- Category A: hand, foot, elbow, knee, shoulder
- Category B: carrot, tomato, broccoli, cucumber, pepper

**Option 3: Simple Pair (like speech paradigm)**
- Category A: hand
- Category B: apple

---

## Key Features

### From Your Research

✅ **Rhythmic protocol** (R=0.60, p<0.005 correlation with accuracy)  
✅ **Structured timing** (reduces covariance entropy)  
✅ **Consistent SOA** (0.8s intervals)  
✅ **Binary classification** (two categories)  
✅ **Balanced design** (alternating categories)

### New for Semantic Task

🎯 **Visual imagery** instead of motor imagery  
🎯 **Semantic categories** (body parts, fruits, tools)  
🎯 **No articulatory component** (purely semantic)  
🎯 **Flexible concept lists** (easily customizable)

---

## Customization Guide

### Changing Concepts

Edit `experiment_config.py`:

```python
# Add your own categories
MY_CONCEPTS_A = ['cat', 'dog', 'bird', 'fish']
MY_CONCEPTS_B = ['car', 'bike', 'train', 'plane']

# Update active design
CONCEPTS_CATEGORY_A = MY_CONCEPTS_A
CONCEPTS_CATEGORY_B = MY_CONCEPTS_B
```

### Adjusting Timing

```python
FIXATION_DURATION = 2.0      # Initial fixation
PROMPT_DURATION = 2.0        # Concept display
BEEP_INTERVAL = 0.8          # Time between beeps
N_BEEPS = 8                  # Number of beeps
```

### Changing Trial Count

```python
N_TRIALS = 40  # Should be even for balanced design
```

---

## EEG Integration

### Trigger Codes (Enhanced Version)

```python
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
```

### Enabling Triggers

```python
# In rhythmic_semantic_enhanced.py
USE_EEG_TRIGGERS = True
PARALLEL_PORT_ADDRESS = 0x0378  # Adjust for your system
```

---

## Expected Output

### Trial Sequence Example

```
Trial 1: hand (Category A)
Trial 2: apple (Category B)
Trial 3: foot (Category A)
Trial 4: banana (Category B)
...
```

### Data Files

When using `rhythmic_semantic_enhanced.py`:

```
experiment_data/
├── sub-001_ses-1_20260126_143022_trials.json
└── sub-001_ses-1_20260126_143022_trials.npy
```

**JSON contains:**
- Metadata (participant, date, concepts used)
- All trial information
- Precise timestamps for every event

**NumPy contains:**
- Same data in array format
- Easy to load for analysis

---

## Analysis Pipeline Compatibility

This paradigm generates data compatible with your `tangent_space_logistic_regressor_classifier.py`:

### Steps to Analyze

1. **Record EEG** using this paradigm
2. **Preprocess** with your standard pipeline (ICA, filtering)
3. **Epoch** around concept onset (use triggers 10/20)
4. **Run classification** with your TS-LR pipeline

### Expected Workflow

```python
# Your existing pipeline
epochs = read_epochs('sub-001/ica_epo.fif')
epochs = epochs[['hand', 'apple']]  # Select classes

# Run your analysis
run_l1_cv(x, y, top_n_bands=5)
```

The covariance-based features your paper found effective (entropy, inter-band correlation) should work equally well for semantic visualization.

---

## Design Considerations

### Why Semantic Visualization?

1. **Semantic networks** in the brain are well-studied
2. **Visual imagery** avoids motor confounds
3. **Concept categories** provide clear semantic distance
4. **Less reliance** on speech motor areas
5. **Potentially more universal** (less language-dependent)

### Recommended Concept Selection

✅ **DO:**
- Use highly visualizable concepts
- Ensure semantic distance between categories
- Choose familiar concepts (all participants know them)
- Keep words short (easier to read quickly)

❌ **AVOID:**
- Abstract concepts (love, justice)
- Ambiguous terms (bank, bat)
- Very similar items within a category
- Long, complex words

### Theoretical Predictions

Based on your paradigm paper:

- **Rhythmic protocol** should enhance decoding vs. non-rhythmic
- **Covariance entropy** should be lower in good performers
- **Inter-band correlation** should be higher in efficient users
- **Left frontal** regions likely involved (semantic processing)
- **Bilateral temporal** regions (semantic memory)
- **Occipital** regions (visual imagery)

---

## Troubleshooting

### Sound Issues

If beeps don't play:

```python
# Try different frequency
BEEP_FREQUENCY = 1000  # Instead of 440

# Or use default note
beep = sound.Sound('A', octave=4, secs=0.1)
```

### Parallel Port Issues

```python
# Check your port address
# Windows: Usually 0x0378 (LPT1)
# Linux: /dev/parport0

# Test with:
from psychopy import parallel
port = parallel.ParallelPort(address=0x0378)
port.setData(255)  # All pins high
```

### Timing Precision

For critical timing, ensure:
- Close other applications
- Disable CPU throttling
- Use dedicated experiment computer
- Check with oscilloscope if possible

---

## Future Extensions

### Possible Enhancements

1. **Visual cues:** Show images of concepts (not just words)
2. **Graded difficulty:** Easy vs. hard visualizations
3. **Similarity ratings:** Collect behavioral data
4. **Multi-session:** Track learning effects
5. **Adaptive difficulty:** Adjust based on performance

### Integration with Other Paradigms

- **Motor imagery:** Compare semantic vs. motor
- **SSVEP:** Add frequency tagging
- **P300:** Oddball within categories
- **Hybrid BCI:** Combine multiple signals

---

## Citation

If you use this paradigm, please cite the foundational work:

```
Tates, A., et al. (2025). "Consolidating the Speech Imagery Paradigm: 
Evidence that Rhythmic Protocols Drive Superior Decoding Accuracy." 
IEEE Transactions on Neural Systems and Rehabilitation Engineering.

Tates, A., et al. (2025). "Speech imagery brain-computer interfaces: 
a systematic literature review." Journal of Neural Engineering, 22, 031003.
```

---

## Contact & Support

**Author:** A. Tates (JP)  
**Lab:** BCI-NE Lab, University of Essex  
**Email:** at18157@essex.ac.uk

For questions about:
- Experimental design → Refer to paradigm paper
- Implementation → Check code comments
- Analysis pipeline → See classifier script
- Theoretical background → See literature review

---

## License

This code is provided for research purposes. Feel free to modify and adapt for your studies.

---

## Version History

**v1.0 (2026-01-26)**
- Initial adaptation from speech imagery paradigm
- Three versions: simple, config, enhanced
- EEG trigger support
- Comprehensive documentation

---

## Quick Reference Card

```
TIMING
------
Fixation:  2.0s
Concept:   2.0s  
Beeps:     8 × 0.8s = 6.4s
Rest:      1.0s
Total:     ~11.4s per trial

TRIGGERS
--------
1  = Fixation
10 = Category A concept
20 = Category B concept
30 = Beep sequence start
31 = Individual beep
40 = Trial end

KEYS
----
SPACE = Continue
ESCAPE = Quit

FILES
-----
Simple:    rhythmic_semantic_visualization.py
Config:    experiment_config.py
Enhanced:  rhythmic_semantic_enhanced.py
Output:    experiment_data/*.json, *.npy
```

---

**Happy experimenting! 🧠🔬**
