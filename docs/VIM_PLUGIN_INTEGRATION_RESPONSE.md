# Vim Plugin Integration Response

## Overview

This document addresses the API enhancement suggestions from the genero-vim plugin development team. The suggestions identify 9 critical gaps that would transform genero-tools from a query tool into a full IDE backend.

## Executive Summary

**Current State:** Good for simple lookups, limited for IDE-like features
**Proposed:** Add batch operations, pagination, metrics, and advanced queries
**Impact:** Enable professional IDE features in Vim

## Critical Gaps Analysis

### 1. Batch/Bulk Operations ⭐⭐⭐

**Problem:** Each lookup requires separate CLI invocation
**Impact:** 10x slower than necessary, no parallel operations

**Proposed Solution:**
```bash
query.sh batch-query queries.json
```

**Implementation Status:** ✅ Feasible
- Requires: Python wrapper for multiple queries
- Benefit: Single DB connection, atomic transactions
- Use Case: Hover info needs definition + dependencies + dependents

**Recommendation:** Implement first - biggest performance impact

---

### 2. Pagination/Streaming ⭐⭐⭐

**Problem:** All results returned at once, memory issues with large codebases
**Impact:** Can't handle 6M+ LOC codebases

**Proposed Solution:**
```bash
query.sh search-functions "pattern" --limit 50 --offset 0 --total-count
```

**Implementation Status:** ✅ Feasible
- Requires: SQL LIMIT/OFFSET in queries
- Benefit: Memory efficient, progressive UI
- Use Case: Search results pagination

**Recommendation:** Implement second - handles scale

---

### 3. Relationship Queries ⭐⭐⭐

**Problem:** Can't ask complex questions like "find callers in this module"
**Impact:** Limited IDE features

**Proposed Commands:**
- `find-dependents-in-module <module> <function>`
- `find-call-chain <from> <to> [--max-depth]`
- `find-common-callers <func1> <func2> ...`

**Implementation Status:** ✅ Feasible
- Requires: SQL joins on call graph + module data
- Benefit: Advanced navigation
- Use Case: "Show me all functions in core that call this"

**Recommendation:** Implement third - enables advanced features

---

### 4. Metrics & Quality Queries ⭐⭐⭐

**Problem:** No complexity, coupling, or cohesion data
**Impact:** Can't provide code quality analysis

**Proposed Commands:**
- `function-metrics <name>` - complexity, LOC, parameters, etc.
- `module-metrics <name>` - function count, avg complexity, coupling
- `find-complex-functions [--threshold]`
- `find-high-coupling [--threshold]`

**Implementation Status:** ✅ Partially Complete
- Already have: Cyclomatic complexity, LOC, parameter count
- Missing: Coupling metrics, cohesion analysis
- Benefit: Code quality features

**Recommendation:** Expose existing metrics via new commands

---

### 5. Advanced Search ⭐⭐

**Problem:** Limited search capabilities, can't combine criteria
**Impact:** Can't implement "find all functions modified by John in last week"

**Proposed Solution:**
```bash
query.sh advanced-search \
  --type function \
  --author John \
  --since 7 \
  --reference 'PRB%' \
  --complexity_min 10
```

**Implementation Status:** ✅ Feasible
- Requires: Multi-criteria SQL WHERE clauses
- Benefit: Powerful filtering
- Use Case: Complex searches

**Recommendation:** Implement after metrics

---

### 6. Error Handling & Diagnostics ⭐⭐

**Problem:** Limited error information, hard to debug
**Impact:** Poor error messages in IDE

**Proposed Commands:**
- `validate-database` - Check integrity
- `get-error-details <code>` - Structured errors

**Implementation Status:** ✅ Feasible
- Requires: Error code system, validation logic
- Benefit: Better diagnostics
- Use Case: Helpful error messages

**Recommendation:** Implement early - improves UX

---

### 7. Diff/Change Detection ⭐

**Problem:** No built-in support for detecting changes
**Impact:** Can't show "what changed in this file"

**Proposed Commands:**
- `diff-functions <name> --old-db --new-db`
- `diff-file <path> --old-db --new-db`

**Implementation Status:** ⚠️ Partial
- Note: SVN integration handled separately
- Requires: Database comparison logic
- Benefit: Version tracking

**Recommendation:** Implement after core features

---

### 8. Export/Report Generation ⭐

**Problem:** No built-in export or report generation
**Impact:** Can't generate IDE reports

**Proposed Commands:**
- `export-call-graph <format>` - dot, json, csv, html
- `generate-report <type>` - quality, complexity, coverage

**Implementation Status:** ✅ Feasible
- Requires: Export formatters
- Benefit: Visualization, documentation
- Use Case: Generate reports

**Recommendation:** Implement after core features

---

### 9. Cache Invalidation ⭐

**Problem:** No cache invalidation hints
**Impact:** Stale data or excessive refreshes

**Proposed Commands:**
- `get-cache-info` - Metadata and invalidation hints
- `invalidate-cache --file --function --module`

**Implementation Status:** ✅ Feasible
- Requires: Cache metadata tracking
- Benefit: Smart caching
- Use Case: After file save, invalidate cache

**Recommendation:** Implement with batch queries

---

## Implementation Roadmap

### Phase 1: Critical (Weeks 1-2)
1. ✅ Batch queries - Parallel operations
2. ✅ Pagination - Handle large codebases
3. ✅ Error handling - Better diagnostics
4. ✅ Relationship queries - Advanced navigation

**Deliverable:** 10x faster, handles 6M+ LOC

### Phase 2: Important (Weeks 3-4)
5. ✅ Metrics exposure - Code quality
6. ✅ Advanced search - Powerful filtering
7. ✅ Cache invalidation - Smart caching

**Deliverable:** Code quality analysis, advanced search

### Phase 3: Nice to Have (Weeks 5-6)
8. ⚠️ Diff detection - Version tracking
9. ✅ Export/reports - Visualization

**Deliverable:** Analysis tools, visualization

---

## Feasibility Assessment

| Gap | Feasibility | Effort | Priority |
|-----|-------------|--------|----------|
| Batch queries | ✅ High | Medium | 1 |
| Pagination | ✅ High | Low | 2 |
| Relationship queries | ✅ High | Medium | 3 |
| Metrics | ✅ High | Low | 4 |
| Advanced search | ✅ High | Medium | 5 |
| Error handling | ✅ High | Low | 6 |
| Diff detection | ⚠️ Medium | High | 7 |
| Export/reports | ✅ High | Medium | 8 |
| Cache invalidation | ✅ High | Low | 9 |

---

## Next Steps

1. **Review** this response with vim plugin team
2. **Prioritize** which features to implement first
3. **Design** batch query API
4. **Implement** Phase 1 features
5. **Test** with vim plugin
6. **Iterate** based on feedback

---

## Questions for Vim Plugin Team

1. Which Phase 1 features are most critical?
2. What's the typical query pattern in the plugin?
3. How many queries per operation?
4. What's acceptable latency for IDE operations?
5. Should batch queries be atomic or independent?

