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
        self.schema_loaded = False
        try:
            self.cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='schema_tables'
            """)
            if not self.cursor.fetchone():
                print("Error: schema_tables not found in database - type resolution cannot proceed", file=sys.stderr)
                print("Ensure parse_schema.py and json_to_sqlite_schema.py ran successfully", file=sys.stderr)
                return
        except Exception as e:
            print(f"Error: Could not check for schema tables: {e}", file=sys.stderr)
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
            print(f"Error: Could not load schema: {e}", file=sys.stderr)
            return
        
        self.schema_loaded = True
    
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
        # Supports: LIKE table.column, LIKE table.*, LIKE schema:table.column, LIKE schema:table.*
        match = re.match(r'LIKE\s+(?:(\w+):)?(\w+)\.(\*|\w+)', like_ref.strip(), re.IGNORECASE)
        if not match:
            return {
                'resolved': False,
                'error': f'Invalid LIKE pattern: {like_ref}'
            }
        
        schema_name = match.group(1)  # May be None
        table_name = match.group(2)
        column_pattern = match.group(3)
        
        # Check if table exists (case-insensitive)
        table_key = None
        for t in self.tables:
            if t.lower() == table_name.lower():
                table_key = t
                break
        
        if table_key is None:
            return {
                'table': table_name,
                'resolved': False,
                'error': f'Table not found: {table_name}'
            }
        
        columns = self.tables[table_key]
        
        # Handle LIKE table.*
        if column_pattern == '*':
            return {
                'table': table_key,
                'columns': [col['name'] for col in columns],
                'types': [col['type'] for col in columns],
                'resolved': True
            }
        
        # Handle LIKE table.column (case-insensitive)
        for col in columns:
            if col['name'].lower() == column_pattern.lower():
                return {
                    'table': table_key,
                    'columns': [col['name']],
                    'types': [col['type']],
                    'resolved': True
                }
        
        return {
            'table': table_key,
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
    
    def resolve_return_type(self, return_type: str) -> Dict:
        """
        Resolve a return type, handling LIKE references.
        
        Returns enhanced type info with resolution status.
        This is similar to resolve_parameter_type but specifically for return types.
        """
        if not return_type.strip().upper().startswith('LIKE'):
            # Not a LIKE reference, return as-is
            return {
                'type': return_type,
                'is_like_reference': False,
                'resolved': True
            }
        
        # Resolve LIKE reference
        resolution = self.resolve_like_reference(return_type)
        resolution['is_like_reference'] = True
        resolution['original_type'] = return_type
        
        return resolution
    
    def process_workspace_json(self, workspace_json_path: str) -> Dict:
        """
        Process workspace.json and resolve all LIKE references.
        
        workspace.json format:
        {
            "_metadata": {...},
            "./path/to/file.4gl": [
                {"name": "func1", "parameters": [...], "returns": [...], ...},
                {"name": "func2", "parameters": [...], "returns": [...], ...}
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
                    
                    # Resolve return types from 'returns' array
                    if 'returns' in func and isinstance(func['returns'], list):
                        for ret in func['returns']:
                            if 'type' in ret:
                                resolution = self.resolve_return_type(ret['type'])
                                ret.update(resolution)
                    
                    # Also handle legacy 'return_type' field for backward compatibility
                    if 'return_type' in func:
                        resolution = self.resolve_return_type(func['return_type'])
                        func['return_type_resolved'] = resolution
        
        return workspace
    
    def close(self):
        """Close database connection."""
        self.conn.close()


def main():
    """Main entry point."""
    if len(sys.argv) < 3:
        print("Usage: resolve_types.py <db_path> <workspace_json_path> [output_path] [--changes <changes_file>]")
        sys.exit(1)
    
    db_path = sys.argv[1]
    workspace_json_path = sys.argv[2]
    
    # Parse remaining args (output_path and --changes)
    output_path = workspace_json_path
    changes_file = None
    
    i = 3
    while i < len(sys.argv):
        if sys.argv[i] == '--changes' and i + 1 < len(sys.argv):
            changes_file = sys.argv[i + 1]
            i += 2
        else:
            output_path = sys.argv[i]
            i += 1
    
    # Validate inputs
    if not Path(db_path).exists():
        print(f"Error: Database not found: {db_path}", file=sys.stderr)
        sys.exit(1)
    
    if not Path(workspace_json_path).exists():
        print(f"Error: workspace.json not found: {workspace_json_path}", file=sys.stderr)
        sys.exit(1)
    
    # Determine which files to resolve
    changed_files = None
    if changes_file and Path(changes_file).exists():
        import os
        with open(changes_file, 'r') as f:
            changes = json.load(f)
        changed = set(changes.get('changed', []))
        added = set(changes.get('added', []))
        # Normalize paths
        changed_files = set()
        for p in changed | added:
            p = os.path.normpath(p)
            if not p.startswith('./') and not p.startswith('/'):
                p = './' + p
            changed_files.add(p)
    
    # Resolve types
    resolver = TypeResolver(db_path)
    try:
        if not resolver.schema_loaded:
            print("Error: Schema could not be loaded - type resolution aborted", file=sys.stderr)
            sys.exit(1)
        
        # If incremental, load existing resolved file and only update changed entries
        if changed_files and Path(output_path).exists():
            # Load existing resolved output
            with open(output_path, 'r') as f:
                workspace = json.load(f)
            
            # Also load the source workspace.json for the changed files' data
            with open(workspace_json_path, 'r') as f:
                source = json.load(f)
            
            # Update only changed files in the resolved output
            for file_path in list(source.keys()):
                if file_path == '_metadata':
                    workspace['_metadata'] = source['_metadata']
                    continue
                
                # Check if this file is in changed set
                if file_path not in changed_files:
                    continue
                
                functions = source[file_path]
                if not isinstance(functions, list):
                    workspace[file_path] = functions
                    continue
                
                # Resolve types for this file's functions
                for func in functions:
                    if 'parameters' in func:
                        for param in func['parameters']:
                            if 'type' in param:
                                resolution = resolver.resolve_parameter_type(param['type'])
                                param.update(resolution)
                    
                    if 'returns' in func and isinstance(func['returns'], list):
                        for ret in func['returns']:
                            if 'type' in ret:
                                resolution = resolver.resolve_return_type(ret['type'])
                                ret.update(resolution)
                    
                    if 'return_type' in func:
                        resolution = resolver.resolve_return_type(func['return_type'])
                        func['return_type_resolved'] = resolution
                
                workspace[file_path] = functions
            
            # Remove deleted files
            removed = set(changes.get('removed', []))
            import os
            removed_normalized = set()
            for p in removed:
                p = os.path.normpath(p)
                if not p.startswith('./') and not p.startswith('/'):
                    p = './' + p
                removed_normalized.add(p)
            
            for key in list(workspace.keys()):
                if key in removed_normalized:
                    del workspace[key]
        else:
            # Full resolution
            workspace = resolver.process_workspace_json(workspace_json_path)
        
        # Write output
        with open(output_path, 'w') as f:
            json.dump(workspace, f, indent=2)
        
        # Summarize resolution results
        resolved_count = 0
        unresolved_count = 0
        unresolved_items = []
        
        for file_path, functions in workspace.items():
            if file_path == '_metadata':
                continue
            if not isinstance(functions, list):
                continue
            for func in functions:
                for param in func.get('parameters', []):
                    if param.get('is_like_reference'):
                        if param.get('resolved'):
                            resolved_count += 1
                        else:
                            unresolved_count += 1
                            unresolved_items.append(
                                f"param {param.get('name')} in {func.get('name')} ({file_path}): {param.get('error', 'unknown')}"
                            )
                for ret in func.get('returns', []):
                    if ret.get('is_like_reference'):
                        if ret.get('resolved'):
                            resolved_count += 1
                        else:
                            unresolved_count += 1
                            unresolved_items.append(
                                f"return {ret.get('name')} in {func.get('name')} ({file_path}): {ret.get('error', 'unknown')}"
                            )
        
        mode = "incremental" if changed_files else "full"
        print(f"Type resolution complete ({mode}). Output: {output_path}")
        print(f"  LIKE references resolved: {resolved_count}")
        print(f"  LIKE references unresolved: {unresolved_count}")
        
        if unresolved_items:
            print(f"\n  Unresolved LIKE references:")
            for item in unresolved_items[:20]:
                print(f"    - {item}")
            if len(unresolved_items) > 20:
                print(f"    ... and {len(unresolved_items) - 20} more")
    finally:
        resolver.close()


if __name__ == '__main__':
    main()
