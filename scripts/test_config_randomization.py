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
        print(f"  {i:2d}. {trial['concept']:12s} (Category {trial['category']})")
    
    # Count distribution
    concept_counts = Counter([t['concept'] for t in block_trials])
    category_counts = Counter([t['category'] for t in block_trials])
    
    print(f"\nDistribution:")
    print(f"  Category A: {category_counts.get('A', 0)} trials")
    print(f"  Category B: {category_counts.get('B', 0)} trials")
    print(f"\n  Concept counts:")
    for concept in sorted(set(concepts_a + concepts_b)):
        count = concept_counts.get(concept, 0)
        print(f"    {concept:12s}: {count}")
    
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
    
    print(f"\n{'='*70}")
    print("TEST COMPLETE")
    print("="*70)

if __name__ == "__main__":
    test_randomization()
