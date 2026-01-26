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

from paradigm.utils.block_utils import load_randomization_protocol, get_latest_subject_folder, find_subject_folders


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


def parcel_triggers_into_trials(triggers: List[Dict[str, str]]) -> Dict[int, List[Dict[str, str]]]:
    """
    Parcel triggers into individual trials based on trial_start/trial_end codes.
    
    Similar to grasp project's trigger parcelation approach.
    Excludes block start/end codes (151-159, 251-259) from trial parcelation.
    
    Parameters
    ----------
    triggers : list
        List of trigger records from CSV
        
    Returns
    -------
    dict
        Dictionary mapping trial_num -> list of triggers in that trial
    """
    trials = {}
    current_trial_num = None
    current_trial_triggers = []
    
    for trigger in triggers:
        trigger_code = int(trigger.get('trigger_code', 0))
        
        # Skip block start/end codes (151-159, 251-259) - they're not trial events
        if 151 <= trigger_code <= 159 or 251 <= trigger_code <= 259:
            continue
        
        # Check for trial start (101-199)
        if 101 <= trigger_code <= 199:
            # Save previous trial if exists
            if current_trial_num is not None:
                trials[current_trial_num] = current_trial_triggers.copy()
            
            # Start new trial
            current_trial_num = trigger_code - 100
            current_trial_triggers = [trigger]
        
        # Check for trial end (201-299, but exclude block_end codes 251-259)
        elif 201 <= trigger_code <= 250:  # Changed from 299 to 250 to exclude block_end
            trial_num = trigger_code - 200
            if trial_num == current_trial_num:
                # End of current trial
                current_trial_triggers.append(trigger)
                trials[current_trial_num] = current_trial_triggers.copy()
                current_trial_num = None
                current_trial_triggers = []
            else:
                # Mismatch - trial end doesn't match current trial
                if current_trial_num is not None:
                    current_trial_triggers.append(trigger)
        
        # Regular trigger within trial
        elif current_trial_num is not None:
            current_trial_triggers.append(trigger)
    
    # Handle last trial if it didn't end
    if current_trial_num is not None:
        trials[current_trial_num] = current_trial_triggers
    
    return trials


def parcel_triggers_into_blocks(triggers: List[Dict[str, str]]) -> Dict[int, List[Dict[str, str]]]:
    """
    Parcel triggers into individual blocks based on block_start/block_end codes.
    
    Similar to grasp project's trigger parcelation approach.
    
    Parameters
    ----------
    triggers : list
        List of trigger records from CSV
        
    Returns
    -------
    dict
        Dictionary mapping block_num -> list of triggers in that block
    """
    blocks = {}
    current_block_num = None
    current_block_triggers = []
    
    for trigger in triggers:
        trigger_code = int(trigger.get('trigger_code', 0))
        
        # Check for block start (151-159)
        if 151 <= trigger_code <= 159:
            # Save previous block if exists
            if current_block_num is not None:
                blocks[current_block_num] = current_block_triggers.copy()
            
            # Start new block
            current_block_num = trigger_code - 150
            current_block_triggers = [trigger]
        
        # Check for block end (251-259)
        elif 251 <= trigger_code <= 259:
            block_num = trigger_code - 250
            if block_num == current_block_num:
                # End of current block
                current_block_triggers.append(trigger)
                blocks[current_block_num] = current_block_triggers.copy()
                current_block_num = None
                current_block_triggers = []
            else:
                # Mismatch - block end doesn't match current block
                if current_block_num is not None:
                    current_block_triggers.append(trigger)
        
        # Regular trigger within block
        elif current_block_num is not None:
            current_block_triggers.append(trigger)
    
    # Handle last block if it didn't end
    if current_block_num is not None:
        blocks[current_block_num] = current_block_triggers
    
    return blocks


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
    
    # Parcel into trials first for better accuracy
    trials = parcel_triggers_into_trials(triggers)
    
    for trial_num in sorted(trials.keys()):
        trial_triggers = trials[trial_num]
        
        # Find concept trigger in this trial
        for trigger in trial_triggers:
            trigger_code = int(trigger.get('trigger_code', 0))
            if trigger_code in [10, 20]:  # Concept triggers
                concept_info = extract_concept_from_event_name(trigger.get('event_name', ''))
                if concept_info:
                    concept, category = concept_info
                    concept_sequence.append((trial_num, concept, category))
                    break  # One concept per trial
    
    return concept_sequence


def analyze_trial_structure(trials: Dict[int, List[Dict[str, str]]], max_beeps: int = 8) -> Dict[str, any]:
    """
    Analyze trial structure and detect issues.
    
    Parameters
    ----------
    trials : dict
        Dictionary mapping trial_num -> list of triggers
        
    Returns
    -------
    dict
        Analysis results
    """
    analysis = {
        'total_trials': len(trials),
        'complete_trials': 0,
        'incomplete_trials': [],
        'missing_concepts': [],
        'trial_lengths': {},
        'issues': []
    }
    
    for trial_num, trial_triggers in trials.items():
        # Check if trial has start and end
        has_start = any(101 <= int(t.get('trigger_code', 0)) <= 199 for t in trial_triggers)
        has_end = any(201 <= int(t.get('trigger_code', 0)) <= 299 for t in trial_triggers)
        
        # Check for concept
        has_concept = any(int(t.get('trigger_code', 0)) in [10, 20] for t in trial_triggers)
        
        # Check for beeps (dynamic range based on max beeps)
        # Beep codes: 31-38 for beeps 1-8, but we check dynamically
        max_beeps = 8  # Maximum supported
        beep_count = sum(1 for t in trial_triggers 
                        if 31 <= int(t.get('trigger_code', 0)) <= (30 + max_beeps))
        
        if has_start and has_end:
            analysis['complete_trials'] += 1
        else:
            analysis['incomplete_trials'].append(trial_num)
            if not has_start:
                analysis['issues'].append(f"Trial {trial_num}: Missing trial start")
            if not has_end:
                analysis['issues'].append(f"Trial {trial_num}: Missing trial end")
        
        if not has_concept:
            analysis['missing_concepts'].append(trial_num)
            analysis['issues'].append(f"Trial {trial_num}: Missing concept trigger")
        
        analysis['trial_lengths'][trial_num] = {
            'total_triggers': len(trial_triggers),
            'beep_count': beep_count,
            'has_start': has_start,
            'has_end': has_end,
            'has_concept': has_concept
        }
    
    return analysis


def analyze_block_structure(blocks: Dict[int, List[Dict[str, str]]]) -> Dict[str, any]:
    """
    Analyze block structure and detect issues.
    
    Parameters
    ----------
    blocks : dict
        Dictionary mapping block_num -> list of triggers
        
    Returns
    -------
    dict
        Analysis results
    """
    analysis = {
        'total_blocks': len(blocks),
        'complete_blocks': 0,
        'incomplete_blocks': [],
        'trials_per_block': {},
        'issues': []
    }
    
    for block_num, block_triggers in blocks.items():
        # Check if block has start and end
        has_start = any(151 <= int(t.get('trigger_code', 0)) <= 159 for t in block_triggers)
        has_end = any(251 <= int(t.get('trigger_code', 0)) <= 259 for t in block_triggers)
        
        # Count trials in this block
        trial_starts = [int(t.get('trigger_code', 0)) - 100 
                       for t in block_triggers 
                       if 101 <= int(t.get('trigger_code', 0)) <= 199]
        
        if has_start and has_end:
            analysis['complete_blocks'] += 1
        else:
            analysis['incomplete_blocks'].append(block_num)
            if not has_start:
                analysis['issues'].append(f"Block {block_num}: Missing block start")
            if not has_end:
                analysis['issues'].append(f"Block {block_num}: Missing block end")
        
        analysis['trials_per_block'][block_num] = len(trial_starts)
    
    return analysis


def validate_trigger_log_against_protocol(
    trigger_csv_path: Path,
    protocol: Dict,
    participant_id: str,
    analyze_structure: bool = True
) -> Tuple[bool, List[str], Dict[str, any]]:
    """
    Validate trigger log against randomization protocol.
    
    Includes trigger parcelation analysis similar to grasp project.
    
    Parameters
    ----------
    trigger_csv_path : Path
        Path to trigger CSV file
    protocol : dict
        Randomization protocol dictionary
    participant_id : str
        Participant ID
    analyze_structure : bool
        Whether to perform detailed structure analysis
        
    Returns
    -------
    tuple
        (is_valid, error_messages, analysis_dict)
    """
    errors = []
    analysis = {}
    
    # Load trigger log
    triggers = load_trigger_csv(trigger_csv_path)
    
    # Parcel triggers into trials and blocks
    trials = parcel_triggers_into_trials(triggers)
    blocks = parcel_triggers_into_blocks(triggers)
    
    if analyze_structure:
        # Get max_beeps from protocol or use default
        max_beeps = protocol.get('config', {}).get('N_BEEPS', 8)
        
        trial_analysis = analyze_trial_structure(trials, max_beeps=max_beeps)
        block_analysis = analyze_block_structure(blocks)
        
        analysis['trials'] = trial_analysis
        analysis['blocks'] = block_analysis
        
        # Report structure issues
        if trial_analysis['issues']:
            errors.extend([f"STRUCTURE: {issue}" for issue in trial_analysis['issues']])
        if block_analysis['issues']:
            errors.extend([f"STRUCTURE: {issue}" for issue in block_analysis['issues']])
    
    # Get protocol blocks
    all_blocks_trials = protocol.get('all_blocks_trials', [])
    
    # Validate each block found in triggers against its corresponding protocol block
    for block_num in sorted(blocks.keys()):
        block_triggers = blocks[block_num]
        
        # Convert block_num from 1-indexed (from trigger codes) to 0-indexed (for protocol)
        protocol_block_idx = block_num - 1
        
        if protocol_block_idx < 0 or protocol_block_idx >= len(all_blocks_trials):
            errors.append(
                f"BLOCK {block_num}: Block number out of range. "
                f"Protocol has {len(all_blocks_trials)} blocks (0-{len(all_blocks_trials)-1})"
            )
            continue
        
        # Get expected trials for this block from protocol
        expected_block_trials = all_blocks_trials[protocol_block_idx]
        
        # Extract concept sequence from this block's triggers
        block_concepts = extract_concept_sequence_from_triggers(block_triggers)
        
        # Build expected sequence for this block (using global trial numbers)
        expected_block_sequence = []
        for trial_idx, trial in enumerate(expected_block_trials):
            # Global trial number = sum of trials in previous blocks + trial_idx + 1
            global_trial_num = sum(len(all_blocks_trials[b]) for b in range(protocol_block_idx)) + trial_idx + 1
            expected_block_sequence.append((
                global_trial_num,  # Use global trial number for comparison
                trial['concept'],
                trial['category']
            ))
        
        # Compare block sequences
        if len(block_concepts) != len(expected_block_sequence):
            errors.append(
                f"BLOCK {block_num}: Mismatch - trigger log has {len(block_concepts)} concepts, "
                f"protocol expects {len(expected_block_sequence)} for this block"
            )
        
        # Compare each trial in this block
        min_length = min(len(block_concepts), len(expected_block_sequence))
        for i in range(min_length):
            trial_num_trig, concept_trig, category_trig = block_concepts[i]
            trial_num_exp, concept_exp, category_exp = expected_block_sequence[i]
            
            if concept_trig != concept_exp:
                errors.append(
                    f"BLOCK {block_num}, Trial {trial_num_trig}: Concept mismatch - "
                    f"trigger='{concept_trig}', expected='{concept_exp}'"
                )
            
            if category_trig != category_exp:
                errors.append(
                    f"BLOCK {block_num}, Trial {trial_num_trig}: Category mismatch - "
                    f"trigger='{category_trig}', expected='{category_exp}'"
                )
        
        # Check for missing or extra trials
        if len(block_concepts) < len(expected_block_sequence):
            missing_count = len(expected_block_sequence) - len(block_concepts)
            errors.append(
                f"BLOCK {block_num}: Missing {missing_count} trial(s) in trigger log"
            )
        elif len(block_concepts) > len(expected_block_sequence):
            extra_count = len(block_concepts) - len(expected_block_sequence)
            errors.append(
                f"BLOCK {block_num}: {extra_count} extra trial(s) in trigger log"
            )
    
    # Check if all expected blocks are present (only if we're validating all blocks)
    # For single CSV files, we only validate the blocks present in that file
    blocks_found = set(blocks.keys())
    if len(blocks_found) > 0:
        # Only warn about missing blocks if we're validating a complete experiment
        # For now, we'll skip this check as CSV files may contain partial blocks
        pass
    
    is_valid = len(errors) == 0
    return is_valid, errors, analysis


def validate_all_blocks(
    results_dir: Path,
    participant_id: str
) -> Dict[str, any]:
    """
    Validate all trigger logs for a participant against protocol.
    
    Parameters
    ----------
    results_dir : Path
        Results directory (e.g., data/results or sim_data/sim_results)
    participant_id : str
        Participant ID
        
    Returns
    -------
    dict
        Validation results
    """
    # Find subject folder(s) for this participant
    subject_folders = find_subject_folders(results_dir, participant_id)
    
    if not subject_folders:
        return {
            'valid': False,
            'error': f'No subject folders found for participant {participant_id}',
            'blocks_validated': 0
        }
    
    # Use most recent subject folder
    subject_folder = subject_folders[0]
    
    # Load protocol
    protocol = load_randomization_protocol(
        subject_folder=subject_folder,
        participant_id=participant_id
    )
    
    if protocol is None:
        return {
            'valid': False,
            'error': 'No randomization protocol found',
            'blocks_validated': 0
        }
    
    # Find trigger CSV files in subject folder
    pattern = f"sub-{participant_id}_*_triggers.csv"
    trigger_files = list(subject_folder.glob(pattern))
    
    if not trigger_files:
        return {
            'valid': False,
            'error': f'No trigger CSV files found in {subject_folder}',
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
        is_valid, errors, analysis = validate_trigger_log_against_protocol(
            trigger_csv_path=trigger_file,
            protocol=protocol,
            participant_id=participant_id,
            analyze_structure=True
        )
        
        results['validations'].append({
            'file': trigger_file.name,
            'valid': is_valid,
            'errors': errors,
            'analysis': analysis
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
        
        # Print structure analysis if available
        if 'analysis' in val and val['analysis']:
            analysis = val['analysis']
            if 'trials' in analysis:
                trial_analysis = analysis['trials']
                print(f"\n    Trial Structure:")
                print(f"      Total trials: {trial_analysis['total_trials']}")
                print(f"      Complete: {trial_analysis['complete_trials']}")
                if trial_analysis['incomplete_trials']:
                    print(f"      Incomplete: {trial_analysis['incomplete_trials'][:5]}{'...' if len(trial_analysis['incomplete_trials']) > 5 else ''}")
            
            if 'blocks' in analysis:
                block_analysis = analysis['blocks']
                print(f"\n    Block Structure:")
                print(f"      Total blocks: {block_analysis['total_blocks']}")
                print(f"      Complete: {block_analysis['complete_blocks']}")
                if block_analysis['trials_per_block']:
                    print(f"      Trials per block: {block_analysis['trials_per_block']}")
    
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
        '--trigger-csv', '-t',
        type=str,
        help='Path to specific trigger CSV file to validate'
    )
    
    parser.add_argument(
        '--results-dir', '-r',
        type=str,
        default=None,
        help='Results directory (default: data/results, use sim_data/sim_results for simulation data)'
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
        is_valid, errors, analysis = validate_trigger_log_against_protocol(
            trigger_csv_path=trigger_csv_path,
            protocol=protocol,
            participant_id=participant_id,
            session_id=session_id,
            analyze_structure=True
        )
        
        print(f"\nValidation: {'PASSED' if is_valid else 'FAILED'}")
        
        # Print structure analysis
        if analysis:
            if 'trials' in analysis:
                trial_analysis = analysis['trials']
                print(f"\nTrial Structure Analysis:")
                print(f"  Total trials: {trial_analysis['total_trials']}")
                print(f"  Complete trials: {trial_analysis['complete_trials']}")
                if trial_analysis['incomplete_trials']:
                    print(f"  Incomplete trials: {trial_analysis['incomplete_trials']}")
                if trial_analysis['missing_concepts']:
                    print(f"  Missing concepts: {trial_analysis['missing_concepts']}")
            
            if 'blocks' in analysis:
                block_analysis = analysis['blocks']
                print(f"\nBlock Structure Analysis:")
                print(f"  Total blocks: {block_analysis['total_blocks']}")
                print(f"  Complete blocks: {block_analysis['complete_blocks']}")
                if block_analysis['incomplete_blocks']:
                    print(f"  Incomplete blocks: {block_analysis['incomplete_blocks']}")
                print(f"  Trials per block: {block_analysis['trials_per_block']}")
        
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
            participant_id=args.participant_id
        )
        
        print_validation_report(results)


if __name__ == "__main__":
    main()
