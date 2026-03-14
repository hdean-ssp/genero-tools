# genero-tools API Documentation

Complete API reference for integrating genero-tools into external applications (Vim plugins, VS Code extensions, etc.).

## Quick Start

1. **Generate metadata**: `bash generate_signatures.sh /path/to/codebase`
2. **Create databases**: `bash query.sh create-dbs`
3. **Query data**: `query.sh find-function my_function`

## Documentation Files

- **INDEX.json** - Overview and file index
- **shell-commands.json** - All query.sh commands
- **python-query-db.json** - Core query functions
- **python-quality-analyzer.json** - Code metrics
- **python-query-headers.json** - Header/reference queries
- **python-metrics-extractor.json** - Metrics extraction
- **python-incremental-generator.json** - Incremental updates
- **python-db-conversion.json** - Database tools
- **data-formats.json** - JSON/output schemas
- **database-schema.json** - SQLite schemas
- **quick-reference.json** - Common tasks
- **vim-plugin-guide.json** - Vim integration

## Interfaces

### Shell Interface
```bash
query.sh find-function my_function
query.sh search-functions "get_*"
query.sh find-function-dependencies my_function
```

### Python API
```python
from scripts.query_db import find_function
results = find_function('workspace.db', 'my_function')
```

### Database Interface
```bash
sqlite3 workspace.db "SELECT * FROM functions WHERE name = 'my_function'"
```

## Query Categories

- **Function Lookup** - Find and search functions
- **Dependency Analysis** - Analyze call relationships
- **Module Queries** - Module-scoped operations
- **Header Queries** - Code references and authors
- **Database Management** - Setup and maintenance

## Performance

- Exact lookup: <1ms
- Pattern search: <10ms
- Database creation: <5s
- Metrics extraction: <1ms per function

## For Vim Plugin Developers

See **vim-plugin-guide.json** for:
- Recommended features and queries
- Integration approaches (shell, Python, database)
- Setup steps
- Caching strategies
- Performance optimization
- Error handling

## Data Formats

All queries return JSON with consistent structure:
- Function objects with signatures, parameters, returns, calls
- Module objects with file lists and dependencies
- Metrics objects with quality indicators

See **data-formats.json** for complete schemas.

## Database Schema

Two SQLite databases:
- **workspace.db** - Functions, parameters, returns, calls, headers
- **modules.db** - Modules and file dependencies

See **database-schema.json** for complete schema.

## Getting Help

1. Check **quick-reference.json** for common tasks
2. Review **vim-plugin-guide.json** for integration patterns
3. See **data-formats.json** for output structure
4. Check **database-schema.json** for direct SQL queries
