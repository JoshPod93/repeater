# Parameter Analysis: Comparing Current Settings to Successful Studies

## From Paradigm Paper (Table I) - Successful Rhythmic Protocols:

1. **BCI Competition** (100% significant performers):
   - Protocol: rhythmic
   - Time window: 2s
   - Trials per class: 70
   - Total trials: 140 (binary classification)

2. **Nguyen** (80%+ significant performers):
   - Protocol: rhythmic  
   - Time window: 1s
   - Trials per class: 100
   - Total trials: 200 (binary classification)

3. **Ours rhythm** (80%+ significant performers):
   - Protocol: rhythmic
   - Time window: 0.8s
   - Trials per class: 100
   - Total trials: 200 (binary classification)

4. **Tec** (rhythmic, successful):
   - Protocol: rhythmic
   - Time window: 1.4s
   - Trials per class: 30
   - Total trials: 60 (binary classification)

## From Email Correspondence:

- Alberto used **0.8s intervals** (matches "Ours rhythm" dataset)
- Other successful datasets used **1.4-2s intervals** (Tec, BCI Competition)
- **Key insight**: "only when I managed each repetition as a single trial did I get better results"
- This means: Each beep = one repetition = one analysis trial

## Current Parameters Analysis:

### ✅ CORRECT:
- **BEEP_INTERVAL = 0.8s** - Matches Alberto's successful protocol ("Ours rhythm")
- **FIXATION_DURATION = 2.0s** - Standard for BCI paradigms
- **PROMPT_DURATION = 2.0s** - Reasonable for concept presentation
- **REST_DURATION = 1.0s** - Standard rest period

### ⚠️ NEEDS ADJUSTMENT:
- **N_BEEPS = 8** - This is reasonable, but need to verify:
  - 8 beeps × 0.8s = 6.4s visualization period
  - Each beep = one repetition = one analysis trial
  - So 8 repetitions per concept presentation
  
- **N_TRIALS = 40** - **TOO LOW** compared to successful studies:
  - Current: 40 total trials = 20 per category
  - Successful studies: 60-200 total trials (30-100 per category)
  - **Recommendation**: Increase to at least 100 total trials (50 per category)
  - For full experiment: 200 total trials (100 per category) matches "Ours rhythm"

## Critical Insight from Email:

"only when I managed each repetition as a single trial did I get better results"

This means:
- Each beep repetition should be treated as a separate analysis trial
- With N_BEEPS = 8, each concept presentation gives 8 analysis trials
- With N_TRIALS = 40 concept presentations:
  - Total analysis trials = 40 × 8 = 320 repetitions
  - Per category = 20 × 8 = 160 repetitions per category
  
This is actually MORE than the 100 trials per class in successful studies!

But wait - the paper says "trials per class" which likely means concept presentations, not repetitions.

## Recommendation:

Based on successful studies, we should:
1. Keep BEEP_INTERVAL = 0.8s ✓
2. Keep N_BEEPS = 8 (gives 8 repetitions per concept) ✓
3. **Increase N_TRIALS to 100-200** for full experiment:
   - Minimum: 100 total trials (50 per category) - matches Tec
   - Optimal: 200 total trials (100 per category) - matches "Ours rhythm" and Nguyen
4. For testing/pilot: 40-60 trials is acceptable

## Window Length Analysis (from research summary):

- Range tested: 0.8 to 5 seconds
- Most favorable: **shorter time windows (up to 2 seconds)**
- Our beep interval (0.8s) is at the optimal short end ✓
- Each repetition window = 0.8s (matches successful protocols)
