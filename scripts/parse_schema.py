#!/usr/bin/env python3
"""
Informix IDS Schema Parser

Parses .sch files (pipe-delimited format) and generates schema.json
with table and column definitions.

Format: table_name^column_name^type_code^length^position^
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional


class InformixTypeMapper:
    """Maps Informix type codes to Genero types."""
    
    TYPE_MAP = {
        0: "VARCHAR",      # CHAR/VARCHAR
        1: "SMALLINT",     # SMALLINT
        2: "INTEGER",      # INTEGER
        5: "DECIMAL",      # DECIMAL/NUMERIC
        7: "DATE",         # DATE
        10: "DATETIME",    # DATETIME
        262: "SERIAL",     # SERIAL (auto-increment)
    }
    
    @staticmethod
    def map_type(type_code: int, length: int) -> str:
        """
        Map Informix type code to Genero type string.
        
        Args:
            type_code: Informix type code (0, 1, 2, 5, 7, 10, 262, etc.)
            length: Column length/precision
            
        Returns:
            Genero type string (e.g., "VARCHAR(8)", "INTEGER", "DATE")
        """
        base_type = InformixTypeMapper.TYPE_MAP.get(type_code)
        
        if base_type is None:
            return f"UNKNOWN({type_code})"
        
        # Types that include length
        if base_type in ("VARCHAR", "DECIMAL"):
            return f"{base_type}({length})"
        
        # Types without length
        return base_type


class SchemaParser:
    """Parses Informix IDS schema files."""
    
    def __init__(self):
        """Initialize the schema parser."""
        self.schema: Dict[str, Any] = {"tables": {}}
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.lines_processed = 0
        self.lines_skipped = 0
    
    def parse_file(self, filename: str) -> Dict[str, Any]:
        """
        Parse a schema file and return structured schema data.
        
        Args:
            filename: Path to .sch file
            
        Returns:
            Dictionary with schema data
            
        Raises:
            FileNotFoundError: If file doesn't exist
            IOError: If file can't be read
        """
        self.schema = {"tables": {}}
        self.errors = []
        self.warnings = []
        self.lines_processed = 0
        self.lines_skipped = 0
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    self._parse_line(line, line_num)
        except FileNotFoundError:
            raise FileNotFoundError(f"Schema file not found: {filename}")
        except IOError as e:
            raise IOError(f"Error reading schema file: {e}")
        
        # Convert tables dict to list
        self.schema["tables"] = list(self.schema["tables"].values())
        
        # Add metadata
        self.schema["_metadata"] = {
            "version": "1.0.0",
            "lines_processed": self.lines_processed,
            "lines_skipped": self.lines_skipped,
            "tables_count": len(self.schema["tables"]),
            "errors": self.errors,
            "warnings": self.warnings
        }
        
        return self.schema
    
    def _parse_line(self, line: str, line_num: int) -> None:
        """
        Parse a single line from schema file.
        
        Format: table_name^column_name^type_code^length^position^
        
        Args:
            line: Line to parse
            line_num: Line number (for error reporting)
        """
        line = line.strip()
        
        # Skip empty lines
        if not line:
            self.lines_skipped += 1
            return
        
        # Skip comment lines (if any)
        if line.startswith('#'):
            self.lines_skipped += 1
            return
        
        # Parse pipe-delimited format
        parts = line.split('^')
        
        # Must have at least 5 parts (table, column, type, length, position)
        if len(parts) < 5:
            self.warnings.append(f"Line {line_num}: Invalid format (expected 5+ fields, got {len(parts)})")
            self.lines_skipped += 1
            return
        
        try:
            table_name = parts[0].strip()
            column_name = parts[1].strip()
            type_code = int(parts[2].strip())
            length = int(parts[3].strip())
            position = int(parts[4].strip())
            
            # Validate required fields
            if not table_name:
                self.warnings.append(f"Line {line_num}: Empty table name")
                self.lines_skipped += 1
                return
            
            if not column_name:
                self.warnings.append(f"Line {line_num}: Empty column name")
                self.lines_skipped += 1
                return
            
            # Map type code to Genero type
            genero_type = InformixTypeMapper.map_type(type_code, length)
            
            # Add to schema
            if table_name not in self.schema["tables"]:
                self.schema["tables"][table_name] = {
                    "name": table_name,
                    "columns": []
                }
            
            self.schema["tables"][table_name]["columns"].append({
                "name": column_name,
                "type": genero_type,
                "type_code": type_code,
                "length": length,
                "position": position
            })
            
            self.lines_processed += 1
            
        except (ValueError, IndexError) as e:
            self.errors.append(f"Line {line_num}: Parse error - {e}")
            self.lines_skipped += 1
    
    def get_table(self, table_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific table definition.
        
        Args:
            table_name: Name of table to retrieve
            
        Returns:
            Table definition or None if not found
        """
        for table in self.schema.get("tables", []):
            if table["name"] == table_name:
                return table
        return None
    
    def get_column(self, table_name: str, column_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific column definition.
        
        Args:
            table_name: Name of table
            column_name: Name of column
            
        Returns:
            Column definition or None if not found
        """
        table = self.get_table(table_name)
        if table:
            for column in table.get("columns", []):
                if column["name"] == column_name:
                    return column
        return None


def main():
    """Command-line interface for schema parser."""
    if len(sys.argv) < 2:
        print("Usage: python3 parse_schema.py <input.sch> [output.json]")
        print()
        print("Parses Informix IDS schema files (.sch) and generates JSON output.")
        print()
        print("Arguments:")
        print("  input.sch    - Input schema file (pipe-delimited format)")
        print("  output.json  - Output JSON file (default: schema.json)")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "schema.json"
    
    try:
        parser = SchemaParser()
        schema = parser.parse_file(input_file)
        
        # Write output
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(schema, f, indent=2)
        
        print(f"✓ Parsed {parser.lines_processed} lines from {input_file}")
        print(f"✓ Found {len(schema['tables'])} tables")
        print(f"✓ Output written to {output_file}")
        
        if parser.warnings:
            print(f"\n⚠ Warnings ({len(parser.warnings)}):")
            for warning in parser.warnings[:5]:
                print(f"  - {warning}")
            if len(parser.warnings) > 5:
                print(f"  ... and {len(parser.warnings) - 5} more")
        
        if parser.errors:
            print(f"\n✗ Errors ({len(parser.errors)}):")
            for error in parser.errors[:5]:
                print(f"  - {error}")
            if len(parser.errors) > 5:
                print(f"  ... and {len(parser.errors) - 5} more")
            sys.exit(1)
        
    except FileNotFoundError as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except IOError as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
