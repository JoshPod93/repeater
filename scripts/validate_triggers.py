#!/usr/bin/env python3
"""
Standalone trigger validation script for real-time data.

Comprehensive Trigger Validation System

Compares triggers from BDF files (actual recorded) vs Mirror CSV files (intended to send)
to detect any discrepancies in trigger timing, counts, or sequences.

Based on: grasp/paradigm/trigger_validation.py

Usage:
    python scripts/validate_triggers.py --bdf-file data/sub_9999/sub_9999.bdf --results-dir data/results/sub-9999_20260127_155544
    python scripts/validate_triggers.py --participant-id 9999
"""
import argparse
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mne
from collections import Counter
from pathlib import Path


def load_bdf_triggers(bdf_path):
    """Extract all triggers from BDF file with timestamps."""
    if not os.path.exists(bdf_path):
        raise FileNotFoundError(f"BDF file not found: {bdf_path}")
    
    print(f"Loading BDF: {bdf_path}")
    raw = mne.io.read_raw_bdf(bdf_path, preload=True, verbose=False)
    
    # Find trigger channel
    trigger_channel = None
    for ch_name in raw.ch_names:
        if 'Status' in ch_name or 'STIM' in ch_name or 'status' in ch_name or 'stim' in ch_name:
            trigger_channel = ch_name
            break
    
    if trigger_channel is None:
        raise ValueError("No Status/STIM channel found in BDF!")
    
    # Extract trigger data
    trigger_data = raw.get_data(picks=[trigger_channel])[0].astype(np.int64)
    sfreq = raw.info['sfreq']
    
    # BioSemi-style trigger processing - consider low byte only
    low_byte = trigger_data & 0xFF
    
    # Find points where low_byte changes (rising/falling edges)
    trigger_changes = np.where(np.diff(low_byte) != 0)[0]
    idx = trigger_changes + 1
    vals = low_byte[idx].astype(int)
    
    # Filter out zeros - the channel returns to 0 between triggers
    non_zero_mask = vals != 0
    vals = vals[non_zero_mask]
    idx = idx[non_zero_mask]
    
    # Convert to timestamps (seconds)
    timestamps = idx / sfreq
    
    bdf_triggers = []
    for i, (val, ts, samp) in enumerate(zip(vals, timestamps, idx)):
        bdf_triggers.append({
            'index': i,
            'trigger_value': int(val),
            'timestamp': float(ts),
            'sample_index': int(samp)
        })
    
    print(f"  Extracted {len(bdf_triggers)} triggers from BDF")
    return bdf_triggers, sfreq


def load_mirror_csv(results_folder):
    """Load mirror CSV file from results folder."""
    # Our project uses a single CSV file per session, not per block
    csv_path = None
    
    # Look for triggers CSV file
    csv_patterns = [
        '*_triggers.csv',
        'triggers.csv',
        '*trigger*.csv'
    ]
    
    for pattern in csv_patterns:
        csv_files = list(Path(results_folder).glob(pattern))
        if csv_files:
            csv_path = csv_files[0]
            break
    
    if csv_path is None:
        raise ValueError(f"No trigger CSV file found in {results_folder}")
    
    print(f"Loading mirror CSV: {csv_path}")
    df = pd.read_csv(csv_path)
    
    if df.empty:
        raise ValueError(f"Mirror CSV is empty: {csv_path}")
    
    # Our CSV has: timestamp_psychopy, trigger_code, event_name, sent_to_eeg
    # Convert to format expected by alignment function
    # Filter to only triggers sent to EEG
    df_sent = df[df['sent_to_eeg'] == 'yes'].copy()
    
    if df_sent.empty:
        raise ValueError("No triggers marked as 'sent_to_eeg' in CSV")
    
    # Rename columns to match expected format
    df_sent['trigger_value'] = df_sent['trigger_code']
    df_sent['system_time'] = df_sent['timestamp_psychopy']
    
    # Sort by timestamp
    df_sent = df_sent.sort_values('system_time').reset_index(drop=True)
    
    print(f"  Loaded {len(df_sent)} triggers from CSV (sent to EEG)")
    return df_sent


def align_triggers_by_sequence(bdf_triggers, mirror_triggers):
    """Strict sequential alignment - if expected trigger isn't found, skip it to avoid false positives."""
    print(f"Aligning triggers with strict sequential matching...")
    
    # Extract trigger sequences
    bdf_sequence = [t['trigger_value'] for t in bdf_triggers]
    mirror_sequence = mirror_triggers['trigger_value'].tolist()
    
    print(f"BDF sequence length: {len(bdf_sequence)}")
    print(f"Mirror sequence length: {len(mirror_sequence)}")
    
    aligned_pairs = []
    bdf_unmatched = []
    mirror_unmatched = []
    
    # Strict sequential alignment - no searching ahead to avoid false positives
    bdf_index = 0
    mirror_index = 0
    
    while bdf_index < len(bdf_sequence) and mirror_index < len(mirror_sequence):
        bdf_value = bdf_sequence[bdf_index]
        mirror_value = mirror_sequence[mirror_index]
        
        if bdf_value == mirror_value:
            # Perfect match at current positions -> compute time_diff
            bdf_ts = bdf_triggers[bdf_index]['timestamp']
            mirror_ts = float(mirror_triggers.iloc[mirror_index]['system_time'])
            time_diff = bdf_ts - mirror_ts  # seconds (BDF_time - Mirror_time)
            
            aligned_pairs.append({
                'bdf_index': bdf_index,
                'mirror_index': mirror_index,
                'bdf_trigger': bdf_triggers[bdf_index],
                'mirror_trigger': mirror_triggers.iloc[mirror_index],
                'status': 'MATCHED',
                'time_diff': time_diff
            })
            bdf_index += 1
            mirror_index += 1
            
        else:
            # No match at current positions - treat mirror trigger as missing from BDF at this position
            mirror_unmatched.append({
                'mirror_index': mirror_index,
                'mirror_trigger': mirror_triggers.iloc[mirror_index],
                'status': 'MIRROR_MISSING',
                'reason': f'Expected at BDF position {bdf_index}, found {bdf_value} instead of {mirror_value}'
            })
            mirror_index += 1
            # Don't advance bdf_index - keep checking the same BDF trigger against next mirror trigger
    
    # Handle remaining triggers
    for remaining_bdf_idx in range(bdf_index, len(bdf_sequence)):
        bdf_unmatched.append({
            'bdf_index': remaining_bdf_idx,
            'bdf_trigger': bdf_triggers[remaining_bdf_idx],
            'status': 'BDF_EXTRA',
            'reason': 'Remaining after mirror sequence ended'
        })
    
    for remaining_mirror_idx in range(mirror_index, len(mirror_sequence)):
        mirror_unmatched.append({
            'mirror_index': remaining_mirror_idx,
            'mirror_trigger': mirror_triggers.iloc[remaining_mirror_idx],
            'status': 'MIRROR_MISSING',
            'reason': 'Remaining after BDF sequence ended'
        })
    
    print(f"Strict sequential alignment results:")
    print(f"  Matched: {len(aligned_pairs)}")
    print(f"  BDF extra: {len(bdf_unmatched)}")
    print(f"  Mirror missing: {len(mirror_unmatched)}")
    
    return aligned_pairs, bdf_unmatched, mirror_unmatched


def analyze_discrepancies(aligned_pairs, bdf_unmatched, mirror_unmatched):
    """Analyze and categorize discrepancies focusing on missing triggers."""
    print(f"\n{'='*60}")
    print("CHRONOLOGICAL SEQUENCE ANALYSIS")
    print(f"{'='*60}")
    
    # Count different types of issues
    matched = len([p for p in aligned_pairs if p['status'] == 'MATCHED'])
    mismatched = len([p for p in aligned_pairs if p.get('status') == 'MISMATCH'])
    bdf_extra = len(bdf_unmatched)
    mirror_extra = len(mirror_unmatched)
    
    total_bdf = matched + mismatched + bdf_extra
    total_mirror = matched + mismatched + mirror_extra
    
    print(f"Mirror triggers sent: {total_mirror}")
    print(f"BDF triggers recorded: {total_bdf}")
    print(f"Difference: {total_mirror - total_bdf} (positive = missing from BDF)")
    
    if total_bdf == total_mirror and mismatched == 0 and bdf_extra == 0 and mirror_extra == 0:
        print("PERFECT: All intended triggers were recorded!")
        return
    
    # CRITICAL: Analyze missing triggers (mirror extra = sent but not recorded)
    if mirror_extra > 0:
        print(f"\nCRITICAL: {mirror_extra} TRIGGERS MISSING FROM BDF!")
        print("   These triggers were sent but not recorded by BioSemi:")
        
        missing_values = [int(t['mirror_trigger']['trigger_value']) for t in mirror_unmatched]
        
        # Group by trigger value
        missing_counts = Counter(missing_values)
        
        print(f"\n   Missing trigger counts:")
        for trigger_val, count in missing_counts.most_common():
            print(f"     Trigger {trigger_val}: {count} missing")
        
        # Show first few missing triggers with context
        print(f"\n   First 20 missing triggers:")
        for i, missing in enumerate(mirror_unmatched[:20]):
            trigger = missing['mirror_trigger']
            mirror_idx = missing['mirror_index']
            reason = missing.get('reason', 'Unknown')
            # trigger is a Series - produce human-readable
            tv = int(trigger['trigger_value']) if 'trigger_value' in trigger.index else trigger.get('trigger_value', 'NA')
            event_name = trigger.get('event_name', 'NA') if 'event_name' in trigger.index else trigger.get('event_name', 'NA')
            print(f"     {i+1}. Mirror pos {mirror_idx}: Trigger {tv} ({event_name}) - {reason}")
    
    # Analyze mismatched triggers (same position, different values)
    if mismatched > 0:
        print(f"\nMISMATCHED TRIGGERS ({mismatched}):")
        print("   Same position but different values (possible corruption):")
        
        for i, pair in enumerate(aligned_pairs):
            if pair['status'] == 'MISMATCH':
                pos = pair.get('sequence_position', i)
                bdf_val = pair.get('bdf_value')
                mirror_val = pair.get('mirror_value')
                print(f"     Position {pos}: BDF={bdf_val}, Mirror={mirror_val}")
                if i >= 9:  # Show first 10
                    break
    
    # Analyze extra BDF triggers (recorded but not sent)
    if bdf_extra > 0:
        print(f"\nEXTRA BDF TRIGGERS ({bdf_extra}):")
        print("   These triggers were recorded but not in mirror CSV:")
        
        extra_values = [t['bdf_trigger']['trigger_value'] for t in bdf_unmatched]
        extra_counts = Counter(extra_values)
        
        for trigger_val, count in extra_counts.most_common():
            print(f"   Trigger {trigger_val}: {count} extra")
    
    # Calculate drop rate
    if total_mirror > 0:
        drop_rate = mirror_extra / total_mirror
        print(f"\nDROP RATE ANALYSIS:")
        print(f"   Triggers sent: {total_mirror}")
        print(f"   Triggers dropped: {mirror_extra}")
        print(f"   Drop rate: {drop_rate:.4f} ({drop_rate*100:.2f}%)")
        
        if drop_rate == 0:
            print("   [PERFECT] No trigger drops detected!")
        elif drop_rate < 0.01:
            print("   [EXCELLENT] <1% drop rate")
        elif drop_rate < 0.05:
            print("   [ACCEPTABLE] <5% drop rate")
        else:
            print("   [PROBLEM] >5% drop rate - investigate immediately!")


def create_validation_plot(bdf_triggers, mirror_triggers, aligned_pairs, bdf_unmatched, mirror_unmatched, output_path):
    """Create comprehensive validation plot with distribution and timing difference."""
    print(f"Creating validation plot: {output_path}")

    fig, axes = plt.subplots(2, 1, figsize=(12, 9), sharex=False, gridspec_kw={'hspace': 0.4})

    # --------------------------
    # Plot 1: Trigger value distribution
    # --------------------------
    ax1 = axes[0]

    bdf_values = [t['trigger_value'] for t in bdf_triggers]
    mirror_values = mirror_triggers['trigger_value'].values

    bdf_value_counts = pd.Series(bdf_values).value_counts().sort_index()
    mirror_value_counts = pd.Series(mirror_values).value_counts().sort_index()

    all_values = sorted(set(bdf_values + list(mirror_values)))
    x_pos = np.arange(len(all_values))
    bdf_counts = [int(bdf_value_counts.get(val, 0)) for val in all_values]
    mirror_counts = [int(mirror_value_counts.get(val, 0)) for val in all_values]

    width = 0.35
    ax1.bar(x_pos - width/2, bdf_counts, width, label='BDF', alpha=0.7)
    ax1.bar(x_pos + width/2, mirror_counts, width, label='Mirror', alpha=0.7)

    ax1.set_xlabel('Trigger Value')
    ax1.set_ylabel('Count')
    ax1.set_title('Trigger Value Distribution')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(all_values, rotation=90, ha='right', fontsize=8)
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # --------------------------
    # Plot 2: Timing differences (matched pairs only)
    # --------------------------
    ax2 = axes[1]

    matched_time_diffs = [p['time_diff']*1000 for p in aligned_pairs if 'time_diff' in p and p['status']=='MATCHED']
    if matched_time_diffs:
        ax2.hist(matched_time_diffs, bins=50, alpha=0.7, edgecolor='black')
        mean_td = np.mean(matched_time_diffs)
        ax2.axvline(mean_td, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_td:.3f} ms')
        ax2.set_xlabel('Time Difference (ms)')
        ax2.set_ylabel('Frequency')
        ax2.set_title('Timing Differences (Matched Pairs)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
    else:
        ax2.text(0.5, 0.5, 'No matched timing pairs available', ha='center', va='center', transform=ax2.transAxes)

    plt.savefig(output_path, dpi=300)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description='Validate triggers between BDF and mirror CSV files')
    parser.add_argument('--bdf-file', type=str, help='Path to BDF file')
    parser.add_argument('--results-dir', type=str, help='Path to results directory containing trigger CSV')
    parser.add_argument('--participant-id', type=str, help='Participant ID (auto-detects paths)')
    parser.add_argument('--output-dir', type=str, default=None, help='Output directory for plots (defaults to results directory)')
    
    args = parser.parse_args()
    
    # Auto-detect paths if participant ID provided
    if args.participant_id and not args.bdf_file:
        project_root = Path(__file__).parent.parent
        # Find BDF file
        bdf_dir = project_root / 'data' / f'sub_{args.participant_id}'
        bdf_files = list(bdf_dir.glob('*.bdf'))
        if not bdf_files:
            print(f"ERROR: No BDF files found in {bdf_dir}")
            return
        args.bdf_file = str(bdf_files[0])
        print(f"Auto-detected BDF file: {args.bdf_file}")
    
    if args.participant_id and not args.results_dir:
        project_root = Path(__file__).parent.parent
        # Find most recent results directory for participant
        results_base = project_root / 'data' / 'results'
        pattern = f'sub-{args.participant_id}_*'
        results_dirs = list(results_base.glob(pattern))
        if not results_dirs:
            print(f"ERROR: No results directories found for participant {args.participant_id}")
            return
        # Get most recent
        args.results_dir = str(max(results_dirs, key=lambda p: p.stat().st_mtime))
        print(f"Auto-detected results directory: {args.results_dir}")
    
    if not args.bdf_file or not args.results_dir:
        parser.print_help()
        return
    
    bdf_path = args.bdf_file
    results_dir = Path(args.results_dir)
    
    # Set output directory to results directory if not specified
    if args.output_dir is None:
        args.output_dir = str(results_dir)
    else:
        args.output_dir = str(Path(args.output_dir))
    
    # Load triggers
    try:
        bdf_triggers, sfreq = load_bdf_triggers(bdf_path)
        mirror_triggers = load_mirror_csv(results_dir)
        
        # Align triggers by sequence order
        aligned_pairs, bdf_unmatched, mirror_unmatched = align_triggers_by_sequence(
            bdf_triggers, mirror_triggers
        )
        
        # Analyze discrepancies
        analyze_discrepancies(aligned_pairs, bdf_unmatched, mirror_unmatched)
        
        # Create validation plot
        participant_id = Path(bdf_path).stem.replace('sub_', '').replace('.bdf', '')
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
        output_path = str(output_dir / f'trigger_validation_{participant_id}.png')
        print(f"Saving validation plot to: {output_path}")
        create_validation_plot(bdf_triggers, mirror_triggers, aligned_pairs, 
                             bdf_unmatched, mirror_unmatched, output_path)
        
        # Final assessment
        total_bdf = len(bdf_triggers)
        total_mirror = len(mirror_triggers)
        matched = len([p for p in aligned_pairs if p['status'] == 'MATCHED'])
        
        print(f"\n{'='*60}")
        print("FINAL ASSESSMENT")
        print(f"{'='*60}")
        
        if total_bdf == total_mirror and matched == total_bdf:
            print("[PERFECT] All triggers match perfectly!")
        elif abs(total_bdf - total_mirror) <= 2 and matched >= min(total_bdf, total_mirror) * 0.95:
            print("[GOOD] Minor discrepancies, likely acceptable")
        else:
            print("[PROBLEM] Significant discrepancies detected!")
            print("   This indicates trigger dropping or timing issues.")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return


if __name__ == "__main__":
    main()
