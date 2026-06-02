#!/usr/bin/env python3
"""
Extract code quality metrics from .4gl source files and store in workspace.db.

This script bridges metrics_extractor.py and metrics_db.py:
1. Finds all .4gl files in the target directory
2. Extracts metrics for each function using MetricsExtractor
3. Looks up corresponding function_id in workspace.db
4. Stores metrics in the function_metrics table

Usage:
    python3 extract_and_store_metrics.py <target_directory> <workspace_db>
"""

import sys
import os
import sqlite3
from pathlib import Path

# Add scripts directory to path for imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from metrics_extractor import MetricsExtractor
from metrics_db import MetricsDatabase


def find_4gl_files(target_dir):
    """Find all .4gl files in the target directory."""
    target = Path(target_dir)
    return sorted(target.rglob("*.4gl"))


def build_function_index(cursor):
    """Build lookup indexes from the database for fast matching.
    
    Returns:
        file_functions: {file_path: {func_name: function_id}}
        name_to_ids: {func_name: [function_id, ...]}
    """
    cursor.execute("SELECT id, name, file_path FROM functions")
    rows = cursor.fetchall()
    
    file_functions = {}  # {file_path: {func_name: func_id}}
    name_to_ids = {}     # {func_name: [func_id, ...]}
    
    for row in rows:
        func_id, name, file_path = row
        
        # Index by file_path
        if file_path not in file_functions:
            file_functions[file_path] = {}
        file_functions[file_path][name] = func_id
        
        # Index by name
        if name not in name_to_ids:
            name_to_ids[name] = []
        name_to_ids[name].append(func_id)
    
    return file_functions, name_to_ids


def find_file_in_index(file_functions, rel_path):
    """Find a file's function map in the index, trying multiple path variants."""
    # Try exact match
    if rel_path in file_functions:
        return file_functions[rel_path]
    
    # Try with ./ prefix
    with_prefix = './' + rel_path.lstrip('./')
    if with_prefix in file_functions:
        return file_functions[with_prefix]
    
    # Try without ./ prefix
    without_prefix = rel_path.lstrip('./')
    if without_prefix in file_functions:
        return file_functions[without_prefix]
    
    # Try matching just the filename portion against all paths
    basename = os.path.basename(rel_path)
    # For paths like "lib/eltrace.4gl", try matching the tail
    for db_path, funcs in file_functions.items():
        if db_path.endswith('/' + rel_path.lstrip('./')) or db_path.endswith('/' + basename):
            # Check if the relative portion matches
            db_stripped = db_path.lstrip('./')
            rel_stripped = rel_path.lstrip('./')
            if db_stripped == rel_stripped or db_stripped.endswith('/' + rel_stripped):
                return funcs
    
    return None


def main():
    if len(sys.argv) < 3:
        print("Usage: extract_and_store_metrics.py <target_directory> <workspace_db>", file=sys.stderr)
        sys.exit(1)
    
    target_dir = sys.argv[1]
    db_path = sys.argv[2]
    verbose = os.environ.get('VERBOSE', '0') == '1'
    
    # Validate inputs
    if not os.path.isdir(target_dir):
        print("Error: Target directory not found: {}".format(target_dir), file=sys.stderr)
        sys.exit(1)
    
    if not os.path.isfile(db_path):
        print("Error: Database not found: {}".format(db_path), file=sys.stderr)
        sys.exit(1)
    
    # Initialize
    extractor = MetricsExtractor()
    metrics_db = MetricsDatabase(db_path)
    metrics_db.connect()
    metrics_db.create_schema()
    
    # Build function index from DB for fast lookups
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    file_functions, name_to_ids = build_function_index(cursor)
    
    if verbose:
        total_in_db = sum(len(v) for v in file_functions.values())
        print("  DB contains {} functions across {} files".format(total_in_db, len(file_functions)), file=sys.stderr)
    
    # Find all .4gl files
    files = find_4gl_files(target_dir)
    
    if verbose:
        print("  Extracting metrics from {} .4gl files...".format(len(files)), file=sys.stderr)
    
    # Stats
    total_functions = 0
    metrics_stored = 0
    metrics_failed_no_match = 0
    metrics_failed_error = 0
    files_processed = 0
    files_failed = 0
    files_no_db_match = 0
    
    for file_path in files:
        file_str = str(file_path)
        
        # Compute relative path
        try:
            rel_path = os.path.relpath(file_str, target_dir)
        except ValueError:
            rel_path = file_str
        
        # Normalize: ensure ./ prefix
        norm_path = rel_path
        if not norm_path.startswith('./') and not norm_path.startswith('/'):
            norm_path = './' + norm_path
        
        # Find this file's functions in the DB index
        db_funcs = find_file_in_index(file_functions, norm_path)
        
        if db_funcs is None:
            files_no_db_match += 1
            if verbose:
                print("  No DB match for file: {}".format(norm_path), file=sys.stderr)
            continue
        
        try:
            # Extract metrics for all functions in this file
            file_metrics = extractor.extract_file_metrics(file_str)
            files_processed += 1
            
            for func_metrics in file_metrics:
                total_functions += 1
                
                # Look up function_id from the file's function map
                func_id = db_funcs.get(func_metrics.name)
                
                # If not found by exact name, try case-insensitive
                if func_id is None:
                    for db_name, db_id in db_funcs.items():
                        if db_name.lower() == func_metrics.name.lower():
                            func_id = db_id
                            break
                
                # Last resort: name-only match (unique names only)
                if func_id is None:
                    candidates = name_to_ids.get(func_metrics.name, [])
                    if len(candidates) == 1:
                        func_id = candidates[0]
                
                if func_id is None:
                    metrics_failed_no_match += 1
                    if verbose:
                        print("  No match: {} in {}".format(func_metrics.name, norm_path), file=sys.stderr)
                    continue
                
                # Store metrics
                try:
                    metrics_db.store_metrics(func_metrics, func_id)
                    metrics_stored += 1
                except Exception as e:
                    metrics_failed_error += 1
                    if verbose:
                        print("  Store error: {} - {}".format(func_metrics.name, e), file=sys.stderr)
        
        except Exception as e:
            files_failed += 1
            if verbose:
                print("  File error: {} - {}".format(file_str, e), file=sys.stderr)
    
    # Close connections
    conn.close()
    metrics_db.disconnect()
    
    # Report results
    metrics_failed = metrics_failed_no_match + metrics_failed_error
    print("[OK] Metrics extraction complete")
    print("[OK] Files processed: {} ({} failed, {} no DB match)".format(
        files_processed, files_failed, files_no_db_match))
    print("[OK] Functions analyzed: {}".format(total_functions))
    print("[OK] Metrics stored: {}".format(metrics_stored))
    if metrics_failed > 0:
        print("[WARN] Metrics failed: {} ({} no match, {} errors)".format(
            metrics_failed, metrics_failed_no_match, metrics_failed_error))


if __name__ == '__main__':
    main()
