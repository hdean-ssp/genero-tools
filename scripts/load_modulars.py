#!/usr/bin/env python3
"""
Load modulars.json (GLOBALS/IMPORT data) into workspace.db.

Creates tables:
    - file_dependencies: tracks GLOBALS and IMPORT relationships between files
    
Enables queries:
    - What files does this file depend on? (GLOBALS it includes, modules it imports)
    - What files depend on this globals file? (reverse lookup)

Usage:
    python3 load_modulars.py <modulars_json> <workspace_db>
"""

import json
import sqlite3
import sys
import os
from pathlib import Path


def create_schema(conn):
    """Create file_dependencies table."""
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS file_dependencies (
            id INTEGER PRIMARY KEY,
            file_path TEXT NOT NULL,
            dependency TEXT NOT NULL,
            dep_type TEXT NOT NULL,
            UNIQUE(file_path, dependency, dep_type)
        )
    ''')
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_filedeps_file ON file_dependencies(file_path)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_filedeps_dep ON file_dependencies(dependency)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_filedeps_type ON file_dependencies(dep_type)')
    
    conn.commit()


def load_modulars(modulars_path: str, db_path: str, verbose: bool = False):
    """Load modulars.json into workspace.db."""
    with open(modulars_path, 'r') as f:
        data = json.load(f)
    
    conn = sqlite3.connect(db_path)
    create_schema(conn)
    cursor = conn.cursor()
    
    # Clear existing data
    cursor.execute("DELETE FROM file_dependencies")
    
    globals_count = 0
    imports_count = 0
    
    for file_path, info in data.items():
        if file_path == '_metadata':
            continue
        if not isinstance(info, dict):
            continue
        
        # Normalize file path
        norm_path = file_path
        if not norm_path.startswith('./') and not norm_path.startswith('/'):
            norm_path = './' + norm_path
        
        # Store GLOBALS dependencies
        for glob_file in info.get('globals', []):
            try:
                cursor.execute(
                    "INSERT OR IGNORE INTO file_dependencies (file_path, dependency, dep_type) VALUES (?, ?, ?)",
                    (norm_path, glob_file, 'GLOBALS')
                )
                globals_count += 1
            except sqlite3.Error:
                pass
        
        # Store IMPORT dependencies
        for import_ref in info.get('imports', []):
            try:
                cursor.execute(
                    "INSERT OR IGNORE INTO file_dependencies (file_path, dependency, dep_type) VALUES (?, ?, ?)",
                    (norm_path, import_ref, 'IMPORT')
                )
                imports_count += 1
            except sqlite3.Error:
                pass
    
    conn.commit()
    conn.close()
    
    return {
        'globals': globals_count,
        'imports': imports_count
    }


def query_file_dependencies(db_path: str, file_path: str):
    """Find what a file depends on (its GLOBALS and IMPORT statements)."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Try exact match, then with/without ./ prefix
    cursor.execute("SELECT * FROM file_dependencies WHERE file_path = ? ORDER BY dep_type, dependency", (file_path,))
    rows = cursor.fetchall()
    
    if not rows:
        alt = './' + file_path.lstrip('./')
        cursor.execute("SELECT * FROM file_dependencies WHERE file_path = ? ORDER BY dep_type, dependency", (alt,))
        rows = cursor.fetchall()
    
    if not rows:
        alt = file_path.lstrip('./')
        cursor.execute("SELECT * FROM file_dependencies WHERE file_path = ? ORDER BY dep_type, dependency", (alt,))
        rows = cursor.fetchall()
    
    conn.close()
    return [dict(r) for r in rows]


def query_dependents(db_path: str, dependency: str):
    """Find what files depend on a given globals file or import."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Search for the dependency (partial match for flexibility)
    cursor.execute(
        "SELECT * FROM file_dependencies WHERE dependency LIKE ? ORDER BY file_path",
        (f"%{dependency}%",)
    )
    rows = cursor.fetchall()
    
    conn.close()
    return [dict(r) for r in rows]


def load_modulars_incremental(modulars_path: str, db_path: str, changes_path: str, verbose: bool = False):
    """Incrementally update file_dependencies for changed files only."""
    import json as json_mod
    
    with open(changes_path, 'r') as f:
        changes = json_mod.load(f)
    
    changed = set(changes.get('changed', []))
    added = set(changes.get('added', []))
    removed = set(changes.get('removed', []))
    
    affected_files = changed | added | removed
    if not affected_files:
        print("[OK] No file dependency changes needed")
        return {'globals': 0, 'imports': 0}
    
    with open(modulars_path, 'r') as f:
        data = json.load(f)
    
    conn = sqlite3.connect(db_path)
    create_schema(conn)
    cursor = conn.cursor()
    
    # Normalize affected paths
    def normalize(p):
        p = os.path.normpath(p)
        if not p.startswith('./') and not p.startswith('/'):
            p = './' + p
        return p
    
    affected_normalized = {normalize(f) for f in affected_files}
    
    # Delete existing entries for affected files
    for norm_path in affected_normalized:
        cursor.execute("DELETE FROM file_dependencies WHERE file_path = ?", (norm_path,))
        # Also try without prefix
        bare = norm_path.lstrip('./')
        cursor.execute("DELETE FROM file_dependencies WHERE file_path = ?", (bare,))
    
    # Re-insert for changed/added files (not removed)
    globals_count = 0
    imports_count = 0
    
    files_to_insert = changed | added
    for rel_path in files_to_insert:
        norm_path = normalize(rel_path)
        
        # Find this file's data in modulars.json
        info = data.get(norm_path) or data.get(rel_path) or data.get('./' + rel_path.lstrip('./'))
        if not info or not isinstance(info, dict):
            continue
        
        for glob_file in info.get('globals', []):
            try:
                cursor.execute(
                    "INSERT OR IGNORE INTO file_dependencies (file_path, dependency, dep_type) VALUES (?, ?, ?)",
                    (norm_path, glob_file, 'GLOBALS')
                )
                globals_count += 1
            except sqlite3.Error:
                pass
        
        for import_ref in info.get('imports', []):
            try:
                cursor.execute(
                    "INSERT OR IGNORE INTO file_dependencies (file_path, dependency, dep_type) VALUES (?, ?, ?)",
                    (norm_path, import_ref, 'IMPORT')
                )
                imports_count += 1
            except sqlite3.Error:
                pass
    
    conn.commit()
    conn.close()
    
    print(f"[OK] Incremental update: {globals_count} GLOBALS and {imports_count} IMPORT dependencies ({len(files_to_insert)} files updated, {len(removed)} removed)")
    return {'globals': globals_count, 'imports': imports_count}


def main():
    if len(sys.argv) < 3:
        print("Usage: load_modulars.py <command> <args...>", file=sys.stderr)
        print("", file=sys.stderr)
        print("Commands:", file=sys.stderr)
        print("  load <modulars_json> <workspace_db>                Load modulars into DB", file=sys.stderr)
        print("  load-incremental <modulars_json> <workspace_db> <changes_file>  Incremental update", file=sys.stderr)
        print("  deps <workspace_db> <file_path>                    Query file dependencies", file=sys.stderr)
        print("  dependents <workspace_db> <dep_name>               Query what depends on a file", file=sys.stderr)
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "load":
        if len(sys.argv) < 4:
            print("Usage: load_modulars.py load <modulars_json> <workspace_db>", file=sys.stderr)
            sys.exit(1)
        
        modulars_path = sys.argv[2]
        db_path = sys.argv[3]
        verbose = os.environ.get('VERBOSE', '0') == '1'
        
        if not Path(modulars_path).exists():
            print(f"Error: {modulars_path} not found", file=sys.stderr)
            sys.exit(1)
        if not Path(db_path).exists():
            print(f"Error: {db_path} not found", file=sys.stderr)
            sys.exit(1)
        
        stats = load_modulars(modulars_path, db_path, verbose)
        print(f"[OK] Loaded {stats['globals']} GLOBALS and {stats['imports']} IMPORT dependencies")
    
    elif command == "load-incremental":
        if len(sys.argv) < 5:
            print("Usage: load_modulars.py load-incremental <modulars_json> <workspace_db> <changes_file>", file=sys.stderr)
            sys.exit(1)
        
        modulars_path = sys.argv[2]
        db_path = sys.argv[3]
        changes_path = sys.argv[4]
        verbose = os.environ.get('VERBOSE', '0') == '1'
        
        if not Path(modulars_path).exists():
            print(f"Error: {modulars_path} not found", file=sys.stderr)
            sys.exit(1)
        if not Path(db_path).exists():
            print(f"Error: {db_path} not found", file=sys.stderr)
            sys.exit(1)
        if not Path(changes_path).exists():
            print(f"Error: {changes_path} not found", file=sys.stderr)
            sys.exit(1)
        
        load_modulars_incremental(modulars_path, db_path, changes_path, verbose)
    
    elif command == "deps":
        if len(sys.argv) < 4:
            print("Usage: load_modulars.py deps <workspace_db> <file_path>", file=sys.stderr)
            sys.exit(1)
        
        db_path = sys.argv[2]
        file_path = sys.argv[3]
        results = query_file_dependencies(db_path, file_path)
        print(json.dumps(results, indent=2))
    
    elif command == "dependents":
        if len(sys.argv) < 4:
            print("Usage: load_modulars.py dependents <workspace_db> <dep_name>", file=sys.stderr)
            sys.exit(1)
        
        db_path = sys.argv[2]
        dep_name = sys.argv[3]
        results = query_dependents(db_path, dep_name)
        print(json.dumps(results, indent=2))
    
    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
