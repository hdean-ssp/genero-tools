# Type Resolution Guide - Phase 1c

## Overview

Phase 1c implements enhanced type resolution for LIKE references in Genero/4GL functions. This enables the system to resolve `LIKE table.*` and `LIKE table.column` references to actual database schema definitions.

## What is Type Resolution?

Type resolution maps abstract type references to concrete database schema information:

**Before (Phase 0):**
```json
{
  "name": "process_account",
  "parameters": [
    {"name": "acc", "type": "LIKE account.*"}
  ]
}
```

**After (Phase 1c):**
```json
{
  "name": "process_account",
  "parameters": [
    {
      "name": "acc",
      "type": "LIKE account.*",
      "is_like_reference": true,
      "resolved": true,
      "table": "account",
      "columns": ["id", "name", "balance", "created_date"],
      "types": ["INTEGER", "VARCHAR(100)", "DECIMAL(10,2)", "DATE"]
    }
  ]
}
```

## Architecture

### Type Resolution Pipeline

```
workspace.json (with LIKE references)
    ↓
resolve_types.py (TypeResolver class)
    ↓
workspace.db (schema_tables, schema_columns)
    ↓
workspace_resolved.json (with resolved types)
```

### Key Components

1. **TypeResolver** (`scripts/resolve_types.py`)
   - Loads schema from workspace.db
   - Parses LIKE references
   - Resolves to actual table/column definitions
   - Handles edge cases (missing tables, columns)

2. **Integration** (`src/generate_signatures.sh`)
   - Calls resolve_types.py after generating workspace.json
   - Controlled by `RESOLVE_TYPES` environment variable
   - Requires workspace.db to exist

## Usage

### Basic Usage

```bash
# Generate signatures with type resolution
RESOLVE_TYPES=1 bash src/generate_signatures.sh /path/to/codebase
```

This generates:
- `workspace.json` - Function signatures with LIKE references
- `workspace_resolved.json` - Same signatures with resolved types

### Direct Usage

```bash
python3 scripts/resolve_types.py workspace.db workspace.json workspace_resolved.json
```

### Programmatic Usage

```python
from scripts.resolve_types import TypeResolver

# Create resolver
resolver = TypeResolver('workspace.db')

# Resolve a single LIKE reference
result = resolver.resolve_like_reference('LIKE account.*')
# Returns:
# {
#   'table': 'account',
#   'columns': ['id', 'name', 'balance'],
#   'types': ['INTEGER', 'VARCHAR(100)', 'DECIMAL(10,2)'],
#   'resolved': True
# }

# Resolve a parameter type
result = resolver.resolve_parameter_type('LIKE account.id')
# Returns:
# {
#   'table': 'account',
#   'columns': ['id'],
#   'types': ['INTEGER'],
#   'is_like_reference': True,
#   'resolved': True
# }

# Process entire workspace.json
workspace = resolver.process_workspace_json('workspace.json')

resolver.close()
```

## LIKE Reference Patterns

### Pattern 1: All Columns

```4gl
FUNCTION process_account(acc LIKE account.*)
```

Resolves to all columns in the `account` table:
```json
{
  "table": "account",
  "columns": ["id", "name", "balance", "created_date"],
  "types": ["INTEGER", "VARCHAR(100)", "DECIMAL(10,2)", "DATE"]
}
```

### Pattern 2: Specific Column

```4gl
FUNCTION get_account_id(id LIKE account.id)
```

Resolves to the specific column:
```json
{
  "table": "account",
  "columns": ["id"],
  "types": ["INTEGER"]
}
```

## Resolution Status

Each resolved parameter includes a `resolved` field indicating success:

### Resolved Successfully

```json
{
  "name": "acc",
  "type": "LIKE account.*",
  "is_like_reference": true,
  "resolved": true,
  "table": "account",
  "columns": ["id", "name", "balance"],
  "types": ["INTEGER", "VARCHAR(100)", "DECIMAL(10,2)"]
}
```

### Unresolved - Missing Table

```json
{
  "name": "rec",
  "type": "LIKE nonexistent.*",
  "is_like_reference": true,
  "resolved": false,
  "error": "Table not found: nonexistent"
}
```

### Unresolved - Missing Column

```json
{
  "name": "val",
  "type": "LIKE account.nonexistent",
  "is_like_reference": true,
  "resolved": false,
  "error": "Column not found: account.nonexistent"
}
```

### Non-LIKE Types

Non-LIKE types are passed through unchanged:

```json
{
  "name": "id",
  "type": "INTEGER",
  "is_like_reference": false,
  "resolved": true
}
```

## Database Schema Requirements

Type resolution requires the schema to be loaded into `workspace.db`:

```sql
-- Required tables
schema_tables (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    source_file TEXT,
    line_number INTEGER
)

schema_columns (
    id INTEGER PRIMARY KEY,
    table_id INTEGER NOT NULL,
    column_name TEXT NOT NULL,
    column_type TEXT NOT NULL,
    FOREIGN KEY (table_id) REFERENCES schema_tables(id)
)
```

See [SCHEMA_PARSING_GUIDE.md](SCHEMA_PARSING_GUIDE.md) for how to populate these tables.

## Performance

Type resolution is optimized for performance:

- **Schema Caching**: Schema is loaded into memory once
- **Fast Lookups**: O(1) table lookups, O(n) column lookups
- **Batch Processing**: Processes entire workspace.json in single pass
- **Typical Performance**: ~1000 functions resolved in <1 second

## Testing

### Unit Tests

```bash
python3 tests/test_type_resolution.py -v
```

Tests cover:
- LIKE reference parsing
- Schema lookups
- Edge cases (missing tables, columns)
- workspace.json processing
- Whitespace handling
- Case insensitivity

### Integration Tests

```bash
python3 tests/test_phase1c_integration.py -v
```

Tests cover:
- End-to-end type resolution workflow
- Unresolved reference handling
- Performance with large workspaces

## Troubleshooting

### "Table not found" Errors

**Problem**: LIKE references resolve to "Table not found"

**Solution**: Ensure schema is loaded into workspace.db:
```bash
python3 scripts/json_to_sqlite_schema.py schema.json workspace.db
```

### "Column not found" Errors

**Problem**: LIKE references resolve to "Column not found"

**Solution**: Verify schema file contains the column definition

### Type Resolution Not Running

**Problem**: workspace_resolved.json not created

**Solution**: Set RESOLVE_TYPES environment variable:
```bash
RESOLVE_TYPES=1 bash src/generate_signatures.sh /path/to/codebase
```

## Next Steps

Phase 1d (Query Layer) will build on type resolution to enable:
- Query functions by the types they use
- Find all functions using a specific table
- Detect type mismatches
- Generate type validation reports

## Related Documentation

- [SCHEMA_PARSING_GUIDE.md](SCHEMA_PARSING_GUIDE.md) - How to parse database schemas
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture and data flow
- [PHASE_1_SPECIFICATION.md](../.kiro/specs/PHASE_1_SPECIFICATION.md) - Phase 1 specification
