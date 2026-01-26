# Launch Commands for Subject 9999 - 2 Blocks

## Quick Launch (Individual Commands)

Run these commands sequentially in your terminal:

### Block 1:
```bash
conda activate repeat
python paradigm/semantic_paradigm_simulation.py --participant-id 9999 --session 1 --block 1
```

### Block 2:
```bash
conda activate repeat
python paradigm/semantic_paradigm_simulation.py --participant-id 9999 --session 1 --block 2
```

## Using Launch Script (Bash/Git Bash)

If you're using Git Bash or Linux/Mac:

```bash
cd c:/Users/jp24194/Desktop/repeater
./paradigm/scripts/launch_simulation.sh 2
```

Note: The launch script uses `sim_9999` by default. To use `9999`, modify the script or use individual commands above.

## PowerShell Commands (Windows)

### Block 1:
```powershell
conda activate repeat
python paradigm/semantic_paradigm_simulation.py --participant-id 9999 --session 1 --block 1
```

### Block 2:
```powershell
conda activate repeat
python paradigm/semantic_paradigm_simulation.py --participant-id 9999 --session 1 --block 2
```

## Expected Configuration

Based on current config:
- **Total trials:** 100 (configured)
- **Total blocks:** 10 (configured)
- **Trials per block:** 10 (100 ÷ 10)
- **For 2 blocks:** 20 trials total (10 per block)
- **Concepts:** 10 items (5 per category)
- **Beeps per trial:** 8 (default)

## What to Review After Running

1. **Foldering:**
   - Check `data/results/Block_0000/` (block 1)
   - Check `data/results/Block_0001/` (block 2)
   - Check `data/results/sub-9999_ses-1_*_randomization_protocol.json`

2. **Pathing:**
   - Verify data files saved correctly
   - Check trigger CSV: `data/triggers/sub-9999_ses-1_*_triggers.csv`

3. **Randomization Protocol:**
   - Load protocol JSON and verify trial sequences
   - Check stratification (10 trials per concept-item across all blocks)
   - Verify unique patterns per block

4. **Trigger vs Ground Truth:**
   ```bash
   python scripts/validate_triggers.py --participant-id 9999 --session 1
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
python paradigm/semantic_paradigm_simulation.py --participant-id 9999 --session 1 --block 1 --n-beeps 3
```

## Verification Checklist

After running both blocks:

- [ ] Block folders created: `Block_0000/`, `Block_0001/`
- [ ] Randomization protocol saved: `*_randomization_protocol.json`
- [ ] Trigger CSV created: `*_triggers.csv`
- [ ] Data files saved: `*_trials.json`, `*_trials.npy`
- [ ] Validation passes: `python scripts/validate_triggers.py --participant-id 9999 --session 1`
- [ ] Trial counts match: 10 trials per block = 20 total
- [ ] Concept stratification: 2 trials per concept-item per block
