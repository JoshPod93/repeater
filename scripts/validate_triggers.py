"""
Validate trigger logs against randomization protocol.

This script ensures that the concepts shown on screen (logged in trigger CSV)
match the ground truth randomization protocol exactly.

Critical for data integrity - any mismatch indicates a serious problem.
"""

import sys
import csv
import json
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple, Optional

# Add parent directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from paradigm.utils.block_utils import load_randomization_protocol


def extract_concept_from_event_name(event_name: str) -> Optional[Tuple[str, str]]:
    """
    Extract concept word and category from trigger event name.
    
    Expected format: 'concept_{word}_category_{A|B}'
    
    Parameters
    ----------
    event_name : str
        Event name from trigger CSV
        
    Returns
    -------
    tuple or None
        (concept_word, category) or None if not a concept event
    """
    pattern = r'concept_([^_]+)_category_([AB])'
    match = re.match(pattern, event_name)
    if match:
        return (match.group(1), match.group(2))
    return None


def extract_trial_num_from_event_name(event_name: str) -> Optional[int]:
    """
    Extract trial number from trigger event name.
    
    Handles: trial_{N}_start, trial_{N}_end
    
    Parameters
    ----------
    event_name : str
        Event name from trigger CSV
        
    Returns
    -------
    int or None
        Trial number or None if not a trial event
    """
    patterns = [
        r'trial_(\d+)_start',
        r'trial_(\d+)_end'
    ]
    for pattern in patterns:
        match = re.match(pattern, event_name)
        if match:
            return int(match.group(1))
    return None


def extract_block_num_from_event_name(event_name: str) -> Optional[int]:
    """
    Extract block number from trigger event name.
    
    Handles: block_{N}_start, block_{N}_end
    
    Parameters
    ----------
    event_name : str
        Event name from trigger CSV
        
    Returns
    -------
    int or None
        Block number (1-indexed) or None if not a block event
    """
    patterns = [
        r'block_(\d+)_start',
        r'block_(\d+)_end'
    ]
    for pattern in patterns:
        match = re.match(pattern, event_name)
        if match:
            return int(match.group(1))
    return None


def load_trigger_csv(csv_path: Path) -> List[Dict[str, str]]:
    """
    Load trigger CSV file.
    
    Parameters
    ----------
    csv_path : Path
        Path to trigger CSV file
        
    Returns
    -------
    list
        List of trigger records as dictionaries
    """
    triggers = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            triggers.append(row)
    return triggers


def extract_concept_sequence_from_triggers(triggers: List[Dict[str, str]]) -> List[Tuple[int, str, str]]:
    """
    Extract concept sequence from trigger log.
    
    Returns list of (trial_num, concept, category) tuples in order.
    
    Parameters
    ----------
    triggers : list
        List of trigger records from CSV
        
    Returns
    -------
    list
        List of (trial_num, concept, category) tuples
    """
    concept_sequence = []
    
    # Track current trial number as we process triggers
    current_trial_num = None
    
    for trigger in triggers:
        event_name = trigger.get('event_name', '')
        trigger_code = int(trigger.get('trigger_code', 0))
        
        # Check if this is a trial start (dynamic code 101-199)
        if 101 <= trigger_code <= 199:
            current_trial_num = trigger_code - 100
        
        # Extract concept if this is a concept event (codes 10 or 20)
        if trigger_code in [10, 20]:
            concept_info = extract_concept_from_event_name(event_name)
            if concept_info and current_trial_num:
                concept, category = concept_info
                concept_sequence.append((current_trial_num, concept, category))
    
    return concept_sequence


def validate_trigger_log_against_protocol(
    trigger_csv_path: Path,
    protocol: Dict,
    participant_id: str,
    session_id: int
) -> Tuple[bool, List[str]]:
    """
    Validate trigger log against randomization protocol.
    
    Parameters
    ----------
    trigger_csv_path : Path
        Path to trigger CSV file
    protocol : dict
        Randomization protocol dictionary
    participant_id : str
        Participant ID
    session_id : int
        Session ID
        
    Returns
    -------
    tuple
        (is_valid, error_messages)
    """
    errors = []
    
    # Load trigger log
    triggers = load_trigger_csv(trigger_csv_path)
    
    # Extract concept sequence from triggers
    trigger_concepts = extract_concept_sequence_from_triggers(triggers)
    
    # Get protocol trials
    all_blocks_trials = protocol.get('all_blocks_trials', [])
    
    # Reconstruct expected sequence from protocol
    expected_sequence = []
    global_trial_num = 1
    
    for block_num, block_trials in enumerate(all_blocks_trials):
        for trial in block_trials:
            expected_sequence.append((
                global_trial_num,
                trial['concept'],
                trial['category']
            ))
            global_trial_num += 1
    
    # Compare sequences
    if len(trigger_concepts) != len(expected_sequence):
        errors.append(
            f"MISMATCH: Trigger log has {len(trigger_concepts)} concepts, "
            f"protocol expects {len(expected_sequence)}"
        )
    
    # Compare each trial
    min_length = min(len(trigger_concepts), len(expected_sequence))
    mismatches = []
    
    for i in range(min_length):
        trial_num_trig, concept_trig, category_trig = trigger_concepts[i]
        trial_num_exp, concept_exp, category_exp = expected_sequence[i]
        
        if trial_num_trig != trial_num_exp:
            mismatches.append(
                f"Trial {i+1}: Trial number mismatch - trigger={trial_num_trig}, expected={trial_num_exp}"
            )
        
        if concept_trig != concept_exp:
            mismatches.append(
                f"Trial {i+1}: Concept mismatch - trigger='{concept_trig}', expected='{concept_exp}'"
            )
        
        if category_trig != category_exp:
            mismatches.append(
                f"Trial {i+1}: Category mismatch - trigger='{category_trig}', expected='{category_exp}'"
            )
    
    if mismatches:
        errors.extend(mismatches)
    
    # Check for missing trials
    if len(trigger_concepts) < len(expected_sequence):
        missing = len(expected_sequence) - len(trigger_concepts)
        errors.append(f"MISSING: {missing} trials not found in trigger log")
    
    # Check for extra trials
    if len(trigger_concepts) > len(expected_sequence):
        extra = len(trigger_concepts) - len(expected_sequence)
        errors.append(f"EXTRA: {extra} extra trials in trigger log")
    
    is_valid = len(errors) == 0
    return is_valid, errors


def validate_all_blocks(
    results_dir: Path,
    participant_id: str,
    session_id: int
) -> Dict[str, any]:
    """
    Validate all trigger logs for a participant/session against protocol.
    
    Parameters
    ----------
    results_dir : Path
        Results directory
    participant_id : str
        Participant ID
    session_id : int
        Session ID
        
    Returns
    -------
    dict
        Validation results
    """
    # Load protocol
    protocol = load_randomization_protocol(
        output_dir=results_dir,
        participant_id=participant_id,
        session_id=session_id
    )
    
    if protocol is None:
        return {
            'valid': False,
            'error': 'No randomization protocol found',
            'blocks_validated': 0
        }
    
    # Find trigger CSV files
    triggers_dir = results_dir.parent / 'triggers'
    pattern = f"sub-{participant_id}_ses-{session_id}_*_triggers.csv"
    trigger_files = list(triggers_dir.glob(pattern))
    
    if not trigger_files:
        return {
            'valid': False,
            'error': 'No trigger CSV files found',
            'blocks_validated': 0
        }
    
    # Validate each trigger file
    results = {
        'valid': True,
        'blocks_validated': len(trigger_files),
        'protocol_timestamp': protocol.get('metadata', {}).get('timestamp', 'unknown'),
        'protocol_blocks': len(protocol.get('all_blocks_trials', [])),
        'validations': []
    }
    
    for trigger_file in sorted(trigger_files):
        is_valid, errors = validate_trigger_log_against_protocol(
            trigger_csv_path=trigger_file,
            protocol=protocol,
            participant_id=participant_id,
            session_id=session_id
        )
        
        results['validations'].append({
            'file': trigger_file.name,
            'valid': is_valid,
            'errors': errors
        })
        
        if not is_valid:
            results['valid'] = False
    
    return results


def print_validation_report(results: Dict[str, any]):
    """Print validation report."""
    print("="*80)
    print("TRIGGER LOG VALIDATION REPORT")
    print("="*80)
    
    if 'error' in results:
        print(f"\nERROR: {results['error']}")
        return
    
    print(f"\nProtocol Info:")
    print(f"  Timestamp: {results.get('protocol_timestamp', 'unknown')}")
    print(f"  Blocks in protocol: {results.get('protocol_blocks', 0)}")
    print(f"  Trigger files validated: {results.get('blocks_validated', 0)}")
    
    print(f"\nValidation Results:")
    
    all_valid = True
    for val in results.get('validations', []):
        status = "OK" if val['valid'] else "FAILED"
        print(f"\n  {val['file']}: {status}")
        
        if not val['valid']:
            all_valid = False
            print(f"    Errors ({len(val['errors'])}):")
            for error in val['errors'][:10]:  # Show first 10 errors
                print(f"      - {error}")
            if len(val['errors']) > 10:
                print(f"      ... and {len(val['errors']) - 10} more errors")
    
    print("\n" + "="*80)
    if all_valid:
        print("OVERALL: VALIDATION PASSED - All trigger logs match protocol")
    else:
        print("OVERALL: VALIDATION FAILED - Mismatches detected!")
    print("="*80)


def main():
    """Main validation function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Validate trigger logs against randomization protocol',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate all trigger logs for a participant
  python scripts/validate_triggers.py --participant-id sim_9999 --session 1
  
  # Validate specific trigger CSV file
  python scripts/validate_triggers.py --trigger-csv data/triggers/sub-sim_9999_ses-1_20260126_154612_triggers.csv
        """
    )
    
    parser.add_argument(
        '--participant-id', '-p',
        type=str,
        help='Participant ID'
    )
    
    parser.add_argument(
        '--session', '-s',
        type=int,
        default=1,
        help='Session number (default: 1)'
    )
    
    parser.add_argument(
        '--trigger-csv', '-t',
        type=str,
        help='Path to specific trigger CSV file to validate'
    )
    
    parser.add_argument(
        '--results-dir', '-r',
        type=str,
        default=None,
        help='Results directory (default: data/results)'
    )
    
    args = parser.parse_args()
    
    # Set up paths
    if args.results_dir:
        results_dir = Path(args.results_dir)
    else:
        results_dir = project_root / 'data' / 'results'
    
    # Validate specific file or all files
    if args.trigger_csv:
        # Single file validation
        trigger_csv_path = Path(args.trigger_csv)
        
        if not trigger_csv_path.exists():
            print(f"ERROR: Trigger CSV file not found: {trigger_csv_path}")
            return
        
        # Extract participant/session from filename or use args
        if args.participant_id and args.session:
            participant_id = args.participant_id
            session_id = args.session
        else:
            # Try to extract from filename
            match = re.search(r'sub-([^_]+)_ses-(\d+)', trigger_csv_path.name)
            if match:
                participant_id = match.group(1)
                session_id = int(match.group(2))
            else:
                print("ERROR: Could not extract participant/session from filename. Use --participant-id and --session")
                return
        
        # Load protocol
        protocol = load_randomization_protocol(
            output_dir=results_dir,
            participant_id=participant_id,
            session_id=session_id
        )
        
        if protocol is None:
            print(f"ERROR: No randomization protocol found for {participant_id} session {session_id}")
            return
        
        # Validate
        is_valid, errors = validate_trigger_log_against_protocol(
            trigger_csv_path=trigger_csv_path,
            protocol=protocol,
            participant_id=participant_id,
            session_id=session_id
        )
        
        print(f"\nValidation: {'PASSED' if is_valid else 'FAILED'}")
        if errors:
            print(f"\nErrors ({len(errors)}):")
            for error in errors:
                print(f"  - {error}")
        
    else:
        # Validate all files
        if not args.participant_id:
            print("ERROR: --participant-id required when validating all files")
            return
        
        results = validate_all_blocks(
            results_dir=results_dir,
            participant_id=args.participant_id,
            session_id=args.session
        )
        
        print_validation_report(results)


if __name__ == "__main__":
    main()
