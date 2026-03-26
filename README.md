# genero-tools

Comprehensive codebase analysis tool that extracts and indexes rich metadata from Genero/4GL codebases to enable IDE/editor integration, AI-powered code review, and developer tooling.

## Features

- **Function Signature Extraction** - Names, parameters, return types, line numbers
- **Call Graph Analysis** - Track which functions call which other functions
- **File Header Parsing** - Extract code references and author information for impact analysis
- **Code Quality Metrics** - Lines of code, cyclomatic complexity, variable count, parameter count, return count, call depth
- **Type Resolution** - Resolve LIKE references to actual schema types, handle multi-instance functions
- **Structured Metadata** - JSON and SQLite databases for fast querying
- **Comprehensive Type Support** - All Genero data types including complex and special types

## Requirements

- Bash shell
- Python 3.6+ (for JSON processing and database tools)
- Standard Unix utilities: `find`, `sed`, `awk`, `date`

No external dependencies like `jq` needed - everything uses built-in Python.

## Quick Start

### 1. Generate Metadata

```bash
# Automatic schema detection and type resolution
bash generate_all.sh /path/to/codebase

# Or individual steps
bash generate_signatures.sh /path/to/codebase
bash generate_modules.sh /path/to/codebase
bash query.sh create-dbs
```

### 2. Query Functions

```bash
# Find a function
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

### 3. Analyze Dependencies

```bash
# Find what a function calls
bash query.sh find-function-dependencies process_request

# Find what calls a function
bash query.sh find-function-dependents log_message
```

### 4. Search Code References

```bash
# Find files containing a code reference
bash query.sh find-reference "PRB-299"

# Find files modified by an author
bash query.sh find-author "Rich"

# Show author expertise areas
bash query.sh author-expertise "Chilly"
```

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
| Signature extraction | <1ms per file |
| Module parsing | <1ms per file |
| Database exact lookup | <1ms |
| Database pattern search | <10ms |
| Type resolution query | <1ms |
| Metrics extraction | <1ms per function |

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

