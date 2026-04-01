# Command-Line Testing Guide

Complete reference for testing all genero-tools command-line functionality with practical examples, advanced scenarios, and execution automation.

## Quick Start

```bash
# Setup (one-time)
bash generate_all.sh tests/sample_codebase
bash query.sh create-dbs

# Test basic queries
bash query.sh find-function "calculate_total"
bash query.sh search-functions "get_*"
bash query.sh find-function-dependencies "calculate_total"
```

---

## Prerequisites

- Genero codebase with `.4gl` and/or `.m3` files
- Python 3.6+
- Bash shell
- Standard Unix utilities (find, sed, awk, date)

For testing: Use `tests/sample_codebase/` (8 .4gl files, 9 .m3 files, 1 .sch file)

---

## Phase 1: Generation Commands

### 1.1 Generate All Metadata

```bash
bash generate_all.sh tests/sample_codebase
```

**Output:**
- `workspace.json` - Function signatures
- `workspace.db` - SQLite database
- `modules.json` - Module dependencies
- `modules.db` - SQLite module database
- `workspace_resolved.json` - Type-resolved signatures (if schema found)

**Variations:**
```bash
# Verbose output
VERBOSE=1 bash generate_all.sh tests/sample_codebase

# Explicit schema file
bash generate_all.sh tests/sample_codebase tests/sample_codebase/schema.sch

# Custom output directory
cd /tmp && bash /path/to/generate_all.sh /path/to/codebase
```

### 1.2 Generate Function Signatures Only

```bash
bash src/generate_signatures.sh tests/sample_codebase
```

**Variations:**
```bash
# Single file
bash src/generate_signatures.sh tests/sample_codebase/simple_functions.4gl

# Specific directory
bash src/generate_signatures.sh tests/sample_codebase/lib

# Verbose
VERBOSE=1 bash src/generate_signatures.sh tests/sample_codebase
```

### 1.3 Generate Module Dependencies

```bash
bash src/generate_modules.sh tests/sample_codebase
```

**Variations:**
```bash
# Modules directory only
bash src/generate_modules.sh tests/sample_codebase/modules

# Verbose
VERBOSE=1 bash src/generate_modules.sh tests/sample_codebase
```

### 1.4 Create SQLite Databases

```bash
bash query.sh create-dbs
```

**Variations:**
```bash
# Signatures database only
bash query.sh create-signatures-db

# Modules database only
bash query.sh create-modules-db

# Custom location
SIGNATURES_DB=/tmp/custom.db bash query.sh create-signatures-db
```

---

## Phase 2: Function Queries

### 2.1 Find Function by Name

```bash
bash query.sh find-function "calculate_total"
```

**Variations:**
```bash
bash query.sh find-function "get_value"
bash query.sh find-function "process_data"
bash query.sh find-function "nonexistent_function"  # Returns empty
```

### 2.2 Search Functions by Pattern

```bash
bash query.sh search-functions "get_*"
```

**Variations:**
```bash
bash query.sh search-functions "process_*"
bash query.sh search-functions "*_total"
bash query.sh search-functions "*"
bash query.sh search-functions "GET_*"  # Case variations
```

### 2.3 List Functions in File

```bash
bash query.sh list-file-functions "tests/sample_codebase/simple_functions.4gl"
```

**Variations:**
```bash
bash query.sh list-file-functions "tests/sample_codebase/complex_types.4gl"
bash query.sh list-file-functions "tests/sample_codebase/lib/complex_types.4gl"
bash query.sh list-file-functions "nonexistent.4gl"  # Error handling
```

### 2.4 Find Function by Name and Path

```bash
bash query.sh find-function-by-name-and-path "calculate_total" "tests/sample_codebase/simple_functions.4gl"
```

**Variations:**
```bash
bash query.sh find-function-by-name-and-path "process_data" "tests/sample_codebase/complex_types.4gl"
bash query.sh find-function-by-name-and-path "calculate_total" "./simple_functions.4gl"
```

### 2.5 Find All Function Instances

```bash
bash query.sh find-all-function-instances "calculate_total"
```

**Variations:**
```bash
bash query.sh find-all-function-instances "process_data"
bash query.sh find-all-function-instances "get_value"
```

---

## Phase 3: Dependency Queries

### 3.1 Find Function Dependencies (Callees)

```bash
bash query.sh find-function-dependencies "calculate_total"
```

**Variations:**
```bash
bash query.sh find-function-dependencies "process_data"
bash query.sh find-function-dependencies "get_value"
bash query.sh find-function-dependencies "simple_function"  # No dependencies
```

### 3.2 Find Function Dependents (Callers)

```bash
bash query.sh find-function-dependents "calculate_total"
```

**Variations:**
```bash
bash query.sh find-function-dependents "process_data"
bash query.sh find-function-dependents "get_value"
bash query.sh find-function-dependents "unused_function"  # No dependents
```

### 3.3 Find Dead Code

```bash
bash query.sh find-dead-code
```

---

## Phase 4: Module Queries

### 4.1 Find Module

```bash
bash query.sh find-module "core"
```

**Variations:**
```bash
bash query.sh find-module "utils"
bash query.sh find-module "test"
bash query.sh find-module "nonexistent"  # Error handling
```

### 4.2 Search Modules

```bash
bash query.sh search-modules "core*"
```

**Variations:**
```bash
bash query.sh search-modules "*"
bash query.sh search-modules "test*"
bash query.sh search-modules "*utils"
```

### 4.3 List Modules in File

```bash
bash query.sh list-file-modules "test.m3"
```

**Variations:**
```bash
bash query.sh list-file-modules "multiline.m3"
bash query.sh list-file-modules "modules/test.m3"
```

### 4.4 Find Functions in Module

```bash
bash query.sh find-functions-in-module "core"
```

**Variations:**
```bash
bash query.sh find-functions-in-module "utils"
bash query.sh find-functions-in-module "test"
```

### 4.5 Find Module for Function

```bash
bash query.sh find-module-for-function "calculate_total"
```

**Variations:**
```bash
bash query.sh find-module-for-function "process_data"
bash query.sh find-module-for-function "get_value"
```

### 4.6 Find Functions Calling in Module

```bash
bash query.sh find-functions-calling-in-module "core" "calculate_total"
```

**Variations:**
```bash
bash query.sh find-functions-calling-in-module "utils" "process_data"
bash query.sh find-functions-calling-in-module "test" "get_value"
```

### 4.7 Find Module Dependencies

```bash
bash query.sh find-module-dependencies "core"
```

**Variations:**
```bash
bash query.sh find-module-dependencies "utils"
bash query.sh find-module-dependencies "test"
```

---

## Phase 5: Reference & Author Queries

### 5.1 Find Reference

```bash
bash query.sh find-reference "PRB-299"
```

**Variations:**
```bash
bash query.sh find-reference "EH100512"
bash query.sh find-reference "BUG-123"
bash query.sh find-reference "NONEXISTENT-999"  # Not found
```

### 5.2 Search References

```bash
bash query.sh search-references "100512"
```

**Variations:**
```bash
bash query.sh search-references "299"
bash query.sh search-references "EH"
bash query.sh search-references "PRB"
bash query.sh search-references "EH100512%"  # Explicit wildcard
```

### 5.3 Search Reference Prefix

```bash
bash query.sh search-reference-prefix "EH100512"
```

**Variations:**
```bash
bash query.sh search-reference-prefix "PRB"
bash query.sh search-reference-prefix "BUG-1"
```

### 5.4 Find Author

```bash
bash query.sh find-author "Rich"
```

**Variations:**
```bash
bash query.sh find-author "Chilly"
bash query.sh find-author "John"
bash query.sh find-author "R"  # Partial match
```

### 5.5 Get File References

```bash
bash query.sh file-references "tests/sample_codebase/simple_functions.4gl"
```

**Variations:**
```bash
bash query.sh file-references "tests/sample_codebase/complex_types.4gl"
bash query.sh file-references "./simple_functions.4gl"
```

### 5.6 Get File Authors

```bash
bash query.sh file-authors "tests/sample_codebase/simple_functions.4gl"
```

**Variations:**
```bash
bash query.sh file-authors "tests/sample_codebase/complex_types.4gl"
bash query.sh file-authors "./simple_functions.4gl"
```

### 5.7 Author Expertise

```bash
bash query.sh author-expertise "Rich"
```

**Variations:**
```bash
bash query.sh author-expertise "Chilly"
bash query.sh author-expertise "John"
```

### 5.8 Recent Changes

```bash
bash query.sh recent-changes 30
```

**Variations:**
```bash
bash query.sh recent-changes 7
bash query.sh recent-changes 1
bash query.sh recent-changes 365
bash query.sh recent-changes  # Default 30 days
```

---

## Phase 6: Type Resolution Queries

### 6.1 Find Function with Resolved Types

```bash
bash query.sh find-function-resolved "process_contract"
```

**Variations:**
```bash
bash query.sh find-function-resolved "calculate_total"
bash query.sh find-function-resolved "process_data"
bash query.sh find-function-resolved "simple_function"  # No LIKE refs
```

### 6.2 Find Unresolved Types

```bash
bash query.sh unresolved-types
```

**Variations:**
```bash
# Filter by error type
bash query.sh unresolved-types --filter missing_table
bash query.sh unresolved-types --filter missing_column
bash query.sh unresolved-types --filter invalid_pattern

# Pagination
bash query.sh unresolved-types --limit 10
bash query.sh unresolved-types --limit 10 --offset 5
bash query.sh unresolved-types --limit 20 --offset 0

# Combined
bash query.sh unresolved-types --filter missing_table --limit 5
```

### 6.3 Validate Types

```bash
bash query.sh validate-types
```

---

## Phase 7: Batch Queries

### 7.1 Batch Query from JSON

```bash
bash query.sh batch-query queries.json
```

**Variations:**
```bash
# With output file
bash query.sh batch-query queries.json --output results.json

# Alternative syntax
bash query.sh batch-query --input queries.json --output results.json

# Without output file (prints to stdout)
bash query.sh batch-query queries.json
```

**Sample queries.json:**
```json
{
  "queries": [
    {
      "command": "find-function",
      "args": ["calculate_total"]
    },
    {
      "command": "search-functions",
      "args": ["get_*"]
    },
    {
      "command": "find-function-dependencies",
      "args": ["calculate_total"]
    }
  ]
}
```

---

## Phase 8: Output Formats (Vim Integration)

### 8.1 Vim Format (Single-Line)

```bash
bash query.sh find-function "calculate_total" --format=vim
bash query.sh search-functions "get_*" --format=vim
bash query.sh search-functions "*" --format=vim --filter=functions-only
```

### 8.2 Vim Hover Format (Multi-Line)

```bash
bash query.sh find-function "calculate_total" --format=vim-hover
bash query.sh search-functions "get_*" --format=vim-hover
bash query.sh search-functions "get_*" --format=vim-hover --filter=no-metrics
```

### 8.3 Vim Completion Format (Tab-Separated)

```bash
bash query.sh search-functions "*" --format=vim-completion
bash query.sh search-functions "get_*" --format=vim-completion --filter=functions-only
bash query.sh search-functions "*" --format=vim-completion --filter=no-file-info
```

---

## Phase 9: Filter Options

### 9.1 Functions Only

```bash
bash query.sh search-functions "*" --filter=functions-only
bash query.sh search-functions "get_*" --format=vim --filter=functions-only
```

### 9.2 No Metrics

```bash
bash query.sh search-functions "get_*" --filter=no-metrics
bash query.sh search-functions "*" --format=vim-hover --filter=no-metrics
```

### 9.3 No File Info

```bash
bash query.sh search-functions "*" --filter=no-file-info
bash query.sh search-functions "get_*" --format=vim-completion --filter=no-file-info
```

---

## Phase 10: Error Handling

### 10.1 Non-Existent Database

```bash
SIGNATURES_DB=/tmp/nonexistent.db bash query.sh find-function "test"
```

### 10.2 Invalid Function Name

```bash
bash query.sh find-function ""
```

### 10.3 Invalid Pattern

```bash
bash query.sh search-functions "[invalid"
```

### 10.4 Missing Arguments

```bash
bash query.sh find-function
```

### 10.5 Unknown Command

```bash
bash query.sh unknown-command
```

---

## Phase 11: Performance Testing

### 11.1 Time Exact Lookup

```bash
time bash query.sh find-function "calculate_total"
```

Expected: <1ms

### 11.2 Time Pattern Search

```bash
time bash query.sh search-functions "get_*"
```

Expected: <10ms

### 11.3 Time Large Result Set

```bash
time bash query.sh search-functions "*"
```

### 11.4 Time Type Resolution

```bash
time bash query.sh find-function-resolved "process_contract"
```

Expected: <1ms

---

## Phase 12: Integration Testing

### 12.1 Complete Workflow

```bash
# 1. Generate metadata
bash generate_all.sh tests/sample_codebase

# 2. Create databases
bash query.sh create-dbs

# 3. Query the database
bash query.sh find-function "calculate_total"
bash query.sh search-functions "get_*"
bash query.sh find-function-dependencies "calculate_total"
```

### 12.2 Module and Function Integration

```bash
# Find module
bash query.sh find-module "core"

# Find functions in module
bash query.sh find-functions-in-module "core"

# Find dependencies for a function in the module
bash query.sh find-function-dependencies "calculate_total"
```

### 12.3 Reference and Author Integration

```bash
# Find reference
bash query.sh find-reference "PRB-299"

# Get file references
bash query.sh file-references "tests/sample_codebase/simple_functions.4gl"

# Get file authors
bash query.sh file-authors "tests/sample_codebase/simple_functions.4gl"

# Get author expertise
bash query.sh author-expertise "Rich"
```

---

## Advanced Scenarios

### Scenario 1: Complete Codebase Analysis

```bash
# Generate with verbose output
VERBOSE=1 bash generate_all.sh /path/to/large/codebase

# Check generated files
ls -lh workspace.json modules.json workspace.db modules.db

# Verify file sizes are reasonable
du -h workspace.json modules.json

# Get statistics
python3 -c "import json; data=json.load(open('workspace.json')); print(f'Files: {len(data)}, Total functions: {sum(len(v) for v in data.values())}')"

# Check database integrity
sqlite3 workspace.db "SELECT COUNT(*) as function_count FROM functions;"
```

### Scenario 2: Code Quality Assessment

```bash
# Find complex functions
bash query.sh search-functions "*" | python3 -c "
import json, sys
data = json.load(sys.stdin)
complex_funcs = [f for f in data if f.get('complexity', 0) > 10]
print(f'Complex functions (>10): {len(complex_funcs)}')
for f in sorted(complex_funcs, key=lambda x: x.get('complexity', 0), reverse=True)[:5]:
    print(f\"  {f['name']}: complexity={f.get('complexity', 0)}\")
"

# Find long functions
bash query.sh search-functions "*" | python3 -c "
import json, sys
data = json.load(sys.stdin)
long_funcs = [f for f in data if f.get('lines_of_code', 0) > 100]
print(f'Long functions (>100 LOC): {len(long_funcs)}')
for f in sorted(long_funcs, key=lambda x: x.get('lines_of_code', 0), reverse=True)[:5]:
    print(f\"  {f['name']}: LOC={f.get('lines_of_code', 0)}\")
"
```

### Scenario 3: Impact Analysis

```bash
# Find all functions a function calls
bash query.sh find-function-dependencies "update_database"

# Find all functions that call a function
bash query.sh find-function-dependents "validate_input"

# Find dead code
bash query.sh find-dead-code
```

### Scenario 4: Type Resolution Validation

```bash
# Get function with resolved types
bash query.sh find-function-resolved "process_contract"

# Find unresolved types
bash query.sh unresolved-types

# Filter by error type
bash query.sh unresolved-types --filter missing_table

# Validate consistency
bash query.sh validate-types
```

---

## Automated Test Execution

### Run All Tests

```bash
#!/bin/bash
# test_all_commands.sh

set -euo pipefail

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

PASSED=0
FAILED=0

test_command() {
    local description="$1"
    local command="$2"
    
    echo -n "Testing: $description... "
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC}"
        ((FAILED++))
    fi
}

# Phase 1: Generation
test_command "Generate all metadata" "bash generate_all.sh tests/sample_codebase"
test_command "Create databases" "bash query.sh create-dbs"

# Phase 2: Function queries
test_command "Find function" "bash query.sh find-function 'calculate_total'"
test_command "Search functions" "bash query.sh search-functions 'get_*'"
test_command "List file functions" "bash query.sh list-file-functions 'tests/sample_codebase/simple_functions.4gl'"

# Phase 3: Dependencies
test_command "Find dependencies" "bash query.sh find-function-dependencies 'calculate_total'"
test_command "Find dependents" "bash query.sh find-function-dependents 'calculate_total'"
test_command "Find dead code" "bash query.sh find-dead-code"

# Phase 4: Modules
test_command "Find module" "bash query.sh find-module 'core'"
test_command "Search modules" "bash query.sh search-modules '*'"

# Phase 5: References
test_command "Find reference" "bash query.sh find-reference 'PRB-299'"
test_command "Find author" "bash query.sh find-author 'Rich'"

# Phase 6: Type resolution
test_command "Validate types" "bash query.sh validate-types"
test_command "Find unresolved types" "bash query.sh unresolved-types"

# Phase 7: Formats
test_command "Vim format" "bash query.sh find-function 'calculate_total' --format=vim"
test_command "Vim hover format" "bash query.sh find-function 'calculate_total' --format=vim-hover"

echo ""
echo -e "Passed:  ${GREEN}$PASSED${NC}"
echo -e "Failed:  ${RED}$FAILED${NC}"
echo -e "Total:   $((PASSED + FAILED))"

[[ $FAILED -eq 0 ]] && exit 0 || exit 1
```

### Run Specific Category

```bash
#!/bin/bash
# test_category.sh

CATEGORY="${1:-all}"

case "$CATEGORY" in
    generation)
        bash generate_all.sh tests/sample_codebase
        bash query.sh create-dbs
        ;;
    functions)
        bash query.sh find-function "calculate_total"
        bash query.sh search-functions "get_*"
        bash query.sh list-file-functions "tests/sample_codebase/simple_functions.4gl"
        ;;
    dependencies)
        bash query.sh find-function-dependencies "calculate_total"
        bash query.sh find-function-dependents "calculate_total"
        bash query.sh find-dead-code
        ;;
    modules)
        bash query.sh find-module "core"
        bash query.sh search-modules "*"
        bash query.sh find-functions-in-module "core"
        ;;
    references)
        bash query.sh find-reference "PRB-299"
        bash query.sh search-references "100512"
        bash query.sh find-author "Rich"
        ;;
    types)
        bash query.sh validate-types
        bash query.sh unresolved-types
        ;;
    formats)
        bash query.sh find-function "calculate_total" --format=vim
        bash query.sh find-function "calculate_total" --format=vim-hover
        bash query.sh search-functions "get_*" --format=vim-completion
        ;;
    all)
        bash "$0" generation
        bash "$0" functions
        bash "$0" dependencies
        bash "$0" modules
        bash "$0" references
        bash "$0" types
        bash "$0" formats
        ;;
    *)
        echo "Unknown category: $CATEGORY"
        echo "Available: generation, functions, dependencies, modules, references, types, formats, all"
        exit 1
        ;;
esac
```

---

## Troubleshooting

### Database Not Found

```bash
# Regenerate metadata
bash generate_all.sh tests/sample_codebase
bash query.sh create-dbs
```

### No Results from Query

```bash
# Verify database has data
sqlite3 workspace.db "SELECT COUNT(*) FROM functions;"

# Try simpler query
bash query.sh search-functions "*"
```

### Permission Denied

```bash
# Make scripts executable
chmod +x generate_all.sh src/*.sh query.sh
```

### Python Errors

```bash
# Verify Python version
python3 --version

# Check required modules
python3 -c "import json, sqlite3; print('OK')"
```

### Slow Queries

```bash
# Check database size
du -h workspace.db

# Check for missing indexes
sqlite3 workspace.db ".indices"

# Recreate database
bash query.sh create-dbs
```

---

## Performance Expectations

| Operation | Time | Notes |
|-----------|------|-------|
| Exact lookup | <1ms | Use for specific function queries |
| Pattern search | <10ms | Use for finding similar functions |
| Dependency query | <10ms | Use for impact analysis |
| Metrics query | <1ms | Use for quality assessment |
| Type validation | <1s | Use for comprehensive validation |

---

## Related Documentation

- [QUERYING.md](QUERYING.md) - Complete query reference
- [FEATURES.md](FEATURES.md) - Feature overview
- [ARCHITECTURE.md](ARCHITECTURE.md) - System design
- [TYPE_RESOLUTION_GUIDE.md](TYPE_RESOLUTION_GUIDE.md) - Type resolution details
- [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) - Development workflow

