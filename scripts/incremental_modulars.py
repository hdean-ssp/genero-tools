#!/usr/bin/env python3
"""
Incremental modular information update.

Only re-extracts GLOBALS/IMPORT statements for changed/added files,
merges results into existing modulars.json, and removes entries for
deleted files.

Usage:
    python3 incremental_modulars.py <target_dir> <modulars_json> <changes_file>
"""

import json
import os
import re
import sys
from pathlib import Path


def extract_modulars_from_file(filepath: str, target_dir: str) -> dict:
    """Extract GLOBALS and IMPORT statements from a single .4gl file.
    
    Returns dict with 'globals' and 'imports' lists.
    """
    globals_list = []
    imports_list = []
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                stripped = line.strip()
                
                # GLOBALS statement
                if stripped.startswith('GLOBALS'):
                    global_name = stripped[len('GLOBALS'):].strip()
                    # Strip inline comments
                    global_name = re.sub(r'#.*', '', global_name).strip()
                    # Strip quotes
                    global_name = global_name.replace('"', '').replace("'", '')
                    if global_name and global_name != 'GLOBALS':
                        globals_list.append(global_name)
                
                # IMPORT statement
                elif stripped.startswith('IMPORT'):
                    import_name = stripped[len('IMPORT'):].strip()
                    # Strip inline comments
                    import_name = re.sub(r'#.*', '', import_name).strip()
                    # Strip quotes
                    import_name = import_name.replace('"', '').replace("'", '')
                    if import_name:
                        imports_list.append(import_name)
    except (IOError, OSError):
        pass
    
    return {
        'globals': globals_list,
        'imports': imports_list
    }


def normalize_path(path: str) -> str:
    """Normalize path to ./ prefix format."""
    path = os.path.normpath(path)
    if not path.startswith('./') and not path.startswith('/'):
        path = './' + path
    return path


def main():
    if len(sys.argv) < 4:
        print("Usage: incremental_modulars.py <target_dir> <modulars_json> <changes_file>", file=sys.stderr)
        sys.exit(1)
    
    target_dir = sys.argv[1]
    modulars_path = sys.argv[2]
    changes_path = sys.argv[3]
    
    # Load changes
    with open(changes_path, 'r') as f:
        changes = json.load(f)
    
    changed = set(changes.get('changed', []))
    added = set(changes.get('added', []))
    removed = set(changes.get('removed', []))
    
    files_to_process = changed | added
    
    if not files_to_process and not removed:
        print("[OK] No modular changes needed")
        return
    
    # Load existing modulars.json
    existing = {}
    if os.path.exists(modulars_path):
        try:
            with open(modulars_path, 'r') as f:
                existing = json.load(f)
        except (json.JSONDecodeError, IOError):
            existing = {}
    
    # Remove deleted files
    for rel_path in removed:
        norm = normalize_path(rel_path)
        existing.pop(norm, None)
        # Also try without prefix
        existing.pop(rel_path, None)
        existing.pop('./' + rel_path.lstrip('./'), None)
    
    # Re-extract for changed/added files
    processed = 0
    for rel_path in sorted(files_to_process):
        full_path = os.path.join(target_dir, rel_path)
        if not os.path.exists(full_path):
            continue
        
        modular_data = extract_modulars_from_file(full_path, target_dir)
        norm = normalize_path(rel_path)
        existing[norm] = modular_data
        processed += 1
    
    # Update metadata
    if '_metadata' in existing:
        existing['_metadata']['files_processed'] = len([k for k in existing if k != '_metadata'])
    
    # Count total files for output message
    total = len([k for k in existing if k != '_metadata'])
    
    # Write output
    with open(modulars_path, 'w') as f:
        json.dump(existing, f, indent=2)
    
    print(f"Generated modulars.json with {total} files")
    print(f"[OK] Incremental modular update: {processed} files re-processed, {len(removed)} removed")


if __name__ == '__main__':
    main()
