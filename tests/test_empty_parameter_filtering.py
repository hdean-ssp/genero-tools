#!/usr/bin/env python3
"""Tests for empty parameter filtering in json_to_sqlite.py"""

import json
import sqlite3
import tempfile
import os
import sys
import logging
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from json_to_sqlite import create_signatures_db

class TestEmptyParameterFiltering:
    """Test suite for empty parameter filtering."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.json_file = os.path.join(self.temp_dir, 'test.json')
        self.db_file = os.path.join(self.temp_dir, 'test.db')
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if os.path.exists(self.json_file):
            os.remove(self.json_file)
        if os.path.exists(self.db_file):
            os.remove(self.db_file)
        os.rmdir(self.temp_dir)
    
    def test_empty_parameters_are_skipped(self):
        """Test that empty parameters are skipped during insertion."""
        # Create test data with empty parameters
        test_data = {
            "_metadata": {"version": "1.0.0"},
            "./test.4gl": [
                {
                    "name": "test_func",
                    "line": {"start": 1, "end": 5},
                    "signature": "1-5: test_func(p1, p2)",
                    "parameters": [
                        {"name": "p1", "type": "STRING"},
                        {"name": "", "type": "INTEGER"},  # Empty name
                        {"name": None, "type": "DECIMAL"},  # None name
                        {"name": "   ", "type": "BOOLEAN"},  # Whitespace only
                        {"name": "p2", "type": "FLOAT"}
                    ],
                    "returns": [],
                    "calls": []
                }
            ]
        }
        
        # Write test data
        with open(self.json_file, 'w') as f:
            json.dump(test_data, f)
        
        # Process with json_to_sqlite
        create_signatures_db(self.json_file, self.db_file)
        
        # Verify results
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        
        # Get function ID
        c.execute('SELECT id FROM functions WHERE name = ?', ('test_func',))
        func_id = c.fetchone()[0]
        
        # Get parameters
        c.execute('SELECT name, type FROM parameters WHERE function_id = ? ORDER BY id', (func_id,))
        params = c.fetchall()
        
        conn.close()
        
        # Should only have 2 parameters (p1 and p2)
        assert len(params) == 2, f"Expected 2 parameters, got {len(params)}"
        assert params[0] == ('p1', 'STRING'), f"First parameter mismatch: {params[0]}"
        assert params[1] == ('p2', 'FLOAT'), f"Second parameter mismatch: {params[1]}"
    
    def test_parameter_count_accuracy(self):
        """Test that parameter counts are accurate after filtering."""
        test_data = {
            "_metadata": {"version": "1.0.0"},
            "./test.4gl": [
                {
                    "name": "func_with_mixed_params",
                    "line": {"start": 1, "end": 10},
                    "signature": "1-10: func_with_mixed_params(a, b, c)",
                    "parameters": [
                        {"name": "a", "type": "STRING"},
                        {"name": "", "type": "INTEGER"},
                        {"name": "b", "type": "DECIMAL"},
                        {"name": "", "type": "BOOLEAN"},
                        {"name": "c", "type": "FLOAT"}
                    ],
                    "returns": [],
                    "calls": []
                }
            ]
        }
        
        with open(self.json_file, 'w') as f:
            json.dump(test_data, f)
        
        create_signatures_db(self.json_file, self.db_file)
        
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        
        c.execute('SELECT id FROM functions WHERE name = ?', ('func_with_mixed_params',))
        func_id = c.fetchone()[0]
        
        c.execute('SELECT COUNT(*) FROM parameters WHERE function_id = ?', (func_id,))
        param_count = c.fetchone()[0]
        
        conn.close()
        
        # Should have exactly 3 parameters (a, b, c)
        assert param_count == 3, f"Expected 3 parameters, got {param_count}"
    
    def test_function_with_all_empty_parameters(self):
        """Test that a function with all empty parameters is inserted with zero parameters."""
        test_data = {
            "_metadata": {"version": "1.0.0"},
            "./test.4gl": [
                {
                    "name": "func_no_params",
                    "line": {"start": 1, "end": 5},
                    "signature": "1-5: func_no_params()",
                    "parameters": [
                        {"name": "", "type": "STRING"},
                        {"name": None, "type": "INTEGER"}
                    ],
                    "returns": [],
                    "calls": []
                }
            ]
        }
        
        with open(self.json_file, 'w') as f:
            json.dump(test_data, f)
        
        create_signatures_db(self.json_file, self.db_file)
        
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        
        # Function should exist
        c.execute('SELECT id FROM functions WHERE name = ?', ('func_no_params',))
        func_id = c.fetchone()
        assert func_id is not None, "Function should be inserted"
        
        # But have no parameters
        c.execute('SELECT COUNT(*) FROM parameters WHERE function_id = ?', (func_id[0],))
        param_count = c.fetchone()[0]
        
        conn.close()
        
        assert param_count == 0, f"Expected 0 parameters, got {param_count}"
    
    def test_file_path_stored_in_functions_table(self):
        """Test that file_path is stored in the functions table."""
        test_data = {
            "_metadata": {"version": "1.0.0"},
            "./path/to/test.4gl": [
                {
                    "name": "test_func",
                    "line": {"start": 1, "end": 5},
                    "signature": "1-5: test_func()",
                    "parameters": [],
                    "returns": [],
                    "calls": []
                }
            ]
        }
        
        with open(self.json_file, 'w') as f:
            json.dump(test_data, f)
        
        create_signatures_db(self.json_file, self.db_file)
        
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        
        c.execute('SELECT file_path FROM functions WHERE name = ?', ('test_func',))
        file_path = c.fetchone()[0]
        
        conn.close()
        
        assert file_path == "./path/to/test.4gl", f"Expected file_path './path/to/test.4gl', got '{file_path}'"
    
    def test_not_null_constraint_on_parameters(self):
        """Test that NOT NULL constraint is enforced on parameter names."""
        test_data = {
            "_metadata": {"version": "1.0.0"},
            "./test.4gl": [
                {
                    "name": "test_func",
                    "line": {"start": 1, "end": 5},
                    "signature": "1-5: test_func()",
                    "parameters": [],
                    "returns": [],
                    "calls": []
                }
            ]
        }
        
        with open(self.json_file, 'w') as f:
            json.dump(test_data, f)
        
        create_signatures_db(self.json_file, self.db_file)
        
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        
        # Try to insert a parameter with NULL name - should fail
        c.execute('SELECT id FROM functions WHERE name = ?', ('test_func',))
        func_id = c.fetchone()[0]
        
        try:
            c.execute('INSERT INTO parameters (function_id, name, type) VALUES (?, ?, ?)',
                     (func_id, None, 'STRING'))
            conn.commit()
            assert False, "Should have raised an error for NULL parameter name"
        except sqlite3.IntegrityError:
            # Expected - NOT NULL constraint should be enforced
            pass
        finally:
            conn.close()
    
    def test_warning_logged_for_empty_parameters(self, caplog):
        """Test that warnings are logged for each skipped empty parameter."""
        test_data = {
            "_metadata": {"version": "1.0.0"},
            "./test.4gl": [
                {
                    "name": "test_func",
                    "line": {"start": 1, "end": 5},
                    "signature": "1-5: test_func()",
                    "parameters": [
                        {"name": "", "type": "STRING"},
                        {"name": None, "type": "INTEGER"}
                    ],
                    "returns": [],
                    "calls": []
                }
            ]
        }
        
        with open(self.json_file, 'w') as f:
            json.dump(test_data, f)
        
        # Capture logging output
        with caplog.at_level(logging.WARNING):
            create_signatures_db(self.json_file, self.db_file)
        
        # Check that warnings were logged
        warning_messages = [record.message for record in caplog.records if record.levelname == 'WARNING']
        
        # Should have warnings for the 2 empty parameters plus the total count
        assert len(warning_messages) >= 2, f"Expected at least 2 warnings, got {len(warning_messages)}"
        assert any('empty parameter' in msg.lower() for msg in warning_messages), \
            f"Expected warning about empty parameter, got: {warning_messages}"
        assert any('test_func' in msg for msg in warning_messages), \
            f"Expected function name in warning, got: {warning_messages}"


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
