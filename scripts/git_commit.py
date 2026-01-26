#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git commit CLI tool for flawless commits.

Ensures proper git workflow:
- Checks for uncommitted changes
- Validates commit message format
- Handles staged/unstaged files appropriately
- Provides helpful error messages
- Follows project conventions
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import List, Optional, Tuple

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        # Python < 3.7
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


def run_git_command(cmd: List[str], check: bool = True) -> Tuple[int, str, str]:
    """
    Run a git command and return the result.
    
    Args:
        cmd: Git command as list of strings
        check: If True, raise error on non-zero exit
    
    Returns:
        Tuple of (exit_code, stdout, stderr)
    """
    try:
        result = subprocess.run(
            ['git'] + cmd,
            capture_output=True,
            text=True,
            check=check
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.CalledProcessError as e:
        return e.returncode, e.stdout.strip(), e.stderr.strip()


def check_git_repo() -> bool:
    """Check if current directory is a git repository."""
    exit_code, _, _ = run_git_command(['rev-parse', '--git-dir'], check=False)
    return exit_code == 0


def get_git_status() -> Tuple[List[str], List[str], List[str]]:
    """
    Get git status information.
    
    Returns:
        Tuple of (modified_files, untracked_files, staged_files)
    """
    exit_code, stdout, stderr = run_git_command(['status', '--porcelain'], check=False)
    
    if exit_code != 0:
        print(f"[ERROR] Error checking git status: {stderr}")
        return [], [], []
    
    modified = []
    untracked = []
    staged = []
    
    for line in stdout.split('\n'):
        if not line.strip():
            continue
        
        status = line[:2]
        filename = line[3:]
        
        if status[0] == ' ' and status[1] != ' ':
            # Modified but not staged
            modified.append(filename)
        elif status[0] != ' ' and status[1] == ' ':
            # Staged
            staged.append(filename)
        elif status == '??':
            # Untracked
            untracked.append(filename)
        elif status[0] != ' ' and status[1] != ' ':
            # Both staged and modified (e.g., 'MM')
            staged.append(filename)
            if status[1] == 'M':
                modified.append(filename)
    
    return modified, untracked, staged


def check_for_changes() -> bool:
    """Check if there are any changes to commit."""
    modified, untracked, staged = get_git_status()
    return len(modified) > 0 or len(untracked) > 0 or len(staged) > 0


def validate_commit_message(message: str) -> Tuple[bool, str]:
    """
    Validate commit message format.
    
    Requirements:
    - Non-empty
    - First line <= 72 characters (GitHub best practice)
    - Descriptive (not just "update" or "fix")
    
    Args:
        message: Commit message
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not message or not message.strip():
        return False, "Commit message cannot be empty"
    
    lines = message.strip().split('\n')
    first_line = lines[0]
    
    if len(first_line) > 72:
        return False, f"First line too long ({len(first_line)} chars, max 72). Consider a shorter summary."
    
    # Check for vague messages
    vague_patterns = ['update', 'fix', 'change', 'modify', 'stuff', 'things']
    first_lower = first_line.lower()
    if any(pattern in first_lower and len(first_line.split()) < 5 for pattern in vague_patterns):
        return False, f"Commit message too vague: '{first_line}'. Be more specific about what changed."
    
    return True, ""


def format_commit_message(summary: str, body: Optional[str] = None) -> str:
    """
    Format commit message with proper structure.
    
    Args:
        summary: One-line summary (max 72 chars)
        body: Optional multi-line body
    
    Returns:
        Formatted commit message
    """
    if len(summary) > 72:
        print(f"[WARNING] Summary line is {len(summary)} characters (recommended: <= 72)")
    
    message = summary.strip()
    
    if body:
        message += "\n\n" + body.strip()
    
    return message


def add_files(files: Optional[List[str]] = None, all_files: bool = False) -> Tuple[bool, str]:
    """
    Stage files for commit.
    
    Args:
        files: Specific files to add (None = all)
        all_files: If True, add all changes (git add -A)
    
    Returns:
        Tuple of (success, message)
    """
    if all_files:
        exit_code, stdout, stderr = run_git_command(['add', '-A'])
        if exit_code != 0:
            return False, f"Error adding files: {stderr}"
        return True, "All changes staged"
    
    if files:
        exit_code, stdout, stderr = run_git_command(['add'] + files)
        if exit_code != 0:
            return False, f"Error adding files: {stderr}"
        return True, f"Staged {len(files)} file(s)"
    
    # Interactive mode - show status and ask
    modified, untracked, staged = get_git_status()
    
    if not modified and not untracked:
        return True, "No files to stage"
    
    print("\nFiles to stage:")
    if modified:
        print("\nModified (not staged):")
        for f in modified:
            print(f"  - {f}")
    
    if untracked:
        print("\nUntracked:")
        for f in untracked:
            print(f"  - {f}")
    
    if staged:
        print("\nAlready staged:")
        for f in staged:
            print(f"  [STAGED] {f}")
    
    # Add all by default (can be made interactive later)
    exit_code, stdout, stderr = run_git_command(['add', '-A'])
    if exit_code != 0:
        return False, f"Error adding files: {stderr}"
    
    return True, "All changes staged"


def create_commit(message: str, allow_empty: bool = False, no_verify: bool = False) -> Tuple[bool, str]:
    """
    Create git commit.
    
    Args:
        message: Commit message
        allow_empty: Allow empty commits
        no_verify: Skip pre-commit hooks
    
    Returns:
        Tuple of (success, message)
    """
    cmd = ['commit', '-m', message]
    if allow_empty:
        cmd.append('--allow-empty')
    if no_verify:
        cmd.append('--no-verify')
    
    exit_code, stdout, stderr = run_git_command(cmd, check=False)
    
    if exit_code != 0:
        return False, f"Commit failed: {stderr}"
    
    return True, stdout or "Commit created successfully"


def get_commit_summary() -> str:
    """Get a summary of what changed for commit message."""
    modified, untracked, staged = get_git_status()
    
    all_files = set(modified + untracked + staged)
    
    # Categorize files
    categories = {
        'config': [],
        'scripts': [],
        'utils': [],
        'docs': [],
        'tests': [],
        'experiments': [],
        'other': []
    }
    
    for file in all_files:
        if 'config' in file.lower():
            categories['config'].append(file)
        elif 'scripts' in file.lower() or (file.endswith('.py') and 'paradigm' in file):
            categories['experiments'].append(file)
        elif 'utils' in file.lower():
            categories['utils'].append(file)
        elif 'docs' in file.lower() or file.endswith('.md'):
            categories['docs'].append(file)
        elif 'test' in file.lower():
            categories['tests'].append(file)
        elif file.endswith('.py') and 'rhythmic' in file:
            categories['experiments'].append(file)
        else:
            categories['other'].append(file)
    
    # Build summary
    parts = []
    if categories['experiments']:
        parts.append(f"experiments ({len(categories['experiments'])})")
    if categories['scripts']:
        parts.append(f"scripts ({len(categories['scripts'])})")
    if categories['utils']:
        parts.append(f"utilities ({len(categories['utils'])})")
    if categories['config']:
        parts.append(f"config ({len(categories['config'])})")
    if categories['docs']:
        parts.append(f"docs ({len(categories['docs'])})")
    if categories['tests']:
        parts.append(f"tests ({len(categories['tests'])})")
    if categories['other']:
        parts.append(f"other ({len(categories['other'])})")
    
    return ", ".join(parts) if parts else "files"


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description='Flawless git commit tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive commit (shows status, asks for message)
  python scripts/git_commit.py
  
  # Commit with message
  python scripts/git_commit.py -m "Add feature X"
  
  # Commit with multi-line message
  python scripts/git_commit.py -m "Add feature X" -b "Detailed description here"
  
  # Stage specific files only
  python scripts/git_commit.py -f file1.py file2.py -m "Update files"
        """
    )
    
    parser.add_argument(
        '-m', '--message',
        type=str,
        help='Commit message (summary line)'
    )
    
    parser.add_argument(
        '-b', '--body',
        type=str,
        help='Commit message body (detailed description)'
    )
    
    parser.add_argument(
        '-f', '--files',
        nargs='+',
        help='Specific files to commit (default: all changes)'
    )
    
    parser.add_argument(
        '-a', '--all',
        action='store_true',
        help='Stage all changes automatically'
    )
    
    parser.add_argument(
        '--allow-empty',
        action='store_true',
        help='Allow empty commits'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be committed without actually committing'
    )
    
    parser.add_argument(
        '--no-verify',
        action='store_true',
        help='Skip pre-commit hooks (use with caution)'
    )
    
    args = parser.parse_args()
    
    # Check if we're in a git repo
    if not check_git_repo():
        print("[ERROR] Not a git repository")
        print("   Run this script from the project root directory")
        sys.exit(1)
    
    # Check for changes
    if not check_for_changes() and not args.allow_empty:
        print("[OK] No changes to commit")
        sys.exit(0)
    
    # Get status
    modified, untracked, staged = get_git_status()
    
    if not args.dry_run:
        # Stage files
        if args.files:
            success, msg = add_files(files=args.files)
        else:
            success, msg = add_files(all_files=args.all)
        
        if not success:
            print(f"[ERROR] {msg}")
            sys.exit(1)
        
        print(f"[OK] {msg}")
    
    # Get commit message
    if args.message:
        commit_message = format_commit_message(args.message, args.body)
    else:
        # Interactive mode - generate suggestion
        summary = get_commit_summary()
        print(f"\n[SUGGESTION] Suggested commit message:")
        print(f"   Update {summary}")
        print("\nEnter commit message (or press Enter to use suggestion):")
        user_input = input("> ").strip()
        
        if user_input:
            commit_message = format_commit_message(user_input, args.body)
        else:
            commit_message = format_commit_message(f"Update {summary}")
    
    # Validate message
    is_valid, error_msg = validate_commit_message(commit_message)
    if not is_valid:
        print(f"[ERROR] Invalid commit message: {error_msg}")
        print(f"\nYour message:")
        print(commit_message)
        sys.exit(1)
    
    if args.dry_run:
        print("\n[DRY RUN] Would commit:")
        print(f"\nMessage:\n{commit_message}\n")
        print(f"Files: {len(modified) + len(untracked) + len(staged)} file(s)")
        sys.exit(0)
    
    # Create commit
    success, msg = create_commit(commit_message, allow_empty=args.allow_empty, no_verify=args.no_verify)
    
    if success:
        print(f"\n[SUCCESS] {msg}")
        
        # Show commit info
        exit_code, stdout, _ = run_git_command(['log', '-1', '--oneline'], check=False)
        if exit_code == 0:
            print(f"   {stdout}")
    else:
        print(f"\n[ERROR] {msg}")
        sys.exit(1)


if __name__ == "__main__":
    main()
