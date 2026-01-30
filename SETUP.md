# Setup Guide - Semantic Visualization Paradigm

This guide will help you set up the project on a new machine.

## Prerequisites

- Conda (Miniconda or Anaconda)
- Git
- Python 3.10+

## Installation Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd repeater
```

### 2. Create Conda Environments

Create both required conda environments:

```bash
# Create repeat environment (for running experiments)
conda env create -f environment_repeat.yml

# Create repeat_analyse environment (for analysis)
conda env create -f environment_repeat_analyse.yml
```

Alternatively, using requirements files:

```bash
# Create repeat environment
conda create -n repeat python=3.10
conda activate repeat
pip install -r requirements_repeat.txt

# Create repeat_analyse environment
conda create -n repeat_analyse python=3.10
conda activate repeat_analyse
pip install -r requirements_repeat_analyse.txt
```

### 3. Configure Biosemi Port (if needed)

The default Biosemi port is `COM4` on Windows or `/dev/ttyUSB0` on Linux.

To override the default port, set an environment variable:

**Windows (PowerShell):**
```powershell
$env:BIOSEMI_PORT="COM3"
```

**Windows (CMD):**
```cmd
set BIOSEMI_PORT=COM3
```

**Linux/Mac:**
```bash
export BIOSEMI_PORT=/dev/ttyUSB1
```

Or edit `config/experiment_config.py` to change the default.

### 4. Verify Installation

```bash
# Activate repeat environment
conda activate repeat

# Test import
python -c "from config import load_config; print('Config loaded successfully')"

# Activate repeat_analyse environment
conda activate repeat_analyse

# Test MNE import
python -c "import mne; print(f'MNE version: {mne.__version__}')"
```

## Project Structure

```
repeater/
├── config/              # Configuration files
├── paradigm/            # Experiment code
│   ├── semantic_paradigm_live.py      # Live experiment
│   ├── semantic_paradigm_simulation.py # Simulation
│   └── utils/           # Utility modules
├── scripts/             # Utility scripts
├── data/                # Data directory (created automatically)
│   ├── results/         # Experiment results
│   └── sub_*/           # BDF files
├── docs/                # Documentation
├── environment_repeat.yml           # Conda env for experiments
├── environment_repeat_analyse.yml   # Conda env for analysis
├── requirements_repeat.txt          # Pip requirements for experiments
├── requirements_repeat_analyse.txt  # Pip requirements for analysis
└── SETUP.md             # This file
```

## Running Experiments

### Live Experiment (with Biosemi)

```bash
conda activate repeat
python paradigm/semantic_paradigm_live.py --participant-id P001
```

### Simulation (no hardware)

```bash
conda activate repeat
python paradigm/semantic_paradigm_simulation.py --participant-id sim_001
```

### Run All Blocks

```bash
conda activate repeat
bash scripts/run_all_blocks.sh P001
```

## Analysis and Validation

```bash
conda activate repeat_analyse
python scripts/validate_triggers.py --participant-id P001
python scripts/validate_captured_data.py --participant-id P001
```

## Troubleshooting

### Serial Port Issues

- **Windows**: Check Device Manager for COM port number
- **Linux**: Check `/dev/ttyUSB*` or `/dev/ttyACM*` devices
- Ensure no other software is using the port
- Try different port numbers if default doesn't work

### Import Errors

- Ensure correct conda environment is activated
- Reinstall dependencies: `pip install -r requirements_*.txt`
- Check Python version: `python --version` (should be 3.10+)

### Path Issues

- All paths use `pathlib.Path` for cross-platform compatibility
- Data directories are created automatically
- No hardcoded absolute paths in code

## Notes

- All paths are relative to project root
- No hardcoded user-specific paths
- Environment variables can override defaults
- Works on Windows, Linux, and Mac (with appropriate serial port configuration)
