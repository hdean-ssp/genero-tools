# Developer Handoff Guide

**Date:** March 24, 2026  
**Project:** genero-tools v2.1.0  
**Status:** Ready for Implementation  
**Contact:** See project documentation

---

## What You're Taking Over

genero-tools is a comprehensive codebase analysis tool for Genero/4GL that extracts and indexes metadata to enable IDE integration, AI-powered code review, and developer tooling.

**Current Status:**
- ✅ Phase 1 Complete: Core signature and module extraction
- ✅ Phase 2 Complete: Code quality metrics, type resolution, batch queries, pagination
- 🔄 Phase 3 In Progress: IDE/editor integration, advanced tooling

**Current Version:** 2.1.0 (Type Resolution v2.1.0 - Complete)

---

## What's Implemented

### Core Features (Phase 1 & 2)
- Function signature extraction from .4gl files
- Module dependency parsing from .m3 files
- Call graph analysis (what calls what)
- File header parsing (code references, authors)
- Code quality metrics (LOC, complexity, etc.)
- Type resolution (LIKE references to schema types)
- Multi-instance function disambiguation
- SQLite database for efficient querying
- Batch query support with pagination

### Query Commands (30+)
```bash
# Function queries
bash query.sh find-function "my_function"
bash query.sh search-functions "get_*"
bash query.sh find-function-resolved "my_function"
bash query.sh find-function-by-name-and-path "my_function" "./src/module.4gl"
bash query.sh find-all-function-instances "my_function"

# Dependency queries
bash query.sh find-function-dependencies "process_request"
bash query.sh find-function-dependents "log_message"

# Type resolution queries
bash query.sh unresolved-types
bash query.sh unresolved-types --filter missing_table
bash query.sh validate-types

# Code reference queries
bash query.sh find-reference "PRB-299"
bash query.sh find-author "Rich"
bash query.sh author-expertise "Chilly"
```

### Python API (13+ functions)
```python
from scripts.query_db import find_function, find_function_resolved
from scripts.quality_analyzer import QualityAnalyzer

results = find_function('workspace.db', 'my_function')
resolved = find_function_resolved('workspace.db', 'my_function')
qa = QualityAnalyzer('workspace.db')
complex_funcs = qa.find_complex_functions(threshold=10)
```

---

## What's Next (Your Roadmap)

### 10 Features to Implement (18-28 days)

**Phase 1: Type Resolution Enhancements (8-12 days)**
1. Type-Aware Queries (1-2 days) - Find functions using specific tables
2. SQL DDL Schema Parsing (2-3 days) - Support PostgreSQL, MySQL, SQL Server
3. Multiple Schema Files (1-2 days) - Support multiple schemas per workspace
4. RECORD/ARRAY Types (2-3 days) - Extend type resolution beyond LIKE

**Phase 2: Performance & Optimization (4-7 days)**
5. Incremental Compilation (1-2 days) - Compile only changed files
6. Parallel Query Execution (1-2 days) - Execute queries in parallel
7. Intelligent Cache (1-2 days) - Selective cache invalidation
8. Persistent Cache (1 day) - Save cache to disk

**Phase 3: IDE Integration (7-11 days)**
9. LSP Server (3-5 days) - Language Server Protocol implementation
10. Vim Plugin (2-3 days) - Vim editor integration
11. VS Code Extension (2-3 days) - VS Code editor integration

**See:** IMPLEMENTATION_ROADMAP.md for complete details

---

## Project Structure

```
genero-tools/
├── src/                          # Shell scripts for generation
│   ├── generate_signatures.sh     # Extract function signatures
│   ├── generate_modules.sh        # Parse module dependencies
│   ├── generate_codebase_index.sh # Merge signatures and modules
│   └── query.sh                   # Query wrapper script
│
├── scripts/                       # Python utility scripts
│   ├── query_db.py               # Query interface
│   ├── quality_analyzer.py       # Code metrics analysis
│   ├── parse_schema.py           # Schema parsing
│   ├── resolve_types.py          # Type resolution
│   ├── metrics_extractor.py      # Metrics extraction
│   └── ... (20+ other scripts)
│
├── tests/                         # Test suite
│   ├── run_all_tests.sh          # Run all tests
│   ├── test_*.py                 # Python tests
│   └── sample_codebase/          # Test data
│
├── docs/                          # User documentation
│   ├── FEATURES.md               # Feature overview
│   ├── QUERYING.md               # Query reference
│   ├── TYPE_RESOLUTION_GUIDE.md  # Type resolution
│   ├── ARCHITECTURE.md           # System design
│   ├── DEVELOPER_GUIDE.md        # Development workflow
│   └── api/                      # API documentation (15 JSON files)
│
├── README.md                      # Main entry point
├── generate_all.sh               # Main orchestration script
├── query.sh                       # Query interface
└── LICENSE                        # License file
```

---

## Key Technologies

- **Bash** - Main orchestration and text processing
- **AWK/sed** - High-performance text parsing
- **Python 3.6+** - JSON processing, database operations
- **SQLite 3** - Indexed database for efficient querying
- **Standard Unix utilities** - find, sed, awk, date, grep

**No external dependencies** - Everything uses built-in tools and standard library

---

## Development Workflow

### 1. Setup Development Environment
```bash
# Clone repository
git clone <repo>
cd genero-tools

# Verify tests pass
bash tests/run_all_tests.sh

# Generate sample metadata
bash generate_all.sh tests/sample_codebase
```

### 2. Implement a Feature
```bash
# Create test data in tests/sample_codebase/
# Create test file in tests/test_*.py or tests/test_*.sh
# Implement feature in appropriate script
# Run tests
bash tests/run_all_tests.sh
# Update documentation
```

### 3. Testing Requirements
- Unit tests for each function
- Integration tests for workflows
- Performance tests for queries
- Target: >90% code coverage
- All queries must execute in <100ms

### 4. Documentation Requirements
- Shell command documentation
- Python API documentation
- Code examples
- Use case descriptions
- Troubleshooting guide

---

## Important Files to Know

### Documentation
- **README.md** - Start here for overview
- **docs/FEATURES.md** - Complete feature list
- **docs/QUERYING.md** - Query reference
- **docs/TYPE_RESOLUTION_GUIDE.md** - Type resolution system
- **docs/ARCHITECTURE.md** - System design
- **docs/DEVELOPER_GUIDE.md** - Development workflow

### Roadmap
- **IMPLEMENTATION_ROADMAP.md** - Complete roadmap with details
- **ROADMAP_QUICK_REFERENCE.md** - Quick reference card
- **FUTURE_WORK.md** - Detailed feature descriptions
- **FUTURE_WORK_SUMMARY.md** - Quick summary

### Status
- **DOCUMENTATION_STATUS.md** - Documentation verification
- **CLEANUP_COMPLETE.md** - Repository cleanup summary
- **FUTURE_WORK_CORRECTIONS.md** - Status updates

---

## Performance Targets

All features must meet these targets:

| Operation | Target |
|-----------|--------|
| Exact function lookup | <1ms |
| Pattern search | <10ms |
| Type resolution query | <1ms |
| Database creation | <5s |
| Metrics extraction | <1ms per function |

---

## Testing Strategy

### Unit Tests
- Test each function independently
- Test edge cases and error conditions
- Test with various input sizes
- Target: >90% code coverage

### Integration Tests
- Test end-to-end workflows
- Test with real codebases
- Test performance with large datasets
- Test backward compatibility

### Performance Tests
- Benchmark query execution time
- Measure memory usage
- Test with 6M+ LOC codebases
- Verify <100ms query time

### Run Tests
```bash
# Run all tests
bash tests/run_all_tests.sh

# Run specific test suite
bash tests/run_tests.sh                    # Signature generation
bash tests/run_module_tests.sh             # Module generation
python3 tests/test_quality_analyzer.py     # Quality analyzer
```

---

## Code Quality Standards

- **Backward Compatibility:** All features must maintain backward compatibility with v2.1.0
- **Performance:** All queries must execute in <100ms for typical codebases
- **Testing:** Comprehensive testing (>90% coverage) required for all features
- **Documentation:** Each feature must be documented with examples
- **Error Handling:** Graceful error handling with informative messages
- **Code Style:** Follow existing code patterns and conventions

---

## Common Tasks

### Add a New Query Command
1. Create Python function in `scripts/query_db.py`
2. Add shell wrapper in `src/query.sh`
3. Add tests in `tests/test_query_db.py`
4. Document in `docs/api/shell-commands.json`
5. Update `docs/QUERYING.md`

### Add a New Feature
1. Create test data in `tests/sample_codebase/`
2. Create test file in `tests/test_*.py`
3. Implement feature in appropriate script
4. Run full test suite: `bash tests/run_all_tests.sh`
5. Update documentation

### Debug an Issue
1. Check test output: `bash tests/run_all_tests.sh`
2. Review error messages
3. Check intermediate files (workspace.json, modules.json)
4. Use Python debugger if needed
5. Add test case to prevent regression

---

## Useful Commands

```bash
# Generate metadata
bash generate_all.sh /path/to/codebase

# Create databases
bash query.sh create-dbs

# Query functions
bash query.sh find-function "my_function"

# Run tests
bash tests/run_all_tests.sh

# Check test coverage
python3 -m pytest tests/ --cov=scripts

# View database schema
sqlite3 workspace.db ".schema"

# Query database directly
sqlite3 workspace.db "SELECT * FROM functions LIMIT 5"
```

---

## Getting Help

### Documentation
1. **README.md** - Project overview
2. **docs/FEATURES.md** - Feature list
3. **docs/QUERYING.md** - Query reference
4. **docs/ARCHITECTURE.md** - System design
5. **docs/DEVELOPER_GUIDE.md** - Development workflow

### Roadmap
1. **IMPLEMENTATION_ROADMAP.md** - Complete roadmap
2. **ROADMAP_QUICK_REFERENCE.md** - Quick reference
3. **FUTURE_WORK.md** - Feature details

### Code
1. Review existing scripts for patterns
2. Check test files for examples
3. Look at docs/api/ for API documentation

---

## Next Steps

1. **Read** IMPLEMENTATION_ROADMAP.md for complete details
2. **Start** with Feature 1.1 (Type-Aware Queries)
3. **Follow** implementation order
4. **Maintain** backward compatibility
5. **Keep** documentation current
6. **Ensure** >90% test coverage

---

## Success Criteria

Your implementation is successful when:
- ✅ All 10 features are implemented
- ✅ All features pass comprehensive tests (>90% coverage)
- ✅ All queries execute in <100ms
- ✅ All features are documented with examples
- ✅ No breaking changes to existing queries
- ✅ Backward compatible with v2.1.0
- ✅ Code follows existing patterns and conventions

---

## Contact & Support

For questions:
1. Review project documentation
2. Check existing code for patterns
3. Review test files for examples
4. Consult DEVELOPER_GUIDE.md for workflow

---

**Good luck! You've got this.** 🚀

The codebase is well-organized, well-tested, and well-documented. Follow the roadmap, maintain the quality standards, and you'll deliver great features.

---

**Status:** Ready for Implementation  
**Last Updated:** March 24, 2026  
**Version:** 2.1.0

