# Genero-Tools API Enhancement Suggestions

Analysis of genero-tools API gaps and enhancement opportunities to better support the vim-genero-tools plugin and IDE-like functionality.

## Current API Coverage

### ✅ Well-Supported Areas

1. **Function Queries** - Comprehensive coverage
   - `find-function` - Exact lookup
   - `search-functions` - Pattern matching
   - `list-file-functions` - File-scoped queries
   - `find-function-dependencies` - Call graph analysis
   - `find-function-dependents` - Reverse call graph
   - `find-dead-code` - Unused function detection

2. **Module Queries** - Good coverage
   - `find-module` - Exact lookup
   - `search-modules` - Pattern matching
   - `find-functions-in-module` - Module-scoped queries
   - `find-module-dependencies` - Module dependency graph

3. **Metadata Queries** - Basic coverage
   - `file-references` - Code references (PRB-XXX, etc.)
   - `file-authors` - Author tracking
   - `find-reference` - Reference-based lookup
   - `find-author` - Author-based lookup
   - `recent-changes` - Time-based queries

## 🔴 Critical Gaps

### 1. **Batch/Bulk Operations**
**Problem:** No batch query support. Each lookup requires separate CLI invocation.
**Impact:** Performance degradation with multiple lookups, no parallel query support.

**Suggested Enhancement:**
```json
{
  "batch-query": {
    "description": "Execute multiple queries in single invocation",
    "syntax": "query.sh batch-query <json_file>",
    "input_format": {
      "queries": [
        {"id": "q1", "command": "find-function", "args": ["myFunc"]},
        {"id": "q2", "command": "find-function-dependencies", "args": ["myFunc"]},
        {"id": "q3", "command": "find-module-for-function", "args": ["myFunc"]}
      ]
    },
    "output_format": {
      "results": [
        {"id": "q1", "data": [...], "success": true},
        {"id": "q2", "data": [...], "success": true},
        {"id": "q3", "data": [...], "success": true}
      ]
    },
    "benefits": [
      "Single database connection for multiple queries",
      "Reduced CLI overhead",
      "Atomic transaction support",
      "Better performance for IDE operations"
    ]
  }
}
```

**Use Case:** When user hovers over a function, fetch definition + dependencies + dependents in one call.

---

### 2. **Incremental/Streaming Results**
**Problem:** All results returned at once. No pagination or streaming support.
**Impact:** Large result sets cause memory issues, no progressive display.

**Suggested Enhancement:**
```json
{
  "query-with-pagination": {
    "description": "Query with built-in pagination support",
    "syntax": "query.sh search-functions <pattern> --limit 50 --offset 0",
    "parameters": [
      {"name": "limit", "type": "integer", "default": 50},
      {"name": "offset", "type": "integer", "default": 0},
      {"name": "total_count", "type": "boolean", "default": false}
    ],
    "output_format": {
      "data": [...],
      "pagination": {
        "limit": 50,
        "offset": 0,
        "total": 1234,
        "has_more": true
      }
    },
    "benefits": [
      "Memory-efficient for large result sets",
      "Progressive UI updates",
      "Better UX for large codebases",
      "Lazy loading support"
    ]
  }
}
```

**Use Case:** Search for functions matching pattern - show first 50, load more on demand.

---



### 3. **Relationship Queries**
**Problem:** No direct support for complex relationships (e.g., "all functions that call this function AND are in this module").
**Impact:** Limited IDE features like "find callers in this module".

**Suggested Enhancement:**
```json
{
  "find-dependents-in-module": {
    "description": "Find functions in a module that call a function",
    "syntax": "query.sh find-dependents-in-module <module> <function>",
    "parameters": [
      {"name": "module", "type": "string", "required": true},
      {"name": "function", "type": "string", "required": true}
    ],
    "returns": "JSON array of functions in module that call function"
  },
  "find-call-chain": {
    "description": "Find call chain between two functions",
    "syntax": "query.sh find-call-chain <from> <to> [--max-depth 5]",
    "parameters": [
      {"name": "from", "type": "string", "required": true},
      {"name": "to", "type": "string", "required": true},
      {"name": "max_depth", "type": "integer", "default": 5}
    ],
    "returns": {
      "paths": [
        ["func1", "func2", "func3"],
        ["func1", "func4", "func3"]
      ]
    }
  },
  "find-common-callers": {
    "description": "Find functions that call all of the given functions",
    "syntax": "query.sh find-common-callers <func1> <func2> [<func3> ...]",
    "returns": "JSON array of functions calling all specified functions"
  }
}
```

**Use Case:** "Show me all functions in the 'core' module that call this function" or "Find the call path from main to this function".

---

### 4. **Metrics and Quality Queries**
**Problem:** Limited quality metrics. No complexity, coupling, or cohesion data.
**Impact:** Can't provide IDE features like "this function is too complex" or "high coupling detected".

**Suggested Enhancement:**
```json
{
  "function-metrics": {
    "description": "Get metrics for a function",
    "syntax": "query.sh function-metrics <name>",
    "returns": {
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
  },
  "module-metrics": {
    "description": "Get metrics for a module",
    "syntax": "query.sh module-metrics <name>",
    "returns": {
      "name": "module_name",
      "metrics": {
        "function_count": 25,
        "avg_complexity": 4.2,
        "coupling": 8,
        "cohesion": 0.85,
        "lines_of_code": 1200
      }
    }
  },
  "find-complex-functions": {
    "description": "Find functions exceeding complexity threshold",
    "syntax": "query.sh find-complex-functions [--threshold 10]",
    "parameters": [
      {"name": "threshold", "type": "integer", "default": 10}
    ],
    "returns": "JSON array of functions with complexity >= threshold"
  },
  "find-high-coupling": {
    "description": "Find functions with high coupling",
    "syntax": "query.sh find-high-coupling [--threshold 15]",
    "returns": "JSON array of functions calling many other functions"
  }
}
```

**Use Case:** Highlight complex functions in editor, suggest refactoring.

---

### 5. **Search and Filter Enhancements**
**Problem:** Limited search capabilities. Can't search by multiple criteria or use advanced filters.
**Impact:** Can't implement IDE features like "find all functions modified by John in the last week".

**Suggested Enhancement:**
```json
{
  "advanced-search": {
    "description": "Search with multiple criteria",
    "syntax": "query.sh advanced-search --type function --author John --since 7 --reference 'PRB%'",
    "parameters": [
      {"name": "type", "type": "string", "enum": ["function", "module", "file"]},
      {"name": "author", "type": "string"},
      {"name": "since", "type": "integer", "description": "Days"},
      {"name": "reference", "type": "string", "description": "Wildcard pattern"},
      {"name": "complexity_min", "type": "integer"},
      {"name": "complexity_max", "type": "integer"},
      {"name": "module", "type": "string"},
      {"name": "file", "type": "string"}
    ],
    "returns": "JSON array of matching items"
  }
}
```

**Use Case:** "Find all functions modified by John in the last 7 days for PRB tickets".

---

### 6. **Diff/Change Detection**
**Problem:** No built-in support for detecting what changed between two versions.
**Impact:** Can't implement "show what changed in this file" or "highlight modified functions".

**Suggested Enhancement:**
```json
{
  "diff-functions": {
    "description": "Compare function signatures between versions",
    "syntax": "query.sh diff-functions <name> --old-db workspace.db.old --new-db workspace.db",
    "returns": {
      "function": "name",
      "changes": {
        "signature_changed": true,
        "parameters_added": ["new_param"],
        "parameters_removed": [],
        "return_type_changed": false,
        "implementation_changed": true
      }
    }
  },
  "diff-file": {
    "description": "Get functions modified in a file",
    "syntax": "query.sh diff-file <path> --old-db workspace.db.old --new-db workspace.db",
    "returns": {
      "file": "path",
      "functions": {
        "added": ["new_func"],
        "removed": ["old_func"],
        "modified": ["changed_func"]
      }
    }
  }
}
```

**Use Case:** Show in editor which functions were modified since last commit.

---

### 7. **Export/Report Generation**
**Problem:** No built-in export or report generation. Must parse JSON manually.
**Impact:** Can't generate IDE reports like "code quality report" or "dependency graph".

**Suggested Enhancement:**
```json
{
  "export-call-graph": {
    "description": "Export call graph in various formats",
    "syntax": "query.sh export-call-graph <format> [--module <name>]",
    "parameters": [
      {"name": "format", "type": "string", "enum": ["dot", "json", "csv", "html"]},
      {"name": "module", "type": "string", "description": "Limit to module"}
    ],
    "returns": "Graph data in requested format"
  },
  "generate-report": {
    "description": "Generate code quality report",
    "syntax": "query.sh generate-report <type> [--output file.html]",
    "parameters": [
      {"name": "type", "type": "string", "enum": ["quality", "complexity", "coverage", "dependencies"]},
      {"name": "output", "type": "string"}
    ],
    "returns": "Report in HTML or JSON format"
  }
}
```

**Use Case:** Generate code quality report for display in IDE.

---

### 8. **Caching/Invalidation Support**
**Problem:** No cache invalidation hints. Plugin must guess when to refresh.
**Impact:** Stale data in IDE, or excessive refreshes.

**Suggested Enhancement:**
```json
{
  "get-cache-info": {
    "description": "Get cache metadata and invalidation hints",
    "syntax": "query.sh get-cache-info",
    "returns": {
      "last_update": "2024-03-15T10:30:00Z",
      "database_version": "1.2.3",
      "files_indexed": 1234,
      "functions_indexed": 5678,
      "cache_valid_until": "2024-03-16T10:30:00Z"
    }
  },
  "invalidate-cache": {
    "description": "Invalidate cache for specific items",
    "syntax": "query.sh invalidate-cache --file <path> --function <name>",
    "parameters": [
      {"name": "file", "type": "string"},
      {"name": "function", "type": "string"},
      {"name": "module", "type": "string"}
    ]
  }
}
```

**Use Case:** After file save, invalidate cache for that file only.

---

### 9. **Error Handling and Diagnostics**
**Problem:** Limited error information. Hard to debug issues.
**Impact:** Poor error messages in IDE, hard to troubleshoot.

**Suggested Enhancement:**
```json
{
  "validate-database": {
    "description": "Validate database integrity",
    "syntax": "query.sh validate-database",
    "returns": {
      "valid": true,
      "issues": [],
      "statistics": {
        "functions": 5678,
        "modules": 45,
        "files": 1234
      }
    }
  },
  "get-error-details": {
    "description": "Get detailed error information",
    "syntax": "query.sh get-error-details <error_code>",
    "returns": {
      "code": "E001",
      "message": "Database not found",
      "suggestion": "Run 'query.sh create-dbs' to create databases",
      "documentation": "https://..."
    }
  }
}
```

**Use Case:** Show helpful error messages when database is missing or corrupted.

---

## 🟡 Medium Priority Gaps

### 10. **Performance Hints**
- Query execution time estimates
- Suggest indexes for slow queries
- Recommend caching strategies

### 11. **Incremental Updates**
- Support for incremental database updates
- Detect and update only changed files
- Merge new data with existing

### 12. **Filtering and Sorting**
- Built-in sorting options (by name, complexity, date, etc.)
- Filter results by criteria
- Limit results with configurable defaults

### 13. **Statistics and Analytics**
- Codebase statistics (total functions, modules, LOC)
- Author statistics (commits, files modified)
- Module statistics (size, complexity, coupling)

### 14. **Workspace Management**
- List available workspaces
- Switch between workspaces
- Merge workspaces

---

## Implementation Priority

### Phase 1 (Critical - Implement First)
1. **Batch queries** - Enables parallel operations
2. **Pagination** - Handles large result sets
3. **Error handling** - Better diagnostics

### Phase 2 (Important - Implement Next)
4. **Relationship queries** - Complex analysis
5. **Metrics** - Code quality features
6. **Advanced search** - Better filtering
7. **Cache invalidation** - Data freshness

### Phase 3 (Nice to Have)
8. **Diff/Change detection** - Version tracking (SVN handled separately)
9. **Export/Reports** - Analysis tools
10. **Performance hints** - Optimization
11. **Statistics** - Analytics

---

## Impact on Vim Plugin

### Immediate Benefits (Phase 1)
- **Faster operations** - Batch queries reduce CLI overhead
- **Better UX** - Pagination handles large result sets
- **Richer features** - Relationship queries enable new IDE features
- **Better errors** - Improved error messages

### Medium-term Benefits (Phase 2)
- **Code quality** - Metrics enable quality analysis
- **Advanced navigation** - Relationship queries enable complex analysis
- **Better search** - Advanced search enables powerful filtering

### Long-term Benefits (Phase 3)
- **Analytics** - Statistics and reports
- **Version tracking** - Diff detection
- **Performance** - Optimization hints

---

## Recommended Next Steps

1. **Prioritize batch queries** - Biggest performance impact
2. **Add pagination** - Handles large codebases
3. **Implement relationship queries** - Enables new IDE features
4. **Improve error handling** - Better diagnostics

These enhancements would transform genero-tools from a query tool into a full IDE backend, enabling rich features like:
- Real-time code analysis
- Intelligent navigation
- Code quality metrics
- Dependency visualization
- Change tracking
- Performance optimization suggestions

---

## Questions for Genero-Tools Team

1. **Batch queries** - Can query.sh support multiple queries in one invocation?
2. **Pagination** - Can queries return total count and support offset/limit?
3. **Metrics** - Can workspace.db store complexity, coupling, and other metrics?
4. **Caching** - Can query.sh provide cache invalidation hints?
5. **Performance** - What's the typical query time for large codebases (6M+ LOC)?
6. **Incremental updates** - Can databases be updated incrementally?
7. **Error codes** - Can query.sh return structured error codes?
8. **Streaming** - Can results be streamed instead of returned all at once?

