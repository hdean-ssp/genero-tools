#!/usr/bin/env python3
"""
Tests for Function Disambiguation (Phase 1e) - Multi-instance function resolution

Tests cover:
- Finding a function by name and file path
- Finding all instances of a function across files
- Proper handling of file_path in results
- Distinguishing between function instances with same name in different files
"""

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

# Add scripts to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from query_db import (
    find_function_by_name_and_path,
    find_all_function_instances
)


class TestFunctionDisambiguation(unittest.TestCase):
    """Test Phase 1e function disambiguation queries."""
    
    def setUp(self):
        """Create temporary database with test data."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_path = self.temp_db.name
        self.temp_db.close()
        
        # Create tables
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Files table
        cursor.execute("""
            CREATE TABLE files (
                id INTEGER PRIMARY KEY,
                path TEXT NOT NULL UNIQUE,
                type TEXT
            )
        """)
        
        # Functions table
        cursor.execute("""
            CREATE TABLE functions (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                file_id INTEGER NOT NULL,
                line_start INTEGER,
                line_end INTEGER,
                signature TEXT,
                FOREIGN KEY (file_id) REFERENCES files(id)
            )
        """)
        
        # Parameters table
        cursor.execute("""
            CREATE TABLE parameters (
                id INTEGER PRIMARY KEY,
                function_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                type TEXT,
                actual_type TEXT,
                is_like_reference BOOLEAN,
                resolved BOOLEAN,
                resolution_error TEXT,
                table_name TEXT,
                columns TEXT,
                types TEXT,
                FOREIGN KEY (function_id) REFERENCES functions(id)
            )
        """)
        
        # Returns table
        cursor.execute("""
            CREATE TABLE returns (
                id INTEGER PRIMARY KEY,
                function_id INTEGER NOT NULL,
                name TEXT,
                type TEXT,
                FOREIGN KEY (function_id) REFERENCES functions(id)
            )
        """)
        
        # Insert test files
        cursor.execute("INSERT INTO files (path, type) VALUES (?, ?)", ('./src/module1.4gl', 'source'))
        file1_id = cursor.lastrowid
        
        cursor.execute("INSERT INTO files (path, type) VALUES (?, ?)", ('./src/module2.4gl', 'source'))
        file2_id = cursor.lastrowid
        
        cursor.execute("INSERT INTO files (path, type) VALUES (?, ?)", ('./lib/utils.4gl', 'source'))
        file3_id = cursor.lastrowid
        
        # Insert test functions - same name in different files
        # process_data in module1.4gl
        cursor.execute("""
            INSERT INTO functions (name, file_id, line_start, line_end, signature)
            VALUES (?, ?, ?, ?, ?)
        """, ('process_data', file1_id, 1, 20, 'FUNCTION process_data(data LIKE account.*)'))
        func1_id = cursor.lastrowid
        
        # process_data in module2.4gl (different implementation)
        cursor.execute("""
            INSERT INTO functions (name, file_id, line_start, line_end, signature)
            VALUES (?, ?, ?, ?, ?)
        """, ('process_data', file2_id, 5, 25, 'FUNCTION process_data(data LIKE customer.*)'))
        func2_id = cursor.lastrowid
        
        # process_data in utils.4gl (another implementation)
        cursor.execute("""
            INSERT INTO functions (name, file_id, line_start, line_end, signature)
            VALUES (?, ?, ?, ?, ?)
        """, ('process_data', file3_id, 10, 30, 'FUNCTION process_data(data LIKE order.*)'))
        func3_id = cursor.lastrowid
        
        # unique_function in module1.4gl (only one instance)
        cursor.execute("""
            INSERT INTO functions (name, file_id, line_start, line_end, signature)
            VALUES (?, ?, ?, ?, ?)
        """, ('unique_function', file1_id, 50, 60, 'FUNCTION unique_function()'))
        func4_id = cursor.lastrowid
        
        # Insert parameters for process_data instances
        # module1.4gl version
        cursor.execute("""
            INSERT INTO parameters 
            (function_id, name, type, actual_type, is_like_reference, resolved, table_name, columns, types)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (func1_id, 'data', 'LIKE account.*', 'RECORD', 1, 1, 'account', 'id,name', json.dumps(['INTEGER', 'VARCHAR(100)'])))
        
        # module2.4gl version
        cursor.execute("""
            INSERT INTO parameters 
            (function_id, name, type, actual_type, is_like_reference, resolved, table_name, columns, types)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (func2_id, 'data', 'LIKE customer.*', 'RECORD', 1, 1, 'customer', 'id,email', json.dumps(['INTEGER', 'VARCHAR(255)'])))
        
        # utils.4gl version
        cursor.execute("""
            INSERT INTO parameters 
            (function_id, name, type, actual_type, is_like_reference, resolved, table_name, columns, types)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (func3_id, 'data', 'LIKE order.*', 'RECORD', 1, 1, 'order', 'id,total', json.dumps(['INTEGER', 'DECIMAL(10,2)'])))
        
        # Insert returns
        cursor.execute("""
            INSERT INTO returns (function_id, name, type)
            VALUES (?, ?, ?)
        """, (func1_id, None, 'INTEGER'))
        
        cursor.execute("""
            INSERT INTO returns (function_id, name, type)
            VALUES (?, ?, ?)
        """, (func2_id, None, 'INTEGER'))
        
        cursor.execute("""
            INSERT INTO returns (function_id, name, type)
            VALUES (?, ?, ?)
        """, (func3_id, None, 'INTEGER'))
        
        cursor.execute("""
            INSERT INTO returns (function_id, name, type)
            VALUES (?, ?, ?)
        """, (func4_id, None, 'VOID'))
        
        conn.commit()
        conn.close()
    
    def tearDown(self):
        """Clean up temporary database."""
        Path(self.db_path).unlink()
    
    def test_find_function_by_name_and_path_success(self):
        """Test finding a function by name and file path."""
        result = find_function_by_name_and_path(self.db_path, 'process_data', './src/module1.4gl')
        
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], 'process_data')
        self.assertEqual(result['path'], './src/module1.4gl')
        self.assertEqual(result['line_start'], 1)
        self.assertEqual(result['line_end'], 20)
    
    def test_find_function_by_name_and_path_with_parameters(self):
        """Test that parameters are included in result."""
        result = find_function_by_name_and_path(self.db_path, 'process_data', './src/module1.4gl')
        
        self.assertIsNotNone(result)
        self.assertIn('parameters', result)
        self.assertEqual(len(result['parameters']), 1)
        
        param = result['parameters'][0]
        self.assertEqual(param['name'], 'data')
        self.assertEqual(param['type'], 'LIKE account.*')
        self.assertEqual(param['table_name'], 'account')
        self.assertEqual(param['columns'], ['id', 'name'])
    
    def test_find_function_by_name_and_path_with_returns(self):
        """Test that returns are included in result."""
        result = find_function_by_name_and_path(self.db_path, 'process_data', './src/module1.4gl')
        
        self.assertIsNotNone(result)
        self.assertIn('returns', result)
        self.assertEqual(len(result['returns']), 1)
        self.assertEqual(result['returns'][0]['type'], 'INTEGER')
    
    def test_find_function_by_name_and_path_different_files(self):
        """Test finding same function name in different files."""
        result1 = find_function_by_name_and_path(self.db_path, 'process_data', './src/module1.4gl')
        result2 = find_function_by_name_and_path(self.db_path, 'process_data', './src/module2.4gl')
        result3 = find_function_by_name_and_path(self.db_path, 'process_data', './lib/utils.4gl')
        
        # All should be found
        self.assertIsNotNone(result1)
        self.assertIsNotNone(result2)
        self.assertIsNotNone(result3)
        
        # But they should be different
        self.assertEqual(result1['path'], './src/module1.4gl')
        self.assertEqual(result2['path'], './src/module2.4gl')
        self.assertEqual(result3['path'], './lib/utils.4gl')
        
        # And have different parameters
        self.assertEqual(result1['parameters'][0]['table_name'], 'account')
        self.assertEqual(result2['parameters'][0]['table_name'], 'customer')
        self.assertEqual(result3['parameters'][0]['table_name'], 'order')
    
    def test_find_function_by_name_and_path_not_found(self):
        """Test finding non-existent function."""
        result = find_function_by_name_and_path(self.db_path, 'nonexistent', './src/module1.4gl')
        
        self.assertIsNone(result)
    
    def test_find_function_by_name_and_path_wrong_file(self):
        """Test finding function with correct name but wrong file."""
        result = find_function_by_name_and_path(self.db_path, 'process_data', './wrong/path.4gl')
        
        self.assertIsNone(result)
    
    def test_find_all_function_instances_multiple(self):
        """Test finding all instances of a function."""
        results = find_all_function_instances(self.db_path, 'process_data')
        
        self.assertEqual(len(results), 3)
        
        # Check that all instances are returned
        paths = [r['path'] for r in results]
        self.assertIn('./src/module1.4gl', paths)
        self.assertIn('./src/module2.4gl', paths)
        self.assertIn('./lib/utils.4gl', paths)
    
    def test_find_all_function_instances_ordered_by_path(self):
        """Test that results are ordered by file path."""
        results = find_all_function_instances(self.db_path, 'process_data')
        
        self.assertEqual(len(results), 3)
        
        # Check ordering
        paths = [r['path'] for r in results]
        self.assertEqual(paths, sorted(paths))
    
    def test_find_all_function_instances_single(self):
        """Test finding all instances when only one exists."""
        results = find_all_function_instances(self.db_path, 'unique_function')
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], 'unique_function')
        self.assertEqual(results[0]['path'], './src/module1.4gl')
    
    def test_find_all_function_instances_not_found(self):
        """Test finding all instances of non-existent function."""
        results = find_all_function_instances(self.db_path, 'nonexistent')
        
        self.assertEqual(len(results), 0)
    
    def test_find_all_function_instances_with_parameters(self):
        """Test that all instances include their parameters."""
        results = find_all_function_instances(self.db_path, 'process_data')
        
        self.assertEqual(len(results), 3)
        
        # Each should have parameters
        for result in results:
            self.assertIn('parameters', result)
            self.assertEqual(len(result['parameters']), 1)
            self.assertEqual(result['parameters'][0]['name'], 'data')
    
    def test_find_all_function_instances_with_returns(self):
        """Test that all instances include their returns."""
        results = find_all_function_instances(self.db_path, 'process_data')
        
        self.assertEqual(len(results), 3)
        
        # Each should have returns
        for result in results:
            self.assertIn('returns', result)
            self.assertEqual(len(result['returns']), 1)
            self.assertEqual(result['returns'][0]['type'], 'INTEGER')
    
    def test_find_all_function_instances_different_parameters(self):
        """Test that different instances have different parameters."""
        results = find_all_function_instances(self.db_path, 'process_data')
        
        self.assertEqual(len(results), 3)
        
        # Extract table names from parameters
        tables = set()
        for result in results:
            for param in result['parameters']:
                if param['table_name']:
                    tables.add(param['table_name'])
        
        # Should have three different tables
        self.assertEqual(len(tables), 3)
        self.assertIn('account', tables)
        self.assertIn('customer', tables)
        self.assertIn('order', tables)


class TestFunctionDisambiguationIntegration(unittest.TestCase):
    """Integration tests for function disambiguation."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / 'test.db'
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_disambiguation_workflow(self):
        """Test complete disambiguation workflow."""
        # Create database
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute("""
            CREATE TABLE files (
                id INTEGER PRIMARY KEY,
                path TEXT NOT NULL UNIQUE,
                type TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE functions (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                file_id INTEGER NOT NULL,
                line_start INTEGER,
                line_end INTEGER,
                signature TEXT,
                FOREIGN KEY (file_id) REFERENCES files(id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE parameters (
                id INTEGER PRIMARY KEY,
                function_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                type TEXT,
                actual_type TEXT,
                is_like_reference BOOLEAN,
                resolved BOOLEAN,
                resolution_error TEXT,
                table_name TEXT,
                columns TEXT,
                types TEXT,
                FOREIGN KEY (function_id) REFERENCES functions(id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE returns (
                id INTEGER PRIMARY KEY,
                function_id INTEGER NOT NULL,
                name TEXT,
                type TEXT,
                FOREIGN KEY (function_id) REFERENCES functions(id)
            )
        """)
        
        # Insert files
        cursor.execute("INSERT INTO files (path, type) VALUES (?, ?)", ('./app/main.4gl', 'source'))
        file1_id = cursor.lastrowid
        
        cursor.execute("INSERT INTO files (path, type) VALUES (?, ?)", ('./lib/main.4gl', 'source'))
        file2_id = cursor.lastrowid
        
        # Insert functions with same name
        cursor.execute("""
            INSERT INTO functions (name, file_id, line_start, line_end, signature)
            VALUES (?, ?, ?, ?, ?)
        """, ('main', file1_id, 1, 50, 'FUNCTION main()'))
        func1_id = cursor.lastrowid
        
        cursor.execute("""
            INSERT INTO functions (name, file_id, line_start, line_end, signature)
            VALUES (?, ?, ?, ?, ?)
        """, ('main', file2_id, 1, 30, 'FUNCTION main()'))
        func2_id = cursor.lastrowid
        
        # Insert parameters
        cursor.execute("""
            INSERT INTO parameters 
            (function_id, name, type, actual_type, is_like_reference, resolved, table_name, columns, types)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (func1_id, 'config', 'RECORD', 'RECORD', 0, 1, None, None, None))
        
        cursor.execute("""
            INSERT INTO parameters 
            (function_id, name, type, actual_type, is_like_reference, resolved, table_name, columns, types)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (func2_id, 'options', 'RECORD', 'RECORD', 0, 1, None, None, None))
        
        # Insert returns
        cursor.execute("""
            INSERT INTO returns (function_id, name, type)
            VALUES (?, ?, ?)
        """, (func1_id, None, 'INTEGER'))
        
        cursor.execute("""
            INSERT INTO returns (function_id, name, type)
            VALUES (?, ?, ?)
        """, (func2_id, None, 'INTEGER'))
        
        conn.commit()
        conn.close()
        
        # Test workflow: find all instances, then get specific one
        all_instances = find_all_function_instances(str(self.db_path), 'main')
        self.assertEqual(len(all_instances), 2)
        
        # Get specific instance
        app_main = find_function_by_name_and_path(str(self.db_path), 'main', './app/main.4gl')
        lib_main = find_function_by_name_and_path(str(self.db_path), 'main', './lib/main.4gl')
        
        # Verify they're different
        self.assertIsNotNone(app_main)
        self.assertIsNotNone(lib_main)
        self.assertEqual(app_main['parameters'][0]['name'], 'config')
        self.assertEqual(lib_main['parameters'][0]['name'], 'options')


if __name__ == '__main__':
    unittest.main()
