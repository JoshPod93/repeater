# Trigger Code Mapping for Semantic Visualization Paradigm

This document lists **every trigger actually sent** in the live experiment. **All codes are 1–160; nothing goes to 200 or 300.** Biosemi uses 8-bit triggers (0–255), and we stay well within that.

**Source of truth:** Codes and event names are taken from:
- `paradigm/utils/trigger_utils.py` — `TRIGGER_CODES`, `get_trial_start_code`, `get_trial_end_code`, `get_block_start_code`, `get_block_end_code`, `get_beep_code` / `get_beep_codes`
- `paradigm/semantic_paradigm_live.py` — every `send_trigger()` / `_log_trigger_to_csv()` call

The trigger CSV columns are: `timestamp_psychopy`, `timestamp_absolute`, `trigger_code`, `event_name`, `sent_to_eeg`. The tables below match what appears in that CSV.

---

## Base Trigger Codes (fixed codes, no trial/block index)

The following table lists the base trigger codes (used for events that don't vary by trial/block number):

| Code | Event Name (CSV `event_name`) | Description |
| :--- | :---------------------------- | :---------- |
| 1    | `fixation`                    | Fixation cross appears (before beeps) |
| 3    | `trial_indicator_N`            | Trial number shown (N = 1–10); e.g. `trial_indicator_1` |
| 10   | `concept_{word}_category_A`    | Category A concept onset; e.g. `concept_leg_category_A` |
| 20   | `concept_{word}_category_B`    | Category B concept onset; e.g. `concept_grape_category_B` |
| 25   | `mask`                         | Mask onset (after concept) |
| 30   | `beep_start`                   | Start of beep sequence |
| 31–38| `beep_1_8`, `beep_2_8`, …, `beep_8_8` | Each beep onset; 0.8 s apart |

**Block-level (N = block number 1–10); CSV e.g. `block_1_start`, `block_1_end`:**

| Event Name      | Code   | Description              |
| :-------------- | :----- | :----------------------- |
| `block_N_start` | **60+N** (61–70) | Block N begins (sent once per block) |
| `block_N_end`   | **70+N** (71–80) | Block N ends (sent once per block)   |

## Dynamic Trigger Codes

### Trial-Level Triggers

**Trial Start Codes:**
- Trial N start = **100 + block_local_trial** (N = trial 1–10 within block)
- Range: **101–110** only (10 trials per block)
- Examples: Trial 1 start = **101**, Trial 10 start = **110**

**Trial End Codes:**
- Trial N end = **150 + (N mod 10)** (block-local trial 1–10)
- Range: 151–160
- Examples: Trial 1 end = **151**, Trial 10 end = **160**

### Block-Level Triggers

**Block Start Codes:**
- Block N start = **60 + N**
- Range: 61–70 (supports up to 10 blocks)
- Examples: Block 1 start = **61**, Block 2 start = **62**

**Block End Codes:**
- Block N end = **70 + N**
- Range: 71–80
- Examples: Block 1 end = **71**, Block 2 end = **72**

## Code Organization Rationale

All codes fit in **8-bit (0–255)**. Biosemi and our pipeline use single-byte triggers; nothing exceeds 255.

- **1–9:** Base trial events (fixation=1, trial_indicator=3)
- **10–19:** Category A (concept = 10)
- **20–29:** Category B (concept = 20), mask = 25
- **30–39:** Beep sequence (beep_start=30, beep_1–8 = 31–38)
- **60–70:** Block start (block N start = 60+N → 61–70)
- **71–80:** Block end (block N end = 70+N → 71–80)
- **101–110:** Trial start (trial 1–10 within block)
- **151–160:** Trial end (trial 1–10 within block)

**Maximum code used: 160.** No codes in the 200s or 300s.

## Verification

- **Code range used:** 1–160 (all within 0–255, Biosemi 8-bit safe)
- **Trial codes:** 101–110 (start), 151–160 (end) — block-local trial 1–10
- **Block codes:** 61–70 (start), 71–80 (end)
- Run `scripts/validate_triggers.py` and `scripts/validate_captured_data.py` to check BDF vs CSV.

## Full Trigger Sequence (per block)

**Block boundaries (once per block):**
- **Block start:** `block_N_start` → code **60+N** (61, 62, … 70) – sent at block start, before any trials.
- **Block end:** `block_N_end` → code **70+N** (71, 72, … 80) – sent after the last trial in the block.

**Per trial** (each trigger at event onset):

1. `trial_N_start` (101–110) – trial begins  
2. `trial_indicator_N` (3) – trial number shown  
3. `concept_X_category_A` (10) OR `concept_X_category_B` (20) – concept word onset  
4. `mask` (25) – mask onset  
5. `fixation` (1) – fixation before beeps  
6. `beep_start` (30) – beep sequence start  
7. `beep_1_8` … `beep_8_8` (31–38) – each beep onset (0.8 s apart)  
8. `trial_N_end` (151–160) – trial end, rest begins  

So the full order is: **block_N_start** → (trial 1 … trial 10) → **block_N_end**.  

## Epoching

All codes are in 0–255 (Biosemi-safe). Triggers are sent at stimulus onset, so BDF events are suitable for building epochs.

**Concept-locked epochs (Category A vs B):**
- Use event codes **10** (Category A) and **20** (Category B) at concept word onset.  
- MNE `event_id`: e.g. `{'Category_A': 10, 'Category_B': 20}`.

**Beep/repetition-locked epochs:**
- Use event codes **31–38** for the 8 beeps (0.8 s SOA).  
- Epoch around each beep for repetition-level analysis.

**Trial boundaries:**
- Trial start: **101–110**; trial end: **151–160** (block-local trial index 1–10).  
- Block boundaries: **61–70** (start), **71–80** (end).

Validation: run `scripts/validate_triggers.py` (BDF vs CSV) and `scripts/validate_captured_data.py` to confirm trigger count and sequence match.

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
