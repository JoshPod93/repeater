# Trial Timing: All Pauses and Wait Periods

Complete list of all pauses, waits, and intervals during a single trial period.

## Configuration Values (from `config/experiment_config.py`)

- `FIXATION_DURATION = 2.0` seconds
- `PROMPT_DURATION = 2.0` seconds  
- `POST_CONCEPT_PAUSE = 1.0` seconds
- `BEEP_INTERVAL = 0.8` seconds (between beeps)
- `N_BEEPS = 8` (number of beeps)
- `REST_DURATION = 1.0` seconds
- `INTER_TRIAL_INTERVAL = 0.5` seconds
- `USE_JITTER = True`
- `JITTER_RANGE = 0.1` (+/-10%)

---

## Chronological List of All Pauses During a Single Trial

### 1. **Fixation Cross Display**
- **Duration**: `FIXATION_DURATION = 2.0` seconds
- **Jitter**: **NO JITTER** (critical timing)
- **Location**: Start of trial, before concept presentation
- **Visual**: Fixation cross displayed
- **Purpose**: Baseline/preparation period

### 2. **Concept Word Display**
- **Duration**: `PROMPT_DURATION = 2.0` seconds
- **Jitter**: **NO JITTER** (critical timing)
- **Location**: After fixation, concept word shown
- **Visual**: Concept word displayed (upper or lower case)
- **Purpose**: Participant reads and initiates visualization

### 3. **Visual Mask**
- **Duration**: `MASK_DURATION = 0.2` seconds
- **Jitter**: **NO JITTER** (critical timing)
- **Location**: Immediately after concept disappears
- **Visual**: Pattern mask (noise stimulus) to prevent afterimages
- **Purpose**: Erase visual afterimages from concept presentation

### 4. **Post-Concept Pause** [JITTERED]
- **Duration**: `POST_CONCEPT_PAUSE = 1.0` seconds (+/-10% jitter)
- **Jitter**: **YES** - Uses `jittered_wait()` with `JITTER_RANGE = 0.1`
- **Actual Range**: 0.9 - 1.1 seconds (randomized per trial)
- **Location**: After mask disappears, before beeps start
- **Visual**: Blank screen (mask cleared)
- **Purpose**: Transition pause before visualization period

### 5. **Beep Intervals** (8 intervals total)
- **Duration**: `BEEP_INTERVAL = 0.8` seconds each
- **Jitter**: **NO JITTER** (critical for rhythmic protocol)
- **Location**: Between each beep during visualization period
- **Visual**: Fixation cross stays on screen
- **Total Duration**: 8 × 0.8s = **6.4 seconds**
- **Purpose**: Rhythmic cue intervals for visualization repetitions

### 6. **Rest Period** [JITTERED]
- **Duration**: `REST_DURATION = 1.0` seconds (+/-10% jitter)
- **Jitter**: **YES** - Uses `jittered_wait()` with `JITTER_RANGE = 0.1`
- **Actual Range**: 0.9 - 1.1 seconds (randomized per trial)
- **Location**: After visualization period (all beeps complete)
- **Visual**: Blank screen
- **Purpose**: Post-trial rest period

### 7. **Inter-Trial Interval** [JITTERED]
- **Duration**: `INTER_TRIAL_INTERVAL = 0.5` seconds (+/-10% jitter)
- **Jitter**: **YES** - Uses `jittered_wait()` with `JITTER_RANGE = 0.1`
- **Actual Range**: 0.45 - 0.55 seconds (randomized per trial)
- **Location**: Between trials (only if not last trial in block)
- **Visual**: Blank screen
- **Purpose**: Break between trials to prevent fatigue

---

## Summary Table

| Pause Name | Duration (s) | Jittered? | When | Visual |
|------------|--------------|-----------|------|--------|
| Fixation Cross | 2.0 | No | Start of trial | Fixation cross |
| Concept Display | 2.0 | No | After fixation | Concept word |
| Visual Mask | 0.2 | No | After concept | Pattern mask |
| Post-Concept Pause | 1.0 (+/-0.1) | Yes | After mask | Blank screen |
| Beep Interval #1 | 0.8 | No | After beep 1 | Fixation cross |
| Beep Interval #2 | 0.8 | No | After beep 2 | Fixation cross |
| Beep Interval #3 | 0.8 | No | After beep 3 | Fixation cross |
| Beep Interval #4 | 0.8 | No | After beep 4 | Fixation cross |
| Beep Interval #5 | 0.8 | No | After beep 5 | Fixation cross |
| Beep Interval #6 | 0.8 | No | After beep 6 | Fixation cross |
| Beep Interval #7 | 0.8 | No | After beep 7 | Fixation cross |
| Beep Interval #8 | 0.8 | No | After beep 8 | Fixation cross |
| Rest Period | 1.0 (+/-0.1) | Yes | After beeps | Blank screen |
| Inter-Trial Interval | 0.5 (+/-0.05) | Yes | Between trials | Blank screen |

---

## Total Trial Duration Calculation

**Fixed Components** (no jitter):
- Fixation: 2.0s
- Concept display: 2.0s
- Visual mask: 0.2s
- Beep intervals: 8 × 0.8s = 6.4s
- **Fixed subtotal**: 10.6s

**Jittered Components** (varies per trial):
- Post-concept pause: ~1.0s (+/-0.1s)
- Rest period: ~1.0s (+/-0.1s)
- Inter-trial interval: ~0.5s (+/-0.05s) [only between trials]

**Total per trial** (excluding inter-trial interval):
- Minimum: 10.4 + 0.9 + 0.9 = **12.2 seconds**
- Maximum: 10.4 + 1.1 + 1.1 = **12.6 seconds**
- Average: 10.4 + 1.0 + 1.0 = **12.4 seconds**

**With inter-trial interval** (between trials):
- Minimum: 12.2 + 0.45 = **12.65 seconds**
- Maximum: 12.6 + 0.55 = **13.15 seconds**
- Average: 12.4 + 0.5 = **12.9 seconds**

**Per block** (10 trials):
- Average: (12.4 × 10) + (0.5 × 9) = 124 + 4.5 = **128.5 seconds** (~2.14 minutes)

---

## Notes

1. **No Jitter Applied To**:
   - Fixation duration (critical baseline)
   - Concept presentation duration (critical for reading/initiation)
   - Visual mask duration (critical for afterimage prevention)
   - Beep intervals (critical for rhythmic protocol - must be exact 0.8s)

2. **Jitter Applied To**:
   - Post-concept pause (transition period)
   - Rest period (post-trial pause)
   - Inter-trial interval (between-trial break)

3. **Jitter Range**: +/-10% (`JITTER_RANGE = 0.1`)
   - Prevents anticipatory responses
   - Reduces temporal predictability
   - Only applied to non-critical pause events

4. **Block Structure**:
   - 10 trials per block
   - Inter-trial interval only occurs between trials (not after last trial)
   - Block breaks are user-initiated (not timed pauses)
