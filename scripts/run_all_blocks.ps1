# Run all blocks sequentially for live experiment
#
# Usage:
#   .\scripts\run_all_blocks.ps1 [-ParticipantId <id>] [-NBlocks <n>] [-PauseSeconds <s>]
#
# Examples:
#   # Run all 10 blocks for participant 9999 (default)
#   .\scripts\run_all_blocks.ps1
#
#   # Run all 10 blocks for specific participant
#   .\scripts\run_all_blocks.ps1 -ParticipantId P001
#
#   # Run specific number of blocks (e.g., 2 blocks for testing)
#   .\scripts\run_all_blocks.ps1 -ParticipantId 9999 -NBlocks 2
#
#   # Custom pause duration between blocks
#   .\scripts\run_all_blocks.ps1 -ParticipantId 9999 -PauseSeconds 10
#
# Notes:
#   - Automatically activates conda environment 'repeat'
#   - Auto-detects next block (no manual block number needed)
#   - Waits for each block to complete before starting next
#   - 5 second pause between blocks by default (configurable)
#   - Stops on error if any block fails

param(
    [string]$ParticipantId = "9999",
    [int]$NBlocks = 10,
    [int]$PauseSeconds = 5
)

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Running All Blocks - Live Experiment" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Participant ID: $ParticipantId"
Write-Host "Number of blocks: $NBlocks"
Write-Host "Pause between blocks: ${PauseSeconds}s"
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Get the project root directory (parent of scripts/)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

# Change to project root
Set-Location $ProjectRoot

# Initialize and activate conda environment
Write-Host "Activating conda environment: repeat" -ForegroundColor Gray
conda activate repeat

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to activate conda environment 'repeat'" -ForegroundColor Red
    Write-Host "Please ensure the environment exists: conda env list" -ForegroundColor Red
    exit 1
}

# Run each block sequentially
for ($blockNum = 0; $blockNum -lt $NBlocks; $blockNum++) {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Yellow
    Write-Host "Starting Block $blockNum / $($NBlocks - 1)" -ForegroundColor Yellow
    Write-Host "==========================================" -ForegroundColor Yellow
    
    # Run the live experiment (auto-detects next block)
    $blockCommand = "python paradigm\semantic_paradigm_live.py --participant-id `"$ParticipantId`" --verbose"
    
    Write-Host "Running: $blockCommand" -ForegroundColor Gray
    Invoke-Expression $blockCommand
    
    # Check exit status
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "ERROR: Block $blockNum failed!" -ForegroundColor Red
        Write-Host "Stopping execution." -ForegroundColor Red
        exit 1
    }
    
    # Pause before next block (except after last block)
    if ($blockNum -lt ($NBlocks - 1)) {
        Write-Host ""
        Write-Host "Block $blockNum completed successfully." -ForegroundColor Green
        Write-Host "Pausing ${PauseSeconds} seconds before next block..." -ForegroundColor Gray
        Start-Sleep -Seconds $PauseSeconds
    } else {
        Write-Host ""
        Write-Host "Block $blockNum completed successfully." -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "All Blocks Completed!" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Participant: $ParticipantId"
Write-Host "Total blocks run: $NBlocks"
Write-Host ""
