#!/usr/bin/env python3
"""
Incremental signature generation - only re-process changed .4gl files.

Tracks file content hashes in a manifest file. On subsequent runs, only
files whose hash has changed (or new files) are re-processed. Results
are merged into the existing workspace.json.

Usage:
    python3 incremental_signatures.py <target_directory> [--manifest .genero-manifest.json]
    
    Set FORCE_FULL=1 to bypass incremental and do a full rebuild.
    Set VERBOSE=1 for progress output.
"""

import json
import hashlib
import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, Set, Tuple


DEFAULT_MANIFEST = ".genero-manifest.json"
WORKSPACE_JSON = "workspace.json"


def hash_file(path: str) -> str:
    """Compute MD5 hash of file contents."""
    h = hashlib.md5()
    try:
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                h.update(chunk)
    except (IOError, OSError):
        return ""
    return h.hexdigest()


def find_4gl_files(target_dir: str) -> Dict[str, str]:
    """Find all .4gl files and compute their hashes. Returns {relative_path: hash}."""
    files = {}
    target = Path(target_dir)
    
    for path in sorted(target.rglob("*.4gl")):
        # Get path relative to target
        try:
            rel = str(path.relative_to(target))
        except ValueError:
            rel = str(path)
        
        files[rel] = hash_file(str(path))
    
    return files


def load_manifest(manifest_path: str) -> Dict[str, str]:
    """Load previous manifest. Returns {relative_path: hash}."""
    if not os.path.exists(manifest_path):
        return {}
    
    try:
        with open(manifest_path, 'r') as f:
            data = json.load(f)
        return data.get("files", {})
    except (json.JSONDecodeError, IOError):
        return {}


def save_manifest(manifest_path: str, file_hashes: Dict[str, str]):
    """Save current manifest."""
    data = {
        "version": "1.0.0",
        "files": file_hashes
    }
    with open(manifest_path, 'w') as f:
        json.dump(data, f, indent=2)


def determine_changes(current: Dict[str, str], previous: Dict[str, str]) -> Tuple[Set[str], Set[str], Set[str]]:
    """Determine which files changed, were added, or removed.
    
    Returns: (changed, added, removed)
    """
    current_keys = set(current.keys())
    previous_keys = set(previous.keys())
    
    added = current_keys - previous_keys
    removed = previous_keys - current_keys
    
    # Check which existing files changed
    changed = set()
    for key in current_keys & previous_keys:
        if current[key] != previous[key]:
            changed.add(key)
    
    return changed, added, removed


def normalize_path(path: str) -> str:
    """Normalize path to ./ prefix format matching workspace.json."""
    path = os.path.normpath(path)
    if not path.startswith('./') and not path.startswith('/'):
        path = './' + path
    return path


def run_signature_extraction(target_dir: str, files_to_process: Set[str], script_dir: str) -> Dict:
    """Run generate_signatures.sh on specific files and return parsed results."""
    if not files_to_process:
        return {}
    
    results = {}
    gen_script = os.path.join(script_dir, "src", "generate_signatures.sh")
    
    for rel_path in sorted(files_to_process):
        full_path = os.path.join(target_dir, rel_path)
        if not os.path.exists(full_path):
            continue
        
        # Run signature extraction on single file
        try:
            result = subprocess.run(
                ["bash", gen_script, full_path],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode == 0 and os.path.exists(WORKSPACE_JSON):
                # Read the output (generate_signatures.sh writes to workspace.json)
                with open(WORKSPACE_JSON, 'r') as f:
                    data = json.load(f)
                
                # Extract the functions for this file (remove metadata)
                for file_key, funcs in data.items():
                    if file_key == '_metadata':
                        continue
                    if isinstance(funcs, list):
                        # Normalize the key to match our format
                        norm_key = normalize_path(rel_path)
                        results[norm_key] = funcs
                        break
        except (subprocess.TimeoutExpired, Exception) as e:
            print(f"  Warning: Failed to process {rel_path}: {e}", file=sys.stderr)
    
    return results


def run_batch_extraction(target_dir: str, files_to_process: Set[str], project_root: str) -> Dict:
    """Run signature extraction on all changed files at once using a temp directory approach."""
    if not files_to_process:
        return {}
    
    # Create a temporary file list and process them through the AWK pipeline directly
    # This is more efficient than calling generate_signatures.sh per file
    import tempfile
    
    gen_script = os.path.join(project_root, "src", "generate_signatures.sh")
    process_script = os.path.join(project_root, "scripts", "process_signatures.py")
    
    temp_file = tempfile.mktemp()
    temp_output = tempfile.mktemp(suffix=".json")
    
    try:
        # Extract the AWK processing from generate_signatures.sh
        # We'll run the AWK pipeline on each file and collect output
        for rel_path in sorted(files_to_process):
            full_path = os.path.join(target_dir, rel_path)
            if not os.path.exists(full_path):
                continue
            
            # Run the AWK extraction using the existing script for a single file
            result = subprocess.run(
                ["bash", gen_script, full_path],
                capture_output=True, text=True, timeout=60,
                env={**os.environ, "OUTPUT_FILE": temp_output, "VERBOSE": "0"}
            )
        
        # Now read the last output (single-file mode produces one file's worth)
        # This approach doesn't work well for batch. Let's use a different strategy.
        pass
    finally:
        for f in [temp_file, temp_output]:
            if os.path.exists(f):
                os.unlink(f)
    
    return {}


def merge_results(existing: Dict, new_results: Dict, removed_files: Set[str]) -> Dict:
    """Merge new extraction results into existing workspace.json data.
    
    - Updates entries for changed/added files
    - Removes entries for deleted files
    - Preserves entries for unchanged files
    """
    # Start with existing data
    merged = dict(existing)
    
    # Remove deleted files
    removed_normalized = {normalize_path(r) for r in removed_files}
    for key in list(merged.keys()):
        if key == '_metadata':
            continue
        if key in removed_normalized:
            del merged[key]
    
    # Update/add changed files
    for file_path, funcs in new_results.items():
        merged[file_path] = funcs
    
    return merged


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Incremental signature generation")
    parser.add_argument("target", help="Target directory containing .4gl files")
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST, help="Path to manifest file")
    parser.add_argument("--output", default=WORKSPACE_JSON, help="Output workspace.json path")
    parser.add_argument("--manifest-only", action="store_true", help="Only create/update manifest without processing")
    args = parser.parse_args()
    
    target_dir = args.target
    manifest_path = args.manifest
    output_file = args.output
    verbose = os.environ.get('VERBOSE', '0') == '1'
    force_full = os.environ.get('FORCE_FULL', '0') == '1'
    
    # Get project root (parent of scripts/)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    gen_script = os.path.join(project_root, "src", "generate_signatures.sh")
    
    if not os.path.isdir(target_dir):
        print(f"Error: Target directory not found: {target_dir}", file=sys.stderr)
        sys.exit(1)
    
    # Compute current file hashes
    current_hashes = find_4gl_files(target_dir)
    total_files = len(current_hashes)
    
    # Manifest-only mode: just save hashes and exit
    if args.manifest_only:
        save_manifest(manifest_path, current_hashes)
        if verbose:
            print(f"Manifest saved: {total_files} files hashed", file=sys.stderr)
        return
    
    if verbose:
        print(f"Found {total_files} .4gl files", file=sys.stderr)
    
    # Load previous manifest
    previous_hashes = load_manifest(manifest_path)
    
    # Determine what changed
    if force_full or not previous_hashes:
        # Full rebuild
        if force_full:
            reason = "FORCE_FULL=1"
        else:
            reason = "no previous manifest"
        
        print(f"[INFO] Full rebuild ({reason}) - processing all {total_files} files")
        
        # Run full signature extraction
        result = subprocess.run(
            ["bash", gen_script, target_dir],
            capture_output=True, text=True,
            env={**os.environ, "OUTPUT_FILE": output_file, "VERBOSE": os.environ.get("VERBOSE", "0")}
        )
        
        if result.returncode != 0:
            print(f"Error: Full extraction failed", file=sys.stderr)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
            sys.exit(1)
        
        # Save manifest
        save_manifest(manifest_path, current_hashes)
        print(f"[OK] Full rebuild complete: {total_files} files processed")
        return
    
    # Incremental mode
    changed, added, removed = determine_changes(current_hashes, previous_hashes)
    files_to_process = changed | added
    
    if not files_to_process and not removed:
        print(f"[OK] No changes detected - workspace.json is up to date ({total_files} files)")
        save_manifest(manifest_path, current_hashes)
        return
    
    print(f"[INFO] Incremental update: {len(changed)} changed, {len(added)} added, {len(removed)} removed (of {total_files} total)")
    
    if verbose:
        for f in sorted(changed):
            print(f"  [CHANGED] {f}", file=sys.stderr)
        for f in sorted(added):
            print(f"  [ADDED]   {f}", file=sys.stderr)
        for f in sorted(removed):
            print(f"  [REMOVED] {f}", file=sys.stderr)
    
    # Load existing workspace.json
    existing_data = {}
    if os.path.exists(output_file):
        try:
            with open(output_file, 'r') as f:
                existing_data = json.load(f)
        except (json.JSONDecodeError, IOError):
            existing_data = {}
    
    # Extract signatures for changed/added files
    # Process each file individually (fast enough for incremental - typically few files)
    new_results = {}
    temp_output = output_file + ".tmp"
    
    for rel_path in sorted(files_to_process):
        full_path = os.path.join(target_dir, rel_path)
        if not os.path.exists(full_path):
            continue
        
        if verbose:
            print(f"  Processing: {rel_path}", file=sys.stderr)
        
        try:
            result = subprocess.run(
                ["bash", gen_script, full_path],
                capture_output=True, text=True, timeout=30,
                env={**os.environ, "OUTPUT_FILE": temp_output, "VERBOSE": "0"}
            )
            
            if result.returncode == 0 and os.path.exists(temp_output):
                with open(temp_output, 'r') as f:
                    file_data = json.load(f)
                
                # Extract functions (skip _metadata)
                for file_key, funcs in file_data.items():
                    if file_key == '_metadata':
                        continue
                    if isinstance(funcs, list):
                        # Use the normalized relative path
                        norm_key = normalize_path(rel_path)
                        new_results[norm_key] = funcs
                        break
        except (subprocess.TimeoutExpired, Exception) as e:
            print(f"  Warning: Failed to process {rel_path}: {e}", file=sys.stderr)
        finally:
            if os.path.exists(temp_output):
                os.unlink(temp_output)
    
    # Merge results
    merged = merge_results(existing_data, new_results, removed)
    
    # Update metadata
    merged['_metadata'] = existing_data.get('_metadata', {})
    merged['_metadata']['files_processed'] = total_files
    merged['_metadata']['version'] = '1.0.0'
    
    # Count actual timestamp
    from datetime import datetime, timezone
    merged['_metadata']['generated'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    
    # Write output
    with open(output_file, 'w') as f:
        json.dump(merged, f, indent=2)
    
    # Save manifest
    save_manifest(manifest_path, current_hashes)
    
    processed = len(new_results)
    print(f"[OK] Incremental update complete: {processed} files re-processed, {len(removed)} removed")
    print(f"[OK] Total functions in workspace.json: {sum(len(v) for k, v in merged.items() if k != '_metadata' and isinstance(v, list))}")


if __name__ == '__main__':
    main()
