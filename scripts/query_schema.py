#!/usr/bin/env python3
"""
Query functions for database schema metadata.

Provides functions to look up table and column definitions from the
schema database, designed for IDE hover integration (e.g., resolving
LIKE table.column references in Genero/4GL code).

Usage:
    python3 query_schema.py <command> <db_file> [args...]

Commands:
    get-table <table_name>              Get full table definition with all columns
    get-column <table_name> <column>    Get a single column definition
    search-tables <pattern>             Search tables by name pattern
    search-columns <pattern>            Search columns by name across all tables
    resolve-like <like_ref>             Resolve a LIKE reference (table.column or table.*)
"""

import sqlite3
import json
import sys
from typing import List, Dict, Any, Optional


def get_table(db_file: str, table_name: str) -> Optional[Dict[str, Any]]:
    """
    Get full table definition with all columns.

    Args:
        db_file: Path to SQLite database
        table_name: Table name (case-insensitive)

    Returns:
        Table definition dict or None if not found
    """
    try:
        conn = sqlite3.connect(db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, name FROM schema_tables WHERE LOWER(name) = LOWER(?)",
            (table_name,)
        )
        row = cursor.fetchone()

        if not row:
            conn.close()
            return None

        table_id = row["id"]

        cursor.execute(
            """SELECT column_name, column_type, type_code, length, position
               FROM schema_columns
               WHERE table_id = ?
               ORDER BY position""",
            (table_id,)
        )

        columns = []
        for col in cursor.fetchall():
            columns.append({
                "name": col["column_name"],
                "type": col["column_type"],
                "type_code": col["type_code"],
                "length": col["length"],
                "position": col["position"]
            })

        conn.close()

        return {
            "table": row["name"],
            "column_count": len(columns),
            "columns": columns
        }
    except Exception as e:
        print(f"Error querying database: {e}", file=sys.stderr)
        return None


def get_column(db_file: str, table_name: str, column_name: str) -> Optional[Dict[str, Any]]:
    """
    Get a single column definition.

    Args:
        db_file: Path to SQLite database
        table_name: Table name (case-insensitive)
        column_name: Column name (case-insensitive)

    Returns:
        Column definition dict or None if not found
    """
    try:
        conn = sqlite3.connect(db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            """SELECT st.name AS table_name,
                      sc.column_name, sc.column_type, sc.type_code,
                      sc.length, sc.position
               FROM schema_columns sc
               JOIN schema_tables st ON sc.table_id = st.id
               WHERE LOWER(st.name) = LOWER(?)
                 AND LOWER(sc.column_name) = LOWER(?)""",
            (table_name, column_name)
        )

        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return {
            "table": row["table_name"],
            "column": row["column_name"],
            "type": row["column_type"],
            "type_code": row["type_code"],
            "length": row["length"],
            "position": row["position"]
        }
    except Exception as e:
        print(f"Error querying database: {e}", file=sys.stderr)
        return None


def search_tables(db_file: str, pattern: str) -> List[Dict[str, Any]]:
    """
    Search tables by name pattern.

    Supports wildcards: * or % for any characters, ? or _ for single character.

    Args:
        db_file: Path to SQLite database
        pattern: Search pattern (case-insensitive)

    Returns:
        List of matching tables with column counts
    """
    try:
        conn = sqlite3.connect(db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Convert glob-style wildcards to SQL LIKE
        like_pattern = pattern.replace("*", "%").replace("?", "_")
        if "%" not in like_pattern and "_" not in like_pattern:
            like_pattern = f"%{like_pattern}%"

        cursor.execute(
            """SELECT st.id, st.name,
                      COUNT(sc.id) AS column_count
               FROM schema_tables st
               LEFT JOIN schema_columns sc ON st.id = sc.table_id
               WHERE LOWER(st.name) LIKE LOWER(?)
               GROUP BY st.id, st.name
               ORDER BY st.name
               LIMIT 100""",
            (like_pattern,)
        )

        results = []
        for row in cursor.fetchall():
            results.append({
                "table": row["name"],
                "column_count": row["column_count"]
            })

        conn.close()
        return results
    except Exception as e:
        print(f"Error querying database: {e}", file=sys.stderr)
        return []


def search_columns(db_file: str, pattern: str) -> List[Dict[str, Any]]:
    """
    Search columns by name across all tables.

    Args:
        db_file: Path to SQLite database
        pattern: Search pattern (case-insensitive)

    Returns:
        List of matching columns with their table names
    """
    try:
        conn = sqlite3.connect(db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        like_pattern = pattern.replace("*", "%").replace("?", "_")
        if "%" not in like_pattern and "_" not in like_pattern:
            like_pattern = f"%{like_pattern}%"

        cursor.execute(
            """SELECT st.name AS table_name,
                      sc.column_name, sc.column_type, sc.type_code,
                      sc.length, sc.position
               FROM schema_columns sc
               JOIN schema_tables st ON sc.table_id = st.id
               WHERE LOWER(sc.column_name) LIKE LOWER(?)
               ORDER BY st.name, sc.position
               LIMIT 100""",
            (like_pattern,)
        )

        results = []
        for row in cursor.fetchall():
            results.append({
                "table": row["table_name"],
                "column": row["column_name"],
                "type": row["column_type"],
                "type_code": row["type_code"],
                "length": row["length"],
                "position": row["position"]
            })

        conn.close()
        return results
    except Exception as e:
        print(f"Error querying database: {e}", file=sys.stderr)
        return []


def resolve_like(db_file: str, like_ref: str) -> Optional[Dict[str, Any]]:
    """
    Resolve a LIKE reference to its schema definition.

    Handles:
        - table.column  → single column definition
        - table.*       → full table definition (all columns)

    This is the primary entry point for IDE hover on LIKE references.

    Args:
        db_file: Path to SQLite database
        like_ref: LIKE reference string (e.g., "account.acc_code" or "account.*")

    Returns:
        Resolved definition dict or None if not found
    """
    like_ref = like_ref.strip()

    # Strip leading "LIKE " if present
    if like_ref.upper().startswith("LIKE "):
        like_ref = like_ref[5:].strip()

    if "." not in like_ref:
        # Bare table name — return full table
        result = get_table(db_file, like_ref)
        if result:
            result["reference"] = like_ref
            result["kind"] = "table"
        return result

    parts = like_ref.split(".", 1)
    table_name = parts[0].strip()
    column_name = parts[1].strip()

    if column_name == "*":
        # Wildcard — return full table definition
        result = get_table(db_file, table_name)
        if result:
            result["reference"] = like_ref
            result["kind"] = "record"
        return result
    else:
        # Specific column
        result = get_column(db_file, table_name, column_name)
        if result:
            result["reference"] = like_ref
            result["kind"] = "column"
        return result


def main():
    """Command-line interface for schema queries."""
    if len(sys.argv) < 3:
        print("Usage: query_schema.py <command> <db_file> [args...]", file=sys.stderr)
        print("", file=sys.stderr)
        print("Commands:", file=sys.stderr)
        print("  get-table <table_name>              Full table definition", file=sys.stderr)
        print("  get-column <table_name> <column>     Single column definition", file=sys.stderr)
        print("  search-tables <pattern>              Search tables by name", file=sys.stderr)
        print("  search-columns <pattern>             Search columns by name", file=sys.stderr)
        print("  resolve-like <like_ref>              Resolve LIKE reference", file=sys.stderr)
        sys.exit(1)

    command = sys.argv[1]
    db_file = sys.argv[2]

    result = None

    if command == "get-table" and len(sys.argv) > 3:
        result = get_table(db_file, sys.argv[3])
    elif command == "get-column" and len(sys.argv) > 4:
        result = get_column(db_file, sys.argv[3], sys.argv[4])
    elif command == "search-tables" and len(sys.argv) > 3:
        result = search_tables(db_file, sys.argv[3])
    elif command == "search-columns" and len(sys.argv) > 3:
        result = search_columns(db_file, sys.argv[3])
    elif command == "resolve-like" and len(sys.argv) > 3:
        # Join remaining args to handle "LIKE table.col" as a single reference
        like_ref = " ".join(sys.argv[3:])
        result = resolve_like(db_file, like_ref)
    else:
        print(f"Unknown command or missing arguments: {command}", file=sys.stderr)
        sys.exit(1)

    if result is None:
        print(json.dumps({"error": "not_found", "message": "No matching schema definition found"}))
    else:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
