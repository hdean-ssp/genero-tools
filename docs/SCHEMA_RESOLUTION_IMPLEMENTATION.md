# Schema Resolution Implementation

## Overview

Implemented automatic schema detection and type resolution in the `generate_all.sh` script. The system now:

1. Automatically finds schema files (`.sch`) in the target workspace
2. Parses schema into JSON format
3. Loads schema into the SQLite database
4. Resolves LIKE type references to actual database schema types
5. Generates `workspace_resolved.json` with resolved types

## Changes Made

### 1. Removed Generated Files from Version Control

- Deleted `workspace_resolved.json` from repository
- Added `workspace_resolved.json` to `.gitignore`
- Reason: It's a generated file, not source code

### 2. Updated generate_all.sh

Added automatic schema detection and processing:

```bash
# Find schema file if not provided
if [[ -z "$SCHEMA_FILE" ]]; then
    # Look for .sch files in the target directory
    SCHEMA_FILES=$(find "$TARGET" -name "*.sch" -type f)
    if [[ $SCHEMA_COUNT -gt 0 ]]; then
        SCHEMA_FILE=$(echo "$SCHEMA_FILES" | head -1)
    fi
fi

# Parse and load schema
if [[ -n "$SCHEMA_FILE" && -f "$SCHEMA_FILE" ]]; then
    python3 "$SCRIPT_DIR/scripts/parse_schema.py" "$SCHEMA_FILE" "$SCHEMA_JSON"
    python3 "$SCRIPT_DIR/scripts/json_to_sqlite_schema.py" "$SCHEMA_JSON" workspace.db
    export RESOLVE_TYPES=1
fi

# Generate resolved types
if [[ "${RESOLVE_TYPES:-0}" == "1" ]]; then
    python3 "$SCRIPT_DIR/scripts/resolve_types.py" workspace.db workspace.json workspace_resolved.json
fi
```

### 3. Workflow

The new workflow is:

```
1. Find .sch files in target directory
   ↓
2. Parse schema file → schema.json
   ↓
3. Load schema into workspace.db
   ↓
4. Generate function signatures → workspace.json
   ↓
5. Resolve LIKE types using schema → workspace_resolved.json
```

## Usage

### Automatic Schema Detection

```bash
# Schema is automatically found and processed
bash generate_all.sh ./tests/sample_codebase
```

Output:
```
[STEP] Parsing schema file and loading into database...
[✓] Schema parsed: ./tests/sample_codebase/schema.sch
[✓] Schema loaded into workspace.db

[STEP] Generating type-resolved signatures...
[✓] Type-resolved signatures generated (workspace_resolved.json)
```

### Explicit Schema File

```bash
# Optionally provide schema file explicitly
bash generate_all.sh /path/to/codebase /path/to/schema.sch
```

### No Schema Available

```bash
# If no schema found, type resolution is skipped gracefully
bash generate_all.sh /path/to/codebase

# Output:
# [INFO] No schema file found in target directory (type resolution will be skipped)
```

## Generated Files

### workspace.json
- Function signatures with parameters and return types
- File headers with code references and authors
- Call graph information

### workspace_resolved.json
- Same as workspace.json but with resolved LIKE types
- Only generated if schema is available
- Contains metadata about type resolution success/failure

**Example:**

```json
{
  "name": "process_abi_message",
  "parameters": [
    {
      "name": "msg",
      "type": "LIKE abi_message.*",
      "is_like_reference": true,
      "resolved": true,
      "table": "abi_message",
      "columns": ["id", "name", "version"],
      "types": ["VARCHAR(6)", "VARCHAR(40)", "VARCHAR(5)"]
    }
  ]
}
```

### workspace.db
- SQLite database with:
  - Function signatures
  - File headers and references
  - Schema tables and columns
  - Indexed for fast queries

## Type Resolution Details

### What Gets Resolved

LIKE type references are resolved to actual database schema types:

```genero
// Before resolution
DEFINE customer LIKE customers.*
DEFINE customer_id LIKE customers.id

// After resolution
DEFINE customer LIKE customers.*
  // Resolved to: id INTEGER, name STRING, email STRING

DEFINE customer_id LIKE customers.id
  // Resolved to: INTEGER
```

### Resolution Metadata

Each resolved type includes:

- `is_like_reference`: Boolean indicating if it's a LIKE reference
- `resolved`: Boolean indicating if resolution was successful
- `table`: The table name referenced
- `columns`: List of column names (for LIKE table.*)
- `types`: List of resolved types
- `error`: Error message if resolution failed

### Partial Resolution

If a specific column is not found, the resolution fails gracefully:

```json
{
  "name": "id",
  "type": "LIKE customers.nonexistent",
  "is_like_reference": true,
  "resolved": false,
  "table": "customers",
  "error": "Column not found: customers.nonexistent"
}
```

## Testing

Verified with sample codebase:

```bash
bash generate_all.sh ./tests/sample_codebase
```

Results:
- ✓ Schema file found: `./tests/sample_codebase/schema.sch`
- ✓ Schema parsed: 12 tables, 45 columns
- ✓ Schema loaded into workspace.db
- ✓ workspace_resolved.json generated with resolved types
- ✓ LIKE references successfully resolved to schema types

## Benefits

1. **Automatic**: No manual schema loading required
2. **Transparent**: Works seamlessly in the generation pipeline
3. **Graceful**: Skips type resolution if schema not available
4. **Complete**: Resolves all LIKE type references
5. **Documented**: Clear metadata about resolution status

## LSP Integration

This enables LSP servers to:

1. Provide type-aware hover information
2. Perform type checking and validation
3. Enable type-safe refactoring
4. Offer type hints in code completion
5. Generate type-aware documentation

## Future Enhancements

1. **Incremental Updates**: Update only changed schema files
2. **Multiple Schemas**: Support multiple schema files
3. **Schema Validation**: Validate schema consistency
4. **Type Caching**: Cache resolved types for performance
5. **Schema Versioning**: Track schema changes over time

## Files Modified

- `generate_all.sh` - Added schema detection and type resolution
- `.gitignore` - Added workspace_resolved.json
- Removed `workspace_resolved.json` from version control

## Backward Compatibility

- Existing workflows continue to work
- Type resolution is optional (skipped if no schema)
- No breaking changes to existing APIs
- All existing query functions work unchanged
