#!/bin/bash

# Launch semantic_paradigm_simulation.py for multiple blocks
# Each execution runs ONE block only (similar to grasp/paradigm pattern)
#
# To run this script from the paradigm folder in Git Bash:
#
# cd /c/Users/jp24194/Desktop/repeater
# ./paradigm/scripts/launch_simulation.sh
#
# Or make it executable and run directly:
#   chmod +x paradigm/scripts/launch_simulation.sh
#   ./paradigm/scripts/launch_simulation.sh

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Change to project root
cd "$PROJECT_ROOT"

# Verify semantic_paradigm_simulation.py exists
if [ ! -f "paradigm/semantic_paradigm_simulation.py" ]; then
    echo "ERROR: paradigm/semantic_paradigm_simulation.py not found"
    echo "Please run this script from the project root"
    exit 1
fi

# Activate the repeat conda environment
echo "Activating conda environment 'repeat'..."
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate repeat

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate conda environment 'repeat'"
    echo "Please ensure the 'repeat' environment exists"
    exit 1
fi

echo "Conda environment activated"

# Number of blocks to run (default: 3)
TOTAL_BLOCKS=${1:-3}

echo "=========================================="
echo "Starting $TOTAL_BLOCKS simulation blocks"
echo "Each execution runs ONE block only"
echo "=========================================="

for block_num in $(seq 1 $TOTAL_BLOCKS); do
    echo ""
    echo "=========================================="
    echo "Block $block_num/$TOTAL_BLOCKS"
    echo "=========================================="
    
    echo "Python location: $(which python)"
    echo "Python version: $(python --version)"
    echo "Current directory: $(pwd)"
    echo "Starting simulation for block $block_num..."
    echo ""
    echo "WARNING: Please be patient - it can take a moment before the simulation launches"
    echo ""
    
    # Run the simulation for this block only
    # Use -u flag for unbuffered output so we see real-time progress
    python -u paradigm/semantic_paradigm_simulation.py --block $block_num --participant-id sim_9999
    EXIT_CODE=$?
    
    # Check if the block was successful
    if [ $EXIT_CODE -eq 0 ]; then
        echo "Block $block_num completed successfully"
    else
        echo "Block $block_num failed with exit code: $EXIT_CODE"
        echo "Stopping execution..."
        exit 1
    fi
    
    # Brief pause between blocks (except after last block)
    if [ $block_num -lt $TOTAL_BLOCKS ]; then
        echo "Pausing 5 seconds before next block..."
        sleep 5
    fi
done

echo ""
echo "=========================================="
echo "All $TOTAL_BLOCKS simulation blocks completed!"
echo "=========================================="
