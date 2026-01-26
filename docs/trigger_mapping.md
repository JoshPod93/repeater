# Trigger Code Mapping

## Overview

This document provides a complete mapping of trigger codes to event names for the semantic visualization paradigm.

## Trigger Code Table

| Event Name | Code | Hex | Binary | Description |
|------------|------|-----|--------|-------------|
| `fixation` | 1 | 0x1 | 0b1 | Fixation cross appears |
| `trial_start` | 2 | 0x2 | 0b10 | Trial begins |
| `concept_category_a` | 10 | 0xa | 0b1010 | Concept word from Category A displayed |
| `concept_category_b` | 20 | 0x14 | 0b10100 | Concept word from Category B displayed |
| `beep_start` | 30 | 0x1e | 0b11110 | Start of beep sequence |
| `beep_1` | 31 | 0x1f | 0b11111 | First beep (repetition 1) |
| `beep_2` | 32 | 0x20 | 0b100000 | Second beep (repetition 2) |
| `beep_3` | 33 | 0x21 | 0b100001 | Third beep (repetition 3) |
| `beep_4` | 34 | 0x22 | 0b100010 | Fourth beep (repetition 4) |
| `beep_5` | 35 | 0x23 | 0b100011 | Fifth beep (repetition 5) |
| `beep_6` | 36 | 0x24 | 0b100100 | Sixth beep (repetition 6) |
| `beep_7` | 37 | 0x25 | 0b100101 | Seventh beep (repetition 7) |
| `beep_8` | 38 | 0x26 | 0b100110 | Eighth beep (repetition 8) |
| `trial_end` | 40 | 0x28 | 0b101000 | End of trial (rest period starts) |
| `block_start` | 50 | 0x32 | 0b110010 | Start of experimental block |
| `block_end` | 51 | 0x33 | 0b110011 | End of experimental block |

## Statistics

- **Total triggers:** 16
- **Unique codes:** 16 (no overlaps)
- **Code range:** 1 - 51
- **Available range:** 0-255 (8-bit parallel port)

## Code Organization

Codes are organized in groups of 10 for easy identification:

- **1-9:** Trial events (fixation, trial_start)
- **10-19:** Category A events
- **20-29:** Category B events  
- **30-39:** Beep sequence events (beep_start + 8 unique beep codes)
- **40-49:** Trial-level events
- **50-59:** Block-level events

## Usage in Codebase

All triggers are used in both:
- `paradigm/semantic_paradigm.py` (main experiment)
- `paradigm/semantic_paradigm_simulation.py` (simulation)

Each trigger appears exactly 2 times (once per file).

## Verification

✅ **No overlapping codes** - All 8 trigger codes are unique  
✅ **All codes used** - Every trigger code is referenced in the codebase  
✅ **Proper spacing** - Codes are spaced to allow for future expansion  

## Trigger Sequence Per Trial

1. `trial_start` (2) - Trial begins
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
13. `trial_end` (40) - Trial ends, rest period begins

## Block-Level Triggers

- `block_start` (50) - Sent once at experiment start
- `block_end` (51) - Sent once at experiment end

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
