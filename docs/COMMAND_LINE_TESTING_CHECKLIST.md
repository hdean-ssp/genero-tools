# Command-Line Testing Checklist

**Purpose:** Sequential testing checklist for new users to verify all genero-tools command-line functionality works correctly.

**Time Required:** ~15 minutes  
**Prerequisites:** Bash, Python 3.6+, sample codebase (included)

---

## Setup Phase

Before running any tests, prepare your environment:

```bash
# Navigate to genero-tools directory
cd /path/to/genero-tools

# Verify scripts are executable
chmod +x generate_all.sh src/*.sh query.sh scripts/*.py

# Verify sample codebase exists
ls -la tests/sample_codebase/
```

---

## Test Execution Checklist

### ✓ Test 1: Generate All Metadata
**Command:** `bash generate_all.sh tests/sample_codebase`  
**Expected Output:** 4 files created
- [ ] `workspace.json` created (15-20 KB)
- [ ] `modules.json` created (2-5 KB)
- [ ] `codebase_index.json` created (15-20 KB)
- [ ] `workspace_resolved.json` created (15-20 KB)

**Verification:**
```bash
ls -lh workspace.json modules.json codebase_index.json workspace_resolved.json
```

---

### ✓ Test 2: Create SQLite Databases
**Command:** `bash query.sh create-dbs`  
**Expected Output:** 2 database files created
- [ ] `workspace.db` created (70-100 KB)
- [ ] `modules.db` created (10-20 KB)

**Verification:**
```bash
ls -lh workspace.db modules.db
sqlite3 workspace.db "SELECT COUNT(*) FROM functions;"
```

---

### ✓ Test 3: Find Specific Function
**Command:** `bash query.sh find-function "calculate_total"`  
**Expected Output:** JSON object with function details
- [ ] Function name: `calculate_total`
- [ ] File path: `tests/sample_codebase/simple_functions.4gl`
- [ ] Parameters: 2 (amount, tax_rate)
- [ ] Returns: 1 (total)
- [ ] Complexity: 3
- [ ] Lines of code: 8

**Variations to Test:**
```bash
bash query.sh find-function "get_value"
bash query.sh find-function "process_data"
bash query.sh find-function "nonexistent_function"  # Should return empty
```

---

### ✓ Test 4: Search Functions by Pattern
**Command:** `bash query.sh search-functions "get_*"`  
**Expected Output:** Array of functions matching pattern
- [ ] Returns multiple functions (3+)
- [ ] All function names start with "get_"
- [ ] Each has file path, complexity, LOC

**Variations to Test:**
```bash
bash query.sh search-functions "process_*"
bash query.sh search-functions "*_total"
bash query.sh search-functions "*"  # All functions
```

---

### ✓ Test 5: List Functions in File
**Command:** `bash query.sh list-file-functions "tests/sample_codebase/simple_functions.4gl"`  
**Expected Output:** Array of all functions in file
- [ ] Returns 3+ functions
- [ ] Each has name, line numbers, complexity, LOC

**Variations to Test:**
```bash
bash query.sh list-file-functions "tests/sample_codebase/complex_types.4gl"
bash query.sh list-file-functions "tests/sample_codebase/lib/complex_types.4gl"
```

---

### ✓ Test 6: Find Function Dependencies (What It Calls)
**Command:** `bash query.sh find-function-dependencies "calculate_total"`  
**Expected Output:** Array of functions it calls
- [ ] Returns array (may be empty if no dependencies)
- [ ] Each entry has function name and file path

**Variations to Test:**
```bash
bash query.sh find-function-dependencies "process_data"
bash query.sh find-function-dependencies "get_value"
bash query.sh find-function-dependencies "simple_function"  # No dependencies
```

---

### ✓ Test 7: Find Function Dependents (What Calls It)
**Command:** `bash query.sh find-function-dependents "calculate_total"`  
**Expected Output:** Array of functions that call it
- [ ] Returns array (may be empty if unused)
- [ ] Each entry has function name and file path

**Variations to Test:**
```bash
bash query.sh find-function-dependents "process_data"
bash query.sh find-function-dependents "get_value"
bash query.sh find-function-dependents "unused_function"  # No dependents
```

---

### ✓ Test 8: Find Module
**Command:** `bash query.sh find-module "core"`  
**Expected Output:** Module object with details
- [ ] Module name: `core`
- [ ] File path: `tests/sample_codebase/modules/test.m3`
- [ ] Functions: array of function names

**Variations to Test:**
```bash
bash query.sh find-module "utils"
bash query.sh find-module "test"
bash query.sh find-module "nonexistent"  # Should return empty
```

---

### ✓ Test 9: Search Modules by Pattern
**Command:** `bash query.sh search-modules "*"`  
**Expected Output:** Array of all modules
- [ ] Returns 3+ modules
- [ ] Each has name, file path, function count

**Variations to Test:**
```bash
bash query.sh search-modules "core*"
bash query.sh search-modules "*utils"
bash query.sh search-modules "test*"
```

---

### ✓ Test 10: Find Functions in Module
**Command:** `bash query.sh find-functions-in-module "core"`  
**Expected Output:** Array of functions in module
- [ ] Returns 1+ functions
- [ ] Each has name, file path, complexity

**Variations to Test:**
```bash
bash query.sh find-functions-in-module "utils"
bash query.sh find-functions-in-module "test"
```

---

### ✓ Test 11: Find Reference
**Command:** `bash query.sh find-reference "PRB-299"`  
**Expected Output:** Array of files containing reference
- [ ] Returns 1+ files
- [ ] Each has file path and context

**Variations to Test:**
```bash
bash query.sh find-reference "EH100512"
bash query.sh find-reference "BUG-123"
bash query.sh find-reference "NONEXISTENT-999"  # Not found
```

---

### ✓ Test 12: Search References by Pattern
**Command:** `bash query.sh search-references "100512"`  
**Expected Output:** Array of matching references
- [ ] Returns 1+ results
- [ ] Each has file path and reference

**Variations to Test:**
```bash
bash query.sh search-references "299"
bash query.sh search-references "EH"
bash query.sh search-references "PRB"
```

---

### ✓ Test 13: Find Author
**Command:** `bash query.sh find-author "Rich"`  
**Expected Output:** Array of files by author
- [ ] Returns 1+ files
- [ ] Each has file path and modification count

**Variations to Test:**
```bash
bash query.sh find-author "Chilly"
bash query.sh find-author "John"
bash query.sh find-author "R"  # Partial match
```

---

### ✓ Test 14: Get File References
**Command:** `bash query.sh file-references "tests/sample_codebase/simple_functions.4gl"`  
**Expected Output:** Array of references in file
- [ ] Returns 1+ references
- [ ] Each has reference ID and context

**Variations to Test:**
```bash
bash query.sh file-references "tests/sample_codebase/complex_types.4gl"
bash query.sh file-references "./simple_functions.4gl"
```

---

### ✓ Test 15: Get File Authors
**Command:** `bash query.sh file-authors "tests/sample_codebase/simple_functions.4gl"`  
**Expected Output:** Array of authors for file
- [ ] Returns 1+ authors
- [ ] Each has author name and modification count

**Variations to Test:**
```bash
bash query.sh file-authors "tests/sample_codebase/complex_types.4gl"
bash query.sh file-authors "./simple_functions.4gl"
```

---

### ✓ Test 16: Get Author Expertise
**Command:** `bash query.sh author-expertise "Rich"`  
**Expected Output:** Object with expertise areas
- [ ] Returns expertise areas
- [ ] Each area has file count and modification count

**Variations to Test:**
```bash
bash query.sh author-expertise "Chilly"
bash query.sh author-expertise "John"
```

---

### ✓ Test 17: Find Unresolved Types
**Command:** `bash query.sh unresolved-types`  
**Expected Output:** Array of unresolved type references
- [ ] Returns array (may be empty if all resolved)
- [ ] Each has function name, parameter name, type

**Variations to Test:**
```bash
bash query.sh unresolved-types --filter missing_table
bash query.sh unresolved-types --filter missing_column
bash query.sh unresolved-types --limit 5
bash query.sh unresolved-types --limit 5 --offset 0
```

---

### ✓ Test 18: Validate Types
**Command:** `bash query.sh validate-types`  
**Expected Output:** Validation result
- [ ] Returns success or error message
- [ ] Shows validation statistics

---

### ✓ Test 19: Find Function with Resolved Types
**Command:** `bash query.sh find-function-resolved "process_contract"`  
**Expected Output:** Function with resolved type information
- [ ] Returns function object
- [ ] Parameters show resolved types (if LIKE references)
- [ ] Shows resolved columns and types

**Variations to Test:**
```bash
bash query.sh find-function-resolved "calculate_total"
bash query.sh find-function-resolved "process_data"
bash query.sh find-function-resolved "simple_function"  # No LIKE refs
```

---

### ✓ Test 20: Vim Format Output
**Command:** `bash query.sh find-function "calculate_total" --format=vim`  
**Expected Output:** Single-line format suitable for Vim
- [ ] Returns single line (no newlines)
- [ ] Contains function name, file, line number
- [ ] Suitable for editor integration

**Variations to Test:**
```bash
bash query.sh search-functions "get_*" --format=vim
bash query.sh search-functions "*" --format=vim --filter=functions-only
```

---

### ✓ Test 21: Vim Hover Format Output
**Command:** `bash query.sh find-function "calculate_total" --format=vim-hover`  
**Expected Output:** Multi-line format for hover tooltips
- [ ] Returns formatted text with line breaks
- [ ] Shows function signature, parameters, returns
- [ ] Shows complexity and LOC

**Variations to Test:**
```bash
bash query.sh search-functions "get_*" --format=vim-hover
bash query.sh search-functions "get_*" --format=vim-hover --filter=no-metrics
```

---

### ✓ Test 22: Vim Completion Format Output
**Command:** `bash query.sh search-functions "*" --format=vim-completion`  
**Expected Output:** Tab-separated format for completion
- [ ] Returns tab-separated values
- [ ] Suitable for completion menus

**Variations to Test:**
```bash
bash query.sh search-functions "get_*" --format=vim-completion
bash query.sh search-functions "*" --format=vim-completion --filter=functions-only
```

---

### ✓ Test 23: Batch Query
**Command:** Create `queries.json` and run batch query
**Setup:**
```bash
cat > queries.json << 'EOF'
{
  "queries": [
    {"command": "find-function", "args": ["calculate_total"]},
    {"command": "search-functions", "args": ["get_*"]},
    {"command": "find-function-dependencies", "args": ["calculate_total"]}
  ]
}
EOF
```

**Command:** `bash query.sh batch-query queries.json`  
**Expected Output:** Array of results for each query
- [ ] Returns 3 results
- [ ] Each result corresponds to a query
- [ ] All results are valid JSON

**Variations to Test:**
```bash
bash query.sh batch-query queries.json --output results.json
cat results.json  # Verify output file created
```

---

### ✓ Test 24: Error Handling - Non-Existent Function
**Command:** `bash query.sh find-function "nonexistent_function_xyz"`  
**Expected Output:** Empty result or error message
- [ ] Returns gracefully (no crash)
- [ ] Returns empty array or null

---

### ✓ Test 25: Error Handling - Invalid Pattern
**Command:** `bash query.sh search-functions "[invalid"`  
**Expected Output:** Error message or empty result
- [ ] Returns gracefully (no crash)
- [ ] Shows helpful error message

---

### ✓ Test 26: Error Handling - Missing Arguments
**Command:** `bash query.sh find-function`  
**Expected Output:** Error message with usage
- [ ] Shows error message
- [ ] Shows correct usage

---

### ✓ Test 27: Error Handling - Unknown Command
**Command:** `bash query.sh unknown-command`  
**Expected Output:** Error message with available commands
- [ ] Shows error message
- [ ] Lists available commands

---

### ✓ Test 28: Performance - Exact Lookup
**Command:** `time bash query.sh find-function "calculate_total"`  
**Expected Output:** Result in <1ms
- [ ] Command completes quickly
- [ ] Real time < 100ms

---

### ✓ Test 29: Performance - Pattern Search
**Command:** `time bash query.sh search-functions "get_*"`  
**Expected Output:** Result in <10ms
- [ ] Command completes quickly
- [ ] Real time < 100ms

---

### ✓ Test 30: Performance - Large Result Set
**Command:** `time bash query.sh search-functions "*"`  
**Expected Output:** Result in <100ms
- [ ] Command completes quickly
- [ ] Real time < 500ms

---

## Summary

**Total Tests:** 30  
**Estimated Time:** 15 minutes

### Test Results Template

```
Test Results - [DATE]
=====================

Setup Phase:
- [ ] Scripts executable
- [ ] Sample codebase present

Generation Phase:
- [ ] Test 1: Generate metadata ✓
- [ ] Test 2: Create databases ✓

Function Queries (Tests 3-5):
- [ ] Test 3: Find function ✓
- [ ] Test 4: Search functions ✓
- [ ] Test 5: List file functions ✓

Dependency Queries (Tests 6-7):
- [ ] Test 6: Find dependencies ✓
- [ ] Test 7: Find dependents ✓

Module Queries (Tests 8-10):
- [ ] Test 8: Find module ✓
- [ ] Test 9: Search modules ✓
- [ ] Test 10: Find functions in module ✓

Reference & Author Queries (Tests 11-16):
- [ ] Test 11: Find reference ✓
- [ ] Test 12: Search references ✓
- [ ] Test 13: Find author ✓
- [ ] Test 14: File references ✓
- [ ] Test 15: File authors ✓
- [ ] Test 16: Author expertise ✓

Type Resolution Queries (Tests 17-19):
- [ ] Test 17: Unresolved types ✓
- [ ] Test 18: Validate types ✓
- [ ] Test 19: Resolved types ✓

Output Formats (Tests 20-22):
- [ ] Test 20: Vim format ✓
- [ ] Test 21: Vim hover format ✓
- [ ] Test 22: Vim completion format ✓

Advanced Features (Tests 23-30):
- [ ] Test 23: Batch query ✓
- [ ] Test 24: Error handling (non-existent) ✓
- [ ] Test 25: Error handling (invalid pattern) ✓
- [ ] Test 26: Error handling (missing args) ✓
- [ ] Test 27: Error handling (unknown command) ✓
- [ ] Test 28: Performance (exact lookup) ✓
- [ ] Test 29: Performance (pattern search) ✓
- [ ] Test 30: Performance (large result set) ✓

Total Passed: __/30
Total Failed: __/30
```

---

## Quick Reference

### Most Common Commands

```bash
# Generate metadata (one-time setup)
bash generate_all.sh tests/sample_codebase
bash query.sh create-dbs

# Find a specific function
bash query.sh find-function "my_function"

# Search for functions by pattern
bash query.sh search-functions "get_*"

# Understand function impact
bash query.sh find-function-dependencies "my_function"
bash query.sh find-function-dependents "my_function"

# Find code references
bash query.sh find-reference "PRB-299"

# Get author information
bash query.sh find-author "John"
bash query.sh author-expertise "John"
```

### Troubleshooting

| Issue | Solution |
|-------|----------|
| "Database not found" | Run `bash query.sh create-dbs` |
| "No results" | Verify database has data: `sqlite3 workspace.db "SELECT COUNT(*) FROM functions;"` |
| "Permission denied" | Make scripts executable: `chmod +x *.sh src/*.sh` |
| "Python error" | Verify Python 3.6+: `python3 --version` |
| "Slow queries" | Recreate database: `bash query.sh create-dbs` |

---

## Next Steps

After completing all tests:

1. **Read Full Documentation**
   - [COMMAND_LINE_TESTING_GUIDE.md](COMMAND_LINE_TESTING_GUIDE.md) - Comprehensive guide with all options
   - [QUERYING.md](QUERYING.md) - Complete query reference
   - [FEATURES.md](FEATURES.md) - Feature overview

2. **Integrate with Your Tools**
   - Use genero-tools with your IDE/editor
   - See [VIM_PLUGIN_INTEGRATION_GUIDE.md](VIM_PLUGIN_INTEGRATION_GUIDE.md) for Vim integration

3. **Automate Your Workflow**
   - Create custom query scripts
   - Integrate with CI/CD pipelines
   - Use batch queries for bulk analysis

4. **Explore Advanced Features**
   - Type resolution for LIKE references
   - Code quality metrics
   - Impact analysis for refactoring

