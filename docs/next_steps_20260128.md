# Next Steps - Semantic Visualization Paradigm
**Date:** 2026-01-28  
**Status:** Data collection ready, validation complete

## Current Status

### Completed
- [x] Experiment paradigm implementation (live + simulation)
- [x] Trigger system integration (Biosemi serial port)
- [x] Block-based data organization
- [x] Comprehensive trigger validation
- [x] Pathing and file structure finalized
- [x] Exception handling for robust data saving
- [x] Full 10-block test run successful (1520 triggers, perfect CSV/BDF alignment)

### System Status
- **Blocks:** 10 blocks × 10 trials = 100 total trials
- **Triggers per trial:** 15 (start, indicator, concept, mask, fixation, beep_start, 8 beeps, end)
- **Triggers per block:** 152 (block_start + 150 trial triggers + block_end)
- **Total triggers:** 1520 for full session
- **Data structure:** Each block folder contains JSON/NPY trial data
- **CSV logging:** Single CSV file per session (appends across blocks)

## Next Steps - Data Collection & Analysis Pipeline

### Phase 1: Real Data Collection
1. **Collect real participant data**
   - Run full 10-block session with actual participant
   - Verify Biosemi recording captures all triggers
   - Ensure BDF file saved correctly to `data/sub_{participant_id}/`

### Phase 2: Epoching Verification
2. **Check epoching**
   - Verify epochs align correctly with trigger codes
   - Confirm epoch windows match experimental design
   - Validate epoch labels (Category A vs B)
   - Check baseline correction windows

### Phase 3: Logging Verification
3. **Re-check logging**
   - Verify all 1520 triggers present in CSV
   - Confirm CSV/BDF alignment still perfect
   - Check trial data files contain all expected fields
   - Validate timestamps are consistent

### Phase 4: Stimuli Optimization
4. **Final stimuli adjustments**
   - Review timing parameters based on real data
   - Adjust concept word display duration if needed
   - Optimize mask timing
   - Fine-tune inter-trial intervals
   - Document any timing changes

### Phase 5: Preprocessing Pipeline
5. **Run preprocessing**
   - Implement preprocessing script
   - Filter settings (bandpass, notch)
   - Artifact rejection parameters
   - ICA for eye movement removal
   - Verify epochs are correctly extracted

6. **Optimize preprocessing**
   - Tune filter parameters
   - Adjust artifact rejection thresholds
   - Optimize ICA components
   - Validate preprocessing quality
   - Document preprocessing parameters

### Phase 6: Analysis Preparation
7. **Prepare for classification**
   - Set up Alberto's classification method
   - Prepare feature extraction
   - Design cross-validation scheme
   - Plan statistical analysis

## File Structure Reference

```
data/
├── results/
│   └── sub-{participant_id}_{timestamp}/
│       ├── Block_0000/
│       │   ├── sub-{id}_{timestamp}_trials.json
│       │   └── sub-{id}_{timestamp}_trials.npy
│       ├── ...
│       ├── sub-{id}_{timestamp}_triggers.csv
│       └── sub-{id}_{timestamp}_randomization_protocol.json
└── sub_{participant_id}/
    └── sub_{participant_id}.bdf
```

## Trigger Code Reference

### Block Level
- Block start: 61-70 (1 per block)
- Block end: 71-80 (1 per block)

### Trial Level (per trial)
- Trial start: 101-110 (cycles, 1 per trial)
- Trial indicator: 3 (1 per trial)
- Concept Category A: 10 (1 per trial)
- Concept Category B: 20 (1 per trial)
- Mask: 25 (1 per trial)
- Fixation: 1 (1 per trial)
- Beep start: 30 (1 per trial)
- Beeps: 31-38 (8 per trial)
- Trial end: 151-160 (cycles, 1 per trial)

## Validation Commands

```bash
# Comprehensive data evaluation
conda activate repeat_analyse
python scripts/validate_captured_data.py --participant-id {id}

# Detailed trigger alignment
python scripts/validate_triggers.py --participant-id {id}
```

## Notes

- All blocks are self-contained - can be run individually
- Data saves even if block interrupted (partial data preserved)
- Single CSV file per session (appends across blocks)
- Validation scripts updated to account for all 15 triggers per trial
