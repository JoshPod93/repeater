"""
Test script for randomization protocol generation.

Tests stratified randomization ensuring:
- Equal representation of each concept-item (10 trials per item for 100 total trials)
- Unique randomization pattern per block
- Date-time based seeding for reproducibility but uniqueness
"""

import sys
from pathlib import Path
from datetime import datetime
from collections import Counter
import json

# Add parent directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import load_config
from paradigm.utils.randomization_utils import create_balanced_sequence


def create_stratified_block_sequence(
    n_trials_per_block: int,
    concepts_a: list,
    concepts_b: list,
    block_num: int,
    participant_id: str,
    session_id: int,
    timestamp: str
) -> list:
    """
    Create stratified trial sequence for a block.
    
    Ensures equal representation of each concept-item within the block.
    Uses date-time + block number + participant for unique seed per block.
    
    Parameters
    ----------
    n_trials_per_block : int
        Number of trials in this block
    concepts_a : list
        Category A concepts
    concepts_b : list
        Category B concepts
    block_num : int
        Block number (0-indexed)
    participant_id : str
        Participant ID
    session_id : int
        Session ID
    timestamp : str
        Timestamp string for seed generation
        
    Returns
    -------
    list
        Stratified trial sequence for this block
    """
    import numpy as np
    
    # Create unique seed for this block
    # Combines: participant_id + session_id + timestamp + block_num
    # This ensures each block has unique randomization while being reproducible
    seed_str = f"{participant_id}_{session_id}_{timestamp}_block{block_num}"
    seed = hash(seed_str) % (2**31)
    np.random.seed(seed)
    
    # Calculate trials per concept-item for this block
    n_concepts_a = len(concepts_a)
    n_concepts_b = len(concepts_b)
    
    # For balanced design, we need equal A/B trials
    trials_per_category = n_trials_per_block // 2
    
    # Calculate how many times each concept should appear in this block
    # This ensures stratification across the entire experiment
    trials_per_concept_a = trials_per_category // n_concepts_a
    trials_per_concept_b = trials_per_category // n_concepts_b
    
    # Create lists with required repetitions of each concept
    concept_list_a = []
    for concept in concepts_a:
        concept_list_a.extend([concept] * trials_per_concept_a)
    
    concept_list_b = []
    for concept in concepts_b:
        concept_list_b.extend([concept] * trials_per_concept_b)
    
    # Handle remainder if trials don't divide evenly
    remainder_a = trials_per_category - len(concept_list_a)
    if remainder_a > 0:
        # Distribute remainder randomly
        extra_a = np.random.choice(concepts_a, remainder_a, replace=False)
        concept_list_a.extend(extra_a)
    
    remainder_b = trials_per_category - len(concept_list_b)
    if remainder_b > 0:
        extra_b = np.random.choice(concepts_b, remainder_b, replace=False)
        concept_list_b.extend(extra_b)
    
    # Shuffle within each category
    np.random.shuffle(concept_list_a)
    np.random.shuffle(concept_list_b)
    
    # Interleave A and B (alternating)
    trials = []
    for i in range(max(len(concept_list_a), len(concept_list_b))):
        if i < len(concept_list_a):
            trials.append({
                'trial_num': len(trials) + 1,
                'concept': concept_list_a[i],
                'category': 'A'
            })
        if i < len(concept_list_b):
            trials.append({
                'trial_num': len(trials) + 1,
                'concept': concept_list_b[i],
                'category': 'B'
            })
    
    return trials


def test_randomization_protocol():
    """Test randomization protocol generation."""
    
    # Load config
    config_path = project_root / 'config' / 'experiment_config.py'
    config = load_config(str(config_path))
    
    # Test parameters
    concepts_a = config.get('CONCEPTS_CATEGORY_A', [])[:5]  # 5 items
    concepts_b = config.get('CONCEPTS_CATEGORY_B', [])[:5]  # 5 items
    n_trials_total = 100
    n_blocks = 10  # 10 blocks = 10 trials per block = 10 trials per concept-item
    trials_per_block = n_trials_total // n_blocks
    
    participant_id = 'test_001'
    session_id = 1
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    print("="*80)
    print("RANDOMIZATION PROTOCOL TEST")
    print("="*80)
    print(f"\nConfiguration:")
    print(f"  Concepts A: {concepts_a}")
    print(f"  Concepts B: {concepts_b}")
    print(f"  Total trials: {n_trials_total}")
    print(f"  Blocks: {n_blocks}")
    print(f"  Trials per block: {trials_per_block}")
    print(f"  Expected trials per concept-item: {n_trials_total // (len(concepts_a) + len(concepts_b))}")
    print(f"  Participant: {participant_id}, Session: {session_id}")
    print(f"  Timestamp: {timestamp}")
    
    # Generate all blocks
    all_blocks_trials = []
    for block_num in range(n_blocks):
        block_trials = create_stratified_block_sequence(
            n_trials_per_block=trials_per_block,
            concepts_a=concepts_a,
            concepts_b=concepts_b,
            block_num=block_num,
            participant_id=participant_id,
            session_id=session_id,
            timestamp=timestamp
        )
        all_blocks_trials.append(block_trials)
    
    # Analyze results
    print("\n" + "="*80)
    print("ANALYSIS")
    print("="*80)
    
    # Count concept occurrences across all blocks
    all_concepts = []
    for block_trials in all_blocks_trials:
        for trial in block_trials:
            all_concepts.append(trial['concept'])
    
    concept_counts = Counter(all_concepts)
    
    print(f"\nTotal trials generated: {len(all_concepts)}")
    print(f"\nConcept-item counts (should be ~10 each):")
    for concept in sorted(set(concepts_a + concepts_b)):
        count = concept_counts.get(concept, 0)
        expected = 10
        status = "OK" if count == expected else f"WARN (expected {expected})"
        print(f"  {concept:15s}: {count:3d} {status}")
    
    # Check category balance
    category_counts = Counter([t['category'] for block in all_blocks_trials for t in block])
    print(f"\nCategory balance:")
    print(f"  Category A: {category_counts.get('A', 0)}")
    print(f"  Category B: {category_counts.get('B', 0)}")
    print(f"  Balance: {'OK' if abs(category_counts.get('A', 0) - category_counts.get('B', 0)) <= 1 else 'WARN'}")
    
    # Check block uniqueness
    print(f"\nBlock uniqueness check:")
    block_patterns = []
    for block_num, block_trials in enumerate(all_blocks_trials):
        # Create pattern signature (sequence of concepts)
        pattern = tuple([t['concept'] for t in block_trials])
        block_patterns.append(pattern)
        print(f"  Block {block_num}: {len(block_trials)} trials, first 5: {pattern[:5]}")
    
    # Check if any blocks have identical patterns
    unique_patterns = len(set(block_patterns))
    print(f"\n  Unique patterns: {unique_patterns}/{n_blocks}")
    if unique_patterns == n_blocks:
        print("  OK: All blocks have unique randomization patterns")
    else:
        print("  WARN: Some blocks have identical patterns!")
        # Find duplicates
        pattern_counts = Counter(block_patterns)
        duplicates = {p: c for p, c in pattern_counts.items() if c > 1}
        if duplicates:
            print(f"  Duplicate patterns found: {len(duplicates)}")
    
    # Check stratification within each block
    print(f"\nStratification within blocks:")
    for block_num, block_trials in enumerate(all_blocks_trials):
        block_concept_counts = Counter([t['concept'] for t in block_trials])
        min_count = min(block_concept_counts.values()) if block_concept_counts else 0
        max_count = max(block_concept_counts.values()) if block_concept_counts else 0
        
        # Each concept should appear roughly equally in each block
        expected_per_block = trials_per_block // (len(concepts_a) + len(concepts_b))
        status = "OK" if abs(min_count - max_count) <= 1 else "WARN"
        print(f"  Block {block_num}: min={min_count}, max={max_count}, expected~{expected_per_block} {status}")
    
    # Show example block sequences
    print(f"\n" + "="*80)
    print("EXAMPLE BLOCK SEQUENCES (first 3 blocks)")
    print("="*80)
    for block_num in range(min(3, n_blocks)):
        print(f"\nBlock {block_num} (first 10 trials):")
        for i, trial in enumerate(all_blocks_trials[block_num][:10]):
            print(f"  Trial {i+1:2d}: {trial['concept']:15s} (Category {trial['category']})")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)


if __name__ == "__main__":
    test_randomization_protocol()
