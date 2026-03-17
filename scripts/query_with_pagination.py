#!/usr/bin/env python3
"""Query wrapper that adds pagination support to all query commands."""

import sys
import json
import argparse
from typing import List, Dict, Any, Optional
from pathlib import Path
import importlib.util

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from pagination_handler import apply_pagination, sort_results, validate_pagination_params


def load_query_module(project_root: str):
    """Dynamically load the query_db module."""
    query_db_path = Path(project_root) / "scripts" / "query_db.py"
    spec = importlib.util.spec_from_file_location("query_db", query_db_path)
    query_db = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(query_db)
    return query_db


def execute_query_with_pagination(command: str,
                                 args: List[str],
                                 signatures_db: str,
                                 modules_db: str,
                                 limit: Optional[int] = None,
                                 offset: Optional[int] = None,
                                 total_count: bool = False,
                                 project_root: str = '.') -> Dict[str, Any]:
    """Execute a query command with pagination support.
    
    Args:
        command: Query command name
        args: Command arguments
        signatures_db: Path to workspace.db
        modules_db: Path to modules.db
        limit: Pagination limit
        offset: Pagination offset
        total_count: Whether to include total count
        project_root: Project root directory
    
    Returns:
        Dict with results and pagination metadata
    """
    # Load query_db module
    query_db = load_query_module(project_root)
    
    # Map command names to query_db functions
    command_map = {
        'find-function': ('query_function', [signatures_db] + args, 'name'),
        'search-functions': ('search_functions', [signatures_db] + args, 'name'),
        'list-file-functions': ('list_functions_in_file', [signatures_db] + args, 'name'),
        'find-function-dependencies': ('find_function_dependencies', [signatures_db] + args, 'name'),
        'find-function-dependents': ('find_function_dependents', [signatures_db] + args, 'name'),
        'find-dead-code': ('find_dead_code', [signatures_db], 'name'),
        'find-functions-in-module': ('find_functions_in_module', [modules_db, signatures_db] + args, 'name'),
        'find-module-for-function': ('find_module_for_function', [modules_db, signatures_db] + args, 'name'),
        'find-functions-calling-in-module': ('find_functions_calling_in_module', [modules_db, signatures_db] + args, 'name'),
        'find-module-dependencies': ('find_module_dependencies', [modules_db, signatures_db] + args, 'name'),
        'find-module': ('query_module', [modules_db] + args, 'name'),
        'search-modules': ('search_modules', [modules_db] + args, 'name'),
        'list-file-modules': ('list_modules_for_file', [modules_db] + args, 'name'),
    }
    
    if command not in command_map:
        raise ValueError(f'Unknown command: {command}')
    
    func_name, func_args, sort_key = command_map[command]
    func = getattr(query_db, func_name)
    
    # Execute query
    results = func(*func_args)
    
    # Handle None results
    if results is None:
        results = []
    
    # Ensure results is a list
    if not isinstance(results, list):
        results = [results] if results else []
    
    # Sort results for deterministic ordering
    if results and isinstance(results[0], dict):
        results = sort_results(results, sort_key=sort_key)
    
    # Apply pagination
    paginated = apply_pagination(results, limit, offset, calculate_total=True)
    
    return {
        'data': paginated['data'],
        'pagination': paginated['pagination']
    }


def main():
    """Command-line interface for query with pagination."""
    parser = argparse.ArgumentParser(
        description='Execute query with pagination support'
    )
    
    parser.add_argument('command', help='Query command name')
    parser.add_argument('args', nargs='*', help='Command arguments')
    parser.add_argument('--signatures-db', default='workspace.db', help='Path to workspace.db')
    parser.add_argument('--modules-db', default='modules.db', help='Path to modules.db')
    parser.add_argument('--limit', type=int, default=None, help='Pagination limit')
    parser.add_argument('--offset', type=int, default=None, help='Pagination offset')
    parser.add_argument('--total-count', action='store_true', help='Include total count')
    parser.add_argument('--project-root', default='.', help='Project root directory')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    try:
        # Validate pagination parameters
        limit, offset = validate_pagination_params(args.limit, args.offset)
        
        # Execute query with pagination
        result = execute_query_with_pagination(
            args.command,
            args.args,
            args.signatures_db,
            args.modules_db,
            limit=limit,
            offset=offset,
            total_count=args.total_count,
            project_root=args.project_root
        )
        
        # Output results
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            # Pretty print results
            print(json.dumps(result['data'], indent=2))
            if args.limit or args.offset or args.total_count:
                print("\nPagination:")
                pagination = result['pagination']
                print(f"  Limit: {pagination['limit']}")
                print(f"  Offset: {pagination['offset']}")
                print(f"  Total: {pagination['total_count']}")
                print(f"  Returned: {pagination['returned_count']}")
                print(f"  Has more: {pagination['has_more']}")
    
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
