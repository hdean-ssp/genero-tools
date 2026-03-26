# Future Work Summary

**Date:** March 23, 2026  
**Status:** Consolidated and Ready for Implementation

---

## Quick Reference

### What's Documented

A comprehensive **FUTURE_WORK.md** document has been created that consolidates all noted improvements, future tasks, and bugs from genero-tools documentation.

**Status Update:**
- Phase 3.1 (Find References) - ✅ Already implemented via `find-function-dependents`
- Phase 3.2 (Call Hierarchy) - ✅ Already implemented via call graph extraction
- Phase 3.3 (Code Search) - ❌ Not needed (developers use grep)
- Phase 3.4 (Statistics) - 🔄 Low priority (implement if time permits)

### Key Statistics

- **10 Unimplemented Features** across 4 phases (down from 13)
- **6 Known Limitations** identified
- **18-28 Days** total estimated effort (down from 25-35 days)
- **3 Priority Levels** (High, Medium, Low)

### Quick Start

**To begin implementation:**
1. Read `FUTURE_WORK.md` for complete details
2. Start with Phase 3.1 (Find References) - highest value
3. Follow recommended implementation order
4. Each feature includes effort estimate, dependencies, and success criteria

---

## High-Priority Features (Start Here)

### Phase 3: Query Layer Enhancements

1. **Find References** ✅ **IMPLEMENTED**
   - Find all functions that call a given function
   - Use: `bash query.sh find-function-dependents "function_name"`
   - Essential for refactoring workflows

2. **Call Hierarchy** ✅ **IMPLEMENTED**
   - Call graph data already extracted
   - Use: `bash query.sh find-function-dependencies` and `find-function-dependents`
   - Understand code flow

3. **Code Search** ❌ **NOT NEEDED**
   - Developers use grep for code search
   - Out of scope - genero-tools focuses on metadata
   - Better handled by existing tools

4. **Statistics API** 🔄 **LOW PRIORITY**
   - Project-wide metrics summary (optional)
   - File and function statistics
   - Uses existing metrics data
   - Implement if time permits

---

## Medium-Priority Features

### Phase 3b: Type Resolution Enhancements (8-12 days)

1. **Type-Aware Queries** (1-2 days)
   - Find functions using specific tables
   - Query by data type
   - Leverages completed Phase 1c

2. **SQL DDL Schema Parsing** (2-3 days)
   - Support SQL DDL in addition to Informix IDS
   - Multiple SQL dialects
   - Extends schema support

3. **Multiple Schema Files** (1-2 days)
   - Support multiple schemas per workspace
   - Handle schema conflicts
   - Supports complex projects

4. **RECORD/ARRAY Types** (2-3 days)
   - Extend type resolution beyond LIKE
   - Complete type support
   - Comprehensive type handling

### Phase 4: Performance & Optimization (4-7 days)

1. **Incremental Compilation** (1-2 days)
   - Track file changes
   - Compile only modified files
   - Faster for large projects

2. **Parallel Queries** (1-2 days)
   - Execute independent queries in parallel
   - Faster batch operations
   - Better resource utilization

3. **Intelligent Cache** (1-2 days)
   - Track file dependencies
   - Invalidate only affected cache
   - Reduce cache misses

4. **Persistent Cache** (1 day)
   - Save cache to disk
   - Faster startup
   - Session persistence

---

## IDE Integration Features

### Phase 5: IDE Integration (7-11 days)

1. **LSP Server** (3-5 days)
   - Language Server Protocol implementation
   - IDE-agnostic support
   - Works with any LSP-compatible editor

2. **Vim Plugin** (2-3 days)
   - Vim editor integration
   - Hover information, completion, navigation
   - Refactoring support

3. **VS Code Extension** (2-3 days)
   - VS Code editor integration
   - Code lens, hover, navigation
   - Metrics display

---

## Known Limitations

### Type Resolution
- ❌ Only Informix IDS `.sch` format (SQL DDL planned)
- ❌ Only LIKE references (RECORD/ARRAY planned)
- ❌ Single schema file (multiple schemas planned)

### Query Layer
- ✅ Reference finding (Phase 3.1 - IMPLEMENTED via find-function-dependents)
- ✅ Call graph traversal (Phase 3.2 - IMPLEMENTED via call graph extraction)
- ❌ Code search (Phase 3.3 - NOT NEEDED, use grep)
- ❌ Statistics API (Phase 3.4 - LOW PRIORITY)

### Performance
- ❌ No incremental compilation (Phase 4.1)
- ❌ No parallel queries (Phase 4.2)

---

## Implementation Roadmap

### Recommended Order (10 Features)

**Phase 3: Type Resolution Enhancements (8-12 days)**
1. Type-Aware Queries (1-2 days)
2. SQL DDL Parsing (2-3 days)
3. Multiple Schemas (1-2 days)
4. RECORD/ARRAY Types (2-3 days)

**Phase 4: Performance & Optimization (4-7 days)**
5. Incremental Compilation (1-2 days)
6. Parallel Queries (1-2 days)
7. Intelligent Cache (1-2 days)
8. Persistent Cache (1 day)

**Phase 5: IDE Integration (7-11 days)**
9. LSP Server (3-5 days)
10. Vim Plugin (2-3 days)
11. VS Code Extension (2-3 days)

**Total: 18-28 days** (reduced from 25-35 days)

---

## Success Criteria

Each feature must meet:
- ✅ Query executes in <100ms for typical codebases
- ✅ Handles pagination for large result sets
- ✅ Returns consistent JSON format
- ✅ Includes comprehensive tests (>90% coverage)
- ✅ Documented with examples
- ✅ No breaking changes to existing queries

---

## Testing Requirements

### Unit Tests
- Test each query function independently
- Test edge cases and error conditions
- Test with various input sizes

### Integration Tests
- Test end-to-end workflows
- Test with real codebases
- Test performance with large datasets

### Performance Tests
- Benchmark query execution time
- Measure memory usage
- Test with 6M+ LOC codebases

---

## Documentation Requirements

For each new feature:
- Shell command documentation
- Python API documentation
- Code examples
- Use case descriptions
- Troubleshooting guide
- Performance characteristics

---

## Next Steps

1. **Review** `FUTURE_WORK.md` for complete details
2. **Start** with Phase 3.1 (Find References)
3. **Follow** recommended implementation order
4. **Maintain** backward compatibility
5. **Keep** documentation current
6. **Ensure** comprehensive testing

---

## Files

- **FUTURE_WORK.md** - Complete future work document (13 features, 6 limitations)
- **FUTURE_WORK_SUMMARY.md** - This file (quick reference)

---

## Summary

All noted improvements, future tasks, and bugs from genero-tools documentation have been consolidated into a single, actionable future work document. The document includes:

- ✅ 10 unimplemented features (down from 13)
- ✅ 6 known limitations
- ✅ Effort estimates for each feature
- ✅ Recommended implementation order
- ✅ Success criteria
- ✅ Testing requirements
- ✅ Documentation requirements

**Status:** Ready for implementation

**Next Priority:** Phase 3b - Type Resolution Enhancements (8-12 days)
- Type-Aware Queries
- SQL DDL Schema Parsing
- Multiple Schema File Support
- RECORD/ARRAY Type Resolution

