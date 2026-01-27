#!/usr/bin/env python3
"""
Generate ground truth trigger sequence from randomization protocol.
Calculates exact expected triggers, distribution, and sequence for validation.
"""

import sys
import json
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Any

# Add parent directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import load_config

# Trigger code functions (avoiding psychopy import)
def get_trial_start_code(trial_num): return 100 + trial_num
def get_trial_end_code(trial_num): return 200 + trial_num
def get_block_start_code(block_num): return 60 + block_num  # FIXED
def get_block_end_code(block_num): return 70 + block_num    # FIXED
def get_beep_code(beep_num): return 30 + beep_num

TRIGGER_CODES = {
    'fixation': 1,
    'concept_category_a': 10,
    'concept_category_b': 20,
    'beep_start': 30,
    'beep_1': 31, 'beep_2': 32, 'beep_3': 33, 'beep_4': 34,
    'beep_5': 35, 'beep_6': 36, 'beep_7': 37, 'beep_8': 38,
}


def load_randomization_protocol(results_dir: Path, participant_id: str) -> Dict[str, Any]:
    """Load randomization protocol JSON."""
    if not results_dir.exists():
        raise FileNotFoundError(f"Results directory does not exist: {results_dir}")
    
    # Find most recent results directory
    pattern = f'sub-{participant_id}_*'
    result_dirs = list(results_dir.glob(pattern))
    if not result_dirs:
        # Try alternative pattern (with underscore instead of hyphen)
        pattern_alt = f'sub_{participant_id}_*'
        result_dirs = list(results_dir.glob(pattern_alt))
    
    if not result_dirs:
        print(f"Available directories in {results_dir}:")
        for d in results_dir.iterdir():
            if d.is_dir():
                print(f"  - {d.name}")
        raise FileNotFoundError(f"No results directory found for participant {participant_id}")
    
    # Get most recent
    latest_dir = max(result_dirs, key=lambda p: p.stat().st_mtime)
    print(f"Using results directory: {latest_dir.name}")
    
    # Find protocol JSON
    protocol_files = list(latest_dir.glob('*_randomization_protocol.json'))
    if not protocol_files:
        raise FileNotFoundError(f"No randomization protocol found in {latest_dir}")
    
    print(f"Loading protocol: {protocol_files[0].name}")
    with open(protocol_files[0], 'r') as f:
        return json.load(f)


def generate_ground_truth_triggers(protocol: Dict[str, Any], config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generate complete ground truth trigger sequence from protocol.
    
    Returns list of expected triggers with:
    - trigger_code
    - event_name
    - trial_num (if applicable)
    - block_num
    - concept (if applicable)
    - category (if applicable)
    - sequence_position (order in sequence)
    """
    all_blocks_trials = protocol['all_blocks_trials']
    n_beeps = config.get('N_BEEPS', 8)
    
    ground_truth = []
    sequence_pos = 0
    
    for block_idx, block_trials in enumerate(all_blocks_trials):
        if not block_trials:
            continue
        
        block_num = block_idx + 1  # 1-indexed for trigger codes
        global_trial_start = sum(len(bt) for bt in all_blocks_trials[:block_idx]) + 1
        
        # Block start trigger
        sequence_pos += 1
        ground_truth.append({
            'sequence_position': sequence_pos,
            'trigger_code': get_block_start_code(block_num),
            'event_name': f'block_{block_num}_start',
            'block_num': block_num,
            'trial_num': None,
            'concept': None,
            'category': None,
            'trigger_type': 'block_start'
        })
        
        # Process each trial in block
        for trial_idx, trial_spec in enumerate(block_trials):
            global_trial_num = global_trial_start + trial_idx
            concept = trial_spec['concept']
            category = trial_spec['category']
            
            # Trial start
            sequence_pos += 1
            ground_truth.append({
                'sequence_position': sequence_pos,
                'trigger_code': get_trial_start_code(global_trial_num),
                'event_name': f'trial_{global_trial_num}_start',
                'block_num': block_num,
                'trial_num': global_trial_num,
                'concept': concept,
                'category': category,
                'trigger_type': 'trial_start'
            })
            
            # Fixation
            sequence_pos += 1
            ground_truth.append({
                'sequence_position': sequence_pos,
                'trigger_code': TRIGGER_CODES['fixation'],
                'event_name': 'fixation',
                'block_num': block_num,
                'trial_num': global_trial_num,
                'concept': concept,
                'category': category,
                'trigger_type': 'fixation'
            })
            
            # Concept presentation (category-specific)
            concept_code = TRIGGER_CODES[f'concept_category_{category.lower()}']
            sequence_pos += 1
            ground_truth.append({
                'sequence_position': sequence_pos,
                'trigger_code': concept_code,
                'event_name': f'concept_{concept}_{category}',
                'block_num': block_num,
                'trial_num': global_trial_num,
                'concept': concept,
                'category': category,
                'trigger_type': 'concept'
            })
            
            # Beep start
            sequence_pos += 1
            ground_truth.append({
                'sequence_position': sequence_pos,
                'trigger_code': TRIGGER_CODES['beep_start'],
                'event_name': 'beep_start',
                'block_num': block_num,
                'trial_num': global_trial_num,
                'concept': concept,
                'category': category,
                'trigger_type': 'beep_start'
            })
            
            # Beeps (1 through n_beeps)
            for beep_num in range(1, n_beeps + 1):
                sequence_pos += 1
                ground_truth.append({
                    'sequence_position': sequence_pos,
                    'trigger_code': get_beep_code(beep_num),
                    'event_name': f'beep_{beep_num}',
                    'block_num': block_num,
                    'trial_num': global_trial_num,
                    'concept': concept,
                    'category': category,
                    'trigger_type': 'beep'
                })
            
            # Trial end
            sequence_pos += 1
            ground_truth.append({
                'sequence_position': sequence_pos,
                'trigger_code': get_trial_end_code(global_trial_num),
                'event_name': f'trial_{global_trial_num}_end',
                'block_num': block_num,
                'trial_num': global_trial_num,
                'concept': concept,
                'category': category,
                'trigger_type': 'trial_end'
            })
        
        # Block end trigger
        sequence_pos += 1
        ground_truth.append({
            'sequence_position': sequence_pos,
            'trigger_code': get_block_end_code(block_num),
            'event_name': f'block_{block_num}_end',
            'block_num': block_num,
            'trial_num': None,
            'concept': None,
            'category': None,
            'trigger_type': 'block_end'
        })
    
    return ground_truth


def analyze_ground_truth(ground_truth: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze ground truth triggers and return statistics."""
    total_triggers = len(ground_truth)
    
    # Count by type
    type_counts = Counter(t['trigger_type'] for t in ground_truth)
    
    # Count by trigger code
    code_counts = Counter(t['trigger_code'] for t in ground_truth)
    
    # Count by block
    block_counts = Counter(t['block_num'] for t in ground_truth if t['block_num'])
    
    # Count by trial
    trial_counts = Counter(t['trial_num'] for t in ground_truth if t['trial_num'])
    
    # Count by concept
    concept_counts = Counter(t['concept'] for t in ground_truth if t['concept'])
    
    # Count by category
    category_counts = Counter(t['category'] for t in ground_truth if t['category'])
    
    # Unique trigger codes
    unique_codes = set(t['trigger_code'] for t in ground_truth)
    
    return {
        'total_triggers': total_triggers,
        'type_counts': dict(type_counts),
        'code_counts': dict(code_counts),
        'block_counts': dict(block_counts),
        'trial_counts': dict(trial_counts),
        'concept_counts': dict(concept_counts),
        'category_counts': dict(category_counts),
        'unique_codes': sorted(unique_codes),
        'num_unique_codes': len(unique_codes),
        'num_blocks': len(block_counts),
        'num_trials': len(trial_counts)
    }


def print_ground_truth_summary(ground_truth: List[Dict[str, Any]], stats: Dict[str, Any]):
    """Print comprehensive ground truth summary."""
    print("="*80)
    print("GROUND TRUTH TRIGGER SEQUENCE")
    print("="*80)
    
    print(f"\n1. OVERALL STATISTICS:")
    print(f"   Total triggers expected: {stats['total_triggers']}")
    print(f"   Unique trigger codes: {stats['num_unique_codes']}")
    print(f"   Number of blocks: {stats['num_blocks']}")
    print(f"   Number of trials: {stats['num_trials']}")
    
    print(f"\n2. TRIGGER TYPE DISTRIBUTION:")
    for trigger_type, count in sorted(stats['type_counts'].items()):
        print(f"   {trigger_type:20s}: {count:4d}")
    
    print(f"\n3. BLOCK DISTRIBUTION:")
    for block_num in sorted(stats['block_counts'].keys()):
        count = stats['block_counts'][block_num]
        print(f"   Block {block_num}: {count:4d} triggers")
    
    print(f"\n4. TRIAL DISTRIBUTION (first 5 and last 5):")
    sorted_trials = sorted(stats['trial_counts'].keys())
    for trial_num in sorted_trials[:5]:
        count = stats['trial_counts'][trial_num]
        print(f"   Trial {trial_num:3d}: {count:4d} triggers")
    if len(sorted_trials) > 10:
        print(f"   ... ({len(sorted_trials) - 10} more trials) ...")
    for trial_num in sorted_trials[-5:]:
        count = stats['trial_counts'][trial_num]
        print(f"   Trial {trial_num:3d}: {count:4d} triggers")
    
    print(f"\n5. CONCEPT DISTRIBUTION:")
    for concept, count in sorted(stats['concept_counts'].items()):
        print(f"   {concept:15s}: {count:4d} triggers")
    
    print(f"\n6. CATEGORY DISTRIBUTION:")
    for category, count in sorted(stats['category_counts'].items()):
        print(f"   Category {category}: {count:4d} triggers")
    
    print(f"\n7. TRIGGER CODE RANGES:")
    unique_codes = stats['unique_codes']
    print(f"   Min code: {min(unique_codes)}")
    print(f"   Max code: {max(unique_codes)}")
    print(f"   Code range: {min(unique_codes)}-{max(unique_codes)}")
    
    # Show first 20 triggers
    print(f"\n8. FIRST 20 TRIGGERS (sequence preview):")
    for trigger in ground_truth[:20]:
        block_str = str(trigger['block_num']) if trigger['block_num'] else 'N/A'
        trial_str = str(trigger['trial_num']) if trigger['trial_num'] else 'N/A'
        print(f"   {trigger['sequence_position']:4d}. Code {trigger['trigger_code']:3d} | "
              f"{trigger['event_name']:25s} | Block {block_str:>3s} | "
              f"Trial {trial_str:>3s}")
    
    if len(ground_truth) > 20:
        print(f"   ... ({len(ground_truth) - 20} more triggers) ...")
    
    # Show last 10 triggers
    print(f"\n9. LAST 10 TRIGGERS:")
    for trigger in ground_truth[-10:]:
        block_str = str(trigger['block_num']) if trigger['block_num'] else 'N/A'
        trial_str = str(trigger['trial_num']) if trigger['trial_num'] else 'N/A'
        print(f"   {trigger['sequence_position']:4d}. Code {trigger['trigger_code']:3d} | "
              f"{trigger['event_name']:25s} | Block {block_str:>3s} | "
              f"Trial {trial_str:>3s}")


def save_ground_truth(ground_truth: List[Dict[str, Any]], stats: Dict[str, Any], 
                     output_path: Path):
    """Save ground truth to JSON file."""
    output_data = {
        'statistics': stats,
        'trigger_sequence': ground_truth
    }
    
    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\n10. GROUND TRUTH SAVED:")
    print(f"    {output_path}")


def generate_protocol_from_config(config: Dict[str, Any], participant_id: str) -> Dict[str, Any]:
    """Generate protocol structure from config (for pre-run ground truth)."""
    import importlib.util
    import numpy as np
    from datetime import datetime
    
    # Import randomization_utils directly without psychopy dependency
    randomization_path = project_root / 'paradigm' / 'utils' / 'randomization_utils.py'
    spec = importlib.util.spec_from_file_location("randomization_utils", randomization_path)
    randomization_utils = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(randomization_utils)
    create_stratified_block_sequence = randomization_utils.create_stratified_block_sequence
    
    n_blocks = config.get('N_BLOCKS', 10)
    n_trials_total = config.get('N_TRIALS', 100)
    concepts_a = config.get('CONCEPTS_CATEGORY_A', [])
    concepts_b = config.get('CONCEPTS_CATEGORY_B', [])
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    trials_per_block = n_trials_total // n_blocks
    
    all_blocks_trials = []
    for b in range(n_blocks):
        if b == n_blocks - 1:
            remaining = n_trials_total - (trials_per_block * (n_blocks - 1))
            block_count = max(remaining, trials_per_block)
        else:
            block_count = trials_per_block
        
        block_trials = create_stratified_block_sequence(
            n_trials_per_block=block_count,
            concepts_a=concepts_a,
            concepts_b=concepts_b,
            block_num=b,
            participant_id=participant_id,
            timestamp=timestamp
        )
        all_blocks_trials.append(block_trials)
    
    return {
        'all_blocks_trials': all_blocks_trials,
        'config': {
            'N_BLOCKS': n_blocks,
            'N_TRIALS': n_trials_total,
            'CONCEPTS_CATEGORY_A': concepts_a,
            'CONCEPTS_CATEGORY_B': concepts_b
        }
    }


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate ground truth trigger sequence')
    parser.add_argument('--participant-id', type=str, required=True,
                       help='Participant ID')
    parser.add_argument('--output', type=str, default=None,
                       help='Output JSON file path (default: auto-detect)')
    parser.add_argument('--from-config', action='store_true',
                       help='Generate from config instead of existing protocol')
    
    args = parser.parse_args()
    
    # Load config
    config = load_config()
    
    # Load or generate protocol
    results_dir = project_root / 'data' / 'results'
    if args.from_config:
        print("Generating protocol from config...")
        protocol = generate_protocol_from_config(config, args.participant_id)
    else:
        try:
            protocol = load_randomization_protocol(results_dir, args.participant_id)
        except FileNotFoundError:
            print("No existing protocol found. Generating from config...")
            protocol = generate_protocol_from_config(config, args.participant_id)
    
    # Generate ground truth
    ground_truth = generate_ground_truth_triggers(protocol, config)
    
    # Analyze
    stats = analyze_ground_truth(ground_truth)
    
    # Print summary
    print_ground_truth_summary(ground_truth, stats)
    
    # Save
    if args.output:
        output_path = Path(args.output)
    else:
        # Auto-detect results directory
        pattern = f'sub-{args.participant_id}_*'
        result_dirs = list(results_dir.glob(pattern))
        if result_dirs:
            latest_dir = max(result_dirs, key=lambda p: p.stat().st_mtime)
            output_path = latest_dir / f'sub-{args.participant_id}_ground_truth_triggers.json'
        else:
            output_path = project_root / 'data' / f'ground_truth_{args.participant_id}.json'
    
    save_ground_truth(ground_truth, stats, output_path)
    
    print("\n" + "="*80)
    print("GROUND TRUTH GENERATION COMPLETE")
    print("="*80)


if __name__ == "__main__":
    main()
