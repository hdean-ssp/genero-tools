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


def find_4gl_files(target_dir: str):
    """Find all .4gl files in the target directory."""
    target = Path(target_dir)
    return sorted(target.rglob("*.4gl"))


def normalize_path(path: str, target_dir: str) -> str:
    """Normalize a file path to match workspace.db file_path format (./ prefix)."""
    # Make path relative to target directory
    try:
        rel = os.path.relpath(path, target_dir)
    except ValueError:
        rel = path
    
    # Ensure ./ prefix
    if not rel.startswith('./') and not rel.startswith('/'):
        rel = './' + rel
    
    return rel


def get_function_id(cursor, func_name: str, file_path: str):
    """Look up function_id in workspace.db by name and file path."""
    # Try exact match first
    cursor.execute(
        'SELECT id FROM functions WHERE name = ? AND file_path = ?',
        (func_name, file_path)
    )
    row = cursor.fetchone()
    if row:
        return row[0]
    
    # Try without ./ prefix
    alt_path = file_path.lstrip('./')
    cursor.execute(
        'SELECT id FROM functions WHERE name = ? AND file_path = ?',
        (func_name, alt_path)
    )
    row = cursor.fetchone()
    if row:
        return row[0]
    
    # Try with ./ prefix
    alt_path = './' + file_path.lstrip('./')
    cursor.execute(
        'SELECT id FROM functions WHERE name = ? AND file_path = ?',
        (func_name, alt_path)
    )
    row = cursor.fetchone()
    if row:
        return row[0]
    
    # Try name-only match (if only one function with that name)
    cursor.execute(
        'SELECT id FROM functions WHERE name = ?',
        (func_name,)
    )
    rows = cursor.fetchall()
    if len(rows) == 1:
        return rows[0][0]
    
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
        print(f"Error: Target directory not found: {target_dir}", file=sys.stderr)
        sys.exit(1)
    
    if not os.path.isfile(db_path):
        print(f"Error: Database not found: {db_path}", file=sys.stderr)
        sys.exit(1)
    
    # Initialize
    extractor = MetricsExtractor()
    metrics_db = MetricsDatabase(db_path)
    metrics_db.connect()
    metrics_db.create_schema()
    
    # Also open a direct connection for function_id lookups
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Find all .4gl files
    files = find_4gl_files(target_dir)
    
    if verbose:
        print(f"Extracting metrics from {len(files)} .4gl files...", file=sys.stderr)
    
    # Stats
    total_functions = 0
    metrics_stored = 0
    metrics_failed = 0
    files_processed = 0
    files_failed = 0
    
    for file_path in files:
        file_str = str(file_path)
        rel_path = normalize_path(file_str, target_dir)
        
        try:
            # Extract metrics for all functions in this file
            file_metrics = extractor.extract_file_metrics(file_str)
            files_processed += 1
            
            for func_metrics in file_metrics:
                total_functions += 1
                
                # Look up function_id
                func_id = get_function_id(cursor, func_metrics.name, rel_path)
                
                if func_id is None:
                    if verbose:
                        print(f"  Warning: Could not find function_id for {func_metrics.name} in {rel_path}", file=sys.stderr)
                    metrics_failed += 1
                    continue
                
                # Store metrics
                try:
                    metrics_db.store_metrics(func_metrics, func_id)
                    metrics_stored += 1
                except Exception as e:
                    if verbose:
                        print(f"  Error storing metrics for {func_metrics.name}: {e}", file=sys.stderr)
                    metrics_failed += 1
        
        except Exception as e:
            files_failed += 1
            if verbose:
                print(f"  Error processing {file_str}: {e}", file=sys.stderr)
    
    # Close connections
    conn.close()
    metrics_db.disconnect()
    
    # Report results
    print(f"[OK] Metrics extraction complete")
    print(f"[OK] Files processed: {files_processed} ({files_failed} failed)")
    print(f"[OK] Functions analyzed: {total_functions}")
    print(f"[OK] Metrics stored: {metrics_stored}")
    if metrics_failed > 0:
        print(f"[WARN] Metrics failed: {metrics_failed} (function not found in DB or storage error)")


if __name__ == '__main__':
    main()
