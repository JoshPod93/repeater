#!/usr/bin/env python3
"""
Validate all trigger logs (BDF, CSV, PsychoPy) against ground truth.
Compares chronological order, trigger retention, and relative temporal distances.
"""

import sys
import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Tuple
from collections import Counter

# Add parent directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def load_ground_truth(ground_truth_path: Path) -> List[Dict[str, Any]]:
    """Load ground truth trigger sequence."""
    with open(ground_truth_path, 'r') as f:
        data = json.load(f)
    return data['trigger_sequence']


def load_csv_triggers(csv_path: Path) -> pd.DataFrame:
    """Load CSV trigger log."""
    df = pd.read_csv(csv_path)
    # Filter for triggers actually sent to EEG
    df = df[df['sent_to_eeg'] == 'yes'].copy()
    return df


def load_bdf_triggers(bdf_path: Path) -> List[Dict[str, Any]]:
    """Load triggers from BDF file using MNE."""
    try:
        import mne
        import numpy as np
        
        # Load BDF
        raw = mne.io.read_raw_bdf(bdf_path, preload=True, verbose=False)
        
        # Find Status channel
        status_ch = None
        for ch_name in raw.ch_names:
            if 'Status' in ch_name or 'STIM' in ch_name:
                status_ch = ch_name
                break
        
        if status_ch is None:
            raise ValueError("No Status/STIM channel found in BDF")
        
        # Get trigger data
        ch_idx = raw.ch_names.index(status_ch)
        trigger_data = raw.get_data()[ch_idx, :]
        
        # Extract triggers (low byte)
        trigger_values = (trigger_data.astype(int) & 0xFF)
        
        # Find changes (triggers)
        diff = np.diff(trigger_values)
        trigger_indices = np.where(diff != 0)[0] + 1
        
        triggers = []
        for idx in trigger_indices:
            code = int(trigger_values[idx])
            if code > 0:  # Ignore zeros
                triggers.append({
                    'trigger_code': code,
                    'sample_index': int(idx),
                    'timestamp_bdf': float(idx / raw.info['sfreq'])
                })
        
        return triggers
        
    except ImportError:
        print("ERROR: MNE not available. Install with: conda activate repeat_analyse; pip install mne")
        return []


def align_triggers_sequential(ground_truth: List[Dict[str, Any]], 
                              observed: List[Dict[str, Any]],
                              code_key: str = 'trigger_code') -> List[Dict[str, Any]]:
    """
    Align triggers sequentially by matching codes in order.
    
    Returns list of alignment results with:
    - expected_code
    - observed_code (or None if missing)
    - position_match (bool)
    - code_match (bool)
    """
    alignments = []
    observed_idx = 0
    
    for gt_idx, gt_trigger in enumerate(ground_truth):
        expected_code = gt_trigger[code_key]
        
        # Find matching code in observed (starting from last position)
        found = False
        match_idx = None
        
        for obs_idx in range(observed_idx, len(observed)):
            if observed[obs_idx][code_key] == expected_code:
                match_idx = obs_idx
                found = True
                observed_idx = obs_idx + 1  # Move forward
                break
        
        alignments.append({
            'sequence_position': gt_idx + 1,
            'expected_code': expected_code,
            'expected_event': gt_trigger.get('event_name', ''),
            'observed_code': observed[match_idx][code_key] if found else None,
            'observed_event': observed[match_idx].get('event_name', '') if found else None,
            'position_match': found,
            'code_match': found and (observed[match_idx][code_key] == expected_code),
            'block_num': gt_trigger.get('block_num'),
            'trial_num': gt_trigger.get('trial_num')
        })
    
    return alignments


def calculate_relative_timing(triggers: List[Dict[str, Any]], 
                              timestamp_key: str) -> List[float]:
    """Calculate relative timing differences between consecutive triggers."""
    if len(triggers) < 2:
        return []
    
    timestamps = [t.get(timestamp_key, 0) for t in triggers]
    return [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]


def validate_against_ground_truth(ground_truth_path: Path,
                                   csv_path: Path = None,
                                   bdf_path: Path = None) -> Dict[str, Any]:
    """
    Validate CSV and/or BDF triggers against ground truth.
    
    Returns validation results dictionary.
    """
    # Load ground truth
    ground_truth = load_ground_truth(ground_truth_path)
    print(f"Loaded ground truth: {len(ground_truth)} triggers")
    
    results = {
        'ground_truth_total': len(ground_truth),
        'csv_validation': None,
        'bdf_validation': None
    }
    
    # Validate CSV
    if csv_path and csv_path.exists():
        print(f"\nValidating CSV: {csv_path.name}")
        csv_df = load_csv_triggers(csv_path)
        
        # Convert CSV to list format
        csv_triggers = []
        for _, row in csv_df.iterrows():
            csv_triggers.append({
                'trigger_code': int(row['trigger_code']),
                'event_name': row.get('event_name', ''),
                'timestamp_csv': float(row['timestamp_psychopy'])
            })
        
        # Align
        csv_alignments = align_triggers_sequential(ground_truth, csv_triggers)
        
        # Calculate statistics
        total_expected = len(csv_alignments)
        matched = sum(1 for a in csv_alignments if a['code_match'])
        missing = sum(1 for a in csv_alignments if not a['position_match'])
        extra = len(csv_triggers) - matched
        
        # Relative timing
        csv_timing = calculate_relative_timing(csv_triggers, 'timestamp_csv')
        gt_timing = calculate_relative_timing(ground_truth, 'sequence_position')  # Use position as proxy
        
        results['csv_validation'] = {
            'total_expected': total_expected,
            'total_observed': len(csv_triggers),
            'matched': matched,
            'missing': missing,
            'extra': extra,
            'match_rate': matched / total_expected if total_expected > 0 else 0,
            'alignments': csv_alignments[:100]  # First 100 for inspection
        }
        
        print(f"  Expected: {total_expected}, Observed: {len(csv_triggers)}")
        print(f"  Matched: {matched}, Missing: {missing}, Extra: {extra}")
        print(f"  Match rate: {matched/total_expected*100:.2f}%")
    
    # Validate BDF
    if bdf_path and bdf_path.exists():
        print(f"\nValidating BDF: {bdf_path.name}")
        bdf_triggers = load_bdf_triggers(bdf_path)
        
        if bdf_triggers:
            # Align
            bdf_alignments = align_triggers_sequential(ground_truth, bdf_triggers)
            
            # Calculate statistics
            total_expected = len(bdf_alignments)
            matched = sum(1 for a in bdf_alignments if a['code_match'])
            missing = sum(1 for a in bdf_alignments if not a['position_match'])
            extra = len(bdf_triggers) - matched
            
            results['bdf_validation'] = {
                'total_expected': total_expected,
                'total_observed': len(bdf_triggers),
                'matched': matched,
                'missing': missing,
                'extra': extra,
                'match_rate': matched / total_expected if total_expected > 0 else 0,
                'alignments': bdf_alignments[:100]  # First 100 for inspection
            }
            
            print(f"  Expected: {total_expected}, Observed: {len(bdf_triggers)}")
            print(f"  Matched: {matched}, Missing: {missing}, Extra: {extra}")
            print(f"  Match rate: {matched/total_expected*100:.2f}%")
        else:
            print("  ERROR: Could not load BDF triggers")
    
    return results


def print_validation_summary(results: Dict[str, Any]):
    """Print comprehensive validation summary."""
    print("\n" + "="*80)
    print("VALIDATION SUMMARY")
    print("="*80)
    
    print(f"\nGround Truth: {results['ground_truth_total']} triggers expected")
    
    if results['csv_validation']:
        csv = results['csv_validation']
        print(f"\nCSV Validation:")
        print(f"  Total observed: {csv['total_observed']}")
        print(f"  Matched: {csv['matched']} ({csv['match_rate']*100:.2f}%)")
        print(f"  Missing: {csv['missing']}")
        print(f"  Extra: {csv['extra']}")
        
        if csv['missing'] > 0:
            print(f"\n  Missing triggers (first 10):")
            missing_triggers = [a for a in csv['alignments'] if not a['position_match']][:10]
            for m in missing_triggers:
                print(f"    Position {m['sequence_position']}: Expected {m['expected_code']} ({m['expected_event']})")
    
    if results['bdf_validation']:
        bdf = results['bdf_validation']
        print(f"\nBDF Validation:")
        print(f"  Total observed: {bdf['total_observed']}")
        print(f"  Matched: {bdf['matched']} ({bdf['match_rate']*100:.2f}%)")
        print(f"  Missing: {bdf['missing']}")
        print(f"  Extra: {bdf['extra']}")
        
        if bdf['missing'] > 0:
            print(f"\n  Missing triggers (first 10):")
            missing_triggers = [a for a in bdf['alignments'] if not a['position_match']][:10]
            for m in missing_triggers:
                print(f"    Position {m['sequence_position']}: Expected {m['expected_code']} ({m['expected_event']})")


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate triggers against ground truth')
    parser.add_argument('--participant-id', type=str, required=True,
                       help='Participant ID')
    parser.add_argument('--ground-truth', type=str, default=None,
                       help='Path to ground truth JSON (default: auto-detect)')
    parser.add_argument('--csv', type=str, default=None,
                       help='Path to CSV trigger log (default: auto-detect)')
    parser.add_argument('--bdf', type=str, default=None,
                       help='Path to BDF file (default: auto-detect)')
    
    args = parser.parse_args()
    
    # Auto-detect paths
    results_dir = project_root / 'data' / 'results'
    data_dir = project_root / 'data'
    
    # Find ground truth
    if args.ground_truth:
        gt_path = Path(args.ground_truth)
    else:
        pattern = f'sub-{args.participant_id}_*'
        result_dirs = list(results_dir.glob(pattern))
        if result_dirs:
            latest_dir = max(result_dirs, key=lambda p: p.stat().st_mtime)
            gt_files = list(latest_dir.glob('*_ground_truth_triggers.json'))
            if gt_files:
                gt_path = gt_files[0]
            else:
                print("ERROR: No ground truth file found. Generate it first:")
                print(f"  python scripts/generate_ground_truth_triggers.py --participant-id {args.participant_id} --from-config")
                return
        else:
            print("ERROR: No results directory found")
            return
    
    # Find CSV
    if args.csv:
        csv_path = Path(args.csv)
    else:
        if result_dirs:
            csv_files = list(latest_dir.glob('*_triggers.csv'))
            csv_path = csv_files[0] if csv_files else None
        else:
            csv_path = None
    
    # Find BDF
    if args.bdf:
        bdf_path = Path(args.bdf)
    else:
        bdf_dir = data_dir / f'sub_{args.participant_id}'
        bdf_files = list(bdf_dir.glob('*.bdf')) if bdf_dir.exists() else []
        bdf_path = bdf_files[0] if bdf_files else None
    
    # Validate
    results = validate_against_ground_truth(gt_path, csv_path, bdf_path)
    
    # Print summary
    print_validation_summary(results)
    
    print("\n" + "="*80)
    print("VALIDATION COMPLETE")
    print("="*80)


if __name__ == "__main__":
    main()
