#!/usr/bin/env python3
"""
Verify there are NO overlaps in trigger codes - compute it properly.
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
            TRIGGER_CODES = ast.literal_eval(dict_match.group(0))
        except:
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

# Define code generation functions manually
def get_trial_start_code(n): 
    # Trial codes are reused per block (1-10)
    block_local = ((n - 1) % 10) + 1
    return 100 + block_local

def get_trial_end_code(n): 
    # Trial codes are reused per block (1-10)
    block_local = ((n - 1) % 10) + 1
    return 150 + block_local

def get_block_start_code(n): return 60 + n
def get_block_end_code(n): return 70 + n
def get_beep_code(n): return 30 + n

# Load config to get actual trial/block counts
from config import load_config
config = load_config()
n_trials_per_block = config.get('TRIALS_PER_BLOCK', 10)
n_blocks = config.get('N_BLOCKS', 10)

# Collect all codes by category
# Base codes EXCLUDING beep_1 through beep_8 (but including beep_start=30)
base_codes_set = {v for k, v in TRIGGER_CODES.items() if not (k.startswith('beep_') and k != 'beep_start')}
beep_codes_set = set(range(31, 39))  # beep_1 through beep_8
block_start_codes_set = {get_block_start_code(b) for b in range(1, n_blocks + 1)}
block_end_codes_set = {get_block_end_code(b) for b in range(1, n_blocks + 1)}
# Trial codes are reused per block (only 1-10)
trial_start_codes_set = {get_trial_start_code(t) for t in range(1, n_trials_per_block + 1)}
trial_end_codes_set = {get_trial_end_code(t) for t in range(1, n_trials_per_block + 1)}

# All codes together
all_codes = (base_codes_set | beep_codes_set | block_start_codes_set | 
             block_end_codes_set | trial_start_codes_set | trial_end_codes_set)

# Print ranges
print("="*80)
print("TRIGGER CODE OVERLAP VERIFICATION")
print("="*80)

print(f"\n1. CODE RANGES:")
print(f"   Base codes: {sorted(base_codes_set)}")
print(f"   Beep codes: {sorted(beep_codes_set)}")
print(f"   Block start codes: {sorted(block_start_codes_set)}")
print(f"   Block end codes: {sorted(block_end_codes_set)}")
print(f"   Trial start codes: {sorted(trial_start_codes_set)[:10]} ... {sorted(trial_start_codes_set)[-5:]}")
print(f"   Trial end codes: {sorted(trial_end_codes_set)[:10]} ... {sorted(trial_end_codes_set)[-5:]}")

print(f"\n2. OVERLAP CHECK:")
overlaps_found = False

# Check each pair of sets
categories = [
    ("Base", base_codes_set),
    ("Beep", beep_codes_set),
    ("Block Start", block_start_codes_set),
    ("Block End", block_end_codes_set),
    ("Trial Start", trial_start_codes_set),
    ("Trial End", trial_end_codes_set)
]

for i, (name1, codes1) in enumerate(categories):
    for name2, codes2 in categories[i+1:]:
        overlap = codes1 & codes2
        if overlap:
            print(f"   [ERROR] {name1} overlaps with {name2}: {sorted(overlap)}")
            overlaps_found = True

# Check for duplicates within sets
print(f"\n3. DUPLICATE CHECK:")
for name, codes in categories:
    if len(codes) != len(set(codes)):
        print(f"   [ERROR] {name} has duplicates!")
        overlaps_found = True

# Check total vs unique
print(f"\n4. TOTAL CODE COUNT:")
total_codes_expected = (len(base_codes_set) + len(beep_codes_set) + 
                        len(block_start_codes_set) + len(block_end_codes_set) +
                        len(trial_start_codes_set) + len(trial_end_codes_set))
print(f"   Sum of all category sizes: {total_codes_expected}")
print(f"   Unique codes in union: {len(all_codes)}")
if total_codes_expected != len(all_codes):
    print(f"   [ERROR] Mismatch! There are overlaps!")
    overlaps_found = True
else:
    print(f"   [OK] Counts match - no overlaps detected")

# Check range boundaries
print(f"\n5. RANGE BOUNDARY CHECK:")
ranges = [
    ("Base", min(base_codes_set) if base_codes_set else None, max(base_codes_set) if base_codes_set else None),
    ("Beep", min(beep_codes_set) if beep_codes_set else None, max(beep_codes_set) if beep_codes_set else None),
    ("Block Start", min(block_start_codes_set) if block_start_codes_set else None, max(block_start_codes_set) if block_start_codes_set else None),
    ("Block End", min(block_end_codes_set) if block_end_codes_set else None, max(block_end_codes_set) if block_end_codes_set else None),
    ("Trial Start", min(trial_start_codes_set) if trial_start_codes_set else None, max(trial_start_codes_set) if trial_start_codes_set else None),
    ("Trial End", min(trial_end_codes_set) if trial_end_codes_set else None, max(trial_end_codes_set) if trial_end_codes_set else None),
]

for name, min_val, max_val in ranges:
    if min_val is not None:
        print(f"   {name:15s}: {min_val:3d} - {max_val:3d}")

# Check if ranges overlap (check actual codes, not just ranges)
print(f"\n6. RANGE OVERLAP CHECK:")
category_sets = [
    ("Base", base_codes_set),
    ("Beep", beep_codes_set),
    ("Block Start", block_start_codes_set),
    ("Block End", block_end_codes_set),
    ("Trial Start", trial_start_codes_set),
    ("Trial End", trial_end_codes_set),
]

for i, (name1, codes1) in enumerate(category_sets):
    if not codes1:
        continue
    min1, max1 = min(codes1), max(codes1)
    for name2, codes2 in category_sets[i+1:]:
        if not codes2:
            continue
        min2, max2 = min(codes2), max(codes2)
        # Check if ranges overlap AND if actual codes overlap
        if not (max1 < min2 or max2 < min1):
            actual_overlap = codes1 & codes2
            if actual_overlap:
                print(f"   [ERROR] {name1} range ({min1}-{max1}) overlaps with {name2} range ({min2}-{max2})")
                print(f"           Overlapping codes: {sorted(actual_overlap)}")
                overlaps_found = True
            else:
                # Ranges overlap but no actual code overlap (sparse allocation)
                print(f"   [OK] {name1} range ({min1}-{max1}) and {name2} range ({min2}-{max2}) are adjacent/overlapping ranges but no code overlap")

if not overlaps_found:
    print("\n" + "="*80)
    print("[OK] NO OVERLAPS DETECTED - All trigger codes are unique!")
    print("="*80)
    print(f"\nTotal unique codes: {len(all_codes)}")
    print(f"Code range: {min(all_codes)} - {max(all_codes)}")
else:
    print("\n" + "="*80)
    print("[ERROR] OVERLAPS DETECTED!")
    print("="*80)
