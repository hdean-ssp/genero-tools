# Genero-Tools Development Roadmap

## Current State (March 2026)

### ✅ Completed Features

**Core Functionality:**
- Function signature extraction from .4gl files
- Module dependency parsing from .m3 files
- Call graph analysis (who calls whom)
- File header parsing (code references, authors)
- SQLite database for fast querying
- Shell query interface (query.sh)
- Python API for programmatic access

**Recent Enhancements:**
- Reference search with partial matching (100512 → EH100512, EH100512-9a)
- Automatic schema detection and type resolution
- LIKE type reference resolution to database schema types
- Code quality metrics (complexity, LOC, parameters)
- Type-aware function signatures
- **Type Resolution Improvements v2.1.0** (NEW):
  - Empty parameter filtering for data quality
  - LIKE reference resolution for both parameters and return types
  - Multi-instance function resolution with file_path disambiguation
  - Unresolved types debugging and query commands
  - Data consistency validation and reporting

**Documentation:**
- LSP integration guides (comprehensive and summary)
- Reference search guide
- Schema resolution implementation guide
- API documentation

---

## Planned Enhancements (Next 6 Weeks)

### Phase 1: Performance & Scale (Weeks 1-2)

**Goal:** 10x faster, handle 6M+ LOC codebases

1. **Batch Queries**
   - Execute multiple queries in single invocation
   - Single DB connection, atomic transactions
   - Use case: Hover info (def + deps + dependents)

2. **Pagination Support**
   - Add --limit, --offset, --total-count parameters
   - Memory efficient for large result sets
   - Use case: Search results pagination

3. **Relationship Queries**
   - `find-dependents-in-module` - Find callers in module
   - `find-call-chain` - Find call path between functions
   - `find-common-callers` - Find functions calling all specified

4. **Error Handling**
   - Structured error codes
   - Helpful error messages
   - Database validation

**Deliverable:** 10x faster, handles large codebases

---

### Phase 2: Code Quality & Search (Weeks 3-4)

**Goal:** Enable code quality analysis and advanced search

1. **Metrics Exposure**
   - `function-metrics` - Complexity, LOC, parameters, etc.
   - `module-metrics` - Function count, avg complexity, coupling
   - `find-complex-functions` - Find functions exceeding threshold
   - `find-high-coupling` - Find high-coupling functions

2. **Advanced Search**
   - Multi-criteria filtering
   - Combine author, reference, complexity, module, file
   - Use case: "Find all functions modified by John for PRB tickets"

3. **Cache Invalidation**
   - `get-cache-info` - Cache metadata
   - `invalidate-cache` - Selective cache invalidation
   - Smart caching for IDE operations

**Deliverable:** Code quality analysis, powerful search

---

### Phase 3: Analysis & Visualization (Weeks 5-6)

**Goal:** Enable analysis tools and visualization

1. **Diff/Change Detection**
   - `diff-functions` - Compare function signatures
   - `diff-file` - Get modified functions in file
   - Note: SVN integration handled separately

2. **Export/Report Generation**
   - `export-call-graph` - Export as dot, json, csv, html
   - `generate-report` - Quality, complexity, coverage, dependencies
   - Use case: Generate reports for team

**Deliverable:** Analysis tools, visualization

---

## Integration Points

### Vim Plugin (genero-vim)
- Uses batch queries for hover info
- Uses pagination for search results
- Uses metrics for code quality highlighting
- Uses advanced search for powerful filtering

### LSP Server (Future)
- Uses batch queries for hover/definition
- Uses metrics for diagnostics
- Uses relationship queries for navigation
- Uses advanced search for workspace symbols

### IDE Extensions (Future)
- VS Code, Neovim, Emacs
- All leverage same API enhancements

---

## Architecture Evolution

### Current (March 2026)
```
CLI (query.sh) → Python Scripts → SQLite DB
```

### After Phase 1
```
CLI (query.sh) → Python Scripts → SQLite DB
                 ↓
            Batch Query Handler
            Pagination Handler
            Relationship Query Handler
```

### After Phase 2
```
CLI (query.sh) → Python Scripts → SQLite DB
                 ↓
            Query Handlers (batch, pagination, relationships)
            Metrics Exposure
            Advanced Search
            Cache Manager
```

### After Phase 3
```
CLI (query.sh) → Python Scripts → SQLite DB
                 ↓
            Query Handlers
            Metrics & Analysis
            Export/Report Generator
            Diff/Change Detector
```

---

## Success Metrics

### Phase 1
- ✅ Batch queries: 10x faster than sequential
- ✅ Pagination: Handle 6M+ LOC without memory issues
- ✅ Relationships: Complex queries working
- ✅ Errors: Structured error codes

### Phase 2
- ✅ Metrics: All quality metrics exposed
- ✅ Search: Multi-criteria filtering working
- ✅ Cache: Smart invalidation implemented

### Phase 3
- ✅ Diff: Change detection working
- ✅ Reports: HTML reports generating

---

## Backward Compatibility

✅ All existing commands continue to work
✅ New parameters are optional
✅ Default behavior unchanged
✅ No breaking changes

---

## Technology Stack

**Current:**
- Bash (shell scripts)
- Python 3.6+ (core logic)
- SQLite (database)
- JSON (data format)

**Planned:**
- Same stack (no new dependencies)
- Optional: Graphviz for visualization
- Optional: Jinja2 for report templates

---

## Team & Responsibilities

**Genero-Tools Team:**
- Implement API enhancements
- Maintain backward compatibility
- Provide documentation
- Support vim plugin integration

**Vim Plugin Team:**
- Test enhancements
- Provide feedback
- Implement plugin features
- Report issues

---

## Key Decisions

1. **Batch Queries:** Sequential execution (simpler) vs parallel (faster)
   - Recommendation: Start with sequential, add parallel if needed

2. **Pagination:** Default or opt-in?
   - Recommendation: Opt-in with --limit/--offset flags

3. **Metrics:** Store in DB or calculate on-demand?
   - Recommendation: Store in DB (already done for complexity)

4. **Cache:** In-memory or file-based?
   - Recommendation: File-based for persistence

---

## Risk Mitigation

**Risk:** Breaking existing workflows
**Mitigation:** All new features are additive, no changes to existing commands

**Risk:** Performance degradation
**Mitigation:** Batch queries reduce overhead, pagination handles scale

**Risk:** Database bloat
**Mitigation:** Metrics already calculated, just need exposure

**Risk:** Complexity explosion
**Mitigation:** Phased approach, test each phase thoroughly

---

## Next Steps

1. **Review** this roadmap with stakeholders
2. **Prioritize** Phase 1 features
3. **Design** batch query API
4. **Implement** Phase 1 (2 weeks)
5. **Test** with vim plugin
6. **Iterate** based on feedback
7. **Continue** with Phase 2 and 3

---

## Related Documentation

- `VIM_PLUGIN_INTEGRATION_RESPONSE.md` - Response to vim plugin suggestions
- `API_ENHANCEMENT_IMPLEMENTATION_PLAN.md` - Detailed implementation plan
- `LSP_INTEGRATION_COMPREHENSIVE.md` - LSP integration guide
- `SCHEMA_RESOLUTION_IMPLEMENTATION.md` - Schema resolution details
- `REFERENCE_SEARCH_GUIDE.md` - Reference search documentation

---

## Questions & Feedback

**For Vim Plugin Team:**
1. Which Phase 1 features are most critical?
2. What's the typical query pattern?
3. How many queries per operation?
4. What's acceptable latency?

**For Stakeholders:**
1. Should we prioritize performance or features?
2. Are there other use cases we should consider?
3. What's the timeline for LSP integration?
4. Should we support other editors?

