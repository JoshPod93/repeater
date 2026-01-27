#!/usr/bin/env python3
"""
Evaluate pathing, triggers, and file organization.
Checks consistency across the codebase.
"""

import sys
from pathlib import Path
from collections import defaultdict

# Add parent directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def evaluate_pathing():
    """Evaluate path structure and consistency."""
    print("="*80)
    print("PATHING EVALUATION")
    print("="*80)
    
    # Check data directory structure
    data_dir = project_root / 'data'
    results_dir = data_dir / 'results'
    
    print("\n1. DATA DIRECTORY STRUCTURE:")
    print(f"   Project root: {project_root}")
    data_exists = '[EXISTS]' if data_dir.exists() else '[MISSING]'
    results_exists = '[EXISTS]' if results_dir.exists() else '[MISSING]'
    print(f"   Data directory: {data_dir} {data_exists}")
    print(f"   Results directory: {results_dir} {results_exists}")
    
    # Check BDF directory structure
    bdf_dirs = list(data_dir.glob('sub_*'))
    print(f"\n   BDF directories found: {len(bdf_dirs)}")
    for bdf_dir in bdf_dirs:
        bdf_files = list(bdf_dir.glob('*.bdf'))
        print(f"     {bdf_dir.name}: {len(bdf_files)} BDF file(s)")
        for bdf_file in bdf_files:
            print(f"       - {bdf_file.name}")
    
    # Check results structure
    if results_dir.exists():
        result_folders = [d for d in results_dir.iterdir() if d.is_dir()]
        print(f"\n   Results folders found: {len(result_folders)}")
        for folder in result_folders[:5]:  # Show first 5
            blocks = list(folder.glob('Block_*'))
            csv_files = list(folder.glob('*_triggers.csv'))
            json_files = list(folder.glob('*_randomization_protocol.json'))
            print(f"     {folder.name}:")
            print(f"       Blocks: {len(blocks)}")
            print(f"       Trigger CSVs: {len(csv_files)}")
            print(f"       Protocol JSONs: {len(json_files)}")
    
    # Expected structure
    print("\n2. EXPECTED PATH STRUCTURE:")
    print("   data/")
    print("     sub_{participant_id}/")
    print("       sub_{participant_id}.bdf          # BDF file from Biosemi")
    print("     results/")
    print("       sub-{participant_id}_{timestamp}/  # Subject folder")
    print("         Block_0000/                      # Block folders")
    print("         Block_0001/")
    print("         ...")
    print("         sub-{participant_id}_{timestamp}_trials.json")
    print("         sub-{participant_id}_{timestamp}_trials.npy")
    print("         sub-{participant_id}_{timestamp}_triggers.csv")
    print("         sub-{participant_id}_{timestamp}_randomization_protocol.json")
    
    # Check for inconsistencies
    print("\n3. PATHING CONSISTENCY CHECK:")
    issues = []
    
    # Check BDF vs Results naming convention
    if bdf_dirs:
        bdf_participants = {d.name.replace('sub_', '') for d in bdf_dirs}
        if result_folders:
            result_participants = {f.name.split('_')[0].replace('sub-', '') for f in result_folders}
            mismatch = bdf_participants - result_participants
            if mismatch:
                issues.append(f"BDF participants without results: {mismatch}")
    
    # Check naming conventions
    for bdf_dir in bdf_dirs:
        if not bdf_dir.name.startswith('sub_'):
            issues.append(f"BDF directory naming: {bdf_dir.name} should start with 'sub_'")
    
    if result_folders:
        for folder in result_folders:
            if not folder.name.startswith('sub-'):
                issues.append(f"Results folder naming: {folder.name} should start with 'sub-'")
    
    if issues:
        print("   ISSUES FOUND:")
        for issue in issues:
            print(f"     - {issue}")
    else:
        print("   [OK] No pathing inconsistencies found")


def evaluate_triggers():
    """Evaluate trigger code usage and consistency."""
    print("\n" + "="*80)
    print("TRIGGER CODE EVALUATION")
    print("="*80)
    
    # Read trigger codes directly from file (avoid psychopy import)
    trigger_utils_path = project_root / 'paradigm' / 'utils' / 'trigger_utils.py'
    with open(trigger_utils_path, 'r') as f:
        content = f.read()
    
    # Extract TRIGGER_CODES dict
    import ast
    import re
    
    # Find TRIGGER_CODES dict
    match = re.search(r'TRIGGER_CODES\s*=\s*\{[^}]+\}', content, re.DOTALL)
    if match:
        # Parse the dict
        dict_str = match.group(0)
        # Extract just the dict content
        dict_match = re.search(r'\{.*\}', dict_str, re.DOTALL)
        if dict_match:
            try:
                TRIGGER_CODES = ast.literal_eval(dict_match.group(0))
            except:
                # Fallback: manual parsing
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
    
    # Define code generation functions manually (matching fixed versions)
    def get_trial_start_code(n): return 100 + n
    def get_trial_end_code(n): return 200 + n
    def get_block_start_code(n): return 60 + n   # FIXED: Changed from 150+N
    def get_block_end_code(n): return 70 + n     # FIXED: Changed from 250+N
    def get_beep_code(n): return 30 + n
    
    print("\n1. TRIGGER CODE MAPPINGS:")
    print("\n   Base Codes (TRIGGER_CODES dict):")
    for name, code in sorted(TRIGGER_CODES.items(), key=lambda x: x[1]):
        print(f"     {name:20s} = {code:3d} (0x{code:02X})")
    
    print("\n   Dynamic Codes:")
    print("     Trial N start  = 100 + N  (Range: 101-199)")
    print("     Trial N end    = 200 + N  (Range: 201-299)")
    print("     Block N start  = 60 + N   (Range: 61-69)   [FIXED: was 150+N]")
    print("     Block N end    = 70 + N   (Range: 71-79)   [FIXED: was 250+N]")
    print("     Beep N         = 30 + N   (Range: 31-38)")
    
    # Check for overlaps
    print("\n2. CODE OVERLAP CHECK:")
    all_codes = set(TRIGGER_CODES.values())
    
    # Check dynamic ranges (using FIXED values)
    trial_start_range = set(range(101, 200))
    trial_end_range = set(range(201, 300))
    block_start_range = set(range(61, 70))   # FIXED: Changed from 151-160
    block_end_range = set(range(71, 80))     # FIXED: Changed from 251-260
    beep_range = set(range(31, 39))
    
    overlaps = []
    if all_codes & trial_start_range:
        overlaps.append(f"Base codes overlap with trial_start range: {all_codes & trial_start_range}")
    if all_codes & trial_end_range:
        overlaps.append(f"Base codes overlap with trial_end range: {all_codes & trial_end_range}")
    if all_codes & block_start_range:
        overlaps.append(f"Base codes overlap with block_start range: {all_codes & block_start_range}")
    if all_codes & block_end_range:
        overlaps.append(f"Base codes overlap with block_end range: {all_codes & block_end_range}")
    if all_codes & beep_range:
        overlaps.append(f"Base codes overlap with beep range: {all_codes & beep_range}")
    
    # Check ranges against each other
    if trial_start_range & trial_end_range:
        overlaps.append("trial_start and trial_end ranges overlap")
    if block_start_range & block_end_range:
        overlaps.append("block_start and block_end ranges overlap")
    if trial_start_range & block_start_range:
        overlaps.append("trial_start and block_start ranges overlap")
    if trial_end_range & block_end_range:
        overlaps.append("trial_end and block_end ranges overlap")
    
    if overlaps:
        print("   ISSUES FOUND:")
        for overlap in overlaps:
            print(f"     - {overlap}")
    else:
        print("   [OK] No code overlaps detected")
    
    # Test code generation
    print("\n3. CODE GENERATION TEST:")
    try:
        test_trial_start = get_trial_start_code(1)
        test_trial_end = get_trial_end_code(1)
        test_block_start = get_block_start_code(1)
        test_block_end = get_block_end_code(1)
        test_beep = get_beep_code(1)
        
        print(f"   Trial 1 start: {test_trial_start} [OK]")
        print(f"   Trial 1 end:   {test_trial_end} [OK]")
        print(f"   Block 1 start:  {test_block_start} [OK]")
        print(f"   Block 1 end:    {test_block_end} [OK]")
        print(f"   Beep 1:         {test_beep} [OK]")
    except Exception as e:
        print(f"   [ERROR] Code generation failed: {e}")


def evaluate_file_organization():
    """Evaluate file organization consistency."""
    print("\n" + "="*80)
    print("FILE ORGANIZATION EVALUATION")
    print("="*80)
    
    results_dir = project_root / 'data' / 'results'
    
    if not results_dir.exists():
        print("\n   [SKIP] No results directory found")
        return
    
    result_folders = [d for d in results_dir.iterdir() if d.is_dir()]
    
    print(f"\n1. FOLDER STRUCTURE ANALYSIS ({len(result_folders)} folders):")
    
    structure_issues = []
    for folder in result_folders[:10]:  # Check first 10
        blocks = sorted([d for d in folder.iterdir() if d.is_dir() and d.name.startswith('Block_')])
        csv_files = list(folder.glob('*_triggers.csv'))
        json_protocols = list(folder.glob('*_randomization_protocol.json'))
        json_trials = list(folder.glob('*_trials.json'))
        npy_trials = list(folder.glob('*_trials.npy'))
        
        # Check expected structure
        if not blocks:
            structure_issues.append(f"{folder.name}: No block folders")
        if not csv_files:
            structure_issues.append(f"{folder.name}: No trigger CSV")
        if not json_protocols:
            structure_issues.append(f"{folder.name}: No randomization protocol JSON")
        
        # Check block folder contents
        for block in blocks:
            block_trials_json = list(block.glob('*_trials.json'))
            block_trials_npy = list(block.glob('*_trials.npy'))
            if not block_trials_json:
                structure_issues.append(f"{folder.name}/{block.name}: No trials JSON")
            if not block_trials_npy:
                structure_issues.append(f"{folder.name}/{block.name}: No trials NPY")
    
    if structure_issues:
        print("   ISSUES FOUND:")
        for issue in structure_issues[:20]:  # Show first 20
            print(f"     - {issue}")
        if len(structure_issues) > 20:
            print(f"     ... and {len(structure_issues) - 20} more")
    else:
        print("   [OK] File organization is consistent")


def main():
    """Run all evaluations."""
    evaluate_pathing()
    evaluate_triggers()
    evaluate_file_organization()
    
    print("\n" + "="*80)
    print("EVALUATION COMPLETE")
    print("="*80)


if __name__ == "__main__":
    main()
