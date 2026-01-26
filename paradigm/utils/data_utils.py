"""
Data utilities for logging and saving experimental data.

Handles data collection, formatting, and saving in standardized formats (JSON + NumPy).
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional


def create_metadata(participant_id: str,
                   config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create metadata dictionary for experiment.
    
    Parameters
    ----------
    participant_id : str
        Participant identifier
    config : dict
        Configuration dictionary
        
    Returns
    -------
    dict
        Metadata dictionary
    """
    return {
        'participant_id': participant_id,
        'date': datetime.now().strftime('%Y-%m-%d'),
        'time': datetime.now().strftime('%H:%M:%S'),
        'concepts_category_a': config.get('concepts_category_a', []),
        'concepts_category_b': config.get('concepts_category_b', []),
        'n_trials': config.get('n_trials', 20),
        'timing': {
            'fixation': config.get('fixation_duration', 2.0),
            'prompt': config.get('prompt_duration', 2.0),
            'beep_interval': config.get('beep_interval', 0.8),
            'n_beeps': config.get('n_beeps', 8),
            'rest': config.get('rest_duration', 1.0)
        }
    }


def create_trial_data_dict(trial_num: int,
                          concept: str,
                          category: str) -> Dict[str, Any]:
    """
    Create trial data dictionary structure.
    
    Parameters
    ----------
    trial_num : int
        Trial number
    concept : str
        Concept word
    category : str
        Category label ('A' or 'B')
    
    Returns
    -------
    dict
        Trial data dictionary
    """
    return {
        'trial_num': trial_num,
        'concept': concept,
        'category': category,
        'timestamps': {}
    }


def save_trial_data(metadata: Dict[str, Any],
                   trial_data: List[Dict[str, Any]],
                   subject_folder: Path,
                   participant_id: str,
                   block_folder: Optional[Path] = None,
                   save_json: bool = True,
                   save_numpy: bool = True) -> Dict[str, Path]:
    """
    Save trial data to files.
    
    Saves data in both JSON (human-readable) and NumPy (analysis-friendly) formats.
    If block_folder is provided, saves to that folder. Otherwise saves to subject_folder.
    
    Parameters
    ----------
    metadata : dict
        Experiment metadata
    trial_data : list
        List of trial data dictionaries
    subject_folder : Path
        Subject folder (e.g., sub-9999_20260126_160000)
    participant_id : str
        Participant identifier
    block_folder : Path, optional
        Block folder path (e.g., Block_0000). If None, saves directly to subject_folder
    save_json : bool
        Whether to save JSON file
    save_numpy : bool
        Whether to save NumPy file
        
    Returns
    -------
    dict
        Dictionary with paths to saved files ('json' and/or 'numpy')
    """
    # Use block_folder if provided, otherwise use subject_folder
    save_dir = block_folder if block_folder else subject_folder
    save_dir.mkdir(parents=True, exist_ok=True)
    
    # Extract timestamp from subject folder name
    folder_name = subject_folder.name
    if '_' in folder_name:
        parts = folder_name.split('_')
        if len(parts) >= 3:
            timestamp = f"{parts[1]}_{parts[2]}"  # YYYYMMDD_HHMMSS
        else:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    else:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Generate filename (no session ID)
    base_filename = f"sub-{participant_id}_{timestamp}"
    
    saved_files = {}
    
    # Save JSON file
    if save_json:
        json_file = save_dir / f"{base_filename}_trials.json"
        with open(json_file, 'w') as f:
            json.dump({
                'metadata': metadata,
                'trials': trial_data
            }, f, indent=2)
        saved_files['json'] = json_file
    
    # Save NumPy file
    if save_numpy:
        np_file = save_dir / f"{base_filename}_trials.npy"
        np.save(np_file, trial_data, allow_pickle=True)
        saved_files['numpy'] = np_file
    
    return saved_files


def load_trial_data(file_path: Path, format: str = 'auto') -> Dict[str, Any]:
    """
    Load trial data from file.
    
    Parameters
    ----------
    file_path : Path
        Path to data file
    format : str
        File format ('json', 'numpy', or 'auto' to detect)
    
    Returns
    -------
    dict
        Loaded data with 'metadata' and 'trials' keys
    """
    if format == 'auto':
        if file_path.suffix == '.json':
            format = 'json'
        elif file_path.suffix == '.npy':
            format = 'numpy'
        else:
            raise ValueError(f"Unknown file format: {file_path.suffix}")
    
    if format == 'json':
        with open(file_path, 'r') as f:
            return json.load(f)
    elif format == 'numpy':
        data = np.load(file_path, allow_pickle=True)
        # NumPy files saved as list of dicts, need to reconstruct
        return {
            'metadata': {},
            'trials': data.tolist()
        }
    else:
        raise ValueError(f"Unsupported format: {format}")


def print_experiment_summary(metadata: Dict[str, Any],
                            trial_data: List[Dict[str, Any]],
                            total_duration: float,
                            saved_files: Optional[Dict[str, Path]] = None):
    """
    Print experiment summary to console.
    
    Parameters
    ----------
    metadata : dict
        Experiment metadata
    trial_data : list
        Trial data list
    total_duration : float
        Total experiment duration in seconds
    saved_files : dict, optional
        Dictionary of saved file paths
    """
    print("\n" + "="*60)
    print("EXPERIMENT SUMMARY")
    print("="*60)
    print(f"Participant: {metadata['participant_id']}")
    print(f"Total duration: {total_duration:.2f}s ({total_duration/60:.2f}min)")
    print(f"Trials completed: {len(trial_data)}/{metadata.get('n_trials', len(trial_data))}")
    
    if saved_files:
        print("\nData saved to:")
        for file_type, file_path in saved_files.items():
            print(f"  {file_type.upper()}: {file_path}")
