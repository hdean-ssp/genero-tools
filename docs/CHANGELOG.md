# Changelog

All notable changes to this project are documented here.

## [Unreleased]

### Added
- File header parsing to extract code references and author information
- `scripts/parse_headers.py` - Flexible header parser with column detection
- `scripts/merge_headers.py` - Merge header data into workspace.json
- `scripts/json_to_sqlite_headers.py` - Create indexed header tables in database
- `scripts/query_headers.py` - Query functions for references and authors
- `tests/test_header_integration.sh` - Comprehensive header parsing tests
- `docs/HEADER_PARSING_ANALYSIS.md` - Header format analysis
- `docs/HEADER_PARSING_IMPLEMENTATION.md` - Implementation details
- `docs/QUICK_START_HEADERS.md` - Quick start guide for header queries
- Header query commands in `query.sh`:
  - `find-reference` - Find files containing a code reference
  - `find-author` - Find files modified by an author
  - `get-file-references` - Get all references for a file
  - `get-file-authors` - Get all authors for a file
  - `author-expertise` - Show author expertise areas
  - `find-recent-changes` - Find recently modified files
  - `search-references` - Search references by pattern

### Changed
- `generate_all.sh` - Now includes header extraction and merging
- `workspace.json` - Functions now include `file_references` and `file_authors`
- `workspace.db` - Added `file_references` and `file_authors` tables with indexes
- Test suite updated with new line numbers from header additions

### Features
- Flexible column detection (no hard-coded patterns)
- Handles variable spacing (tabs/spaces)
- Works with optional columns
- Supports any reference format (PRB-299, EH100512, SR-40356-3, etc.)
- Graceful error handling (files with no headers skipped silently)
- Author statistics (first/last change, change count)
- Indexed database queries for fast lookups

### Performance
- Header parsing: <1ms per file
- Database queries: <10ms for most operations
- Minimal overhead to generation pipeline

### Testing
- All 7 header integration tests passing
- All 32 function signature tests passing
- All 8 call graph tests passing
- Full end-to-end pipeline verified

## [1.1.0] - 2026-03-13

### Added
- Call graph generation to track function dependencies
- `scripts/query_db.py` - Query interface for databases
- `tests/test_call_graph.sh` - Call graph test suite
- `docs/CALL_GRAPH_QUERIES.md` - Call graph documentation
- Query commands for dependencies and dependents
- Support for control flow call detection (IF, WHILE, CASE, etc.)

### Features
- Extracts function calls from function bodies
- Tracks call line numbers
- Handles nested function calls
- Supports all control flow structures
- Backward compatible with existing code

## [1.0.0] - 2026-03-12

### Added
- Initial release of Genero Function Signatures project
- `generate_signatures.sh` - Extract function signatures from .4gl files
- `generate_modules.sh` - Parse module dependencies from .m3 files
- `generate_codebase_index.sh` - Generate unified codebase index
- Comprehensive test suite with 23 test functions
- Full documentation (README, MODULE_GENERATOR, CODEBASE_INDEX)
- Support for all Genero data types
- Line number tracking for IDE integration
- Metadata generation for validation

### Features
- Extracts function names, parameters, return values
- Handles multi-line function definitions
- Parses module file dependencies (L4GLS, U4GLS, 4GLS)
- Handles multi-line variable assignments
- Generates structured JSON output
- Includes generation metadata and timestamps
- Robust error handling with automatic cleanup

### Added (Previous Release)
- SQLite database tools for efficient querying of large JSON files
- `query.sh` - User-friendly shell wrapper for database queries
- `scripts/json_to_sqlite.py` - Convert JSON to indexed SQLite databases
- `QUERYING.md` - Documentation for database tools
- `ARCHITECTURE.md` - Comprehensive architecture documentation
- Separate Python scripts for JSON processing (cleaner code organization)

### Changed (Previous Release)
- Replaced `jq` dependency with Python 3 (built-in on most systems)
- Moved Python code from heredocs to separate script files
- Improved error handling and code organization
- Updated all documentation to reflect Python-based approach

### Removed (Previous Release)
- Dependency on `jq` command-line tool
- Inline Python heredocs (moved to separate files)
