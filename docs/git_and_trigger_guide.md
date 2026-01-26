# Git Configuration and Remote Setup Guide

## Secure Token Usage

**NEVER commit tokens directly in code or git history!**

### Setting up Remote Repository (Secure Method)

#### Option 1: Using Git Credential Helper (Recommended)
```bash
# Configure credential helper to store token securely
git config --global credential.helper wincred  # Windows
# or
git config --global credential.helper store     # Cross-platform

# When pushing, git will prompt for credentials
# Username: your-github-username
# Password: YOUR_GITHUB_TOKEN_HERE
```

#### Option 2: Using Environment Variable
```bash
# Set token as environment variable (Windows PowerShell)
$env:GIT_TOKEN="YOUR_GITHUB_TOKEN_HERE"

# Add remote with token in URL (one-time)
git remote add origin https://${env:GIT_TOKEN}@github.com/username/repo.git
```

#### Option 3: Using SSH (Most Secure)
```bash
# Generate SSH key if you don't have one
ssh-keygen -t ed25519 -C "your_email@example.com"

# Add SSH key to GitHub account
# Then use SSH URL instead of HTTPS
git remote add origin git@github.com:username/repo.git
```

## Common Git Commands

### Basic Workflow
```bash
# Check status
git status

# Add files
git add .                    # All files
git add specific_file.py      # Specific file

# Commit
git commit -m "Descriptive commit message"

# Push to remote
git push origin main         # or master
git push origin main --force  # Force push (use with caution)

# Pull from remote
git pull origin main
```

### Branch Management
```bash
# Create and switch to new branch
git checkout -b feature-branch-name

# Switch branches
git checkout branch-name

# List branches
git branch

# Merge branch
git checkout main
git merge feature-branch-name
```

### Viewing History
```bash
# View commit history
git log --oneline
git log --graph --oneline --all

# View changes in a file
git diff filename.py
git diff HEAD~1 filename.py  # Compare with previous version
```

## EEG Trigger Methods

### Parallel Port Setup (Windows)
```python
from psychopy import parallel

# Standard LPT1 address
PARALLEL_PORT_ADDRESS = 0x0378

# Initialize port
try:
    port = parallel.ParallelPort(address=PARALLEL_PORT_ADDRESS)
    print(f"Parallel port initialized at {hex(PARALLEL_PORT_ADDRESS)}")
except Exception as e:
    print(f"Warning: Could not initialize parallel port: {e}")
```

### Sending Triggers
```python
def send_trigger(trigger_code, port, duration=0.01):
    """
    Send EEG trigger via parallel port.
    
    Parameters
    ----------
    trigger_code : int
        Trigger code to send (0-255)
    port : parallel.ParallelPort
        Initialized parallel port object
    duration : float
        How long to hold trigger (seconds)
    """
    try:
        port.setData(trigger_code)
        core.wait(duration)  # Hold trigger
        port.setData(0)      # Reset to zero
        return True
    except Exception as e:
        print(f"Warning: Failed to send trigger {trigger_code}: {e}")
        return False
```

### Trigger Code Convention
```python
TRIGGER_CODES = {
    'fixation': 1,
    'concept_category_a': 10,
    'concept_category_b': 20,
    'beep_start': 30,
    'beep': 31,
    'trial_end': 40,
    'block_start': 50,
    'block_end': 51
}
```

## CLI Methods for Script Execution

### Running Experiments
```bash
# Activate conda environment first
conda activate repeat

# Simple version (testing)
python rhythmic_semantic_visualization.py

# Full-featured version (with data collection)
python rhythmic_semantic_enhanced.py

# With arguments (if implemented)
python rhythmic_semantic_enhanced.py --participant-id sub-001 --session 1
```

### Analysis Pipeline
```bash
# Run tangent space logistic regression classifier
python examples/tangent_space_logistic_regressor_classifier.py -c hand apple

# With MNE epochs file
python examples/tangent_space_logistic_regressor_classifier.py -c category_a category_b
```

## Troubleshooting

### Git Issues
- **Permission denied**: Check file permissions, ensure files aren't locked
- **Merge conflicts**: Use `git status` to see conflicts, edit files, then `git add` and `git commit`
- **Remote not found**: Check `git remote -v` to see configured remotes

### Parallel Port Issues
- **Port not found**: Check device manager for LPT port, verify address
- **Permission error**: Run as administrator or check port permissions
- **Trigger not received**: Verify port address, check cable connection, test with oscilloscope

### PsychoPy Issues
- **Window not opening**: Check display settings, try windowed mode first
- **Sound not playing**: Check audio device, try different frequency
- **Timing issues**: Close other applications, disable CPU throttling

## Useful Resources

- Git documentation: https://git-scm.com/doc
- PsychoPy documentation: https://www.psychopy.org/
- MNE-Python: https://mne.tools/
- PyRiemann: https://pyriemann.readthedocs.io/
