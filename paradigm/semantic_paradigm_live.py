"""
Live variant of semantic visualization paradigm.

Runs the complete experimental protocol with live Biosemi EEG data capture.
Connects to Biosemi hardware, sends real triggers to the data stream, and enables
real-time data capture during experiments.

Author: A. Tates (JP)
BCI-NE Lab, University of Essex
Date: January 26, 2026
"""

import os
import sys
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

import numpy as np
from psychopy import core, sound, event, visual

# Add parent directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import load_config
from paradigm.utils import (
    TriggerHandler, TRIGGER_CODES, create_trigger_handler,
    get_trial_start_code, get_trial_end_code,
    get_block_start_code, get_block_end_code,
    get_beep_code, get_beep_codes,
    DisplayManager, create_window,
    create_metadata, create_trial_data_dict, save_trial_data, print_experiment_summary,
    create_balanced_sequence, validate_trial_sequence, create_stratified_block_sequence,
    create_beep_sound, play_beep,
    jittered_wait,
    get_subject_folder, find_subject_folders, get_latest_subject_folder,
    find_block_folders, get_next_block_number, get_block_folder_path, ensure_block_folder,
    save_randomization_protocol, load_randomization_protocol, get_block_trials_from_protocol,
    connect_biosemi, verify_biosemi_connection, close_biosemi_connection
)


def run_visualization_period(
    win: visual.Window,
    display: DisplayManager,
    n_beeps: int,
    beep_interval: float,
    beep_sound: sound.Sound,
    trigger_handler: TriggerHandler,
    trial_num: int,
    total_trials: int,
    block_trial_num: int = None,
    trials_per_block: int = None
) -> List[float]:
    """
    Run visualization period with beeps.
    
    Fixation cross stays on screen during beeps.
    
    Parameters
    ----------
    win : visual.Window
        PsychoPy window
    display : DisplayManager
        Display manager
    n_beeps : int
        Number of beeps
    beep_interval : float
        Time between beeps
    beep_sound : sound.Sound
        Beep sound object
    trigger_handler : TriggerHandler
        Trigger handler
    trial_num : int
        Current trial number
    total_trials : int
        Total number of trials
    
    Returns
    -------
    list
        List of beep timestamps
    """
    beep_timestamps = []
    
    # Send beep start trigger
    timestamp, _ = trigger_handler.send_trigger(
        TRIGGER_CODES['beep_start'],
        event_name='beep_start'
    )
    beep_timestamps.append(timestamp)
    
    # Visualization period with beeps (fixation stays on screen)
    # Get beep trigger codes dynamically based on n_beeps (OUR codes: 31-38)
    beep_trigger_codes = get_beep_codes(n_beeps, max_beeps=8)
    
    for beep_idx in range(n_beeps):
        # Redraw fixation (keeps it visible during beeps)
        display.show_fixation()
        
        # Use dynamic beep code (OUR codes: 31-38)
        trigger_code = beep_trigger_codes[beep_idx]
        timestamp, _ = trigger_handler.send_trigger(
            trigger_code,
            event_name=f'beep_{beep_idx + 1}_{n_beeps}'
        )
        beep_timestamps.append(timestamp)
        
        # Play beep using utility function
        play_beep(beep_sound, stop_first=True)
        
        print(f"  Beep {beep_idx + 1}/{n_beeps} (trigger {trigger_code}) at {timestamp:.3f}s")
        
        # Fixed interval - NO JITTER (critical for rhythmic protocol)
        # 0.8s interval provides sufficient buffer time between triggers
        core.wait(beep_interval)
    
    return beep_timestamps


def run_single_trial_live(
    win: visual.Window,
    display: DisplayManager,
    trial_spec: Dict[str, any],
    config: Dict[str, any],
    trigger_handler: TriggerHandler,
    beep_sound: sound.Sound,
    trial_num: int,
    total_trials: int,
    block_trial_num: int = None,
    trials_per_block: int = None
) -> Dict[str, any]:
    """
    Run a single trial with live EEG capture.
    
    Same structure as simulation but uses real triggers.
    
    Parameters
    ----------
    win : visual.Window
        PsychoPy window
    display : DisplayManager
        Display manager
    trial_spec : dict
        Trial specification
    config : dict
        Configuration dictionary
    trigger_handler : TriggerHandler
        Trigger handler
    beep_sound : sound.Sound
        Beep sound object
    trial_num : int
        Current trial number
    total_trials : int
        Total number of trials
    
    Returns
    -------
    dict
        Complete trial data with timestamps
    """
    concept = trial_spec['concept']
    category = trial_spec['category']
    case = trial_spec.get('case', 'lower')  # Get case from trial spec, default to lower
    
    # Create trial data structure (case already included in trial_spec)
    trial_data = create_trial_data_dict(trial_num, concept, category, case=case)
    
    # Determine display text based on case
    display_concept = concept.upper() if case == 'upper' else concept.lower()
    
    print(f"\nTrial {trial_num}/{total_trials}: {display_concept} (Category {category})")
    
    # Initialize jitter settings (used throughout trial)
    use_jitter = config.get('USE_JITTER', True)
    jitter_range = config.get('JITTER_RANGE', 0.1)
    
    # Send trial start trigger (unique code for this trial number)
    trial_start_code = get_trial_start_code(trial_num)
    timestamp, _ = trigger_handler.send_trigger(
        trial_start_code,
        event_name=f'trial_{trial_num}_start'
    )
    trial_data['timestamps']['trial_start'] = timestamp
    print(f"  Trial {trial_num} start (trigger {trial_start_code}) at {timestamp:.3f}s")
    
    # 1. TRIAL INDICATOR (centered text, like concept word) - FIRST ELEMENT
    display.show_trial_indicator(trial_num, total_trials)
    timestamp, _ = trigger_handler.send_trigger(
        TRIGGER_CODES['trial_indicator'],
        event_name=f'trial_indicator_{trial_num}'
    )
    trial_data['timestamps']['trial_indicator'] = timestamp
    print(f"  Trial indicator at {timestamp:.3f}s")
    trial_indicator_duration = 1.0  # Show trial indicator for 1 second
    core.wait(trial_indicator_duration)
    
    # Pause after trial indicator (JITTERED - pause event)
    display.clear_screen()
    post_indicator_pause = config.get('POST_FIXATION_PAUSE', 0.5)  # Use same pause duration
    core.wait(jittered_wait(post_indicator_pause, jitter_range) if use_jitter else post_indicator_pause)
    
    # 3. CONCEPT PRESENTATION (with case)
    display.show_concept(concept, case=case)
    
    # Send category-specific trigger (OUR codes)
    trigger_code = (TRIGGER_CODES['concept_category_a'] if category == 'A' 
                   else TRIGGER_CODES['concept_category_b'])
    event_name = f'concept_{concept}_category_{category}'
    timestamp, _ = trigger_handler.send_trigger(trigger_code, event_name=event_name)
    trial_data['timestamps']['concept'] = timestamp
    print(f"  Concept '{concept}' (Category {category}) at {timestamp:.3f}s")
    
    # NO JITTER - important timing for concept presentation
    core.wait(config.get('PROMPT_DURATION', 3.5))
    
    # Pause after concept (JITTERED - pause event)
    display.clear_screen()
    post_concept_word_pause = config.get('POST_FIXATION_PAUSE', 0.5)  # Use same pause duration
    core.wait(jittered_wait(post_concept_word_pause, jitter_range) if use_jitter else post_concept_word_pause)
    
    # 3. VISUAL MASK (after concept word)
    display.show_mask()
    timestamp, _ = trigger_handler.send_trigger(
        TRIGGER_CODES['mask'],
        event_name='mask'
    )
    trial_data['timestamps']['mask'] = timestamp
    print(f"  Mask at {timestamp:.3f}s")
    mask_duration = config.get('MASK_DURATION', 0.3)
    core.wait(mask_duration)
    
    # Pause after mask (JITTERED - pause event)
    display.clear_screen()
    post_mask_pause = config.get('POST_MASK_PAUSE', 0.5)
    core.wait(jittered_wait(post_mask_pause, jitter_range) if use_jitter else post_mask_pause)
    
    # Pause after mask (JITTERED - pause event)
    post_concept_pause = config.get('POST_CONCEPT_PAUSE', 3.0)
    core.wait(jittered_wait(post_concept_pause, jitter_range) if use_jitter else post_concept_pause)
    
    # 4. FIXATION CROSS (for beep presentation - stays on during beeps)
    display.show_fixation()
    timestamp, _ = trigger_handler.send_trigger(
        TRIGGER_CODES['fixation'],
        event_name='fixation'
    )
    trial_data['timestamps']['fixation'] = timestamp
    print(f"  Fixation at {timestamp:.3f}s")
    
    # 3. VISUALIZATION PERIOD (fixation stays on screen)
    n_beeps = config.get('N_BEEPS', 8)
    beep_interval = config.get('BEEP_INTERVAL', 0.8)
    
    beep_timestamps = run_visualization_period(
        win=win,
        display=display,
        n_beeps=n_beeps,
        beep_interval=beep_interval,
        beep_sound=beep_sound,
        trigger_handler=trigger_handler,
        trial_num=trial_num,
        total_trials=total_trials,
        block_trial_num=block_trial_num,
        trials_per_block=trials_per_block
    )
    
    trial_data['timestamps']['beep_start'] = beep_timestamps[0]
    trial_data['timestamps']['beeps'] = beep_timestamps[1:]  # Rest are beep timestamps
    
    # 4. REST PERIOD
    display.clear_screen()
    
    # Send trial end trigger (unique code for this trial number)
    trial_end_code = get_trial_end_code(trial_num)
    timestamp, _ = trigger_handler.send_trigger(
        trial_end_code,
        event_name=f'trial_{trial_num}_end'
    )
    trial_data['timestamps']['rest'] = timestamp
    print(f"  Trial {trial_num} end (trigger {trial_end_code}) at {timestamp:.3f}s")
    
    # Rest (JITTERED - pause event)
    use_jitter = config.get('USE_JITTER', True)
    jitter_range = config.get('JITTER_RANGE', 0.1)
    rest_duration = config.get('REST_DURATION', 2.0)
    core.wait(jittered_wait(rest_duration, jitter_range) if use_jitter else rest_duration)
    
    return trial_data


def run_experiment_live(
    participant_id: str,
    biosemi_port: str = None,  # Ignored - always uses COM4
    config_path: Optional[Path] = None,
    n_trials: Optional[int] = None,
    n_beeps: Optional[int] = None,
    verbose: bool = True
) -> Dict[str, any]:
    """
    Run complete experiment with live Biosemi EEG data capture.
    
    Connects to Biosemi hardware, sends real triggers, and captures live data.
    Automatically detects existing blocks and runs the next block in sequence.
    
    Parameters
    ----------
    participant_id : str
        Participant identifier
    biosemi_port : str
        Serial port for Biosemi (ignored - always uses COM4)
    config_path : Path, optional
        Path to config file
    n_trials : int, optional
        Number of trials to run (default: from config)
    n_beeps : int, optional
        Override number of beeps per trial (1-8)
    verbose : bool
        Whether to print verbose output
        
    Returns
    -------
    dict
        Experiment results dictionary
    """
    print("="*80)
    print("SEMANTIC VISUALIZATION PARADIGM - LIVE MODE")
    print("="*80)
    print(f"Participant: {participant_id}")
    print(f"Mode: LIVE (Biosemi EEG capture)")
    print("="*80)
    
    # Load configuration first (needed for BIOSEMI_PORT)
    if config_path is None:
        config_path = project_root / 'config' / 'experiment_config.py'
    config = load_config(str(config_path))
    
    # Connect to Biosemi (REQUIRED - exit if fails, per reference protocol)
    print("\n[EEG] INITIALIZING EEG TRIGGER SYSTEM")
    print("=" * 80)
    
    # Use port from config or environment variable (defaults to COM4 on Windows)
    from paradigm.utils.biosemi_utils import open_serial_port, get_default_port
    import os
    biosemi_port = os.environ.get('BIOSEMI_PORT') or config.get('BIOSEMI_PORT', get_default_port())
    print(f"Attempting to open serial port: {biosemi_port}")
    
    biosemi_conn = open_serial_port(port=biosemi_port)
    if biosemi_conn is None:
        print("[ERROR] CRITICAL ERROR: Failed to open serial port for EEG triggers!")
        print("   The experiment cannot continue without trigger capability.")
        print("   Please check:")
        print(f"   1. COM port is correct (currently using: {biosemi_port})")
        print("   2. Hardware is connected and powered on")
        print("   3. No other software is using the port")
        print("   4. Device drivers are properly installed")
        print("=" * 80)
        input("Press Enter to exit...")
        return {}
    
    if not verify_biosemi_connection(biosemi_conn):
        print("[ERROR] CRITICAL ERROR: Biosemi connection verification failed!")
        print("=" * 80)
        input("Press Enter to exit...")
        return {}
    
    print("[OK] EEG trigger system initialized successfully")
    print("=" * 80)
    
    if verbose:
        print(f"\n[CONFIG] Loaded configuration from: {config_path}")
        print(f"  Category A concepts: {config.get('CONCEPTS_CATEGORY_A', [])}")
        print(f"  Category B concepts: {config.get('CONCEPTS_CATEGORY_B', [])}")
        print(f"  Trials: {config.get('N_TRIALS', 20)}")
        print(f"  Beep interval: {config.get('BEEP_INTERVAL', 0.8)}s")
        print(f"  Number of beeps: {config.get('N_BEEPS', 8)}")
    
    # Override N_BEEPS if provided via CLI (for rapid testing)
    if n_beeps is not None:
        if n_beeps < 1 or n_beeps > 8:
            raise ValueError(f"N_BEEPS must be between 1 and 8, got {n_beeps}")
        config['N_BEEPS'] = n_beeps
        if verbose:
            print(f"\n[OVERRIDE] Using {n_beeps} beeps per trial (instead of {config.get('N_BEEPS', 8)})")
    
    # Override trial count if specified (do this BEFORE protocol generation)
    if n_trials is not None:
        config['N_TRIALS'] = n_trials
        if verbose:
            print(f"\n[OVERRIDE] Running {n_trials} trials total (instead of {config.get('N_TRIALS', 20)})")
    
    # Set up results directory and subject folder
    # Live data goes to data/results (not sim_data)
    results_dir = project_root / 'data' / 'results'
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # Get or create subject folder
    # Check if subject folder already exists (for continuing blocks)
    existing_subject_folders = find_subject_folders(results_dir, participant_id)
    
    if existing_subject_folders:
        # Use existing subject folder (most recent)
        subject_folder = existing_subject_folders[0]
        if verbose:
            print(f"\n[SUBJECT] Using existing subject folder: {subject_folder.name}")
    else:
        # Create new subject folder with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        subject_folder = get_subject_folder(results_dir, participant_id, timestamp)
        if verbose:
            print(f"\n[SUBJECT] Created new subject folder: {subject_folder.name}")
    
    # Extract timestamp from subject folder name for use in randomization
    folder_name = subject_folder.name
    timestamp_match = re.search(r'(\d{8}_\d{6})$', folder_name)
    if timestamp_match:
        timestamp = timestamp_match.group(1)
    else:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')  # Fallback
    
    # Check for existing block folders within subject folder
    existing_blocks = find_block_folders(subject_folder)
    
    # Initialize all_blocks_trials here so it's accessible later
    all_blocks_trials = []
    protocol = None
    
    if not existing_blocks:
        # No blocks exist - need to generate randomization protocol first
        print("\n[BLOCK] No existing blocks found. Generating randomization protocol...")
        
        n_blocks = config.get('N_BLOCKS', 1)
        n_trials_total = config.get('N_TRIALS', 20)  # This now includes any override
        
        # Calculate how many blocks we actually need
        # If we have fewer trials than blocks, only generate trials for the blocks we need
        blocks_to_generate = min(n_blocks, n_trials_total)
        trials_per_block = max(1, n_trials_total // blocks_to_generate) if blocks_to_generate > 0 else 1
        
        if verbose:
            print(f"[PROTOCOL] Generating protocol: {blocks_to_generate} blocks (of {n_blocks} configured), {n_trials_total} total trials, {trials_per_block} trials per block")
        
        # Generate trial sequences for blocks we need
        # Each block gets unique seed but same timestamp ensures reproducibility
        # Case and concept-item stratification happens within each block
        all_blocks_trials = []
        for b in range(blocks_to_generate):
            # For the last block, include any remainder trials
            if b == blocks_to_generate - 1:
                # Last block gets remaining trials
                remaining_trials = n_trials_total - (trials_per_block * (blocks_to_generate - 1))
                block_trial_count = max(remaining_trials, trials_per_block)
            else:
                block_trial_count = trials_per_block
            
            # create_stratified_block_sequence handles both concept-item and case stratification per block
            block_trials = create_stratified_block_sequence(
                n_trials_per_block=block_trial_count,
                concepts_a=config.get('CONCEPTS_CATEGORY_A', []),
                concepts_b=config.get('CONCEPTS_CATEGORY_B', []),
                block_num=b,
                participant_id=participant_id,
                timestamp=timestamp
            )
            
            all_blocks_trials.append(block_trials)
        
        # Pad remaining blocks with empty lists if needed
        for b in range(blocks_to_generate, n_blocks):
            all_blocks_trials.append([])
        
        # Save randomization protocol
        randomization_data = {
            'all_blocks_trials': all_blocks_trials,
            'config': {
                'N_TRIALS': n_trials_total,
                'N_BLOCKS': n_blocks,
                'TRIALS_PER_BLOCK': trials_per_block,
                'CONCEPTS_CATEGORY_A': config.get('CONCEPTS_CATEGORY_A', []),
                'CONCEPTS_CATEGORY_B': config.get('CONCEPTS_CATEGORY_B', [])
            },
            'metadata': {
                'participant_id': participant_id,
                'timestamp': timestamp
            }
        }
        
        protocol_path = save_randomization_protocol(
            randomization_data=randomization_data,
            subject_folder=subject_folder,
            participant_id=participant_id
        )
        print(f"[PROTOCOL] Randomization protocol saved: {protocol_path}")
        
        # Block number is 0 (first block, will be saved as Block_0000)
        block_num = 0
        
    else:
        # Blocks exist - load protocol and determine next block number automatically
        print(f"\n[BLOCK] Found {len(existing_blocks)} existing block(s)")
        
        # Load randomization protocol
        protocol = load_randomization_protocol(
            subject_folder=subject_folder,
            participant_id=participant_id
        )
        
        if protocol is None:
            raise RuntimeError(
                f"Found existing blocks but no randomization protocol found. "
                f"Please delete block folders or ensure protocol exists."
            )
        
        # Auto-detect: use next available block number
        next_block_num = get_next_block_number(subject_folder)
        block_num = next_block_num
        
        # Check if all blocks are complete - recommend changing participant ID
        n_blocks = protocol['config']['N_BLOCKS']
        if block_num >= n_blocks:
            print(f"\n[ERROR] All {n_blocks} blocks have been completed for participant ID '{participant_id}'.")
            print(f"[INFO] Found {len(existing_blocks)} block(s), next would be block {block_num} (exceeds configured {n_blocks} blocks)")
            print(f"\n[RECOMMENDATION] Please use a different participant ID for a new session.")
            print(f"[INFO] Example: --participant-id <new_id>")
            raise ValueError(
                f"All {n_blocks} blocks completed for participant '{participant_id}'. "
                f"Please use a different participant ID for a new session."
            )
        
        if verbose:
            print(f"[AUTO] Next block number: {block_num} (will be saved as Block_{block_num:04d})")
    
    # Convert block_num to 1-indexed for trigger codes (block_num is 0-indexed for folders)
    trigger_block_num = block_num + 1
    
    if verbose:
        print(f"\n[BLOCK] Running block {block_num} (trigger block {trigger_block_num})")
    
    # Create block folder at START of block (not at end)
    block_folder = ensure_block_folder(subject_folder, block_num)
    print(f"[BLOCK] Block folder created at start: {block_folder}")
    
    # Initialize trigger handler with CSV logging
    # Use ONE CSV file per session (reuse if exists, create if first block)
    # Extract timestamp from subject folder name for consistent filename
    folder_name = subject_folder.name
    if '_' in folder_name:
        parts = folder_name.split('_')
        if len(parts) >= 3:
            session_timestamp = f"{parts[1]}_{parts[2]}"  # YYYYMMDD_HHMMSS from folder name
        else:
            session_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    else:
        session_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    csv_log_path = subject_folder / f"sub-{participant_id}_{session_timestamp}_triggers.csv"
    
    trigger_handler = create_trigger_handler(
        port_address=config.get('PARALLEL_PORT_ADDRESS', 0x0378),
        use_triggers=True,  # Live mode - real triggers
        csv_log_path=csv_log_path,  # Enable CSV mirror logging (will append if exists)
        biosemi_connection=biosemi_conn  # Pass Biosemi connection
    )
    if biosemi_conn:
        print("\n[TRIGGER] Live mode enabled (triggers sent to Biosemi)")
    else:
        print("\n[TRIGGER] Fallback mode (triggers simulated, Biosemi not connected)")
    print(f"[TRIGGER] CSV logging enabled: {csv_log_path}")
    
    # Send Block Start trigger IMMEDIATELY after connection (same as reference project)
    # This should appear in ActiView right away
    block_start_code = get_block_start_code(trigger_block_num)
    from paradigm.utils.biosemi_utils import send_biosemi_trigger
    send_biosemi_trigger(block_start_code, f'block_{trigger_block_num}_start')
    print(f"[TRIGGER] Block {trigger_block_num} start (trigger {block_start_code}) sent immediately after connection")
    
    # Create window (fullscreen on configured monitor, e.g. second monitor)
    win = create_window(
        size=config.get('WINDOW_SIZE', (1024, 768)),
        color=config.get('BACKGROUND_COLOR', 'black'),
        fullscreen=config.get('FULLSCREEN', False),
        screen=config.get('WINDOW_SCREEN')  # e.g. 1 = second monitor
    )
    fullscreen_status = "fullscreen" if config.get('FULLSCREEN', False) else "windowed"
    screen_num = config.get('WINDOW_SCREEN')
    screen_info = f" on monitor {screen_num}" if screen_num is not None else ""
    # Report actual size (win.size is a numpy array - don't use 'or' or it raises)
    raw_size = getattr(win, 'size', None)
    actual_size = tuple(raw_size) if raw_size is not None else config.get('WINDOW_SIZE', (1024, 768))
    print(f"[DISPLAY] Window created: {actual_size} ({fullscreen_status}{screen_info})")
    
    # Create display manager
    display_config = {
        'fixation_height': config.get('FIXATION_HEIGHT', 0.1),
        'text_height': config.get('TEXT_HEIGHT', 0.08),
        'text_color': config.get('TEXT_COLOR', 'white'),
        'bold_text': config.get('BOLD_TEXT', True),
        'instruction_text': config.get('INSTRUCTION_TEXT', '')
    }
    display = DisplayManager(win, display_config)
    
    # Create clocks
    clock = core.Clock()
    experiment_clock = core.Clock()
    
    # Create audio stimulus using utility function
    beep_sound = create_beep_sound(
        frequency=config.get('BEEP_FREQUENCY', 440),
        duration=config.get('BEEP_DURATION', 0.1),
        fallback_note='A',
        octave=4
    )
    if beep_sound is not None:
        print(f"[AUDIO] Beep sound created: {config.get('BEEP_FREQUENCY', 440)} Hz")
    else:
        print("[WARNING] Could not create beep sound. Audio will be silent.")
    
    # Data storage
    trial_data_list = []
    # Get number of trials in this block for metadata
    if not existing_blocks:
        trials_per_block = len(all_blocks_trials[block_num])
    else:
        if protocol is None:
            protocol = load_randomization_protocol(
                subject_folder=subject_folder,
                participant_id=participant_id
            )
        block_trials_temp = get_block_trials_from_protocol(protocol, block_num)
        trials_per_block = len(block_trials_temp)
    
    metadata = create_metadata(participant_id, config, trials_per_block=trials_per_block)
    metadata['block_num'] = block_num  # Add block number to metadata for filename generation
    
    # Clear screen and show warning (match simulation exactly)
    display.clear_screen()
    core.wait(0.1)  # Brief pause to ensure screen is cleared
    print("\n[WARNING] Experiment starting soon...")
    warning_text = "WARNING: Experiment starting soon.\n\nPress ESCAPE to exit."
    display.show_text(warning_text, height=0.05, color='yellow')
    # Allow escape during 2s warning (poll so Esc works immediately)
    for _ in range(20):
        core.wait(0.1)
        keys = event.getKeys(keyList=['escape'])
        if 'escape' in keys:
            print("\n[EXIT] Experiment terminated by user (Escape during warning)")
            if biosemi_conn:
                close_biosemi_connection(biosemi_conn)
            win.close()
            core.quit()
            return {}
    
    # Countdown from 3
    for count in [3, 2, 1]:
        # Check for escape during countdown
        keys = event.getKeys(keyList=['escape'])
        if 'escape' in keys:
            print("\n[EXIT] Experiment terminated by user (Escape during countdown)")
            if biosemi_conn:
                close_biosemi_connection(biosemi_conn)
            win.close()
            core.quit()
            return {}
        
        # Clear screen before showing countdown
        display.clear_screen()
        core.wait(0.1)  # Brief pause to ensure screen is cleared
        display.show_text(f"Starting in {count}...", height=0.08, color='white')
        # Poll for escape during 1s countdown
        for _ in range(10):
            core.wait(0.1)
            keys = event.getKeys(keyList=['escape'])
            if 'escape' in keys:
                print("\n[EXIT] Experiment terminated by user (Escape during countdown)")
                if biosemi_conn:
                    close_biosemi_connection(biosemi_conn)
                win.close()
                core.quit()
                return {}
    
    # Clear screen before experiment starts
    display.clear_screen()
    core.wait(0.1)
    
    # Get trial sequence for this block
    if not existing_blocks:
        # First block - use trials from protocol we just generated
        trials = all_blocks_trials[block_num]
        print(f"\n[SEQUENCE] Using trials from generated protocol (block {block_num})")
    else:
        # Subsequent blocks - load from protocol
        if protocol is None:
            protocol = load_randomization_protocol(
                subject_folder=subject_folder,
                participant_id=participant_id
            )
        trials = get_block_trials_from_protocol(protocol, block_num)
        print(f"\n[SEQUENCE] Loaded trials from protocol (block {block_num})")
    
    # Validate sequence
    is_valid, error_msg = validate_trial_sequence(
        trials,
        config.get('CONCEPTS_CATEGORY_A', []),
        config.get('CONCEPTS_CATEGORY_B', [])
    )
    if not is_valid:
        print(f"[WARNING] Sequence validation: {error_msg}")
    else:
        print(f"[OK] Trial sequence validated: {len(trials)} trials")
    
    # Start experiment
    print("\n" + "="*80)
    print(f"STARTING LIVE EXPERIMENT - BLOCK {block_num} (Block_{block_num:04d})")
    print("="*80)
    
    experiment_clock.reset()
    
    # Trials are already for this block (from protocol)
    block_trials = trials
    n_trials_total = config.get('N_TRIALS', 20)  # Total across all blocks
    
    # Calculate global trial numbers (1-indexed across all blocks)
    trials_per_block = len(block_trials)
    global_trial_start = block_num * trials_per_block + 1
    
    print(f"\n[BLOCK {block_num}] Running {len(block_trials)} trials (global trials {global_trial_start}-{global_trial_start + len(block_trials) - 1})")
    
    # Block start trigger was already sent immediately after connection
    # Log it here for CSV/timing purposes (but trigger was sent earlier)
    block_start_code = get_block_start_code(trigger_block_num)
    timestamp = experiment_clock.getTime()
    # Log to CSV (trigger was already sent to Biosemi earlier)
    trigger_handler._log_trigger_to_csv(timestamp, block_start_code, f'block_{trigger_block_num}_start', True)
    print(f"[TRIGGER] Block {trigger_block_num} start (trigger {block_start_code}) logged at {timestamp:.3f}s (sent earlier)")
    
    # Wrap block execution in try/finally to ensure data is always saved
    interrupted = False
    try:
        # Run trials in this block
        # Trial numbers are global (1-indexed across all blocks)
        for trial_idx, trial_spec in enumerate(block_trials):
            # Get global trial number (1-indexed)
            global_trial_num = global_trial_start + trial_idx
            
            # Check for escape
            keys = event.getKeys(keyList=['escape'])
            if 'escape' in keys:
                print("\n[EXIT] Experiment terminated by user (Escape key)")
                interrupted = True
                break
            
            # Run trial
            # Calculate block-local trial number (1-indexed within block)
            block_trial_num = trial_idx + 1
            trials_per_block = len(block_trials)
            
            trial_data = run_single_trial_live(
                win=win,
                display=display,
                trial_spec=trial_spec,
                config=config,
                trigger_handler=trigger_handler,
                beep_sound=beep_sound,
                trial_num=global_trial_num,
                total_trials=n_trials_total,
                block_trial_num=block_trial_num,
                trials_per_block=trials_per_block
            )
            
            trial_data_list.append(trial_data)
            
            # Inter-trial interval (jittered) - only if not last trial in block
            if len(trial_data_list) < len(block_trials):
                use_jitter = config.get('USE_JITTER', True)
                jitter_range = config.get('JITTER_RANGE', 0.1)
                inter_trial_interval = config.get('INTER_TRIAL_INTERVAL', 3.0)
                wait_duration = jittered_wait(inter_trial_interval, jitter_range) if use_jitter else inter_trial_interval
                core.wait(wait_duration)
        
        # Block end (use 1-indexed for trigger codes) - only if not interrupted
        if not interrupted:
            block_end_code = get_block_end_code(trigger_block_num)
            timestamp, _ = trigger_handler.send_trigger(
                block_end_code,
                event_name=f'block_{trigger_block_num}_end'
            )
            print(f"[TRIGGER] Block {trigger_block_num} end (trigger {block_end_code}) at {timestamp:.3f}s")
        else:
            print(f"\n[WARNING] Block {block_num} was interrupted - saving partial data")
    
    except KeyboardInterrupt:
        interrupted = True
        print(f"\n[WARNING] Block {block_num} interrupted by user (Ctrl+C) - saving partial data")
    
    except Exception as e:
        interrupted = True
        print(f"\n[ERROR] Block {block_num} encountered error: {e}")
        print("[INFO] Saving partial data before exiting...")
        import traceback
        traceback.print_exc()
    
    finally:
        # ALWAYS save data, close connections, and cleanup - even if interrupted
        # Close trigger handler (saves CSV file)
        try:
            trigger_handler.close()
        except:
            pass
        
        # Save data to BLOCK FOLDER (each block contains its own data files)
        if trial_data_list:  # Only save if we have some data
            print("\n[DATA] Saving trial data...")
            print(f"[DATA] Saving to block folder: {block_folder}")
            
            try:
                saved_files = save_trial_data(
                    metadata=metadata,
                    trial_data=trial_data_list,
                    subject_folder=subject_folder,
                    participant_id=participant_id,
                    block_folder=block_folder  # Save to block folder
                )
                
                total_duration = experiment_clock.getTime()
                
                # Print summary
                print("\n" + "="*80)
                print("BLOCK SUMMARY")
                print("="*80)
                print_experiment_summary(
                    metadata=metadata,
                    trial_data=trial_data_list,
                    total_duration=total_duration,
                    saved_files=saved_files
                )
                
                if interrupted:
                    print(f"\n[INFO] Block {block_num} saved with {len(trial_data_list)}/{len(block_trials)} trials completed")
                else:
                    print(f"\n[INFO] Block {block_num} completed successfully with {len(trial_data_list)} trials")
                    
            except Exception as e:
                print(f"[ERROR] Failed to save data: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"\n[WARNING] No trial data to save for block {block_num}")
        
        # Clean up Biosemi connection
        if biosemi_conn:
            try:
                close_biosemi_connection(biosemi_conn)
                print("[BIOSEMI] Connection closed")
            except:
                pass
        
        # End screen (brief display, then auto-quit) - only if not interrupted
        if not interrupted:
            try:
                display.show_text(
                    "Block Complete!\n\nThank you for participating.",
                    height=0.06
                )
                core.wait(2.0)  # Show completion message for 2 seconds
            except:
                pass
        
        # Cleanup window
        try:
            win.close()
        except:
            pass
        
        try:
            core.quit()
        except:
            pass
    
    # Return results (saved_files may not exist if save failed)
    try:
        saved_files_var = saved_files
    except NameError:
        saved_files_var = {}
    
    try:
        total_duration_var = total_duration
    except NameError:
        total_duration_var = experiment_clock.getTime() if 'experiment_clock' in locals() else 0.0
    
    return {
        'participant_id': participant_id,
        'subject_folder': str(subject_folder),
        'block_num': block_num,
        'trials_completed': len(trial_data_list),
        'total_trials': len(block_trials),
        'total_duration': total_duration_var,
        'saved_files': saved_files_var,
        'interrupted': interrupted
    }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Run semantic visualization experiment with live Biosemi EEG capture',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run live experiment with default settings (auto-detects next block)
  python paradigm/semantic_paradigm_live.py --participant-id P001
  
  # Run with specific Biosemi port (auto-detects next block)
  python paradigm/semantic_paradigm_live.py --participant-id P001 --biosemi-port COM4
  
  # Run fewer trials for quick test (auto-detects next block)
  python paradigm/semantic_paradigm_live.py --participant-id P001 --n-trials 5
  
  # Verbose output (auto-detects next block)
  python paradigm/semantic_paradigm_live.py --participant-id P001 --verbose
        """
    )
    
    parser.add_argument(
        '--participant-id', '-p',
        type=str,
        required=True,
        help='Participant identifier (required)'
    )
    
    parser.add_argument(
        '--biosemi-port',
        type=str,
        default='COM3',
        help='Serial port for Biosemi (default: COM3)'
    )
    
    parser.add_argument(
        '--n-trials', '-n',
        type=int,
        default=None,
        help='Number of trials to run (default: from config)'
    )
    
    parser.add_argument(
        '--n-beeps', '--beeps',
        type=int,
        default=None,
        help='Number of beeps per trial (default: from config, max: 8). Useful for rapid testing (e.g., --n-beeps 3)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    try:
        results = run_experiment_live(
            participant_id=args.participant_id,
            biosemi_port=args.biosemi_port,
            config_path=None,  # Always use default config path
            n_trials=args.n_trials,
            n_beeps=args.n_beeps,
            verbose=args.verbose
        )
        
        if results:
            print("\n[OK] Experiment completed successfully!")
            print("\n[VERIFICATION] Check the following:")
            print(f"  1. Data files: {results.get('saved_files', {})}")
            print(f"  2. Trials completed: {results.get('trials_completed', 0)}")
            print(f"  3. Total duration: {results.get('total_duration', 0):.2f}s")
        else:
            print("\n[WARNING] Experiment completed with warnings")
            
    except KeyboardInterrupt:
        print("\n\n[WARNING] Experiment interrupted by user (Ctrl+C)")
    except Exception as e:
        print(f"\n[ERROR] Error during experiment: {e}")
        import traceback
        traceback.print_exc()
