#!/bin/bash
# Run all blocks sequentially for live experiment
#
# Usage:
#   ./scripts/run_all_blocks.sh [participant_id] [n_blocks]
#
# Examples:
#   # Run all 10 blocks for participant 9999 (default)
#   ./scripts/run_all_blocks.sh
#
#   # Run all 10 blocks for specific participant
#   ./scripts/run_all_blocks.sh P001
#
#   # Run specific number of blocks (e.g., 2 blocks for testing)
#   ./scripts/run_all_blocks.sh 9999 2
#
# Notes:
#   - Automatically activates conda environment 'repeat'
#   - Auto-detects next block (no manual block number needed)
#   - Waits for each block to complete before starting next
#   - 5 second pause between blocks (configurable via PAUSE_SECONDS variable)
#   - Stops on error if any block fails

set -e  # Exit on error

# Default values
PARTICIPANT_ID="${1:-9999}"
N_BLOCKS="${2:-10}"
PAUSE_SECONDS=5

echo "=========================================="
echo "Running All Blocks - Live Experiment"
echo "=========================================="
echo "Participant ID: $PARTICIPANT_ID"
echo "Number of blocks: $N_BLOCKS"
echo "Pause between blocks: ${PAUSE_SECONDS}s"
echo "=========================================="
echo ""

# Get the project root directory (parent of scripts/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Change to project root
cd "$PROJECT_ROOT"

# Initialize conda (if not already initialized)
if ! command -v conda &> /dev/null; then
    # Try to find conda installation
    if [ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]; then
        source "$HOME/miniconda3/etc/profile.d/conda.sh"
    elif [ -f "$HOME/anaconda3/etc/profile.d/conda.sh" ]; then
        source "$HOME/anaconda3/etc/profile.d/conda.sh"
    elif [ -f "/opt/conda/etc/profile.d/conda.sh" ]; then
        source "/opt/conda/etc/profile.d/conda.sh"
    else
        echo "ERROR: conda not found. Please initialize conda first."
        echo "Run: eval \"\$(conda shell.bash hook)\""
        exit 1
    fi
else
    # Initialize conda for this shell session
    eval "$(conda shell.bash hook)"
fi

# Activate conda environment
echo "Activating conda environment: repeat"
conda activate repeat

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate conda environment 'repeat'"
    echo "Please ensure the environment exists: conda env list"
    exit 1
fi

# Run each block sequentially
for block_num in $(seq 0 $((N_BLOCKS - 1))); do
    echo ""
    echo "=========================================="
    echo "Starting Block $block_num / $((N_BLOCKS - 1))"
    echo "=========================================="
    
    # Run the live experiment (auto-detects next block)
    python paradigm/semantic_paradigm_live.py \
        --participant-id "$PARTICIPANT_ID" \
        --verbose
    
    # Check exit status
    if [ $? -ne 0 ]; then
        echo ""
        echo "ERROR: Block $block_num failed!"
        echo "Stopping execution."
        exit 1
    fi
    
    # Pause before next block (except after last block)
    if [ $block_num -lt $((N_BLOCKS - 1)) ]; then
        echo ""
        echo "Block $block_num completed successfully."
        echo "Pausing ${PAUSE_SECONDS} seconds before next block..."
        sleep $PAUSE_SECONDS
    else
        echo ""
        echo "Block $block_num completed successfully."
    fi
done

echo ""
echo "=========================================="
echo "All Blocks Completed!"
echo "=========================================="
echo "Participant: $PARTICIPANT_ID"
echo "Total blocks run: $N_BLOCKS"
echo ""

# Run evaluation scripts
echo "=========================================="
echo "Running Data Evaluation Scripts"
echo "=========================================="
echo ""

# Check if repeat_analyse environment exists
if conda env list | grep -q "^repeat_analyse"; then
    echo "Switching to repeat_analyse environment for validation..."
    conda activate repeat_analyse
    
    if [ $? -ne 0 ]; then
        echo "WARNING: Failed to activate repeat_analyse environment"
        echo "Skipping evaluation scripts. You can run them manually:"
        echo "  conda activate repeat_analyse"
        echo "  python scripts/validate_triggers.py --participant-id $PARTICIPANT_ID"
    else
        echo ""
        echo "Running comprehensive trigger validation..."
        python scripts/validate_triggers.py --participant-id "$PARTICIPANT_ID"
        
        VALIDATION_EXIT=$?
        if [ $VALIDATION_EXIT -eq 0 ]; then
            echo ""
            echo "[OK] Trigger validation completed successfully"
        else
            echo ""
            echo "[WARNING] Trigger validation completed with errors (exit code: $VALIDATION_EXIT)"
        fi
        
        echo ""
        echo "Evaluation complete!"
        echo ""
        echo "Note: For additional evaluation scripts, run manually:"
        echo "  python scripts/comprehensive_data_evaluation.py"
        echo "  python scripts/validate_captured_data.py"
    fi
else
    echo "WARNING: repeat_analyse environment not found"
    echo "Skipping evaluation scripts. To set up the analysis environment:"
    echo "  bash scripts/setup_analysis_env.sh"
    echo ""
    echo "Then run validation manually:"
    echo "  conda activate repeat_analyse"
    echo "  python scripts/validate_triggers.py --participant-id $PARTICIPANT_ID"
fi

echo ""
echo "=========================================="
echo "Experiment Session Complete"
echo "=========================================="
echo "Participant: $PARTICIPANT_ID"
echo "Blocks completed: $N_BLOCKS"
echo ""
