#!/usr/bin/env python3
"""Test data consistency validation for type resolution."""

import json
import sqlite3
import tempfile
import os
import sys

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from query_db import validate_type_resolution

def create_test_db_with_issues():
    """Create a test database with various issues."""
    fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Create tables
    c.execute('''CREATE TABLE files (
        id INTEGER PRIMARY KEY,
        path TEXT UNIQUE NOT NULL
    )''')
    
    c.execute('''CREATE TABLE functions (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        file_id INTEGER NOT NULL,
        file_path TEXT,
        signature TEXT,
        line_start INTEGER,
        line_end INTEGER,
        FOREIGN KEY(file_id) REFERENCES files(id)
    )''')
    
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
    c.execute("INSERT INTO files (path) VALUES (?)", ("test.4gl",))
    file_id = c.lastrowid
    
    # Function 1: with file_path
    c.execute('''INSERT INTO functions (name, file_id, file_path, signature, line_start, line_end)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              ("func1", file_id, "test.4gl", "FUNCTION func1()", 1, 5))
    func1_id = c.lastrowid
    
    # Function 2: without file_path (issue)
    c.execute('''INSERT INTO functions (name, file_id, file_path, signature, line_start, line_end)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              ("func2", file_id, None, "FUNCTION func2()", 6, 10))
    func2_id = c.lastrowid
    
    # Parameters for func1 - valid
    c.execute('''INSERT INTO parameters (function_id, name, type, is_like_reference, resolved)
                 VALUES (?, ?, ?, ?, ?)''',
              (func1_id, "param1", "STRING", 0, 0))
    
    # Parameters for func1 - LIKE reference resolved
    c.execute('''INSERT INTO parameters (function_id, name, type, actual_type, is_like_reference, resolved, table_name, columns, types)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (func1_id, "param2", "LIKE users.*", "users.id,users.name", 1, 1, "users", "id,name", '["INTEGER","STRING"]'))
    
    # Parameters for func1 - LIKE reference unresolved (issue)
    c.execute('''INSERT INTO parameters (function_id, name, type, is_like_reference, resolved, resolution_error)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (func1_id, "param3", "LIKE missing_table.*", 1, 0, "Table 'missing_table' not found"))
    
    # Return types for func1 - valid
    c.execute('''INSERT INTO returns (function_id, name, type, is_like_reference, resolved)
                 VALUES (?, ?, ?, ?, ?)''',
              (func1_id, "result", "STRING", 0, 0))
    
    # Return types for func1 - LIKE reference resolved
    c.execute('''INSERT INTO returns (function_id, name, type, actual_type, is_like_reference, resolved, table_name, columns, types)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (func1_id, "result2", "LIKE orders.*", "orders.id,orders.total", 1, 1, "orders", "id,total", '["INTEGER","DECIMAL"]'))
    
    # Return types for func1 - LIKE reference unresolved (issue)
    c.execute('''INSERT INTO returns (function_id, name, type, is_like_reference, resolved, resolution_error)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (func1_id, "result3", "LIKE missing_table.column", 1, 0, "Column 'column' not found in table 'missing_table'"))
    
    conn.commit()
    conn.close()
    
    return db_path

def test_validate_with_issues():
    """Test validation with various issues."""
    db_path = create_test_db_with_issues()
    
    try:
        report = validate_type_resolution(db_path)
        
        # Verify report structure
        assert 'status' in report, "Report missing 'status' field"
        assert 'issues' in report, "Report missing 'issues' field"
        assert 'summary' in report, "Report missing 'summary' field"
        
        # Verify status is invalid due to issues
        assert report['status'] == 'invalid', f"Expected status 'invalid', got '{report['status']}'"
        
        # Verify issues were detected
        assert len(report['issues']) > 0, "Expected issues to be detected"
        
        # Check for specific issues
        issue_types = {issue['type'] for issue in report['issues']}
        assert 'missing_file_path' in issue_types, "Expected 'missing_file_path' issue"
        assert 'unresolved_parameters' in issue_types, "Expected 'unresolved_parameters' issue"
        assert 'unresolved_returns' in issue_types, "Expected 'unresolved_returns' issue"
        
        # Verify summary statistics
        summary = report['summary']
        assert summary['total_functions'] == 2, f"Expected 2 functions, got {summary['total_functions']}"
        assert summary['functions_without_file_path'] == 1, f"Expected 1 function without file_path, got {summary['functions_without_file_path']}"
        assert summary['total_parameters'] == 3, f"Expected 3 parameters, got {summary['total_parameters']}"
        assert summary['parameters_with_like_reference'] == 2, f"Expected 2 LIKE parameters, got {summary['parameters_with_like_reference']}"
        assert summary['parameters_resolved'] == 1, f"Expected 1 resolved parameter, got {summary['parameters_resolved']}"
        assert summary['parameters_unresolved'] == 1, f"Expected 1 unresolved parameter, got {summary['parameters_unresolved']}"
        assert summary['total_returns'] == 3, f"Expected 3 return types, got {summary['total_returns']}"
        assert summary['returns_with_like_reference'] == 2, f"Expected 2 LIKE returns, got {summary['returns_with_like_reference']}"
        assert summary['returns_resolved'] == 1, f"Expected 1 resolved return, got {summary['returns_resolved']}"
        assert summary['returns_unresolved'] == 1, f"Expected 1 unresolved return, got {summary['returns_unresolved']}"
        
        print("✓ test_validate_with_issues passed")
        return True
    finally:
        os.unlink(db_path)

def create_test_db_valid():
    """Create a valid test database with no issues."""
    fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Create tables
    c.execute('''CREATE TABLE files (
        id INTEGER PRIMARY KEY,
        path TEXT UNIQUE NOT NULL
    )''')
    
    c.execute('''CREATE TABLE functions (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        file_id INTEGER NOT NULL,
        file_path TEXT,
        signature TEXT,
        line_start INTEGER,
        line_end INTEGER,
        FOREIGN KEY(file_id) REFERENCES files(id)
    )''')
    
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
    
    # Insert valid test data
    c.execute("INSERT INTO files (path) VALUES (?)", ("test.4gl",))
    file_id = c.lastrowid
    
    # Function with file_path
    c.execute('''INSERT INTO functions (name, file_id, file_path, signature, line_start, line_end)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              ("func1", file_id, "test.4gl", "FUNCTION func1()", 1, 5))
    func1_id = c.lastrowid
    
    # Valid parameters
    c.execute('''INSERT INTO parameters (function_id, name, type, is_like_reference, resolved)
                 VALUES (?, ?, ?, ?, ?)''',
              (func1_id, "param1", "STRING", 0, 0))
    
    # LIKE reference resolved
    c.execute('''INSERT INTO parameters (function_id, name, type, actual_type, is_like_reference, resolved, table_name, columns, types)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (func1_id, "param2", "LIKE users.*", "users.id,users.name", 1, 1, "users", "id,name", '["INTEGER","STRING"]'))
    
    # Valid return types
    c.execute('''INSERT INTO returns (function_id, name, type, is_like_reference, resolved)
                 VALUES (?, ?, ?, ?, ?)''',
              (func1_id, "result", "STRING", 0, 0))
    
    # LIKE reference resolved
    c.execute('''INSERT INTO returns (function_id, name, type, actual_type, is_like_reference, resolved, table_name, columns, types)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (func1_id, "result2", "LIKE orders.*", "orders.id,orders.total", 1, 1, "orders", "id,total", '["INTEGER","DECIMAL"]'))
    
    conn.commit()
    conn.close()
    
    return db_path

def test_validate_valid_db():
    """Test validation with a valid database."""
    db_path = create_test_db_valid()
    
    try:
        report = validate_type_resolution(db_path)
        
        # Verify report structure
        assert 'status' in report, "Report missing 'status' field"
        assert 'issues' in report, "Report missing 'issues' field"
        assert 'summary' in report, "Report missing 'summary' field"
        
        # Verify status is valid
        assert report['status'] == 'valid', f"Expected status 'valid', got '{report['status']}'"
        
        # Verify no critical issues
        critical_issues = [i for i in report['issues'] if i.get('severity') == 'critical']
        assert len(critical_issues) == 0, f"Expected no critical issues, got {len(critical_issues)}"
        
        # Verify summary statistics
        summary = report['summary']
        assert summary['total_functions'] == 1, f"Expected 1 function, got {summary['total_functions']}"
        assert summary['functions_without_file_path'] == 0, f"Expected 0 functions without file_path, got {summary['functions_without_file_path']}"
        assert summary['total_parameters'] == 2, f"Expected 2 parameters, got {summary['total_parameters']}"
        assert summary['parameters_with_like_reference'] == 1, f"Expected 1 LIKE parameter, got {summary['parameters_with_like_reference']}"
        assert summary['parameters_resolved'] == 1, f"Expected 1 resolved parameter, got {summary['parameters_resolved']}"
        assert summary['parameters_unresolved'] == 0, f"Expected 0 unresolved parameters, got {summary['parameters_unresolved']}"
        
        print("✓ test_validate_valid_db passed")
        return True
    finally:
        os.unlink(db_path)

def test_validate_empty_db():
    """Test validation with an empty database."""
    fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Create empty tables
    c.execute('''CREATE TABLE files (
        id INTEGER PRIMARY KEY,
        path TEXT UNIQUE NOT NULL
    )''')
    
    c.execute('''CREATE TABLE functions (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        file_id INTEGER NOT NULL,
        file_path TEXT,
        signature TEXT,
        line_start INTEGER,
        line_end INTEGER,
        FOREIGN KEY(file_id) REFERENCES files(id)
    )''')
    
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
    
    conn.commit()
    conn.close()
    
    try:
        report = validate_type_resolution(db_path)
        
        # Verify report structure
        assert 'status' in report, "Report missing 'status' field"
        assert 'issues' in report, "Report missing 'issues' field"
        assert 'summary' in report, "Report missing 'summary' field"
        
        # Verify status is valid for empty database
        assert report['status'] == 'valid', f"Expected status 'valid' for empty db, got '{report['status']}'"
        
        # Verify summary shows zeros
        summary = report['summary']
        assert summary['total_functions'] == 0, f"Expected 0 functions, got {summary['total_functions']}"
        assert summary['total_parameters'] == 0, f"Expected 0 parameters, got {summary['total_parameters']}"
        assert summary['total_returns'] == 0, f"Expected 0 return types, got {summary['total_returns']}"
        
        print("✓ test_validate_empty_db passed")
        return True
    finally:
        os.unlink(db_path)

if __name__ == '__main__':
    print("=" * 60)
    print("Running validation tests")
    print("=" * 60)
    
    try:
        test_validate_with_issues()
        test_validate_valid_db()
        test_validate_empty_db()
        
        print()
        print("=" * 60)
        print("✓ All validation tests passed!")
        print("=" * 60)
    except AssertionError as e:
        print(f"✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
