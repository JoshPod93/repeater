# Setup Scripts

Environment setup scripts for the semantic visualization paradigm.

## Usage

### Windows

```cmd
setup\setup_environment.bat
```

### Linux/Mac

```bash
chmod +x setup/setup_environment.sh
./setup/setup_environment.sh
```

## What They Do

1. Check for conda installation
2. Create conda environment named "repeat" with Python 3.9
3. Install dependencies from `environment.yml` or `requirements.txt`
4. Provide activation instructions

## Manual Setup

If scripts don't work, manually run:

```bash
conda create -n repeat python=3.9
conda activate repeat
conda env update -n repeat -f environment.yml --prune
```
