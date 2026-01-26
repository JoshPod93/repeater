"""
Randomization utilities for creating balanced trial sequences.

Handles trial sequence generation with proper balancing and randomization.
"""

import numpy as np
from typing import List, Dict, Tuple, Optional


def create_balanced_sequence(n_trials: int,
                            concepts_a: List[str],
                            concepts_b: List[str],
                            randomize: bool = True,
                            seed: Optional[int] = None) -> List[Dict[str, any]]:
    """
    Create balanced trial sequence alternating between categories.
    
    Parameters
    ----------
    n_trials : int
        Total number of trials
    concepts_a : list
        Concepts from category A
    concepts_b : list
        Concepts from category B
    randomize : bool
        Whether to randomize concept selection within categories
    seed : int, optional
        Random seed for reproducibility
    
    Returns
    -------
    list
        List of trial dictionaries with 'trial_num', 'concept', 'category'
    """
    if seed is not None:
        np.random.seed(seed)
    
    trials = []
    
    for trial_idx in range(n_trials):
        # Alternate between categories
        if trial_idx % 2 == 0:
            category = 'A'
            concepts = concepts_a
        else:
            category = 'B'
            concepts = concepts_b
        
        # Select concept
        if randomize:
            concept = np.random.choice(concepts)
        else:
            # Sequential selection
            concept_idx = (trial_idx // 2) % len(concepts)
            concept = concepts[concept_idx]
        
        trials.append({
            'trial_num': trial_idx + 1,
            'concept': concept,
            'category': category
        })
    
    return trials


def create_date_seeded_sequence(n_trials: int,
                                concepts_a: List[str],
                                concepts_b: List[str],
                                participant_id: str,
                                randomize: bool = True) -> List[Dict[str, any]]:
    """
    Create trial sequence with date/time-based seed for unique sequences per participant.
    
    Uses participant ID and current date/time to create unique but reproducible sequences.
    
    Parameters
    ----------
    n_trials : int
        Total number of trials
    concepts_a : list
        Concepts from category A
    concepts_b : list
        Concepts from category B
    participant_id : str
        Participant identifier (used in seed)
    randomize : bool
        Whether to randomize concept selection
    
    Returns
    -------
    list
        List of trial dictionaries
    """
    from datetime import datetime
    
    # Create seed from participant ID and date
    date_str = datetime.now().strftime('%Y%m%d')
    seed_str = f"{participant_id}{date_str}"
    seed = hash(seed_str) % (2**31)  # Convert to 32-bit integer
    
    return create_balanced_sequence(
        n_trials=n_trials,
        concepts_a=concepts_a,
        concepts_b=concepts_b,
        randomize=randomize,
        seed=seed
    )


def validate_trial_sequence(trials: List[Dict[str, any]],
                           concepts_a: List[str],
                           concepts_b: List[str]) -> Tuple[bool, str]:
    """
    Validate trial sequence for proper balancing.
    
    Parameters
    ----------
    trials : list
        List of trial dictionaries
    concepts_a : list
        Expected category A concepts
    concepts_b : list
        Expected category B concepts
    
    Returns
    -------
    tuple
        (is_valid, error_message)
    """
    if not trials:
        return False, "Empty trial sequence"
    
    # Count categories
    count_a = sum(1 for t in trials if t['category'] == 'A')
    count_b = sum(1 for t in trials if t['category'] == 'B')
    
    # Check balance (should be equal or differ by 1)
    if abs(count_a - count_b) > 1:
        return False, f"Unbalanced categories: A={count_a}, B={count_b}"
    
    # Check all concepts are valid
    for trial in trials:
        if trial['category'] == 'A':
            if trial['concept'] not in concepts_a:
                return False, f"Invalid concept '{trial['concept']}' in category A"
        else:
            if trial['concept'] not in concepts_b:
                return False, f"Invalid concept '{trial['concept']}' in category B"
    
    return True, ""


def create_stratified_block_sequence(
    n_trials_per_block: int,
    concepts_a: List[str],
    concepts_b: List[str],
    block_num: int,
    participant_id: str,
    session_id: int,
    timestamp: str
) -> List[Dict[str, any]]:
    """
    Create stratified trial sequence for a block.
    
    Ensures equal representation of each concept-item within the block.
    Uses date-time + block number + participant for unique seed per block.
    This ensures each block has a unique randomization pattern.
    
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
        Timestamp string for seed generation (format: YYYYMMDD_HHMMSS)
        
    Returns
    -------
    list
        Stratified trial sequence for this block
    """
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


def shuffle_trials(trials: List[Dict[str, any]],
                  preserve_balance: bool = True,
                  seed: Optional[int] = None) -> List[Dict[str, any]]:
    """
    Shuffle trial sequence while optionally preserving category balance.
    
    Parameters
    ----------
    trials : list
        List of trial dictionaries
    preserve_balance : bool
        If True, maintains alternating A/B pattern
    seed : int, optional
        Random seed
    
    Returns
    -------
    list
        Shuffled trial sequence
    """
    if seed is not None:
        np.random.seed(seed)
    
    if preserve_balance:
        # Shuffle within each category separately
        trials_a = [t for t in trials if t['category'] == 'A']
        trials_b = [t for t in trials if t['category'] == 'B']
        
        np.random.shuffle(trials_a)
        np.random.shuffle(trials_b)
        
        # Interleave
        shuffled = []
        for i in range(max(len(trials_a), len(trials_b))):
            if i < len(trials_a):
                shuffled.append(trials_a[i])
            if i < len(trials_b):
                shuffled.append(trials_b[i])
        
        return shuffled
    else:
        # Complete shuffle
        shuffled = trials.copy()
        np.random.shuffle(shuffled)
        return shuffled
