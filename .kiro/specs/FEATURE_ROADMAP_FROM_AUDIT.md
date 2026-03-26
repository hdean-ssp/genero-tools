# Genero-Tools Feature Roadmap - Derived from Vim Plugin Audit

**Date:** March 23, 2026  
**Source:** GENERO_TOOLS_USAGE_AUDIT.md (Vim/Neovim plugin analysis)  
**Purpose:** Identify and prioritize new functionality for genero-tools based on real-world plugin usage patterns

---

## Executive Summary

The Vim/Neovim plugin audit reveals that genero-tools is being used for:
- Function lookup and navigation
- File metadata extraction
- Module file listing
- Batch query operations with pagination

**Key Finding:** The plugin expects several features that genero-tools doesn't yet provide. These gaps represent high-value functionality that would benefit all consumers of genero-tools.

---

## Relevant Feature Gaps for Genero-Tools

### Priority 1: High-Value, Core Functionality

#### 1.1 Find References / Find Usages
**Current State:** Not implemented  
**Use Case:** Refactoring, impact analysis, understanding code dependencies  
**Plugin Need:** Essential for safe refactoring workflows  
**Implementation:** Query layer to find all functions that call a given function

**Proposed API:**
```bash
# Shell interface
bash query.sh find-references "function_name"
bash query.sh find-usages "function_name"

# Python interface
python3 scripts/query_db.py find-references workspace.db "function_name"
```

**Output Format:**
```json
{
  "function": "process_contract",
  "references": [
    {
      "file": "src/main.4gl",
      "line": 42,
      "caller": "main_handler",
      "context": "CALL process_contract(c)"
    },
    {
      "file": "src/utils.4gl",
      "line": 156,
      "caller": "validate_data",
      "context": "CALL process_contract(rec)"
    }
  ],
  "total_references": 2
}
```

---

#### 1.2 Call Hierarchy / Call Graph
**Current State:** Partially implemented (call graph extraction exists)  
**Use Case:** Understanding code flow, tracing execution paths  
**Plugin Need:** Visualize which functions call which other functions  
**Implementation:** Enhanced query layer to traverse call graph

**Proposed API:**
```bash
# Get all functions called by a function
bash query.sh get-callees "function_name"

# Get all functions that call a function
bash query.sh get-callers "function_name"

# Get full call hierarchy (depth-limited)
bash query.sh call-hierarchy "function_name" --depth 3
```

**Output Format:**
```json
{
  "function": "main_handler",
  "callees": [
    {
      "name": "validate_input",
      "file": "src/validation.4gl",
      "line": 10,
      "calls_count": 1
    },
    {
      "name": "process_contract",
      "file": "src/processing.4gl",
      "line": 45,
      "calls_count": 2
    }
  ],
  "depth": 1
}
```

---

#### 1.3 Code Search with Pattern Matching
**Current State:** Not implemented  
**Use Case:** Find code patterns, locate specific implementations  
**Plugin Need:** Search across codebase for regex patterns  
**Implementation:** Query layer with regex support

**Proposed API:**
```bash
# Search for pattern in function names
bash query.sh search-functions "get_*"

# Search for pattern in code (requires full parsing)
bash query.sh search-pattern "LIKE.*contract"

# Search in specific file
bash query.sh search-file "src/main.4gl" "CALL.*process"
```

**Output Format:**
```json
{
  "pattern": "get_*",
  "matches": [
    {
      "file": "src/data.4gl",
      "line": 15,
      "name": "get_account",
      "type": "function"
    },
    {
      "file": "src/data.4gl",
      "line": 42,
      "name": "get_contract",
      "type": "function"
    }
  ],
  "total_matches": 2
}
```

---

#### 1.4 Code Statistics / Metrics Summary
**Current State:** Metrics extracted but no summary API  
**Use Case:** Project health overview, complexity analysis  
**Plugin Need:** Quick statistics on codebase  
**Implementation:** Aggregate metrics queries

**Proposed API:**
```bash
# Get project-wide statistics
bash query.sh statistics

# Get statistics for specific file
bash query.sh file-statistics "src/main.4gl"

# Get statistics for specific function
bash query.sh function-statistics "process_contract"
```

**Output Format:**
```json
{
  "project_statistics": {
    "total_files": 42,
    "total_functions": 156,
    "total_lines_of_code": 45230,
    "average_function_size": 290,
    "average_complexity": 3.2,
    "functions_with_high_complexity": 12,
    "functions_with_many_parameters": 8
  }
}
```

---

### Priority 2: Important Enhancements

#### 2.1 Batch Query Operations
**Current State:** Partially implemented  
**Use Case:** Retrieve multiple pieces of information in one call  
**Plugin Need:** Reduce round-trips for complex queries  
**Implementation:** Batch query handler

**Proposed API:**
```bash
# Execute multiple queries in one call
bash query.sh batch --queries queries.json

# Or via Python
python3 scripts/batch_query_handler.py workspace.db queries.json
```

**Input Format:**
```json
{
  "queries": [
    {"type": "find-function", "name": "process_contract"},
    {"type": "get-signature", "name": "validate_input"},
    {"type": "find-references", "name": "main_handler"}
  ]
}
```

**Output Format:**
```json
{
  "results": [
    {"query_id": 0, "result": {...}},
    {"query_id": 1, "result": {...}},
    {"query_id": 2, "result": {...}}
  ]
}
```

---

#### 2.2 Pagination for Large Result Sets
**Current State:** Implemented  
**Use Case:** Handle large codebases without memory issues  
**Plugin Need:** Retrieve results in chunks  
**Implementation:** Already exists, ensure consistency across all queries

**Proposed API:**
```bash
# Query with pagination
bash query.sh find-references "function_name" --page 1 --page-size 50

# Get next page
bash query.sh find-references "function_name" --page 2 --page-size 50
```

---

#### 2.3 Type-Aware Queries
**Current State:** Type resolution implemented, queries not yet built  
**Use Case:** Find functions working with specific types  
**Plugin Need:** Query by data type  
**Implementation:** Query layer for type-resolved data

**Proposed API:**
```bash
# Find all functions using a specific table
bash query.sh functions-using-table "contract"

# Find all functions with specific parameter type
bash query.sh functions-with-type "LIKE account.*"

# Find type mismatches
bash query.sh type-mismatches
```

**Output Format:**
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

---

### Priority 3: Nice-to-Have Features

#### 3.1 Incremental Compilation Support
**Current State:** Not implemented  
**Use Case:** Faster compilation for large projects  
**Plugin Need:** Track file changes, compile only modified files  
**Implementation:** File modification tracking

---

#### 3.2 Parallel Query Execution
**Current State:** Not implemented  
**Use Case:** Faster multi-query operations  
**Plugin Need:** Execute independent queries in parallel  
**Implementation:** Async query execution

---

#### 3.3 LSP Server Implementation
**Current State:** Not implemented  
**Use Case:** IDE-agnostic integration  
**Plugin Need:** Standard LSP protocol support  
**Implementation:** Separate LSP server wrapping genero-tools

---

## Implementation Roadmap

### Phase 2a: Reference Finding & Call Hierarchy (Recommended Next)
**Effort:** 2-3 days  
**Impact:** High - enables refactoring workflows  
**Dependencies:** Existing call graph data

**Tasks:**
1. Implement `find-references` query
2. Implement `get-callees` query
3. Implement `get-callers` query
4. Add shell command wrappers
5. Create tests
6. Update documentation

---

### Phase 2b: Code Search
**Effort:** 1-2 days  
**Impact:** Medium - useful for exploration  
**Dependencies:** None

**Tasks:**
1. Implement pattern matching in query layer
2. Add regex support
3. Add shell command wrappers
4. Create tests
5. Update documentation

---

### Phase 2c: Statistics & Metrics Queries
**Effort:** 1 day  
**Impact:** Medium - useful for analysis  
**Dependencies:** Existing metrics data

**Tasks:**
1. Implement aggregation queries
2. Add shell command wrappers
3. Create tests
4. Update documentation

---

### Phase 2d: Type-Aware Queries
**Effort:** 1-2 days  
**Impact:** High - enables type-based analysis  
**Dependencies:** Phase 1c (type resolution) - already complete

**Tasks:**
1. Implement type-based queries
2. Add shell command wrappers
3. Create tests
4. Update documentation

---

## What NOT to Implement

The following items from the audit are **Vim/Neovim plugin internals** and not relevant to genero-tools:

- Compiler integration (fglcomp execution) - plugin responsibility
- SVN integration - plugin responsibility
- Snippet management - plugin responsibility
- Hint system - plugin responsibility
- Debug streaming - plugin responsibility
- Lua API - plugin responsibility
- Display modes (quickfix, popup, split) - plugin responsibility
- Keybindings - plugin responsibility
- Configuration management - plugin responsibility
- Error handling/display - plugin responsibility

These are all UI/editor concerns that belong in the plugin, not in genero-tools.

---

## Success Criteria

For each new feature:
1. ✅ Query executes in <100ms for typical codebases
2. ✅ Handles pagination for large result sets
3. ✅ Returns consistent JSON format
4. ✅ Includes comprehensive tests (>90% coverage)
5. ✅ Documented with examples
6. ✅ No breaking changes to existing queries

---

## Summary

**Recommended Implementation Order:**
1. **Phase 2a:** Find References & Call Hierarchy (highest value)
2. **Phase 2b:** Code Search (fundamental feature)
3. **Phase 2c:** Statistics & Metrics (useful analysis)
4. **Phase 2d:** Type-Aware Queries (leverages Phase 1 work)

**Total Estimated Effort:** 5-8 days for all Priority 1 & 2 features

**Expected Outcome:** Genero-tools becomes a comprehensive codebase analysis platform with IDE-ready APIs for refactoring, navigation, and analysis workflows.

