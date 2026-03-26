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

Track which functions call which other functions.

```bash
# Find what a function calls
bash query.sh find-function-dependencies process_request

# Find what calls a function
bash query.sh find-function-dependents log_message
```

**Use cases:** Impact analysis, dependency tracking, dead code detection.

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
- Variable Count
- Parameter Count
- Return Count
- Call Depth

```bash
# Find complex functions
python3 -c "from scripts.quality_analyzer import QualityAnalyzer; qa = QualityAnalyzer('workspace.db'); print(qa.find_complex_functions(threshold=10))"

# Get function metrics
python3 -c "from scripts.quality_analyzer import QualityAnalyzer; qa = QualityAnalyzer('workspace.db'); print(qa.get_function_metrics('my_function'))"
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

## Incremental Updates

Efficiently update metrics for changed files only.

```python
from scripts.incremental_generator import IncrementalGenerator

gen = IncrementalGenerator('workspace.db')
gen.update_metrics('/path/to/codebase')
```

**Benefits:** Fast updates for CI/CD pipelines, preserves existing data.

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
