# Trigger Code Mapping for Semantic Visualization Paradigm

This document provides a comprehensive overview of the trigger codes used in the experiment, their corresponding event names, and their numerical values. These codes are crucial for synchronizing EEG data with experimental events.

## Base Trigger Codes

The following table lists the base trigger codes (used for events that don't vary by trial/block number):

| Event Name           | Code | Hex   | Description                                   |
| :------------------- | :--- | :---- | :-------------------------------------------- |
| `fixation`           | 1    | `0x1` | Fixation cross appears                        |
| `concept_category_a` | 10   | `0xa` | Category A concept word is displayed          |
| `concept_category_b` | 20   | `0x14`| Category B concept word is displayed          |
| `beep_start`         | 30   | `0x1e`| Marks the beginning of the rhythmic beep sequence |
| `beep_1`             | 31   | `0x1f`| First beep within the sequence                |
| `beep_2`             | 32   | `0x20`| Second beep within the sequence               |
| `beep_3`             | 33   | `0x21`| Third beep within the sequence                |
| `beep_4`             | 34   | `0x22`| Fourth beep within the sequence               |
| `beep_5`             | 35   | `0x23`| Fifth beep within the sequence                |
| `beep_6`             | 36   | `0x24`| Sixth beep within the sequence                |
| `beep_7`             | 37   | `0x25`| Seventh beep within the sequence              |
| `beep_8`             | 38   | `0x26`| Eighth beep within the sequence               |

## Dynamic Trigger Codes

### Trial-Level Triggers

**Trial Start Codes:**
- Trial N start = **100 + N**
- Range: 101-199 (supports up to 99 trials)
- Examples:
  - Trial 1 start = **101**
  - Trial 2 start = **102**
  - Trial 50 start = **150**

**Trial End Codes:**
- Trial N end = **200 + N**
- Range: 201-299 (supports up to 99 trials)
- Examples:
  - Trial 1 end = **201**
  - Trial 2 end = **202**
  - Trial 50 end = **250**

### Block-Level Triggers

**Block Start Codes:**
- Block N start = **150 + N**
- Range: 151-159 (supports up to 9 blocks)
- Examples:
  - Block 1 start = **151**
  - Block 2 start = **152**
  - Block 5 start = **155**

**Block End Codes:**
- Block N end = **250 + N**
- Range: 251-259 (supports up to 9 blocks)
- Examples:
  - Block 1 end = **251**
  - Block 2 end = **252**
  - Block 5 end = **255**

## Code Organization Rationale

The trigger codes are organized systematically to provide maximum informational resolution:

- **1-9:** Base trial events (e.g., `fixation`)
- **10-19:** Category A specific events
- **20-29:** Category B specific events
- **30-39:** Beep sequence events (8 unique beep codes)
- **40-49:** Reserved for future trial-level events
- **50-59:** Reserved for future block-level events
- **100-199:** Trial start codes (unique per trial)
- **150-159:** Block start codes (unique per block)
- **200-299:** Trial end codes (unique per trial)
- **250-259:** Block end codes (unique per block)

This systematic assignment provides:
1. **Unique identification** of every trial and block
2. **Easy decoding** - trial/block number can be extracted from code
3. **No overlaps** - all codes are unique
4. **Future expansion** - plenty of room for additional events

## Verification

The `scripts/check_triggers.py` script is used to verify the trigger mapping.

**Verification Results:**

- **Base triggers:** 14 unique codes
- **Dynamic range:** Supports up to 99 trials and 9 blocks
- **Total possible codes:** 14 base + up to 198 trial codes + up to 18 block codes = 230 codes maximum
- **Code range:** 1 - 299
- **Available range:** 0-255 (8-bit parallel port) - Note: codes 256-299 require 9-bit support

**Conclusion:** All trigger codes are unique, properly spaced, and provide maximum informational resolution for detailed analysis.

## Trigger Sequence Per Trial

1. `trial_N_start` (100+N) - Trial N begins
2. `fixation` (1) - Fixation cross appears
3. `concept_category_a` (10) OR `concept_category_b` (20) - Concept word shown
4. `beep_start` (30) - Beep sequence begins
5. `beep_1` (31) - First beep/repetition
6. `beep_2` (32) - Second beep/repetition
7. `beep_3` (33) - Third beep/repetition
8. `beep_4` (34) - Fourth beep/repetition
9. `beep_5` (35) - Fifth beep/repetition
10. `beep_6` (36) - Sixth beep/repetition
11. `beep_7` (37) - Seventh beep/repetition
12. `beep_8` (38) - Eighth beep/repetition
13. `trial_N_end` (200+N) - Trial N ends, rest period begins

## Block-Level Triggers

- `block_N_start` (150+N) - Block N begins (sent once at block start)
- `block_N_end` (250+N) - Block N ends (sent once at block end)

## Benefits of Dynamic Trigger Codes

1. **Trial-Level Analysis:** Identify exactly which trial had issues
2. **Block-Level Analysis:** Track performance across blocks
3. **Repetition-Level Analysis:** Each beep has unique code (31-38)
4. **Error Detection:** Pinpoint problematic trials/blocks/repetitions
5. **Detailed Logging:** Complete event history with full context
6. **Easy Decoding:** Extract trial/block number directly from trigger code

## Buffer Timing Considerations

**Critical:** Triggers are spaced to avoid buffer overflow issues:

- **Beep interval:** 0.8 seconds between beeps
  - Provides 800ms buffer time (well above minimum requirements)
  - Allows parallel port and EEG system to process each trigger
  - Prevents trigger loss or corruption

- **Other intervals:**
  - Fixation → Concept: 2.0s (plenty of buffer)
  - Concept → Post-pause: 2.0s + jittered pause
  - Post-pause → Beep start: Immediate (but beep_start → beep_1 has 0.8s)
  - Trial end → Next trial start: Inter-trial interval (0.5s + jitter)

**Best Practice:** The 0.8s beep interval ensures no back-to-back triggers, preventing buffer issues while maintaining rhythmic protocol timing.
