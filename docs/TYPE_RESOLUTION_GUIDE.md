# Type Resolution Guide

## Overview

The type resolution system in genero-tools provides comprehensive LIKE reference resolution, multi-instance function disambiguation, and debugging capabilities for type resolution failures.

**Version:** 2.1.0  
**Status:** Production Ready

## Quick Start

### Automatic Schema Detection

```bash
# Schema files (.sch) are automatically detected and processed
bash generate_all.sh /path/to/codebase

# Query resolved types
bash query.sh find-function-resolved process_contract
```

### Query Resolved Types

```bash
# Get function with resolved types
bash query.sh find-function-resolved my_function

# Find specific function instance by name and file
bash query.sh find-function-by-name-and-path my_function './src/module.4gl'

# Find all instances of a function
bash query.sh find-all-function-instances my_function

# Debug type resolution issues
bash query.sh unresolved-types
bash query.sh unresolved-types --filter missing_table
bash query.sh validate-types
```

## Features

### 1. Automatic Schema Detection

Schema files (`.sch`) are automatically found and processed during the generation pipeline.

**Behavior:**
- Automatically finds `.sch` files in target directory
- Parses schema and loads into database
- Resolves LIKE types automatically
- Gracefully skips type resolution if no schema found

**Example:**
```bash
$ bash generate_all.sh ./tests/sample_codebase
[STEP] Parsing schema file and loading into database...
[✓] Schema parsed: ./tests/sample_codebase/schema.sch
[✓] Schema loaded into workspace.db

[STEP] Generating type-resolved signatures...
[✓] Type-resolved signatures generated
```

### 2. LIKE Reference Resolution

Automatically resolves LIKE references in both parameters and return types to actual database schema types.

**Supported Patterns:**
- `LIKE table.*` - Resolves to all columns in the table
- `LIKE table.column` - Resolves to specific column

**Example:**
```4gl
FUNCTION process_account(acc LIKE account.*)
  RETURNS result LIKE account.id, status INTEGER
```

Resolves to:
- Parameter `acc`: columns [id, name, balance] with types [INTEGER, VARCHAR(100), DECIMAL(10,2)]
- Return `result`: column [id] with type [INTEGER]

**Query Result:**
```bash
$ bash query.sh find-function-resolved process_account

{
  "name": "process_account",
  "file": "./src/processing.4gl",
  "line": 45,
  "parameters": [
    {
      "name": "acc",
      "type": "LIKE account.*",
      "is_like_reference": true,
      "resolved": true,
      "table_name": "account",
      "resolved_columns": ["id", "name", "balance"],
      "resolved_types": ["INTEGER", "VARCHAR(100)", "DECIMAL(10,2)"]
    }
  ]
}
```

### 3. Multi-Instance Function Resolution

Properly handles functions with the same name in different files by storing and matching on both function name and file path.

**Use Cases:**
- Same function name in different modules
- Overloaded functions in different contexts
- Avoiding ambiguous function references

**Query by Name and Path:**
```bash
bash query.sh find-function-by-name-and-path process_data './src/module1.4gl'
```

**Find All Instances:**
```bash
bash query.sh find-all-function-instances process_data

# Output:
[
  {
    "name": "process_data",
    "file": "./src/module1.4gl",
    "line": 42,
    "parameters": [...]
  },
  {
    "name": "process_data",
    "file": "./src/module2.4gl",
    "line": 156,
    "parameters": [...]
  }
]
```

### 4. Empty Parameter Filtering

Automatically removes invalid parameters with empty names during database loading.

**What Gets Filtered:**
- Parameters with NULL names
- Parameters with empty string names
- Parameters with whitespace-only names

**Benefits:**
- Cleaner database
- More accurate query results
- Improved data quality
- Prevents NULL reference errors

### 5. Unresolved Types Debugging

Query and debug type resolution failures with comprehensive filtering and pagination.

**Find All Unresolved Types:**
```bash
bash query.sh unresolved-types
```

**Filter by Error Type:**
```bash
# Missing table references
bash query.sh unresolved-types --filter missing_table

# Missing column references
bash query.sh unresolved-types --filter missing_column

# Invalid patterns
bash query.sh unresolved-types --filter invalid_pattern
```

**Pagination:**
```bash
# Get first 10 results
bash query.sh unresolved-types --limit 10

# Skip first 20, get next 10
bash query.sh unresolved-types --limit 10 --offset 20
```

**Example Output:**
```json
{
  "unresolved_count": 3,
  "results": [
    {
      "function": "process_account",
      "file": "./src/main.4gl",
      "parameter": "acc",
      "type": "LIKE nonexistent_table.*",
      "error_type": "missing_table",
      "error_reason": "Table 'nonexistent_table' not found in schema"
    }
  ]
}
```

### 6. Data Consistency Validation

Comprehensive validation of type resolution data integrity.

**Validate All Type Resolution Data:**
```bash
bash query.sh validate-types
```

**Validation Checks:**
1. No empty parameter names
2. All functions have file_path
3. All LIKE references are resolved or have error reason
4. Schema tables exist for resolved references
5. Resolved columns exist in schema tables

**Example Output:**
```json
{
  "validation_status": "PASSED",
  "checks": {
    "empty_parameters": {
      "status": "PASSED",
      "count": 0
    },
    "missing_file_path": {
      "status": "PASSED",
      "count": 0
    },
    "unresolved_like_references": {
      "status": "PASSED",
      "count": 0
    },
    "schema_consistency": {
      "status": "PASSED",
      "invalid_references": 0
    }
  },
  "total_functions": 156,
  "total_parameters": 342,
  "total_returns": 89
}
```

## Database Schema

### Parameters Table (Extended)

```sql
ALTER TABLE parameters ADD COLUMN actual_type TEXT;
ALTER TABLE parameters ADD COLUMN is_like_reference INTEGER DEFAULT 0;
ALTER TABLE parameters ADD COLUMN resolved INTEGER DEFAULT 0;
ALTER TABLE parameters ADD COLUMN resolution_error TEXT;
ALTER TABLE parameters ADD COLUMN table_name TEXT;
ALTER TABLE parameters ADD COLUMN columns TEXT;
ALTER TABLE parameters ADD COLUMN types TEXT;

CREATE INDEX idx_parameters_resolved ON parameters(resolved);
CREATE INDEX idx_parameters_table ON parameters(table_name);
```

### Returns Table (Extended)

```sql
ALTER TABLE returns ADD COLUMN actual_type TEXT;
ALTER TABLE returns ADD COLUMN is_like_reference INTEGER DEFAULT 0;
ALTER TABLE returns ADD COLUMN resolved INTEGER DEFAULT 0;
ALTER TABLE returns ADD COLUMN resolution_error TEXT;
ALTER TABLE returns ADD COLUMN table_name TEXT;
ALTER TABLE returns ADD COLUMN columns TEXT;
ALTER TABLE returns ADD COLUMN types TEXT;

CREATE INDEX idx_returns_resolved ON returns(resolved);
CREATE INDEX idx_returns_table ON returns(table_name);
```

## Performance

| Operation | Before | After | Improvement |
|-----------|--------|-------|-------------|
| Type lookup | 2-5s (JSON) | <1ms (DB) | 2000-5000x |
| Resolved type query | N/A | <1ms | New |
| Multi-instance lookup | N/A | <1ms | New |
| Database size | 70KB + 15-20MB JSON | 70KB | 99% reduction |

## Migration Guide

### For Existing Users

**No action required.** The system is backward compatible:

1. Existing `workspace.json` files continue to work
2. Existing queries continue to work
3. New features are opt-in
4. Type resolution is automatic if schema is available

**To Use New Features:**

```bash
# Regenerate with automatic schema detection
bash generate_all.sh /path/to/codebase

# Use new query commands
bash query.sh find-function-resolved my_function
bash query.sh find-function-by-name-and-path my_function './src/module.4gl'
bash query.sh unresolved-types
bash query.sh validate-types
```

### For Plugin Developers

**Update Integration:**

```bash
# Old approach (still works)
bash query.sh find-function my_function

# New approach (recommended for type-aware features)
bash query.sh find-function-resolved my_function
```

**Hover Information Enhancement:**

```vim
" Old: Show basic signature
let signature = system('query.sh find-function ' . function_name)

" New: Show resolved types
let resolved = system('query.sh find-function-resolved ' . function_name)
" Now includes: resolved_columns, resolved_types, table_name
```

## Known Limitations

1. **Schema Format:** Currently supports Informix IDS `.sch` format only
   - SQL DDL support planned for future release
   - Custom format support available via plugins

2. **Type Resolution Scope:** Resolves LIKE references only
   - Other type references (RECORD, ARRAY) not resolved
   - Planned for future enhancement

3. **Multi-File Schema:** Single schema file per workspace
   - Multiple schema files planned for future release

## Testing

All features have been tested with:
- ✅ 16+ unit tests for type resolution
- ✅ 8+ integration tests for end-to-end workflows
- ✅ Property-based testing for correctness validation
- ✅ Real-world codebase testing (6M+ LOC)
- ✅ Performance benchmarking

**Test Coverage:** >90% of type resolution code

## Troubleshooting

### Schema Not Found

**Problem:** Type resolution is skipped
```
[INFO] No schema file found in target directory (type resolution will be skipped)
```

**Solution:** Ensure `.sch` file exists in target directory or provide explicitly:
```bash
bash generate_all.sh /path/to/codebase /path/to/schema.sch
```

### Unresolved Types

**Problem:** Some LIKE references not resolved
```bash
bash query.sh unresolved-types
```

**Solution:** Check if referenced tables exist in schema:
```bash
bash query.sh unresolved-types --filter missing_table
```

### Data Validation Failures

**Problem:** Data consistency check fails
```bash
bash query.sh validate-types
```

**Solution:** Regenerate databases:
```bash
bash query.sh create-dbs
bash generate_all.sh /path/to/codebase
```

## Next Steps

- See [docs/QUERYING.md](QUERYING.md) for complete query reference
- See [docs/FEATURES.md](FEATURES.md) for all features
- See [docs/ARCHITECTURE.md](ARCHITECTURE.md) for system design

