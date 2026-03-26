#!/usr/bin/env python3
"""
Option parsing and integration for Vim output formats.

Handles parsing of --format and --filter command-line options
and integrates with query functions.
"""

import sys
from typing import List, Dict, Any, Tuple, Optional
from format_generators import apply_format
from filter_functions import apply_filters, validate_filters


class OutputOptions:
    """Manages output format and filter options."""
    
    def __init__(self):
        self.format_type = None  # 'vim', 'vim-hover', 'vim-completion', or None (default)
        self.filters = []  # List of filter names
    
    def parse_args(self, args: List[str]) -> Tuple[List[str], List[str]]:
        """
        Parse command-line arguments to extract format and filter options.
        
        Args:
            args: Command-line arguments
        
        Returns:
            Tuple of (remaining_args, errors)
            - remaining_args: Arguments without --format and --filter
            - errors: List of error messages (empty if valid)
        """
        remaining = []
        errors = []
        
        i = 0
        while i < len(args):
            arg = args[i]
            
            if arg.startswith('--format='):
                # Parse format option
                format_val = arg.split('=', 1)[1]
                if not format_val:
                    errors.append("Error: --format option requires a value")
                    i += 1
                    continue
                
                format_val = format_val.lower()
                valid_formats = {'vim', 'vim-hover', 'vim-completion'}
                
                if format_val not in valid_formats:
                    errors.append(
                        f"Error: Invalid format '{format_val}'. "
                        f"Supported formats: vim, vim-hover, vim-completion"
                    )
                else:
                    self.format_type = format_val
            
            elif arg.startswith('--filter='):
                # Parse filter option
                filter_val = arg.split('=', 1)[1]
                if not filter_val:
                    errors.append("Error: --filter option requires a value")
                    i += 1
                    continue
                
                filter_val = filter_val.lower()
                valid_filters = {'functions-only', 'no-metrics', 'no-file-info'}
                
                if filter_val not in valid_filters:
                    errors.append(
                        f"Error: Invalid filter '{filter_val}'. "
                        f"Supported filters: functions-only, no-metrics, no-file-info"
                    )
                else:
                    self.filters.append(filter_val)
            
            else:
                # Keep non-option arguments
                remaining.append(arg)
            
            i += 1
        
        return remaining, errors
    
    def apply_to_results(self, functions: List[Dict[str, Any]]) -> str:
        """
        Apply format and filters to query results.
        
        Args:
            functions: List of function metadata dictionaries
        
        Returns:
            Formatted output string
        
        Raises:
            ValueError: If format or filters are invalid
        """
        # Apply filters first
        if self.filters:
            functions = apply_filters(functions, self.filters)
        
        # Apply format (default to JSON if not specified)
        if self.format_type:
            return apply_format(functions, self.format_type)
        else:
            # Default format: JSON (backward compatible)
            import json
            return json.dumps(functions, indent=2)
    
    def get_help_text(self) -> str:
        """Get help text for format and filter options."""
        return """
Format Options:
  --format=vim              Output concise function signatures
  --format=vim-hover        Output with file location and metrics
  --format=vim-completion   Output tab-separated for Vim completion

Filter Options:
  --filter=functions-only   Include only functions (exclude procedures)
  --filter=no-metrics       Exclude complexity and LOC metrics
  --filter=no-file-info     Exclude file path and line number

Examples:
  query.sh find-function "calculate" --format=vim
  query.sh search-functions "get_*" --format=vim-hover
  query.sh search-functions "*" --format=vim-completion --filter=functions-only
  query.sh find-function "my_func" --format=vim-hover --filter=no-metrics
"""


def process_query_results(
    functions: List[Dict[str, Any]],
    args: List[str]
) -> Tuple[str, Optional[str]]:
    """
    Process query results with format and filter options.
    
    Args:
        functions: List of function metadata dictionaries
        args: Command-line arguments containing --format and --filter options
    
    Returns:
        Tuple of (output, error_message)
        - output: Formatted output string (or empty if error)
        - error_message: Error message (or None if successful)
    """
    options = OutputOptions()
    remaining_args, errors = options.parse_args(args)
    
    if errors:
        return '', '\n'.join(errors)
    
    try:
        output = options.apply_to_results(functions)
        return output, None
    except ValueError as e:
        return '', str(e)


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
    
    # Test different option combinations
    test_cases = [
        ['--format=vim'],
        ['--format=vim-hover'],
        ['--format=vim-completion'],
        ['--format=vim', '--filter=functions-only'],
        ['--format=vim-hover', '--filter=no-metrics'],
    ]
    
    for args in test_cases:
        print(f"\n=== Args: {' '.join(args)} ===")
        output, error = process_query_results(sample_functions, args)
        if error:
            print(f"Error: {error}")
        else:
            print(output)
