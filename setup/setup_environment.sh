#!/bin/bash
# Linux/Mac setup script for semantic visualization paradigm
# Creates conda environment and installs dependencies

echo "========================================"
echo "Semantic Visualization Paradigm Setup"
echo "========================================"
echo ""

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "ERROR: conda not found. Please install Anaconda or Miniconda first."
    exit 1
fi

echo "Creating conda environment 'repeat'..."
conda create -n repeat python=3.9 -y
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create conda environment."
    exit 1
fi

echo ""
echo "Activating environment and installing packages..."
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate repeat

if [ -f "environment.yml" ]; then
    echo "Installing from environment.yml..."
    conda env update -n repeat -f environment.yml --prune
elif [ -f "requirements.txt" ]; then
    echo "Installing from requirements.txt..."
    pip install -r requirements.txt
else
    echo "Installing core dependencies..."
    pip install psychopy numpy
fi

echo ""
echo "========================================"
echo "Setup complete!"
echo "========================================"
echo ""
echo "To activate the environment, run:"
echo "  conda activate repeat"
echo ""
echo "To run the experiment:"
echo "  python paradigm/scripts/run_experiment.py"
echo ""
