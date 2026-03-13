# Genero Function Signatures - Project Specification

## Project Mission

**Build a comprehensive codebase analysis and indexing system that extracts, organizes, and exposes rich metadata about Genero/4GL codebases to enable:**

1. **IDE/Editor Integration** - Vim plugins, VS Code extensions, and other tools for code navigation, search, and autocompletion
2. **AI-Powered Code Review** - Automated analysis agents that can review new functions/files against codebase patterns and best practices
3. **Developer Tooling** - Command-line tools for impact analysis, refactoring support, and codebase understanding
4. **Architectural Analysis** - Understanding code structure, dependencies, and quality metrics

## Core Principles

1. **Comprehensive Metadata** - Extract not just signatures, but context, relationships, and metrics
2. **Fast Queryability** - All data indexed and queryable in <100ms for typical codebases
3. **AI-Ready Format** - Output structured data that AI agents can consume for analysis and decision-making
4. **No External Dependencies** - Use only built-in tools (Python, SQLite, Bash)
5. **Backward Compatibility** - Never break existing functionality when adding features

## What We Extract

### Current (Phase 0 - Complete)

- ✅ **Function Signatures** - Names, parameters, return types, line numbers
- ✅ **Module Dependencies** - Which files are in which modules (L4GLS, U4GLS, 4GLS)
- ✅ **Call Graphs** - Which functions call which other functions
- ✅ **File Metadata** - Code references (tickets), authors, change history

### Next Priority (Phase 1)

- 🔄 **Type Resolution** - Map called function names to actual function signatures
- 🔄 **Function Metrics** - Complexity, parameter count, return count, line count, call depth
- 🔄 **Dead Code Detection** - Functions never called anywhere
- 🔄 **Type Validation** - Detect type mismatches and unresolved calls

### Future (Phase 2+)

- ⏳ **Enhanced Type Parser** - LIKE types, RECORD types, complex types
- ⏳ **Database Schema Integration** - Parse and validate against actual schema
- ⏳ **Circular Dependency Detection** - Find problematic call cycles
- ⏳ **Code Duplication** - Identify similar/duplicate functions

## Data Model

### Core Entities

```
File
├── Functions
│   ├── Signature (name, parameters, returns)
│   ├── Location (file, line numbers)
│   ├── Calls (list of called functions)
│   ├── Metrics (complexity, parameter count, etc.)
│   └── Metadata (authors, references)
├── Modules (which modules use this file)
└── Metadata (authors, references, change history)

Module
├── Files (L4GLS, U4GLS, 4GLS)
├── Functions (all functions in module)
└── Dependencies (other modules this depends on)

Call Graph
├── Caller (function A)
├── Callee (function B)
├── Line Number (where the call happens)
└── Resolved Signature (full signature of B)
```

### Output Formats

1. **JSON** - Human-readable, complete data export
2. **SQLite** - Indexed, queryable, efficient for large codebases
3. **Query API** - Python functions and shell commands for common operations

## Use Cases

### Use Case 1: Vim Plugin - Function Lookup

**Scenario:** Developer types `:VimFunctionLookup my_function` in Vim

**Data Needed:**
- Function signature (parameters, returns)
- File location (for jumping to definition)
- Who calls this function (impact analysis)
- What this function calls (dependencies)
- Metrics (complexity, if it's dead code)

**Query:** `get-function-full-context my_function`

**Output:**
```json
{
  "name": "my_function",
  "signature": "my_function(param1 INTEGER, param2 STRING): result DECIMAL",
  "file": "./src/utils.4gl",
  "line": {"start": 42, "end": 87},
  "metrics": {
    "parameters": 2,
    "returns": 1,
    "lines": 45,
    "calls_count": 3,
    "called_by_count": 5
  },
  "calls": [
    {"name": "validate_input", "line": 50},
    {"name": "process_data", "line": 65},
    {"name": "log_result", "line": 80}
  ],
  "called_by": [
    {"name": "main_handler", "file": "./src/main.4gl", "line": 120},
    {"name": "batch_processor", "file": "./src/batch.4gl", "line": 45}
  ],
  "modules": ["core", "utils"],
  "authors": ["John Smith", "Jane Doe"],
  "references": ["PRB-299", "EH100512"]
}
```

### Use Case 2: AI Code Review Agent

**Scenario:** New function added to codebase, AI agent reviews it

**Data Needed:**
- Function signature and metrics
- Similar functions in codebase (for pattern matching)
- Functions it calls (to validate they exist and types match)
- Functions that call it (to understand impact)
- Code references and authors (for context)
- Complexity metrics (to flag overly complex functions)

**Queries:**
- `get-function-full-context new_function` - Get everything about the new function
- `find-similar-functions new_function` - Find functions with similar signatures
- `find-unresolved-calls new_function` - Check if it calls non-existent functions
- `find-functions-by-parameter-count 5` - Find other functions with 5 parameters
- `get-call-chain new_function` - Understand full dependency tree

**Output:** Structured data for AI agent to analyze and produce review report

### Use Case 3: Impact Analysis

**Scenario:** Developer wants to refactor a function, needs to know what breaks

**Data Needed:**
- All functions that call this function (direct dependents)
- All functions those call (transitive dependents)
- Metrics to understand scope of change
- Type information to detect potential mismatches

**Query:** `get-impact-analysis function_name`

**Output:**
```json
{
  "function": "process_order",
  "direct_dependents": 12,
  "transitive_dependents": 47,
  "affected_modules": ["core", "orders", "billing"],
  "call_chain": [
    {
      "depth": 1,
      "functions": ["handle_order", "validate_order", "submit_order"]
    },
    {
      "depth": 2,
      "functions": ["main_handler", "batch_processor", "api_endpoint"]
    }
  ]
}
```

### Use Case 4: Dead Code Detection

**Scenario:** Codebase cleanup - find unused functions

**Data Needed:**
- All functions in codebase
- Which functions are called
- Which functions are never called

**Query:** `find-dead-code`

**Output:**
```json
{
  "dead_functions": [
    {
      "name": "old_utility",
      "file": "./src/utils.4gl",
      "line": 150,
      "last_modified": "2024-01-15",
      "last_author": "John Smith"
    }
  ],
  "count": 3
}
```

## Query Categories

### Essential Queries (MVP)

1. **Function Context** - `get-function-full-context <name>`
2. **Impact Analysis** - `get-impact-analysis <name>`
3. **Dead Code** - `find-dead-code`
4. **Unresolved Calls** - `find-unresolved-calls <file>`
5. **Similar Functions** - `find-similar-functions <name>`

### Extended Queries (Phase 1+)

6. **Metrics-based** - `find-functions-by-parameter-count`, `find-complex-functions`
7. **Pattern-based** - `find-functions-matching-pattern <regex>`
8. **Type-based** - `find-functions-with-type <type>`
9. **Module-scoped** - `find-functions-in-module`, `find-module-dependencies`
10. **Export** - `export-function-report`, `generate-codebase-report`

## Implementation Phases

### Phase 0 (Complete ✅)
- Function signature extraction
- Module dependency parsing
- Call graph generation
- File header parsing (references, authors)

### Phase 1 (Next - Type Resolution & Metrics)
- Resolve called function names to signatures
- Extract function metrics (complexity, parameter count, etc.)
- Dead code detection
- Unresolved call detection
- Similar function detection
- New query layer for AI agents

### Phase 2 (Enhanced Type Support)
- LIKE type resolution
- RECORD type parsing
- Type validation
- Database schema integration

### Phase 3 (Advanced Analysis)
- Circular dependency detection
- Code duplication analysis
- Performance metrics
- Visualization exports

## Success Criteria

### For Vim Plugin Integration
- [ ] Can retrieve full function context in <100ms
- [ ] Can find similar functions for autocompletion
- [ ] Can show impact analysis on hover
- [ ] Can navigate to function definitions with context

### For AI Code Review
- [ ] Can extract all needed context for a new function
- [ ] Can detect unresolved calls and type mismatches
- [ ] Can identify similar functions for pattern matching
- [ ] Can provide complexity metrics for prioritization

### For General Tooling
- [ ] All queries execute in <100ms on typical codebases
- [ ] Dead code detection works accurately
- [ ] Impact analysis is complete and correct
- [ ] All data is queryable via CLI, Python API, and SQL

### For Codebase Understanding
- [ ] Can generate comprehensive function reports
- [ ] Can visualize module dependencies
- [ ] Can identify architectural patterns
- [ ] Can track code ownership and expertise

## Data Quality & Validation

### Validation Rules

1. **No Unresolved Calls** - Every called function should exist in codebase
2. **Type Consistency** - Function calls should match parameter types
3. **No Dead Code** - Functions should be called somewhere (or marked as entry points)
4. **Metadata Completeness** - All functions should have author/reference info

### Reporting

- Generate validation reports showing issues
- Flag functions that violate rules
- Provide suggestions for fixes

## Integration Points

### Vim Plugin
- Query API for function lookup
- Metrics for complexity highlighting
- Call graph for navigation

### AI Code Review Agent
- Full context queries
- Metrics for decision-making
- Validation reports for issues

### Build Pipeline
- Generate reports as build artifacts
- Fail build on critical issues (unresolved calls)
- Track metrics over time

### Documentation Generation
- Export function reports
- Generate API documentation
- Create architecture diagrams

## Non-Goals

- ❌ We do NOT execute code or run tests
- ❌ We do NOT modify source files
- ❌ We do NOT provide IDE-specific plugins (we provide data for plugins to use)
- ❌ We do NOT replace version control (git)
- ❌ We do NOT provide real-time analysis (batch processing only)

## Technical Constraints

- **No external dependencies** - Only Python 3.6+, SQLite, Bash, standard Unix tools
- **Performance** - Queries must execute in <100ms
- **Scalability** - Must handle codebases with 100K+ functions
- **Backward compatibility** - Never break existing queries or data formats
- **Robustness** - Graceful error handling, no crashes on malformed input

## Documentation Requirements

- README - Quick start and overview
- ARCHITECTURE - System design and components
- QUERYING - Query reference and examples
- INTEGRATION - How to use with Vim, AI agents, etc.
- API - Python API reference
- EXAMPLES - Real-world usage examples

## Next Steps

1. ✅ Create this specification
2. 🔄 Review existing documentation for consistency
3. 🔄 Create Phase 1 implementation spec
4. 🔄 Begin Phase 1 implementation
