#!/usr/bin/env python3
"""Relationship query algorithms for complex call graph traversals."""

import sqlite3
from typing import List, Dict, Any, Optional, Set, Tuple
from collections import deque


def find_dependents_in_module(modules_db: str,
                             signatures_db: str,
                             module_name: str,
                             function_name: str) -> Optional[List[Dict[str, Any]]]:
    """Find all functions in a module that call a specific function.
    
    Args:
        modules_db: Path to modules.db
        signatures_db: Path to workspace.db
        module_name: Name of the module
        function_name: Name of the function to find callers for
    
    Returns:
        List of function objects that call the function, or None if module/function not found
    
    Raises:
        ValueError: If module or function not found
    """
    # Validate module exists
    conn_mod = sqlite3.connect(modules_db)
    conn_mod.row_factory = sqlite3.Row
    c_mod = conn_mod.cursor()
    
    c_mod.execute('SELECT id FROM modules WHERE name = ?', (module_name,))
    module_row = c_mod.fetchone()
    
    if not module_row:
        conn_mod.close()
        raise ValueError(f'Module not found: {module_name}')
    
    module_id = module_row['id']
    
    # Get all files in module
    c_mod.execute('SELECT file_name FROM module_files WHERE module_id = ?', (module_id,))
    files = [row['file_name'] for row in c_mod.fetchall()]
    conn_mod.close()
    
    if not files:
        return []
    
    # Query signatures database
    conn_sig = sqlite3.connect(signatures_db)
    conn_sig.row_factory = sqlite3.Row
    c_sig = conn_sig.cursor()
    
    # Get all functions in module files
    module_functions = []
    for file_name in files:
        c_sig.execute('''SELECT f.id, f.name, f.signature, fi.path, f.line_start, f.line_end
                         FROM functions f
                         JOIN files fi ON f.file_id = fi.id
                         WHERE fi.path LIKE ? OR fi.path LIKE ?
                         ORDER BY f.name''',
                     (f'%/{file_name}', f'%\\{file_name}'))
        module_functions.extend([dict(row) for row in c_sig.fetchall()])
    
    # Find which functions call the target function
    dependents = []
    for func in module_functions:
        c_sig.execute('''SELECT COUNT(*) as count FROM calls
                         WHERE caller_id = ? AND callee_name = ?''',
                     (func['id'], function_name))
        count = c_sig.fetchone()['count']
        
        if count > 0:
            dependents.append(func)
    
    conn_sig.close()
    
    # Sort by name
    dependents.sort(key=lambda x: x['name'])
    
    return dependents


def find_call_chain(signatures_db: str,
                   source_function: str,
                   target_function: str,
                   max_depth: int = 5) -> List[List[str]]:
    """Find all call paths from one function to another using BFS.
    
    Args:
        signatures_db: Path to workspace.db
        source_function: Name of source function
        target_function: Name of target function
        max_depth: Maximum depth to search (default 5, max 20)
    
    Returns:
        List of call paths (each path is a list of function names)
    
    Raises:
        ValueError: If source or target function not found
    """
    # Validate max_depth
    max_depth = min(max_depth, 20)
    max_depth = max(max_depth, 1)
    
    conn = sqlite3.connect(signatures_db)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Verify both functions exist
    c.execute('SELECT id FROM functions WHERE name = ?', (source_function,))
    if not c.fetchone():
        conn.close()
        raise ValueError(f'Source function not found: {source_function}')
    
    c.execute('SELECT id FROM functions WHERE name = ?', (target_function,))
    if not c.fetchone():
        conn.close()
        raise ValueError(f'Target function not found: {target_function}')
    
    # Build call graph
    c.execute('SELECT caller_id, callee_name FROM calls')
    call_graph = {}
    for row in c.fetchall():
        caller_id = row['caller_id']
        callee_name = row['callee_name']
        
        if caller_id not in call_graph:
            call_graph[caller_id] = []
        call_graph[caller_id].append(callee_name)
    
    # Get function ID to name mapping
    c.execute('SELECT id, name FROM functions')
    id_to_name = {row['id']: row['name'] for row in c.fetchall()}
    
    # Get name to ID mapping
    c.execute('SELECT id, name FROM functions')
    name_to_id = {row['name']: row['id'] for row in c.fetchall()}
    
    conn.close()
    
    # BFS to find all paths
    paths = []
    queue = deque([(source_function, [source_function], 0)])
    visited_states = set()
    
    while queue:
        current_func, path, depth = queue.popleft()
        
        # Check if we reached target
        if current_func == target_function:
            paths.append(path)
            continue
        
        # Check depth limit
        if depth >= max_depth:
            continue
        
        # Get current function ID
        current_id = name_to_id.get(current_func)
        if current_id is None:
            continue
        
        # Get callees
        callees = call_graph.get(current_id, [])
        
        for callee in callees:
            # Avoid cycles
            if callee not in path:
                state = (callee, tuple(path))
                if state not in visited_states:
                    visited_states.add(state)
                    queue.append((callee, path + [callee], depth + 1))
    
    return paths


def find_common_callers(signatures_db: str,
                       function_names: List[str]) -> List[Dict[str, Any]]:
    """Find all functions that call all specified functions.
    
    Args:
        signatures_db: Path to workspace.db
        function_names: List of function names (must have at least 2)
    
    Returns:
        List of function objects that call all specified functions
    
    Raises:
        ValueError: If fewer than 2 functions specified or any function not found
    """
    if len(function_names) < 2:
        raise ValueError('At least 2 functions must be specified')
    
    conn = sqlite3.connect(signatures_db)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Verify all functions exist
    for func_name in function_names:
        c.execute('SELECT id FROM functions WHERE name = ?', (func_name,))
        if not c.fetchone():
            conn.close()
            raise ValueError(f'Function not found: {func_name}')
    
    # Get callers for first function
    c.execute('''SELECT DISTINCT caller_id FROM calls WHERE callee_name = ?''',
             (function_names[0],))
    common_callers = set(row['caller_id'] for row in c.fetchall())
    
    # Intersect with callers of remaining functions
    for func_name in function_names[1:]:
        c.execute('''SELECT DISTINCT caller_id FROM calls WHERE callee_name = ?''',
                 (func_name,))
        callers = set(row['caller_id'] for row in c.fetchall())
        common_callers = common_callers.intersection(callers)
    
    # Get function details for common callers
    if not common_callers:
        conn.close()
        return []
    
    placeholders = ','.join('?' * len(common_callers))
    c.execute(f'''SELECT f.id, f.name, f.signature, fi.path, f.line_start, f.line_end
                  FROM functions f
                  JOIN files fi ON f.file_id = fi.id
                  WHERE f.id IN ({placeholders})
                  ORDER BY f.name''',
             list(common_callers))
    
    results = [dict(row) for row in c.fetchall()]
    conn.close()
    
    return results


def main():
    """Command-line interface for relationship queries."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: relationship_queries.py <command> [args...]", file=sys.stderr)
        print("Commands:", file=sys.stderr)
        print("  find-dependents-in-module <modules_db> <signatures_db> <module> <function>", file=sys.stderr)
        print("  find-call-chain <signatures_db> <source> <target> [max_depth]", file=sys.stderr)
        print("  find-common-callers <signatures_db> <function1> <function2> [function3...]", file=sys.stderr)
        sys.exit(1)
    
    command = sys.argv[1]
    
    try:
        if command == 'find-dependents-in-module':
            if len(sys.argv) < 6:
                print("Error: find-dependents-in-module requires 4 arguments", file=sys.stderr)
                sys.exit(1)
            
            modules_db = sys.argv[2]
            signatures_db = sys.argv[3]
            module_name = sys.argv[4]
            function_name = sys.argv[5]
            
            result = find_dependents_in_module(modules_db, signatures_db, module_name, function_name)
            
            import json
            print(json.dumps(result, indent=2))
        
        elif command == 'find-call-chain':
            if len(sys.argv) < 5:
                print("Error: find-call-chain requires at least 3 arguments", file=sys.stderr)
                sys.exit(1)
            
            signatures_db = sys.argv[2]
            source_function = sys.argv[3]
            target_function = sys.argv[4]
            max_depth = int(sys.argv[5]) if len(sys.argv) > 5 else 5
            
            result = find_call_chain(signatures_db, source_function, target_function, max_depth)
            
            import json
            print(json.dumps(result, indent=2))
        
        elif command == 'find-common-callers':
            if len(sys.argv) < 5:
                print("Error: find-common-callers requires at least 2 function names", file=sys.stderr)
                sys.exit(1)
            
            signatures_db = sys.argv[2]
            function_names = sys.argv[3:]
            
            result = find_common_callers(signatures_db, function_names)
            
            import json
            print(json.dumps(result, indent=2))
        
        else:
            print(f"Unknown command: {command}", file=sys.stderr)
            sys.exit(1)
    
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
