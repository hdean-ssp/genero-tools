#!/usr/bin/env python3
"""
Type Resolution Engine - Resolves LIKE references to actual database schema types.

This script:
1. Loads schema from workspace.db (schema_tables, schema_columns)
2. Parses LIKE references from workspace.json
3. Resolves table/column references to actual types
4. Merges resolved type info back into workspace.json
5. Handles edge cases (missing tables, columns, etc.)
"""

import json
import sqlite3
import sys
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class TypeResolver:
    """Resolves LIKE references to database schema types."""
    
    def __init__(self, db_path: str):
        """Initialize resolver with database connection."""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self._load_schema_cache()
    
    def _load_schema_cache(self):
        """Load schema into memory for fast lookups."""
        self.tables = {}
        
        # Check if schema tables exist
        try:
            self.cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='schema_tables'
            """)
            if not self.cursor.fetchone():
                print("Warning: schema_tables not found in database", file=sys.stderr)
                print("Type resolution will not work without schema", file=sys.stderr)
                return
        except Exception as e:
            print(f"Warning: Could not check for schema tables: {e}", file=sys.stderr)
            return
        
        # Query all tables and columns
        try:
            self.cursor.execute("""
                SELECT 
                    st.name as table_name,
                    sc.column_name,
                    sc.column_type
                FROM schema_tables st
                LEFT JOIN schema_columns sc ON st.id = sc.table_id
                ORDER BY st.name, sc.id
            """)
            
            for row in self.cursor.fetchall():
                table_name = row['table_name']
                if table_name not in self.tables:
                    self.tables[table_name] = []
                
                if row['column_name']:
                    self.tables[table_name].append({
                        'name': row['column_name'],
                        'type': row['column_type']
                    })
        except Exception as e:
            print(f"Warning: Could not load schema: {e}", file=sys.stderr)
    
    def resolve_like_reference(self, like_ref: str) -> Optional[Dict]:
        """
        Resolve a LIKE reference to table/column definitions.
        
        Patterns:
        - LIKE table.* → all columns of table
        - LIKE table.column → specific column
        
        Returns:
        {
            'table': 'table_name',
            'columns': ['col1', 'col2', ...],
            'types': ['type1', 'type2', ...],
            'resolved': True/False,
            'error': 'error message if not resolved'
        }
        """
        # Extract table and column pattern
        match = re.match(r'LIKE\s+(\w+)\.(\*|\w+)', like_ref.strip(), re.IGNORECASE)
        if not match:
            return {
                'resolved': False,
                'error': f'Invalid LIKE pattern: {like_ref}'
            }
        
        table_name = match.group(1)
        column_pattern = match.group(2)
        
        # Check if table exists
        if table_name not in self.tables:
            return {
                'table': table_name,
                'resolved': False,
                'error': f'Table not found: {table_name}'
            }
        
        columns = self.tables[table_name]
        
        # Handle LIKE table.*
        if column_pattern == '*':
            return {
                'table': table_name,
                'columns': [col['name'] for col in columns],
                'types': [col['type'] for col in columns],
                'resolved': True
            }
        
        # Handle LIKE table.column
        for col in columns:
            if col['name'] == column_pattern:
                return {
                    'table': table_name,
                    'columns': [col['name']],
                    'types': [col['type']],
                    'resolved': True
                }
        
        return {
            'table': table_name,
            'column': column_pattern,
            'resolved': False,
            'error': f'Column not found: {table_name}.{column_pattern}'
        }
    
    def resolve_parameter_type(self, param_type: str) -> Dict:
        """
        Resolve a parameter type, handling LIKE references.
        
        Returns enhanced type info with resolution status.
        """
        if not param_type.strip().upper().startswith('LIKE'):
            # Not a LIKE reference, return as-is
            return {
                'type': param_type,
                'is_like_reference': False,
                'resolved': True
            }
        
        # Resolve LIKE reference
        resolution = self.resolve_like_reference(param_type)
        resolution['is_like_reference'] = True
        resolution['original_type'] = param_type
        
        return resolution
    
    def process_workspace_json(self, workspace_json_path: str) -> Dict:
        """
        Process workspace.json and resolve all LIKE references.
        
        workspace.json format:
        {
            "_metadata": {...},
            "./path/to/file.4gl": [
                {"name": "func1", "parameters": [...], ...},
                {"name": "func2", "parameters": [...], ...}
            ]
        }
        
        Returns updated workspace data with same structure.
        """
        with open(workspace_json_path, 'r') as f:
            workspace = json.load(f)
        
        # Process each file's functions
        for file_path, functions in workspace.items():
            # Skip metadata
            if file_path == '_metadata':
                continue
            
            # Process each function in the file
            if isinstance(functions, list):
                for func in functions:
                    # Resolve parameter types
                    if 'parameters' in func:
                        for param in func['parameters']:
                            if 'type' in param:
                                resolution = self.resolve_parameter_type(param['type'])
                                param.update(resolution)
                    
                    # Resolve return types
                    if 'return_type' in func:
                        resolution = self.resolve_parameter_type(func['return_type'])
                        func['return_type_resolved'] = resolution
        
        return workspace
    
    def close(self):
        """Close database connection."""
        self.conn.close()


def main():
    """Main entry point."""
    if len(sys.argv) < 3:
        print("Usage: resolve_types.py <db_path> <workspace_json_path> [output_path]")
        sys.exit(1)
    
    db_path = sys.argv[1]
    workspace_json_path = sys.argv[2]
    output_path = sys.argv[3] if len(sys.argv) > 3 else workspace_json_path
    
    # Validate inputs
    if not Path(db_path).exists():
        print(f"Error: Database not found: {db_path}", file=sys.stderr)
        sys.exit(1)
    
    if not Path(workspace_json_path).exists():
        print(f"Error: workspace.json not found: {workspace_json_path}", file=sys.stderr)
        sys.exit(1)
    
    # Resolve types
    resolver = TypeResolver(db_path)
    try:
        workspace = resolver.process_workspace_json(workspace_json_path)
        
        # Write output
        with open(output_path, 'w') as f:
            json.dump(workspace, f, indent=2)
        
        print(f"Type resolution complete. Output: {output_path}")
    finally:
        resolver.close()


if __name__ == '__main__':
    main()
