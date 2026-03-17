#!/usr/bin/env python3
"""Test NOT NULL constraint on parameters table."""

import json
import sqlite3
import tempfile
import os
import sys
import logging

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from json_to_sqlite import create_signatures_db, migrate_add_not_null_constraint

def test_not_null_constraint_on_new_database():
    """Test that NOT NULL constraint is enforced on new database."""
    print("Test 1: NOT NULL constraint on new database...")
    
    temp_dir = tempfile.mkdtemp()
    json_file = os.path.join(temp_dir, 'test.json')
    db_file = os.path.join(temp_dir, 'test.db')
    
    try:
        # Create test data
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
        
        # Write test data
        with open(json_file, 'w') as f:
            json.dump(test_data, f)
        
        # Create database
        create_signatures_db(json_file, db_file)
        
        # Try to insert a parameter with NULL name - should fail
        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        
        c.execute('SELECT id FROM functions WHERE name = ?', ('test_func',))
        func_id = c.fetchone()[0]
        
        try:
            c.execute('INSERT INTO parameters (function_id, name, type) VALUES (?, ?, ?)',
                     (func_id, None, 'STRING'))
            conn.commit()
            print("  [FAIL] Should have raised an error for NULL parameter name")
            return False
        except sqlite3.IntegrityError as e:
            print(f"  [PASS] NOT NULL constraint enforced: {e}")
            conn.close()
            return True
    finally:
        if os.path.exists(json_file):
            os.remove(json_file)
        if os.path.exists(db_file):
            os.remove(db_file)
        os.rmdir(temp_dir)

def test_migration_adds_constraint():
    """Test that migration adds NOT NULL constraint to existing database."""
    print("\nTest 2: Migration adds NOT NULL constraint...")
    
    temp_dir = tempfile.mkdtemp()
    db_file = os.path.join(temp_dir, 'test.db')
    
    try:
        # Create a database without NOT NULL constraint
        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        
        c.execute('''CREATE TABLE files
                     (id INTEGER PRIMARY KEY, path TEXT UNIQUE, type TEXT)''')
        c.execute('''CREATE TABLE functions
                     (id INTEGER PRIMARY KEY, file_id INTEGER, name TEXT, 
                      line_start INTEGER, line_end INTEGER, signature TEXT, file_path TEXT,
                      FOREIGN KEY(file_id) REFERENCES files(id))''')
        
        # Create parameters table WITHOUT NOT NULL constraint
        c.execute('''CREATE TABLE parameters
                     (id INTEGER PRIMARY KEY, function_id INTEGER, name TEXT, type TEXT,
                      FOREIGN KEY(function_id) REFERENCES functions(id))''')
        
        # Insert test data
        c.execute('INSERT INTO files (path, type) VALUES (?, ?)', ('./test.4gl', '4GLS'))
        file_id = c.lastrowid
        
        c.execute('''INSERT INTO functions (file_id, name, line_start, line_end, signature, file_path)
                    VALUES (?, ?, ?, ?, ?, ?)''',
                 (file_id, 'test_func', 1, 5, '1-5: test_func()', './test.4gl'))
        func_id = c.lastrowid
        
        # Insert a parameter with NULL name (this should work without constraint)
        c.execute('INSERT INTO parameters (function_id, name, type) VALUES (?, ?, ?)',
                 (func_id, None, 'STRING'))
        conn.commit()
        conn.close()
        
        # Now run migration
        conn = sqlite3.connect(db_file)
        migrate_add_not_null_constraint(conn)
        conn.close()
        
        # Verify constraint is now enforced
        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        
        try:
            c.execute('INSERT INTO parameters (function_id, name, type) VALUES (?, ?, ?)',
                     (func_id, None, 'INTEGER'))
            conn.commit()
            print("  [FAIL] Migration did not add NOT NULL constraint")
            return False
        except sqlite3.IntegrityError as e:
            print(f"  [PASS] Migration successfully added NOT NULL constraint: {e}")
            conn.close()
            return True
    finally:
        if os.path.exists(db_file):
            os.remove(db_file)
        os.rmdir(temp_dir)

def test_migration_preserves_valid_data():
    """Test that migration preserves valid data and removes invalid data."""
    print("\nTest 3: Migration preserves valid data...")
    
    temp_dir = tempfile.mkdtemp()
    db_file = os.path.join(temp_dir, 'test.db')
    
    try:
        # Create a database without NOT NULL constraint
        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        
        c.execute('''CREATE TABLE files
                     (id INTEGER PRIMARY KEY, path TEXT UNIQUE, type TEXT)''')
        c.execute('''CREATE TABLE functions
                     (id INTEGER PRIMARY KEY, file_id INTEGER, name TEXT, 
                      line_start INTEGER, line_end INTEGER, signature TEXT, file_path TEXT,
                      FOREIGN KEY(file_id) REFERENCES functions(id))''')
        
        # Create parameters table WITHOUT NOT NULL constraint
        c.execute('''CREATE TABLE parameters
                     (id INTEGER PRIMARY KEY, function_id INTEGER, name TEXT, type TEXT,
                      FOREIGN KEY(function_id) REFERENCES functions(id))''')
        
        # Insert test data
        c.execute('INSERT INTO files (path, type) VALUES (?, ?)', ('./test.4gl', '4GLS'))
        file_id = c.lastrowid
        
        c.execute('''INSERT INTO functions (file_id, name, line_start, line_end, signature, file_path)
                    VALUES (?, ?, ?, ?, ?, ?)''',
                 (file_id, 'test_func', 1, 5, '1-5: test_func()', './test.4gl'))
        func_id = c.lastrowid
        
        # Insert mixed data: valid and invalid parameters
        c.execute('INSERT INTO parameters (function_id, name, type) VALUES (?, ?, ?)',
                 (func_id, 'param1', 'STRING'))
        c.execute('INSERT INTO parameters (function_id, name, type) VALUES (?, ?, ?)',
                 (func_id, None, 'INTEGER'))
        c.execute('INSERT INTO parameters (function_id, name, type) VALUES (?, ?, ?)',
                 (func_id, 'param2', 'DECIMAL'))
        c.execute('INSERT INTO parameters (function_id, name, type) VALUES (?, ?, ?)',
                 (func_id, '', 'BOOLEAN'))
        conn.commit()
        conn.close()
        
        # Verify we have 4 parameters before migration
        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM parameters')
        count_before = c.fetchone()[0]
        conn.close()
        
        if count_before != 4:
            print(f"  [FAIL] Expected 4 parameters before migration, got {count_before}")
            return False
        
        # Run migration
        conn = sqlite3.connect(db_file)
        migrate_add_not_null_constraint(conn)
        conn.close()
        
        # Verify we have 2 parameters after migration (only valid ones)
        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM parameters')
        count_after = c.fetchone()[0]
        
        c.execute('SELECT name FROM parameters ORDER BY id')
        names = [row[0] for row in c.fetchall()]
        conn.close()
        
        if count_after != 2:
            print(f"  [FAIL] Expected 2 parameters after migration, got {count_after}")
            return False
        
        if names != ['param1', 'param2']:
            print(f"  [FAIL] Expected ['param1', 'param2'], got {names}")
            return False
        
        print(f"  [PASS] Migration preserved valid data: {names}")
        return True
    finally:
        if os.path.exists(db_file):
            os.remove(db_file)
        os.rmdir(temp_dir)

def test_migration_idempotent():
    """Test that migration can be run multiple times safely."""
    print("\nTest 4: Migration is idempotent...")
    
    temp_dir = tempfile.mkdtemp()
    db_file = os.path.join(temp_dir, 'test.db')
    
    try:
        # Create a database without NOT NULL constraint
        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        
        c.execute('''CREATE TABLE files
                     (id INTEGER PRIMARY KEY, path TEXT UNIQUE, type TEXT)''')
        c.execute('''CREATE TABLE functions
                     (id INTEGER PRIMARY KEY, file_id INTEGER, name TEXT, 
                      line_start INTEGER, line_end INTEGER, signature TEXT, file_path TEXT,
                      FOREIGN KEY(file_id) REFERENCES functions(id))''')
        
        # Create parameters table WITHOUT NOT NULL constraint
        c.execute('''CREATE TABLE parameters
                     (id INTEGER PRIMARY KEY, function_id INTEGER, name TEXT, type TEXT,
                      FOREIGN KEY(function_id) REFERENCES functions(id))''')
        
        # Insert test data
        c.execute('INSERT INTO files (path, type) VALUES (?, ?)', ('./test.4gl', '4GLS'))
        file_id = c.lastrowid
        
        c.execute('''INSERT INTO functions (file_id, name, line_start, line_end, signature, file_path)
                    VALUES (?, ?, ?, ?, ?, ?)''',
                 (file_id, 'test_func', 1, 5, '1-5: test_func()', './test.4gl'))
        func_id = c.lastrowid
        
        c.execute('INSERT INTO parameters (function_id, name, type) VALUES (?, ?, ?)',
                 (func_id, 'param1', 'STRING'))
        conn.commit()
        conn.close()
        
        # Run migration twice
        conn = sqlite3.connect(db_file)
        migrate_add_not_null_constraint(conn)
        conn.close()
        
        conn = sqlite3.connect(db_file)
        migrate_add_not_null_constraint(conn)
        conn.close()
        
        # Verify data is still intact
        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM parameters')
        count = c.fetchone()[0]
        
        c.execute('SELECT name FROM parameters')
        name = c.fetchone()[0]
        conn.close()
        
        if count != 1 or name != 'param1':
            print(f"  [FAIL] Data corrupted after multiple migrations")
            return False
        
        print(f"  [PASS] Migration is idempotent")
        return True
    finally:
        if os.path.exists(db_file):
            os.remove(db_file)
        os.rmdir(temp_dir)

if __name__ == '__main__':
    results = []
    results.append(test_not_null_constraint_on_new_database())
    results.append(test_migration_adds_constraint())
    results.append(test_migration_preserves_valid_data())
    results.append(test_migration_idempotent())
    
    print("\n" + "="*50)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("All tests passed!")
        sys.exit(0)
    else:
        print("Some tests failed!")
        sys.exit(1)
