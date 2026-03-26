# Quick Start: Type Resolution

Get started with type resolution features in 5 minutes.

## Setup (1 minute)

```bash
# Generate metadata
bash generate_signatures.sh /path/to/codebase

# Create databases
bash query.sh create-dbs

# Verify setup
bash query.sh validate-types
```

## Common Tasks

### Find a Function by Name and File

When you have multiple functions with the same name in different files:

```bash
# Find specific instance
bash query.sh find-function-by-name-and-path my_function './src/module.4gl'

# Find all instances
bash query.sh find-all-function-instances my_function
```

### Debug Type Resolution Issues

When LIKE references aren't resolving:

```bash
# See all unresolved types
bash query.sh unresolved-types

# Filter by error type
bash query.sh unresolved-types --filter missing_table

# Get first 10 results
bash query.sh unresolved-types --limit 10
```

### Validate Data Quality

Check if your database is consistent:

```bash
bash query.sh validate-types
```

**Output shows:**
- ✓ Validation status (VALID or INVALID)
- Summary statistics (functions, parameters, return types)
- Any issues found with severity levels

## Python Examples

### Find Function Instance

```python
from scripts.query_db import find_function_by_name_and_path

result = find_function_by_name_and_path(
    'workspace.db',
    'process_data',
    './src/module1.4gl'
)

if result:
    print(f"Found: {result['name']} at line {result['line_start']}")
    print(f"Parameters: {len(result['parameters'])}")
    print(f"Returns: {len(result['returns'])}")
```

### Find All Instances

```python
from scripts.query_db import find_all_function_instances

instances = find_all_function_instances('workspace.db', 'process_data')

for instance in instances:
    print(f"{instance['name']} in {instance['file_path']}")
```

### Find Unresolved Types

```python
from scripts.query_db import find_unresolved_types

# All unresolved
unresolved = find_unresolved_types('workspace.db')
print(f"Found {len(unresolved)} unresolved types")

# Filter by error type
missing_tables = find_unresolved_types(
    'workspace.db',
    filter_type='missing_table'
)

# With pagination
page = find_unresolved_types(
    'workspace.db',
    limit=10,
    offset=0
)
```

### Validate Data

```python
from scripts.query_db import validate_type_resolution

report = validate_type_resolution('workspace.db')

print(f"Status: {report['status']}")
print(f"Functions: {report['summary']['total_functions']}")
print(f"Unresolved types: {report['summary']['parameters_unresolved'] + report['summary']['returns_unresolved']}")

if report['issues']:
    print("\nIssues found:")
    for issue in report['issues']:
        print(f"  - {issue['message']}")
```

## Understanding LIKE References

### What are LIKE References?

LIKE references are type specifications that reference database schema:

```4gl
FUNCTION process_account(acc LIKE account.*)
  RETURNS result LIKE account.id, status INTEGER
```

### Resolution Process

1. **Parsing**: Extract LIKE pattern from function signature
2. **Lookup**: Find table and columns in schema
3. **Resolution**: Store actual column types
4. **Storage**: Save resolved types in database

### Supported Patterns

- `LIKE table.*` - All columns from table
- `LIKE table.column` - Specific column

### Troubleshooting

**Problem: LIKE references not resolving**

```bash
# Check what's unresolved
bash query.sh unresolved-types --filter missing_table

# Verify schema is loaded
bash query.sh validate-types
```

## Multi-Instance Functions

### What are Multi-Instance Functions?

Same function name in different files:

```
./src/module1.4gl: FUNCTION process_data(...)
./src/module2.4gl: FUNCTION process_data(...)
```

### How to Handle

```bash
# Find all versions
bash query.sh find-all-function-instances process_data

# Get specific version
bash query.sh find-function-by-name-and-path process_data './src/module1.4gl'
```

## Performance Tips

1. **Use specific queries**: `find-function-by-name-and-path` is faster than `find-all-function-instances`
2. **Paginate large results**: Use `--limit` and `--offset` for unresolved-types
3. **Cache validation results**: Run `validate-types` once, not repeatedly
4. **Use Python API**: Faster than shell commands for batch operations

## Next Steps

- Read [TYPE_RESOLUTION_GUIDE.md](TYPE_RESOLUTION_GUIDE.md) for detailed documentation
- Check [QUERYING.md](QUERYING.md) for all available queries
- See [TYPE_RESOLUTION_RELEASE_NOTES.md](TYPE_RESOLUTION_RELEASE_NOTES.md) for what's new

## Common Issues

### "Database not found"
```bash
bash query.sh create-dbs
```

### "Function not found"
- Check function name spelling
- Use `find-all-function-instances` to see all versions
- Verify file path is correct

### "Many unresolved types"
- Check schema is loaded
- Verify table names match schema (case-sensitive)
- Use `unresolved-types --filter missing_table` to identify issues

### "Validation shows issues"
- Run `validate-types` to see specific problems
- Regenerate databases if needed: `query.sh create-dbs`
- Check for empty parameters: `unresolved-types --filter empty_parameters`

## Getting Help

1. Check [TYPE_RESOLUTION_GUIDE.md](TYPE_RESOLUTION_GUIDE.md) for detailed docs
2. Review test files in `tests/` for usage examples
3. Check [IMPLEMENTATION_SUMMARY.md](../IMPLEMENTATION_SUMMARY.md) for technical details
