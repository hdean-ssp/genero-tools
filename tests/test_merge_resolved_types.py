#!/usr/bin/env python3
"""
Tests for merge_resolved_types.py

Tests cover:
- Merging resolved parameter types into database
- Merging resolved return types into database
- Handling unresolved LIKE references
- Column creation and schema updates
"""

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

# Add scripts to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from merge_resolved_types import ResolvedTypeMerger


class TestMergeResolvedTypes(unittest.TestCase):
    """Test ResolvedTypeMerger class."""
    
    def setUp(self):
        """Create temporary database and workspace_resolved.json."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / 'test.db'
        self.workspace_resolved_path = Path(self.temp_dir) / 'workspace_resolved.json'
        
        # Create test database with functions, parameters, and returns tables
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''CREATE TABLE files
                         (id INTEGER PRIMARY KEY, path TEXT UNIQUE, type TEXT)''')
        
        cursor.execute('''CREATE TABLE functions
                         (id INTEGER PRIMARY KEY, file_id INTEGER, name TEXT, 
                          line_start INTEGER, line_end INTEGER, signature TEXT, file_path TEXT,
                          FOREIGN KEY(file_id) REFERENCES files(id))''')
        
        cursor.execute('''CREATE TABLE parameters
                         (id INTEGER PRIMARY KEY, function_id INTEGER, name TEXT NOT NULL, type TEXT,
                          FOREIGN KEY(function_id) REFERENCES functions(id))''')
        
        cursor.execute('''CREATE TABLE returns
                         (id INTEGER PRIMARY KEY, function_id INTEGER, name TEXT, type TEXT,
                          FOREIGN KEY(function_id) REFERENCES functions(id))''')
        
        # Insert test data
        cursor.execute('INSERT INTO files (path, type) VALUES (?, ?)', ('./test.4gl', '4GLS'))
        file_id = cursor.lastrowid
        
        cursor.execute('''INSERT INTO functions (file_id, name, line_start, line_end, signature, file_path)
                         VALUES (?, ?, ?, ?, ?, ?)''',
                      (file_id, 'process_account', 1, 10, '1-10: process_account(acc LIKE account.*)', './test.4gl'))
        func_id = cursor.lastrowid
        
        # Insert parameter
        cursor.execute('INSERT INTO parameters (function_id, name, type) VALUES (?, ?, ?)',
                      (func_id, 'acc', 'LIKE account.*'))
        
        # Insert return
        cursor.execute('INSERT INTO returns (function_id, name, type) VALUES (?, ?, ?)',
                      (func_id, 'result', 'LIKE account.id'))
        
        conn.commit()
        conn.close()
    
    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_merge_resolved_parameters(self):
        """Test merging resolved parameter types."""
        # Create workspace_resolved.json
        workspace_resolved = {
            "_metadata": {
                "version": "1.0.0",
                "generated": "2026-03-13T00:00:00Z",
                "files_processed": 1
            },
            "./test.4gl": [
                {
                    "name": "process_account",
                    "parameters": [
                        {
                            "name": "acc",
                            "type": "LIKE account.*",
                            "is_like_reference": True,
                            "resolved": True,
                            "table": "account",
                            "columns": ["id", "name", "balance"],
                            "types": ["INTEGER", "VARCHAR(100)", "DECIMAL(10,2)"]
                        }
                    ],
                    "returns": []
                }
            ]
        }
        
        with open(str(self.workspace_resolved_path), 'w') as f:
            json.dump(workspace_resolved, f)
        
        # Merge resolved types
        merger = ResolvedTypeMerger(str(self.db_path))
        merger.merge_resolved_types(str(self.workspace_resolved_path))
        merger.close()
        
        # Verify results
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('SELECT actual_type, is_like_reference, resolved, table_name, columns, types FROM parameters WHERE name = ?', ('acc',))
        row = cursor.fetchone()
        
        self.assertIsNotNone(row)
        actual_type, is_like_ref, resolved, table_name, columns, types = row
        
        self.assertEqual(actual_type, 'INTEGER')
        self.assertEqual(is_like_ref, 1)
        self.assertEqual(resolved, 1)
        self.assertEqual(table_name, 'account')
        self.assertEqual(columns, 'id,name,balance')
        
        # Verify types is JSON
        types_list = json.loads(types)
        self.assertEqual(types_list, ["INTEGER", "VARCHAR(100)", "DECIMAL(10,2)"])
        
        conn.close()
    
    def test_merge_resolved_returns(self):
        """Test merging resolved return types."""
        # Create workspace_resolved.json
        workspace_resolved = {
            "_metadata": {
                "version": "1.0.0",
                "generated": "2026-03-13T00:00:00Z",
                "files_processed": 1
            },
            "./test.4gl": [
                {
                    "name": "process_account",
                    "parameters": [],
                    "returns": [
                        {
                            "name": "result",
                            "type": "LIKE account.id",
                            "is_like_reference": True,
                            "resolved": True,
                            "table": "account",
                            "columns": ["id"],
                            "types": ["INTEGER"]
                        }
                    ]
                }
            ]
        }
        
        with open(str(self.workspace_resolved_path), 'w') as f:
            json.dump(workspace_resolved, f)
        
        # Merge resolved types
        merger = ResolvedTypeMerger(str(self.db_path))
        merger.merge_resolved_types(str(self.workspace_resolved_path))
        merger.close()
        
        # Verify results
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('SELECT actual_type, is_like_reference, resolved, table_name, columns, types FROM returns WHERE name = ?', ('result',))
        row = cursor.fetchone()
        
        self.assertIsNotNone(row)
        actual_type, is_like_ref, resolved, table_name, columns, types = row
        
        self.assertEqual(actual_type, 'INTEGER')
        self.assertEqual(is_like_ref, 1)
        self.assertEqual(resolved, 1)
        self.assertEqual(table_name, 'account')
        self.assertEqual(columns, 'id')
        
        # Verify types is JSON
        types_list = json.loads(types)
        self.assertEqual(types_list, ["INTEGER"])
        
        conn.close()
    
    def test_merge_unresolved_return_type(self):
        """Test merging unresolved return types with error reasons."""
        # Create workspace_resolved.json with unresolved return type
        workspace_resolved = {
            "_metadata": {
                "version": "1.0.0",
                "generated": "2026-03-13T00:00:00Z",
                "files_processed": 1
            },
            "./test.4gl": [
                {
                    "name": "process_account",
                    "parameters": [],
                    "returns": [
                        {
                            "name": "result",
                            "type": "LIKE nonexistent.*",
                            "is_like_reference": True,
                            "resolved": False,
                            "error": "Table not found: nonexistent"
                        }
                    ]
                }
            ]
        }
        
        with open(str(self.workspace_resolved_path), 'w') as f:
            json.dump(workspace_resolved, f)
        
        # Merge resolved types
        merger = ResolvedTypeMerger(str(self.db_path))
        merger.merge_resolved_types(str(self.workspace_resolved_path))
        merger.close()
        
        # Verify results
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('SELECT is_like_reference, resolved, resolution_error FROM returns WHERE name = ?', ('result',))
        row = cursor.fetchone()
        
        self.assertIsNotNone(row)
        is_like_ref, resolved, error = row
        
        self.assertEqual(is_like_ref, 1)
        self.assertEqual(resolved, 0)
        self.assertIn('not found', error.lower())
        
        conn.close()
    
    def test_merge_statistics(self):
        """Test that merge statistics are correctly tracked."""
        # Create workspace_resolved.json with both parameters and returns
        workspace_resolved = {
            "_metadata": {
                "version": "1.0.0",
                "generated": "2026-03-13T00:00:00Z",
                "files_processed": 1
            },
            "./test.4gl": [
                {
                    "name": "process_account",
                    "parameters": [
                        {
                            "name": "acc",
                            "type": "LIKE account.*",
                            "is_like_reference": True,
                            "resolved": True,
                            "table": "account",
                            "columns": ["id", "name", "balance"],
                            "types": ["INTEGER", "VARCHAR(100)", "DECIMAL(10,2)"]
                        }
                    ],
                    "returns": [
                        {
                            "name": "result",
                            "type": "LIKE account.id",
                            "is_like_reference": True,
                            "resolved": True,
                            "table": "account",
                            "columns": ["id"],
                            "types": ["INTEGER"]
                        }
                    ]
                }
            ]
        }
        
        with open(str(self.workspace_resolved_path), 'w') as f:
            json.dump(workspace_resolved, f)
        
        # Merge resolved types
        merger = ResolvedTypeMerger(str(self.db_path))
        merger.merge_resolved_types(str(self.workspace_resolved_path))
        
        # Verify statistics
        self.assertEqual(merger.stats['parameters_updated'], 1)
        self.assertEqual(merger.stats['parameters_resolved'], 1)
        self.assertEqual(merger.stats['parameters_unresolved'], 0)
        self.assertEqual(merger.stats['returns_updated'], 1)
        self.assertEqual(merger.stats['returns_resolved'], 1)
        self.assertEqual(merger.stats['returns_unresolved'], 0)
        
        merger.close()
    
    def test_merge_mixed_resolved_unresolved(self):
        """Test merging mix of resolved and unresolved types."""
        # Create workspace_resolved.json with both resolved and unresolved
        workspace_resolved = {
            "_metadata": {
                "version": "1.0.0",
                "generated": "2026-03-13T00:00:00Z",
                "files_processed": 1
            },
            "./test.4gl": [
                {
                    "name": "process_account",
                    "parameters": [
                        {
                            "name": "acc",
                            "type": "LIKE account.*",
                            "is_like_reference": True,
                            "resolved": True,
                            "table": "account",
                            "columns": ["id", "name", "balance"],
                            "types": ["INTEGER", "VARCHAR(100)", "DECIMAL(10,2)"]
                        }
                    ],
                    "returns": [
                        {
                            "name": "result",
                            "type": "LIKE nonexistent.*",
                            "is_like_reference": True,
                            "resolved": False,
                            "error": "Table not found: nonexistent"
                        }
                    ]
                }
            ]
        }
        
        with open(str(self.workspace_resolved_path), 'w') as f:
            json.dump(workspace_resolved, f)
        
        # Merge resolved types
        merger = ResolvedTypeMerger(str(self.db_path))
        merger.merge_resolved_types(str(self.workspace_resolved_path))
        
        # Verify statistics
        self.assertEqual(merger.stats['parameters_updated'], 1)
        self.assertEqual(merger.stats['parameters_resolved'], 1)
        self.assertEqual(merger.stats['returns_updated'], 1)
        self.assertEqual(merger.stats['returns_unresolved'], 1)
        
        merger.close()
    
    def test_columns_created_if_missing(self):
        """Test that columns are created if they don't exist."""
        # Create workspace_resolved.json
        workspace_resolved = {
            "_metadata": {
                "version": "1.0.0",
                "generated": "2026-03-13T00:00:00Z",
                "files_processed": 1
            },
            "./test.4gl": [
                {
                    "name": "process_account",
                    "parameters": [
                        {
                            "name": "acc",
                            "type": "LIKE account.*",
                            "is_like_reference": True,
                            "resolved": True,
                            "table": "account",
                            "columns": ["id"],
                            "types": ["INTEGER"]
                        }
                    ],
                    "returns": [
                        {
                            "name": "result",
                            "type": "LIKE account.id",
                            "is_like_reference": True,
                            "resolved": True,
                            "table": "account",
                            "columns": ["id"],
                            "types": ["INTEGER"]
                        }
                    ]
                }
            ]
        }
        
        with open(str(self.workspace_resolved_path), 'w') as f:
            json.dump(workspace_resolved, f)
        
        # Merge resolved types
        merger = ResolvedTypeMerger(str(self.db_path))
        merger.merge_resolved_types(str(self.workspace_resolved_path))
        merger.close()
        
        # Verify columns exist
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Check parameters table columns
        cursor.execute("PRAGMA table_info(parameters)")
        param_columns = {row[1] for row in cursor.fetchall()}
        
        self.assertIn('actual_type', param_columns)
        self.assertIn('is_like_reference', param_columns)
        self.assertIn('resolved', param_columns)
        self.assertIn('resolution_error', param_columns)
        self.assertIn('table_name', param_columns)
        self.assertIn('columns', param_columns)
        self.assertIn('types', param_columns)
        
        # Check returns table columns
        cursor.execute("PRAGMA table_info(returns)")
        return_columns = {row[1] for row in cursor.fetchall()}
        
        self.assertIn('actual_type', return_columns)
        self.assertIn('is_like_reference', return_columns)
        self.assertIn('resolved', return_columns)
        self.assertIn('resolution_error', return_columns)
        self.assertIn('table_name', return_columns)
        self.assertIn('columns', return_columns)
        self.assertIn('types', return_columns)
        
        conn.close()


if __name__ == '__main__':
    unittest.main()
