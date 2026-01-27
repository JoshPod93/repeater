#!/bin/bash
# Setup script for repeat_analyse conda environment
# For validation, preprocessing, and analysis tasks

echo "Creating repeat_analyse conda environment..."

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

echo ""
echo "✅ repeat_analyse environment created successfully!"
echo ""
echo "To use it:"
echo "  conda activate repeat_analyse"
echo "  python scripts/validate_triggers.py --participant-id 9999"
echo ""
