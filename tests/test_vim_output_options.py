#!/usr/bin/env python3
"""
Unit tests for vim_output_options module.

Tests option parsing and integration functionality.
"""

import sys
import os
import unittest

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from vim_output_options import (
    OutputOptions,
    process_query_results
)


class TestOutputOptions(unittest.TestCase):
    """Test OutputOptions class."""
    
    def setUp(self):
        """Set up test data."""
        self.options = OutputOptions()
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
    
    def test_parse_format_vim(self):
        """Test parsing --format=vim option."""
        remaining, errors = self.options.parse_args(['--format=vim', 'arg1'])
        self.assertEqual(self.options.format_type, 'vim')
        self.assertEqual(remaining, ['arg1'])
        self.assertEqual(len(errors), 0)
    
    def test_parse_format_vim_hover(self):
        """Test parsing --format=vim-hover option."""
        remaining, errors = self.options.parse_args(['--format=vim-hover'])
        self.assertEqual(self.options.format_type, 'vim-hover')
        self.assertEqual(len(errors), 0)
    
    def test_parse_format_vim_completion(self):
        """Test parsing --format=vim-completion option."""
        remaining, errors = self.options.parse_args(['--format=vim-completion'])
        self.assertEqual(self.options.format_type, 'vim-completion')
        self.assertEqual(len(errors), 0)
    
    def test_parse_filter_functions_only(self):
        """Test parsing --filter=functions-only option."""
        remaining, errors = self.options.parse_args(['--filter=functions-only'])
        self.assertIn('functions-only', self.options.filters)
        self.assertEqual(len(errors), 0)
    
    def test_parse_filter_no_metrics(self):
        """Test parsing --filter=no-metrics option."""
        remaining, errors = self.options.parse_args(['--filter=no-metrics'])
        self.assertIn('no-metrics', self.options.filters)
        self.assertEqual(len(errors), 0)
    
    def test_parse_filter_no_file_info(self):
        """Test parsing --filter=no-file-info option."""
        remaining, errors = self.options.parse_args(['--filter=no-file-info'])
        self.assertIn('no-file-info', self.options.filters)
        self.assertEqual(len(errors), 0)
    
    def test_parse_multiple_filters(self):
        """Test parsing multiple --filter options."""
        remaining, errors = self.options.parse_args([
            '--filter=functions-only',
            '--filter=no-metrics'
        ])
        self.assertEqual(len(self.options.filters), 2)
        self.assertIn('functions-only', self.options.filters)
        self.assertIn('no-metrics', self.options.filters)
        self.assertEqual(len(errors), 0)
    
    def test_parse_format_and_filters(self):
        """Test parsing both format and filter options."""
        remaining, errors = self.options.parse_args([
            '--format=vim-hover',
            '--filter=functions-only',
            'arg1'
        ])
        self.assertEqual(self.options.format_type, 'vim-hover')
        self.assertIn('functions-only', self.options.filters)
        self.assertEqual(remaining, ['arg1'])
        self.assertEqual(len(errors), 0)
    
    def test_parse_case_insensitive_format(self):
        """Test format option is case-insensitive."""
        options1 = OutputOptions()
        options1.parse_args(['--format=VIM'])
        self.assertEqual(options1.format_type, 'vim')
        
        options2 = OutputOptions()
        options2.parse_args(['--format=Vim-Hover'])
        self.assertEqual(options2.format_type, 'vim-hover')
    
    def test_parse_case_insensitive_filter(self):
        """Test filter option is case-insensitive."""
        options1 = OutputOptions()
        options1.parse_args(['--filter=Functions-Only'])
        self.assertIn('functions-only', options1.filters)
        
        options2 = OutputOptions()
        options2.parse_args(['--filter=NO-METRICS'])
        self.assertIn('no-metrics', options2.filters)
    
    def test_parse_invalid_format(self):
        """Test parsing invalid format option."""
        remaining, errors = self.options.parse_args(['--format=invalid'])
        self.assertEqual(len(errors), 1)
        self.assertIn('Invalid format', errors[0])
    
    def test_parse_invalid_filter(self):
        """Test parsing invalid filter option."""
        remaining, errors = self.options.parse_args(['--filter=invalid'])
        self.assertEqual(len(errors), 1)
        self.assertIn('Invalid filter', errors[0])
    
    def test_parse_format_no_value(self):
        """Test parsing --format with no value."""
        remaining, errors = self.options.parse_args(['--format='])
        self.assertEqual(len(errors), 1)
        self.assertIn('requires a value', errors[0])
    
    def test_parse_filter_no_value(self):
        """Test parsing --filter with no value."""
        remaining, errors = self.options.parse_args(['--filter='])
        self.assertEqual(len(errors), 1)
        self.assertIn('requires a value', errors[0])
    
    def test_parse_non_option_arguments(self):
        """Test that non-option arguments are preserved."""
        remaining, errors = self.options.parse_args([
            'arg1',
            '--format=vim',
            'arg2',
            '--filter=functions-only',
            'arg3'
        ])
        self.assertEqual(remaining, ['arg1', 'arg2', 'arg3'])
        self.assertEqual(len(errors), 0)
    
    def test_apply_to_results_with_format(self):
        """Test apply_to_results with format option."""
        self.options.format_type = 'vim'
        result = self.options.apply_to_results(self.functions)
        self.assertIn('calculate', result)
        self.assertNotIn('File:', result)
    
    def test_apply_to_results_with_filters(self):
        """Test apply_to_results with filter options."""
        self.options.filters = ['no-metrics']
        result = self.options.apply_to_results(self.functions)
        # Result should be JSON (default format)
        import json
        data = json.loads(result)
        self.assertNotIn('complexity', data[0])
        self.assertNotIn('loc', data[0])
    
    def test_apply_to_results_default_format(self):
        """Test apply_to_results defaults to JSON."""
        result = self.options.apply_to_results(self.functions)
        import json
        data = json.loads(result)
        self.assertEqual(data[0]['name'], 'calculate')
    
    def test_get_help_text(self):
        """Test get_help_text returns help information."""
        help_text = self.options.get_help_text()
        self.assertIn('--format=vim', help_text)
        self.assertIn('--filter=functions-only', help_text)
        self.assertIn('Examples:', help_text)


class TestProcessQueryResults(unittest.TestCase):
    """Test process_query_results function."""
    
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
    
    def test_process_with_format(self):
        """Test process_query_results with format option."""
        output, error = process_query_results(self.functions, ['--format=vim'])
        self.assertIsNone(error)
        self.assertIn('calculate', output)
    
    def test_process_with_filter(self):
        """Test process_query_results with filter option."""
        output, error = process_query_results(self.functions, ['--filter=no-metrics'])
        self.assertIsNone(error)
        import json
        data = json.loads(output)
        self.assertNotIn('complexity', data[0])
    
    def test_process_with_format_and_filter(self):
        """Test process_query_results with both format and filter."""
        output, error = process_query_results(
            self.functions,
            ['--format=vim-hover', '--filter=no-metrics']
        )
        self.assertIsNone(error)
        self.assertIn('calculate', output)
        self.assertIn('File:', output)
    
    def test_process_invalid_format(self):
        """Test process_query_results with invalid format."""
        output, error = process_query_results(self.functions, ['--format=invalid'])
        self.assertIsNotNone(error)
        self.assertIn('Invalid format', error)
        self.assertEqual(output, '')
    
    def test_process_invalid_filter(self):
        """Test process_query_results with invalid filter."""
        output, error = process_query_results(self.functions, ['--filter=invalid'])
        self.assertIsNotNone(error)
        self.assertIn('Invalid filter', error)
        self.assertEqual(output, '')
    
    def test_process_empty_functions(self):
        """Test process_query_results with empty function list."""
        output, error = process_query_results([], ['--format=vim'])
        self.assertIsNone(error)
        self.assertEqual(output, '')
    
    def test_process_no_options(self):
        """Test process_query_results with no options."""
        output, error = process_query_results(self.functions, [])
        self.assertIsNone(error)
        import json
        data = json.loads(output)
        self.assertEqual(data[0]['name'], 'calculate')


class TestIntegration(unittest.TestCase):
    """Integration tests for option parsing and formatting."""
    
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
            },
            {
                'name': 'my_procedure',
                'parameters': [{'name': 'id', 'type': 'INTEGER'}],
                'return_type': None,
                'file_path': 'src/utils.4gl',
                'line_number': 100,
                'complexity': 2,
                'loc': 10
            }
        ]
    
    def test_vim_format_with_functions_only(self):
        """Test vim format with functions-only filter."""
        output, error = process_query_results(
            self.functions,
            ['--format=vim', '--filter=functions-only']
        )
        self.assertIsNone(error)
        # Should only have calculate, not my_procedure
        self.assertIn('calculate', output)
        self.assertNotIn('my_procedure', output)
    
    def test_vim_hover_with_no_metrics(self):
        """Test vim-hover format with no-metrics filter."""
        output, error = process_query_results(
            self.functions,
            ['--format=vim-hover', '--filter=no-metrics']
        )
        self.assertIsNone(error)
        self.assertIn('calculate', output)
        self.assertIn('File:', output)
        # When metrics are removed, hover format shows "unknown"
        self.assertIn('Complexity: unknown', output)
    
    def test_vim_completion_with_functions_only(self):
        """Test vim-completion format with functions-only filter."""
        output, error = process_query_results(
            self.functions,
            ['--format=vim-completion', '--filter=functions-only']
        )
        self.assertIsNone(error)
        lines = output.split('\n')
        # Should only have one line (calculate)
        self.assertEqual(len(lines), 1)
        self.assertIn('calculate', lines[0])
        self.assertIn('\t', lines[0])


if __name__ == '__main__':
    unittest.main()
