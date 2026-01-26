# Trigger Validation System

## Overview

The trigger validation system ensures that the concepts shown on screen (logged in trigger CSV files) match the ground truth randomization protocol exactly. This is **critical for data integrity** - any mismatch indicates a serious problem that must be corrected.

## Ground Truth: Randomization Protocol

The randomization protocol (`*_randomization_protocol.json`) is the **ground truth** for what concepts should be shown. It contains:

- Complete trial sequence for all blocks
- Concept words and categories for each trial
- Trial numbers (global across all blocks)
- Block assignments

## Trigger Logs: What Was Actually Shown

The trigger CSV files (`*_triggers.csv`) log what was actually displayed:

- Concept words embedded in `event_name` field: `concept_{word}_category_{A|B}`
- Trial numbers from dynamic trigger codes (101-199 for trial start)
- Timestamps for each event

## Validation Process

The `scripts/validate_triggers.py` script:

1. **Loads the randomization protocol** (ground truth)
2. **Loads trigger CSV files** (what was actually shown)
3. **Extracts concept sequence** from trigger logs
4. **Compares sequences** trial-by-trial
5. **Reports mismatches**:
   - Concept word mismatches
   - Category mismatches
   - Missing trials
   - Extra trials
   - Sequence order errors

## Usage

### Validate all trigger files for a participant:

```bash
python scripts/validate_triggers.py --participant-id sim_9999 --session 1
```

### Validate a specific trigger CSV file:

```bash
python scripts/validate_triggers.py \
  --trigger-csv data/triggers/sub-sim_9999_ses-1_20260126_154741_triggers.csv \
  --participant-id sim_9999 --session 1
```

## Expected Output

### Validation Passed:
```
OVERALL: VALIDATION PASSED - All trigger logs match protocol
```

### Validation Failed:
```
OVERALL: VALIDATION FAILED - Mismatches detected!
  Errors:
    - Trial 5: Concept mismatch - trigger='hand', expected='foot'
    - Trial 10: Category mismatch - trigger='A', expected='B'
    - MISSING: 5 trials not found in trigger log
```

## Critical Checks

The validation ensures:

1. **Concept words match**: Each trial shows the correct concept word
2. **Categories match**: Each trial has the correct category (A or B)
3. **Trial count matches**: All expected trials are present
4. **Sequence order matches**: Trials appear in the correct order
5. **No extra trials**: No unexpected trials in the log

## Why This Matters

- **Data integrity**: Ensures EEG data is labeled correctly
- **Analysis validity**: Wrong labels = wrong analysis results
- **Reproducibility**: Protocol is the source of truth
- **Error detection**: Catches bugs in experiment code early

## Integration

The validation should be run:

1. **After each experiment session** to verify data integrity
2. **Before analysis** to ensure labels are correct
3. **As part of quality control** pipeline
4. **When debugging** trigger/logging issues

## Example: Validation Report

```
================================================================================
TRIGGER LOG VALIDATION REPORT
================================================================================

Protocol Info:
  Timestamp: 20260126_155321
  Blocks in protocol: 10
  Trigger files validated: 1

Validation Results:

  sub-test_validation3_ses-1_20260126_155321_triggers.csv: FAILED
    Errors (2):
      - MISMATCH: Trigger log has 2 concepts, protocol expects 20
      - MISSING: 18 trials not found in trigger log

================================================================================
OVERALL: VALIDATION FAILED - Mismatches detected!
================================================================================
```

This correctly detected that only 2 trials were run (first block only) while the protocol expects 20 total trials across all blocks.
