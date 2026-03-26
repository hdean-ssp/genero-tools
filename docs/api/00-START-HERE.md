# genero-tools API Documentation

**Start here for complete API reference for integrating genero-tools into external applications.**

## What is This?

Complete, structured API documentation for genero-tools in JSON format. Use this to integrate genero-tools into:
- Vim plugins
- VS Code extensions
- Custom analysis tools
- IDE integrations
- CI/CD pipelines

## Quick Navigation

### I want to...

**Understand what's available**
→ Read [README.md](README.md) or [INDEX.json](INDEX.json)

**Get started quickly**
→ See [quick-reference.json](quick-reference.json)

**Build a Vim plugin**
→ Read [vim-plugin-guide.json](vim-plugin-guide.json)

**See code examples**
→ Check [integration-examples.json](integration-examples.json)

**Use shell commands**
→ Reference [shell-commands.json](shell-commands.json)

**Use Python API**
→ See [python-query-db.json](python-query-db.json) and related files

**Query the database directly**
→ Review [database-schema.json](database-schema.json)

**Understand data formats**
→ Check [data-formats.json](data-formats.json)

## Files Overview

| File | Purpose | Size |
|------|---------|------|
| README.md | Overview and quick start | 1.8 KB |
| INDEX.json | Complete file index | 1.2 KB |
| MANIFEST.md | File manifest and organization | 2.5 KB |
| shell-commands.json | All query.sh commands | 8.5 KB |
| python-query-db.json | Core query functions | 5.2 KB |
| python-quality-analyzer.json | Code metrics | 2.8 KB |
| python-query-headers.json | Header queries | 2.4 KB |
| python-metrics-extractor.json | Metrics extraction | 1.9 KB |
| python-incremental-generator.json | Incremental updates | 1.6 KB |
| python-db-conversion.json | Database conversion | 0.8 KB |
| data-formats.json | JSON schemas | 2.1 KB |
| database-schema.json | SQLite schemas | 2.9 KB |
| quick-reference.json | Quick reference | 1.2 KB |
| vim-plugin-guide.json | Vim integration | 3.5 KB |
| integration-examples.json | Code examples | 3.8 KB |

## Key Features Documented

### Query Types
- Function lookup and search (including resolved types)
- Dependency analysis
- Module queries
- Header/reference queries
- Type resolution and debugging
- Database management
- Multi-instance function resolution

### Interfaces
- **Shell**: `query.sh` commands (30+ commands)
- **Python**: Direct module imports (13+ functions)
- **Database**: Direct SQLite queries

### Metrics
- Lines of Code (LOC)
- Cyclomatic Complexity
- Variable Count
- Parameter Count
- Return Count
- Call Depth

### Type Resolution (v2.1.0)
- LIKE reference resolution (parameters and return types)
- Multi-instance function disambiguation
- Unresolved types debugging with filtering
- Data quality validation
- Empty parameter filtering
- Automatic schema detection
- Resolved types merged into workspace.db

### Integration Patterns
- Shell-based integration
- Python-based integration
- Database-based integration
- Vim plugin integration

## Getting Started

### 1. Setup (5 minutes)
```bash
# Generate metadata
bash generate_signatures.sh /path/to/codebase
bash generate_modules.sh /path/to/codebase

# Create databases
bash query.sh create-dbs
```

### 2. Test (1 minute)
```bash
# Try a query
query.sh find-function test_function
```

### 3. Integrate (depends on your tool)
- See [integration-examples.json](integration-examples.json) for code samples
- See [vim-plugin-guide.json](vim-plugin-guide.json) for Vim-specific guidance

## Documentation Format

All documentation is in **JSON format** for easy parsing:
- Consistent structure
- No external dependencies
- Machine-readable
- Human-readable with indentation

## Performance

- Exact function lookup: **<1ms**
- Pattern search: **<10ms**
- Database creation: **<5s**
- Metrics extraction: **<1ms per function**

## What's Documented

✅ 30+ shell commands
✅ 13+ Python functions
✅ 7 Python classes
✅ Complete database schemas
✅ All data formats
✅ Integration patterns
✅ Code examples
✅ Performance characteristics
✅ Error handling
✅ Vim plugin guidance

## Next Steps

1. **For quick overview**: Read [README.md](README.md)
2. **For specific queries**: Check [shell-commands.json](shell-commands.json)
3. **For Python integration**: See [python-query-db.json](python-query-db.json)
4. **For Vim plugin**: Read [vim-plugin-guide.json](vim-plugin-guide.json)
5. **For code examples**: Check [integration-examples.json](integration-examples.json)

## Questions?

- Check [quick-reference.json](quick-reference.json) for common tasks
- See [integration-examples.json](integration-examples.json) for code samples
- Review [vim-plugin-guide.json](vim-plugin-guide.json) for Vim-specific help
- Check [database-schema.json](database-schema.json) for SQL queries

---

**Ready to integrate?** Start with [README.md](README.md) or jump to [integration-examples.json](integration-examples.json) for code samples.
