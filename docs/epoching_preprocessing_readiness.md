# Epoching & Preprocessing Readiness

## Trigger & data check (session sub-8888_20260130_124255)

- **Blocks:** 10/10 (Block_0000 … Block_0009).
- **Triggers:** 1520/1520 (1 CSV at session level).
- **Codes:** Block 61–70 (start), 71–80 (end); trial 101–110 (start), 151–160 (end); fixation 1, trial_indicator 3, concept 10/20, mask 25, beep_start 30, beeps 31–38. Code range 1–160, 8-bit safe.
- **Base counts:** Fixation 100, Concept A 50, Concept B 50, beep_start 100, beeps 800.
- **Evaluation:** `python scripts/comprehensive_data_evaluation.py --participant-id 8888` → **[COMPLETE]**.

## Pathing

| What | Where |
|------|--------|
| **Results (paradigm)** | `data/results/sub-{ID}_{YYYYMMDD}_{HHMMSS}/` |
| **Per block** | `Block_0000/` … `Block_0009/` each with `sub-*_trials.json` (and `sub-*_trials.npy` if saved; `.npy` is gitignored) |
| **Trigger CSV** | `data/results/sub-{ID}_{timestamp}/sub-{ID}_{timestamp}_triggers.csv` |
| **Randomization** | `data/results/sub-{ID}_{timestamp}/sub-{ID}_{timestamp}_randomization_protocol.json` |
| **BDF (expected for validation & epoching)** | `data/sub_{ID}/sub_{ID}.bdf` |

So for participant 8888:

- Results: `data/results/sub-8888_20260130_124255/`
- BDF (you must place/record here for epoching): `data/sub_8888/sub_8888.bdf`

## BDF ↔ CSV validation (before epoching)

Once the BDF is in place:

```bash
python scripts/validate_triggers.py --participant-id 8888
# or with explicit paths:
python scripts/validate_triggers.py --bdf-file data/sub_8888/sub_8888.bdf --results-dir data/results/sub-8888_20260130_124255
```

```bash
python scripts/validate_captured_data.py --participant-id 8888
```

These check that BDF trigger count and sequence match the CSV (1520 triggers, same order).

## Ready for epoching?

- **Paradigm side:** Yes. Triggers and trial/block structure are complete and validated; pathing is as above.
- **BDF:** You need the continuous EEG file at `data/sub_8888/sub_8888.bdf` (same run as the session `sub-8888_20260130_124255`).
- **Epoch creation:** The repo does **not** yet contain a script that builds epochs from BDF + events. The analysis script `analysis/tangent_space_logistic_regressor_classifier.py` expects **pre-made epochs** in `ica_epo.fif` (per subject folder).

So you are ready to **add** a preprocessing pipeline that:

1. Loads raw BDF: `mne.io.read_raw_bdf('data/sub_8888/sub_8888.bdf')`
2. Extracts events from the Status channel (same codes as in the trigger CSV; see `docs/trigger_mapping.md`).
3. Builds epochs (e.g. around concept onset with `event_id={'Category_A': 10, 'Category_B': 20}`, or around beeps 31–38).
4. Applies filtering, baseline, optional ICA.
5. Saves epochs (e.g. `ica_epo.fif`) in a subject directory layout that your analysis script expects.

After that pipeline is in place and run, epoching and preprocessing are ready to use with the current analysis code.
