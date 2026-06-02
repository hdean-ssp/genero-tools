#!/usr/bin/env python3
"""
Resolve cross-file call references in workspace.db.

After signature extraction stores calls as (function_id, called_function_name),
this script resolves called_function_name to an actual function_id in the DB,
enabling true cross-file dependency graphs.

Usage:
    python3 resolve_calls.py <workspace_db>

Adds/updates:
    - calls.resolved_function_id: FK to functions.id of the callee
    - idx_calls_resolved: index on resolved_function_id
"""

import sqlite3
import sys
import os
from pathlib import Path


def resolve_calls(db_path: str, verbose: bool = False):
    """Resolve called_function_name to function IDs in the calls table."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Add resolved_function_id column if not exists
    cursor.execute("PRAGMA table_info(calls)")
    columns = {row['name'] for row in cursor.fetchall()}
    
    if 'resolved_function_id' not in columns:
        cursor.execute("ALTER TABLE calls ADD COLUMN resolved_function_id INTEGER")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_calls_resolved ON calls(resolved_function_id)")
        conn.commit()
    
    # Build a lookup of function names to IDs
    # For functions with unique names, map directly
    # For duplicates, we'll need caller context to disambiguate
    cursor.execute("SELECT id, name, file_path FROM functions")
    all_functions = cursor.fetchall()
    
    # Group functions by name
    name_to_ids = {}
    for row in all_functions:
        name = row['name']
        if name not in name_to_ids:
            name_to_ids[name] = []
        name_to_ids[name].append({'id': row['id'], 'file_path': row['file_path']})
    
    # Get all unresolved calls
    cursor.execute("""
        SELECT c.id, c.function_id, c.called_function_name, f.file_path as caller_file
        FROM calls c
        JOIN functions f ON c.function_id = f.id
        WHERE c.resolved_function_id IS NULL
    """)
    unresolved_calls = cursor.fetchall()
    
    if verbose:
        print(f"  Resolving {len(unresolved_calls)} call references...", file=sys.stderr)
    
    resolved_count = 0
    ambiguous_count = 0
    not_found_count = 0
    
    for call in unresolved_calls:
        called_name = call['called_function_name']
        caller_file = call['caller_file']
        
        if called_name not in name_to_ids:
            not_found_count += 1
            continue
        
        candidates = name_to_ids[called_name]
        
        if len(candidates) == 1:
            # Unique function name - resolve directly
            resolved_id = candidates[0]['id']
            cursor.execute(
                "UPDATE calls SET resolved_function_id = ? WHERE id = ?",
                (resolved_id, call['id'])
            )
            resolved_count += 1
        else:
            # Multiple functions with same name - try to disambiguate
            # Strategy 1: prefer function in the same file
            same_file = [c for c in candidates if c['file_path'] == caller_file]
            if len(same_file) == 1:
                resolved_id = same_file[0]['id']
                cursor.execute(
                    "UPDATE calls SET resolved_function_id = ? WHERE id = ?",
                    (resolved_id, call['id'])
                )
                resolved_count += 1
            else:
                # Strategy 2: prefer function in same module (future enhancement)
                # For now, pick the first one and count as ambiguous
                resolved_id = candidates[0]['id']
                cursor.execute(
                    "UPDATE calls SET resolved_function_id = ? WHERE id = ?",
                    (resolved_id, call['id'])
                )
                resolved_count += 1
                ambiguous_count += 1
    
    conn.commit()
    conn.close()
    
    return {
        'total_calls': len(unresolved_calls),
        'resolved': resolved_count,
        'ambiguous': ambiguous_count,
        'not_found': not_found_count
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: resolve_calls.py <workspace_db>", file=sys.stderr)
        sys.exit(1)
    
    db_path = sys.argv[1]
    verbose = os.environ.get('VERBOSE', '0') == '1'
    
    if not Path(db_path).exists():
        print(f"Error: Database not found: {db_path}", file=sys.stderr)
        sys.exit(1)
    
    stats = resolve_calls(db_path, verbose)
    
    print(f"[OK] Call resolution complete")
    print(f"[OK] Total calls: {stats['total_calls']}")
    print(f"[OK] Resolved: {stats['resolved']}")
    if stats['ambiguous'] > 0:
        print(f"[WARN] Ambiguous (multiple targets): {stats['ambiguous']}")
    if stats['not_found'] > 0:
        print(f"[INFO] External/unresolved (callee not in codebase): {stats['not_found']}")


if __name__ == '__main__':
    main()
