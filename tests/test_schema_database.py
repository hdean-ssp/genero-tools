#!/usr/bin/env python3
"""
Unit tests for schema database integration.

Tests the SchemaDatabase class and database operations.
"""

import unittest
import json
import sqlite3
import tempfile
import os
from pathlib import Path

# Add scripts directory to path
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from json_to_sqlite_schema import SchemaDatabase, load_schema_file


class TestSchemaDatabase(unittest.TestCase):
    """Test schema database operations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_file = os.path.join(self.temp_dir, "test.db")
        self.db = SchemaDatabase(self.db_file)
        self.db.connect()
        self.db.create_tables()
    
    def tearDown(self):
        """Clean up test files."""
        self.db.disconnect()
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def _create_schema_data(self) -> dict:
        """Create sample schema data."""
        return {
            "tables": [
                {
                    "name": "account",
                    "columns": [
                        {"name": "acc_code", "type": "VARCHAR(8)", "type_code": 0, "length": 8, "position": 1},
                        {"name": "acc_type", "type": "VARCHAR(2)", "type_code": 0, "length": 2, "position": 2},
                        {"name": "acc_balance", "type": "DECIMAL(3842)", "type_code": 5, "length": 3842, "position": 3},
                        {"name": "acc_del_date", "type": "DATE", "type_code": 7, "length": 4, "position": 4}
                    ]
                },
                {
                    "name": "customer",
                    "columns": [
                        {"name": "cust_id", "type": "INTEGER", "type_code": 2, "length": 4, "position": 1},
                        {"name": "cust_name", "type": "VARCHAR(40)", "type_code": 0, "length": 40, "position": 2}
                    ]
                }
            ]
        }
    
    def test_create_tables(self):
        """Test that tables are created."""
        # Tables should already be created in setUp
        cursor = self.db.conn.cursor()
        
        # Check schema_tables exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='schema_tables'"
        )
        self.assertIsNotNone(cursor.fetchone())
        
        # Check schema_columns exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='schema_columns'"
        )
        self.assertIsNotNone(cursor.fetchone())
    
    def test_create_indexes(self):
        """Test that indexes are created."""
        cursor = self.db.conn.cursor()
        
        # Check indexes exist
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_schema%'"
        )
        indexes = cursor.fetchall()
        self.assertGreater(len(indexes), 0)
    
    def test_load_single_table(self):
        """Test loading a single table."""
        schema_data = {
            "tables": [
                {
                    "name": "account",
                    "columns": [
                        {"name": "acc_code", "type": "VARCHAR(8)", "type_code": 0, "length": 8, "position": 1}
                    ]
                }
            ]
        }
        
        self.db.load_schema(schema_data)
        
        self.assertEqual(self.db.tables_inserted, 1)
        self.assertEqual(self.db.columns_inserted, 1)
    
    def test_load_multiple_tables(self):
        """Test loading multiple tables."""
        schema_data = self._create_schema_data()
        
        self.db.load_schema(schema_data)
        
        self.assertEqual(self.db.tables_inserted, 2)
        self.assertEqual(self.db.columns_inserted, 6)
    
    def test_get_table_count(self):
        """Test getting table count."""
        schema_data = self._create_schema_data()
        self.db.load_schema(schema_data)
        
        count = self.db.get_table_count()
        self.assertEqual(count, 2)
    
    def test_get_column_count(self):
        """Test getting column count."""
        schema_data = self._create_schema_data()
        self.db.load_schema(schema_data)
        
        count = self.db.get_column_count()
        self.assertEqual(count, 6)
    
    def test_get_table(self):
        """Test retrieving a table."""
        schema_data = self._create_schema_data()
        self.db.load_schema(schema_data)
        
        table = self.db.get_table("account")
        
        self.assertIsNotNone(table)
        self.assertEqual(table["name"], "account")
        self.assertEqual(len(table["columns"]), 4)
    
    def test_get_table_not_found(self):
        """Test retrieving non-existent table."""
        schema_data = self._create_schema_data()
        self.db.load_schema(schema_data)
        
        table = self.db.get_table("nonexistent")
        
        self.assertIsNone(table)
    
    def test_get_column(self):
        """Test retrieving a column."""
        schema_data = self._create_schema_data()
        self.db.load_schema(schema_data)
        
        column = self.db.get_column("account", "acc_code")
        
        self.assertIsNotNone(column)
        self.assertEqual(column["name"], "acc_code")
        self.assertEqual(column["type"], "VARCHAR(8)")
        self.assertEqual(column["type_code"], 0)
        self.assertEqual(column["length"], 8)
        self.assertEqual(column["position"], 1)
    
    def test_get_column_not_found(self):
        """Test retrieving non-existent column."""
        schema_data = self._create_schema_data()
        self.db.load_schema(schema_data)
        
        column = self.db.get_column("account", "nonexistent")
        
        self.assertIsNone(column)
    
    def test_find_tables_by_type(self):
        """Test finding tables by type code."""
        schema_data = self._create_schema_data()
        self.db.load_schema(schema_data)
        
        # Find tables with VARCHAR (type_code 0)
        tables = self.db.find_tables_by_type(0)
        
        self.assertEqual(len(tables), 2)
        table_names = [t["name"] for t in tables]
        self.assertIn("account", table_names)
        self.assertIn("customer", table_names)
    
    def test_find_columns_by_type(self):
        """Test finding columns by type code."""
        schema_data = self._create_schema_data()
        self.db.load_schema(schema_data)
        
        # Find VARCHAR columns (type_code 0)
        columns = self.db.find_columns_by_type(0)
        
        self.assertGreater(len(columns), 0)
        
        # Check that all returned columns have type_code 0
        for column in columns:
            self.assertEqual(column["type_code"], 0)
    
    def test_find_columns_by_type_not_found(self):
        """Test finding columns by non-existent type code."""
        schema_data = self._create_schema_data()
        self.db.load_schema(schema_data)
        
        # Find columns with type_code 999 (doesn't exist)
        columns = self.db.find_columns_by_type(999)
        
        self.assertEqual(len(columns), 0)
    
    def test_load_schema_clears_existing(self):
        """Test that loading schema clears existing data."""
        schema_data1 = {
            "tables": [
                {
                    "name": "table1",
                    "columns": [
                        {"name": "col1", "type": "INTEGER", "type_code": 2, "length": 4, "position": 1}
                    ]
                }
            ]
        }
        
        schema_data2 = {
            "tables": [
                {
                    "name": "table2",
                    "columns": [
                        {"name": "col2", "type": "VARCHAR(10)", "type_code": 0, "length": 10, "position": 1}
                    ]
                }
            ]
        }
        
        # Load first schema
        self.db.load_schema(schema_data1)
        self.assertEqual(self.db.get_table_count(), 1)
        
        # Load second schema (should clear first)
        self.db.load_schema(schema_data2)
        self.assertEqual(self.db.get_table_count(), 1)
        self.assertIsNone(self.db.get_table("table1"))
        self.assertIsNotNone(self.db.get_table("table2"))
    
    def test_duplicate_table_error(self):
        """Test handling of duplicate table names."""
        schema_data = {
            "tables": [
                {
                    "name": "account",
                    "columns": [
                        {"name": "col1", "type": "INTEGER", "type_code": 2, "length": 4, "position": 1}
                    ]
                },
                {
                    "name": "account",  # Duplicate
                    "columns": [
                        {"name": "col2", "type": "VARCHAR(10)", "type_code": 0, "length": 10, "position": 1}
                    ]
                }
            ]
        }
        
        self.db.load_schema(schema_data)
        
        # Should have error for duplicate
        self.assertGreater(len(self.db.errors), 0)
    
    def test_column_ordering(self):
        """Test that columns are ordered by position."""
        schema_data = {
            "tables": [
                {
                    "name": "account",
                    "columns": [
                        {"name": "col3", "type": "VARCHAR(10)", "type_code": 0, "length": 10, "position": 3},
                        {"name": "col1", "type": "INTEGER", "type_code": 2, "length": 4, "position": 1},
                        {"name": "col2", "type": "VARCHAR(20)", "type_code": 0, "length": 20, "position": 2}
                    ]
                }
            ]
        }
        
        self.db.load_schema(schema_data)
        
        table = self.db.get_table("account")
        
        # Columns should be ordered by position
        self.assertEqual(table["columns"][0]["name"], "col1")
        self.assertEqual(table["columns"][1]["name"], "col2")
        self.assertEqual(table["columns"][2]["name"], "col3")


class TestLoadSchemaFile(unittest.TestCase):
    """Test loading schema from file."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test files."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def _create_schema_json_file(self, schema_data: dict) -> str:
        """Create a temporary schema JSON file."""
        filepath = os.path.join(self.temp_dir, "schema.json")
        with open(filepath, 'w') as f:
            json.dump(schema_data, f)
        return filepath
    
    def test_load_schema_file(self):
        """Test loading schema from file."""
        schema_data = {
            "tables": [
                {
                    "name": "account",
                    "columns": [
                        {"name": "acc_code", "type": "VARCHAR(8)", "type_code": 0, "length": 8, "position": 1}
                    ]
                }
            ]
        }
        
        schema_file = self._create_schema_json_file(schema_data)
        db_file = os.path.join(self.temp_dir, "test.db")
        
        load_schema_file(schema_file, db_file)
        
        # Verify database was created and populated
        db = SchemaDatabase(db_file)
        db.connect()
        
        self.assertEqual(db.get_table_count(), 1)
        self.assertEqual(db.get_column_count(), 1)
        
        table = db.get_table("account")
        self.assertIsNotNone(table)
        
        db.disconnect()
    
    def test_load_schema_file_not_found(self):
        """Test error handling for missing file."""
        db_file = os.path.join(self.temp_dir, "test.db")
        
        with self.assertRaises(FileNotFoundError):
            load_schema_file("/nonexistent/schema.json", db_file)
    
    def test_load_invalid_json(self):
        """Test error handling for invalid JSON."""
        filepath = os.path.join(self.temp_dir, "invalid.json")
        with open(filepath, 'w') as f:
            f.write("{ invalid json }")
        
        db_file = os.path.join(self.temp_dir, "test.db")
        
        with self.assertRaises(json.JSONDecodeError):
            load_schema_file(filepath, db_file)


class TestSchemaIntegration(unittest.TestCase):
    """Integration tests for schema database."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test files."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_end_to_end_workflow(self):
        """Test complete workflow from schema file to database."""
        # Create schema JSON
        schema_data = {
            "tables": [
                {
                    "name": "abi_fields",
                    "columns": [
                        {"name": "id", "type": "VARCHAR(4)", "type_code": 0, "length": 4, "position": 1},
                        {"name": "name", "type": "VARCHAR(40)", "type_code": 0, "length": 40, "position": 2},
                        {"name": "version", "type": "VARCHAR(5)", "type_code": 0, "length": 5, "position": 3}
                    ]
                },
                {
                    "name": "account",
                    "columns": [
                        {"name": "acc_code", "type": "VARCHAR(8)", "type_code": 0, "length": 8, "position": 1},
                        {"name": "acc_type", "type": "VARCHAR(2)", "type_code": 0, "length": 2, "position": 2},
                        {"name": "acc_balance", "type": "DECIMAL(3842)", "type_code": 5, "length": 3842, "position": 3},
                        {"name": "acc_del_date", "type": "DATE", "type_code": 7, "length": 4, "position": 4}
                    ]
                }
            ]
        }
        
        # Write to file
        schema_file = os.path.join(self.temp_dir, "schema.json")
        with open(schema_file, 'w') as f:
            json.dump(schema_data, f)
        
        # Load into database
        db_file = os.path.join(self.temp_dir, "test.db")
        load_schema_file(schema_file, db_file)
        
        # Verify
        db = SchemaDatabase(db_file)
        db.connect()
        
        # Check tables
        self.assertEqual(db.get_table_count(), 2)
        self.assertEqual(db.get_column_count(), 7)
        
        # Check specific table
        account = db.get_table("account")
        self.assertIsNotNone(account)
        self.assertEqual(len(account["columns"]), 4)
        
        # Check specific column
        col = db.get_column("account", "acc_balance")
        self.assertIsNotNone(col)
        self.assertEqual(col["type"], "DECIMAL(3842)")
        
        # Check type queries
        varchar_tables = db.find_tables_by_type(0)
        self.assertEqual(len(varchar_tables), 2)
        
        decimal_cols = db.find_columns_by_type(5)
        self.assertEqual(len(decimal_cols), 1)
        self.assertEqual(decimal_cols[0]["name"], "acc_balance")
        
        db.disconnect()


if __name__ == "__main__":
    unittest.main()
