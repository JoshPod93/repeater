# PowerShell script to setup repeat_analyse conda environment
# For validation, preprocessing, and analysis tasks

Write-Host "Creating repeat_analyse conda environment..." -ForegroundColor Green

# Create conda environment with Python 3.10
conda create -n repeat_analyse python=3.10 -y

# Activate environment
conda activate repeat_analyse

# Install core scientific packages
conda install -y numpy scipy pandas matplotlib

# Install MNE for BDF/EEG processing
pip install mne

# Install pybdf as alternative (lighter weight)
pip install pybdf

# Install other useful analysis tools
pip install scikit-learn seaborn

Write-Host ""
Write-Host "[OK] repeat_analyse environment created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "To use it:" -ForegroundColor Yellow
Write-Host "  conda activate repeat_analyse"
Write-Host "  python scripts/validate_triggers.py --participant-id 9999"
Write-Host ""
