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
| `beep` | 31 | 0x1f | 0b11111 | Individual beep (sent 8 times per trial) |
| `trial_end` | 40 | 0x28 | 0b101000 | End of trial (rest period starts) |
| `block_start` | 50 | 0x32 | 0b110010 | Start of experimental block |
| `block_end` | 51 | 0x33 | 0b110011 | End of experimental block |

## Statistics

- **Total triggers:** 9
- **Unique codes:** 9 (no overlaps)
- **Code range:** 1 - 51
- **Available range:** 0-255 (8-bit parallel port)

## Code Organization

Codes are organized in groups of 10 for easy identification:

- **1-9:** Trial events (fixation, trial_start)
- **10-19:** Category A events
- **20-29:** Category B events  
- **30-39:** Beep sequence events
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
5. `beep` (31) × 8 - Individual beeps (one per repetition)
6. `trial_end` (40) - Trial ends, rest period begins

## Block-Level Triggers

- `block_start` (50) - Sent once at experiment start
- `block_end` (51) - Sent once at experiment end

## Notes

- Trigger codes are sent via parallel port (default: 0x0378)
- Codes are held for 0.01 seconds (10ms) before resetting to 0
- All triggers are logged to CSV file with timestamps
- Triggers are sent to EEG stream FIRST, then logged (best practice)
