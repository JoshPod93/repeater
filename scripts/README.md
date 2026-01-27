# Scripts

Utility scripts for project management, testing, and validation.

## Git Utilities

### git_commit.py

Git commit tool for consistent, validated commits.

```bash
# Interactive commit
python scripts/git_commit.py

# Quick commit
python scripts/git_commit.py -m "Add feature X"

# With detailed description
python scripts/git_commit.py -m "Add feature X" -b "Detailed description"
```

See `docs/git_and_trigger_guide.md` for more details.

## Trigger Validation

### validate_triggers.py

Comprehensive trigger validation script comparing BDF file triggers (recorded) vs CSV mirror logs (sent).

**Requires:** `repeat_analyse` conda environment

```bash
conda activate repeat_analyse
python scripts/validate_triggers.py --participant-id 9999

# Or specify paths explicitly
python scripts/validate_triggers.py --bdf-file data/sub_9999/sub_9999.bdf --results-dir data/results/sub-9999_20260127_155544
```

**Features:**
- Strict sequential alignment
- Chronological sequence analysis
- Drop rate calculation
- Validation plots
- Missing trigger detection

### check_triggers.py

Checks trigger code mapping for uniqueness and shows usage across codebase.

```bash
python scripts/check_triggers.py
```

**Features:**
- Verifies all trigger codes are unique
- Shows trigger code mapping (decimal, hex, binary)
- Reports usage in paradigm files
- Statistics (total triggers, code range)

## Testing Scripts

### test_biosemi_connection.py

Test Biosemi serial port connection.

```bash
python scripts/test_biosemi_connection.py
```

### test_biosemi_triggers.py

Send test triggers to Biosemi hardware.

```bash
python scripts/test_biosemi_triggers.py --n-triggers 10
```

### test_randomization.py

Test randomization protocol generation.

```bash
python scripts/test_randomization.py
```

### test_config_randomization.py

Quick test of randomization with current config (2 categories, 5 items each). Tests both single block and full protocol generation.

```bash
python scripts/test_config_randomization.py
```

**Features:**
- Tests block sequence generation
- Validates concept distribution
- Checks full protocol (all blocks) balance
- No psychopy dependency (can run without full environment)

## Experiment Execution

### run_all_blocks.ps1 / run_all_blocks.sh

Runs all blocks sequentially for live experiments with automatic block detection. Waits for each block to complete before starting the next, with a 5-second pause between blocks.

**Windows:**
```powershell
# Run all 10 blocks for participant 9999
.\scripts\run_all_blocks.ps1 -ParticipantId 9999

# Run specific number of blocks
.\scripts\run_all_blocks.ps1 -ParticipantId 9999 -NBlocks 5

# Custom pause duration
.\scripts\run_all_blocks.ps1 -ParticipantId 9999 -PauseSeconds 10
```

**Linux/Mac:**
```bash
# Run all 10 blocks for participant 9999
bash scripts/run_all_blocks.sh 9999

# Run specific number of blocks
bash scripts/run_all_blocks.sh 9999 5
```

**Features:**
- Auto-detects next block (no manual block number needed)
- Waits for each block to complete before starting next
- Configurable pause between blocks (default: 5 seconds)
- Error handling (stops on failure)
- Progress indicators

**Note:** The script runs `paradigm/semantic_paradigm_live.py` which automatically detects and runs the next available block for the participant.

## Analysis Environment Setup

### setup_analysis_env.ps1 / setup_analysis_env.sh

Creates the `repeat_analyse` conda environment for validation and analysis tasks.

**Windows:**
```powershell
.\scripts\setup_analysis_env.ps1
```

**Linux/Mac:**
```bash
bash scripts/setup_analysis_env.sh
```

See `scripts/README_analysis_env.md` for details.
