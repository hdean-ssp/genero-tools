#!/usr/bin/env python3
"""Verify find_unresolved_types() meets all requirements."""

import sqlite3
import sys
import tempfile
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from query_db import find_unresolved_types


def create_comprehensive_test_db():
    """Create a comprehensive test database with various unresolved types."""
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Create tables
    c.execute('''CREATE TABLE files (
        id INTEGER PRIMARY KEY,
        path TEXT NOT NULL
    )''')
    
    c.execute('''CREATE TABLE functions (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        file_id INTEGER NOT NULL,
        signature TEXT,
        FOREIGN KEY(file_id) REFERENCES files(id)
    )''')
    
    c.execute('''CREATE TABLE parameters (
        id INTEGER PRIMARY KEY,
        function_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        type TEXT,
        is_like_reference INTEGER DEFAULT 0,
        resolved INTEGER DEFAULT 0,
        resolution_error TEXT,
        FOREIGN KEY(function_id) REFERENCES functions(id)
    )''')
    
    c.execute('''CREATE TABLE returns (
        id INTEGER PRIMARY KEY,
        function_id INTEGER NOT NULL,
        name TEXT,
        type TEXT,
        is_like_reference INTEGER DEFAULT 0,
        resolved INTEGER DEFAULT 0,
        resolution_error TEXT,
        FOREIGN KEY(function_id) REFERENCES functions(id)
    )''')
    
    # Insert test data
    c.execute("INSERT INTO files (path) VALUES (?)", ("./src/file1.4gl",))
    file1_id = c.lastrowid
    
    c.execute("INSERT INTO files (path) VALUES (?)", ("./src/file2.4gl",))
    file2_id = c.lastrowid
    
    # Function 1: has unresolved parameter (missing table)
    c.execute("INSERT INTO functions (name, file_id, signature) VALUES (?, ?, ?)",
              ("func1", file1_id, "FUNCTION func1(p1)"))
    func1_id = c.lastrowid
    
    c.execute('''INSERT INTO parameters 
                 (function_id, name, type, is_like_reference, resolved, resolution_error)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (func1_id, "param1", "LIKE missing_table.*", 1, 0, "Table not found: missing_table"))
    
    # Function 2: has unresolved return (missing column)
    c.execute("INSERT INTO functions (name, file_id, signature) VALUES (?, ?, ?)",
              ("func2", file2_id, "FUNCTION func2() RETURNS STRING"))
    func2_id = c.lastrowid
    
    c.execute('''INSERT INTO returns 
                 (function_id, name, type, is_like_reference, resolved, resolution_error)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (func2_id, None, "LIKE table.missing_col", 1, 0, "Column not found: table.missing_col"))
    
    # Function 3: has multiple unresolved parameters
    c.execute("INSERT INTO functions (name, file_id, signature) VALUES (?, ?, ?)",
              ("func3", file1_id, "FUNCTION func3(p1, p2)"))
    func3_id = c.lastrowid
    
    c.execute('''INSERT INTO parameters 
                 (function_id, name, type, is_like_reference, resolved, resolution_error)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (func3_id, "param1", "LIKE invalid_table.*", 1, 0, "Table not found: invalid_table"))
    
    c.execute('''INSERT INTO parameters 
                 (function_id, name, type, is_like_reference, resolved, resolution_error)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (func3_id, "param2", "LIKE table.invalid_col", 1, 0, "Column not found: table.invalid_col"))
    
    # Function 4: has resolved parameter (should not be returned)
    c.execute("INSERT INTO functions (name, file_id, signature) VALUES (?, ?, ?)",
              ("func4", file2_id, "FUNCTION func4(p1)"))
    func4_id = c.lastrowid
    
    c.execute('''INSERT INTO parameters 
                 (function_id, name, type, is_like_reference, resolved, resolution_error)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (func4_id, "param1", "LIKE table.*", 1, 1, None))
    
    conn.commit()
    conn.close()
    
    return db_path


def test_requirement_5_1():
    """Requirement 5.1: find_unresolved_types() returns all unresolved LIKE references."""
    db_path = create_comprehensive_test_db()
    
    try:
        results = find_unresolved_types(db_path)
        
        # Should return 4 unresolved types (3 parameters + 1 return)
        assert len(results) == 4, f"Expected 4 results, got {len(results)}"
        
        # Verify all required fields are present
        required_fields = ['function_name', 'file_path', 'type_name', 'original_type', 'error_reason', 'error_type', 'source']
        for result in results:
            for field in required_fields:
                assert field in result, f"Missing field: {field}"
        
        print("✓ Requirement 5.1: find_unresolved_types() returns all unresolved LIKE references")
    finally:
        Path(db_path).unlink()


def test_requirement_5_2():
    """Requirement 5.2: Returns all parameters with unresolved LIKE references."""
    db_path = create_comprehensive_test_db()
    
    try:
        results = find_unresolved_types(db_path)
        
        # Count parameters
        param_results = [r for r in results if r['source'] == 'parameter']
        assert len(param_results) == 3, f"Expected 3 parameters, got {len(param_results)}"
        
        print("✓ Requirement 5.2: Returns all parameters with unresolved LIKE references")
    finally:
        Path(db_path).unlink()


def test_requirement_5_3():
    """Requirement 5.3: Returns all return types with unresolved LIKE references."""
    db_path = create_comprehensive_test_db()
    
    try:
        results = find_unresolved_types(db_path)
        
        # Count returns
        return_results = [r for r in results if r['source'] == 'return']
        assert len(return_results) == 1, f"Expected 1 return, got {len(return_results)}"
        
        print("✓ Requirement 5.3: Returns all return types with unresolved LIKE references")
    finally:
        Path(db_path).unlink()


def test_requirement_5_4():
    """Requirement 5.4: Returns results with required fields."""
    db_path = create_comprehensive_test_db()
    
    try:
        results = find_unresolved_types(db_path)
        
        # Verify required fields
        for result in results:
            assert 'function_name' in result
            assert 'file_path' in result
            assert 'type_name' in result
            assert 'original_type' in result
            assert 'error_reason' in result
            assert result['function_name'] is not None
            assert result['file_path'] is not None
            assert result['original_type'] is not None
        
        print("✓ Requirement 5.4: Returns results with required fields")
    finally:
        Path(db_path).unlink()


def test_requirement_5_5():
    """Requirement 5.5: Supports filtering by error type."""
    db_path = create_comprehensive_test_db()
    
    try:
        # Test missing_table filter
        results = find_unresolved_types(db_path, filter_type='missing_table')
        assert len(results) == 2, f"Expected 2 missing_table results, got {len(results)}"
        for result in results:
            assert result['error_type'] == 'missing_table'
        
        # Test missing_column filter
        results = find_unresolved_types(db_path, filter_type='missing_column')
        assert len(results) == 2, f"Expected 2 missing_column results, got {len(results)}"
        for result in results:
            assert result['error_type'] == 'missing_column'
        
        # Test invalid_pattern filter (should return 0)
        results = find_unresolved_types(db_path, filter_type='invalid_pattern')
        assert len(results) == 0, f"Expected 0 invalid_pattern results, got {len(results)}"
        
        print("✓ Requirement 5.5: Supports filtering by error type")
    finally:
        Path(db_path).unlink()


def test_requirement_5_6():
    """Requirement 5.6: Supports pagination with limit and offset."""
    db_path = create_comprehensive_test_db()
    
    try:
        # Test limit
        results = find_unresolved_types(db_path, limit=2)
        assert len(results) == 2, f"Expected 2 results with limit=2, got {len(results)}"
        
        # Test offset
        results = find_unresolved_types(db_path, offset=2)
        assert len(results) == 2, f"Expected 2 results with offset=2, got {len(results)}"
        
        # Test limit and offset
        results = find_unresolved_types(db_path, limit=1, offset=1)
        assert len(results) == 1, f"Expected 1 result with limit=1, offset=1, got {len(results)}"
        
        print("✓ Requirement 5.6: Supports pagination with limit and offset")
    finally:
        Path(db_path).unlink()


def test_backward_compatibility():
    """Verify backward compatibility with existing find_unresolved_like_references()."""
    db_path = create_comprehensive_test_db()
    
    try:
        from query_db import find_unresolved_like_references
        
        # Call the old function
        results = find_unresolved_like_references(db_path)
        
        # Should return 3 unresolved parameters
        assert len(results) == 3, f"Expected 3 results, got {len(results)}"
        
        # Verify old format
        for result in results:
            assert 'function' in result
            assert 'file' in result
            assert 'parameter' in result
            assert 'type' in result
        
        print("✓ Backward compatibility: find_unresolved_like_references() still works")
    finally:
        Path(db_path).unlink()


if __name__ == '__main__':
    test_requirement_5_1()
    test_requirement_5_2()
    test_requirement_5_3()
    test_requirement_5_4()
    test_requirement_5_5()
    test_requirement_5_6()
    test_backward_compatibility()
    print("\n✓ All requirements verified!")
