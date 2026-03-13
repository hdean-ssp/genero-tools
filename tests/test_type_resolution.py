#!/usr/bin/env python3
"""
Tests for Type Resolution Engine (scripts/resolve_types.py)

Tests cover:
- LIKE reference parsing and resolution
- Schema lookups
- Edge cases (missing tables, columns)
- workspace.json processing
"""

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from typing import Dict

# Add scripts to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from resolve_types import TypeResolver


class TestTypeResolver(unittest.TestCase):
    """Test TypeResolver class."""
    
    def setUp(self):
        """Create temporary database with test schema."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_path = self.temp_db.name
        self.temp_db.close()
        
        # Create schema tables
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create schema tables
        cursor.execute("""
            CREATE TABLE schema_tables (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                source_file TEXT,
                line_number INTEGER
            )
        """)
        
        cursor.execute("""
            CREATE TABLE schema_columns (
                id INTEGER PRIMARY KEY,
                table_id INTEGER NOT NULL,
                column_name TEXT NOT NULL,
                column_type TEXT NOT NULL,
                FOREIGN KEY (table_id) REFERENCES schema_tables(id)
            )
        """)
        
        # Insert test data
        cursor.execute("INSERT INTO schema_tables (name) VALUES ('account')")
        account_id = cursor.lastrowid
        
        cursor.execute("INSERT INTO schema_tables (name) VALUES ('customer')")
        customer_id = cursor.lastrowid
        
        # Account columns
        cursor.execute("""
            INSERT INTO schema_columns (table_id, column_name, column_type)
            VALUES (?, ?, ?)
        """, (account_id, 'id', 'INTEGER'))
        
        cursor.execute("""
            INSERT INTO schema_columns (table_id, column_name, column_type)
            VALUES (?, ?, ?)
        """, (account_id, 'name', 'VARCHAR(100)'))
        
        cursor.execute("""
            INSERT INTO schema_columns (table_id, column_name, column_type)
            VALUES (?, ?, ?)
        """, (account_id, 'balance', 'DECIMAL(10,2)'))
        
        # Customer columns
        cursor.execute("""
            INSERT INTO schema_columns (table_id, column_name, column_type)
            VALUES (?, ?, ?)
        """, (customer_id, 'id', 'INTEGER'))
        
        cursor.execute("""
            INSERT INTO schema_columns (table_id, column_name, column_type)
            VALUES (?, ?, ?)
        """, (customer_id, 'email', 'VARCHAR(255)'))
        
        conn.commit()
        conn.close()
        
        # Create resolver
        self.resolver = TypeResolver(self.db_path)
    
    def tearDown(self):
        """Clean up temporary database."""
        self.resolver.close()
        Path(self.db_path).unlink()
    
    def test_resolve_like_all_columns(self):
        """Test resolving LIKE table.* pattern."""
        result = self.resolver.resolve_like_reference('LIKE account.*')
        
        self.assertTrue(result['resolved'])
        self.assertEqual(result['table'], 'account')
        self.assertEqual(result['columns'], ['id', 'name', 'balance'])
        self.assertEqual(result['types'], ['INTEGER', 'VARCHAR(100)', 'DECIMAL(10,2)'])
    
    def test_resolve_like_specific_column(self):
        """Test resolving LIKE table.column pattern."""
        result = self.resolver.resolve_like_reference('LIKE account.name')
        
        self.assertTrue(result['resolved'])
        self.assertEqual(result['table'], 'account')
        self.assertEqual(result['columns'], ['name'])
        self.assertEqual(result['types'], ['VARCHAR(100)'])
    
    def test_resolve_like_missing_table(self):
        """Test resolving LIKE with non-existent table."""
        result = self.resolver.resolve_like_reference('LIKE nonexistent.*')
        
        self.assertFalse(result['resolved'])
        self.assertIn('not found', result['error'].lower())
    
    def test_resolve_like_missing_column(self):
        """Test resolving LIKE with non-existent column."""
        result = self.resolver.resolve_like_reference('LIKE account.nonexistent')
        
        self.assertFalse(result['resolved'])
        self.assertIn('not found', result['error'].lower())
    
    def test_resolve_like_invalid_pattern(self):
        """Test resolving invalid LIKE pattern."""
        result = self.resolver.resolve_like_reference('LIKE invalid')
        
        self.assertFalse(result['resolved'])
        self.assertIn('invalid', result['error'].lower())
    
    def test_resolve_like_case_insensitive(self):
        """Test that LIKE keyword is case-insensitive."""
        result1 = self.resolver.resolve_like_reference('LIKE account.*')
        result2 = self.resolver.resolve_like_reference('like account.*')
        result3 = self.resolver.resolve_like_reference('Like account.*')
        
        self.assertTrue(result1['resolved'])
        self.assertTrue(result2['resolved'])
        self.assertTrue(result3['resolved'])
    
    def test_resolve_parameter_type_like_reference(self):
        """Test resolving parameter type with LIKE reference."""
        result = self.resolver.resolve_parameter_type('LIKE account.*')
        
        self.assertTrue(result['resolved'])
        self.assertTrue(result['is_like_reference'])
        self.assertEqual(result['table'], 'account')
    
    def test_resolve_parameter_type_non_like(self):
        """Test resolving parameter type without LIKE reference."""
        result = self.resolver.resolve_parameter_type('INTEGER')
        
        self.assertTrue(result['resolved'])
        self.assertFalse(result['is_like_reference'])
        self.assertEqual(result['type'], 'INTEGER')
    
    def test_resolve_parameter_type_varchar(self):
        """Test resolving VARCHAR parameter type."""
        result = self.resolver.resolve_parameter_type('VARCHAR(100)')
        
        self.assertTrue(result['resolved'])
        self.assertFalse(result['is_like_reference'])
        self.assertEqual(result['type'], 'VARCHAR(100)')
    
    def test_process_workspace_json(self):
        """Test processing workspace.json with LIKE references."""
        # Create temporary workspace.json with correct format
        workspace = {
            "_metadata": {
                "version": "1.0.0",
                "generated": "2026-03-13T00:00:00Z",
                "files_processed": 1
            },
            "./test.4gl": [
                {
                    'name': 'process_account',
                    'parameters': [
                        {'name': 'acc', 'type': 'LIKE account.*'},
                        {'name': 'id', 'type': 'INTEGER'}
                    ],
                    'return_type': 'VOID'
                },
                {
                    'name': 'get_customer',
                    'parameters': [
                        {'name': 'cust', 'type': 'LIKE customer.id'}
                    ],
                    'return_type': 'VARCHAR(255)'
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(workspace, f)
            workspace_path = f.name
        
        try:
            result = self.resolver.process_workspace_json(workspace_path)
            
            # Check metadata is preserved
            self.assertIn('_metadata', result)
            
            # Check first file's functions
            funcs = result['./test.4gl']
            self.assertEqual(len(funcs), 2)
            
            func1 = funcs[0]
            self.assertEqual(func1['name'], 'process_account')
            
            # Check LIKE parameter
            param1 = func1['parameters'][0]
            self.assertTrue(param1['resolved'])
            self.assertTrue(param1['is_like_reference'])
            self.assertEqual(param1['table'], 'account')
            self.assertEqual(param1['columns'], ['id', 'name', 'balance'])
            
            # Check non-LIKE parameter
            param2 = func1['parameters'][1]
            self.assertTrue(param2['resolved'])
            self.assertFalse(param2['is_like_reference'])
            self.assertEqual(param2['type'], 'INTEGER')
            
            # Check second function
            func2 = funcs[1]
            param3 = func2['parameters'][0]
            self.assertTrue(param3['resolved'])
            self.assertTrue(param3['is_like_reference'])
            self.assertEqual(param3['table'], 'customer')
            self.assertEqual(param3['columns'], ['id'])
            
        finally:
            Path(workspace_path).unlink()
    
    def test_multiple_tables(self):
        """Test resolving references to different tables."""
        result1 = self.resolver.resolve_like_reference('LIKE account.*')
        result2 = self.resolver.resolve_like_reference('LIKE customer.*')
        
        self.assertTrue(result1['resolved'])
        self.assertTrue(result2['resolved'])
        self.assertEqual(len(result1['columns']), 3)
        self.assertEqual(len(result2['columns']), 2)
    
    def test_whitespace_handling(self):
        """Test handling of whitespace in LIKE patterns."""
        result1 = self.resolver.resolve_like_reference('LIKE account.*')
        result2 = self.resolver.resolve_like_reference('  LIKE  account.*  ')
        result3 = self.resolver.resolve_like_reference('LIKE\taccount.*')
        
        self.assertTrue(result1['resolved'])
        self.assertTrue(result2['resolved'])
        self.assertTrue(result3['resolved'])


class TestTypeResolutionIntegration(unittest.TestCase):
    """Integration tests for type resolution."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / 'test.db'
        self.workspace_path = Path(self.temp_dir) / 'workspace.json'
        
        # Create test database
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE schema_tables (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                source_file TEXT,
                line_number INTEGER
            )
        """)
        
        cursor.execute("""
            CREATE TABLE schema_columns (
                id INTEGER PRIMARY KEY,
                table_id INTEGER NOT NULL,
                column_name TEXT NOT NULL,
                column_type TEXT NOT NULL,
                FOREIGN KEY (table_id) REFERENCES schema_tables(id)
            )
        """)
        
        # Insert test schema
        cursor.execute("INSERT INTO schema_tables (name) VALUES ('orders')")
        orders_id = cursor.lastrowid
        
        cursor.execute("""
            INSERT INTO schema_columns (table_id, column_name, column_type)
            VALUES (?, ?, ?)
        """, (orders_id, 'order_id', 'INTEGER'))
        
        cursor.execute("""
            INSERT INTO schema_columns (table_id, column_name, column_type)
            VALUES (?, ?, ?)
        """, (orders_id, 'customer_id', 'INTEGER'))
        
        cursor.execute("""
            INSERT INTO schema_columns (table_id, column_name, column_type)
            VALUES (?, ?, ?)
        """, (orders_id, 'total', 'DECIMAL(10,2)'))
        
        conn.commit()
        conn.close()
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_end_to_end_resolution(self):
        """Test complete type resolution workflow."""
        # Create workspace.json with correct format
        workspace = {
            "_metadata": {
                "version": "1.0.0",
                "generated": "2026-03-13T00:00:00Z",
                "files_processed": 1
            },
            "./test.4gl": [
                {
                    'name': 'process_order',
                    'parameters': [
                        {'name': 'order', 'type': 'LIKE orders.*'},
                        {'name': 'amount', 'type': 'DECIMAL(10,2)'}
                    ],
                    'return_type': 'INTEGER'
                }
            ]
        }
        
        with open(str(self.workspace_path), 'w') as f:
            json.dump(workspace, f)
        
        # Resolve types
        resolver = TypeResolver(str(self.db_path))
        result = resolver.process_workspace_json(str(self.workspace_path))
        resolver.close()
        
        # Verify results
        func = result['./test.4gl'][0]
        param = func['parameters'][0]
        
        self.assertTrue(param['resolved'])
        self.assertEqual(param['table'], 'orders')
        self.assertEqual(len(param['columns']), 3)


if __name__ == '__main__':
    unittest.main()
