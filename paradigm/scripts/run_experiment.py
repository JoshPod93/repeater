#!/usr/bin/env python3
"""
Experiment launcher script.

Provides CLI interface for running semantic visualization experiments.
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from paradigm.semantic_paradigm import SemanticVisualizationExperiment


def main():
    """Main launcher function."""
    parser = argparse.ArgumentParser(
        description='Semantic Visualization Paradigm - BCI Experiment',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default settings
  python paradigm/scripts/run_experiment.py
  
  # Run with specific participant
  python paradigm/scripts/run_experiment.py --participant-id sub-001 --session 1
  
  # Run with triggers enabled
  python paradigm/scripts/run_experiment.py --participant-id sub-001 --triggers
  
        """
    )
    
    parser.add_argument(
        '--participant-id', '-p',
        type=str,
        default=None,
        help='Participant identifier (default: prompt for input)'
    )
    
    parser.add_argument(
        '--session', '-s',
        type=int,
        default=None,
        help='Session number (default: prompt for input or 1)'
    )
    
    parser.add_argument(
        '--triggers', '-t',
        action='store_true',
        help='Enable EEG triggers (default: False)'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default=None,
        help='Path to config file (default: config/experiment_config.py)'
    )
    
    args = parser.parse_args()
    
    # Get participant info
    participant_id = args.participant_id
    if participant_id is None:
        participant_id = input("Enter participant ID (or press Enter for 'test'): ").strip()
        if not participant_id:
            participant_id = 'test'
    
    session_id = args.session
    if session_id is None:
        session_input = input("Enter session number (or press Enter for '1'): ").strip()
        if not session_input:
            session_id = 1
        else:
            session_id = int(session_input)
    
    use_triggers = args.triggers
    if not use_triggers:
        trigger_input = input("Use EEG triggers? (y/n, default=n): ").strip().lower()
        use_triggers = trigger_input == 'y'
    
    # Create config path
    config_path = None
    if args.config:
        config_path = Path(args.config)
    
    # Create and run experiment
    exp = SemanticVisualizationExperiment(
        participant_id=participant_id,
        session_id=session_id,
        use_triggers=use_triggers,
        config_path=config_path
    )
    
    try:
        exp.run_experiment()
    except KeyboardInterrupt:
        print("\n\nExperiment interrupted by user.")
    except Exception as e:
        print(f"\nError during experiment: {e}")
        import traceback
        traceback.print_exc()
    finally:
        exp.quit()


if __name__ == "__main__":
    main()
