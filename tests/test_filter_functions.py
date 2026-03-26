#!/usr/bin/env python3
"""
Unit tests for filter_functions module.

Tests all three filtering options:
- functions-only: Exclude procedures
- no-metrics: Remove complexity and LOC
- no-file-info: Remove file path and line number
"""

import sys
import os
import unittest

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from filter_functions import (
    filter_functions_only,
    filter_no_metrics,
    filter_no_file_info,
    apply_filters,
    validate_filters
)


class TestFilterFunctionsOnly(unittest.TestCase):
    """Test filter_functions_only function."""
    
    def test_exclude_procedures(self):
        """Test that procedures (no return type) are excluded."""
        functions = [
            {
                'name': 'calculate',
                'return_type': 'DECIMAL'
            },
            {
                'name': 'my_procedure',
                'return_type': None
            },
            {
                'name': 'get_account',
                'return_type': 'RECORD'
            }
        ]
        result = filter_functions_only(functions)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], 'calculate')
        self.assertEqual(result[1]['name'], 'get_account')
    
    def test_exclude_empty_return_type(self):
        """Test that functions with empty return type are excluded."""
        functions = [
            {
                'name': 'calculate',
                'return_type': 'DECIMAL'
            },
            {
                'name': 'my_procedure',
                'return_type': ''
            }
        ]
        result = filter_functions_only(functions)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], 'calculate')
    
    def test_keep_all_functions(self):
        """Test that all functions are kept when no procedures."""
        functions = [
            {
                'name': 'calculate',
                'return_type': 'DECIMAL'
            },
            {
                'name': 'get_account',
                'return_type': 'RECORD'
            }
        ]
        result = filter_functions_only(functions)
        self.assertEqual(len(result), 2)
    
    def test_empty_list(self):
        """Test filter with empty function list."""
        result = filter_functions_only([])
        self.assertEqual(len(result), 0)
    
    def test_all_procedures(self):
        """Test filter when all are procedures."""
        functions = [
            {
                'name': 'proc1',
                'return_type': None
            },
            {
                'name': 'proc2',
                'return_type': ''
            }
        ]
        result = filter_functions_only(functions)
        self.assertEqual(len(result), 0)
    
    def test_non_destructive(self):
        """Test that filter doesn't modify original list."""
        functions = [
            {
                'name': 'calculate',
                'return_type': 'DECIMAL'
            },
            {
                'name': 'my_procedure',
                'return_type': None
            }
        ]
        original_len = len(functions)
        result = filter_functions_only(functions)
        self.assertEqual(len(functions), original_len)


class TestFilterNoMetrics(unittest.TestCase):
    """Test filter_no_metrics function."""
    
    def test_remove_complexity_and_loc(self):
        """Test that complexity and LOC are removed."""
        functions = [
            {
                'name': 'calculate',
                'complexity': 5,
                'loc': 23
            }
        ]
        result = filter_no_metrics(functions)
        self.assertNotIn('complexity', result[0])
        self.assertNotIn('loc', result[0])
    
    def test_keep_other_fields(self):
        """Test that other fields are kept."""
        functions = [
            {
                'name': 'calculate',
                'return_type': 'DECIMAL',
                'file_path': 'src/math.4gl',
                'complexity': 5,
                'loc': 23
            }
        ]
        result = filter_no_metrics(functions)
        self.assertEqual(result[0]['name'], 'calculate')
        self.assertEqual(result[0]['return_type'], 'DECIMAL')
        self.assertEqual(result[0]['file_path'], 'src/math.4gl')
    
    def test_missing_metrics(self):
        """Test filter when metrics are missing."""
        functions = [
            {
                'name': 'calculate',
                'return_type': 'DECIMAL'
            }
        ]
        result = filter_no_metrics(functions)
        self.assertEqual(len(result), 1)
        self.assertNotIn('complexity', result[0])
        self.assertNotIn('loc', result[0])
    
    def test_multiple_functions(self):
        """Test filter with multiple functions."""
        functions = [
            {
                'name': 'calculate',
                'complexity': 5,
                'loc': 23
            },
            {
                'name': 'get_account',
                'complexity': 3,
                'loc': 15
            }
        ]
        result = filter_no_metrics(functions)
        self.assertEqual(len(result), 2)
        for func in result:
            self.assertNotIn('complexity', func)
            self.assertNotIn('loc', func)
    
    def test_non_destructive(self):
        """Test that filter doesn't modify original list."""
        functions = [
            {
                'name': 'calculate',
                'complexity': 5,
                'loc': 23
            }
        ]
        original_complexity = functions[0]['complexity']
        result = filter_no_metrics(functions)
        self.assertEqual(functions[0]['complexity'], original_complexity)


class TestFilterNoFileInfo(unittest.TestCase):
    """Test filter_no_file_info function."""
    
    def test_remove_file_path_and_line(self):
        """Test that file path and line number are removed."""
        functions = [
            {
                'name': 'calculate',
                'file_path': 'src/math.4gl',
                'line_number': 42
            }
        ]
        result = filter_no_file_info(functions)
        self.assertNotIn('file_path', result[0])
        self.assertNotIn('line_number', result[0])
    
    def test_keep_other_fields(self):
        """Test that other fields are kept."""
        functions = [
            {
                'name': 'calculate',
                'return_type': 'DECIMAL',
                'complexity': 5,
                'loc': 23,
                'file_path': 'src/math.4gl',
                'line_number': 42
            }
        ]
        result = filter_no_file_info(functions)
        self.assertEqual(result[0]['name'], 'calculate')
        self.assertEqual(result[0]['return_type'], 'DECIMAL')
        self.assertEqual(result[0]['complexity'], 5)
        self.assertEqual(result[0]['loc'], 23)
    
    def test_missing_file_info(self):
        """Test filter when file info is missing."""
        functions = [
            {
                'name': 'calculate',
                'return_type': 'DECIMAL'
            }
        ]
        result = filter_no_file_info(functions)
        self.assertEqual(len(result), 1)
        self.assertNotIn('file_path', result[0])
        self.assertNotIn('line_number', result[0])
    
    def test_multiple_functions(self):
        """Test filter with multiple functions."""
        functions = [
            {
                'name': 'calculate',
                'file_path': 'src/math.4gl',
                'line_number': 42
            },
            {
                'name': 'get_account',
                'file_path': 'src/queries.4gl',
                'line_number': 128
            }
        ]
        result = filter_no_file_info(functions)
        self.assertEqual(len(result), 2)
        for func in result:
            self.assertNotIn('file_path', func)
            self.assertNotIn('line_number', func)
    
    def test_non_destructive(self):
        """Test that filter doesn't modify original list."""
        functions = [
            {
                'name': 'calculate',
                'file_path': 'src/math.4gl',
                'line_number': 42
            }
        ]
        original_file = functions[0]['file_path']
        result = filter_no_file_info(functions)
        self.assertEqual(functions[0]['file_path'], original_file)


class TestApplyFilters(unittest.TestCase):
    """Test apply_filters function."""
    
    def setUp(self):
        """Set up test data."""
        self.functions = [
            {
                'name': 'calculate',
                'return_type': 'DECIMAL',
                'file_path': 'src/math.4gl',
                'line_number': 42,
                'complexity': 5,
                'loc': 23
            },
            {
                'name': 'my_procedure',
                'return_type': None,
                'file_path': 'src/utils.4gl',
                'line_number': 100,
                'complexity': 2,
                'loc': 10
            },
            {
                'name': 'get_account',
                'return_type': 'RECORD',
                'file_path': 'src/queries.4gl',
                'line_number': 128,
                'complexity': 3,
                'loc': 15
            }
        ]
    
    def test_single_filter(self):
        """Test apply_filters with single filter."""
        result = apply_filters(self.functions, ['functions-only'])
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], 'calculate')
        self.assertEqual(result[1]['name'], 'get_account')
    
    def test_multiple_filters(self):
        """Test apply_filters with multiple filters."""
        result = apply_filters(self.functions, ['functions-only', 'no-metrics'])
        self.assertEqual(len(result), 2)
        for func in result:
            self.assertNotIn('complexity', func)
            self.assertNotIn('loc', func)
    
    def test_all_filters(self):
        """Test apply_filters with all filters."""
        result = apply_filters(self.functions, [
            'functions-only',
            'no-metrics',
            'no-file-info'
        ])
        self.assertEqual(len(result), 2)
        for func in result:
            self.assertNotIn('complexity', func)
            self.assertNotIn('loc', func)
            self.assertNotIn('file_path', func)
            self.assertNotIn('line_number', func)
    
    def test_case_insensitive_filters(self):
        """Test apply_filters is case-insensitive."""
        result1 = apply_filters(self.functions, ['functions-only'])
        result2 = apply_filters(self.functions, ['Functions-Only'])
        result3 = apply_filters(self.functions, ['FUNCTIONS-ONLY'])
        self.assertEqual(len(result1), len(result2))
        self.assertEqual(len(result2), len(result3))
    
    def test_invalid_filter(self):
        """Test apply_filters with invalid filter."""
        with self.assertRaises(ValueError) as context:
            apply_filters(self.functions, ['invalid-filter'])
        self.assertIn('Invalid filter', str(context.exception))
    
    def test_empty_filters(self):
        """Test apply_filters with empty filter list."""
        result = apply_filters(self.functions, [])
        self.assertEqual(len(result), len(self.functions))
    
    def test_filter_order_independence(self):
        """Test that filter order doesn't matter."""
        result1 = apply_filters(self.functions, ['functions-only', 'no-metrics'])
        result2 = apply_filters(self.functions, ['no-metrics', 'functions-only'])
        # Both should have same number of results
        self.assertEqual(len(result1), len(result2))


class TestValidateFilters(unittest.TestCase):
    """Test validate_filters function."""
    
    def test_valid_filters(self):
        """Test validate_filters with valid filters."""
        # Should not raise
        validate_filters(['functions-only'])
        validate_filters(['no-metrics'])
        validate_filters(['no-file-info'])
        validate_filters(['functions-only', 'no-metrics'])
    
    def test_case_insensitive_validation(self):
        """Test validate_filters is case-insensitive."""
        # Should not raise
        validate_filters(['Functions-Only'])
        validate_filters(['NO-METRICS'])
        validate_filters(['No-File-Info'])
    
    def test_invalid_filter(self):
        """Test validate_filters with invalid filter."""
        with self.assertRaises(ValueError) as context:
            validate_filters(['invalid-filter'])
        self.assertIn('Invalid filter', str(context.exception))
    
    def test_mixed_valid_invalid(self):
        """Test validate_filters with mix of valid and invalid."""
        with self.assertRaises(ValueError):
            validate_filters(['functions-only', 'invalid-filter'])
    
    def test_empty_list(self):
        """Test validate_filters with empty list."""
        # Should not raise
        validate_filters([])


if __name__ == '__main__':
    unittest.main()
