# Trigger Code Coverage Check

## Current Trial Sequence and Triggers

### Trial-Level Events:

1. **Trial Start** ✓
   - Code: 101-110 (reused per block, based on trial number 1-10)
   - Function: `get_trial_start_code(trial_num)`
   - When: Start of each trial

2. **Trial Indicator** ✓
   - Code: 3
   - When: When "Trial X/100" text is displayed

3. **Concept Word** ✓
   - Code: 10 (Category A) or 20 (Category B)
   - When: When concept word appears on screen

4. **Visual Mask** ✓
   - Code: 25
   - When: When mask appears after concept word

5. **Fixation Cross** ✓
   - Code: 1
   - When: When fixation cross appears before beeps

6. **Beep Start** ✓
   - Code: 30
   - When: Start of beep sequence

7. **Individual Beeps** ✓
   - Codes: 31-38 (one per beep)
   - When: Each beep sound

8. **Trial End** ✓
   - Code: 151-160 (reused per block, based on trial number 1-10)
   - Function: `get_trial_end_code(trial_num)`
   - When: End of trial (before rest period)

### Block-Level Events:

9. **Block Start** ✓
   - Code: 61-70 (one per block, blocks 1-10)
   - Function: `get_block_start_code(block_num)`
   - When: Start of each block

10. **Block End** ✓
    - Code: 71-80 (one per block, blocks 1-10)
    - Function: `get_block_end_code(block_num)`
    - When: End of each block

## Summary

All essential events have trigger codes:
- Trial start/end ✓
- Trial indicator ✓
- Concept presentation ✓
- Visual mask ✓
- Fixation cross ✓
- Beep sequence (start + individual beeps) ✓
- Block start/end ✓

No missing triggers detected.
