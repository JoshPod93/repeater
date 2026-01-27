# Next Steps: Final Optimization & Data Collection Pipeline
**Created:** January 27, 2026  
**Status:** Immediate priorities for next session

## Overview

This document outlines the immediate next steps following successful trigger validation and alignment confirmation. The system is now ready for final timing optimizations, behavioral analysis, and full data collection pipeline development.

## Current Status

### ✅ Completed
- **Trigger system validated** - Perfect alignment between CSV, BDF, and expected triggers confirmed
- **9 blocks collected** - Data collection successful with perfect trigger alignment
- **Script cleanup** - Redundant scripts removed, essential validation tools maintained
- **Block 10 fix** - Validation updated to support all 10 blocks (ready for next run)
- **Code cleanup** - All trigger codes within 8-bit limit (0-255), no overlaps

### 🔄 Immediate Next Steps

---

## 1. Final Timing Optimization & Adjustment

**Priority:** High  
**Estimated Time:** 1-2 hours

### Tasks:
- [ ] Review current timing parameters in `config/experiment_config.py`
- [ ] Adjust trial durations, fixation times, beep intervals based on pilot data
- [ ] Test timing adjustments with short test runs
- [ ] Document final timing parameters

### Files to Review:
- `config/experiment_config.py` - Timing configuration
- `paradigm/semantic_paradigm_live.py` - Timing implementation

### Notes:
- Current timing should be validated against behavioral data from 9 blocks
- Consider participant comfort and attention span
- Ensure timing allows for proper EEG signal capture

---

## 2. Behavioral Analysis & Concept Selection

**Priority:** High  
**Estimated Time:** 2-4 hours (analysis, not coding)

### Tasks:
- [ ] Analyze behavioral data from collected blocks
- [ ] Identify concepts with best behavioral responses
- [ ] Determine optimal concept-item pairs based on:
  - Response accuracy
  - Response consistency
  - Participant engagement
  - Task difficulty appropriateness

### Data Sources:
- Behavioral responses from CSV files in `data/results/`
- Response times and accuracy metrics
- Any participant feedback or notes

### Notes:
- This is **behavioral analysis only** - no coding required
- Results will inform concept-item amendments in next step
- Consider both individual and group-level patterns

---

## 3. Amend Concept-Items Configuration

**Priority:** High  
**Estimated Time:** 30 minutes

### Tasks:
- [ ] Update `config/experiment_config.py` with selected concepts
- [ ] Modify concept lists based on behavioral analysis:
  - `BODY_PARTS_FULL` - Update items if needed
  - `VEGETABLES` - Update items if needed
  - Ensure 5 items per category maintained
- [ ] Update `DESIGN_1_CATEGORY_A` and `DESIGN_1_CATEGORY_B` if needed
- [ ] Test randomization with new concept lists

### Files to Modify:
- `config/experiment_config.py` - Concept lists and design configuration

### Validation:
- Run `python scripts/test_config_randomization.py` to verify
- Ensure balanced distribution across blocks
- Confirm no duplicate items within blocks

---

## 4. Collect Actual Data

**Priority:** Critical  
**Estimated Time:** 2-3 hours per participant

### Tasks:
- [ ] Run full 10-block experiment with optimized timings
- [ ] Use updated concept-items from behavioral analysis
- [ ] Collect data for target number of participants
- [ ] Verify trigger alignment after each session:
  ```bash
  conda activate repeat_analyse
  python scripts/validate_captured_data.py
  ```

### Execution:
- Use `scripts/run_all_blocks.ps1` (Windows) or `scripts/run_all_blocks.sh` (Linux/Mac)
- Monitor for any timing issues or participant fatigue
- Ensure BDF files are properly saved

### Data Organization:
- Each participant gets: `data/sub_XXXX/` directory
- Results: `data/results/sub-XXXX_TIMESTAMP/`
- BDF files: `data/sub_XXXX/sub_XXXX.bdf`

---

## 5. Develop/Implement Preprocessing Pipeline

**Priority:** High  
**Estimated Time:** 4-6 hours

### Tasks:
- [ ] Create preprocessing script/module for EEG data
- [ ] Implement standard preprocessing steps:
  - [ ] Filtering (bandpass, notch)
  - [ ] Bad channel detection/interpolation
  - [ ] Epoch extraction (trial-based)
  - [ ] Artifact rejection (ICA, manual)
  - [ ] Baseline correction
- [ ] Align preprocessing with trigger codes
- [ ] Create epoch structure matching trial structure:
  - Trial start/end markers
  - Concept presentation markers
  - Beep sequence markers

### Files to Create:
- `preprocessing/preprocess_eeg.py` - Main preprocessing script
- `preprocessing/config.py` - Preprocessing parameters
- `preprocessing/utils.py` - Helper functions

### Reference:
- Use MNE-Python for preprocessing
- Follow Alberto's preprocessing standards if available
- Ensure compatibility with classification pipeline

### Validation:
- Test preprocessing on pilot data
- Verify epoch structure matches expected trial structure
- Check data quality metrics

---

## 6. Run Analysis: Alberto's Classification Method

**Priority:** High  
**Estimated Time:** 4-8 hours

### Tasks:
- [ ] Implement/adapt Alberto's original classification method
- [ ] Apply to preprocessed data
- [ ] Run classification analysis:
  - [ ] Feature extraction
  - [ ] Model training
  - [ ] Cross-validation
  - [ ] Performance evaluation
- [ ] Generate results and visualizations
- [ ] Compare with behavioral data

### Files to Create:
- `analysis/classify.py` - Classification implementation
- `analysis/features.py` - Feature extraction
- `analysis/evaluate.py` - Evaluation metrics

### Reference:
- Alberto's original classification method (from reference project)
- Ensure method matches original implementation
- Document any adaptations or improvements

### Output:
- Classification accuracy metrics
- Confusion matrices
- Feature importance analysis
- Comparison with chance level

---

## Summary Checklist

Before next session:
- [ ] Review timing parameters
- [ ] Complete behavioral analysis
- [ ] Update concept-items
- [ ] Prepare for data collection

During next session:
- [ ] Finalize timing optimizations
- [ ] Collect actual participant data
- [ ] Develop preprocessing pipeline
- [ ] Implement classification analysis

---

## Notes & Considerations

### Timing Optimization
- Consider participant fatigue across 10 blocks
- Ensure sufficient inter-trial intervals
- Balance between data quality and session length

### Concept Selection
- Prioritize concepts with clear behavioral differentiation
- Consider semantic relationships between categories
- Ensure concepts are appropriate for visualization task

### Preprocessing
- Document all preprocessing steps clearly
- Save intermediate files for debugging
- Ensure reproducibility

### Classification
- Maintain consistency with Alberto's original method
- Document any modifications
- Compare results with behavioral performance

---

## Files Reference

### Configuration
- `config/experiment_config.py` - Experiment parameters, concept lists

### Execution
- `scripts/run_all_blocks.ps1` / `scripts/run_all_blocks.sh` - Run all blocks
- `paradigm/semantic_paradigm_live.py` - Main experiment script

### Validation
- `scripts/validate_captured_data.py` - Quick validation
- `scripts/comprehensive_data_evaluation.py` - Full evaluation
- `scripts/validate_triggers.py` - Detailed trigger validation

### Data
- `data/sub_XXXX/` - Participant BDF files
- `data/results/sub-XXXX_TIMESTAMP/` - Results and CSV logs

---

**Last Updated:** January 27, 2026  
**Next Session:** January 28, 2026
