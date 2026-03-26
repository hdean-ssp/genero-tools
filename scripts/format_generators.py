#!/usr/bin/env python3
"""
Format generators for Vim plugin output.

Provides three output formats optimized for Vim/Neovim integration:
1. Concise format: Single-line function signatures
2. Hover format: Multi-line with file location and metrics
3. Completion format: Tab-separated for Vim completion API
"""

import json
from typing import List, Dict, Any, Optional


def format_function_signature(func_data: Dict[str, Any]) -> str:
    """
    Generate concise function signature.
    
    Format: function_name(param1: TYPE1, param2: TYPE2) -> RETURN_TYPE
    
    Args:
        func_data: Function metadata dictionary with keys:
            - name: Function name
            - parameters: List of parameter dicts with 'name' and 'type'
            - return_type: Return type string (or None/empty for procedures)
    
    Returns:
        Concise signature string
    """
    name = func_data.get('name', 'unknown')
    
    # Format parameters
    params = func_data.get('parameters', [])
    if isinstance(params, str):
        # If parameters is already a string, use it directly
        param_str = params
    else:
        # Build parameter string from list
        param_parts = []
        for param in params:
            if isinstance(param, dict):
                param_name = param.get('name', '')
                param_type = param.get('type', '')
                if param_name and param_type:
                    param_parts.append(f"{param_name}: {param_type}")
            elif isinstance(param, str):
                param_parts.append(param)
        param_str = ', '.join(param_parts)
    
    # Format return type
    return_type = func_data.get('return_type', '')
    if isinstance(return_type, list):
        return_type = ', '.join(return_type)
    
    # Build signature
    if return_type:
        return f"{name}({param_str}) -> {return_type}"
    else:
        return f"{name}({param_str})"


def generate_concise_format(functions: List[Dict[str, Any]]) -> str:
    """
    Generate concise format output (single-line signatures).
    
    Args:
        functions: List of function metadata dictionaries
    
    Returns:
        Concise format output (one signature per line)
    """
    lines = []
    for func in functions:
        signature = format_function_signature(func)
        lines.append(signature)
    
    return '\n'.join(lines)


def generate_hover_format(functions: List[Dict[str, Any]]) -> str:
    """
    Generate hover format output (multi-line with metadata).
    
    Format:
    function_name(params) -> return_type
    File: path/to/file.4gl:line_number
    Complexity: N, LOC: M
    
    Args:
        functions: List of function metadata dictionaries
    
    Returns:
        Hover format output (three lines per function, blank line between)
    """
    lines = []
    
    for i, func in enumerate(functions):
        # Line 1: Signature
        signature = format_function_signature(func)
        lines.append(signature)
        
        # Line 2: File location
        file_path = func.get('file_path', 'unknown')
        line_number = func.get('line_number', 0)
        if line_number:
            lines.append(f"File: {file_path}:{line_number}")
        else:
            lines.append(f"File: {file_path}")
        
        # Line 3: Complexity metrics
        complexity = func.get('complexity', None)
        loc = func.get('loc', None)
        
        if complexity is not None and loc is not None:
            lines.append(f"Complexity: {complexity}, LOC: {loc}")
        elif complexity is not None:
            lines.append(f"Complexity: {complexity}, LOC: unknown")
        elif loc is not None:
            lines.append(f"Complexity: unknown, LOC: {loc}")
        else:
            lines.append("Complexity: unknown, LOC: unknown")
        
        # Add blank line between functions (except after last one)
        if i < len(functions) - 1:
            lines.append("")
    
    return '\n'.join(lines)


def generate_completion_format(functions: List[Dict[str, Any]]) -> str:
    """
    Generate completion format output (tab-separated for Vim/Neovim).
    
    Format: word<TAB>menu<TAB>info
    
    Columns:
    - word: Function name (completion word)
    - menu: Function signature
    - info: File location and metrics
    
    Args:
        functions: List of function metadata dictionaries
    
    Returns:
        Completion format output (one function per line, tab-separated)
    """
    lines = []
    
    for func in functions:
        # Column 1: Function name (word)
        name = func.get('name', 'unknown')
        
        # Column 2: Function signature (menu)
        signature = format_function_signature(func)
        # Remove function name from signature for menu (keep just the signature part)
        # Extract just the parameters and return type
        if '(' in signature:
            menu = 'function' + signature[signature.index('('):]
        else:
            menu = signature
        
        # Column 3: File location and metrics (info)
        file_path = func.get('file_path', 'unknown')
        line_number = func.get('line_number', 0)
        complexity = func.get('complexity', None)
        loc = func.get('loc', None)
        
        # Build info string
        if line_number:
            file_info = f"{file_path}:{line_number}"
        else:
            file_info = file_path
        
        if complexity is not None and loc is not None:
            metrics = f"Complexity: {complexity}, LOC: {loc}"
        elif complexity is not None:
            metrics = f"Complexity: {complexity}, LOC: unknown"
        elif loc is not None:
            metrics = f"Complexity: unknown, LOC: {loc}"
        else:
            metrics = "Complexity: unknown, LOC: unknown"
        
        info = f"{file_info} | {metrics}"
        
        # Build tab-separated line
        line = f"{name}\t{menu}\t{info}"
        lines.append(line)
    
    return '\n'.join(lines)


def apply_format(functions: List[Dict[str, Any]], format_type: str) -> str:
    """
    Apply the specified format to function data.
    
    Args:
        functions: List of function metadata dictionaries
        format_type: Format type ('vim', 'vim-hover', 'vim-completion')
    
    Returns:
        Formatted output string
    
    Raises:
        ValueError: If format_type is invalid
    """
    format_type = format_type.lower()
    
    if format_type == 'vim':
        return generate_concise_format(functions)
    elif format_type == 'vim-hover':
        return generate_hover_format(functions)
    elif format_type == 'vim-completion':
        return generate_completion_format(functions)
    else:
        raise ValueError(
            f"Invalid format '{format_type}'. "
            f"Supported formats: vim, vim-hover, vim-completion"
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
    
    print("=== Concise Format ===")
    print(generate_concise_format(sample_functions))
    print("\n=== Hover Format ===")
    print(generate_hover_format(sample_functions))
    print("\n=== Completion Format ===")
    print(generate_completion_format(sample_functions))
