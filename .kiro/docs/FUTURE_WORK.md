# Future Work - genero-tools

**Date:** March 23, 2026  
**Version:** 2.1.0  
**Status:** Consolidated from documentation review

---

## Overview

This document consolidates all noted improvements, future tasks, bugs, and enhancements identified in genero-tools documentation. Items are organized by priority and effort level.

---

## Phase 3: Query Layer Enhancements (Priority 1 - High Value)

### 3.1 Find References / Find Usages
**Status:** ✅ IMPLEMENTED  
**Priority:** High  
**Effort:** Complete  
**Impact:** Essential for refactoring workflows

**Description:**
Query layer to find all functions that call a given function. This is critical for impact analysis and safe refactoring.

**Implementation:**
```bash
bash query.sh find-function-dependents "function_name"
```

**Output:**
```json
{
  "function": "process_contract",
  "dependents": [
    {
      "file": "src/main.4gl",
      "line": 42,
      "caller": "main_handler"
    }
  ],
  "total_dependents": 2
}
```

**Status:** Already implemented via `find-function-dependents` command  
**Documentation:** Documented in docs/QUERYING.md and docs/api/shell-commands.json

---

### 3.2 Call Hierarchy / Call Graph Traversal
**Status:** ✅ IMPLEMENTED  
**Priority:** High  
**Effort:** Complete  
**Impact:** Enables code flow understanding

**Description:**
Call graph data is already extracted and available. Functions identify what they call (callees) and what calls them (callers).

**Implementation:**
```bash
bash query.sh find-function-dependencies "function_name"    # What it calls
bash query.sh find-function-dependents "function_name"      # What calls it
```

**Output:**
```json
{
  "function": "main_handler",
  "dependencies": [
    {
      "name": "validate_input",
      "file": "src/validation.4gl",
      "line": 10
    }
  ]
}
```

**Status:** Already implemented via existing call graph extraction  
**Documentation:** Documented in docs/QUERYING.md and docs/api/shell-commands.json

---

### 3.3 Code Search with Pattern Matching
**Status:** ❌ NOT NEEDED  
**Priority:** Low  
**Effort:** N/A  
**Impact:** Developers use grep for code search

**Description:**
Code search with pattern matching is not a priority. Developers already use standard tools like `grep` for searching code patterns across the codebase.

**Rationale:**
- Developers are familiar with grep and other standard tools
- genero-tools focuses on metadata extraction, not text search
- Text search is better handled by existing tools
- Out of scope for this project

**Status:** Removed from roadmap

---

### 3.4 Code Statistics / Metrics Summary
**Status:** 🔄 LOW PRIORITY  
**Priority:** Low  
**Effort:** 1 day  
**Impact:** Nice-to-have for project health overview

**Description:**
Aggregate metrics queries to provide project-wide and file-level statistics. Could be useful but not high priority.

**Proposed Implementation:**
```bash
bash query.sh statistics
bash query.sh file-statistics "src/main.4gl"
bash query.sh function-statistics "process_contract"
```

**Expected Output:**
```json
{
  "project_statistics": {
    "total_files": 42,
    "total_functions": 156,
    "total_lines_of_code": 45230,
    "average_function_size": 290,
    "average_complexity": 3.2,
    "functions_with_high_complexity": 12
  }
}
```

**Dependencies:** Existing metrics data  
**Tests Required:** Unit tests  
**Documentation:** Shell commands, Python API, examples  
**Status:** Deferred - implement if time permits

---

## Phase 3b: Type Resolution Enhancements (Priority 2)

### 3b.1 Type-Aware Queries
**Status:** Type resolution implemented, queries not yet built  
**Priority:** High  
**Effort:** 1-2 days  
**Impact:** Enables type-based analysis

**Description:**
Query layer for type-resolved data to find functions working with specific types.

**Proposed Implementation:**
```bash
bash query.sh functions-using-table "contract"
bash query.sh functions-with-type "LIKE account.*"
bash query.sh type-mismatches
```

**Expected Output:**
```json
{
  "table": "contract",
  "functions": [
    {
      "name": "process_contract",
      "file": "src/processing.4gl",
      "line": 45,
      "parameter": "c",
      "resolved_columns": ["id", "name", "amount"]
    }
  ]
}
```

**Dependencies:** Phase 1c (type resolution) - already complete  
**Tests Required:** Unit tests, integration tests  
**Documentation:** Shell commands, Python API, examples

---

### 3b.2 SQL DDL Schema Parsing
**Status:** Not implemented  
**Priority:** Medium  
**Effort:** 2-3 days  
**Impact:** Extends schema support beyond Informix

**Description:**
Add support for SQL DDL schema files in addition to Informix IDS `.sch` format.

**Current Limitation:**
- Only supports Informix IDS `.sch` format
- SQL DDL support planned for future release

**Proposed Implementation:**
- Parse standard SQL CREATE TABLE statements
- Support multiple SQL dialects (PostgreSQL, MySQL, SQL Server)
- Maintain backward compatibility with existing `.sch` parsing

**Tests Required:** Unit tests for each SQL dialect  
**Documentation:** Schema format guide, examples

---

### 3b.3 Multiple Schema File Support
**Status:** Not implemented  
**Priority:** Medium  
**Effort:** 1-2 days  
**Impact:** Supports complex multi-schema projects

**Description:**
Support multiple schema files per workspace instead of single schema file.

**Current Limitation:**
- Single schema file per workspace
- Multiple schema files planned for future release

**Proposed Implementation:**
- Auto-detect multiple `.sch` files in directory
- Merge schema data from multiple files
- Handle schema conflicts and overlaps

**Tests Required:** Unit tests, integration tests  
**Documentation:** Multi-schema guide, examples

---

### 3b.4 RECORD and ARRAY Type Resolution
**Status:** Not implemented  
**Priority:** Medium  
**Effort:** 2-3 days  
**Impact:** Comprehensive type support

**Description:**
Extend type resolution to handle RECORD and ARRAY types in addition to LIKE references.

**Current Limitation:**
- Only resolves LIKE references
- Other type references (RECORD, ARRAY) not resolved
- Planned for future enhancement

**Proposed Implementation:**
- Parse RECORD type definitions
- Resolve ARRAY element types
- Store resolved type information in database

**Tests Required:** Unit tests, integration tests  
**Documentation:** Type resolution guide update

---

## Phase 4: Performance & Optimization (Priority 2)

### 4.1 Incremental Compilation Support
**Status:** Not implemented  
**Priority:** Medium  
**Effort:** 1-2 days  
**Impact:** Faster compilation for large projects

**Description:**
Track file modification times and compile only changed files.

**Proposed Implementation:**
- Store file modification timestamps
- Compare with current timestamps
- Compile only modified files
- Update database incrementally

**Tests Required:** Integration tests  
**Documentation:** Incremental compilation guide

---

### 4.2 Parallel Query Execution
**Status:** Not implemented  
**Priority:** Medium  
**Effort:** 1-2 days  
**Impact:** Faster multi-query operations

**Description:**
Execute independent queries in parallel for better performance.

**Proposed Implementation:**
- Identify independent queries in batch operations
- Execute in parallel using thread pool
- Aggregate results
- Maintain result ordering

**Tests Required:** Performance tests, integration tests  
**Documentation:** Batch query guide update

---

### 4.3 Intelligent Cache Invalidation
**Status:** Not implemented  
**Priority:** Low  
**Effort:** 1-2 days  
**Impact:** Reduce cache misses

**Description:**
Track file dependencies and invalidate only affected cache entries.

**Current Limitation:**
- No intelligent cache invalidation
- All cache invalidated on any change

**Proposed Implementation:**
- Track file dependencies
- Invalidate only affected cache entries
- Reduce cache misses

**Tests Required:** Unit tests  
**Documentation:** Caching guide update

---

### 4.4 Persistent Cache
**Status:** Not implemented  
**Priority:** Low  
**Effort:** 1 day  
**Impact:** Faster startup

**Description:**
Save cache to disk between sessions.

**Proposed Implementation:**
- Serialize cache to disk
- Load cache on startup
- Validate cache freshness

**Tests Required:** Unit tests  
**Documentation:** Caching guide update

---

## Phase 5: IDE Integration (Priority 3)

### 5.1 LSP Server Implementation
**Status:** Not implemented  
**Priority:** Medium  
**Effort:** 3-5 days  
**Impact:** IDE-agnostic integration

**Description:**
Implement Language Server Protocol (LSP) server for genero-tools.

**Benefits:**
- IDE-agnostic support
- Standard protocol support
- Works with any LSP-compatible editor

**Proposed Implementation:**
- Implement LSP server wrapper
- Map genero-tools queries to LSP methods
- Support hover, completion, go-to-definition, find-references

**Tests Required:** Integration tests with LSP clients  
**Documentation:** LSP integration guide

---

### 5.2 Vim Plugin Integration
**Status:** Partially documented  
**Priority:** Medium  
**Effort:** 2-3 days  
**Impact:** Vim editor integration

**Description:**
Create Vim plugin that uses genero-tools for code analysis.

**Features:**
- Hover information with function signatures
- Code completion
- Go-to-definition
- Find references
- Code metrics display

**Tests Required:** Manual testing in Vim  
**Documentation:** Vim plugin guide

---

### 5.3 VS Code Extension
**Status:** Not implemented  
**Priority:** Medium  
**Effort:** 2-3 days  
**Impact:** VS Code editor integration

**Description:**
Create VS Code extension that uses genero-tools for code analysis.

**Features:**
- Code lens showing complexity and call count
- Hover information with full signature
- Go-to-definition navigation
- Find references
- Code metrics in sidebar

**Tests Required:** Manual testing in VS Code  
**Documentation:** VS Code extension guide

---

## Known Limitations & Bugs

### Type Resolution Limitations

1. **Schema Format Support**
   - **Current:** Only Informix IDS `.sch` format
   - **Limitation:** Cannot parse SQL DDL schemas
   - **Fix:** Implement SQL DDL parser (Phase 3b.2)

2. **Type Resolution Scope**
   - **Current:** Only LIKE references resolved
   - **Limitation:** RECORD and ARRAY types not resolved
   - **Fix:** Extend type resolution (Phase 3b.4)

3. **Multi-File Schema**
   - **Current:** Single schema file per workspace
   - **Limitation:** Cannot handle multi-schema projects
   - **Fix:** Implement multiple schema support (Phase 3b.3)

### Query Layer Limitations

1. **No Reference Finding**
   - **Current:** Cannot find all references to a function
   - **Limitation:** Impacts refactoring workflows
   - **Fix:** Implement find-references (Phase 3.1)

2. **No Code Search**
   - **Current:** Cannot search codebase with patterns
   - **Limitation:** Limits code exploration
   - **Fix:** Implement code search (Phase 3.3)

3. **No Statistics API**
   - **Current:** Metrics extracted but no summary API
   - **Limitation:** Cannot get project-wide statistics
   - **Fix:** Implement statistics queries (Phase 3.4)

### Performance Limitations

1. **No Incremental Compilation**
   - **Current:** Full recompilation required
   - **Limitation:** Slow for large projects
   - **Fix:** Implement incremental compilation (Phase 4.1)

2. **No Parallel Queries**
   - **Current:** Queries executed sequentially
   - **Limitation:** Slow for batch operations
   - **Fix:** Implement parallel execution (Phase 4.2)

---

## Implementation Roadmap

### Recommended Order

1. ~~**Phase 3.1** - Find References (2-3 days)~~ ✅ IMPLEMENTED
2. ~~**Phase 3.2** - Call Hierarchy (2-3 days)~~ ✅ IMPLEMENTED
3. ~~**Phase 3.3** - Code Search (1-2 days)~~ ❌ NOT NEEDED (use grep)
4. **Phase 3.4** - Statistics (1 day) - LOW PRIORITY
5. **Phase 3b.1** - Type-Aware Queries (1-2 days) - Leverages Phase 1
6. **Phase 3b.2** - SQL DDL Parsing (2-3 days) - Schema support
7. **Phase 3b.3** - Multiple Schemas (1-2 days) - Complex projects
8. **Phase 3b.4** - RECORD/ARRAY Types (2-3 days) - Complete types
9. **Phase 4.1** - Incremental Compilation (1-2 days) - Performance
10. **Phase 4.2** - Parallel Queries (1-2 days) - Performance
11. **Phase 5.1** - LSP Server (3-5 days) - IDE integration
12. **Phase 5.2** - Vim Plugin (2-3 days) - Vim integration
13. **Phase 5.3** - VS Code Extension (2-3 days) - VS Code integration

**Total Estimated Effort:** 18-28 days (reduced from 25-35 days)

---

## Success Criteria

For each new feature:
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

## Summary

**Total Unimplemented Features:** 13  
**Total Known Limitations:** 6  
**Estimated Total Effort:** 25-35 days  
**Expected Outcome:** Comprehensive codebase analysis platform with IDE integration

**Next Steps:**
1. Start with Phase 3.1 (Find References)
2. Follow recommended implementation order
3. Maintain backward compatibility
4. Keep documentation current
5. Ensure comprehensive testing

---

## Notes

- All features maintain backward compatibility
- No breaking changes to existing APIs
- Performance targets: <100ms for typical queries
- Test coverage target: >90%
- Documentation required for all features

