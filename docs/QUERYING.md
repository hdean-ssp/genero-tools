# Querying Guide

Complete reference for querying extracted metadata using shell commands, Python API, or direct database queries.

## Quick Start

```bash
# Create indexed databases (one-time setup)
bash query.sh create-dbs

# Find a function
bash query.sh find-function "my_function"

# Search functions by pattern
bash query.sh search-functions "get_*"

# Find dependencies
bash query.sh find-function-dependencies "process_request"

# Find code references
bash query.sh find-reference "PRB-299"

# Query resolved types
bash query.sh find-function-resolved "my_function"
```

## Function Queries

### Find Function

```bash
bash query.sh find-function "my_function"
```

Returns function signature, parameters, returns, and calls.

### Search Functions

```bash
bash query.sh search-functions "get_*"
```

Search functions by name pattern. Supports wildcards.

### List File Functions

```bash
bash query.sh list-file-functions "path/to/file.4gl"
```

List all functions in a specific file.

### Find Function by Name and Path

```bash
bash query.sh find-function-by-name-and-path "my_function" "./src/module.4gl"
```

Find specific function instance when multiple functions have the same name.

### Find All Function Instances

```bash
bash query.sh find-all-function-instances "my_function"
```

Find all instances of a function across different files.

## Dependency Queries

### Find Function Dependencies

```bash
bash query.sh find-function-dependencies "process_request"
```

Find all functions that `process_request` calls.

### Find Function Dependents

```bash
bash query.sh find-function-dependents "log_message"
```

Find all functions that call `log_message`.

## Code Reference Queries

### Find Reference

```bash
bash query.sh find-reference "PRB-299"
```

Find files containing a specific code reference.

### Search References

```bash
bash query.sh search-references "100512"
```

Search for code references matching a pattern. Automatically adds wildcards for partial matches.

**Examples:**
```bash
# Partial numeric search - finds EH100512, EH100512-9a, etc.
bash query.sh search-references "100512"

# Partial prefix search
bash query.sh search-references "EH100512"

# Explicit wildcard search
bash query.sh search-references "EH100512%"
```

### Search Reference Prefix

```bash
bash query.sh search-reference-prefix "EH100512"
```

Search for references starting with a specific prefix.

### Find Author

```bash
bash query.sh find-author "Rich"
```

Find files modified by a specific author.

### Author Expertise

```bash
bash query.sh author-expertise "Chilly"
```

Show what areas an author has expertise in based on modifications.

### Get File References

```bash
bash query.sh get-file-references "./src/utils.4gl"
```

Get all code references for a specific file.

## Type Resolution Queries

### Find Function Resolved

```bash
bash query.sh find-function-resolved "process_contract"
```

Get function with resolved LIKE type information.

### Unresolved Types

```bash
bash query.sh unresolved-types
```

Find all unresolved LIKE references.

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

### Validate Types

```bash
bash query.sh validate-types
```

Validate type resolution data consistency.

## Python API

### Query Functions

```python
from scripts.query_db import find_function, search_functions

# Find a function
result = find_function('workspace.db', 'my_function')

# Search functions by pattern
results = search_functions('workspace.db', 'get_*')
```

### Type Resolution API

```python
from scripts.query_db import (
    find_function_by_name_and_path,
    find_all_function_instances,
    find_unresolved_types,
    validate_type_resolution
)

# Find specific function instance
result = find_function_by_name_and_path('workspace.db', 'process_data', './src/module1.4gl')

# Find all instances of a function
instances = find_all_function_instances('workspace.db', 'process_data')

# Find unresolved LIKE references
unresolved = find_unresolved_types('workspace.db')

# Filter by error type
missing_tables = find_unresolved_types('workspace.db', filter_type='missing_table')

# With pagination
page = find_unresolved_types('workspace.db', limit=10, offset=20)

# Validate data consistency
report = validate_type_resolution('workspace.db')
if report['status'] == 'valid':
    print("Database is consistent")
else:
    for issue in report['issues']:
        print(f"Issue: {issue['message']}")
```

### Quality Analysis

```python
from scripts.quality_analyzer import QualityAnalyzer

qa = QualityAnalyzer('workspace.db')

# Find complex functions
complex_funcs = qa.find_complex_functions(threshold=10)

# Find long functions
long_funcs = qa.find_long_functions(threshold=100)

# Get function metrics
metrics = qa.get_function_metrics('my_function')

# Get file metrics
file_metrics = qa.get_file_metrics('path/to/file.4gl')
```

### Header Queries

```python
from scripts.query_headers import (
    find_reference,
    search_references,
    find_author,
    author_expertise
)

# Find files with a reference
files = find_reference('workspace.db', 'PRB-299')

# Search references by pattern
results = search_references('workspace.db', '100512')

# Find files by author
files = find_author('workspace.db', 'Rich')

# Get author expertise
expertise = author_expertise('workspace.db', 'Chilly')
```

## Direct Database Queries

### Find Functions with STRING Parameters

```python
import sqlite3
import json

conn = sqlite3.connect('workspace.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute('''SELECT DISTINCT f.name FROM functions f 
  JOIN parameters p ON f.id = p.function_id 
  WHERE p.type = 'STRING' ''')

results = [dict(row) for row in c.fetchall()]
print(json.dumps(results, indent=2))
conn.close()
```

### Find Resolved LIKE References

```python
import sqlite3

conn = sqlite3.connect('workspace.db')
c = conn.cursor()

c.execute('''SELECT f.name, p.type, p.resolved_columns, p.resolved_types
  FROM functions f
  JOIN parameters p ON f.id = p.function_id
  WHERE p.is_like_reference = 1 AND p.resolved = 1''')

for row in c.fetchall():
    print(f"{row[0]}: {row[1]} -> {row[2]}")

conn.close()
```

### Find Functions by Complexity

```python
import sqlite3

conn = sqlite3.connect('workspace.db')
c = conn.cursor()

c.execute('''SELECT name, file_path, complexity
  FROM functions
  WHERE complexity > 10
  ORDER BY complexity DESC''')

for row in c.fetchall():
    print(f"{row[0]} ({row[1]}): complexity={row[2]}")

conn.close()
```

## Performance

| Operation | Time |
|-----------|------|
| Exact lookup | <1ms |
| Pattern search | <10ms |
| Metrics queries | <10ms |
| Type resolution queries | <1ms |
| Validation | <1s |

## Troubleshooting

### Database Not Found

```
Error: database file not found
```

**Solution:** Create databases first:
```bash
bash query.sh create-dbs
```

### No Results

1. Verify the database has been created
2. Check that the search pattern is correct
3. Try a simpler pattern (e.g., "get_*" instead of "get_account_*")

### Too Many Results

1. Use a more specific pattern
2. Filter by file or author
3. Use pagination with `--limit` and `--offset`

## Related Documentation

- [docs/FEATURES.md](FEATURES.md) - Feature overview
- [docs/TYPE_RESOLUTION_GUIDE.md](TYPE_RESOLUTION_GUIDE.md) - Type resolution
- [docs/ARCHITECTURE.md](ARCHITECTURE.md) - System design
- [docs/api/](api/) - Complete API reference

