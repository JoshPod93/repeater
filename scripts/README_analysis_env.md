# Analysis Environment Setup

This project uses a separate Python environment (`repeat_analyse`) for validation, preprocessing, and analysis tasks. This keeps analysis dependencies (like MNE) separate from the experiment runtime environment.

## Quick Setup

### Using Conda (Recommended)

**Windows (PowerShell):**
```powershell
.\scripts\setup_analysis_env.ps1
```

**Linux/Mac:**
```bash
bash scripts/setup_analysis_env.sh
```

### Manual Setup

1. Create conda environment:
   ```bash
   conda create -n repeat_analyse python=3.10 -y
   conda activate repeat_analyse
   ```

2. Install requirements:
   ```bash
   pip install -r requirements_analysis.txt
   ```

## Using the Analysis Environment

Activate the environment before running analysis scripts:

```bash
conda activate repeat_analyse
python scripts/validate_triggers.py --participant-id 9999
```

## Why a Separate Environment?

- **MNE-Python** is a heavy dependency that can conflict with experiment runtime
- Analysis tools often have different version requirements than experiment code
- Keeps experiment environment lean and focused on PsychoPy/Biosemi integration
- Allows independent updates to analysis tools without affecting experiment

## Included Packages

- **mne**: EEG/BDF file processing and trigger extraction
- **pybdf**: Lightweight alternative BDF reader
- **numpy/scipy/pandas**: Core scientific computing
- **matplotlib/seaborn**: Visualization
- **scikit-learn**: Machine learning utilities (for future analysis)
