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
    DisplayManager, create_window,
    create_metadata, create_trial_data_dict, save_trial_data, print_experiment_summary,
    create_balanced_sequence, validate_trial_sequence,
    create_beep_sound, play_beep,
    jittered_wait
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
    # Use unique trigger codes for each beep (31-38)
    beep_trigger_codes = [
        TRIGGER_CODES['beep_1'],
        TRIGGER_CODES['beep_2'],
        TRIGGER_CODES['beep_3'],
        TRIGGER_CODES['beep_4'],
        TRIGGER_CODES['beep_5'],
        TRIGGER_CODES['beep_6'],
        TRIGGER_CODES['beep_7'],
        TRIGGER_CODES['beep_8']
    ]
    
    for beep_idx in range(n_beeps):
        # Redraw fixation (keeps it visible during beeps)
        display.show_fixation()
        
        # Use unique trigger code for each beep
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
    
    # Create trial data structure
    trial_data = create_trial_data_dict(trial_num, concept, category)
    
    print(f"\n[SIM] Trial {trial_num}/{total_trials}: {concept} (Category {category})")
    
    # Send trial start trigger (unique code for this trial number)
    trial_start_code = get_trial_start_code(trial_num)
    timestamp, _ = trigger_handler.send_trigger(
        trial_start_code,
        event_name=f'trial_{trial_num}_start'
    )
    trial_data['timestamps']['trial_start'] = timestamp
    print(f"  [SIM] Trial {trial_num} start (trigger {trial_start_code}) at {timestamp:.3f}s")
    
    # 1. FIXATION (NO JITTER - important timing)
    display.show_fixation()
    timestamp, _ = trigger_handler.send_trigger(
        TRIGGER_CODES['fixation'],
        event_name='fixation'
    )
    trial_data['timestamps']['fixation'] = timestamp
    print(f"  [SIM] Fixation at {timestamp:.3f}s")
    core.wait(config.get('FIXATION_DURATION', 2.0))
    
    # 2. CONCEPT PRESENTATION
    progress_text = f"Trial {trial_num}/{total_trials}"
    display.show_concept(concept, show_progress=True, progress_text=progress_text)
    
    # Send category-specific trigger
    trigger_code = (TRIGGER_CODES['concept_category_a'] if category == 'A' 
                   else TRIGGER_CODES['concept_category_b'])
    event_name = f'concept_{concept}_category_{category}'
    timestamp, _ = trigger_handler.send_trigger(trigger_code, event_name=event_name)
    trial_data['timestamps']['concept'] = timestamp
    print(f"  [SIM] Concept '{concept}' (Category {category}) at {timestamp:.3f}s")
    
    # NO JITTER - important timing for concept presentation
    core.wait(config.get('PROMPT_DURATION', 2.0))
    
    # Clear concept and pause before beeps (JITTERED - pause event)
    display.clear_screen()
    use_jitter = config.get('USE_JITTER', True)
    jitter_range = config.get('JITTER_RANGE', 0.1)
    post_concept_pause = config.get('POST_CONCEPT_PAUSE', 1.0)
    core.wait(jittered_wait(post_concept_pause, jitter_range) if use_jitter else post_concept_pause)
    
    # Show fixation cross (stays on during beeps)
    display.show_fixation()
    
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
    rest_duration = config.get('REST_DURATION', 1.0)
    core.wait(jittered_wait(rest_duration, jitter_range) if use_jitter else rest_duration)
    
    return trial_data


def run_experiment_simulation(
    participant_id: str = 'sim_9999',
    session_id: int = 1,
    config_path: Optional[Path] = None,
    n_trials: Optional[int] = None,
    verbose: bool = True
) -> Dict[str, any]:
    """
    Run complete experiment simulation.
    
    Tests all functionality without requiring EEG hardware or participant.
    
    Parameters
    ----------
    participant_id : str
        Participant identifier (default: sim_9999 for simulation)
    session_id : int
        Session number
    config_path : Path, optional
        Path to config file
    n_trials : int, optional
        Number of trials to run (default: from config)
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
    print(f"Session: {session_id}")
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
    
    # Override trial count if specified
    if n_trials is not None:
        config['N_TRIALS'] = n_trials
        if verbose:
            print(f"\n[OVERRIDE] Running {n_trials} trials (instead of {config.get('N_TRIALS', 20)})")
    
    # Initialize trigger handler (test mode - no hardware) with CSV logging
    csv_log_dir = Path(__file__).parent.parent / 'data' / 'triggers'
    csv_log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_log_path = csv_log_dir / f"sub-{participant_id}_ses-{session_id}_{timestamp}_triggers.csv"
    
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
    metadata = create_metadata(
        participant_id=participant_id,
        session_id=session_id,
        config=config
    )
    
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
    
    # Create trial sequence
    print("\n[SEQUENCE] Creating trial sequence...")
    trials = create_balanced_sequence(
        n_trials=config.get('N_TRIALS', 20),
        concepts_a=config.get('CONCEPTS_CATEGORY_A', []),
        concepts_b=config.get('CONCEPTS_CATEGORY_B', []),
        randomize=config.get('RANDOMIZE_CONCEPTS', True)
    )
    
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
    print("STARTING SIMULATION EXPERIMENT")
    print("="*80)
    
    experiment_clock.reset()
    
    # Get block configuration
    n_blocks = config.get('N_BLOCKS', 1)
    n_trials_total = len(trials)
    trials_per_block = n_trials_total // n_blocks
    
    print(f"\n[CONFIG] Blocks: {n_blocks}, Trials per block: {trials_per_block}, Total trials: {n_trials_total}")
    
    # Run blocks
    trial_counter = 0
    for block_num in range(1, n_blocks + 1):
        # Block start
        block_start_code = get_block_start_code(block_num)
        timestamp, _ = trigger_handler.send_trigger(
            block_start_code,
            event_name=f'block_{block_num}_start'
        )
        print(f"\n[TRIGGER] Block {block_num} start (trigger {block_start_code}) at {timestamp:.3f}s")
        
        # Calculate trials for this block
        block_start_idx = (block_num - 1) * trials_per_block
        block_end_idx = block_start_idx + trials_per_block
        block_trials = trials[block_start_idx:block_end_idx]
        
        print(f"[BLOCK {block_num}] Running trials {block_start_idx + 1}-{block_end_idx} ({len(block_trials)} trials)")
        
        # Run trials in this block
        for trial_spec in block_trials:
            trial_counter += 1
            
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
                trial_num=trial_counter,
                total_trials=n_trials_total
            )
            
            trial_data_list.append(trial_data)
            
            # Inter-trial interval (jittered)
            if trial_counter < n_trials_total:
                use_jitter = config.get('USE_JITTER', True)
                jitter_range = config.get('JITTER_RANGE', 0.1)
                inter_trial_interval = config.get('INTER_TRIAL_INTERVAL', 0.5)
                wait_duration = jittered_wait(inter_trial_interval, jitter_range) if use_jitter else inter_trial_interval
                core.wait(wait_duration)
        
        # Block end
        block_end_code = get_block_end_code(block_num)
        timestamp, _ = trigger_handler.send_trigger(
            block_end_code,
            event_name=f'block_{block_num}_end'
        )
        print(f"[TRIGGER] Block {block_num} end (trigger {block_end_code}) at {timestamp:.3f}s")
        
        # Block break (except after last block)
        if block_num < n_blocks:
            print(f"\n[BLOCK BREAK] Rest before block {block_num + 1}...")
            display.show_text(
                f"Block {block_num} complete.\n\nTake a short break.\n\nBlock {block_num + 1} starting soon...",
                height=0.05,
                color='yellow'
            )
            core.wait(5.0)  # 5 second break between blocks
            display.clear_screen()
    
    # Close trigger handler (saves CSV file)
    trigger_handler.close()
    
    # Save data
    print("\n[DATA] Saving trial data...")
    output_dir = project_root / 'data' / 'results'
    
    saved_files = save_trial_data(
        metadata=metadata,
        trial_data=trial_data_list,
        output_dir=output_dir,
        participant_id=participant_id,
        session_id=session_id
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
        'session_id': session_id,
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
  # Run simulation with default settings
  python paradigm/semantic_paradigm_simulation.py
  
  # Run with specific participant ID
  python paradigm/semantic_paradigm_simulation.py --participant-id sim_0001
  
  # Run fewer trials for quick test
  python paradigm/semantic_paradigm_simulation.py --n-trials 5
  
  # Verbose output
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
        '--session', '-s',
        type=int,
        default=1,
        help='Session number (default: 1)'
    )
    
    parser.add_argument(
        '--n-trials', '-n',
        type=int,
        default=None,
        help='Number of trials to run (default: from config)'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default=None,
        help='Path to config file (default: config/experiment_config.py)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    config_path = None
    if args.config:
        config_path = Path(args.config)
    
    try:
        results = run_experiment_simulation(
            participant_id=args.participant_id,
            session_id=args.session,
            config_path=config_path,
            n_trials=args.n_trials,
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
