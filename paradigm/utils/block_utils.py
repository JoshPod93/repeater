"""
Block folder management utilities.

Handles detection of existing block folders, generation of next block number,
and integration with randomization protocol.
"""

import re
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any


def find_block_folders(results_dir: Path) -> List[Path]:
    """
    Find all Block_XXXX folders in results directory.
    
    Parameters
    ----------
    results_dir : Path
        Results directory to search
        
    Returns
    -------
    list of Path
        List of Block_XXXX folder paths, sorted by block number
    """
    if not results_dir.exists():
        return []
    
    block_folders = []
    pattern = re.compile(r'^Block_(\d{4})$')
    
    for item in results_dir.iterdir():
        if item.is_dir() and pattern.match(item.name):
            block_folders.append(item)
    
    # Sort by block number
    block_folders.sort(key=lambda p: int(pattern.match(p.name).group(1)))
    
    return block_folders


def get_next_block_number(results_dir: Path) -> int:
    """
    Determine the next block number based on existing Block_XXXX folders.
    
    If no Block_0000 exists, returns 0 (first block).
    Otherwise, finds highest numbered block and returns next number.
    
    Parameters
    ----------
    results_dir : Path
        Results directory to check
        
    Returns
    -------
    int
        Next block number (0-indexed: 0, 1, 2, ...)
    """
    block_folders = find_block_folders(results_dir)
    
    if not block_folders:
        return 0  # No blocks exist, start with Block_0000
    
    # Extract block numbers and find maximum
    pattern = re.compile(r'^Block_(\d{4})$')
    block_numbers = [int(pattern.match(f.name).group(1)) for f in block_folders]
    max_block_num = max(block_numbers)
    
    return max_block_num + 1


def get_block_folder_path(results_dir: Path, block_num: int) -> Path:
    """
    Get path for Block_XXXX folder given block number.
    
    Parameters
    ----------
    results_dir : Path
        Results directory
    block_num : int
        Block number (0-indexed: 0, 1, 2, ...)
        
    Returns
    -------
    Path
        Path to Block_XXXX folder
    """
    block_folder_name = f"Block_{block_num:04d}"
    return results_dir / block_folder_name


def ensure_block_folder(results_dir: Path, block_num: int) -> Path:
    """
    Ensure Block_XXXX folder exists, create if needed.
    
    Parameters
    ----------
    results_dir : Path
        Results directory
    block_num : int
        Block number (0-indexed: 0, 1, 2, ...)
        
    Returns
    -------
    Path
        Path to Block_XXXX folder (created if needed)
    """
    block_folder = get_block_folder_path(results_dir, block_num)
    block_folder.mkdir(parents=True, exist_ok=True)
    return block_folder


def save_randomization_protocol(
    randomization_data: Dict[str, Any],
    output_dir: Path,
    participant_id: str,
    session_id: int
) -> Path:
    """
    Save randomization protocol (cross-block instructions/programs, clue patterns).
    
    This is saved once before any blocks are run, and contains the trial sequences
    for all blocks.
    
    Parameters
    ----------
    randomization_data : dict
        Dictionary containing:
        - 'all_blocks_trials': List of trial sequences (one per block)
        - 'config': Configuration used
        - 'metadata': Additional metadata
    output_dir : Path
        Output directory (results folder)
    participant_id : str
        Participant identifier
    session_id : int
        Session number
        
    Returns
    -------
    Path
        Path to saved randomization protocol file
    """
    import json
    from datetime import datetime
    
    # Create filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"sub-{participant_id}_ses-{session_id}_{timestamp}_randomization_protocol.json"
    filepath = output_dir / filename
    
    # Add metadata
    randomization_data['saved_at'] = datetime.now().isoformat()
    randomization_data['participant_id'] = participant_id
    randomization_data['session_id'] = session_id
    
    # Save to JSON
    with open(filepath, 'w') as f:
        json.dump(randomization_data, f, indent=2)
    
    return filepath


def load_randomization_protocol(
    output_dir: Path,
    participant_id: str,
    session_id: int
) -> Optional[Dict[str, Any]]:
    """
    Load the most recent randomization protocol for a participant/session.
    
    Parameters
    ----------
    output_dir : Path
        Results directory
    participant_id : str
        Participant identifier
    session_id : int
        Session number
        
    Returns
    -------
    dict or None
        Randomization protocol data, or None if not found
    """
    import json
    
    # Find all randomization protocol files for this participant/session
    pattern = f"sub-{participant_id}_ses-{session_id}_*_randomization_protocol.json"
    protocol_files = list(output_dir.glob(pattern))
    
    if not protocol_files:
        return None
    
    # Get most recent
    protocol_file = max(protocol_files, key=lambda p: p.stat().st_mtime)
    
    # Load JSON
    with open(protocol_file, 'r') as f:
        return json.load(f)


def get_block_trials_from_protocol(
    protocol: Dict[str, Any],
    block_num: int
) -> List[Dict[str, Any]]:
    """
    Extract trials for a specific block from randomization protocol.
    
    Parameters
    ----------
    protocol : dict
        Randomization protocol data (from load_randomization_protocol)
    block_num : int
        Block number (0-indexed: 0, 1, 2, ...)
        
    Returns
    -------
    list
        Trial sequence for the specified block
    """
    all_blocks_trials = protocol.get('all_blocks_trials', [])
    
    if block_num < 0 or block_num >= len(all_blocks_trials):
        raise ValueError(f"Block {block_num} not found in protocol (available: 0-{len(all_blocks_trials)-1})")
    
    return all_blocks_trials[block_num]
