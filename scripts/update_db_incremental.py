#!/usr/bin/env python3
"""
Incremental database update - update workspace.db for only changed files.

Instead of dropping and recreating the entire database, this script:
1. Deletes all rows (functions, parameters, returns, calls, variables, metrics)
   for files that changed or were removed
2. Inserts new data for changed/added files from workspace.json
3. Leaves unchanged file data intact

Usage:
    python3 update_db_incremental.py <workspace_json> <workspace_db> <changed_files_json>
    
    changed_files_json format: {"changed": ["file1.4gl", ...], "added": [...], "removed": [...]}
"""

import json
import sqlite3
import sys
import os
from pathlib import Path


def normalize_path(path):
    """Normalize path to ./ prefix format."""
    path = os.path.normpath(path)
    if not path.startswith('./') and not path.startswith('/'):
        path = './' + path
    return path


def delete_file_data(conn, file_path):
    """Delete all data associated with a file path from the database."""
    cursor = conn.cursor()
    
    # Find the file ID
    cursor.execute("SELECT id FROM files WHERE path = ?", (file_path,))
    row = cursor.fetchone()
    if not row:
        # Try without ./ prefix
        alt = file_path.lstrip('./')
        cursor.execute("SELECT id FROM files WHERE path = ?", (alt,))
        row = cursor.fetchone()
    if not row:
        # Try with ./ prefix
        alt = './' + file_path.lstrip('./')
        cursor.execute("SELECT id FROM files WHERE path = ?", (alt,))
        row = cursor.fetchone()
    
    if not row:
        return 0  # File not in DB
    
    file_id = row[0]
    
    # Get all function IDs for this file
    cursor.execute("SELECT id FROM functions WHERE file_id = ?", (file_id,))
    func_ids = [r[0] for r in cursor.fetchall()]
    
    if func_ids:
        placeholders = ','.join('?' * len(func_ids))
        
        # Delete related data
        cursor.execute("DELETE FROM parameters WHERE function_id IN ({})".format(placeholders), func_ids)
        cursor.execute("DELETE FROM returns WHERE function_id IN ({})".format(placeholders), func_ids)
        cursor.execute("DELETE FROM calls WHERE function_id IN ({})".format(placeholders), func_ids)
        cursor.execute("DELETE FROM variables WHERE function_id IN ({})".format(placeholders), func_ids)
        
        # Delete metrics if table exists
        try:
            cursor.execute("DELETE FROM function_metrics WHERE function_id IN ({})".format(placeholders), func_ids)
        except sqlite3.OperationalError:
            pass  # Table might not exist yet
        
        # Delete functions
        cursor.execute("DELETE FROM functions WHERE file_id = ?", (file_id,))
    
    # Delete the file entry
    cursor.execute("DELETE FROM files WHERE id = ?", (file_id,))
    
    return len(func_ids)


def insert_file_data(conn, file_path, functions, workspace_data):
    """Insert data for a file from workspace.json into the database."""
    cursor = conn.cursor()
    
    # Determine file type
    file_type = "L4GLS" if "L4GLS" in file_path else ("U4GLS" if "U4GLS" in file_path else "4GLS")
    
    # Insert file
    cursor.execute("INSERT INTO files (path, type) VALUES (?, ?)", (file_path, file_type))
    file_id = cursor.lastrowid
    
    for func in functions:
        # Insert function
        cursor.execute(
            """INSERT INTO functions (file_id, name, line_start, line_end, signature, file_path, body_hash, body_loc)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (file_id, func['name'], func['line']['start'], func['line']['end'],
             func['signature'], file_path, func.get('body_hash'), func.get('body_loc'))
        )
        func_id = cursor.lastrowid
        
        # Insert parameters
        for param in func.get('parameters', []):
            param_name = param.get('name')
            if param_name and param_name.strip():
                cursor.execute(
                    "INSERT INTO parameters (function_id, name, type) VALUES (?, ?, ?)",
                    (func_id, param_name.strip(), param.get('type', ''))
                )
        
        # Insert returns
        for ret in func.get('returns', []):
            cursor.execute(
                "INSERT INTO returns (function_id, name, type) VALUES (?, ?, ?)",
                (func_id, ret['name'], ret['type'])
            )
        
        # Insert calls
        for call in func.get('calls', []):
            cursor.execute(
                "INSERT INTO calls (function_id, called_function_name, line_number) VALUES (?, ?, ?)",
                (func_id, call['name'], call['line'])
            )
        
        # Insert variables
        for var in func.get('variables', []):
            cursor.execute(
                "INSERT INTO variables (function_id, name, type) VALUES (?, ?, ?)",
                (func_id, var['name'], var['type'])
            )
    
    return len(functions)


def main():
    if len(sys.argv) < 4:
        print("Usage: update_db_incremental.py <workspace_json> <workspace_db> <changed_files_json>", file=sys.stderr)
        sys.exit(1)
    
    workspace_json_path = sys.argv[1]
    db_path = sys.argv[2]
    changed_files_path = sys.argv[3]
    verbose = os.environ.get('VERBOSE', '0') == '1'
    
    # Load changed files list
    with open(changed_files_path, 'r') as f:
        changes = json.load(f)
    
    changed = set(changes.get('changed', []))
    added = set(changes.get('added', []))
    removed = set(changes.get('removed', []))
    
    files_to_update = changed | added
    files_to_remove = removed
    
    if not files_to_update and not files_to_remove:
        print("[OK] No changes to apply to database")
        return
    
    # Load workspace.json for new data
    with open(workspace_json_path, 'r') as f:
        workspace = json.load(f)
    
    # Connect to existing DB
    conn = sqlite3.connect(db_path)
    
    # Delete data for changed and removed files
    deleted_funcs = 0
    for file_path in files_to_update | files_to_remove:
        norm = normalize_path(file_path)
        deleted_funcs += delete_file_data(conn, norm)
    
    # Insert new data for changed/added files
    inserted_funcs = 0
    for file_path in sorted(files_to_update):
        norm = normalize_path(file_path)
        functions = workspace.get(norm, [])
        if not functions:
            # Try without prefix
            alt = file_path.lstrip('./')
            functions = workspace.get('./' + alt, workspace.get(alt, []))
        
        if isinstance(functions, list) and functions:
            inserted_funcs += insert_file_data(conn, norm, functions, workspace)
    
    conn.commit()
    conn.close()
    
    print("[OK] Incremental DB update: deleted {} functions, inserted {} functions ({} files updated, {} removed)".format(
        deleted_funcs, inserted_funcs, len(files_to_update), len(files_to_remove)))


if __name__ == '__main__':
    main()
