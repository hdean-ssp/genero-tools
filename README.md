# genero-tools

Comprehensive codebase analysis tool that extracts and indexes rich metadata from Genero/4GL codebases to enable IDE/editor integration, AI-powered code review, and developer tooling.

## Features

- **Function Signature Extraction** - Names, parameters, return types, line numbers
- **Call Graph Analysis** - Track which functions call which, with cross-file resolution
- **Schema Impact Analysis** - Find all functions affected by a table/column change
- **File Header Parsing** - Extract code references and author information for impact analysis
- **Code Quality Metrics** - Lines of code, cyclomatic complexity, variable count, parameter count, return count, call depth
- **Type Resolution** - Resolve LIKE references to actual schema types, handle multi-instance functions
- **Incremental Generation** - Only re-process changed files on subsequent runs
- **Structured Metadata** - JSON and SQLite databases for fast querying
- **Comprehensive Type Support** - All Genero data types including complex and special types

## Requirements

- Bash shell
- Python 3.6+ (for JSON processing and database tools)
- Standard Unix utilities: `find`, `sed`, `awk`, `date`

No external dependencies like `jq` needed - everything uses built-in Python.

## Quick Start

### Generate the index for your workspace

From the genero-tools directory, point `generate_all.sh` at your Genero codebase:

```bash
# Basic usage - auto-detects .sch schema files in the target directory
bash generate_all.sh /path/to/your/genero/codebase

# If your schema file is stored elsewhere
bash generate_all.sh /path/to/your/genero/codebase /path/to/database.sch

# Verbose output to see what's happening
VERBOSE=1 bash generate_all.sh /path/to/your/genero/codebase
```

This produces:
- `workspace.json` + `workspace.db` — function signatures, metrics, call graphs
- `modules.json` + `modules.db` — module dependencies from `.m3` files
- `modulars.json` — GLOBALS/IMPORT relationships
- `workspace_resolved.json` — signatures with resolved LIKE types (if schema found)

**Re-running is fast** — only changed files are re-processed automatically. To force a full rebuild: `FORCE_FULL=1 bash generate_all.sh ...`

### Query the results

```bash
# Find a function by name
bash query.sh find-function my_function

# Search functions by pattern
bash query.sh search-functions "get_*"

# Get resolved types (v2.1.0+)
bash query.sh find-function-resolved my_function

# Find all instances of a function
bash query.sh find-all-function-instances my_function

# Debug type resolution
bash query.sh unresolved-types
bash query.sh validate-types
```

### Analyze dependencies

```bash
# Find what a function calls
bash query.sh find-function-dependencies process_request

# Find what calls a function (cross-file resolution included)
bash query.sh find-function-dependents log_message

# Find dead code (functions never called by anything)
bash query.sh find-dead-code

# What GLOBALS/IMPORT does a file depend on?
bash query.sh file-deps my_module.4gl

# What files include a specific globals file?
bash query.sh file-dependents shared_globals
```

### Schema impact analysis

```bash
# Which functions break if I change the customer table?
bash query.sh find-functions-using customer

# Which functions reference a specific column?
bash query.sh find-functions-using customer cus_name
```

### Search code references

```bash
# Find files containing a code reference
bash query.sh find-reference "PRB-299"

# Find files modified by an author
bash query.sh find-author "Rich"

# Show author expertise areas
bash query.sh author-expertise "Chilly"
```

For the full list of available commands: `bash query.sh --help`

## Documentation

- **[docs/FEATURES.md](docs/FEATURES.md)** - Complete feature list with examples
- **[docs/QUERYING.md](docs/QUERYING.md)** - Query interface documentation
- **[docs/TYPE_RESOLUTION_GUIDE.md](docs/TYPE_RESOLUTION_GUIDE.md)** - Type resolution system
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System design and components
- **[docs/DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md)** - Development workflow
- **[docs/SECURITY.md](docs/SECURITY.md)** - Security practices
- **[docs/api/](docs/api/)** - Complete API reference (JSON format)

## Type Resolution (v2.1.0)

Comprehensive LIKE reference resolution with automatic schema detection and data quality improvements.

```bash
# Automatically detects and processes schema files
bash generate_all.sh /path/to/codebase

# Query resolved types
bash query.sh find-function-resolved "process_contract"

# Find specific function instance by name and file
bash query.sh find-function-by-name-and-path "my_function" "./src/module.4gl"

# Find all instances of a function across files
bash query.sh find-all-function-instances "my_function"

# Debug type resolution issues
bash query.sh unresolved-types
bash query.sh unresolved-types --filter missing_table
bash query.sh unresolved-types --limit 10 --offset 5

# Validate type resolution data consistency
bash query.sh validate-types
```

**Features:**
- Automatic schema detection and parsing
- LIKE reference resolution (parameters and return types)
- Multi-instance function disambiguation
- Empty parameter filtering for data quality
- Comprehensive type resolution debugging
- Data consistency validation

## Code Quality Metrics

Automatically extracted during `generate_all.sh` and stored in `workspace.db` for instant querying.

**Metrics per function:**
- Lines of Code (LOC), cyclomatic complexity, local variable count
- Parameter count, return count, early returns, call depth
- Comment lines and comment ratio

```bash
# Find complex functions (complexity > 10, LOC > 100, or params > 5)
python3 -c "
import sys; sys.path.insert(0, 'scripts')
from quality_analyzer import QualityAnalyzer
qa = QualityAnalyzer('workspace.db')
for f in qa.find_complex_functions():
    print(f'{f[\"name\"]} - complexity:{f[\"complexity\"]}, loc:{f[\"loc\"]}')
"

# Direct SQL query
sqlite3 workspace.db "
  SELECT f.name, fm.complexity, fm.loc, fm.parameters
  FROM function_metrics fm
  JOIN functions f ON fm.function_id = f.id
  WHERE fm.complexity > 10
  ORDER BY fm.complexity DESC
"
```

## Use Cases

### IDE/Editor Integration
Query the database to provide rich metadata for editor plugins:
- Hover information with function signatures and dependencies
- Code completion with parameter types
- Go-to-definition navigation
- Find references for refactoring

### AI-Powered Code Review
Automated analysis agents can use this data to:
- Review new functions against codebase patterns
- Detect type mismatches and unresolved calls
- Identify similar functions for pattern matching
- Prioritize review based on complexity metrics

### Developer Tooling
Command-line tools for common development tasks:
- Impact analysis before changes
- Dead code detection
- Dependency tracking
- Code ownership and expertise tracking

## Performance

| Operation | Time |
|-----------|------|
| Incremental re-run (no changes) | <1s |
| Incremental re-run (few files changed) | ~2-5s |
| Full rebuild (3,400 files) | ~10 min |
| Database exact lookup | <1ms |
| Database pattern search | <10ms |
| Type resolution query | <1ms |

## Pipeline

`generate_all.sh` runs the following steps in order:

1. **Signature extraction** — Parse `.4gl` files for function signatures (incremental)
2. **Header extraction** — Extract code references and author info from file headers
3. **Modular extraction** — Parse GLOBALS/IMPORT statements from `.4gl` files
4. **Module dependencies** — Parse `.m3` makefiles for file relationships
5. **Database creation** — Convert JSON to indexed SQLite databases
6. **Call resolution** — Resolve cross-file function call references
7. **Schema parsing** — Load `.sch` files for type resolution (if found)
8. **Type resolution** — Resolve LIKE references to actual schema types
9. **Metrics extraction** — Extract LOC, complexity, and other quality metrics

### Incremental Mode

File content hashes are stored in `.genero-manifest.json`. On subsequent runs:
- **No changes detected** — exits in under 1 second, skipping all steps
- **Files changed** — only re-processes changed files through the entire pipeline (signatures, DB update, metrics). Unchanged data stays intact in workspace.db.

This is the default behavior when a manifest and workspace.db already exist.

| Environment Variable | Effect |
|---------------------|--------|
| `INCREMENTAL=0` | Disable incremental mode, always do full rebuild |
| `FORCE_FULL=1` | One-time full rebuild (still updates manifest for next run) |
| `VERBOSE=1` | Show detailed progress output |

| Scenario | Time (3,400 files) |
|----------|-------------------|
| No changes | <1 second |
| 1-5 files changed | ~2-5 seconds |
| Full rebuild | ~10 minutes |

### Generated Files

| File | Description |
|------|-------------|
| `workspace.json` | Function signatures grouped by file |
| `workspace.db` | SQLite database (signatures, headers, metrics) |
| `workspace_resolved.json` | Signatures with resolved LIKE types |
| `modules.json` | Module dependencies from `.m3` files |
| `modules.db` | SQLite database for module queries |
| `modulars.json` | GLOBALS/IMPORT statements per file |
| `.genero-manifest.json` | File hashes for incremental mode (not committed) |

## Testing

Run the test suite to verify the script works correctly:

```bash
bash tests/run_all_tests.sh
```

The test suite includes comprehensive tests for:
- Signature extraction
- Module parsing
- Call graph analysis
- Header parsing
- Type resolution
- Metrics extraction

## Integration

### Shell Interface
```bash
bash query.sh find-function my_function
bash query.sh search-functions "get_*"
bash query.sh find-function-dependencies my_function
bash query.sh find-function-by-name-and-path my_function "./src/module.4gl"
```

### Python API
```python
from scripts.query_db import find_function, find_function_resolved
from scripts.quality_analyzer import QualityAnalyzer

results = find_function('workspace.db', 'my_function')
resolved = find_function_resolved('workspace.db', 'my_function')
qa = QualityAnalyzer('workspace.db')
complex_funcs = qa.find_complex_functions(threshold=10)
```

### Database Interface
```bash
sqlite3 workspace.db "SELECT * FROM functions WHERE name = 'my_function'"
sqlite3 workspace.db "SELECT * FROM parameters WHERE is_like_reference = 1 AND resolved = 1"
```

## Project Status

- **Phase 1 (Complete):** Core signature and module extraction
- **Phase 2 (Complete):** Code quality metrics, type resolution, batch queries, pagination
- **Phase 3 (In Progress):** IDE/editor integration, advanced tooling

## License

See [LICENSE](LICENSE) file for details.

## Getting Help

1. Check [docs/FEATURES.md](docs/FEATURES.md) for feature overview
2. Review [docs/QUERYING.md](docs/QUERYING.md) for query examples
3. See [docs/TYPE_RESOLUTION_GUIDE.md](docs/TYPE_RESOLUTION_GUIDE.md) for type resolution
4. Check [docs/api/](docs/api/) for complete API reference
5. Review [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for system design

