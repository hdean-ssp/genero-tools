# Project Structure & Organization

## Directory Layout

```
genero-tools/
├── src/                              # Main generation scripts
│   ├── generate_signatures.sh         # Extract function signatures from .4gl files
│   ├── generate_modules.sh            # Parse module dependencies from .m3 files
│   ├── generate_codebase_index.sh     # Merge signatures and modules into unified index
│   └── query.sh                       # Query wrapper script for database operations
│
├── scripts/                           # Python utility scripts
│   ├── parse_headers.py               # Extract file headers and author information
│   ├── merge_headers.py               # Merge header data into workspace.json
│   ├── parse_schema.py                # Parse database schema files
│   ├── resolve_types.py               # Resolve LIKE references to schema types
│   ├── merge_resolved_types.py        # Merge type resolution results
│   │
│   ├── json_to_sqlite.py              # Convert JSON to SQLite database
│   ├── json_to_sqlite_headers.py      # Create header tables in database
│   ├── json_to_sqlite_schema.py       # Create schema tables in database
│   ├── query_db.py                    # Query database functions
│   ├── query_headers.py               # Query header metadata
│   │
│   ├── metrics_extractor.py           # Extract code quality metrics
│   ├── metrics_models.py              # Metrics data models
│   ├── metrics_db.py                  # Metrics database operations
│   ├── quality_analyzer.py            # Analyze metrics and code quality
│   ├── incremental_generator.py       # Incremental metric updates
│   │
│   ├── batch_query_handler.py         # Handle batch query operations
│   ├── pagination_handler.py          # Handle pagination for large result sets
│   ├── query_with_pagination.py       # Query interface with pagination
│   ├── relationship_queries.py        # Query function relationships and dependencies
│   │
│   ├── process_codebase_index.py      # Process and validate codebase index
│   ├── process_modules.py             # Process module data
│   ├── process_signatures.py          # Process signature data
│   └── test_utils.py                  # Test helper functions
│
├── tests/                             # Test suite
│   ├── run_all_tests.sh               # Run all test suites
│   ├── run_tests.sh                   # Test signature generation
│   ├── run_module_tests.sh            # Test module generation
│   ├── test_call_graph.sh             # Test call graph extraction
│   ├── test_header_integration.sh     # Test header parsing integration
│   │
│   ├── test_*.py                      # Python test files (property-based, integration, unit)
│   │   ├── test_batch_query.py        # Batch query functionality
│   │   ├── test_pagination.py         # Pagination functionality
│   │   ├── test_type_resolution.py    # Type resolution system
│   │   ├── test_quality_analyzer.py   # Quality analyzer
│   │   ├── test_metrics_extraction.py # Metrics extraction
│   │   └── ... (more test files)
│   │
│   ├── sample_codebase/               # Test data
│   │   ├── simple_functions.4gl       # Basic function examples
│   │   ├── complex_types.4gl          # Complex type examples
│   │   ├── multiple_returns.4gl       # Multiple return value examples
│   │   ├── edge_cases.4gl             # Edge case examples
│   │   ├── special_types.4gl          # Special type examples
│   │   ├── whitespace_variations.4gl  # Whitespace handling examples
│   │   ├── no_returns.4gl             # Procedure-style functions
│   │   ├── schema.sch                 # Database schema for type resolution
│   │   ├── modules/                   # Module definition examples
│   │   ├── lib/                       # Library file examples
│   │   ├── expected_output.json       # Expected signature output
│   │   ├── expected_modules.json      # Expected module output
│   │   └── expected_index.json        # Expected codebase index output
│   │
│   └── README.md                      # Test documentation
│
├── docs/                              # Documentation
│   ├── ARCHITECTURE.md                # System architecture and design
│   ├── DEVELOPER_GUIDE.md             # Developer workflow and conventions
│   ├── FEATURES.md                    # Feature list and status
│   ├── QUERYING.md                    # Query interface documentation
│   ├── SECURITY.md                    # Security practices
│   ├── INDEX.md                       # Documentation index
│   │
│   ├── QUERY_LAYER_GUIDE.md           # Phase 2: Query layer and metrics
│   ├── CALL_GRAPH_QUERIES.md          # Call graph query documentation
│   ├── TYPE_RESOLUTION_GUIDE.md       # Type resolution system
│   ├── SCHEMA_PARSING_GUIDE.md        # Schema parsing documentation
│   ├── SCHEMA_RESOLUTION_IMPLEMENTATION.md # Type resolution implementation
│   │
│   ├── QUICK_START_*.md               # Feature-specific quick start guides
│   │   ├── QUICK_START_CALL_GRAPH.md
│   │   ├── QUICK_START_HEADERS.md
│   │   └── QUICK_START_TYPE_RESOLUTION.md
│   │
│   ├── PHASE_*.md                     # Phase completion reports
│   ├── GENERO_TOOLS_ROADMAP.md        # Project roadmap
│   ├── LSP_INTEGRATION_*.md           # LSP integration documentation
│   ├── VIM_PLUGIN_INTEGRATION_*.md    # Vim plugin integration
│   │
│   ├── api/                           # API documentation
│   │   ├── 00-START-HERE.md           # API quick start
│   │   ├── README.md                  # API overview
│   │   ├── MANIFEST.md                # API manifest
│   │   ├── INDEX.json                 # API index
│   │   ├── QUICK_REFERENCE.md         # API quick reference
│   │   ├── python-*.json              # Python API documentation
│   │   ├── shell-commands.json        # Shell command documentation
│   │   └── database-schema.json       # Database schema documentation
│   │
│   └── archive/                       # Archived documentation
│       └── (older documentation versions)
│
├── .kiro/                             # Kiro IDE configuration
│   ├── specs/                         # Spec files for features and bugfixes
│   │   ├── api-documentation/         # API documentation spec
│   │   ├── api-phase-1-enhancements/  # API enhancements spec
│   │   ├── type-resolution-improvements/ # Type resolution spec
│   │   ├── tag-parsing-clipping-fix/  # Bugfix spec
│   │   └── archive/                   # Archived specs
│   │
│   ├── steering/                      # Steering documents (this directory)
│   │   ├── product.md                 # Product overview
│   │   ├── tech.md                    # Technology stack
│   │   └── structure.md               # Project structure (this file)
│   │
│   ├── hooks/                         # Agent hooks configuration
│   └── suggestions/                   # Kiro suggestions
│
├── generate_all.sh                    # Main orchestration script
├── query.sh                           # Query interface wrapper
├── README.md                          # Project overview
├── LICENSE                            # License file
├── modules.json                       # Generated module data
├── workspace.json                     # Generated function signatures
├── workspace_resolved.json            # Generated type-resolved signatures
├── codebase_index.json                # Generated unified index
├── CODEBASE_INDEX.md                  # Codebase index documentation
├── DOCUMENTATION_UPDATES.md           # Documentation update log
├── CHECKPOINT_VERIFICATION_*.md       # Verification reports
└── castle.sch                         # Sample schema file
```

## Key File Categories

### Generation Scripts (src/)
- **generate_signatures.sh** - Extracts function signatures from .4gl files using AWK/sed
- **generate_modules.sh** - Parses .m3 module files for dependencies
- **generate_codebase_index.sh** - Merges signatures and modules into unified index
- **query.sh** - Shell wrapper for database queries

### Python Utilities (scripts/)

**Parsing & Processing:**
- parse_headers.py, parse_schema.py - Extract metadata from files
- merge_headers.py, merge_resolved_types.py - Merge data sources
- process_*.py - Data validation and transformation

**Database Operations:**
- json_to_sqlite*.py - Convert JSON to SQLite
- query_db.py, query_headers.py - Query interfaces
- metrics_db.py - Metrics database operations

**Analysis & Metrics:**
- metrics_extractor.py - Extract code quality metrics
- quality_analyzer.py - Analyze metrics
- incremental_generator.py - Efficient incremental updates
- relationship_queries.py - Query function relationships

**Advanced Features:**
- batch_query_handler.py - Handle batch operations
- pagination_handler.py - Handle large result sets
- resolve_types.py - Type resolution system

### Test Suite (tests/)

**Test Runners:**
- run_all_tests.sh - Execute all tests
- run_tests.sh - Signature generation tests
- run_module_tests.sh - Module generation tests
- test_*.sh - Feature-specific tests

**Test Files:**
- test_*.py - Python unit, integration, and property-based tests
- sample_codebase/ - Test data with expected outputs

### Documentation (docs/)

**Core Documentation:**
- ARCHITECTURE.md - System design
- DEVELOPER_GUIDE.md - Development workflow
- QUERYING.md - Query interface

**Feature Documentation:**
- QUERY_LAYER_GUIDE.md - Phase 2 metrics and queries
- CALL_GRAPH_QUERIES.md - Call graph functionality
- TYPE_RESOLUTION_GUIDE.md - Type resolution system
- SCHEMA_PARSING_GUIDE.md - Schema parsing

**Quick Start Guides:**
- QUICK_START_*.md - Feature-specific getting started guides

**API Documentation:**
- docs/api/ - Complete API reference and examples

## Data Flow

```
Genero Codebase (.4gl, .m3, .sch files)
    ↓
generate_signatures.sh → workspace.json (function signatures)
generate_modules.sh → modules.json (module dependencies)
generate_codebase_index.sh → codebase_index.json (unified index)
    ↓
parse_headers.py → extract headers
merge_headers.py → merge into workspace.json
    ↓
parse_schema.py → extract schema
resolve_types.py → resolve LIKE references
merge_resolved_types.py → workspace_resolved.json
    ↓
metrics_extractor.py → extract metrics
    ↓
json_to_sqlite*.py → create SQLite databases
    ↓
query_db.py / query.sh → Query Results (JSON)
```

## Output Files

### Generated Metadata
- **workspace.json** - Function signatures grouped by file (15-20MB for large codebases)
- **modules.json** - Module dependencies and file relationships
- **codebase_index.json** - Unified index with file IDs and module references
- **workspace_resolved.json** - Type-resolved signatures with schema references

### Generated Databases (Optional)
- **workspace.db** - Indexed function signatures (70KB for large codebases)
- **modules.db** - Indexed module dependencies
- **headers.db** - Indexed file headers and author information
- **metrics.db** - Code quality metrics and analysis data

## Naming Conventions

### File Naming
- Shell scripts: `generate_*.sh`, `test_*.sh`
- Python scripts: `parse_*.py`, `query_*.py`, `test_*.py`
- Test data: `*.4gl`, `*.m3`, `*.sch`
- Expected output: `expected_*.json`

### Function Naming (Python)
- Extraction: `parse_*()`, `extract_*()`
- Querying: `find_*()`, `search_*()`, `get_*()`
- Processing: `merge_*()`, `process_*()`, `normalize_*()`
- Analysis: `analyze_*()`, `calculate_*()`

### Variable Naming
- File paths: `file_path`, `output_file`
- Database connections: `conn`, `cursor`
- Results: `results`, `matches`, `records`
- Metadata: `metadata`, `_metadata`

## Code Organization Principles

1. **Separation of Concerns** - Each script has a single responsibility
2. **Reusability** - Common functions in test_utils.py
3. **Testability** - Comprehensive test suite with sample data
4. **Documentation** - Inline comments and docstrings
5. **Error Handling** - Graceful failures with informative messages
6. **Performance** - Optimized parsing and database queries
7. **Maintainability** - Clear naming and consistent patterns

## Adding New Features

1. Create test data in `tests/sample_codebase/`
2. Create test file in `tests/test_*.py` or `tests/test_*.sh`
3. Implement feature in appropriate script
4. Update documentation in `docs/`
5. Run full test suite: `bash tests/run_all_tests.sh`
6. Update this structure document if needed
