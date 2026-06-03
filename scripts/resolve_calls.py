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


def resolve_calls_incremental(db_path: str, changes_file: str, verbose: bool = False):
    """Resolve calls only for functions in changed files.
    
    Strategy:
    1. Clear resolved_function_id for calls FROM changed files (their calls may have changed)
    2. Clear resolved_function_id for calls TO functions in changed files (targets may have moved)
    3. Re-resolve only those affected calls
    """
    import json
    
    with open(changes_file, 'r') as f:
        changes = json.load(f)
    
    changed = set(changes.get('changed', []))
    added = set(changes.get('added', []))
    removed = set(changes.get('removed', []))
    
    affected_files = changed | added
    if not affected_files and not removed:
        return {'total_calls': 0, 'resolved': 0, 'ambiguous': 0, 'not_found': 0}
    
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
    
    # Normalize paths for matching
    def normalize(p):
        import os
        p = os.path.normpath(p)
        if not p.startswith('./') and not p.startswith('/'):
            p = './' + p
        return p
    
    affected_normalized = {normalize(f) for f in affected_files}
    
    # Find function IDs in affected files
    placeholders = ','.join('?' * len(affected_normalized))
    cursor.execute(
        f"SELECT id, file_path FROM functions WHERE file_path IN ({placeholders})",
        list(affected_normalized)
    )
    affected_func_ids = [row['id'] for row in cursor.fetchall()]
    
    if not affected_func_ids:
        conn.close()
        return {'total_calls': 0, 'resolved': 0, 'ambiguous': 0, 'not_found': 0}
    
    # Clear resolution for calls FROM affected functions
    id_placeholders = ','.join('?' * len(affected_func_ids))
    cursor.execute(
        f"UPDATE calls SET resolved_function_id = NULL WHERE function_id IN ({id_placeholders})",
        affected_func_ids
    )
    
    # Also clear resolution for calls TO functions that were in affected files
    # (their function IDs may have changed during the DB update)
    cursor.execute(
        f"UPDATE calls SET resolved_function_id = NULL WHERE resolved_function_id IN ({id_placeholders})",
        affected_func_ids
    )
    
    conn.commit()
    conn.close()
    
    # Now run normal resolution which only resolves NULL entries
    return resolve_calls(db_path, verbose)


def main():
    if len(sys.argv) < 2:
        print("Usage: resolve_calls.py <workspace_db> [--changes <changes_file>]", file=sys.stderr)
        sys.exit(1)
    
    db_path = sys.argv[1]
    verbose = os.environ.get('VERBOSE', '0') == '1'
    changes_file = None
    
    # Parse --changes argument
    if '--changes' in sys.argv:
        idx = sys.argv.index('--changes')
        if idx + 1 < len(sys.argv):
            changes_file = sys.argv[idx + 1]
    
    if not Path(db_path).exists():
        print(f"Error: Database not found: {db_path}", file=sys.stderr)
        sys.exit(1)
    
    if changes_file:
        # Incremental: only re-resolve calls for changed files
        stats = resolve_calls_incremental(db_path, changes_file, verbose)
    else:
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
