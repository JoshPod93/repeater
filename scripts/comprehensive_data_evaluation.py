#!/usr/bin/env python3
"""
Comprehensive evaluation of collected data - complete summary report.
"""

import sys
import argparse
import pandas as pd
from pathlib import Path
from collections import Counter
import json

# Add parent directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import load_config

def find_latest_results_dir(participant_id: str = '9999') -> Path:
    """Find the latest results directory for a participant."""
    results_base = project_root / 'data' / 'results'
    pattern = f'sub-{participant_id}_*'
    matching_dirs = list(results_base.glob(pattern))
    
    if not matching_dirs:
        raise FileNotFoundError(f"No results directory found for participant {participant_id}")
    
    # Return the most recently modified directory
    latest_dir = max(matching_dirs, key=lambda p: p.stat().st_mtime)
    return latest_dir

def main():
    parser = argparse.ArgumentParser(description='Comprehensive data evaluation')
    parser.add_argument('--participant-id', type=str, default='9999',
                       help='Participant ID (default: 9999)')
    args = parser.parse_args()
    
    # Find latest results directory
    try:
        results_dir = find_latest_results_dir(args.participant_id)
        print(f"Using results directory: {results_dir.name}")
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        return
    csv_files = sorted(results_dir.glob('*_triggers.csv'))
    block_dirs = sorted([d for d in results_dir.iterdir() if d.is_dir() and d.name.startswith('Block_')])
    
    # Load all triggers
    all_triggers = []
    csv_details = []
    
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        sent = df[df['sent_to_eeg'] == 'yes'].copy()
        csv_details.append({
            'file': csv_file.name,
            'sent': len(sent),
            'codes': sent['trigger_code'].tolist() if len(sent) > 0 else []
        })
        all_triggers.extend(sent['trigger_code'].tolist() if len(sent) > 0 else [])
    
    code_counts = Counter(all_triggers)
    config = load_config()
    
    print("="*80)
    print("COMPREHENSIVE DATA EVALUATION REPORT")
    print("="*80)
    
    print(f"\n1. BLOCK COMPLETION:")
    print(f"   Blocks completed: {len(block_dirs)}/10")
    print(f"   Blocks found: {[d.name for d in block_dirs]}")
    if len(block_dirs) < 10:
        expected_blocks = set(range(10))
        found_blocks = {int(d.name.split('_')[1]) for d in block_dirs}
        missing = sorted(expected_blocks - found_blocks)
        print(f"   [WARNING] Missing blocks: {missing}")
    
    print(f"\n2. TRIGGER FILES:")
    print(f"   CSV files: {len(csv_files)}")
    print(f"   Empty CSVs: {sum(1 for d in csv_details if d['sent'] == 0)}")
    for detail in csv_details:
        status = "[EMPTY]" if detail['sent'] == 0 else f"{detail['sent']:4d} triggers"
        print(f"     {detail['file']:50s}: {status}")
    
    print(f"\n3. TRIGGER COUNTS:")
    total_sent = len(all_triggers)
    expected_total = 1320  # 10 blocks × 132 triggers
    print(f"   Total triggers sent: {total_sent}")
    print(f"   Expected: {expected_total}")
    print(f"   Difference: {total_sent - expected_total}")
    if total_sent == expected_total:
        print(f"   [OK] All triggers present")
    else:
        print(f"   [WARNING] Missing {expected_total - total_sent} triggers")
    
    print(f"\n4. TRIGGER CODE VERIFICATION:")
    
    # Block codes
    block_starts = [c for c in all_triggers if 61 <= c <= 70]
    block_ends = [c for c in all_triggers if 71 <= c <= 80]
    print(f"   Block start codes: {sorted(set(block_starts))} (expected: 61-70)")
    print(f"   Block end codes: {sorted(set(block_ends))} (expected: 71-80)")
    missing_starts = set(range(61, 71)) - set(block_starts)
    missing_ends = set(range(71, 81)) - set(block_ends)
    if missing_starts or missing_ends:
        print(f"   [WARNING] Missing block codes: start={missing_starts}, end={missing_ends}")
    
    # Trial codes
    trial_starts = [c for c in all_triggers if 101 <= c <= 110]
    trial_ends = [c for c in all_triggers if 151 <= c <= 160]
    print(f"   Trial start codes: {sorted(set(trial_starts))} (expected: 101-110)")
    print(f"   Trial end codes: {sorted(set(trial_ends))} (expected: 151-160)")
    print(f"   Trial start count: {len(trial_starts)} (expected: 100)")
    print(f"   Trial end count: {len(trial_ends)} (expected: 100)")
    
    # Base codes
    fixation_count = code_counts.get(1, 0)
    concept_a_count = code_counts.get(10, 0)
    concept_b_count = code_counts.get(20, 0)
    beep_start_count = code_counts.get(30, 0)
    beep_counts = sum(code_counts.get(i, 0) for i in range(31, 39))
    
    print(f"\n5. BASE CODE COUNTS:")
    print(f"   Fixation (1): {fixation_count} (expected: 100)")
    print(f"   Concept A (10): {concept_a_count} (expected: 50)")
    print(f"   Concept B (20): {concept_b_count} (expected: 50)")
    print(f"   Beep start (30): {beep_start_count} (expected: 100)")
    print(f"   Beeps (31-38): {beep_counts} (expected: 800)")
    
    print(f"\n6. CODE DISTRIBUTION SUMMARY:")
    print(f"   Unique codes used: {len(code_counts)}")
    print(f"   Code range: {min(all_triggers) if all_triggers else 'N/A'} - {max(all_triggers) if all_triggers else 'N/A'}")
    print(f"   All codes within 0-255: {'[OK]' if (not all_triggers or max(all_triggers) <= 255) else '[ERROR]'}")
    
    print(f"\n7. DATA QUALITY:")
    issues = []
    if len(block_dirs) < 10:
        issues.append(f"Missing {10 - len(block_dirs)} block(s)")
    if total_sent < expected_total:
        issues.append(f"Missing {expected_total - total_sent} triggers")
    if missing_starts or missing_ends:
        issues.append(f"Missing block codes")
    if len(trial_starts) < 100:
        issues.append(f"Missing {100 - len(trial_starts)} trial start triggers")
    if len(trial_ends) < 100:
        issues.append(f"Missing {100 - len(trial_ends)} trial end triggers")
    
    if issues:
        print(f"   [WARNING] Issues found:")
        for issue in issues:
            print(f"     - {issue}")
    else:
        print(f"   [OK] All data complete")
    
    print(f"\n8. SUMMARY:")
    print(f"   Blocks: {len(block_dirs)}/10 completed")
    print(f"   Triggers: {total_sent}/{expected_total}")
    if expected_total > 0:
        print(f"   Completion: {(total_sent/expected_total)*100:.1f}%")
    print(f"   Status: {'[COMPLETE]' if total_sent == expected_total and len(block_dirs) == 10 else '[INCOMPLETE]'}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()
