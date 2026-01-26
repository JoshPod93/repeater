# Simulation Testing Guide

## Overview

The simulation variant (`paradigm/semantic_paradigm_simulation.py`) allows you to test all experiment functionality without requiring:
- EEG hardware
- Parallel port
- Actual participant

## What It Tests

1. **Display Functionality**
   - Window creation
   - Fixation cross display
   - Concept text presentation
   - Progress indicators
   - Screen clearing

2. **Trigger Logging**
   - All trigger codes are logged with timestamps
   - Trigger sequence verification
   - Category-specific triggers (A vs B)

3. **Timing Accuracy**
   - Fixation duration (2.0s)
   - Concept display duration (2.0s)
   - Beep intervals (0.8s)
   - Rest periods (1.0s)

4. **Data Saving**
   - JSON file creation
   - NumPy file creation
   - Metadata recording
   - Timestamp accuracy

5. **Trial Sequence**
   - Balanced A/B alternation
   - Concept randomization
   - Sequence validation

## Usage

### Quick Test (2 trials)
```bash
python paradigm/semantic_paradigm_simulation.py --n-trials 2
```

### Full Test (default from config)
```bash
python paradigm/semantic_paradigm_simulation.py
```

### Verbose Output
```bash
python paradigm/semantic_paradigm_simulation.py --n-trials 5 --verbose
```

## Verification Checklist

After running simulation, verify:

- [ ] Window opens correctly
- [ ] Instructions display properly
- [ ] Fixation cross appears
- [ ] Concept words display correctly
- [ ] Countdown shows during visualization (if enabled)
- [ ] All triggers logged with timestamps
- [ ] Beep intervals are ~0.8s apart
- [ ] Data files created in `data/results/`
- [ ] JSON file contains all trial data
- [ ] NumPy file can be loaded
- [ ] Timestamps are sequential and reasonable

## Expected Output

```
[SIM] Trial 1/2: wrist (Category A)
  [SIM] Fixation at 7.803s
  [SIM] Concept 'wrist' (Category A) at 9.840s
  [SIM] Beep 1/8 at 11.892s
  [SIM] Beep 2/8 at 12.707s
  ...
  [SIM] Trial end at 18.428s
```

## Differences from Real Experiment

1. **No EEG Hardware**: Triggers are simulated, not sent
2. **Windowed Mode**: Always runs in window (not fullscreen)
3. **No Practice Trials**: Skips practice by default
4. **Visual Countdown**: Shows countdown during visualization period
5. **Silent Beeps**: Audio may not work (depends on PsychoPy backend)

## Troubleshooting

### Sound Issues
If beeps don't play (common on some systems):
- This is OK for simulation - triggers still work
- Check PsychoPy sound backend compatibility
- Real experiment will use proper audio setup

### Display Issues
- Ensure window is visible
- Check monitor configuration
- Try different window sizes

### Trigger Issues
- All triggers are logged even if not sent
- Check console output for trigger timestamps
- Verify trigger codes match expected values

## Next Steps

Once simulation passes all checks:

1. Test with real participant (no EEG)
2. Test trigger hardware connection
3. Integrate with BioSemi system
4. Run full experiment
