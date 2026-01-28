#!/usr/bin/env python3
"""
Quick test of randomization with new 2-category, 5-items-each setup.
"""

import sys
from pathlib import Path
from collections import Counter

# Add parent directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import load_config
import sys
import importlib.util
# Import randomization_utils directly without triggering psychopy imports
spec = importlib.util.spec_from_file_location(
    "randomization_utils",
    project_root / "paradigm" / "utils" / "randomization_utils.py"
)
randomization_utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(randomization_utils)
create_stratified_block_sequence = randomization_utils.create_stratified_block_sequence

from datetime import datetime
import numpy as np

def test_randomization():
    """Test randomization with new config."""
    config = load_config()
    
    concepts_a = config.get('CONCEPTS_CATEGORY_A', [])
    concepts_b = config.get('CONCEPTS_CATEGORY_B', [])
    n_trials = config.get('N_TRIALS', 100)
    n_blocks = config.get('N_BLOCKS', 10)
    
    print("="*70)
    print("RANDOMIZATION TEST")
    print("="*70)
    print(f"\nConfiguration:")
    print(f"  Category A ({len(concepts_a)} items): {concepts_a}")
    print(f"  Category B ({len(concepts_b)} items): {concepts_b}")
    print(f"  Total trials: {n_trials}")
    print(f"  Blocks: {n_blocks}")
    print(f"  Trials per block: {n_trials // n_blocks}")
    
    # Test single block generation
    print(f"\n{'='*70}")
    print("Testing Block 0 (10 trials)")
    print("="*70)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    block_trials = create_stratified_block_sequence(
        n_trials_per_block=10,
        concepts_a=concepts_a,
        concepts_b=concepts_b,
        block_num=0,
        participant_id='test_9999',
        timestamp=timestamp
    )
    
    print(f"\nGenerated {len(block_trials)} trials:")
    for i, trial in enumerate(block_trials, 1):
        case_display = trial.get('case', 'lower')
        display_concept = trial['concept'].upper() if case_display == 'upper' else trial['concept'].lower()
        print(f"  {i:2d}. {display_concept:12s} (Category {trial['category']}, {case_display})")
    
    # Count distribution
    concept_counts = Counter([t['concept'] for t in block_trials])
    category_counts = Counter([t['category'] for t in block_trials])
    case_counts = Counter([t.get('case', 'lower') for t in block_trials])
    
    print(f"\nDistribution:")
    print(f"  Category A: {category_counts.get('A', 0)} trials")
    print(f"  Category B: {category_counts.get('B', 0)} trials")
    print(f"  Case - Upper: {case_counts.get('upper', 0)}, Lower: {case_counts.get('lower', 0)}")
    print(f"\n  Concept counts (should be 1 each):")
    for concept in sorted(set(concepts_a + concepts_b)):
        count = concept_counts.get(concept, 0)
        status = "OK" if count == 1 else "ERROR"
        print(f"    {concept:12s}: {count} [{status}]")
    
    # Test full protocol (all blocks)
    print(f"\n{'='*70}")
    print(f"Testing Full Protocol ({n_blocks} blocks, {n_trials} total trials)")
    print("="*70)
    
    all_blocks_trials = []
    trials_per_block = n_trials // n_blocks
    
    for b in range(n_blocks):
        if b == n_blocks - 1:
            # Last block gets remainder
            remaining = n_trials - (trials_per_block * (n_blocks - 1))
            block_count = max(remaining, trials_per_block)
        else:
            block_count = trials_per_block
        
        block_trials = create_stratified_block_sequence(
            n_trials_per_block=block_count,
            concepts_a=concepts_a,
            concepts_b=concepts_b,
            block_num=b,
            participant_id='test_9999',
            timestamp=timestamp
        )
        all_blocks_trials.append(block_trials)
    
    # Analyze full protocol
    all_trials = [t for block in all_blocks_trials for t in block]
    total_concept_counts = Counter([t['concept'] for t in all_trials])
    total_category_counts = Counter([t['category'] for t in all_trials])
    
    print(f"\nFull Protocol Analysis:")
    print(f"  Total trials: {len(all_trials)}")
    print(f"  Category A: {total_category_counts.get('A', 0)} trials")
    print(f"  Category B: {total_category_counts.get('B', 0)} trials")
    print(f"\n  Concept counts (should be ~10 each for 100 trials):")
    for concept in sorted(set(concepts_a + concepts_b)):
        count = total_concept_counts.get(concept, 0)
        expected = n_trials // len(set(concepts_a + concepts_b))
        status = "OK" if abs(count - expected) <= 2 else "WARN"
        print(f"    {concept:12s}: {count:3d} (expected ~{expected}) [{status}]")
    
    # Check case distribution per block (should be 5 upper, 5 lower per block)
    print(f"\n  Case distribution per block:")
    all_blocks_case_ok = True
    for b, block_trials in enumerate(all_blocks_trials):
        block_case_counts = Counter([t.get('case', 'lower') for t in block_trials])
        upper_count = block_case_counts.get('upper', 0)
        lower_count = block_case_counts.get('lower', 0)
        is_balanced = (upper_count == 5 and lower_count == 5)
        if not is_balanced:
            all_blocks_case_ok = False
        status = "OK" if is_balanced else "ERROR"
        print(f"    Block {b}: Upper={upper_count}, Lower={lower_count} [{status}]")
    
    # Check global case distribution
    case_counts = Counter([t.get('case', 'lower') for t in all_trials])
    if 'upper' in case_counts or 'lower' in case_counts:
        print(f"\n  Global case distribution:")
        print(f"    Upper case: {case_counts.get('upper', 0)} trials")
        print(f"    Lower case: {case_counts.get('lower', 0)} trials")
        total_cases = case_counts.get('upper', 0) + case_counts.get('lower', 0)
        if total_cases > 0:
            upper_pct = (case_counts.get('upper', 0) / total_cases) * 100
            print(f"    Distribution: {upper_pct:.1f}% upper, {100-upper_pct:.1f}% lower")
            if abs(upper_pct - 50) <= 5:
                print(f"    [OK] Global case distribution is balanced (~50/50)")
            else:
                print(f"    [WARN] Global case distribution is not balanced")
    
    if all_blocks_case_ok:
        print(f"\n  [OK] All blocks have balanced case distribution (5 upper, 5 lower per block)")
    else:
        print(f"\n  [ERROR] Some blocks do not have balanced case distribution!")
    
    print(f"\n{'='*70}")
    print("TEST COMPLETE")
    print("="*70)

if __name__ == "__main__":
    test_randomization()
