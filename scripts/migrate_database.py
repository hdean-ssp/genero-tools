#!/usr/bin/env python3
"""
Migrate workspace.db to add missing columns for type resolution improvements.

This script:
1. Adds file_path column to functions table
2. Adds resolved type columns to returns table
3. Adds NOT NULL constraint to parameters.name
4. Populates file_path from files table
"""

import sqlite3
import sys
from pathlib import Path

def migrate_database(db_path):
    """Migrate database schema."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Starting database migration...")
    
    # Step 1: Add file_path column to functions table if it doesn't exist
    print("\n1. Checking functions table...")
    cursor.execute("PRAGMA table_info(functions)")
    func_columns = {row[1] for row in cursor.fetchall()}
    
    if 'file_path' not in func_columns:
        print("   - Adding file_path column to functions table...")
        cursor.execute("ALTER TABLE functions ADD COLUMN file_path TEXT")
        
        # Populate file_path from files table
        print("   - Populating file_path from files table...")
        cursor.execute("""
            UPDATE functions
            SET file_path = (
                SELECT path FROM files WHERE files.id = functions.file_id
            )
        """)
        
        conn.commit()
        print("   ✓ file_path column added and populated")
    else:
        print("   ✓ file_path column already exists")
    
    # Step 2: Add resolved type columns to returns table
    print("\n2. Checking returns table...")
    cursor.execute("PRAGMA table_info(returns)")
    return_columns = {row[1] for row in cursor.fetchall()}
    
    required_columns = {
        'actual_type': 'TEXT',
        'is_like_reference': 'INTEGER DEFAULT 0',
        'resolved': 'INTEGER DEFAULT 0',
        'resolution_error': 'TEXT',
        'table_name': 'TEXT',
        'columns': 'TEXT',
        'types': 'TEXT'
    }
    
    for col_name, col_type in required_columns.items():
        if col_name not in return_columns:
            print(f"   - Adding {col_name} column to returns table...")
            cursor.execute(f"ALTER TABLE returns ADD COLUMN {col_name} {col_type}")
    
    conn.commit()
    print("   ✓ All required columns added to returns table")
    
    # Step 3: Add NOT NULL constraint to parameters.name
    print("\n3. Checking parameters table NOT NULL constraint...")
    cursor.execute("PRAGMA table_info(parameters)")
    param_columns = cursor.fetchall()
    name_column = next((col for col in param_columns if col[1] == 'name'), None)
    
    if name_column and name_column[3] == 0:  # notnull flag is 0 (not set)
        print("   - Adding NOT NULL constraint to parameters.name...")
        
        # Create new table with constraint
        cursor.execute('''CREATE TABLE parameters_new
                         (id INTEGER PRIMARY KEY, function_id INTEGER, name TEXT NOT NULL, type TEXT,
                          actual_type TEXT, is_like_reference INTEGER DEFAULT 0, resolved INTEGER DEFAULT 0,
                          resolution_error TEXT, table_name TEXT, columns TEXT, types TEXT,
                          FOREIGN KEY(function_id) REFERENCES functions(id))''')
        
        # Copy valid data (non-null, non-empty names)
        cursor.execute('''INSERT INTO parameters_new 
                         SELECT id, function_id, name, type, actual_type, is_like_reference, resolved,
                                resolution_error, table_name, columns, types
                         FROM parameters
                         WHERE name IS NOT NULL AND TRIM(name) != ''
                      ''')
        
        # Drop old table and rename new one
        cursor.execute('DROP TABLE parameters')
        cursor.execute('ALTER TABLE parameters_new RENAME TO parameters')
        
        # Recreate indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_parameters_function ON parameters(function_id)')
        
        conn.commit()
        print("   ✓ NOT NULL constraint added to parameters.name")
    else:
        print("   ✓ NOT NULL constraint already exists on parameters.name")
    
    # Step 4: Verify migration
    print("\n4. Verifying migration...")
    
    cursor.execute("PRAGMA table_info(functions)")
    func_columns = {row[1] for row in cursor.fetchall()}
    if 'file_path' in func_columns:
        print("   ✓ file_path column exists in functions table")
    else:
        print("   ✗ file_path column missing from functions table")
        return False
    
    cursor.execute("PRAGMA table_info(returns)")
    return_columns = {row[1] for row in cursor.fetchall()}
    for col_name in required_columns.keys():
        if col_name in return_columns:
            print(f"   ✓ {col_name} column exists in returns table")
        else:
            print(f"   ✗ {col_name} column missing from returns table")
            return False
    
    cursor.execute("PRAGMA table_info(parameters)")
    param_columns = cursor.fetchall()
    name_column = next((col for col in param_columns if col[1] == 'name'), None)
    if name_column and name_column[3] == 1:
        print("   ✓ NOT NULL constraint exists on parameters.name")
    else:
        print("   ✗ NOT NULL constraint missing from parameters.name")
        return False
    
    conn.close()
    print("\n✓ Database migration completed successfully!")
    return True


if __name__ == '__main__':
    db_path = sys.argv[1] if len(sys.argv) > 1 else 'workspace.db'
    
    if not Path(db_path).exists():
        print(f"Error: Database not found: {db_path}")
        sys.exit(1)
    
    if migrate_database(db_path):
        sys.exit(0)
    else:
        sys.exit(1)
