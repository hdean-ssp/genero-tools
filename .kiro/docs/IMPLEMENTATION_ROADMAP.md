# Implementation Roadmap - genero-tools

**Date:** March 24, 2026  
**Version:** 2.1.0  
**Status:** Consolidated from documentation review

---

## Overview

This document consolidates all noted improvements, future tasks, bugs, and enhancements identified in genero-tools documentation. Items are organized by priority and effort level.

---

## Priority 1: Vim Plugin Optimization & Type Resolution (10-14 days)

### 1.1 Refined Output for Vim Plugin
**Effort:** 1-2 days  
**Priority:** HIGH  
**Business Value:** Better Vim plugin integration with concise output  
**Dependencies:** Phase 2 (Type Resolution v2.1.0) - COMPLETE

**Description:**
Create refined output formats optimized for Vim plugin use. Easier to refine output in genero-tools than in plugin code.

**Implementation Tasks:**
1. Create `--format=vim` option for query commands
2. Implement concise signature format (function name + params + return type)
3. Create hover-friendly output format
4. Add completion-friendly output format
5. Implement filtering for plugin use cases
6. Add comprehensive tests
7. Document output formats

**Expected Output Formats:**
```bash
# Concise signature format
bash query.sh find-function "my_function" --format=vim
# Output: my_function(param1: INTEGER, param2: VARCHAR) -> DECIMAL

# Hover format
bash query.sh find-function "my_function" --format=vim-hover
# Output: function my_function(param1: INTEGER, param2: VARCHAR) -> DECIMAL
#         File: src/module.4gl:42
#         Complexity: 5, LOC: 23

# Completion format
bash query.sh search-functions "get_*" --format=vim-completion
# Output: [{"name": "get_account", "params": "id: INTEGER", "return": "RECORD"}]
```

**Success Criteria:**
- Concise output format for Vim
- Hover-friendly format
- Completion-friendly format
- Comprehensive tests pass
- Documented with examples

**Testing:**
- Unit tests for each format
- Integration tests with Vim plugin
- Performance tests

**Documentation:**
- Output format reference
- Vim plugin integration guide
- Code examples

---

### 1.2 Table Definition Queries for Plugin Use
**Effort:** 1-2 days  
**Priority:** HIGH  
**Business Value:** Enable hover over table names to see columns and types  
**Dependencies:** Phase 2 (Type Resolution v2.1.0) - COMPLETE

**Description:**
Return table definitions from schema for plugin use. Allow hovering over table names to see columns and types.

**Implementation Tasks:**
1. Create `get-table-definition` query command
2. Create `get-table-columns` query command
3. Create `get-column-type` query command
4. Implement schema lookup by table name
5. Add refined output format for plugin use
6. Add comprehensive tests
7. Document table queries

**Expected Queries:**
```bash
bash query.sh get-table-definition "contract"
# Output: table contract with columns [id, name, amount, created_date]

bash query.sh get-table-columns "contract"
# Output: [{"name": "id", "type": "INTEGER"}, {"name": "name", "type": "VARCHAR(100)"}]

bash query.sh get-column-type "contract" "amount"
# Output: DECIMAL(10,2)
```

**Success Criteria:**
- Returns table definitions correctly
- Returns column information with types
- Handles missing tables gracefully
- Comprehensive tests pass
- Documented with examples

**Testing:**
- Unit tests for each query
- Integration tests with schema
- Error handling tests

**Documentation:**
- Table query reference
- Plugin integration guide
- Code examples

---

### 1.3 RECORD and ARRAY Type Resolution (HIGH PRIORITY)
**Effort:** 2-3 days  
**Priority:** HIGH  
**Business Value:** Comprehensive type support with examples  
**Dependencies:** None

**Description:**
Extend type resolution to handle RECORD and ARRAY types in addition to LIKE references. Include comprehensive test code examples.

**Implementation Tasks:**
1. Parse RECORD type definitions
2. Resolve ARRAY element types
3. Store resolved type information in database
4. Update query layer for RECORD/ARRAY queries
5. Create comprehensive test code examples
6. Add comprehensive tests
7. Document type resolution

**Features:**
- Parse RECORD type definitions
- Resolve ARRAY element types
- Handle nested RECORD/ARRAY types
- Store resolved types in database
- Provide test code examples

**Test Code Examples:**
```4gl
# RECORD type example
DEFINE customer RECORD
  id INTEGER,
  name VARCHAR(100),
  balance DECIMAL(10,2)
END RECORD

# ARRAY type example
DEFINE accounts ARRAY[100] OF RECORD
  account_id INTEGER,
  balance DECIMAL(10,2)
END RECORD

# Nested types
DEFINE company RECORD
  id INTEGER,
  employees ARRAY[50] OF RECORD
    emp_id INTEGER,
    name VARCHAR(100)
  END RECORD
END RECORD
```

**Success Criteria:**
- Correctly parses RECORD definitions
- Correctly resolves ARRAY types
- Handles nested types
- Comprehensive tests pass
- Test code examples provided
- Documented with examples

**Testing:**
- Unit tests for RECORD parsing
- Unit tests for ARRAY resolution
- Integration tests with complex types
- Nested type tests
- Test code examples included

**Documentation:**
- Type resolution guide update
- RECORD/ARRAY examples
- Nested type handling
- Test code examples

---

### 1.4 Multiple Schema File Support (LOW PRIORITY)
**Effort:** 1-2 days  
**Priority:** LOW  
**Business Value:** Supports complex multi-schema projects  
**Dependencies:** None

**Description:**
Support multiple schema files per workspace instead of single schema file. Deferred to later phase.

**Implementation Tasks:**
1. Implement schema file discovery
2. Create schema merging logic
3. Handle schema conflicts and overlaps
4. Add conflict resolution strategy
5. Implement validation
6. Add comprehensive tests
7. Document multi-schema setup

**Features:**
- Auto-detect multiple `.sch` files in directory
- Merge schema data from multiple files
- Handle schema conflicts gracefully
- Validate merged schema integrity

**Success Criteria:**
- Discovers all schema files in directory
- Merges schemas correctly
- Handles conflicts gracefully
- Comprehensive tests pass
- Documented with examples

**Testing:**
- Unit tests for schema discovery
- Integration tests with multiple schemas
- Conflict resolution tests

**Documentation:**
- Multi-schema setup guide
- Conflict resolution strategy
- Examples with multiple schemas

**Status:** Deferred - implement in later phase if needed

---

## Priority 2: Performance & Optimization (4-7 days)

### 2.1 Incremental Compilation Support
**Effort:** 1-2 days  
**Priority:** MEDIUM  
**Business Value:** Faster compilation for large projects  
**Dependencies:** None

**Description:**
Track file modification times and compile only changed files.

**Implementation Tasks:**
1. Implement file timestamp tracking
2. Create change detection logic
3. Implement incremental compilation
4. Update database incrementally
5. Add comprehensive tests
6. Document incremental compilation

**Features:**
- Store file modification timestamps
- Compare with current timestamps
- Compile only modified files
- Update database incrementally

**Success Criteria:**
- Correctly detects file changes
- Compiles only modified files
- Database updates correctly
- Comprehensive tests pass
- Performance improvement >50%

**Testing:**
- Unit tests for change detection
- Integration tests with file changes
- Performance tests

**Documentation:**
- Incremental compilation guide
- Performance improvement metrics
- Usage examples

---

### 2.2 Parallel Query Execution
**Effort:** 1-2 days  
**Priority:** MEDIUM  
**Business Value:** Faster multi-query operations  
**Dependencies:** None

**Description:**
Execute independent queries in parallel for better performance.

**Implementation Tasks:**
1. Identify independent queries in batch operations
2. Implement thread pool for parallel execution
3. Aggregate results maintaining order
4. Add error handling for failed queries
5. Add comprehensive tests
6. Document parallel queries

**Features:**
- Execute independent queries in parallel
- Maintain result ordering
- Handle query failures gracefully
- Aggregate results correctly

**Success Criteria:**
- Executes queries in parallel
- Maintains result ordering
- Handles failures gracefully
- Comprehensive tests pass
- Performance improvement >30%

**Testing:**
- Unit tests for parallel execution
- Integration tests with batch queries
- Performance tests
- Error handling tests

**Documentation:**
- Parallel query guide
- Performance improvement metrics
- Usage examples

---

### 2.3 Intelligent Cache Invalidation
**Effort:** 1-2 days  
**Priority:** LOW  
**Business Value:** Reduce cache misses  
**Dependencies:** None

**Description:**
Track file dependencies and invalidate only affected cache entries.

**Implementation Tasks:**
1. Implement file dependency tracking
2. Create cache invalidation logic
3. Invalidate only affected entries
4. Add comprehensive tests
5. Document cache invalidation

**Features:**
- Track file dependencies
- Invalidate only affected cache entries
- Reduce cache misses
- Improve cache hit rate

**Success Criteria:**
- Correctly tracks dependencies
- Invalidates only affected entries
- Reduces cache misses
- Comprehensive tests pass

**Testing:**
- Unit tests for dependency tracking
- Integration tests with cache invalidation
- Performance tests

**Documentation:**
- Cache invalidation guide
- Performance improvement metrics

---

### 2.4 Persistent Cache
**Effort:** 1 day  
**Priority:** LOW  
**Business Value:** Faster startup  
**Dependencies:** None

**Description:**
Save cache to disk between sessions.

**Implementation Tasks:**
1. Implement cache serialization
2. Implement cache deserialization
3. Add cache freshness validation
4. Add comprehensive tests
5. Document persistent cache

**Features:**
- Serialize cache to disk
- Load cache on startup
- Validate cache freshness
- Handle stale cache gracefully

**Success Criteria:**
- Correctly serializes cache
- Correctly deserializes cache
- Validates freshness
- Comprehensive tests pass
- Startup time improvement >50%

**Testing:**
- Unit tests for serialization
- Integration tests with cache loading
- Performance tests

**Documentation:**
- Persistent cache guide
- Performance improvement metrics

---

## Priority 3: IDE Integration (5-8 days)

### 3.1 LSP Server Implementation
**Effort:** 3-5 days  
**Priority:** HIGH  
**Business Value:** IDE-agnostic integration  
**Dependencies:** All Priority 1 and 2 features

**Description:**
Implement Language Server Protocol (LSP) server for genero-tools.

**Implementation Tasks:**
1. Implement LSP server wrapper
2. Map genero-tools queries to LSP methods
3. Implement hover information
4. Implement code completion
5. Implement go-to-definition
6. Implement find-references
7. Add comprehensive tests
8. Document LSP integration

**LSP Methods:**
- `textDocument/hover` - Function signature and metadata
- `textDocument/completion` - Function name completion
- `textDocument/definition` - Go-to-definition
- `textDocument/references` - Find references
- `textDocument/documentSymbol` - Document symbols

**Success Criteria:**
- Implements all LSP methods
- Works with LSP-compatible editors
- Comprehensive tests pass
- Documented with examples

**Testing:**
- Unit tests for LSP methods
- Integration tests with LSP clients
- Manual testing with editors

**Documentation:**
- LSP integration guide
- Supported LSP methods
- Editor setup instructions

---

### 3.2 Vim Plugin Integration
**Effort:** 2-3 days  
**Priority:** HIGH  
**Business Value:** Vim editor integration  
**Dependencies:** 3.1 (LSP Server) or direct query integration

**Description:**
Create Vim plugin that uses genero-tools for code analysis.

**Implementation Tasks:**
1. Create Vim plugin structure
2. Implement hover information
3. Implement code completion
4. Implement go-to-definition
5. Implement find references
6. Implement code metrics display
7. Add comprehensive tests
8. Document Vim plugin

**Features:**
- Hover information with function signatures
- Code completion
- Go-to-definition navigation
- Find references
- Code metrics display
- Type resolution information
- Table definition lookup

**Success Criteria:**
- All features work in Vim
- Comprehensive tests pass
- Documented with setup instructions
- Performance acceptable

**Testing:**
- Manual testing in Vim
- Integration tests with genero-tools
- Performance tests

**Documentation:**
- Vim plugin setup guide
- Feature documentation
- Troubleshooting guide

---

### 3.3 VS Code Extension (LOW PRIORITY - DEFERRED)
**Effort:** 2-3 days  
**Priority:** LOW  
**Business Value:** VS Code editor integration  
**Dependencies:** 3.1 (LSP Server)
**Status:** Deferred indefinitely - keep for reference

**Description:**
Create VS Code extension that uses genero-tools for code analysis. This feature is deferred but kept for reference for future implementation.

**Implementation Tasks:**
1. Create VS Code extension structure
2. Implement code lens
3. Implement hover information
4. Implement go-to-definition
5. Implement find references
6. Implement code metrics sidebar
7. Add comprehensive tests
8. Document VS Code extension

**Features:**
- Code lens showing complexity and call count
- Hover information with full signature
- Go-to-definition navigation
- Find references
- Code metrics in sidebar
- Type resolution information

**Success Criteria:**
- All features work in VS Code
- Comprehensive tests pass
- Documented with setup instructions
- Performance acceptable

**Testing:**
- Manual testing in VS Code
- Integration tests with genero-tools
- Performance tests

**Documentation:**
- VS Code extension setup guide
- Feature documentation
- Troubleshooting guide

**Status:** Deferred - implement in future if needed

---

## Implementation Schedule

### Week 1: Vim Plugin Output Optimization (2-4 days)
- **Day 1-2:** 1.1 Refined Output for Vim Plugin
- **Day 3-4:** 1.2 Table Definition Queries

### Week 1-2: Type Resolution (2-3 days)
- **Day 5-7:** 1.3 RECORD/ARRAY Type Resolution

### Week 2-3: Performance & Optimization (4-7 days)
- **Day 8-9:** 2.1 Incremental Compilation
- **Day 10-11:** 2.2 Parallel Query Execution
- **Day 12:** 2.3 Intelligent Cache
- **Day 13:** 2.4 Persistent Cache

### Week 3-4: IDE Integration (5-8 days)
- **Day 14-18:** 3.1 LSP Server Implementation
- **Day 19-21:** 3.2 Vim Plugin Integration

**Total: 15-25 days** (reduced from 18-28 days)

---

## Success Criteria for All Features

- ✅ Query executes in <100ms for typical codebases
- ✅ Handles pagination for large result sets
- ✅ Returns consistent JSON format
- ✅ Includes comprehensive tests (>90% coverage)
- ✅ Documented with examples
- ✅ No breaking changes to existing queries
- ✅ Backward compatible with v2.1.0

---

## Testing Requirements

### Unit Tests
- Test each feature function independently
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

---

## Documentation Requirements

For each feature:
- Shell command documentation
- Python API documentation
- Code examples
- Use case descriptions
- Troubleshooting guide
- Performance characteristics
- Migration guide (if applicable)

---

## Handoff Checklist

- ✅ 9 features prioritized by business value
- ✅ Effort estimates for each feature
- ✅ Dependencies clearly identified
- ✅ Success criteria defined
- ✅ Testing requirements specified
- ✅ Documentation requirements listed
- ✅ Implementation schedule provided
- ✅ All features maintain backward compatibility
- ✅ Performance targets defined (<100ms)
- ✅ Ready for implementation

---

## Notes

1. **Dependencies:** Features should be implemented in order to respect dependencies
2. **Backward Compatibility:** All features must maintain backward compatibility with v2.1.0
3. **Performance:** All queries must execute in <100ms for typical codebases
4. **Testing:** Comprehensive testing (>90% coverage) required for all features
5. **Documentation:** Each feature must be documented with examples
6. **Flexibility:** Effort estimates are ranges; actual time may vary based on complexity
7. **Vim Plugin Focus:** Phases 1.1 and 1.2 prioritize Vim plugin integration with refined output
8. **Type Resolution:** RECORD/ARRAY types are high priority with comprehensive test examples
9. **VS Code Deferred:** VS Code extension is deferred indefinitely but kept for reference

---

**Status:** Ready for Implementation  
**Last Updated:** March 24, 2026  
**Version:** 2.1.0

