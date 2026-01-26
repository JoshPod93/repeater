"""
Block folder management utilities.

Handles detection of existing block folders, generation of next block number,
and integration with randomization protocol.

Subject folder structure:
  data/results/sub-{participant_id}_{timestamp}/
    Block_0000/
    Block_0001/
    ...
    sub-{participant_id}_{timestamp}_randomization_protocol.json
"""

import re
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any
from datetime import datetime


def get_subject_folder(results_dir: Path, participant_id: str, timestamp: Optional[str] = None) -> Path:
    """
    Get or create subject folder with timestamp.
    
    Format: sub-{participant_id}_{timestamp}
    Example: sub-9999_20260126_160000
    
    Parameters
    ----------
    results_dir : Path
        Base results directory
    participant_id : str
        Participant identifier
    timestamp : str, optional
        Timestamp string (YYYYMMDD_HHMMSS). If None, uses current time.
        
    Returns
    -------
    Path
        Path to subject folder
    """
    if timestamp is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    folder_name = f"sub-{participant_id}_{timestamp}"
    subject_folder = results_dir / folder_name
    subject_folder.mkdir(parents=True, exist_ok=True)
    
    return subject_folder


def find_subject_folders(results_dir: Path, participant_id: str) -> List[Path]:
    """
    Find all subject folders for a participant.
    
    Parameters
    ----------
    results_dir : Path
        Base results directory
    participant_id : str
        Participant identifier
        
    Returns
    -------
    list
        List of subject folder paths, sorted by timestamp (newest first)
    """
    if not results_dir.exists():
        return []
    
    pattern = re.compile(rf'^sub-{re.escape(participant_id)}_\d{{8}}_\d{{6}}$')
    subject_folders = []
    
    for item in results_dir.iterdir():
        if item.is_dir() and pattern.match(item.name):
            subject_folders.append(item)
    
    # Sort by timestamp (extract from folder name)
    def extract_timestamp(folder_path: Path) -> str:
        parts = folder_path.name.split('_')
        if len(parts) >= 3:
            return f"{parts[1]}_{parts[2]}"  # YYYYMMDD_HHMMSS
        return ""
    
    subject_folders.sort(key=extract_timestamp, reverse=True)  # Newest first
    
    return subject_folders


def get_latest_subject_folder(results_dir: Path, participant_id: str) -> Optional[Path]:
    """
    Get the most recent subject folder for a participant.
    
    Parameters
    ----------
    results_dir : Path
        Base results directory
    participant_id : str
        Participant identifier
        
    Returns
    -------
    Path or None
        Most recent subject folder, or None if none exist
    """
    subject_folders = find_subject_folders(results_dir, participant_id)
    return subject_folders[0] if subject_folders else None


def find_block_folders(subject_folder: Path) -> List[Path]:
    """
    Find all Block_XXXX folders in subject folder.
    
    Parameters
    ----------
    subject_folder : Path
        Subject folder to search
        
    Returns
    -------
    list of Path
        List of Block_XXXX folder paths, sorted by block number
    """
    if not subject_folder.exists():
        return []
    
    block_folders = []
    pattern = re.compile(r'^Block_(\d{4})$')
    
    for item in subject_folder.iterdir():
        if item.is_dir() and pattern.match(item.name):
            block_folders.append(item)
    
    # Sort by block number
    block_folders.sort(key=lambda p: int(pattern.match(p.name).group(1)))
    
    return block_folders


def get_next_block_number(subject_folder: Path) -> int:
    """
    Determine the next block number based on existing Block_XXXX folders.
    
    If no Block_0000 exists, returns 0 (first block).
    Otherwise, finds highest numbered block and returns next number.
    
    Parameters
    ----------
    subject_folder : Path
        Subject folder to check
        
    Returns
    -------
    int
        Next block number (0-indexed: 0, 1, 2, ...)
    """
    block_folders = find_block_folders(subject_folder)
    
    if not block_folders:
        return 0  # No blocks exist, start with Block_0000
    
    # Extract block numbers and find maximum
    pattern = re.compile(r'^Block_(\d{4})$')
    block_numbers = [int(pattern.match(f.name).group(1)) for f in block_folders]
    max_block_num = max(block_numbers)
    
    return max_block_num + 1


def get_block_folder_path(subject_folder: Path, block_num: int) -> Path:
    """
    Get path for Block_XXXX folder given block number.
    
    Parameters
    ----------
    subject_folder : Path
        Subject folder
    block_num : int
        Block number (0-indexed: 0, 1, 2, ...)
        
    Returns
    -------
    Path
        Path to Block_XXXX folder
    """
    block_folder_name = f"Block_{block_num:04d}"
    return subject_folder / block_folder_name


def ensure_block_folder(subject_folder: Path, block_num: int) -> Path:
    """
    Ensure Block_XXXX folder exists, create if needed.
    
    Parameters
    ----------
    subject_folder : Path
        Subject folder
    block_num : int
        Block number (0-indexed: 0, 1, 2, ...)
        
    Returns
    -------
    Path
        Path to Block_XXXX folder (created if needed)
    """
    block_folder = get_block_folder_path(subject_folder, block_num)
    block_folder.mkdir(parents=True, exist_ok=True)
    return block_folder


def save_randomization_protocol(
    randomization_data: Dict[str, Any],
    subject_folder: Path,
    participant_id: str
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
    subject_folder : Path
        Subject folder
    participant_id : str
        Participant identifier
        
    Returns
    -------
    Path
        Path to saved randomization protocol file
    """
    import json
    from datetime import datetime
    
    # Extract timestamp from folder name or use current time
    folder_name = subject_folder.name
    if '_' in folder_name:
        parts = folder_name.split('_')
        if len(parts) >= 3:
            timestamp = f"{parts[1]}_{parts[2]}"  # YYYYMMDD_HHMMSS
        else:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    else:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Create filename (no session ID)
    filename = f"sub-{participant_id}_{timestamp}_randomization_protocol.json"
    filepath = subject_folder / filename
    
    # Add metadata
    randomization_data['saved_at'] = datetime.now().isoformat()
    randomization_data['participant_id'] = participant_id
    
    # Save to JSON
    with open(filepath, 'w') as f:
        json.dump(randomization_data, f, indent=2)
    
    return filepath


def load_randomization_protocol(
    subject_folder: Path,
    participant_id: str
) -> Optional[Dict[str, Any]]:
    """
    Load the randomization protocol from subject folder.
    
    Parameters
    ----------
    subject_folder : Path
        Subject folder
    participant_id : str
        Participant identifier
        
    Returns
    -------
    dict or None
        Randomization protocol data, or None if not found
    """
    import json
    
    # Find randomization protocol file in subject folder
    pattern = f"sub-{participant_id}_*_randomization_protocol.json"
    protocol_files = list(subject_folder.glob(pattern))
    
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
