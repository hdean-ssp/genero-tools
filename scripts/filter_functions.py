#!/usr/bin/env python3
"""
Filter functions for Vim plugin output.

Provides filtering options to customize query results:
1. functions-only: Exclude procedures (functions with no return type)
2. no-metrics: Remove complexity and LOC fields
3. no-file-info: Remove file path and line number
"""

from typing import List, Dict, Any


def filter_functions_only(functions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filter to include only functions (exclude procedures).
    
    A function has a return type, a procedure does not.
    
    Args:
        functions: List of function metadata dictionaries
    
    Returns:
        Filtered list containing only functions with return types
    """
    return [
        func for func in functions
        if func.get('return_type') and str(func.get('return_type')).strip()
    ]


def filter_no_metrics(functions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filter to remove complexity and LOC metrics.
    
    Args:
        functions: List of function metadata dictionaries
    
    Returns:
        Filtered list with complexity and loc fields removed
    """
    filtered = []
    for func in functions:
        func_copy = func.copy()
        func_copy.pop('complexity', None)
        func_copy.pop('loc', None)
        filtered.append(func_copy)
    
    return filtered


def filter_no_file_info(functions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filter to remove file path and line number.
    
    Args:
        functions: List of function metadata dictionaries
    
    Returns:
        Filtered list with file_path and line_number fields removed
    """
    filtered = []
    for func in functions:
        func_copy = func.copy()
        func_copy.pop('file_path', None)
        func_copy.pop('line_number', None)
        filtered.append(func_copy)
    
    return filtered


def apply_filters(
    functions: List[Dict[str, Any]],
    filters: List[str]
) -> List[Dict[str, Any]]:
    """
    Apply multiple filters to function data.
    
    Filters are applied in order and are cumulative (AND logic).
    
    Args:
        functions: List of function metadata dictionaries
        filters: List of filter names to apply
    
    Returns:
        Filtered list of functions
    
    Raises:
        ValueError: If any filter name is invalid
    """
    result = functions
    
    for filter_name in filters:
        filter_name = filter_name.lower()
        
        if filter_name == 'functions-only':
            result = filter_functions_only(result)
        elif filter_name == 'no-metrics':
            result = filter_no_metrics(result)
        elif filter_name == 'no-file-info':
            result = filter_no_file_info(result)
        else:
            raise ValueError(
                f"Invalid filter '{filter_name}'. "
                f"Supported filters: functions-only, no-metrics, no-file-info"
            )
    
    return result


def validate_filters(filters: List[str]) -> None:
    """
    Validate filter names.
    
    Args:
        filters: List of filter names to validate
    
    Raises:
        ValueError: If any filter name is invalid
    """
    valid_filters = {'functions-only', 'no-metrics', 'no-file-info'}
    
    for filter_name in filters:
        if filter_name.lower() not in valid_filters:
            raise ValueError(
                f"Invalid filter '{filter_name}'. "
                f"Supported filters: functions-only, no-metrics, no-file-info"
            )


if __name__ == '__main__':
    # Example usage
    sample_functions = [
        {
            'name': 'calculate',
            'parameters': [
                {'name': 'amount', 'type': 'DECIMAL'},
                {'name': 'rate', 'type': 'DECIMAL'}
            ],
            'return_type': 'DECIMAL',
            'file_path': 'src/math.4gl',
            'line_number': 42,
            'complexity': 5,
            'loc': 23
        },
        {
            'name': 'my_procedure',
            'parameters': [
                {'name': 'id', 'type': 'INTEGER'}
            ],
            'return_type': None,  # Procedure (no return type)
            'file_path': 'src/utils.4gl',
            'line_number': 100,
            'complexity': 2,
            'loc': 10
        },
        {
            'name': 'get_account',
            'parameters': [
                {'name': 'id', 'type': 'INTEGER'}
            ],
            'return_type': 'RECORD',
            'file_path': 'src/queries.4gl',
            'line_number': 128,
            'complexity': 3,
            'loc': 15
        }
    ]
    
    print("=== Original ===")
    for func in sample_functions:
        print(f"{func['name']}: {func.get('return_type', 'PROCEDURE')}")
    
    print("\n=== Filter: functions-only ===")
    filtered = filter_functions_only(sample_functions)
    for func in filtered:
        print(f"{func['name']}: {func.get('return_type')}")
    
    print("\n=== Filter: no-metrics ===")
    filtered = filter_no_metrics(sample_functions)
    for func in filtered:
        print(f"{func['name']}: complexity={func.get('complexity')}, loc={func.get('loc')}")
    
    print("\n=== Filter: no-file-info ===")
    filtered = filter_no_file_info(sample_functions)
    for func in filtered:
        print(f"{func['name']}: file={func.get('file_path')}, line={func.get('line_number')}")
    
    print("\n=== Multiple filters: functions-only + no-metrics ===")
    filtered = apply_filters(sample_functions, ['functions-only', 'no-metrics'])
    for func in filtered:
        print(f"{func['name']}: {func.get('return_type')}, complexity={func.get('complexity')}")
