#!/usr/bin/env python3
"""
Unit tests for format_generators module.

Tests all three output formats:
- Concise format (single-line signatures)
- Hover format (multi-line with metadata)
- Completion format (tab-separated for Vim/Neovim)
"""

import sys
import os
import unittest

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from format_generators import (
    format_function_signature,
    generate_concise_format,
    generate_hover_format,
    generate_completion_format,
    apply_format
)


class TestFormatFunctionSignature(unittest.TestCase):
    """Test format_function_signature function."""
    
    def test_basic_signature(self):
        """Test basic function signature formatting."""
        func = {
            'name': 'calculate',
            'parameters': [
                {'name': 'amount', 'type': 'DECIMAL'},
                {'name': 'rate', 'type': 'DECIMAL'}
            ],
            'return_type': 'DECIMAL'
        }
        result = format_function_signature(func)
        self.assertEqual(result, 'calculate(amount: DECIMAL, rate: DECIMAL) -> DECIMAL')
    
    def test_no_parameters(self):
        """Test function with no parameters."""
        func = {
            'name': 'get_timestamp',
            'parameters': [],
            'return_type': 'DATETIME'
        }
        result = format_function_signature(func)
        self.assertEqual(result, 'get_timestamp() -> DATETIME')
    
    def test_no_return_type(self):
        """Test procedure with no return type."""
        func = {
            'name': 'my_procedure',
            'parameters': [
                {'name': 'id', 'type': 'INTEGER'}
            ],
            'return_type': None
        }
        result = format_function_signature(func)
        self.assertEqual(result, 'my_procedure(id: INTEGER)')
    
    def test_empty_return_type(self):
        """Test procedure with empty return type string."""
        func = {
            'name': 'my_procedure',
            'parameters': [
                {'name': 'id', 'type': 'INTEGER'}
            ],
            'return_type': ''
        }
        result = format_function_signature(func)
        self.assertEqual(result, 'my_procedure(id: INTEGER)')
    
    def test_multiple_return_types(self):
        """Test function with multiple return types."""
        func = {
            'name': 'get_data',
            'parameters': [
                {'name': 'id', 'type': 'INTEGER'}
            ],
            'return_type': ['INTEGER', 'VARCHAR', 'DECIMAL']
        }
        result = format_function_signature(func)
        self.assertEqual(result, 'get_data(id: INTEGER) -> INTEGER, VARCHAR, DECIMAL')
    
    def test_string_parameters(self):
        """Test function with parameters as string."""
        func = {
            'name': 'calculate',
            'parameters': 'amount: DECIMAL, rate: DECIMAL',
            'return_type': 'DECIMAL'
        }
        result = format_function_signature(func)
        self.assertEqual(result, 'calculate(amount: DECIMAL, rate: DECIMAL) -> DECIMAL')
    
    def test_missing_name(self):
        """Test function with missing name."""
        func = {
            'parameters': [],
            'return_type': 'DECIMAL'
        }
        result = format_function_signature(func)
        self.assertEqual(result, 'unknown() -> DECIMAL')
    
    def test_complex_types(self):
        """Test function with complex types."""
        func = {
            'name': 'process_record',
            'parameters': [
                {'name': 'data', 'type': 'RECORD'},
                {'name': 'items', 'type': 'ARRAY[100]'}
            ],
            'return_type': 'RECORD'
        }
        result = format_function_signature(func)
        self.assertEqual(result, 'process_record(data: RECORD, items: ARRAY[100]) -> RECORD')


class TestConciseFormat(unittest.TestCase):
    """Test generate_concise_format function."""
    
    def test_single_function(self):
        """Test concise format with single function."""
        functions = [
            {
                'name': 'calculate',
                'parameters': [{'name': 'amount', 'type': 'DECIMAL'}],
                'return_type': 'DECIMAL'
            }
        ]
        result = generate_concise_format(functions)
        self.assertEqual(result, 'calculate(amount: DECIMAL) -> DECIMAL')
    
    def test_multiple_functions(self):
        """Test concise format with multiple functions."""
        functions = [
            {
                'name': 'calculate',
                'parameters': [{'name': 'amount', 'type': 'DECIMAL'}],
                'return_type': 'DECIMAL'
            },
            {
                'name': 'get_account',
                'parameters': [{'name': 'id', 'type': 'INTEGER'}],
                'return_type': 'RECORD'
            }
        ]
        result = generate_concise_format(functions)
        lines = result.split('\n')
        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[0], 'calculate(amount: DECIMAL) -> DECIMAL')
        self.assertEqual(lines[1], 'get_account(id: INTEGER) -> RECORD')
    
    def test_empty_list(self):
        """Test concise format with empty function list."""
        result = generate_concise_format([])
        self.assertEqual(result, '')
    
    def test_mixed_functions_and_procedures(self):
        """Test concise format with both functions and procedures."""
        functions = [
            {
                'name': 'calculate',
                'parameters': [{'name': 'amount', 'type': 'DECIMAL'}],
                'return_type': 'DECIMAL'
            },
            {
                'name': 'my_procedure',
                'parameters': [{'name': 'id', 'type': 'INTEGER'}],
                'return_type': None
            }
        ]
        result = generate_concise_format(functions)
        lines = result.split('\n')
        self.assertEqual(len(lines), 2)
        self.assertIn('-> DECIMAL', lines[0])
        self.assertNotIn('->', lines[1])


class TestHoverFormat(unittest.TestCase):
    """Test generate_hover_format function."""
    
    def test_single_function(self):
        """Test hover format with single function."""
        functions = [
            {
                'name': 'calculate',
                'parameters': [{'name': 'amount', 'type': 'DECIMAL'}],
                'return_type': 'DECIMAL',
                'file_path': 'src/math.4gl',
                'line_number': 42,
                'complexity': 5,
                'loc': 23
            }
        ]
        result = generate_hover_format(functions)
        lines = result.split('\n')
        self.assertEqual(len(lines), 3)
        self.assertEqual(lines[0], 'calculate(amount: DECIMAL) -> DECIMAL')
        self.assertEqual(lines[1], 'File: src/math.4gl:42')
        self.assertEqual(lines[2], 'Complexity: 5, LOC: 23')
    
    def test_multiple_functions(self):
        """Test hover format with multiple functions."""
        functions = [
            {
                'name': 'calculate',
                'parameters': [{'name': 'amount', 'type': 'DECIMAL'}],
                'return_type': 'DECIMAL',
                'file_path': 'src/math.4gl',
                'line_number': 42,
                'complexity': 5,
                'loc': 23
            },
            {
                'name': 'get_account',
                'parameters': [{'name': 'id', 'type': 'INTEGER'}],
                'return_type': 'RECORD',
                'file_path': 'src/queries.4gl',
                'line_number': 128,
                'complexity': 3,
                'loc': 15
            }
        ]
        result = generate_hover_format(functions)
        lines = result.split('\n')
        # 3 lines per function + 1 blank line between = 7 lines
        self.assertEqual(len(lines), 7)
        self.assertEqual(lines[0], 'calculate(amount: DECIMAL) -> DECIMAL')
        self.assertEqual(lines[3], '')  # Blank line
        self.assertEqual(lines[4], 'get_account(id: INTEGER) -> RECORD')
    
    def test_missing_metrics(self):
        """Test hover format with missing metrics."""
        functions = [
            {
                'name': 'calculate',
                'parameters': [{'name': 'amount', 'type': 'DECIMAL'}],
                'return_type': 'DECIMAL',
                'file_path': 'src/math.4gl',
                'line_number': 42,
                'complexity': None,
                'loc': None
            }
        ]
        result = generate_hover_format(functions)
        lines = result.split('\n')
        self.assertEqual(lines[2], 'Complexity: unknown, LOC: unknown')
    
    def test_missing_file_info(self):
        """Test hover format with missing file info."""
        functions = [
            {
                'name': 'calculate',
                'parameters': [{'name': 'amount', 'type': 'DECIMAL'}],
                'return_type': 'DECIMAL',
                'file_path': 'unknown',
                'line_number': 0,
                'complexity': 5,
                'loc': 23
            }
        ]
        result = generate_hover_format(functions)
        lines = result.split('\n')
        self.assertEqual(lines[1], 'File: unknown')


class TestCompletionFormat(unittest.TestCase):
    """Test generate_completion_format function."""
    
    def test_single_function(self):
        """Test completion format with single function."""
        functions = [
            {
                'name': 'calculate',
                'parameters': [{'name': 'amount', 'type': 'DECIMAL'}],
                'return_type': 'DECIMAL',
                'file_path': 'src/math.4gl',
                'line_number': 42,
                'complexity': 5,
                'loc': 23
            }
        ]
        result = generate_completion_format(functions)
        parts = result.split('\t')
        self.assertEqual(len(parts), 3)
        self.assertEqual(parts[0], 'calculate')
        self.assertIn('function', parts[1])
        self.assertIn('DECIMAL', parts[1])
        self.assertIn('src/math.4gl:42', parts[2])
        self.assertIn('Complexity: 5', parts[2])
    
    def test_tab_separated(self):
        """Test completion format uses tabs as separators."""
        functions = [
            {
                'name': 'calculate',
                'parameters': [{'name': 'amount', 'type': 'DECIMAL'}],
                'return_type': 'DECIMAL',
                'file_path': 'src/math.4gl',
                'line_number': 42,
                'complexity': 5,
                'loc': 23
            }
        ]
        result = generate_completion_format(functions)
        # Should have exactly 2 tabs (3 columns)
        self.assertEqual(result.count('\t'), 2)
    
    def test_multiple_functions(self):
        """Test completion format with multiple functions."""
        functions = [
            {
                'name': 'calculate',
                'parameters': [{'name': 'amount', 'type': 'DECIMAL'}],
                'return_type': 'DECIMAL',
                'file_path': 'src/math.4gl',
                'line_number': 42,
                'complexity': 5,
                'loc': 23
            },
            {
                'name': 'get_account',
                'parameters': [{'name': 'id', 'type': 'INTEGER'}],
                'return_type': 'RECORD',
                'file_path': 'src/queries.4gl',
                'line_number': 128,
                'complexity': 3,
                'loc': 15
            }
        ]
        result = generate_completion_format(functions)
        lines = result.split('\n')
        self.assertEqual(len(lines), 2)
        # Each line should have 2 tabs
        for line in lines:
            self.assertEqual(line.count('\t'), 2)
    
    def test_vim_completion_compatibility(self):
        """Test completion format is compatible with Vim complete() function."""
        functions = [
            {
                'name': 'calculate',
                'parameters': [{'name': 'amount', 'type': 'DECIMAL'}],
                'return_type': 'DECIMAL',
                'file_path': 'src/math.4gl',
                'line_number': 42,
                'complexity': 5,
                'loc': 23
            }
        ]
        result = generate_completion_format(functions)
        parts = result.split('\t')
        
        # Vim complete() expects: word, menu, info
        word = parts[0]  # Function name
        menu = parts[1]  # Signature
        info = parts[2]  # File + metrics
        
        # Verify structure
        self.assertTrue(word)  # Word should not be empty
        self.assertTrue(menu)  # Menu should not be empty
        self.assertTrue(info)  # Info should not be empty
        self.assertIn('function', menu)  # Menu should contain 'function'
        self.assertIn('|', info)  # Info should contain pipe separator


class TestApplyFormat(unittest.TestCase):
    """Test apply_format function."""
    
    def setUp(self):
        """Set up test data."""
        self.functions = [
            {
                'name': 'calculate',
                'parameters': [{'name': 'amount', 'type': 'DECIMAL'}],
                'return_type': 'DECIMAL',
                'file_path': 'src/math.4gl',
                'line_number': 42,
                'complexity': 5,
                'loc': 23
            }
        ]
    
    def test_apply_vim_format(self):
        """Test apply_format with vim format."""
        result = apply_format(self.functions, 'vim')
        self.assertIn('calculate', result)
        self.assertIn('DECIMAL', result)
        self.assertNotIn('File:', result)
    
    def test_apply_vim_hover_format(self):
        """Test apply_format with vim-hover format."""
        result = apply_format(self.functions, 'vim-hover')
        self.assertIn('calculate', result)
        self.assertIn('File:', result)
        self.assertIn('Complexity:', result)
    
    def test_apply_vim_completion_format(self):
        """Test apply_format with vim-completion format."""
        result = apply_format(self.functions, 'vim-completion')
        self.assertIn('calculate', result)
        self.assertIn('\t', result)
    
    def test_case_insensitive_format(self):
        """Test apply_format is case-insensitive."""
        result1 = apply_format(self.functions, 'vim')
        result2 = apply_format(self.functions, 'VIM')
        result3 = apply_format(self.functions, 'Vim')
        self.assertEqual(result1, result2)
        self.assertEqual(result2, result3)
    
    def test_invalid_format(self):
        """Test apply_format with invalid format."""
        with self.assertRaises(ValueError) as context:
            apply_format(self.functions, 'invalid')
        self.assertIn('Invalid format', str(context.exception))
    
    def test_empty_functions(self):
        """Test apply_format with empty function list."""
        result = apply_format([], 'vim')
        self.assertEqual(result, '')


if __name__ == '__main__':
    unittest.main()
