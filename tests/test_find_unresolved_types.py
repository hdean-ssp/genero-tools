#!/usr/bin/env python3
"""Tests for find_unresolved_types() function."""

import sqlite3
import sys
import tempfile
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from query_db import find_unresolved_types


def create_test_db():
    """Create a test database with unresolved types."""
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Create files table
    c.execute('''CREATE TABLE files (
        id INTEGER PRIMARY KEY,
        path TEXT NOT NULL
    )''')
    
    # Create functions table
    c.execute('''CREATE TABLE functions (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        file_id INTEGER NOT NULL,
        signature TEXT,
        line_start INTEGER,
        line_end INTEGER,
        FOREIGN KEY(file_id) REFERENCES files(id)
    )''')
    
    # Create parameters table with resolved type columns
    c.execute('''CREATE TABLE parameters (
        id INTEGER PRIMARY KEY,
        function_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        type TEXT,
        actual_type TEXT,
        is_like_reference INTEGER DEFAULT 0,
        resolved INTEGER DEFAULT 0,
        resolution_error TEXT,
        table_name TEXT,
        columns TEXT,
        types TEXT,
        FOREIGN KEY(function_id) REFERENCES functions(id)
    )''')
    
    # Create returns table with resolved type columns
    c.execute('''CREATE TABLE returns (
        id INTEGER PRIMARY KEY,
        function_id INTEGER NOT NULL,
        name TEXT,
        type TEXT,
        actual_type TEXT,
        is_like_reference INTEGER DEFAULT 0,
        resolved INTEGER DEFAULT 0,
        resolution_error TEXT,
        table_name TEXT,
        columns TEXT,
        types TEXT,
        FOREIGN KEY(function_id) REFERENCES functions(id)
    )''')
    
    # Insert test data
    # File 1
    c.execute("INSERT INTO files (path) VALUES (?)", ("./src/utils.4gl",))
    file1_id = c.lastrowid
    
    # File 2
    c.execute("INSERT INTO files (path) VALUES (?)", ("./src/core.4gl",))
    file2_id = c.lastrowid
    
    # Function 1: validate_input in file 1
    c.execute("INSERT INTO functions (name, file_id, signature) VALUES (?, ?, ?)",
              ("validate_input", file1_id, "FUNCTION validate_input(p1)"))
    func1_id = c.lastrowid
    
    # Function 2: process_data in file 2
    c.execute("INSERT INTO functions (name, file_id, signature) VALUES (?, ?, ?)",
              ("process_data", file2_id, "FUNCTION process_data(p1) RETURNS STRING"))
    func2_id = c.lastrowid
    
    # Function 3: another_func in file 1
    c.execute("INSERT INTO functions (name, file_id, signature) VALUES (?, ?, ?)",
              ("another_func", file1_id, "FUNCTION another_func(p1)"))
    func3_id = c.lastrowid
    
    # Unresolved parameter in func1: missing table
    c.execute('''INSERT INTO parameters 
                 (function_id, name, type, is_like_reference, resolved, resolution_error)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (func1_id, "param1", "LIKE missing_table.*", 1, 0, "Table not found: missing_table"))
    
    # Unresolved parameter in func2: missing column
    c.execute('''INSERT INTO parameters 
                 (function_id, name, type, is_like_reference, resolved, resolution_error)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (func2_id, "param2", "LIKE table.missing_col", 1, 0, "Column not found: table.missing_col"))
    
    # Unresolved return in func2: missing table
    c.execute('''INSERT INTO returns 
                 (function_id, name, type, is_like_reference, resolved, resolution_error)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (func2_id, None, "LIKE invalid_table.*", 1, 0, "Table not found: invalid_table"))
    
    # Unresolved parameter in func3: invalid pattern
    c.execute('''INSERT INTO parameters 
                 (function_id, name, type, is_like_reference, resolved, resolution_error)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (func3_id, "param3", "LIKE invalid", 1, 0, "Invalid pattern: invalid"))
    
    # Resolved parameter (should not be returned)
    c.execute('''INSERT INTO parameters 
                 (function_id, name, type, is_like_reference, resolved, resolution_error)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (func1_id, "param_resolved", "LIKE table.*", 1, 1, None))
    
    conn.commit()
    conn.close()
    
    return db_path


def test_find_unresolved_types_all():
    """Test finding all unresolved types."""
    db_path = create_test_db()
    
    try:
        results = find_unresolved_types(db_path)
        
        # Should return 4 unresolved types (3 parameters + 1 return)
        assert len(results) == 4, f"Expected 4 results, got {len(results)}"
        
        # Check that all required fields are present
        for result in results:
            assert 'function_name' in result
            assert 'file_path' in result
            assert 'type_name' in result
            assert 'original_type' in result
            assert 'error_reason' in result
            assert 'error_type' in result
            assert 'source' in result
        
        # Check specific results
        func_names = [r['function_name'] for r in results]
        assert 'validate_input' in func_names
        assert 'process_data' in func_names
        assert 'another_func' in func_names
        
        print("✓ test_find_unresolved_types_all passed")
    finally:
        Path(db_path).unlink()


def test_find_unresolved_types_filter_missing_table():
    """Test filtering by missing_table error type."""
    db_path = create_test_db()
    
    try:
        results = find_unresolved_types(db_path, filter_type='missing_table')
        
        # Should return 2 results (param1 and return in func2)
        assert len(results) == 2, f"Expected 2 results, got {len(results)}"
        
        # All should have error_type = 'missing_table'
        for result in results:
            assert result['error_type'] == 'missing_table', f"Expected missing_table, got {result['error_type']}"
        
        print("✓ test_find_unresolved_types_filter_missing_table passed")
    finally:
        Path(db_path).unlink()


def test_find_unresolved_types_filter_missing_column():
    """Test filtering by missing_column error type."""
    db_path = create_test_db()
    
    try:
        results = find_unresolved_types(db_path, filter_type='missing_column')
        
        # Should return 1 result (param2 in func2)
        assert len(results) == 1, f"Expected 1 result, got {len(results)}"
        assert results[0]['error_type'] == 'missing_column'
        assert results[0]['function_name'] == 'process_data'
        
        print("✓ test_find_unresolved_types_filter_missing_column passed")
    finally:
        Path(db_path).unlink()


def test_find_unresolved_types_filter_invalid_pattern():
    """Test filtering by invalid_pattern error type."""
    db_path = create_test_db()
    
    try:
        results = find_unresolved_types(db_path, filter_type='invalid_pattern')
        
        # Should return 1 result (param3 in func3)
        assert len(results) == 1, f"Expected 1 result, got {len(results)}"
        assert results[0]['error_type'] == 'invalid_pattern'
        assert results[0]['function_name'] == 'another_func'
        
        print("✓ test_find_unresolved_types_filter_invalid_pattern passed")
    finally:
        Path(db_path).unlink()


def test_find_unresolved_types_pagination_limit():
    """Test pagination with limit."""
    db_path = create_test_db()
    
    try:
        results = find_unresolved_types(db_path, limit=2)
        
        # Should return 2 results
        assert len(results) == 2, f"Expected 2 results, got {len(results)}"
        
        print("✓ test_find_unresolved_types_pagination_limit passed")
    finally:
        Path(db_path).unlink()


def test_find_unresolved_types_pagination_offset():
    """Test pagination with offset."""
    db_path = create_test_db()
    
    try:
        # Get all results
        all_results = find_unresolved_types(db_path)
        
        # Get results with offset
        results = find_unresolved_types(db_path, offset=2)
        
        # Should return 2 results (4 total - 2 offset)
        assert len(results) == 2, f"Expected 2 results, got {len(results)}"
        
        # Results should be different from first 2
        all_names = [r['function_name'] for r in all_results]
        offset_names = [r['function_name'] for r in results]
        
        print("✓ test_find_unresolved_types_pagination_offset passed")
    finally:
        Path(db_path).unlink()


def test_find_unresolved_types_pagination_limit_offset():
    """Test pagination with both limit and offset."""
    db_path = create_test_db()
    
    try:
        results = find_unresolved_types(db_path, limit=2, offset=1)
        
        # Should return 2 results (starting from position 1)
        assert len(results) == 2, f"Expected 2 results, got {len(results)}"
        
        print("✓ test_find_unresolved_types_pagination_limit_offset passed")
    finally:
        Path(db_path).unlink()


def test_find_unresolved_types_excludes_resolved():
    """Test that resolved types are excluded."""
    db_path = create_test_db()
    
    try:
        results = find_unresolved_types(db_path)
        
        # Should not include param_resolved
        param_names = [r['type_name'] for r in results]
        assert 'param_resolved' not in param_names, "Resolved parameter should not be included"
        
        print("✓ test_find_unresolved_types_excludes_resolved passed")
    finally:
        Path(db_path).unlink()


def test_find_unresolved_types_source_field():
    """Test that source field correctly identifies parameters vs returns."""
    db_path = create_test_db()
    
    try:
        results = find_unresolved_types(db_path)
        
        # Check that source field is set correctly
        for result in results:
            assert result['source'] in ['parameter', 'return'], f"Invalid source: {result['source']}"
        
        # Count parameters and returns
        param_count = sum(1 for r in results if r['source'] == 'parameter')
        return_count = sum(1 for r in results if r['source'] == 'return')
        
        assert param_count == 3, f"Expected 3 parameters, got {param_count}"
        assert return_count == 1, f"Expected 1 return, got {return_count}"
        
        print("✓ test_find_unresolved_types_source_field passed")
    finally:
        Path(db_path).unlink()


if __name__ == '__main__':
    test_find_unresolved_types_all()
    test_find_unresolved_types_filter_missing_table()
    test_find_unresolved_types_filter_missing_column()
    test_find_unresolved_types_filter_invalid_pattern()
    test_find_unresolved_types_pagination_limit()
    test_find_unresolved_types_pagination_offset()
    test_find_unresolved_types_pagination_limit_offset()
    test_find_unresolved_types_excludes_resolved()
    test_find_unresolved_types_source_field()
    print("\n✓ All tests passed!")
