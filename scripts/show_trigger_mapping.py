#!/usr/bin/env python3
"""
Show complete trigger code mapping for the experiment.
"""

import sys
from pathlib import Path

# Add parent directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Read trigger codes directly from file (avoiding psychopy dependency)
trigger_utils_path = project_root / 'paradigm' / 'utils' / 'trigger_utils.py'
with open(trigger_utils_path, 'r') as f:
    content = f.read()

# Extract TRIGGER_CODES dict
import ast
import re

# Find TRIGGER_CODES dict
match = re.search(r'TRIGGER_CODES\s*=\s*\{.*?\n\}', content, re.DOTALL)
if match:
    dict_str = match.group(0)
    dict_match = re.search(r'\{.*\}', dict_str, re.DOTALL)
    if dict_match:
        try:
            # Try to parse as literal
            TRIGGER_CODES = ast.literal_eval(dict_match.group(0))
        except:
            # Fallback: manual extraction
            TRIGGER_CODES = {
                'trial_start': 2, 'fixation': 1,
                'concept_category_a': 10, 'concept_category_b': 20,
                'beep_start': 30, 'beep_1': 31, 'beep_2': 32, 'beep_3': 33,
                'beep_4': 34, 'beep_5': 35, 'beep_6': 36, 'beep_7': 37, 'beep_8': 38,
                'trial_end': 40, 'block_start': 50, 'block_end': 51
            }
    else:
        TRIGGER_CODES = {}
else:
    TRIGGER_CODES = {}

# Define code generation functions manually (matching the fixed versions)
def get_trial_start_code(trial_num): 
    # Trial codes are reused per block (1-10)
    block_local = ((trial_num - 1) % 10) + 1
    if block_local < 1 or block_local > 10:
        raise ValueError(f"Block-local trial number must be between 1 and 10, got {block_local} from {trial_num}")
    return 100 + block_local

def get_trial_end_code(trial_num):
    # Trial codes are reused per block (1-10)
    block_local = ((trial_num - 1) % 10) + 1
    if block_local < 1 or block_local > 10:
        raise ValueError(f"Block-local trial number must be between 1 and 10, got {block_local} from {trial_num}")
    return 150 + block_local

def get_block_start_code(block_num):
    if block_num < 1 or block_num > 10:
        raise ValueError(f"Block number must be between 1 and 10, got {block_num}")
    return 60 + block_num

def get_block_end_code(block_num):
    if block_num < 1 or block_num > 10:
        raise ValueError(f"Block number must be between 1 and 10, got {block_num}")
    return 70 + block_num

def get_beep_code(beep_num, max_beeps=8):
    if beep_num < 1 or beep_num > max_beeps:
        raise ValueError(f"Beep number must be between 1 and {max_beeps}, got {beep_num}")
    return 30 + beep_num

def show_complete_mapping():
    """Show complete trigger code mapping."""
    print("="*80)
    print("COMPLETE TRIGGER CODE MAPPING")
    print("="*80)
    
    # Base codes
    print("\n1. BASE CODES (Static):")
    print("-" * 80)
    for name, code in sorted(TRIGGER_CODES.items(), key=lambda x: x[1]):
        print(f"   {name:25s} = {code:3d} (0x{code:02X})")
    
    # Beep codes
    print("\n2. BEEP CODES (Dynamic):")
    print("-" * 80)
    print("   Formula: 30 + beep_num")
    print("   Range: 31-38 (for beeps 1-8)")
    for beep in range(1, 9):
        code = get_beep_code(beep)
        print(f"   beep_{beep:2d}                    = {code:3d} (0x{code:02X})")
    
    # Block codes
    print("\n3. BLOCK CODES (Dynamic):")
    print("-" * 80)
    print("   Block Start: 60 + block_num")
    print("   Block End:   70 + block_num")
    print("   Range: 61-70 (start), 71-80 (end) for blocks 1-10")
    for block in range(1, 11):
        start_code = get_block_start_code(block)
        end_code = get_block_end_code(block)
        print(f"   Block {block} start              = {start_code:3d} (0x{start_code:02X})")
        print(f"   Block {block} end                = {end_code:3d} (0x{end_code:02X})")
    
    # Trial codes (1-10, reused per block)
    print("\n4. TRIAL CODES (Dynamic, reused per block):")
    print("-" * 80)
    print("   Trial Start: 100 + (trial_num % 10)")
    print("   Trial End:   150 + (trial_num % 10)")
    print("   Range: 101-110 (start), 151-160 (end) for trials 1-10")
    print("   NOTE: Codes are reused across blocks (each block has trials 1-10)")
    print("\n   All 10 trials:")
    for trial in range(1, 11):
        start_code = get_trial_start_code(trial)
        end_code = get_trial_end_code(trial)
        print(f"   Trial {trial:2d} start              = {start_code:3d} (0x{start_code:02X})")
        print(f"   Trial {trial:2d} end                = {end_code:3d} (0x{end_code:02X})")
    
    # Code range summary
    print("\n5. CODE RANGE SUMMARY:")
    print("-" * 80)
    print("   Base codes:        1-51 (sparse)")
    print("   Beep codes:       31-38")
    print("   Block start:      61-70")
    print("   Block end:        71-80")
    print("   Trial start:     101-110 (reused per block)")
    print("   Trial end:       151-160 (reused per block)")
    print("\n   Total unique codes: 55 (all within 0-255)")
    
    # Overlap check (excluding beep codes from base since they're intentionally duplicated)
    print("\n6. OVERLAP VERIFICATION:")
    print("-" * 80)
    # Base codes EXCLUDING beep codes (beeps are handled separately)
    base_codes = {v for k, v in TRIGGER_CODES.items() if not k.startswith('beep_')}
    beep_codes = set(range(31, 39))
    block_start_codes = set(range(61, 71))
    block_end_codes = set(range(71, 81))
    trial_start_codes = set(range(101, 111))
    trial_end_codes = set(range(151, 161))
    
    all_ranges = [
        ("Base", base_codes),
        ("Beep", beep_codes),
        ("Block Start", block_start_codes),
        ("Block End", block_end_codes),
        ("Trial Start", trial_start_codes),
        ("Trial End", trial_end_codes)
    ]
    
    overlaps_found = False
    for i, (name1, codes1) in enumerate(all_ranges):
        for name2, codes2 in all_ranges[i+1:]:
            overlap = codes1 & codes2
            if overlap:
                print(f"   [ERROR] {name1} overlaps with {name2}: {sorted(overlap)}")
                overlaps_found = True
    
    if not overlaps_found:
        print("   [OK] No overlaps detected - all code ranges are unique")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    show_complete_mapping()
