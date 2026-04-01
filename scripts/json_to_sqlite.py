#!/usr/bin/env python3
"""Convert JSON files to SQLite database for efficient querying."""

import json
import sqlite3
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(levelname)s: %(message)s'
)

def is_valid_parameter_name(name):
    """
    Validate if a parameter name is non-empty and non-null.
    
    Args:
        name: The parameter name to validate
        
    Returns:
        bool: True if the name is valid (non-empty, non-null), False otherwise
    """
    if name is None:
        return False
    if isinstance(name, str):
        return len(name.strip()) > 0
    return False

def migrate_add_not_null_constraint(conn):
    """
    Migrate existing database to add NOT NULL constraint to parameters table.
    
    This function handles databases created before the NOT NULL constraint was added.
    It creates a new parameters table with the constraint and migrates existing data,
    skipping any parameters with NULL or empty names.
    
    Args:
        conn: SQLite database connection
    """
    c = conn.cursor()
    
    try:
        # Check if parameters table exists
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='parameters'")
        if not c.fetchone():
            # Table doesn't exist, no migration needed
            return
        
        # Check if the table already has the NOT NULL constraint
        c.execute("PRAGMA table_info(parameters)")
        columns = c.fetchall()
        name_column = next((col for col in columns if col[1] == 'name'), None)
        
        if name_column and name_column[3] == 1:  # notnull flag is set
            # Constraint already exists
            return
        
        # Migration needed: create new table with constraint and migrate data
        c.execute('''CREATE TABLE parameters_new
                     (id INTEGER PRIMARY KEY, function_id INTEGER, name TEXT NOT NULL, type TEXT,
                      FOREIGN KEY(function_id) REFERENCES functions(id))''')
        
        # Copy valid data (non-null, non-empty names)
        c.execute('''INSERT INTO parameters_new (id, function_id, name, type)
                     SELECT id, function_id, name, type FROM parameters
                     WHERE name IS NOT NULL AND TRIM(name) != ''
                  ''')
        
        # Drop old table and rename new one
        c.execute('DROP TABLE parameters')
        c.execute('ALTER TABLE parameters_new RENAME TO parameters')
        
        # Recreate indexes
        c.execute('CREATE INDEX IF NOT EXISTS idx_parameters_function ON parameters(function_id)')
        
        conn.commit()
        logging.info("Successfully migrated parameters table with NOT NULL constraint")
    except Exception as e:
        logging.error(f"Migration failed: {e}")
        conn.rollback()
        raise

def create_signatures_db(json_file, db_file):
    """Create SQLite database from workspace.json signatures."""
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    
    # Run migration for existing databases
    migrate_add_not_null_constraint(conn)
    
    # Create tables
    c.execute('''CREATE TABLE IF NOT EXISTS files
                 (id INTEGER PRIMARY KEY, path TEXT UNIQUE, type TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS functions
                 (id INTEGER PRIMARY KEY, file_id INTEGER, name TEXT, 
                  line_start INTEGER, line_end INTEGER, signature TEXT, file_path TEXT,
                  FOREIGN KEY(file_id) REFERENCES files(id))''')
    
    # Parameters table with NOT NULL constraint on name column to ensure data quality.
    # This constraint prevents insertion of parameters with null or empty names,
    # maintaining database integrity and ensuring all parameters have valid identifiers.
    c.execute('''CREATE TABLE IF NOT EXISTS parameters
                 (id INTEGER PRIMARY KEY, function_id INTEGER, name TEXT NOT NULL, type TEXT,
                  FOREIGN KEY(function_id) REFERENCES functions(id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS returns
                 (id INTEGER PRIMARY KEY, function_id INTEGER, name TEXT, type TEXT,
                  FOREIGN KEY(function_id) REFERENCES functions(id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS calls
                 (id INTEGER PRIMARY KEY, function_id INTEGER, called_function_name TEXT, 
                  line_number INTEGER,
                  FOREIGN KEY(function_id) REFERENCES functions(id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS variables
                 (id INTEGER PRIMARY KEY, function_id INTEGER, name TEXT, type TEXT,
                  FOREIGN KEY(function_id) REFERENCES functions(id))''')
    
    # Create indexes
    c.execute('CREATE INDEX IF NOT EXISTS idx_functions_name ON functions(name)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_functions_file ON functions(file_id)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_parameters_function ON parameters(function_id)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_returns_function ON returns(function_id)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_calls_function ON calls(function_id)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_calls_called_name ON calls(called_function_name)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_variables_function ON variables(function_id)')
    
    # Load data
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    data.pop('_metadata', None)
    
    empty_param_count = 0
    
    for file_path, functions in data.items():
        # Determine file type
        file_type = "L4GLS" if "L4GLS" in file_path else ("U4GLS" if "U4GLS" in file_path else "4GLS")
        
        c.execute('INSERT INTO files (path, type) VALUES (?, ?)', (file_path, file_type))
        file_id = c.lastrowid
        
        for func in functions:
            c.execute('''INSERT INTO functions (file_id, name, line_start, line_end, signature, file_path)
                        VALUES (?, ?, ?, ?, ?, ?)''',
                     (file_id, func['name'], func['line']['start'], func['line']['end'], func['signature'], file_path))
            func_id = c.lastrowid
            
            # Insert parameters - filter out empty names
            for param in func.get('parameters', []):
                param_name = param.get('name')
                if not is_valid_parameter_name(param_name):
                    logging.warning(f"Skipping empty parameter in function '{func['name']}' at {file_path}")
                    empty_param_count += 1
                else:
                    c.execute('INSERT INTO parameters (function_id, name, type) VALUES (?, ?, ?)',
                             (func_id, param_name.strip(), param.get('type', '')))
            
            # Insert returns
            for ret in func.get('returns', []):
                c.execute('INSERT INTO returns (function_id, name, type) VALUES (?, ?, ?)',
                         (func_id, ret['name'], ret['type']))
            
            # Insert calls
            for call in func.get('calls', []):
                c.execute('INSERT INTO calls (function_id, called_function_name, line_number) VALUES (?, ?, ?)',
                         (func_id, call['name'], call['line']))
            
            # Insert variables
            for var in func.get('variables', []):
                c.execute('INSERT INTO variables (function_id, name, type) VALUES (?, ?, ?)',
                         (func_id, var['name'], var['type']))
    
    conn.commit()
    conn.close()
    
    if empty_param_count > 0:
        logging.warning(f"Total empty parameters skipped: {empty_param_count}")
    
    print(f"Created {db_file} from {json_file}")

def create_modules_db(json_file, db_file):
    """Create SQLite database from modules.json."""
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    
    # Create tables
    c.execute('''CREATE TABLE IF NOT EXISTS modules
                 (id INTEGER PRIMARY KEY, name TEXT UNIQUE, file TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS module_files
                 (id INTEGER PRIMARY KEY, module_id INTEGER, file_name TEXT, category TEXT,
                  FOREIGN KEY(module_id) REFERENCES modules(id))''')
    
    # Create indexes
    c.execute('CREATE INDEX IF NOT EXISTS idx_modules_name ON modules(name)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_module_files_module ON module_files(module_id)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_module_files_category ON module_files(category)')
    
    # Load data
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    for module in data.get('modules', []):
        c.execute('INSERT INTO modules (name, file) VALUES (?, ?)',
                 (module['module'], module['file']))
        module_id = c.lastrowid
        
        # Insert L4GLS files
        for fname in module.get('L4GLS', []):
            c.execute('INSERT INTO module_files (module_id, file_name, category) VALUES (?, ?, ?)',
                     (module_id, fname, 'L4GLS'))
        
        # Insert U4GLS files
        for fname in module.get('U4GLS', []):
            c.execute('INSERT INTO module_files (module_id, file_name, category) VALUES (?, ?, ?)',
                     (module_id, fname, 'U4GLS'))
        
        # Insert 4GLS files
        for fname in module.get('4GLS', []):
            c.execute('INSERT INTO module_files (module_id, file_name, category) VALUES (?, ?, ?)',
                     (module_id, fname, '4GLS'))
    
    conn.commit()
    conn.close()
    print(f"Created {db_file} from {json_file}")

def main():
    if len(sys.argv) < 3:
        print("Usage: json_to_sqlite.py <type> <json_file> [db_file]", file=sys.stderr)
        print("  type: 'signatures' or 'modules'", file=sys.stderr)
        sys.exit(1)
    
    json_type = sys.argv[1]
    json_file = sys.argv[2]
    db_file = sys.argv[3] if len(sys.argv) > 3 else json_file.replace('.json', '.db')
    
    if not Path(json_file).exists():
        print(f"Error: {json_file} not found", file=sys.stderr)
        sys.exit(1)
    
    try:
        if json_type == 'signatures':
            create_signatures_db(json_file, db_file)
        elif json_type == 'modules':
            create_modules_db(json_file, db_file)
        else:
            print(f"Error: Unknown type '{json_type}'", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
