#!/usr/bin/env python3
"""Manual test for empty parameter filtering in json_to_sqlite.py"""

import json
import sqlite3
import tempfile
import os
import sys
import logging
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from json_to_sqlite import create_signatures_db, is_valid_parameter_name

def test_is_valid_parameter_name():
    """Test the validation function."""
    print("Testing is_valid_parameter_name()...")
    
    # Valid names
    assert is_valid_parameter_name("param1") == True, "Should accept valid name"
    assert is_valid_parameter_name("p") == True, "Should accept single char"
    assert is_valid_parameter_name("  param  ") == True, "Should accept name with whitespace"
    
    # Invalid names
    assert is_valid_parameter_name("") == False, "Should reject empty string"
    assert is_valid_parameter_name(None) == False, "Should reject None"
    assert is_valid_parameter_name("   ") == False, "Should reject whitespace-only"
    
    print("✓ is_valid_parameter_name() tests passed")

def test_empty_parameters_are_skipped():
    """Test that empty parameters are skipped during insertion."""
    print("\nTesting empty parameter filtering...")
    
    temp_dir = tempfile.mkdtemp()
    json_file = os.path.join(temp_dir, 'test.json')
    db_file = os.path.join(temp_dir, 'test.db')
    
    try:
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
        with open(json_file, 'w') as f:
            json.dump(test_data, f)
        
        # Process with json_to_sqlite
        create_signatures_db(json_file, db_file)
        
        # Verify results
        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        
        # Get function ID
        c.execute('SELECT id FROM functions WHERE name = ?', ('test_func',))
        func_id = c.fetchone()[0]
        
        # Get parameters
        c.execute('SELECT name, type FROM parameters WHERE function_id = ? ORDER BY id', (func_id,))
        params = c.fetchall()
        
        conn.close()
        
        # Should only have 2 parameters (p1 and p2)
        assert len(params) == 2, f"Expected 2 parameters, got {len(params)}: {params}"
        assert params[0] == ('p1', 'STRING'), f"First parameter mismatch: {params[0]}"
        assert params[1] == ('p2', 'FLOAT'), f"Second parameter mismatch: {params[1]}"
        
        print("✓ Empty parameters are correctly skipped")
        
    finally:
        if os.path.exists(json_file):
            os.remove(json_file)
        if os.path.exists(db_file):
            os.remove(db_file)
        os.rmdir(temp_dir)

def test_parameter_count_accuracy():
    """Test that parameter counts are accurate after filtering."""
    print("\nTesting parameter count accuracy...")
    
    temp_dir = tempfile.mkdtemp()
    json_file = os.path.join(temp_dir, 'test.json')
    db_file = os.path.join(temp_dir, 'test.db')
    
    try:
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
        
        with open(json_file, 'w') as f:
            json.dump(test_data, f)
        
        create_signatures_db(json_file, db_file)
        
        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        
        c.execute('SELECT id FROM functions WHERE name = ?', ('func_with_mixed_params',))
        func_id = c.fetchone()[0]
        
        c.execute('SELECT COUNT(*) FROM parameters WHERE function_id = ?', (func_id,))
        param_count = c.fetchone()[0]
        
        conn.close()
        
        # Should have exactly 3 parameters (a, b, c)
        assert param_count == 3, f"Expected 3 parameters, got {param_count}"
        
        print("✓ Parameter counts are accurate")
        
    finally:
        if os.path.exists(json_file):
            os.remove(json_file)
        if os.path.exists(db_file):
            os.remove(db_file)
        os.rmdir(temp_dir)

def test_function_with_all_empty_parameters():
    """Test that a function with all empty parameters is inserted with zero parameters."""
    print("\nTesting function with all empty parameters...")
    
    temp_dir = tempfile.mkdtemp()
    json_file = os.path.join(temp_dir, 'test.json')
    db_file = os.path.join(temp_dir, 'test.db')
    
    try:
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
        
        with open(json_file, 'w') as f:
            json.dump(test_data, f)
        
        create_signatures_db(json_file, db_file)
        
        conn = sqlite3.connect(db_file)
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
        
        print("✓ Function with all empty parameters has zero parameters")
        
    finally:
        if os.path.exists(json_file):
            os.remove(json_file)
        if os.path.exists(db_file):
            os.remove(db_file)
        os.rmdir(temp_dir)

def test_file_path_stored():
    """Test that file_path is stored in the functions table."""
    print("\nTesting file_path storage...")
    
    temp_dir = tempfile.mkdtemp()
    json_file = os.path.join(temp_dir, 'test.json')
    db_file = os.path.join(temp_dir, 'test.db')
    
    try:
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
        
        with open(json_file, 'w') as f:
            json.dump(test_data, f)
        
        create_signatures_db(json_file, db_file)
        
        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        
        c.execute('SELECT file_path FROM functions WHERE name = ?', ('test_func',))
        file_path = c.fetchone()[0]
        
        conn.close()
        
        assert file_path == "./path/to/test.4gl", f"Expected file_path './path/to/test.4gl', got '{file_path}'"
        
        print("✓ file_path is correctly stored")
        
    finally:
        if os.path.exists(json_file):
            os.remove(json_file)
        if os.path.exists(db_file):
            os.remove(db_file)
        os.rmdir(temp_dir)

def test_not_null_constraint():
    """Test that NOT NULL constraint is enforced on parameter names."""
    print("\nTesting NOT NULL constraint...")
    
    temp_dir = tempfile.mkdtemp()
    json_file = os.path.join(temp_dir, 'test.json')
    db_file = os.path.join(temp_dir, 'test.db')
    
    try:
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
        
        with open(json_file, 'w') as f:
            json.dump(test_data, f)
        
        create_signatures_db(json_file, db_file)
        
        conn = sqlite3.connect(db_file)
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
            print("✓ NOT NULL constraint is correctly enforced")
        finally:
            conn.close()
        
    finally:
        if os.path.exists(json_file):
            os.remove(json_file)
        if os.path.exists(db_file):
            os.remove(db_file)
        os.rmdir(temp_dir)

def test_warning_logged():
    """Test that warnings are logged for each skipped empty parameter."""
    print("\nTesting warning logging...")
    
    temp_dir = tempfile.mkdtemp()
    json_file = os.path.join(temp_dir, 'test.json')
    db_file = os.path.join(temp_dir, 'test.db')
    
    try:
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
        
        with open(json_file, 'w') as f:
            json.dump(test_data, f)
        
        # Capture logging output
        import io
        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)
        handler.setLevel(logging.WARNING)
        logger = logging.getLogger()
        logger.addHandler(handler)
        
        create_signatures_db(json_file, db_file)
        
        logger.removeHandler(handler)
        log_output = log_capture.getvalue()
        
        # Check that warnings were logged
        assert 'empty parameter' in log_output.lower(), f"Expected warning about empty parameter, got: {log_output}"
        assert 'test_func' in log_output, f"Expected function name in warning, got: {log_output}"
        assert 'test.4gl' in log_output, f"Expected file path in warning, got: {log_output}"
        assert 'Total empty parameters skipped: 2' in log_output, f"Expected total count in warning, got: {log_output}"
        
        print("✓ Warnings are correctly logged with function name and file path")
        
    finally:
        if os.path.exists(json_file):
            os.remove(json_file)
        if os.path.exists(db_file):
            os.remove(db_file)
        os.rmdir(temp_dir)

if __name__ == '__main__':
    print("=" * 60)
    print("Running manual tests for empty parameter filtering")
    print("=" * 60)
    
    try:
        test_is_valid_parameter_name()
        test_empty_parameters_are_skipped()
        test_parameter_count_accuracy()
        test_function_with_all_empty_parameters()
        test_file_path_stored()
        test_not_null_constraint()
        test_warning_logged()
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        sys.exit(0)
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
