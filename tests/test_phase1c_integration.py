#!/usr/bin/env python3
"""
Integration tests for Phase 1c - Enhanced Type Parser

Tests the complete workflow:
1. Parse schema files
2. Load schema into database
3. Generate function signatures
4. Resolve LIKE types
5. Verify resolved types in output
"""

import json
import sqlite3
import subprocess
import tempfile
import unittest
from pathlib import Path


class TestPhase1cIntegration(unittest.TestCase):
    """Integration tests for Phase 1c type resolution."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.project_root = Path(__file__).parent.parent
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_type_resolution_workflow(self):
        """Test complete type resolution workflow."""
        # Create test schema
        schema_file = self.temp_dir / 'test_schema.sch'
        schema_file.write_text("""account^id^2^4^1^
account^name^0^100^2^
account^balance^5^10^3^
customer^id^2^4^1^
customer^email^0^255^2^
""")
        
        # Create test 4GL file
        code_file = self.temp_dir / 'test.4gl'
        code_file.write_text("""FUNCTION process_account(acc LIKE account.*)
    DEFINE acc LIKE account.*
    DEFINE id INTEGER
    
    LET id = acc.id
    
    RETURN id
END FUNCTION

FUNCTION get_customer(cust LIKE customer.id)
    DEFINE cust LIKE customer.id
    
    RETURN cust
END FUNCTION
""")
        
        # Create database with schema
        db_file = self.temp_dir / 'workspace.db'
        conn = sqlite3.connect(str(db_file))
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
        
        # Insert schema data
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
        """, (account_id, 'balance', 'DECIMAL(10)'))
        
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
        
        # Generate signatures
        workspace_file = self.temp_dir / 'workspace.json'
        result = subprocess.run(
            ['bash', str(self.project_root / 'src' / 'generate_signatures.sh'), str(self.temp_dir)],
            cwd=str(self.temp_dir),
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.returncode, 0, f"generate_signatures.sh failed: {result.stderr}")
        self.assertTrue(workspace_file.exists(), "workspace.json not created")
        
        # Load generated signatures
        with open(workspace_file) as f:
            signatures = json.load(f)
        
        self.assertEqual(len(signatures), 2, "Should have 2 functions")
        
        # Resolve types
        resolved_file = self.temp_dir / 'workspace_resolved.json'
        result = subprocess.run(
            ['python3', str(self.project_root / 'scripts' / 'resolve_types.py'),
             str(db_file), str(workspace_file), str(resolved_file)],
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.returncode, 0, f"resolve_types.py failed: {result.stderr}")
        self.assertTrue(resolved_file.exists(), "workspace_resolved.json not created")
        
        # Verify resolved types
        with open(resolved_file) as f:
            resolved = json.load(f)
        
        # Get functions from the file
        self.assertIn('./test.4gl', resolved)
        functions = resolved['./test.4gl']
        self.assertEqual(len(functions), 2, "Should have 2 functions")
        
        # Check first function (process_account)
        func1 = functions[0]
        self.assertEqual(func1['name'], 'process_account')
        
        param1 = func1['parameters'][0]
        self.assertTrue(param1['resolved'])
        self.assertTrue(param1['is_like_reference'])
        self.assertEqual(param1['table'], 'account')
        self.assertEqual(param1['columns'], ['id', 'name', 'balance'])
        self.assertEqual(param1['types'], ['INTEGER', 'VARCHAR(100)', 'DECIMAL(10)'])
        
        # Check second function (get_customer)
        func2 = functions[1]
        self.assertEqual(func2['name'], 'get_customer')
        
        param2 = func2['parameters'][0]
        self.assertTrue(param2['resolved'])
        self.assertTrue(param2['is_like_reference'])
        self.assertEqual(param2['table'], 'customer')
        self.assertEqual(param2['columns'], ['id'])
        self.assertEqual(param2['types'], ['INTEGER'])
    
    def test_unresolved_like_reference(self):
        """Test handling of unresolved LIKE references."""
        # Create database with minimal schema
        db_file = self.temp_dir / 'workspace.db'
        conn = sqlite3.connect(str(db_file))
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
        
        conn.commit()
        conn.close()
        
        # Create workspace.json with unresolved reference
        workspace_file = self.temp_dir / 'workspace.json'
        workspace = {
            "_metadata": {
                "version": "1.0.0",
                "generated": "2026-03-13T00:00:00Z",
                "files_processed": 1
            },
            "./test.4gl": [
                {
                    'name': 'test_func',
                    'parameters': [
                        {'name': 'rec', 'type': 'LIKE nonexistent.*'}
                    ],
                    'return_type': 'VOID'
                }
            ]
        }
        
        with open(workspace_file, 'w') as f:
            json.dump(workspace, f)
        
        # Resolve types
        resolved_file = self.temp_dir / 'workspace_resolved.json'
        result = subprocess.run(
            ['python3', str(self.project_root / 'scripts' / 'resolve_types.py'),
             str(db_file), str(workspace_file), str(resolved_file)],
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.returncode, 0)
        
        # Verify unresolved reference is marked
        with open(resolved_file) as f:
            resolved = json.load(f)
        
        param = resolved['./test.4gl'][0]['parameters'][0]
        self.assertFalse(param['resolved'])
        self.assertTrue(param['is_like_reference'])
        self.assertIn('error', param)


class TestTypeResolutionPerformance(unittest.TestCase):
    """Performance tests for type resolution."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.project_root = Path(__file__).parent.parent
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_resolution_performance(self):
        """Test type resolution performance with large workspace."""
        import time
        
        # Create database with many tables
        db_file = self.temp_dir / 'workspace.db'
        conn = sqlite3.connect(str(db_file))
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
        
        # Insert 100 tables with 10 columns each
        for t in range(100):
            table_name = f'table_{t}'
            cursor.execute("INSERT INTO schema_tables (name) VALUES (?)", (table_name,))
            table_id = cursor.lastrowid
            
            for c in range(10):
                col_name = f'col_{c}'
                col_type = 'INTEGER' if c % 2 == 0 else 'VARCHAR(100)'
                cursor.execute("""
                    INSERT INTO schema_columns (table_id, column_name, column_type)
                    VALUES (?, ?, ?)
                """, (table_id, col_name, col_type))
        
        conn.commit()
        conn.close()
        
        # Create workspace.json with 1000 functions
        workspace_file = self.temp_dir / 'workspace.json'
        workspace = {
            "_metadata": {
                "version": "1.0.0",
                "generated": "2026-03-13T00:00:00Z",
                "files_processed": 1
            },
            "./test.4gl": []
        }
        
        for f in range(1000):
            table_idx = f % 100
            workspace["./test.4gl"].append({
                'name': f'func_{f}',
                'parameters': [
                    {'name': 'rec', 'type': f'LIKE table_{table_idx}.*'}
                ],
                'return_type': 'VOID'
            })
        
        with open(workspace_file, 'w') as f:
            json.dump(workspace, f)
        
        # Measure resolution time
        resolved_file = self.temp_dir / 'workspace_resolved.json'
        start = time.time()
        
        result = subprocess.run(
            ['python3', str(self.project_root / 'scripts' / 'resolve_types.py'),
             str(db_file), str(workspace_file), str(resolved_file)],
            capture_output=True,
            text=True
        )
        
        elapsed = time.time() - start
        
        self.assertEqual(result.returncode, 0)
        
        # Should complete in reasonable time (< 5 seconds for 1000 functions)
        self.assertLess(elapsed, 5.0, f"Resolution took {elapsed:.2f}s, expected < 5s")
        
        # Verify output
        with open(resolved_file) as f:
            resolved = json.load(f)
        
        self.assertEqual(len(resolved['./test.4gl']), 1000)
        
        # Spot check a few functions
        for idx in [0, 500, 999]:
            func = resolved['./test.4gl'][idx]
            param = func['parameters'][0]
            self.assertTrue(param['resolved'])


if __name__ == '__main__':
    unittest.main()
