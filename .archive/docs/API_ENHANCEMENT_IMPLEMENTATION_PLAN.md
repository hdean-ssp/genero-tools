# API Enhancement Implementation Plan

## Phase 1: Critical Enhancements (Weeks 1-2)

### 1.1 Batch Queries

**Goal:** Execute multiple queries in single invocation

**API Design:**
```bash
query.sh batch-query <json_file>
```

**Input Format:**
```json
{
  "queries": [
    {"id": "q1", "command": "find-function", "args": ["myFunc"]},
    {"id": "q2", "command": "find-function-dependencies", "args": ["myFunc"]},
    {"id": "q3", "command": "find-function-dependents", "args": ["myFunc"]}
  ]
}
```

**Output Format:**
```json
{
  "results": [
    {"id": "q1", "data": [...], "success": true},
    {"id": "q2", "data": [...], "success": true},
    {"id": "q3", "data": [...], "success": true}
  ],
  "execution_time_ms": 45
}
```

**Implementation:**
- Create `batch_query.py` module
- Parse JSON input
- Execute queries sequentially (or parallel with thread pool)
- Aggregate results
- Return with timing info

**Benefits:**
- Single DB connection
- Atomic transactions
- 10x faster than separate calls
- Enables hover info (def + deps + dependents)

---

### 1.2 Pagination Support

**Goal:** Handle large result sets efficiently

**API Design:**
```bash
query.sh search-functions "pattern" --limit 50 --offset 0 --total-count
```

**Output Format:**
```json
{
  "data": [...],
  "pagination": {
    "limit": 50,
    "offset": 0,
    "total": 1234,
    "has_more": true
  }
}
```

**Implementation:**
- Add `--limit` and `--offset` parameters to all query commands
- Add `--total-count` flag for total count
- Modify SQL queries to use LIMIT/OFFSET
- Return pagination metadata

**Benefits:**
- Memory efficient
- Progressive UI updates
- Handles 6M+ LOC codebases
- Lazy loading support

---

### 1.3 Relationship Queries

**Goal:** Support complex relationship queries

**New Commands:**

```bash
# Find functions in module that call a function
query.sh find-dependents-in-module <module> <function>

# Find call chain between two functions
query.sh find-call-chain <from> <to> [--max-depth 5]

# Find functions that call all specified functions
query.sh find-common-callers <func1> <func2> [<func3> ...]
```

**Implementation:**
- `find-dependents-in-module`: JOIN call_graph + modules
- `find-call-chain`: Recursive SQL or Python traversal
- `find-common-callers`: Intersection of caller sets

**Benefits:**
- Advanced navigation
- "Find callers in module" feature
- "Find call path" feature
- Better code understanding

---

### 1.4 Error Handling

**Goal:** Provide structured error information

**New Commands:**

```bash
# Validate database integrity
query.sh validate-database

# Get detailed error information
query.sh get-error-details <error_code>
```

**Error Codes:**
- E001: Database not found
- E002: Database corrupted
- E003: Query syntax error
- E004: Function not found
- E005: Module not found

**Implementation:**
- Create error code system
- Add validation logic
- Return structured errors with suggestions

**Benefits:**
- Better error messages
- Helpful suggestions
- Easier debugging

---

## Phase 2: Important Enhancements (Weeks 3-4)

### 2.1 Metrics Exposure

**Goal:** Expose code quality metrics

**New Commands:**

```bash
# Get metrics for a function
query.sh function-metrics <name>

# Get metrics for a module
query.sh module-metrics <name>

# Find complex functions
query.sh find-complex-functions [--threshold 10]

# Find high-coupling functions
query.sh find-high-coupling [--threshold 15]
```

**Output Format:**
```json
{
  "name": "function_name",
  "metrics": {
    "cyclomatic_complexity": 5,
    "lines_of_code": 45,
    "parameters": 3,
    "return_type": "string",
    "calls_count": 8,
    "called_by_count": 12,
    "nesting_depth": 3,
    "comment_ratio": 0.15
  }
}
```

**Implementation:**
- Expose existing metrics from workspace.db
- Add coupling calculation
- Add cohesion analysis
- Create threshold-based queries

**Benefits:**
- Code quality analysis
- Identify refactoring candidates
- Visual indicators in IDE
- Improve code health

---

### 2.2 Advanced Search

**Goal:** Multi-criteria search and filtering

**New Command:**

```bash
query.sh advanced-search \
  --type function \
  --author John \
  --since 7 \
  --reference 'PRB%' \
  --complexity_min 10 \
  --complexity_max 20 \
  --module core \
  --file "*.4gl"
```

**Implementation:**
- Build dynamic WHERE clauses
- Support multiple criteria
- Combine with pagination
- Return filtered results

**Benefits:**
- Powerful filtering
- Find related code
- Understand code ownership
- Complex searches

---

### 2.3 Cache Invalidation

**Goal:** Smart cache management

**New Commands:**

```bash
# Get cache metadata
query.sh get-cache-info

# Invalidate cache for specific items
query.sh invalidate-cache --file <path> --function <name> --module <name>
```

**Output Format:**
```json
{
  "last_update": "2024-03-15T10:30:00Z",
  "database_version": "1.2.3",
  "files_indexed": 1234,
  "functions_indexed": 5678,
  "cache_valid_until": "2024-03-16T10:30:00Z"
}
```

**Implementation:**
- Track database metadata
- Implement cache invalidation
- Return invalidation hints
- Support selective invalidation

**Benefits:**
- Smart caching
- Data freshness
- Reduced unnecessary refreshes
- Better performance

---

## Phase 3: Nice to Have (Weeks 5-6)

### 3.1 Diff/Change Detection

**Goal:** Track changes between versions

**New Commands:**

```bash
# Compare function signatures
query.sh diff-functions <name> --old-db workspace.db.old --new-db workspace.db

# Get functions modified in file
query.sh diff-file <path> --old-db workspace.db.old --new-db workspace.db
```

**Note:** SVN integration handled separately

**Implementation:**
- Database comparison logic
- Signature diffing
- Change detection

**Benefits:**
- Version tracking
- Show what changed
- Highlight modifications

---

### 3.2 Export/Report Generation

**Goal:** Generate reports and visualizations

**New Commands:**

```bash
# Export call graph
query.sh export-call-graph <format> [--module <name>]
# Formats: dot, json, csv, html

# Generate report
query.sh generate-report <type> [--output file.html]
# Types: quality, complexity, coverage, dependencies
```

**Implementation:**
- Create export formatters
- Generate HTML reports
- Support multiple formats
- Include visualizations

**Benefits:**
- Analysis tools
- Visualization
- Documentation
- Metrics tracking

---

## Implementation Priority Matrix

| Feature | Phase | Effort | Impact | Priority |
|---------|-------|--------|--------|----------|
| Batch queries | 1 | Medium | High | 1 |
| Pagination | 1 | Low | High | 2 |
| Relationship queries | 1 | Medium | High | 3 |
| Error handling | 1 | Low | Medium | 4 |
| Metrics exposure | 2 | Low | High | 5 |
| Advanced search | 2 | Medium | Medium | 6 |
| Cache invalidation | 2 | Low | Medium | 7 |
| Diff detection | 3 | High | Low | 8 |
| Export/reports | 3 | Medium | Low | 9 |

---

## Success Metrics

### Phase 1
- ✅ Batch queries working
- ✅ Pagination support added
- ✅ Relationship queries implemented
- ✅ Error handling improved
- **Result:** 10x faster, handles 6M+ LOC

### Phase 2
- ✅ Metrics exposed
- ✅ Advanced search working
- ✅ Cache invalidation implemented
- **Result:** Code quality analysis enabled

### Phase 3
- ✅ Diff detection working
- ✅ Reports generating
- **Result:** Full analysis toolkit

---

## Testing Strategy

### Unit Tests
- Batch query parsing
- Pagination logic
- Relationship query correctness
- Error handling

### Integration Tests
- End-to-end batch queries
- Large result set pagination
- Complex relationship queries
- Error scenarios

### Performance Tests
- Batch query performance
- Pagination overhead
- Large codebase handling
- Query execution time

### Vim Plugin Tests
- Integration with plugin
- Real-world usage patterns
- Performance under load

---

## Estimated Timeline

- **Phase 1:** 2 weeks (batch, pagination, relationships, errors)
- **Phase 2:** 2 weeks (metrics, search, caching)
- **Phase 3:** 2 weeks (diff, reports)
- **Total:** 6 weeks to full IDE-like capabilities

---

## Backward Compatibility

- ✅ All existing commands continue to work
- ✅ New parameters are optional
- ✅ Default behavior unchanged
- ✅ No breaking changes

---

## Questions for Implementation

1. Should batch queries be atomic or independent?
2. What's the maximum result set size?
3. Should pagination be default or opt-in?
4. How deep should call chains go?
5. What metrics are most important?

