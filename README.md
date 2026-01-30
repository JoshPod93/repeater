# Semantic Visualization Paradigm

**Adaptation of Speech Imagery BCI paradigm for semantic processing tasks**

Author: A. Tates (JP)  
BCI-NE Lab, University of Essex  
Date: January 26, 2026

## Project Structure

```
repeater/
├── .cursorrules              # Cursor IDE rules and coding standards
├── environment.yml           # Conda environment specification
├── requirements.txt          # Python dependencies (if not using conda)
├── README.md                 # This file
│
├── setup/                    # Setup scripts
│   ├── setup_environment.sh  # Linux/Mac environment setup
│   ├── setup_environment.bat # Windows environment setup
│   └── README.md             # Setup instructions
│
├── scripts/                  # Utility scripts
│   ├── git_commit.py         # Git commit tool
│   ├── validate_triggers.py  # BDF vs CSV trigger validation
│   ├── validate_captured_data.py  # Quick validation
│   ├── comprehensive_data_evaluation.py  # Full data evaluation
│   ├── generate_ground_truth_triggers.py  # Ground truth generation
│   ├── test_biosemi_connection.py  # Biosemi connection test
│   ├── test_biosemi_triggers.py    # Biosemi trigger test
│   ├── test_config_randomization.py  # Randomization test
│   ├── run_all_blocks.sh     # Run all blocks (Linux/Mac)
│   ├── run_all_blocks.ps1    # Run all blocks (Windows)
│   ├── setup_analysis_env.ps1      # Analysis env setup (Windows)
│   ├── setup_analysis_env.sh       # Analysis env setup (Linux/Mac)
│   └── README.md             # Scripts documentation
│
├── paradigm/                 # Main experiment code
│   ├── __init__.py
│   ├── utils/                # Utility function banks
│   │   ├── __init__.py
│   │   ├── trigger_utils.py  # Trigger handling
│   │   ├── display_utils.py  # Visual presentation
│   │   ├── data_utils.py     # Data logging/saving
│   │   ├── randomization_utils.py  # Stimulus randomization
│   │   └── biosemi_utils.py  # Biosemi connection utilities
│   ├── semantic_paradigm_live.py  # Live experiment (with Biosemi)
│   └── semantic_paradigm_simulation.py  # Simulation variant (testing)
│
├── config/                   # Configuration files
│   ├── experiment_config.py  # Main experiment config
│   ├── load_config.py        # Config loader
│   └── __init__.py
│
├── data/                     # Experimental data/results ONLY
│   └── results/              # Subject results
│
├── analysis/                 # Analysis scripts
│   └── tangent_space_logistic_regressor_classifier.py
│
├── requirements_analysis.txt # Analysis environment dependencies
│
├── docs/                     # Documentation
│   ├── git_and_trigger_guide.md
│   └── speech_imagery_research_summary.md
│
├── examples/                 # Example code
│   └── rhytmic_experiment.py
│
└── tests/                    # Unit tests
    └── __init__.py
```

## Quick Start

### 1. Setup Environment

**For detailed setup instructions, see `SETUP.md`**

Quick setup:

```bash
# Create both conda environments
conda env create -f environment_repeat.yml
conda env create -f environment_repeat_analyse.yml

# Activate environment
conda activate repeat
```

### 2. Run Experiment

#### Live Mode (with Biosemi EEG capture):
```bash
# Run live experiment (single block - auto-detects next block)
python paradigm/semantic_paradigm_live.py --participant-id 9999

# Run all blocks sequentially
bash scripts/run_all_blocks.sh 9999
# Or on Windows PowerShell:
.\scripts\run_all_blocks.ps1 -ParticipantId 9999
```

#### Simulation Mode (for testing without hardware):
```bash
# Run simulation
python paradigm/semantic_paradigm_simulation.py --participant-id sim_9999
```

#### Test Biosemi Connection:
```bash
# Test Biosemi connection
python scripts/test_biosemi_connection.py --port COM3

# Test trigger sending
python scripts/test_biosemi_triggers.py --port COM3 --n-triggers 10
```

### 3. Analysis Environment

The `repeat_analyse` environment is already created in step 1. Activate it for validation/analysis:

```bash
conda activate repeat_analyse
python scripts/validate_triggers.py --participant-id 9999
```

For all available commands, see `launch_commands.md`.

## Development Guidelines

See `.cursorrules` for comprehensive coding standards. Key points:

* **Always use conda environment**: `conda activate repeat`
* **Use git for version control**: Commit frequently with descriptive messages
* **CLI for launching**: All scripts use command-line arguments
* **Modular code**: Small functions, dynamic pathing, clear separation of concerns
* **Clean codebase**: Remove redundant code, follow best practices

## Key Features

* **Trigger System**: EEG trigger sending via parallel port with dual logging (EEG first, then PsychoPy)
* **Modular Design**: Separated utilities for triggers, display, data, and randomization
* **Configuration Management**: Centralized config with easy parameter modification
* **Data Logging**: Comprehensive per-trial data logging in JSON + NumPy formats
* **Randomization**: Date/time-based seeding for unique trial sequences per participant

## Dependencies

See `environment_repeat.yml` and `environment_repeat_analyse.yml` for complete lists. Key dependencies:

* Python 3.10
* PsychoPy (stimulus presentation)
* numpy, scipy, pandas (scientific computing)
* mne (EEG processing - analysis environment)
* pyserial (Biosemi communication)

## Directory Organization Logic

* **`setup/`**: Setup scripts (environment initialization) - kept at root level for easy discovery
* **`scripts/`**: Utility scripts (git tools, etc.) - project-level utilities
* **`paradigm/`**: All experiment code, utilities, and launchers - self-contained experiment module
* **`config/`**: Configuration files - centralized parameter management
* **`data/`**: ONLY experimental results/data - clear separation from code and config
* **`analysis/`**: Analysis scripts - post-processing tools
* **`docs/`**: Documentation - project documentation
* **`tests/`**: Unit tests - test suite

## Git Workflow

Use the git commit tool for consistent commits:

```bash
python scripts/git_commit.py -m "Your commit message"
```

## Experimental Design

Each trial consists of:

1. **Fixation cross** (2.0s) - Prepares participant
2. **Concept presentation** (2.0s) - Shows word (e.g., "hand" or "apple")
3. **Rhythmic beep sequence** (6.4s) - 8 beeps at 0.8s intervals, blank screen
4. **Rest period** (1.0s) - Blank screen

**Total per trial**: ~11.4 seconds

Based on research findings showing rhythmic protocols drive superior decoding accuracy (R=0.60, p<0.005).

## License

[Add license information if applicable]

## About

Rhythmic Semantic Visualization Paradigm - BCI experiment adaptation from speech imagery to semantic visualization.
