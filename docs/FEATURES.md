# Features Guide

Comprehensive overview of all genero-tools features with examples.

## Function Signatures

Extract function names, parameters, return types, and line numbers from .4gl files.

```bash
bash generate_signatures.sh /path/to/codebase
```

Output: `workspace.json` with structured function metadata grouped by file.

**Example:**
```json
{
  "path/to/file.4gl": [
    {
      "name": "calculate",
      "line": {"start": 15, "end": 42},
      "signature": "15-42: calculate(amount INTEGER):result DECIMAL",
      "parameters": [{"name": "amount", "type": "INTEGER"}],
      "returns": [{"name": "result", "type": "DECIMAL"}]
    }
  ]
}
```

## Module Dependencies

Parse .m3 makefiles to extract file dependencies (L4GLS, U4GLS, 4GLS).

```bash
bash generate_modules.sh /path/to/codebase
```

Output: `modules.json` with module definitions and file lists.

## Call Graphs

Track which functions call which other functions, with automatic cross-file resolution. Called function names are resolved to their actual database IDs, enabling true file-to-file dependency analysis.

```bash
# Find what a function calls
bash query.sh find-function-dependencies process_request

# Find what calls a function (resolves across files)
bash query.sh find-function-dependents log_message

# Find dead code (functions never called by anything)
bash query.sh find-dead-code
```

**Cross-file resolution:** The `calls` table includes a `resolved_function_id` column linking each call to the callee's actual function record. This enables queries like:

```sql
-- Find all cross-file dependencies
SELECT f1.name AS caller, fi1.path AS caller_file,
       f2.name AS callee, fi2.path AS callee_file
FROM calls c
JOIN functions f1 ON c.function_id = f1.id
JOIN files fi1 ON f1.file_id = fi1.id
JOIN functions f2 ON c.resolved_function_id = f2.id
JOIN files fi2 ON f2.file_id = fi2.id
WHERE fi1.path != fi2.path
```

**Use cases:** Impact analysis, dependency tracking, dead code detection.

## Schema Impact Analysis

Find all functions that reference a given database table or column via LIKE types. Essential for planning schema migrations.

```bash
# Which functions reference the customer table at all?
bash query.sh find-functions-using customer

# Which functions specifically use customer.cus_name?
bash query.sh find-functions-using customer cus_name
```

Searches parameters, returns, and local variables for LIKE references matching the specified table/column.

**Use cases:** Schema migration planning, impact assessment before column changes.

## File Headers

Extract code references and author information from file modification sections.

```bash
# Find files containing a code reference
bash query.sh find-reference "PRB-299"

# Find files modified by an author
bash query.sh find-author "Rich"

# Show author expertise areas
bash query.sh author-expertise "Chilly"
```

**Supported formats:** PRB-299, EH100512, SR-40356-3, etc.

## Code Quality Metrics (Phase 2)

Extract and analyze code metrics for quality assessment.

**Metrics extracted:**
- Lines of Code (LOC)
- Cyclomatic Complexity
- Local Variable Count
- Parameter Count
- Return Count
- Early Returns
- Call Depth
- Comment Lines and Comment Ratio

Metrics are automatically extracted during `generate_all.sh` and stored in the `function_metrics` table in workspace.db.

```bash
# Find complex functions (via Python API)
python3 -c "
import sys; sys.path.insert(0, 'scripts')
from quality_analyzer import QualityAnalyzer
qa = QualityAnalyzer('workspace.db')
for f in qa.find_complex_functions(max_complexity=10, max_loc=100, max_parameters=5):
    print(f'{f[\"name\"]} - complexity:{f[\"complexity\"]}, loc:{f[\"loc\"]}')
"

# Direct SQL query for full control
sqlite3 workspace.db "
  SELECT f.name, fi.path, fm.complexity, fm.loc, fm.parameters
  FROM function_metrics fm
  JOIN functions f ON fm.function_id = f.id
  JOIN files fi ON f.file_id = fi.id
  WHERE fm.complexity > 10
  ORDER BY fm.complexity DESC
"

# Find functions by flexible criteria
python3 -c "
import sys; sys.path.insert(0, 'scripts')
from quality_analyzer import QualityAnalyzer
qa = QualityAnalyzer('workspace.db')
results = qa.find_by_metrics({'complexity': {'gt': 5}, 'loc': {'gt': 50}})
print(f'Found {len(results)} functions')
"
```

## Type Resolution

Resolve LIKE references and database schema types with automatic schema detection.

```bash
# Automatic schema detection and type resolution
bash generate_all.sh /path/to/codebase

# Query resolved types
bash query.sh find-function-resolved "process_contract"

# Parse schema file (manual)
python3 scripts/parse_schema.py database.sch schema.json

# Load into database (manual)
python3 scripts/json_to_sqlite_schema.py schema.json workspace.db

# Generate signatures with type resolution (manual)
RESOLVE_TYPES=1 bash src/generate_signatures.sh /path/to/codebase
```

### Type Resolution Features (v2.1.0)

**Automatic Schema Detection**
- Automatically finds and processes `.sch` files in target directory
- Gracefully skips type resolution if no schema found
- Integrated into `generate_all.sh` workflow

**Empty Parameter Filtering**
- Automatically removes invalid parameters with empty names
- Enforces data quality constraints
- Improves database query accuracy

**LIKE Reference Resolution**
- Resolves LIKE references in both parameters and return types
- Supports `LIKE table.*` and `LIKE table.column` patterns
- Stores resolved type information in database
- Merged into workspace.db for efficient querying

**Multi-Instance Function Resolution**
- Properly handles functions with same name in different files
- Stores file_path for each function instance
- Query by name and file path for disambiguation

```bash
# Find specific function instance
bash query.sh find-function-by-name-and-path my_function './src/module.4gl'

# Find all instances of a function
bash query.sh find-all-function-instances my_function

# Get function with resolved types
bash query.sh find-function-resolved process_contract
```

**Unresolved Types Debugging**
- Query command to identify type resolution failures
- Filter by error type (missing_table, missing_column, invalid_pattern)
- Pagination support for large result sets

```bash
# Show all unresolved types
bash query.sh unresolved-types

# Filter by error type
bash query.sh unresolved-types --filter missing_table

# Paginate results
bash query.sh unresolved-types --limit 10 --offset 5
```

**Data Consistency Validation**
- Comprehensive validation of type resolution data
- Checks for empty parameters, missing file_path, unresolved LIKE references
- Validates schema consistency

```bash
bash query.sh validate-types
```

## Database Queries

Query extracted metadata using Python's sqlite3 module.

```python
import sqlite3
import json

# Find all functions with STRING parameters
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

## Incremental Generation

The pipeline tracks file content hashes in `.genero-manifest.json`. On subsequent runs, only changed or added files are re-processed and merged into the existing workspace.json. Deleted files are automatically removed from the index.

```bash
# First run: processes all files, creates .genero-manifest.json
bash generate_all.sh /path/to/codebase

# Subsequent runs: only re-processes changed files
bash generate_all.sh /path/to/codebase

# Force full rebuild when needed (e.g. after tool update)
FORCE_FULL=1 bash generate_all.sh /path/to/codebase

# Disable incremental mode entirely
INCREMENTAL=0 bash generate_all.sh /path/to/codebase
```

**Benefits:**
- Fast re-runs: skips unchanged files entirely
- Ideal for CI/CD pipelines where only a few files change per commit
- Preserves existing data for unchanged files
- Automatically handles added and deleted files

## Performance

| Operation | Time |
|-----------|------|
| Signature extraction | <1ms per file |
| Module parsing | <1ms per file |
| Header parsing | <1ms per file |
| Database exact lookup | <1ms |
| Database pattern search | <10ms |
| Metrics extraction | <1ms per function |

## Integration

### Query Interface

```bash
# Create indexed databases
bash query.sh create-dbs

# Find a function
bash query.sh find-function "my_function"

# Search functions by pattern
bash query.sh search-functions "get_*"

# List functions in a file
bash query.sh list-file-functions "path/to/file.4gl"
```

### Python API

```python
from scripts.query_db import query_function, search_functions
from scripts.quality_analyzer import QualityAnalyzer

# Query functions
results = query_function('workspace.db', 'my_function')

# Search functions
results = search_functions('workspace.db', 'get_*')

# Analyze quality
qa = QualityAnalyzer('workspace.db')
complex_funcs = qa.find_complex_functions(threshold=10)
```

## Requirements

- Bash shell
- Python 3.6+
- Standard Unix utilities: `find`, `sed`, `awk`, `date`
- No external dependencies

## Release Notes

- **[Type Resolution v2.1.0 Release Notes](TYPE_RESOLUTION_RELEASE_NOTES_v2_1_0.md)** - Complete v2.1.0 feature overview, migration guide, and performance improvements

## Next Steps

- Read [README.md](../README.md) for quick start
- Read [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- Read [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) for development workflow
- Read [SECURITY.md](SECURITY.md) for security practices
- Read [TYPE_RESOLUTION_RELEASE_NOTES_v2_1_0.md](TYPE_RESOLUTION_RELEASE_NOTES_v2_1_0.md) for latest features
