"""
Simulation variant of semantic visualization paradigm.

Runs through the entire experimental protocol using simulated visualization periods.
Tests everything: folder structures, autosaving, trigger logging, display behavior,
and all functionality without requiring EEG hardware or participant.

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
    save_randomization_protocol, load_randomization_protocol, get_block_trials_from_protocol
)


def simulate_visualization_period(
    win: visual.Window,
    display: DisplayManager,
    n_beeps: int,
    beep_interval: float,
    beep_sound: sound.Sound,
    trigger_handler: TriggerHandler,
    trial_num: int,
    total_trials: int
) -> List[float]:
    """
    Simulate visualization period with beeps.
    
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
    # Get beep trigger codes dynamically based on n_beeps
    beep_trigger_codes = get_beep_codes(n_beeps, max_beeps=8)
    
    for beep_idx in range(n_beeps):
        # Redraw fixation (keeps it visible during beeps)
        display.show_fixation()
        
        # Use dynamic beep code
        trigger_code = beep_trigger_codes[beep_idx]
        timestamp, _ = trigger_handler.send_trigger(
            trigger_code,
            event_name=f'beep_{beep_idx + 1}_{n_beeps}'
        )
        beep_timestamps.append(timestamp)
        
        # Play beep using utility function
        play_beep(beep_sound, stop_first=True)
        
        print(f"  [SIM] Beep {beep_idx + 1}/{n_beeps} (trigger {trigger_code}) at {timestamp:.3f}s")
        
        # Fixed interval - NO JITTER (critical for rhythmic protocol)
        # 0.8s interval provides sufficient buffer time between triggers
        core.wait(beep_interval)
    
    return beep_timestamps


def run_single_trial_simulation(
    win: visual.Window,
    display: DisplayManager,
    trial_spec: Dict[str, any],
    config: Dict[str, any],
    trigger_handler: TriggerHandler,
    beep_sound: sound.Sound,
    trial_num: int,
    total_trials: int
) -> Dict[str, any]:
    """
    Run a single trial with simulation.
    
    Same structure as real trial but uses simulated visualization period.
    
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
    
    # Create trial data structure
    trial_data = create_trial_data_dict(trial_num, concept, category, case=case)
    
    # Determine display text based on case
    display_concept = concept.upper() if case == 'upper' else concept.lower()
    print(f"\n[SIM] Trial {trial_num}/{total_trials}: {display_concept} (Category {category})")
    
    # Send trial start trigger (unique code for this trial number)
    trial_start_code = get_trial_start_code(trial_num)
    timestamp, _ = trigger_handler.send_trigger(
        trial_start_code,
        event_name=f'trial_{trial_num}_start'
    )
    trial_data['timestamps']['trial_start'] = timestamp
    print(f"  [SIM] Trial {trial_num} start (trigger {trial_start_code}) at {timestamp:.3f}s")
    
    # Initialize jitter settings (used throughout trial)
    use_jitter = config.get('USE_JITTER', True)
    jitter_range = config.get('JITTER_RANGE', 0.1)
    
    # 1. TRIAL INDICATOR (centered text, like concept word) - FIRST ELEMENT
    display.show_trial_indicator(trial_num, total_trials)
    timestamp, _ = trigger_handler.send_trigger(
        TRIGGER_CODES['trial_indicator'],
        event_name=f'trial_indicator_{trial_num}'
    )
    trial_data['timestamps']['trial_indicator'] = timestamp
    print(f"  [SIM] Trial indicator at {timestamp:.3f}s")
    trial_indicator_duration = 1.0  # Show trial indicator for 1 second
    core.wait(trial_indicator_duration)
    
    # Pause after trial indicator (JITTERED - pause event)
    display.clear_screen()
    post_indicator_pause = config.get('POST_FIXATION_PAUSE', 0.5)  # Use same pause duration
    core.wait(jittered_wait(post_indicator_pause, jitter_range) if use_jitter else post_indicator_pause)
    
    # 2. CONCEPT PRESENTATION (with case)
    display.show_concept(concept, case=case)
    
    # Send category-specific trigger
    trigger_code = (TRIGGER_CODES['concept_category_a'] if category == 'A' 
                   else TRIGGER_CODES['concept_category_b'])
    event_name = f'concept_{concept}_category_{category}'
    timestamp, _ = trigger_handler.send_trigger(trigger_code, event_name=event_name)
    trial_data['timestamps']['concept'] = timestamp
    print(f"  [SIM] Concept '{concept}' (Category {category}) at {timestamp:.3f}s")
    
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
    print(f"  [SIM] Mask at {timestamp:.3f}s")
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
    print(f"  [SIM] Fixation at {timestamp:.3f}s")
    
    # 3. SIMULATED VISUALIZATION PERIOD (fixation stays on screen)
    n_beeps = config.get('N_BEEPS', 8)
    beep_interval = config.get('BEEP_INTERVAL', 0.8)
    
    beep_timestamps = simulate_visualization_period(
        win=win,
        display=display,
        n_beeps=n_beeps,
        beep_interval=beep_interval,
        beep_sound=beep_sound,
        trigger_handler=trigger_handler,
        trial_num=trial_num,
        total_trials=total_trials
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
    print(f"  [SIM] Trial {trial_num} end (trigger {trial_end_code}) at {timestamp:.3f}s")
    
    # Rest (JITTERED - pause event)
    use_jitter = config.get('USE_JITTER', True)
    jitter_range = config.get('JITTER_RANGE', 0.1)
    rest_duration = config.get('REST_DURATION', 2.0)
    core.wait(jittered_wait(rest_duration, jitter_range) if use_jitter else rest_duration)
    
    return trial_data


def run_experiment_simulation(
    participant_id: str = 'sim_9999',
    config_path: Optional[Path] = None,
    n_trials: Optional[int] = None,
    n_beeps: Optional[int] = None,
    verbose: bool = True
) -> Dict[str, any]:
    """
    Run complete experiment simulation.
    
    Tests all functionality without requiring EEG hardware or participant.
    Automatically detects existing blocks and runs the next block in sequence.
    
    Parameters
    ----------
    participant_id : str
        Participant identifier (default: sim_9999 for simulation)
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
    print("SEMANTIC VISUALIZATION PARADIGM - SIMULATION MODE")
    print("="*80)
    print(f"Participant: {participant_id}")
    print(f"Mode: SIMULATION (no EEG hardware required)")
    print("="*80)
    
    # Load configuration
    if config_path is None:
        config_path = project_root / 'config' / 'experiment_config.py'
    config = load_config(str(config_path))
    
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
    # Simulation data goes to sim_data/sim_results to keep it separate from real experiment data
    results_dir = project_root / 'sim_data' / 'sim_results'
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
        all_blocks_trials = []
        for b in range(blocks_to_generate):
            # For the last block, include any remainder trials
            if b == blocks_to_generate - 1:
                # Last block gets remaining trials
                remaining_trials = n_trials_total - (trials_per_block * (blocks_to_generate - 1))
                block_trial_count = max(remaining_trials, trials_per_block)
            else:
                block_trial_count = trials_per_block
            
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
        
        if verbose:
            n_blocks = protocol['config']['N_BLOCKS']
            print(f"[AUTO] Next block number: {block_num} (will be saved as Block_{block_num:04d})")
            if block_num >= n_blocks:
                print(f"[WARNING] Block {block_num} exceeds configured {n_blocks} blocks")
                print(f"[INFO] All {n_blocks} blocks completed for this participant.")
                return {}
    
    # Convert block_num to 1-indexed for trigger codes (block_num is 0-indexed for folders)
    trigger_block_num = block_num + 1
    
    if verbose:
        print(f"\n[BLOCK] Running block {block_num} (trigger block {trigger_block_num})")
    
    # Initialize trigger handler (test mode - no hardware) with CSV logging
    # Save trigger CSV in subject folder (same organization as results)
    csv_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_log_path = subject_folder / f"sub-{participant_id}_{csv_timestamp}_triggers.csv"
    
    trigger_handler = create_trigger_handler(
        port_address=config.get('PARALLEL_PORT_ADDRESS', 0x0378),
        use_triggers=False,  # Simulation mode - no actual triggers
        csv_log_path=csv_log_path  # Enable CSV mirror logging
    )
    print("\n[TRIGGER] Test mode enabled (triggers simulated, not sent)")
    print(f"[TRIGGER] CSV logging enabled: {csv_log_path}")
    
    # Create window (non-fullscreen for simulation)
    win = create_window(
        size=config.get('WINDOW_SIZE', (1024, 768)),
        color=config.get('BACKGROUND_COLOR', 'black'),
        fullscreen=False  # Always windowed for simulation
    )
    print(f"[DISPLAY] Window created: {config.get('WINDOW_SIZE', (1024, 768))} (windowed)")
    
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
    
    # Clear screen and show warning
    display.clear_screen()
    core.wait(0.1)  # Brief pause to ensure screen is cleared
    print("\n[WARNING] Simulation starting soon...")
    warning_text = "WARNING: Simulation starting soon.\n\nPress ESCAPE to exit."
    display.show_text(warning_text, height=0.05, color='yellow')
    core.wait(2.0)  # Show warning for 2 seconds
    
    # Countdown from 3
    for count in [3, 2, 1]:
        # Check for escape during countdown
        keys = event.getKeys(keyList=['escape'])
        if 'escape' in keys:
            print("\n[EXIT] Simulation terminated by user")
            win.close()
            core.quit()
            return {}
        
        # Clear screen before showing countdown
        display.clear_screen()
        core.wait(0.1)  # Brief pause to ensure screen is cleared
        display.show_text(f"Starting in {count}...", height=0.08, color='white')
        core.wait(1.0)
    
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
    print(f"STARTING SIMULATION EXPERIMENT - BLOCK {block_num} (Block_{block_num:04d})")
    print("="*80)
    
    experiment_clock.reset()
    
    # Trials are already for this block (from protocol)
    block_trials = trials
    n_trials_total = config.get('N_TRIALS', 20)  # Total across all blocks
    
    # Calculate global trial numbers (1-indexed across all blocks)
    trials_per_block = len(block_trials)
    global_trial_start = block_num * trials_per_block + 1
    
    print(f"\n[BLOCK {block_num}] Running {len(block_trials)} trials (global trials {global_trial_start}-{global_trial_start + len(block_trials) - 1})")
    
    # Block start (use 1-indexed for trigger codes)
    block_start_code = get_block_start_code(trigger_block_num)
    timestamp, _ = trigger_handler.send_trigger(
        block_start_code,
        event_name=f'block_{trigger_block_num}_start'
    )
    print(f"[TRIGGER] Block {trigger_block_num} start (trigger {block_start_code}) at {timestamp:.3f}s")
    
    # Run trials in this block
    # Trial numbers are global (1-indexed across all blocks)
    for trial_idx, trial_spec in enumerate(block_trials):
        # Get global trial number (1-indexed)
        global_trial_num = global_trial_start + trial_idx
        
        # Check for escape
        keys = event.getKeys(keyList=['escape'])
        if 'escape' in keys:
            print("\n[EXIT] Simulation terminated by user (Escape key)")
            break
        
        # Run trial
        trial_data = run_single_trial_simulation(
            win=win,
            display=display,
            trial_spec=trial_spec,
            config=config,
            trigger_handler=trigger_handler,
            beep_sound=beep_sound,
            trial_num=global_trial_num,
            total_trials=n_trials_total
        )
        
        trial_data_list.append(trial_data)
        
        # Inter-trial interval (jittered) - only if not last trial in block
        if len(trial_data_list) < len(block_trials):
            use_jitter = config.get('USE_JITTER', True)
            jitter_range = config.get('JITTER_RANGE', 0.1)
            inter_trial_interval = config.get('INTER_TRIAL_INTERVAL', 3.0)
            wait_duration = jittered_wait(inter_trial_interval, jitter_range) if use_jitter else inter_trial_interval
            core.wait(wait_duration)
    
    # Block end (use 1-indexed for trigger codes)
    block_end_code = get_block_end_code(trigger_block_num)
    timestamp, _ = trigger_handler.send_trigger(
        block_end_code,
        event_name=f'block_{trigger_block_num}_end'
    )
    print(f"[TRIGGER] Block {trigger_block_num} end (trigger {block_end_code}) at {timestamp:.3f}s")
    
    # Close trigger handler (saves CSV file)
    trigger_handler.close()
    
    # Save data to block folder
    print("\n[DATA] Saving trial data...")
    block_folder = ensure_block_folder(subject_folder, block_num)
    print(f"[BLOCK] Saving to: {block_folder}")
    
    saved_files = save_trial_data(
        metadata=metadata,
        trial_data=trial_data_list,
        subject_folder=subject_folder,
        participant_id=participant_id,
        block_folder=block_folder
    )
    
    total_duration = experiment_clock.getTime()
    
    # End screen (brief display, then auto-quit)
    display.show_text(
        "Simulation Complete!\n\nAll functionality tested.",
        height=0.06
    )
    core.wait(2.0)  # Show completion message for 2 seconds
    
    # Print summary
    print("\n" + "="*80)
    print("SIMULATION SUMMARY")
    print("="*80)
    print_experiment_summary(
        metadata=metadata,
        trial_data=trial_data_list,
        total_duration=total_duration,
        saved_files=saved_files
    )
    
    # Verification checklist
    print("\n" + "="*80)
    print("VERIFICATION CHECKLIST")
    print("="*80)
    print("[ ] All triggers logged correctly")
    print("[ ] Display stimuli shown correctly")
    print("[ ] Beeps played at correct intervals")
    print("[ ] Data saved to files")
    print("[ ] Timestamps recorded accurately")
    print(f"\nCheck saved files:")
    for file_type, file_path in saved_files.items():
        print(f"  {file_type.upper()}: {file_path}")
    print("="*80)
    
    # Cleanup
    trigger_handler.close()
    win.close()
    core.quit()
    
    return {
        'participant_id': participant_id,
        'subject_folder': str(subject_folder),
        'block_num': block_num,
        'trials_completed': len(trial_data_list),
        'total_duration': total_duration,
        'saved_files': saved_files,
        'trial_data': trial_data_list
    }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Run semantic visualization experiment simulation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run simulation with default settings (auto-detects next block)
  python paradigm/semantic_paradigm_simulation.py
  
  # Run with specific participant ID (auto-detects next block)
  python paradigm/semantic_paradigm_simulation.py --participant-id 9999
  
  # Run fewer trials for quick test (auto-detects next block)
  python paradigm/semantic_paradigm_simulation.py --n-trials 5
  
  # Verbose output (auto-detects next block)
  python paradigm/semantic_paradigm_simulation.py --verbose
        """
    )
    
    parser.add_argument(
        '--participant-id', '-p',
        type=str,
        default='sim_9999',
        help='Participant identifier (default: sim_9999 for simulation)'
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
        results = run_experiment_simulation(
            participant_id=args.participant_id,
            config_path=None,  # Always use default config path
            n_trials=args.n_trials,
            n_beeps=args.n_beeps,
            verbose=args.verbose
        )
        
        if results:
            print("\n[OK] Simulation completed successfully!")
            print("\n[VERIFICATION] Check the following:")
            print(f"  1. Data files: {results.get('saved_files', {})}")
            print(f"  2. Trials completed: {results.get('trials_completed', 0)}")
            print(f"  3. Total duration: {results.get('total_duration', 0):.2f}s")
        else:
            print("\n[WARNING] Simulation completed with warnings")
            
    except KeyboardInterrupt:
        print("\n\n[WARNING] Simulation interrupted by user (Ctrl+C)")
    except Exception as e:
        print(f"\n[ERROR] Error during simulation: {e}")
        import traceback
        traceback.print_exc()
