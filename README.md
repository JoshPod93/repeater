# Semantic Visualization Paradigm

**Adaptation of Speech Imagery BCI paradigm for semantic processing tasks**

Author: A. Tates (JP)  
BCI-NE Lab, University of Essex  
Date: January 26, 2026

## Installation

### Prerequisites

- Conda (Miniconda or Anaconda)
- Git
- Python 3.10+

### Setup Steps

1. **Clone the Repository**

```bash
git clone <repository-url>
cd repeater
```

2. **Create Conda Environments**

**Recommended method (using requirements files):**

```bash
# Create repeat environment (for running experiments)
conda create -n repeat python=3.10 -y
conda activate repeat
pip install -r requirements_repeat.txt

# Create repeat_analyse environment (for analysis)
conda create -n repeat_analyse python=3.10 -y
conda activate repeat_analyse
pip install -r requirements_repeat_analyse.txt
```

**Alternative method (using conda environment files):**

If you prefer to use the conda environment YAML files:

```bash
# Create repeat environment
conda env create -f environment_repeat.yml

# Create repeat_analyse environment
conda env create -f environment_repeat_analyse.yml
```

*Note: Some systems may encounter issues with conda environment creation due to cache or permission restrictions. If you encounter errors, use the requirements file method above.*

3. **Configure Biosemi Port (if needed)**

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

4. **Verify Installation**

```bash
# Activate repeat environment
conda activate repeat
python -c "from config import load_config; print('Config loaded successfully')"

# Activate repeat_analyse environment
conda activate repeat_analyse
python -c "import mne; print(f'MNE version: {mne.__version__}')"
```

## Quick Start

### Run Live Experiment

```bash
conda activate repeat
python paradigm/semantic_paradigm_live.py --participant-id 9999
```

### Run All Blocks

```bash
bash scripts/run_all_blocks.sh 9999
```

### Run Simulation

```bash
conda activate repeat
python paradigm/semantic_paradigm_simulation.py --participant-id sim_9999
```

### Validate Data

```bash
conda activate repeat_analyse
python scripts/validate_triggers.py --participant-id 9999
```

**For all available commands, see `launch_commands.md`**

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
└── requirements_repeat_analyse.txt  # Pip requirements for analysis
```

## Key Features

- **Trigger System**: EEG trigger sending via Biosemi serial port with CSV logging
- **Modular Design**: Separated utilities for triggers, display, data, and randomization
- **Configuration Management**: Centralized config with easy parameter modification
- **Data Logging**: Comprehensive per-trial data logging in JSON + NumPy formats
- **Block-based**: Self-contained blocks with automatic block detection

## Dependencies

See `environment_repeat.yml` and `environment_repeat_analyse.yml` for complete lists. Key dependencies:

- Python 3.10
- PsychoPy (stimulus presentation)
- numpy, scipy, pandas (scientific computing)
- mne (EEG processing - analysis environment)
- pyserial (Biosemi communication)

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

## Experimental Design

Each trial consists of:

1. **Trial indicator** - Shows trial number
2. **Concept presentation** (1.5s) - Shows word (e.g., "hand" or "apple")
3. **Visual mask** (0.3s) - Backward mask
4. **Fixation cross** (2.0s) - Prepares participant
5. **Rhythmic beep sequence** (6.4s) - 8 beeps at 0.8s intervals
6. **Rest period** (1.0s) - Blank screen

**Total per trial**: ~16 seconds  
**Trials per block**: 10  
**Blocks**: 10  
**Total trials**: 100

Based on research findings showing rhythmic protocols drive superior decoding accuracy.
