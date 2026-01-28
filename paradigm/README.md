# Paradigm Package

Main experiment code for semantic visualization paradigm.

## Structure

- **`semantic_paradigm_live.py`**: Live experiment with Biosemi EEG capture
- **`semantic_paradigm_simulation.py`**: Simulation variant for testing
- **`utils/`**: Utility function banks
  - `trigger_utils.py`: EEG trigger handling
  - `display_utils.py`: Visual stimulus management
  - `data_utils.py`: Data logging and saving
  - `randomization_utils.py`: Trial sequence generation
  - `biosemi_utils.py`: Biosemi connection utilities
  - `block_utils.py`: Block management utilities
  - `audio_utils.py`: Audio/beep utilities
  - `timing_utils.py`: Timing and jitter utilities

## Usage

```bash
# Run live experiment (single block - auto-detects next block)
python paradigm/semantic_paradigm_live.py --participant-id 9999

# Run simulation
python paradigm/semantic_paradigm_simulation.py --participant-id sim_9999

# Run all blocks sequentially
bash scripts/run_all_blocks.sh 9999
```

## Importing

```python
from paradigm.semantic_paradigm import SemanticVisualizationExperiment
from paradigm.utils import TriggerHandler, DisplayManager, create_balanced_sequence
```
