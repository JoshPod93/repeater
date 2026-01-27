#!/usr/bin/env python3
"""
Calculate how much of the trigger space is being used.
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

# Calculate all used codes
all_codes = set()

# Base codes (excluding beeps which are in TRIGGER_CODES)
base_codes = {v for k, v in TRIGGER_CODES.items() if not k.startswith('beep_')}
all_codes.update(base_codes)

# Beep codes (31-38)
beep_codes = set(range(31, 39))
all_codes.update(beep_codes)

# Block codes
for block in range(1, n_blocks + 1):
    all_codes.add(get_block_start_code(block))
    all_codes.add(get_block_end_code(block))

# Trial codes (only 1-10, reused per block)
for trial in range(1, n_trials_per_block + 1):
    all_codes.add(get_trial_start_code(trial))
    all_codes.add(get_trial_end_code(trial))

# Calculate statistics
min_code = min(all_codes)
max_code = max(all_codes)
total_unique_codes = len(all_codes)

# 8-bit space (0-255)
codes_8bit = {c for c in all_codes if c <= 255}
codes_over_8bit = {c for c in all_codes if c > 255}

# Print results
print("="*80)
print("TRIGGER SPACE USAGE ANALYSIS")
print("="*80)

print(f"\n1. CONFIGURATION:")
print(f"   Trials per block: {n_trials_per_block}")
print(f"   Blocks: {n_blocks}")
print(f"   Total trials: {n_trials_per_block * n_blocks}")
print(f"   NOTE: Trial codes (1-10) are reused per block")

print(f"\n2. CODE RANGES:")
print(f"   Minimum code: {min_code}")
print(f"   Maximum code: {max_code}")
print(f"   Total unique codes: {total_unique_codes}")

print(f"\n3. CODE DISTRIBUTION:")
print(f"   Base codes: {len(base_codes)} codes")
print(f"   Beep codes: {len(beep_codes)} codes")
print(f"   Block codes: {n_blocks * 2} codes ({n_blocks} start + {n_blocks} end)")
print(f"   Trial codes: {n_trials_per_block * 2} codes ({n_trials_per_block} start + {n_trials_per_block} end, reused per block)")

print(f"\n4. 8-BIT SPACE (0-255):")
print(f"   Total available: 256 codes (0-255)")
print(f"   Codes used (<=255): {len(codes_8bit)} codes")
print(f"   Codes exceeding 8-bit (>255): {len(codes_over_8bit)} codes")
if codes_over_8bit:
    print(f"   Exceeding codes: {sorted(codes_over_8bit)}")
    print(f"   WARNING: These codes exceed 8-bit parallel port range!")

usage_8bit = (len(codes_8bit) / 256) * 100
print(f"   8-bit space usage: {usage_8bit:.2f}%")

print(f"\n5. FULL RANGE USAGE:")
if max_code <= 255:
    full_range = 256
else:
    # Calculate actual range used
    full_range = max_code + 1
full_usage = (total_unique_codes / full_range) * 100
print(f"   Range: 0-{max_code} ({full_range} codes)")
print(f"   Codes used: {total_unique_codes}")
print(f"   Usage: {full_usage:.2f}%")

print(f"\n6. SPARSE VS DENSE:")
# Calculate density
used_ranges = []
if base_codes:
    used_ranges.append((min(base_codes), max(base_codes)))
if beep_codes:
    used_ranges.append((min(beep_codes), max(beep_codes)))
if n_blocks > 0:
    used_ranges.append((get_block_start_code(1), get_block_start_code(n_blocks)))
    used_ranges.append((get_block_end_code(1), get_block_end_code(n_blocks)))
if n_trials_per_block > 0:
    used_ranges.append((get_trial_start_code(1), get_trial_start_code(n_trials_per_block)))
    used_ranges.append((get_trial_end_code(1), get_trial_end_code(n_trials_per_block)))

total_range_span = sum(end - start + 1 for start, end in used_ranges)
print(f"   Total span of ranges: {total_range_span} codes")
print(f"   Actual codes used: {total_unique_codes} codes")
print(f"   Density: {(total_unique_codes / total_range_span) * 100:.2f}% (sparse allocation)")

print(f"\n7. AVAILABLE SPACE:")
available_8bit = 256 - len(codes_8bit)
print(f"   Available in 8-bit space: {available_8bit} codes")
if max_code > 255:
    print(f"   Codes beyond 8-bit: {max_code - 255} codes")
    print(f"   NOTE: Biosemi may support >8-bit triggers, but verify compatibility")

print("\n" + "="*80)
