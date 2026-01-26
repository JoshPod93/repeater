#!/usr/bin/env python3
"""
Check trigger code mapping and usage.

Verifies trigger codes are unique and shows usage across codebase.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from paradigm.utils import TRIGGER_CODES

def check_trigger_mapping():
    """Check trigger code mapping for overlaps and show usage."""
    
    print("="*70)
    print("TRIGGER CODE MAPPING")
    print("="*70)
    print()
    
    # Sort by code value
    codes_sorted = sorted(TRIGGER_CODES.items(), key=lambda x: x[1])
    
    print(f"{'Event Name':<30} {'Code':<8} {'Hex':<10} {'Binary':<10}")
    print("-"*70)
    
    for name, code in codes_sorted:
        hex_code = hex(code)
        bin_code = bin(code)
        print(f"{name:<30} {code:<8} {hex_code:<10} {bin_code:<10}")
    
    print("-"*70)
    print()
    
    # Statistics
    values = list(TRIGGER_CODES.values())
    unique_values = set(values)
    
    print("STATISTICS:")
    print(f"  Total triggers: {len(TRIGGER_CODES)}")
    print(f"  Unique codes: {len(unique_values)}")
    print(f"  Code range: {min(values)} - {max(values)}")
    print()
    
    # Check for duplicates
    duplicates = [v for v in unique_values if values.count(v) > 1]
    if duplicates:
        print("ERROR: DUPLICATE CODES FOUND!")
        for dup_code in duplicates:
            events = [name for name, code in TRIGGER_CODES.items() if code == dup_code]
            print(f"  Code {dup_code} used by: {', '.join(events)}")
    else:
        print("OK: All trigger codes are unique (no overlaps)")
    
    print()
    
    # Check usage in codebase
    print("USAGE IN CODEBASE:")
    paradigm_files = [
        Path(__file__).parent.parent / 'paradigm' / 'semantic_paradigm_live.py',
        Path(__file__).parent.parent / 'paradigm' / 'semantic_paradigm_simulation.py'
    ]
    
    usage_count = {name: 0 for name in TRIGGER_CODES.keys()}
    
    for file_path in paradigm_files:
        if file_path.exists():
            content = file_path.read_text()
            for trigger_name in TRIGGER_CODES.keys():
                # Count occurrences of TRIGGER_CODES['name'] or TRIGGER_CODES["name"]
                count = content.count(f"TRIGGER_CODES['{trigger_name}']")
                count += content.count(f'TRIGGER_CODES["{trigger_name}"]')
                usage_count[trigger_name] += count
    
    print(f"{'Event Name':<30} {'Uses':<8}")
    print("-"*40)
    for name, count in sorted(usage_count.items(), key=lambda x: -x[1]):
        print(f"{name:<30} {count:<8}")
    
    print()
    print("="*70)

if __name__ == "__main__":
    check_trigger_mapping()
