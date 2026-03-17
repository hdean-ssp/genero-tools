# Technology Stack & Build System

## Core Technologies

### Languages
- **Bash** - Main orchestration and text processing scripts
- **AWK/sed** - High-performance text parsing and extraction
- **Python 3.6+** - JSON processing, database operations, testing, utilities
- **SQLite 3** - Optional indexed database for efficient querying (built-in, no external dependencies)

### Key Libraries
- **Standard Library Only** - No external Python dependencies (json, sqlite3, os, sys, argparse, etc.)
- **Built-in Tools** - find, sed, awk, date, grep (standard Unix utilities)

## Project Structure

```
genero-tools/
├── src/                    # Main generation scripts (Bash/AWK)
├── scripts/                # Python utility scripts
├── tests/                  # Test suite (Bash and Python)
├── docs/                   # Documentation (Markdown)
└── generate_all.sh         # Main orchestration script
```

## Build & Execution

### Main Generation Pipeline

```bash
# Generate all metadata (signatures, modules, metrics)
bash generate_all.sh /path/to/genero/code

# Or individual components:
bash src/generate_signatures.sh /path/to/code      # Extract function signatures
bash src/generate_modules.sh /path/to/code         # Parse module dependencies
bash src/generate_codebase_index.sh                # Merge signatures and modules
```

### Database Creation (Optional)

```bash
# Create SQLite databases for efficient querying
python3 scripts/json_to_sqlite.py workspace.json workspace.db
python3 scripts/json_to_sqlite_headers.py workspace.json workspace.db
```

### Querying

```bash
# Query interface (shell wrapper)
bash query.sh find-function "my_function"
bash query.sh search-functions "get_*"
bash query.sh find-reference "PRB-299"

# Or direct Python
python3 scripts/query_db.py find-function workspace.db "my_function"
```

## Testing

### Run All Tests
```bash
bash tests/run_all_tests.sh
```

### Run Specific Test Suites
```bash
bash tests/run_tests.sh                    # Signature generation
bash tests/run_module_tests.sh             # Module generation
bash tests/test_call_graph.sh              # Call graph extraction
bash tests/test_header_integration.sh      # Header parsing
python3 tests/test_quality_analyzer.py     # Quality analyzer
python3 tests/test_metrics_extraction.py   # Metrics extraction
python3 tests/test_phase2_integration.py   # Phase 2 integration
```

### Test Data
- Located in `tests/sample_codebase/`
- 7 .4gl files with 23 functions covering various scenarios
- 9 .m3 files with module dependency examples
- Expected output files for comparison

## Common Commands

### Development Workflow

```bash
# Generate metadata with verbose output
VERBOSE=1 bash generate_all.sh tests/sample_codebase

# Run full test suite
bash tests/run_all_tests.sh

# Test a single file
bash src/generate_signatures.sh tests/sample_codebase/simple_functions.4gl

# Query the database
bash query.sh find-function "calculate"
bash query.sh search-functions "get_*"
bash query.sh find-reference "PRB-299"
```

### Performance & Debugging

```bash
# Time the generation
time bash generate_all.sh /path/to/code

# Check intermediate files
python3 -c "import json; data=json.load(open('workspace.json')); print(f'Functions: {sum(len(v) for k,v in data.items() if not k.startswith(\"_\"))}')"

# Query database directly
python3 -c "import sqlite3; conn=sqlite3.connect('workspace.db'); c=conn.cursor(); c.execute('SELECT COUNT(*) FROM functions'); print(c.fetchone())"
```

## Output Formats

### JSON Files
- **workspace.json** - Function signatures grouped by file
- **modules.json** - Module dependencies and file relationships
- **codebase_index.json** - Unified index with file IDs and module references
- **workspace_resolved.json** - Type-resolved signatures with schema references

### SQLite Databases
- **workspace.db** - Indexed function signatures and metadata
- **modules.db** - Indexed module dependencies
- **headers.db** - Indexed file headers and author information
- **metrics.db** - Code quality metrics and analysis data

## Performance Characteristics

| Operation | JSON | SQLite |
|-----------|------|--------|
| File size | 15-20MB | 70KB |
| Load time | 2-5s | <100ms |
| Exact lookup | 2-5s | <1ms |
| Pattern search | 2-5s | <10ms |
| Memory usage | 100-200MB | <10MB |

## Environment Variables

```bash
VERBOSE=1              # Enable progress output (default: 0)
OUTPUT_FILE=custom.json # Specify output filename (default: workspace.json)
```

## Requirements

- Bash shell
- Python 3.6+
- Standard Unix utilities: find, sed, awk, date, grep
- SQLite 3 (optional, for database queries)

## No External Dependencies

- No pip packages required
- No npm/yarn dependencies
- No system libraries to install
- Everything uses standard library and built-in tools
