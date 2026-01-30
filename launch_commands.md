# Launch Commands

Quick reference for running all experiment and analysis commands.

**For initial setup on a new machine, see `README.md`**

## Prerequisites

Activate the appropriate conda environment:

```bash
# For running experiments
conda activate repeat

# For validation/analysis
conda activate repeat_analyse
```

## Experiment Execution

### Live Experiment (Single Block)

Run a single block with Biosemi EEG capture:

```bash
conda activate repeat
python paradigm/semantic_paradigm_live.py --participant-id 9999
```

The script automatically detects and runs the next available block for the participant.

### Live Experiment (All Blocks)

Run all 10 blocks sequentially:

**Windows (PowerShell):**
```powershell
.\scripts\run_all_blocks.ps1 -ParticipantId 9999
```

**Linux/Mac (Bash):**
```bash
bash scripts/run_all_blocks.sh 9999
```

**Git Bash (Windows):**
```bash
bash scripts/run_all_blocks.sh 9999
```

Options:
- `-NBlocks 5` - Run specific number of blocks
- `-PauseSeconds 10` - Custom pause between blocks (default: 5 seconds)

### Simulation Mode

Run simulation without hardware (for testing):

```bash
conda activate repeat
python paradigm/semantic_paradigm_simulation.py --participant-id sim_9999
```

## Testing & Validation

### Test Biosemi Connection

```bash
conda activate repeat
python scripts/test_biosemi_connection.py
```

### Test Biosemi Triggers

Send test triggers to verify hardware:

```bash
conda activate repeat
python scripts/test_biosemi_triggers.py --n-triggers 10
```

### Test Randomization

Verify randomization protocol generation:

```bash
conda activate repeat
python scripts/test_config_randomization.py
```

## Data Validation

### Quick Validation

Quick check of CSV vs BDF trigger alignment:

```bash
conda activate repeat_analyse
python scripts/validate_captured_data.py
```

### Comprehensive Trigger Validation

Detailed validation with plots and analysis:

```bash
conda activate repeat_analyse
python scripts/validate_triggers.py --participant-id 9999

# Or specify paths explicitly
python scripts/validate_triggers.py --bdf-file data/sub_9999/sub_9999.bdf --results-dir data/results/sub-9999_TIMESTAMP
```

### Comprehensive Data Evaluation

Complete evaluation report:

```bash
conda activate repeat_analyse
python scripts/comprehensive_data_evaluation.py
```

### Generate Ground Truth

Generate expected trigger sequence:

```bash
conda activate repeat
python scripts/generate_ground_truth_triggers.py --participant-id 9999
```


## Git Utilities

### Git Commit Tool

Interactive commit with validation:

```bash
python scripts/git_commit.py

# Quick commit
python scripts/git_commit.py -m "Add feature X"

# With detailed description
python scripts/git_commit.py -m "Add feature X" -b "Detailed description"
```

## File Locations

### Data Files
- BDF files: `data/sub_XXXX/sub_XXXX.bdf`
- Results: `data/results/sub-XXXX_TIMESTAMP/`
- CSV triggers: `data/results/sub-XXXX_TIMESTAMP/*_triggers.csv`

### Configuration
- Experiment config: `config/experiment_config.py`

### Scripts
- All scripts: `scripts/`
- Main experiment: `paradigm/semantic_paradigm_live.py`
- Simulation: `paradigm/semantic_paradigm_simulation.py`
