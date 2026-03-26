# genero-tools API Documentation

Complete API reference for integrating genero-tools into external applications (Vim plugins, VS Code extensions, etc.).

## Quick Start

1. **Generate metadata (automatic schema detection)**: `bash generate_all.sh /path/to/codebase`
2. **Create databases**: `bash query.sh create-dbs`
3. **Query data**: `query.sh find-function my_function`
4. **Query resolved types**: `query.sh find-function-resolved my_function` (v2.1.0+)

## Documentation Files

- **INDEX.json** - Overview and file index
- **shell-commands.json** - All query.sh commands (30+)
- **python-query-db.json** - Core query functions (13+)
- **python-quality-analyzer.json** - Code metrics
- **python-query-headers.json** - Header/reference queries
- **python-metrics-extractor.json** - Metrics extraction
- **python-incremental-generator.json** - Incremental updates
- **python-db-conversion.json** - Database tools
- **data-formats.json** - JSON/output schemas
- **database-schema.json** - SQLite schemas
- **quick-reference.json** - Common tasks
- **vim-plugin-guide.json** - Vim integration (updated for v2.1.0)

## Interfaces

### Shell Interface
```bash
# Basic queries
query.sh find-function my_function
query.sh search-functions "get_*"

# Dependency analysis
query.sh find-function-dependencies my_function
query.sh find-function-dependents my_function

# Type resolution (v2.1.0+)
query.sh find-function-resolved my_function
query.sh find-function-by-name-and-path my_function "./src/module.4gl"
query.sh find-all-function-instances my_function
query.sh unresolved-types
query.sh unresolved-types --filter missing_table
query.sh validate-types
```

### Python API
```python
from scripts.query_db import find_function, find_function_resolved
from scripts.query_db import find_function_by_name_and_path, find_all_function_instances
from scripts.query_db import find_unresolved_types, validate_type_resolution

results = find_function('workspace.db', 'my_function')
resolved = find_function_resolved('workspace.db', 'my_function')
instance = find_function_by_name_and_path('workspace.db', 'my_function', './src/module.4gl')
```

### Database Interface
```bash
sqlite3 workspace.db "SELECT * FROM functions WHERE name = 'my_function'"
sqlite3 workspace.db "SELECT * FROM parameters WHERE is_like_reference = 1 AND resolved = 1"
```

## Query Categories

- **Function Lookup** - Find and search functions
- **Dependency Analysis** - Analyze call relationships
- **Module Queries** - Module-scoped operations
- **Header Queries** - Code references and authors
- **Type Resolution** - LIKE reference resolution, multi-instance functions, debugging (v2.1.0+)
- **Database Management** - Setup and maintenance

## Performance

- Exact lookup: <1ms
- Pattern search: <10ms
- Type resolution query: <1ms (v2.1.0+)
- Database creation: <5s
- Metrics extraction: <1ms per function

## For Vim Plugin Developers

See **vim-plugin-guide.json** for:
- Recommended features and queries (including type resolution v2.1.0)
- Integration approaches (shell, Python, database)
- Setup steps (automatic schema detection)
- Caching strategies
- Performance optimization
- Error handling
- New in v2.1.0 features

## Type Resolution Features (v2.1.0)

**Automatic Schema Detection**
- Schema files automatically found and processed
- Graceful fallback if no schema available

**Multi-instance Function Resolution**
- Disambiguate same-named functions in different files
- Query by name and file path

**LIKE Reference Resolution**
- Resolve database schema types for parameters and returns
- Supports `LIKE table.*` and `LIKE table.column` patterns
- Merged into workspace.db for efficient querying

**Unresolved Types Debugging**
- Query and debug type resolution failures
- Filter by error type (missing_table, missing_column, invalid_pattern)
- Pagination support

**Data Consistency Validation**
- Validate type resolution data integrity
- Check for empty parameters, missing file_path, unresolved references

See **vim-plugin-guide.json** for type resolution integration patterns.

## Data Formats

All queries return JSON with consistent structure:
- Function objects with signatures, parameters, returns, calls
- Resolved type information (v2.1.0+)
- Module objects with file lists and dependencies
- Metrics objects with quality indicators

See **data-formats.json** for complete schemas.

## Database Schema

Two SQLite databases:
- **workspace.db** - Functions, parameters, returns, calls, headers, resolved types (v2.1.0+)
- **modules.db** - Modules and file dependencies

See **database-schema.json** for complete schema.

## Getting Help

1. Check **quick-reference.json** for common tasks
2. Review **vim-plugin-guide.json** for integration patterns
3. See **data-formats.json** for output structure
4. Check **database-schema.json** for direct SQL queries
5. Read **TYPE_RESOLUTION_RELEASE_NOTES_v2_1_0.md** for v2.1.0 features

