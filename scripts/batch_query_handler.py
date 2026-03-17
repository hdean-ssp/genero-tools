#!/usr/bin/env python3
"""Batch query handler for executing multiple queries in a single database connection."""

import json
import sys
import time
import sqlite3
from typing import Dict, List, Any, Optional
from pathlib import Path
import importlib.util

def load_query_module(project_root: str):
    """Dynamically load the query_db module."""
    query_db_path = Path(project_root) / "scripts" / "query_db.py"
    spec = importlib.util.spec_from_file_location("query_db", query_db_path)
    query_db = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(query_db)
    return query_db


def execute_single_query(query_db, query_request: Dict[str, Any], 
                        signatures_db: str, modules_db: str) -> Dict[str, Any]:
    """Execute a single query and return results with timing information.
    
    Args:
        query_db: The loaded query_db module
        query_request: Dict with 'command' and 'args' keys
        signatures_db: Path to workspace.db
        modules_db: Path to modules.db
    
    Returns:
        Dict with 'status', 'time_ms', 'data', and optional 'error' keys
    """
    start_time = time.time()
    
    try:
        command = query_request.get('command')
        args = query_request.get('args', [])
        
        # Map command names to query_db functions
        command_map = {
            'find-function': ('query_function', [signatures_db] + args),
            'search-functions': ('search_functions', [signatures_db] + args),
            'list-file-functions': ('list_functions_in_file', [signatures_db] + args),
            'find-function-dependencies': ('find_function_dependencies', [signatures_db] + args),
            'find-function-dependents': ('find_function_dependents', [signatures_db] + args),
            'find-dead-code': ('find_dead_code', [signatures_db]),
            'find-functions-in-module': ('find_functions_in_module', [modules_db, signatures_db] + args),
            'find-module-for-function': ('find_module_for_function', [modules_db, signatures_db] + args),
            'find-functions-calling-in-module': ('find_functions_calling_in_module', [modules_db, signatures_db] + args),
            'find-module-dependencies': ('find_module_dependencies', [modules_db, signatures_db] + args),
            'find-module': ('query_module', [modules_db] + args),
            'search-modules': ('search_modules', [modules_db] + args),
            'list-file-modules': ('list_modules_for_file', [modules_db] + args),
        }
        
        if command not in command_map:
            elapsed_ms = (time.time() - start_time) * 1000
            return {
                'status': 'error',
                'time_ms': elapsed_ms,
                'error': f'Unknown command: {command}'
            }
        
        func_name, func_args = command_map[command]
        func = getattr(query_db, func_name)
        result = func(*func_args)
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        return {
            'status': 'success',
            'time_ms': elapsed_ms,
            'data': result
        }
    
    except Exception as e:
        elapsed_ms = (time.time() - start_time) * 1000
        return {
            'status': 'error',
            'time_ms': elapsed_ms,
            'error': str(e)
        }


def execute_batch_query(batch_request: Dict[str, Any], 
                       signatures_db: str, 
                       modules_db: str,
                       project_root: str = '.') -> Dict[str, Any]:
    """Execute multiple queries in a single batch.
    
    Args:
        batch_request: Dict with 'queries' array, each containing 'id', 'command', 'args'
        signatures_db: Path to workspace.db
        modules_db: Path to modules.db
        project_root: Path to project root for loading query_db module
    
    Returns:
        Dict with batch results, timing information, and status
    """
    batch_start_time = time.time()
    
    try:
        # Load query_db module
        query_db = load_query_module(project_root)
        
        # Validate batch request
        if 'queries' not in batch_request:
            return {
                'status': 'error',
                'error': 'Batch request must contain "queries" array'
            }
        
        queries = batch_request['queries']
        if not isinstance(queries, list):
            return {
                'status': 'error',
                'error': '"queries" must be an array'
            }
        
        if len(queries) == 0:
            return {
                'status': 'error',
                'error': 'Batch request must contain at least one query'
            }
        
        # Execute queries sequentially
        results = []
        for query_request in queries:
            query_id = query_request.get('id', f'query_{len(results)}')
            
            # Validate query request
            if 'command' not in query_request:
                results.append({
                    'query_id': query_id,
                    'status': 'error',
                    'error': 'Query must contain "command" field'
                })
                continue
            
            # Execute query
            query_result = execute_single_query(query_db, query_request, 
                                              signatures_db, modules_db)
            query_result['query_id'] = query_id
            results.append(query_result)
        
        total_time_ms = (time.time() - batch_start_time) * 1000
        
        return {
            'batch_id': f'batch_{int(batch_start_time * 1000)}',
            'status': 'success',
            'total_time_ms': total_time_ms,
            'results': results
        }
    
    except Exception as e:
        total_time_ms = (time.time() - batch_start_time) * 1000
        return {
            'batch_id': f'batch_{int(batch_start_time * 1000)}',
            'status': 'error',
            'total_time_ms': total_time_ms,
            'error': str(e)
        }


def main():
    """Command-line interface for batch query execution."""
    if len(sys.argv) < 2:
        print("Usage: batch_query_handler.py <batch_json_file> [signatures_db] [modules_db] [project_root]", 
              file=sys.stderr)
        sys.exit(1)
    
    batch_file = sys.argv[1]
    signatures_db = sys.argv[2] if len(sys.argv) > 2 else 'workspace.db'
    modules_db = sys.argv[3] if len(sys.argv) > 3 else 'modules.db'
    project_root = sys.argv[4] if len(sys.argv) > 4 else '.'
    
    try:
        with open(batch_file, 'r') as f:
            batch_request = json.load(f)
    except FileNotFoundError:
        print(f"Error: Batch file not found: {batch_file}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in batch file: {e}", file=sys.stderr)
        sys.exit(1)
    
    result = execute_batch_query(batch_request, signatures_db, modules_db, project_root)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
