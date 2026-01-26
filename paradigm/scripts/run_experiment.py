#!/usr/bin/env python3
"""
Experiment launcher script.

Provides CLI interface for running semantic visualization experiments.
Supports both simulation and live modes.
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from paradigm.semantic_paradigm_live import run_experiment_live
from paradigm.semantic_paradigm_simulation import run_experiment_simulation


def main():
    """Main launcher function."""
    parser = argparse.ArgumentParser(
        description='Semantic Visualization Paradigm - BCI Experiment',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run live experiment with Biosemi
  python paradigm/scripts/run_experiment.py --live --participant-id P001
  
  # Run simulation (for testing)
  python paradigm/scripts/run_experiment.py --simulation --participant-id sim_9999
  
  # Run live with specific Biosemi port
  python paradigm/scripts/run_experiment.py --live --participant-id P001 --biosemi-port COM4
  
  # Run with fewer trials for testing
  python paradigm/scripts/run_experiment.py --live --participant-id P001 --n-trials 5
        """
    )
    
    parser.add_argument(
        '--live',
        action='store_true',
        help='Run with live Biosemi EEG capture (default: simulation)'
    )
    
    parser.add_argument(
        '--simulation', '--sim',
        action='store_true',
        help='Run in simulation mode (no hardware required)'
    )
    
    parser.add_argument(
        '--participant-id', '-p',
        type=str,
        required=True,
        help='Participant identifier (required)'
    )
    
    parser.add_argument(
        '--biosemi-port',
        type=str,
        default='COM3',
        help='Serial port for Biosemi (default: COM3, only used in live mode)'
    )
    
    parser.add_argument(
        '--n-trials', '-n',
        type=int,
        default=None,
        help='Number of trials to run (default: from config)'
    )
    
    parser.add_argument(
        '--n-beeps', '--beeps',
        type=int,
        default=None,
        help='Number of beeps per trial (default: from config, max: 8)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default=None,
        help='Path to config file (default: config/experiment_config.py)'
    )
    
    args = parser.parse_args()
    
    # Determine mode
    if args.live:
        mode = 'live'
    elif args.simulation:
        mode = 'simulation'
    else:
        # Default to simulation if neither specified
        mode = 'simulation'
        print("[INFO] No mode specified, defaulting to simulation mode")
    
    config_path = None
    if args.config:
        config_path = Path(args.config)
    
    try:
        if mode == 'live':
            results = run_experiment_live(
                participant_id=args.participant_id,
                biosemi_port=args.biosemi_port,
                config_path=config_path,
                n_trials=args.n_trials,
                n_beeps=args.n_beeps,
                verbose=args.verbose
            )
        else:
            results = run_experiment_simulation(
                participant_id=args.participant_id,
                config_path=config_path,
                n_trials=args.n_trials,
                n_beeps=args.n_beeps,
                verbose=args.verbose
            )
        
        if results:
            print("\n[OK] Experiment completed successfully!")
        else:
            print("\n[WARNING] Experiment completed with warnings")
            
    except KeyboardInterrupt:
        print("\n\n[WARNING] Experiment interrupted by user (Ctrl+C)")
    except Exception as e:
        print(f"\n[ERROR] Error during experiment: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
