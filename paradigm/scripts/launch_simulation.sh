#!/bin/bash

# Launch semantic_paradigm_simulation.py for multiple blocks
# Each execution runs ONE block only, automatically detecting the next block.

# To run this script from the project root in Git Bash:
#
# cd /c/Users/jp24194/Desktop/repeater
# ./paradigm/scripts/launch_simulation.sh
#
# Or make it executable and run directly:
#   chmod +x paradigm/scripts/launch_simulation.sh
#   ./paradigm/scripts/launch_simulation.sh [PARTICIPANT_ID] [NUMBER_OF_BEEPS_PER_TRIAL]

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

# Participant ID (default: sim_9999)
PARTICIPANT_ID=${1:-sim_9999}
# Number of beeps per trial (default: 8)
N_BEEPS=${2:-8}

echo "=========================================="
echo "Starting simulation blocks for participant: $PARTICIPANT_ID"
echo "Beeps per trial: $N_BEEPS"
echo "Each execution runs ONE block only (auto-detects next block)"
echo "=========================================="

# Run blocks sequentially - each execution auto-detects the next block
# We'll run until we get an error or the script indicates all blocks are done
block_count=1
while true; do
    echo ""
    echo "=========================================="
    echo "Block $block_count"
    echo "=========================================="
    
    echo "Python location: $(which python)"
    echo "Python version: $(python --version)"
    echo "Current directory: $(pwd)"
    echo "Starting simulation for block $block_count (auto-detected)..."
    echo ""
    echo "WARNING: Please be patient - it can take a moment before the simulation launches"
    echo ""
    
    # Run the simulation - it will auto-detect the next block
    # Use -u flag for unbuffered output so we see real-time progress
    python -u paradigm/semantic_paradigm_simulation.py --participant-id "$PARTICIPANT_ID" --n-beeps $N_BEEPS
    EXIT_CODE=$?
    
    # Check if the block was successful
    if [ $EXIT_CODE -eq 0 ]; then
        echo "Block $block_count completed successfully"
        block_count=$((block_count + 1))
    else
        echo "Block $block_count failed with exit code: $EXIT_CODE"
        echo "Stopping execution..."
        exit 1
    fi
    
    # Brief pause between blocks
    echo "Pausing 2 seconds before checking for next block..."
    sleep 2
done

echo ""
echo "=========================================="
echo "All simulation blocks completed!"
echo "=========================================="
