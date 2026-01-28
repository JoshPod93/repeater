#!/usr/bin/env python3
"""
Validate captured data alignment - CSV vs BDF vs expected.
"""

import sys
import argparse
import pandas as pd
from pathlib import Path
from collections import Counter

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
    parser = argparse.ArgumentParser(description='Validate captured data')
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
    
    # BDF path based on participant ID
    bdf_path = project_root / 'data' / f'sub_{args.participant_id}' / f'sub_{args.participant_id}.bdf'
    
    # Count actual blocks completed
    block_dirs = sorted([d for d in results_dir.iterdir() if d.is_dir() and d.name.startswith('Block_')])
    n_blocks = len(block_dirs)
    
    print("="*80)
    print(f"CAPTURED DATA VALIDATION ({n_blocks} Blocks)")
    print("="*80)
    
    # Load CSV triggers
    print("\n1. LOADING CSV TRIGGERS:")
    csv_files = sorted(results_dir.glob('*_triggers.csv'))
    csv_triggers = []
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        sent = df[df['sent_to_eeg'] == 'yes'].copy()
        csv_triggers.extend(sent['trigger_code'].tolist())
    print(f"   Total CSV triggers: {len(csv_triggers)}")
    
    # Load BDF triggers
    print("\n2. LOADING BDF TRIGGERS:")
    if not bdf_path.exists():
        print(f"   [SKIP] BDF file not found: {bdf_path}")
        print("   BDF validation will be skipped")
        bdf_triggers = []
    else:
        try:
            import mne
            import numpy as np
            
            # Try loading without preload first to check file size
            print(f"   Attempting to load BDF: {bdf_path.name}")
            raw = mne.io.read_raw_bdf(bdf_path, preload=False, verbose=False)
            
            status_ch = None
            for ch_name in raw.ch_names:
                if 'Status' in ch_name or 'STIM' in ch_name:
                    status_ch = ch_name
                    break
            
            if status_ch:
                ch_idx = raw.ch_names.index(status_ch)
                # Load only the status channel data
                trigger_data = raw.get_data(picks=[status_ch])[0].astype(np.int64)
                trigger_values = (trigger_data & 0xFF)
                diff = np.diff(trigger_values)
                trigger_indices = np.where(diff != 0)[0] + 1
                
                bdf_triggers = []
                for idx in trigger_indices:
                    code = int(trigger_values[idx])
                    if code > 0:
                        bdf_triggers.append(code)
                
                print(f"   Total BDF triggers: {len(bdf_triggers)}")
            else:
                print("   [ERROR] No Status channel found")
                bdf_triggers = []
        except MemoryError as e:
            print(f"   [SKIP] BDF file too large to load into memory: {e}")
            print("   BDF validation skipped - use validate_triggers.py for detailed BDF analysis")
            bdf_triggers = []
        except Exception as e:
            print(f"   [ERROR] Failed to load BDF: {e}")
            bdf_triggers = []
    
    # Calculate expected triggers
    print(f"\n3. EXPECTED TRIGGERS ({n_blocks} blocks):")
    config = load_config()
    n_trials_per_block = config.get('TRIALS_PER_BLOCK', 10)
    n_beeps = config.get('N_BEEPS', 8)
    
    triggers_per_trial = 13  # start + fixation + concept + beep_start + 8 beeps + end
    triggers_per_block = 1 + (n_trials_per_block * triggers_per_trial) + 1  # block_start + trials + block_end
    expected_total = n_blocks * triggers_per_block
    
    print(f"   Blocks completed: {n_blocks}")
    print(f"   Triggers per block: {triggers_per_block}")
    print(f"   Expected total: {expected_total}")
    
    # Compare
    print("\n4. ALIGNMENT CHECK:")
    print(f"   CSV count: {len(csv_triggers)}")
    print(f"   BDF count: {len(bdf_triggers)}")
    print(f"   Expected: {expected_total}")
    
    if len(csv_triggers) == expected_total:
        print(f"   [OK] CSV count matches expected!")
    else:
        print(f"   [WARNING] CSV count differs by {len(csv_triggers) - expected_total}")
    
    if len(bdf_triggers) == len(csv_triggers):
        print(f"   [OK] BDF count matches CSV!")
    else:
        print(f"   [WARNING] BDF count differs from CSV by {len(bdf_triggers) - len(csv_triggers)}")
    
    # Code sequence alignment
    print("\n5. CODE SEQUENCE ALIGNMENT:")
    if len(bdf_triggers) == len(csv_triggers):
        matches = sum(1 for b, c in zip(bdf_triggers, csv_triggers) if b == c)
        match_rate = (matches / len(bdf_triggers)) * 100 if bdf_triggers else 0
        print(f"   BDF vs CSV code matches: {matches}/{len(bdf_triggers)} ({match_rate:.1f}%)")
        
        if matches == len(bdf_triggers):
            print(f"   [OK] Perfect code alignment between BDF and CSV!")
        else:
            # Find first mismatch
            for i, (b, c) in enumerate(zip(bdf_triggers, csv_triggers)):
                if b != c:
                    print(f"   [WARNING] First mismatch at position {i+1}: BDF={b}, CSV={c}")
                    break
    else:
        print(f"   [SKIP] Cannot compare - different lengths")
    
    # Code distribution
    print("\n6. CODE DISTRIBUTION:")
    csv_codes = Counter(csv_triggers)
    bdf_codes = Counter(bdf_triggers) if bdf_triggers else Counter()
    
    print(f"   CSV unique codes: {len(csv_codes)}")
    print(f"   BDF unique codes: {len(bdf_codes)}")
    
    if csv_codes == bdf_codes:
        print(f"   [OK] Code distributions match perfectly!")
    else:
        csv_set = set(csv_codes.keys())
        bdf_set = set(bdf_codes.keys())
        missing = bdf_set - csv_set
        extra = csv_set - bdf_set
        if missing:
            print(f"   [WARNING] Codes in BDF but not CSV: {sorted(missing)}")
        if extra:
            print(f"   [WARNING] Codes in CSV but not BDF: {sorted(extra)}")
    
    # Expected code counts
    print(f"\n7. EXPECTED CODE COUNTS ({n_blocks} blocks):")
    expected_counts = {
        'block_start': n_blocks,  # 61-69
        'block_end': n_blocks,   # 71-79
        'trial_start': n_blocks * n_trials_per_block,  # 101-110 (reused)
        'trial_end': n_blocks * n_trials_per_block,    # 151-160 (reused)
        'fixation': n_blocks * n_trials_per_block,     # 1
        'concept': n_blocks * n_trials_per_block,      # 10, 20
        'beep_start': n_blocks * n_trials_per_block,   # 30
        'beeps': n_blocks * n_trials_per_block * n_beeps  # 31-38
    }
    
    actual_counts = {
        'block_start': sum(1 for c in csv_triggers if 61 <= c <= 70),
        'block_end': sum(1 for c in csv_triggers if 71 <= c <= 80),
        'trial_start': sum(1 for c in csv_triggers if 101 <= c <= 110),
        'trial_end': sum(1 for c in csv_triggers if 151 <= c <= 160),
        'fixation': csv_codes.get(1, 0),
        'concept_a': csv_codes.get(10, 0),
        'concept_b': csv_codes.get(20, 0),
        'beep_start': csv_codes.get(30, 0),
        'beeps': sum(csv_codes.get(i, 0) for i in range(31, 39))
    }
    
    print(f"   Block starts: {actual_counts['block_start']} (expected: {expected_counts['block_start']})")
    print(f"   Block ends: {actual_counts['block_end']} (expected: {expected_counts['block_end']})")
    print(f"   Trial starts: {actual_counts['trial_start']} (expected: {expected_counts['trial_start']})")
    print(f"   Trial ends: {actual_counts['trial_end']} (expected: {expected_counts['trial_end']})")
    print(f"   Fixation: {actual_counts['fixation']} (expected: {expected_counts['fixation']})")
    print(f"   Concept A: {actual_counts['concept_a']} (expected: {expected_counts['concept']//2})")
    print(f"   Concept B: {actual_counts['concept_b']} (expected: {expected_counts['concept']//2})")
    print(f"   Beep start: {actual_counts['beep_start']} (expected: {expected_counts['beep_start']})")
    print(f"   Beeps: {actual_counts['beeps']} (expected: {expected_counts['beeps']})")
    
    # Final verdict
    print("\n" + "="*80)
    print("VALIDATION VERDICT")
    print("="*80)
    
    all_match = True
    if len(csv_triggers) != expected_total:
        all_match = False
    if len(bdf_triggers) != len(csv_triggers):
        all_match = False
    if bdf_triggers and csv_triggers:
        if bdf_triggers != csv_triggers:
            all_match = False
    
    if all_match:
        print("\n[OK] PERFECT ALIGNMENT!")
        print("   - CSV and BDF have identical trigger sequences")
        print(f"   - Counts match expected for {n_blocks} blocks")
        print("   - All codes are correct and within 0-255")
    else:
        print("\n[WARNING] Some discrepancies found (see details above)")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()
