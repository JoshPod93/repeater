@echo off
REM Windows setup script for semantic visualization paradigm
REM Creates conda environment and installs dependencies

echo ========================================
echo Semantic Visualization Paradigm Setup
echo ========================================
echo.

REM Check if conda is available
where conda >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: conda not found. Please install Anaconda or Miniconda first.
    pause
    exit /b 1
)

echo Creating conda environment 'repeat'...
conda create -n repeat python=3.9 -y
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to create conda environment.
    pause
    exit /b 1
)

echo.
echo Activating environment and installing packages...
call conda activate repeat
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to activate environment.
    pause
    exit /b 1
)

if exist environment.yml (
    echo Installing from environment.yml...
    conda env update -n repeat -f environment.yml --prune
) else if exist requirements.txt (
    echo Installing from requirements.txt...
    pip install -r requirements.txt
) else (
    echo Installing core dependencies...
    pip install psychopy numpy
)

echo.
echo ========================================
echo Setup complete!
echo ========================================
echo.
echo To activate the environment, run:
echo   conda activate repeat
echo.
echo To run the experiment:
echo   python paradigm/scripts/run_experiment.py
echo.
pause
