#!/usr/bin/env python3
"""
Load schema JSON into SQLite database.

Creates schema_tables and schema_columns tables and loads data from schema.json.
"""

import json
import sqlite3
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional


class SchemaDatabase:
    """Manages schema data in SQLite database."""
    
    def __init__(self, db_file: str):
        """
        Initialize schema database.
        
        Args:
            db_file: Path to SQLite database file
        """
        self.db_file = db_file
        self.conn: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None
        self.tables_inserted = 0
        self.columns_inserted = 0
        self.errors: List[str] = []
    
    def connect(self) -> None:
        """Connect to database."""
        try:
            self.conn = sqlite3.connect(self.db_file)
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Failed to connect to database: {e}")
    
    def disconnect(self) -> None:
        """Disconnect from database."""
        if self.conn:
            self.conn.close()
    
    def create_tables(self) -> None:
        """Create schema tables in database."""
        if not self.cursor:
            raise RuntimeError("Not connected to database")
        
        try:
            # Create schema_tables table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS schema_tables (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    source_file TEXT,
                    line_number INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create schema_columns table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS schema_columns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    table_id INTEGER NOT NULL,
                    column_name TEXT NOT NULL,
                    column_type TEXT NOT NULL,
                    type_code INTEGER,
                    length INTEGER,
                    position INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (table_id) REFERENCES schema_tables(id),
                    UNIQUE(table_id, column_name)
                )
            """)
            
            # Create indexes
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_schema_tables_name 
                ON schema_tables(name)
            """)
            
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_schema_columns_table_id 
                ON schema_columns(table_id)
            """)
            
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_schema_columns_name 
                ON schema_columns(column_name)
            """)
            
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_schema_columns_type_code 
                ON schema_columns(type_code)
            """)
            
            self.conn.commit()
            
        except sqlite3.Error as e:
            self.errors.append(f"Failed to create tables: {e}")
            raise
    
    def load_schema(self, schema_data: Dict[str, Any]) -> None:
        """
        Load schema data into database.
        
        Args:
            schema_data: Schema dictionary from schema.json
        """
        if not self.cursor:
            raise RuntimeError("Not connected to database")
        
        try:
            # Clear existing data
            self.cursor.execute("DELETE FROM schema_columns")
            self.cursor.execute("DELETE FROM schema_tables")
            
            # Insert tables and columns
            for table in schema_data.get("tables", []):
                table_name = table.get("name")
                
                if not table_name:
                    self.errors.append("Table without name found")
                    continue
                
                try:
                    # Insert table
                    self.cursor.execute(
                        "INSERT INTO schema_tables (name, source_file) VALUES (?, ?)",
                        (table_name, None)
                    )
                    table_id = self.cursor.lastrowid
                    self.tables_inserted += 1
                    
                    # Insert columns
                    for column in table.get("columns", []):
                        column_name = column.get("name")
                        column_type = column.get("type")
                        type_code = column.get("type_code")
                        length = column.get("length")
                        position = column.get("position")
                        
                        if not column_name or not column_type:
                            self.errors.append(
                                f"Column without name or type in table {table_name}"
                            )
                            continue
                        
                        self.cursor.execute(
                            """INSERT INTO schema_columns 
                               (table_id, column_name, column_type, type_code, length, position)
                               VALUES (?, ?, ?, ?, ?, ?)""",
                            (table_id, column_name, column_type, type_code, length, position)
                        )
                        self.columns_inserted += 1
                
                except sqlite3.IntegrityError as e:
                    self.errors.append(f"Integrity error for table {table_name}: {e}")
                except sqlite3.Error as e:
                    self.errors.append(f"Error inserting table {table_name}: {e}")
            
            self.conn.commit()
            
        except sqlite3.Error as e:
            self.errors.append(f"Failed to load schema: {e}")
            raise
    
    def get_table_count(self) -> int:
        """Get count of tables in database."""
        if not self.cursor:
            return 0
        
        self.cursor.execute("SELECT COUNT(*) FROM schema_tables")
        result = self.cursor.fetchone()
        return result[0] if result else 0
    
    def get_column_count(self) -> int:
        """Get count of columns in database."""
        if not self.cursor:
            return 0
        
        self.cursor.execute("SELECT COUNT(*) FROM schema_columns")
        result = self.cursor.fetchone()
        return result[0] if result else 0
    
    def get_table(self, table_name: str) -> Optional[Dict[str, Any]]:
        """
        Get table definition from database.
        
        Args:
            table_name: Name of table
            
        Returns:
            Table definition or None if not found
        """
        if not self.cursor:
            return None
        
        self.cursor.execute(
            "SELECT id, name FROM schema_tables WHERE name = ?",
            (table_name,)
        )
        result = self.cursor.fetchone()
        
        if not result:
            return None
        
        table_id, name = result
        
        # Get columns
        self.cursor.execute(
            """SELECT column_name, column_type, type_code, length, position 
               FROM schema_columns 
               WHERE table_id = ? 
               ORDER BY position""",
            (table_id,)
        )
        
        columns = []
        for row in self.cursor.fetchall():
            columns.append({
                "name": row[0],
                "type": row[1],
                "type_code": row[2],
                "length": row[3],
                "position": row[4]
            })
        
        return {
            "id": table_id,
            "name": name,
            "columns": columns
        }
    
    def get_column(self, table_name: str, column_name: str) -> Optional[Dict[str, Any]]:
        """
        Get column definition from database.
        
        Args:
            table_name: Name of table
            column_name: Name of column
            
        Returns:
            Column definition or None if not found
        """
        if not self.cursor:
            return None
        
        self.cursor.execute(
            """SELECT sc.column_name, sc.column_type, sc.type_code, sc.length, sc.position
               FROM schema_columns sc
               JOIN schema_tables st ON sc.table_id = st.id
               WHERE st.name = ? AND sc.column_name = ?""",
            (table_name, column_name)
        )
        
        result = self.cursor.fetchone()
        
        if not result:
            return None
        
        return {
            "name": result[0],
            "type": result[1],
            "type_code": result[2],
            "length": result[3],
            "position": result[4]
        }
    
    def find_tables_by_type(self, type_code: int) -> List[Dict[str, Any]]:
        """
        Find all tables containing columns of a specific type.
        
        Args:
            type_code: Informix type code
            
        Returns:
            List of table definitions
        """
        if not self.cursor:
            return []
        
        self.cursor.execute(
            """SELECT DISTINCT st.id, st.name 
               FROM schema_tables st
               JOIN schema_columns sc ON st.id = sc.table_id
               WHERE sc.type_code = ?""",
            (type_code,)
        )
        
        tables = []
        for row in self.cursor.fetchall():
            table = self.get_table(row[1])
            if table:
                tables.append(table)
        
        return tables
    
    def find_columns_by_type(self, type_code: int) -> List[Dict[str, Any]]:
        """
        Find all columns of a specific type.
        
        Args:
            type_code: Informix type code
            
        Returns:
            List of column definitions with table names
        """
        if not self.cursor:
            return []
        
        self.cursor.execute(
            """SELECT st.name, sc.column_name, sc.column_type, sc.type_code, sc.length, sc.position
               FROM schema_columns sc
               JOIN schema_tables st ON sc.table_id = st.id
               WHERE sc.type_code = ?
               ORDER BY st.name, sc.position""",
            (type_code,)
        )
        
        columns = []
        for row in self.cursor.fetchall():
            columns.append({
                "table_name": row[0],
                "name": row[1],
                "type": row[2],
                "type_code": row[3],
                "length": row[4],
                "position": row[5]
            })
        
        return columns


def load_schema_file(schema_json_file: str, db_file: str) -> None:
    """
    Load schema from JSON file into SQLite database.
    
    Args:
        schema_json_file: Path to schema.json file
        db_file: Path to SQLite database file
        
    Raises:
        FileNotFoundError: If schema file doesn't exist
        json.JSONDecodeError: If schema file is invalid JSON
        sqlite3.Error: If database operation fails
    """
    # Read schema JSON
    try:
        with open(schema_json_file, 'r', encoding='utf-8') as f:
            schema_data = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Schema file not found: {schema_json_file}")
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON in schema file: {e}", "", 0)
    
    # Load into database
    db = SchemaDatabase(db_file)
    
    try:
        db.connect()
        db.create_tables()
        db.load_schema(schema_data)
        
        print(f"[OK] Loaded {db.tables_inserted} tables")
        print(f"[OK] Loaded {db.columns_inserted} columns")
        print(f"[OK] Database: {db_file}")
        
        if db.errors:
            print(f"\n[WARN] Warnings ({len(db.errors)}):")
            for error in db.errors[:5]:
                print(f"  - {error}")
            if len(db.errors) > 5:
                print(f"  ... and {len(db.errors) - 5} more")
        
    finally:
        db.disconnect()


def main():
    """Command-line interface."""
    if len(sys.argv) < 2:
        print("Usage: python3 json_to_sqlite_schema.py <schema.json> [database.db]")
        print()
        print("Loads schema data from JSON into SQLite database.")
        print()
        print("Arguments:")
        print("  schema.json   - Input schema JSON file")
        print("  database.db   - Output SQLite database (default: workspace.db)")
        sys.exit(1)
    
    schema_file = sys.argv[1]
    db_file = sys.argv[2] if len(sys.argv) > 2 else "workspace.db"
    
    try:
        load_schema_file(schema_file, db_file)
    except FileNotFoundError as e:
        sys.stderr.write(f"Error: {e}\n")
        sys.exit(1)
    except json.JSONDecodeError as e:
        sys.stderr.write(f"Error: {e}\n")
        sys.exit(1)
    except sqlite3.Error as e:
        sys.stderr.write(f"Database error: {e}\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"Unexpected error: {e}\n")
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
