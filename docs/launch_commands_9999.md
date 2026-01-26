# Launch Commands for Subject 9999 - 2 Blocks

## Quick Launch (Individual Commands)

Run these commands sequentially in your terminal:

### Block 1:
```bash
conda activate repeat
python paradigm/semantic_paradigm_simulation.py --participant-id 9999 --block 1
```

### Block 2:
```bash
conda activate repeat
python paradigm/semantic_paradigm_simulation.py --participant-id 9999 --block 2
```

## Expected Configuration

Based on current config:
- **Total trials:** 100 (configured)
- **Total blocks:** 10 (configured)
- **Trials per block:** 10 (100 ÷ 10)
- **For 2 blocks:** 20 trials total (10 per block)
- **Concepts:** 10 items (5 per category)
- **Beeps per trial:** 8 (default)

## Folder Structure

All subject data is organized in a single timestamped folder:

```
data/results/
  sub-9999_{timestamp}/
    ├── Block_0000/              (block 1 data)
    │   ├── sub-9999_{timestamp}_trials.json
    │   └── sub-9999_{timestamp}_trials.npy
    ├── Block_0001/              (block 2 data)
    │   ├── sub-9999_{timestamp}_trials.json
    │   └── sub-9999_{timestamp}_trials.npy
    ├── sub-9999_{timestamp}_randomization_protocol.json  (ground truth)
    └── sub-9999_{timestamp}_triggers.csv                (all triggers)
```

## What to Review After Running

1. **Foldering:**
   - Check `data/results/sub-9999_{timestamp}/` exists
   - Verify `Block_0000/` and `Block_0001/` folders created
   - Check `*_randomization_protocol.json` in subject folder
   - Check `*_triggers.csv` in subject folder (not separate triggers folder)

2. **Pathing:**
   - Verify all files saved in correct locations
   - Trigger CSV should be in subject folder, not `data/triggers/`

3. **Randomization Protocol:**
   - Load protocol JSON and verify trial sequences
   - Check stratification (10 trials per concept-item across all blocks)
   - Verify unique patterns per block

4. **Trigger vs Ground Truth:**
   ```bash
   python scripts/validate_triggers.py --participant-id 9999
   ```

5. **Stimuli Presentation:**
   - Review console output for timing
   - Check trigger timestamps in CSV
   - Verify beep intervals (0.8s)
   - Check concept presentation timing

## Rapid Testing (Fewer Beeps)

For faster testing, use `--n-beeps 3`:

```bash
conda activate repeat
python paradigm/semantic_paradigm_simulation.py --participant-id 9999 --block 1 --n-beeps 3
```

## Verification Checklist

After running both blocks:

- [ ] Subject folder created: `sub-9999_{timestamp}/`
- [ ] Block folders created: `Block_0000/`, `Block_0001/`
- [ ] Randomization protocol saved: `*_randomization_protocol.json` (in subject folder)
- [ ] Trigger CSV created: `*_triggers.csv` (in subject folder, not separate triggers folder)
- [ ] Data files saved: `*_trials.json`, `*_trials.npy` (in block folders)
- [ ] Validation passes: `python scripts/validate_triggers.py --participant-id 9999`
- [ ] Trial counts match: 10 trials per block = 20 total
- [ ] Concept stratification: 2 trials per concept-item per block
