# Paradigm Package

Main experiment code for semantic visualization paradigm.

## Structure

- **`semantic_paradigm.py`**: Main experiment class
- **`scripts/run_experiment.py`**: CLI launcher script
- **`utils/`**: Utility function banks
  - `trigger_utils.py`: EEG trigger handling
  - `display_utils.py`: Visual stimulus management
  - `data_utils.py`: Data logging and saving
  - `randomization_utils.py`: Trial sequence generation

## Usage

```bash
# Run experiment
python paradigm/scripts/run_experiment.py --participant-id sub-001 --session 1

# With triggers
python paradigm/scripts/run_experiment.py --participant-id sub-001 --triggers

# Skip practice trials
python paradigm/scripts/run_experiment.py --participant-id sub-001 --no-practice
```

## Importing

```python
from paradigm.semantic_paradigm import SemanticVisualizationExperiment
from paradigm.utils import TriggerHandler, DisplayManager, create_balanced_sequence
```
