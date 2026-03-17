# Type Resolution Guide

## Overview

The type resolution system in genero-tools provides comprehensive LIKE reference resolution, multi-instance function disambiguation, and debugging capabilities for type resolution failures.

## Features

### 1. LIKE Reference Resolution

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

### 2. Multi-Instance Function Resolution

Properly handles functions with the same name in different files by storing and matching on both function name and file path.

**Use Cases:**
- Same function name in different modules
- Overloaded functions in different contexts
- Avoiding ambiguous function references

**Query by Name and Path:**
```bash
query.sh find-function-by-name-and-path process_data './src/module1.4gl'
```

**Find All Instances:**
```bash
query.sh find-all-function-instances process_data
```

### 3. Data Quality Improvements

#### Empty Parameter Filtering
- Eliminates invalid parameters with null or empty names
- Enforces NOT NULL constraint on parameter names
- Logs warnings for skipped parameters

#### Resolved Type Information
- Stores actual resolved types in database
- Tracks resolution status (resolved/unresolved)
- Records error reasons for failed resolutions

### 4. Unresolved Types Debugging

Query and debug type resolution failures with comprehensive filtering and pagination.

**Find All Unresolved Types:**
```bash
query.sh unresolved-types
```

**Filter by Error Type:**
```bash
# Missing table references
query.sh unresolved-types --filter missing_table

# Missing column references
query.sh unresolved-types --filter missing_column

# Invalid patterns
query.sh unresolved-types --filter invalid_pattern
```

**Pagination:**
```bash
# Get first 10 results
query.sh unresolved-types --limit 10

# Skip first 20, get next 10
query.sh unresolved-types --limit 10 --offset 20
```

## Database Schema

### Parameters Table
Extended with resolved type information:
- `actual_type` - First resolved type (for quick access)
- `is_like_reference` - Whether original type was a LIKE reference
- `resolved` - Resolution status (0=unresolved, 1=resolved)
- `resolution_error` - Error message if unresolved
- `table_name` - Resolved table name
- `columns` - Comma-separated column names
- `types` - JSON array of column types

### Returns Table
Same structure as parameters table for consistency.

### Functions Table
Extended with:
- `file_path` - Source file path for multi-instance disambiguation

## Python API

### Find Function by Name and Path
```python
from scripts.query_db import find_function_by_name_and_path

result = find_function_by_name_and_path(
    'workspace.db',
    'process_data',
    './src/module1.4gl'
)
```

### Find All Function Instances
```python
from scripts.query_db import find_all_function_instances

results = find_all_function_instances('workspace.db', 'process_data')
for instance in results:
    print(f"{instance['name']} in {instance['path']}")
```

### Find Unresolved Types
```python
from scripts.query_db import find_unresolved_types

# All unresolved types
results = find_unresolved_types('workspace.db')

# Filter by error type
results = find_unresolved_types(
    'workspace.db',
    filter_type='missing_table'
)

# With pagination
results = find_unresolved_types(
    'workspace.db',
    limit=10,
    offset=20
)
```

## Shell Commands

### Query Functions by Name and Path
```bash
# Find specific function instance
query.sh find-function-by-name-and-path process_data './src/module1.4gl'

# Find all instances of a function
query.sh find-all-function-instances process_data
```

### Debug Type Resolution
```bash
# Show all unresolved types
query.sh unresolved-types

# Show summary with breakdown by error type
query.sh unresolved-types

# Filter by specific error type
query.sh unresolved-types --filter missing_table

# Paginate results
query.sh unresolved-types --limit 10 --offset 5
```

## Workflow Examples

### Debugging Type Resolution Issues

1. **Identify unresolved types:**
   ```bash
   query.sh unresolved-types
   ```

2. **Filter by error type:**
   ```bash
   query.sh unresolved-types --filter missing_table
   ```

3. **Find specific function:**
   ```bash
   query.sh find-function-by-name-and-path function_name './path/to/file.4gl'
   ```

4. **Check resolved types:**
   ```bash
   query.sh find-function function_name
   ```

### Handling Multi-Instance Functions

1. **Find all instances:**
   ```bash
   query.sh find-all-function-instances my_function
   ```

2. **Get specific instance:**
   ```bash
   query.sh find-function-by-name-and-path my_function './src/module1.4gl'
   ```

3. **Compare resolved types:**
   - Check parameters and returns for each instance
   - Verify LIKE references are resolved correctly

## Performance

- Function lookup by name and path: **<1ms**
- Find all instances: **<1ms**
- Unresolved types query: **<100ms**
- Pagination: **<1ms per page**

## Data Consistency

The system maintains data consistency through:
- NOT NULL constraints on parameter names
- Automatic filtering of empty parameters
- Consistent resolved type storage
- Validation of LIKE reference patterns

### Validate Type Resolution Data

Check data consistency and identify issues:

```bash
# Validate all type resolution data
query.sh validate-types
```

**Output includes:**
- Validation status (VALID or INVALID)
- Summary statistics:
  - Total functions and file_path coverage
  - Total parameters and LIKE reference count
  - Total return types and LIKE reference count
  - Resolution status breakdown
- Issues found with severity levels (CRITICAL, WARNING)

**Example Output:**
```
✓ Validation Status: VALID

Summary Statistics:
  Total functions: 1234
  Functions with file_path: 1234
  Functions without file_path: 0

  Total parameters: 5678
  Empty parameters: 0
  Parameters with LIKE reference: 234
  Parameters resolved: 234
  Parameters unresolved: 0

  Total return types: 1234
  Return types with LIKE reference: 89
  Return types resolved: 89
  Return types unresolved: 0

Issues Found:
  No issues found. Database is consistent.
```

### Python API for Validation

```python
from scripts.query_db import validate_type_resolution

report = validate_type_resolution('workspace.db')

# Check status
if report['status'] == 'valid':
    print("Database is consistent")
else:
    print("Issues found:")
    for issue in report['issues']:
        print(f"  [{issue['severity']}] {issue['type']}: {issue['message']}")

# Access statistics
summary = report['summary']
print(f"Functions: {summary['total_functions']}")
print(f"Parameters: {summary['total_parameters']}")
print(f"Unresolved types: {summary['parameters_unresolved'] + summary['returns_unresolved']}")
```

## Troubleshooting

### Unresolved LIKE References

**Problem:** Many unresolved LIKE references in database

**Solutions:**
1. Check schema is properly loaded
2. Verify table names match schema exactly (case-sensitive)
3. Check for typos in LIKE patterns
4. Use `query.sh unresolved-types --filter missing_table` to identify missing tables

### Multi-Instance Function Confusion

**Problem:** Getting wrong function instance

**Solutions:**
1. Use `find-function-by-name-and-path` with explicit file path
2. Use `find-all-function-instances` to see all versions
3. Check file paths in results match expected locations

### Data Consistency Issues

**Problem:** Validation reports issues

**Solutions:**
1. Run `query.sh validate-types` to identify specific issues
2. Check for empty parameters: `query.sh unresolved-types --filter empty_parameters`
3. Verify all functions have file_path: Check functions table
4. Regenerate databases if corruption suspected: `query.sh create-dbs`

### Empty Parameters

**Problem:** Functions showing with no parameters

**Solutions:**
1. Check logs for "Skipping empty parameter" warnings
2. Verify source code has valid parameter names
3. Regenerate database with latest parser

## Integration Examples

### Vim Plugin Integration
```vim
" Find function by name and path
function! FindFunctionInstance(name, path)
  let cmd = 'query.sh find-function-by-name-and-path ' . a:name . ' ' . a:path
  let result = system(cmd)
  " Parse and display result
endfunction
```

### IDE Integration
```python
# Get resolved types for hover information
def get_resolved_types(function_name, file_path):
    result = find_function_by_name_and_path(
        'workspace.db',
        function_name,
        file_path
    )
    return {
        'parameters': result['parameters'],
        'returns': result['returns']
    }
```

## See Also

- [SCHEMA_RESOLUTION_IMPLEMENTATION.md](SCHEMA_RESOLUTION_IMPLEMENTATION.md) - Implementation details
- [QUERYING.md](QUERYING.md) - General query documentation
- [docs/api/shell-commands.json](docs/api/shell-commands.json) - Shell command reference
- [docs/api/python-query-db.json](docs/api/python-query-db.json) - Python API reference
