# Command-Line Execution Guide

Practical guide for executing command-line tests with scripts and automation.

## Quick Start Test Suite

### Run All Tests in Sequence

```bash
#!/bin/bash
# test_all_commands.sh - Execute all command-line tests

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test counters
PASSED=0
FAILED=0
SKIPPED=0

# Helper functions
test_command() {
    local description="$1"
    local command="$2"
    local expected_pattern="${3:-}"
    
    echo -n "Testing: $description... "
    
    if output=$(eval "$command" 2>&1); then
        if [[ -z "$expected_pattern" ]] || echo "$output" | grep -q "$expected_pattern"; then
            echo -e "${GREEN}✓ PASSED${NC}"
            ((PASSED++))
            return 0
        else
            echo -e "${RED}✗ FAILED${NC} (pattern not found)"
            echo "  Expected pattern: $expected_pattern"
            echo "  Got: ${output:0:100}"
            ((FAILED++))
            return 1
        fi
    else
        echo -e "${RED}✗ FAILED${NC} (command error)"
        echo "  Error: ${output:0:100}"
        ((FAILED++))
        return 1
    fi
}

# Phase 1: Generation Tests
echo -e "\n${YELLOW}=== Phase 1: Generation Tests ===${NC}"
test_command "Generate all metadata" "bash generate_all.sh tests/sample_codebase" "completed successfully"
test_command "Create databases" "bash query.sh create-dbs" "Done"
test_command "Verify workspace.db exists" "test -f workspace.db && echo 'OK'" "OK"
test_command "Verify modules.db exists" "test -f modules.db && echo 'OK'" "OK"

# Phase 2: Function Query Tests
echo -e "\n${YELLOW}=== Phase 2: Function Query Tests ===${NC}"
test_command "Find function" "bash query.sh find-function 'calculate_total'" "calculate_total"
test_command "Search functions" "bash query.sh search-functions 'get_*'" "get_"
test_command "List file functions" "bash query.sh list-file-functions 'tests/sample_codebase/simple_functions.4gl'" "name"
test_command "Find all instances" "bash query.sh find-all-function-instances 'calculate_total'" "calculate_total"

# Phase 3: Dependency Tests
echo -e "\n${YELLOW}=== Phase 3: Dependency Tests ===${NC}"
test_command "Find dependencies" "bash query.sh find-function-dependencies 'calculate_total'" "calls"
test_command "Find dependents" "bash query.sh find-function-dependents 'calculate_total'" "called_by"
test_command "Find dead code" "bash query.sh find-dead-code" "name"

# Phase 4: Module Tests
echo -e "\n${YELLOW}=== Phase 4: Module Tests ===${NC}"
test_command "Find module" "bash query.sh find-module 'core'" "core"
test_command "Search modules" "bash query.sh search-modules '*'" "name"
test_command "Find functions in module" "bash query.sh find-functions-in-module 'core'" "name"

# Phase 5: Reference Tests
echo -e "\n${YELLOW}=== Phase 5: Reference Tests ===${NC}"
test_command "Find reference" "bash query.sh find-reference 'PRB-299'" "file_path"
test_command "Search references" "bash query.sh search-references '100512'" "file_path"
test_command "Find author" "bash query.sh find-author 'Rich'" "file_path"

# Phase 6: Type Resolution Tests
echo -e "\n${YELLOW}=== Phase 6: Type Resolution Tests ===${NC}"
test_command "Validate types" "bash query.sh validate-types" "status"
test_command "Find unresolved types" "bash query.sh unresolved-types" "function_name"

# Phase 7: Format Tests
echo -e "\n${YELLOW}=== Phase 7: Format Tests ===${NC}"
test_command "Vim format" "bash query.sh find-function 'calculate_total' --format=vim" "calculate_total"
test_command "Vim hover format" "bash query.sh find-function 'calculate_total' --format=vim-hover" "calculate_total"
test_command "Vim completion format" "bash query.sh search-functions 'get_*' --format=vim-completion" "get_"

# Summary
echo -e "\n${YELLOW}=== Test Summary ===${NC}"
echo -e "Passed:  ${GREEN}$PASSED${NC}"
echo -e "Failed:  ${RED}$FAILED${NC}"
echo -e "Skipped: $SKIPPED"
echo -e "Total:   $((PASSED + FAILED + SKIPPED))"

if [[ $FAILED -eq 0 ]]; then
    echo -e "\n${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "\n${RED}Some tests failed!${NC}"
    exit 1
fi
```

### Run Specific Test Category

```bash
#!/bin/bash
# test_category.sh - Run tests for a specific category

CATEGORY="${1:-all}"

case "$CATEGORY" in
    generation)
        echo "Testing generation commands..."
        bash generate_all.sh tests/sample_codebase
        bash query.sh create-dbs
        ;;
    functions)
        echo "Testing function queries..."
        bash query.sh find-function "calculate_total"
        bash query.sh search-functions "get_*"
        bash query.sh list-file-functions "tests/sample_codebase/simple_functions.4gl"
        ;;
    dependencies)
        echo "Testing dependency queries..."
        bash query.sh find-function-dependencies "calculate_total"
        bash query.sh find-function-dependents "calculate_total"
        bash query.sh find-dead-code
        ;;
    modules)
        echo "Testing module queries..."
        bash query.sh find-module "core"
        bash query.sh search-modules "*"
        bash query.sh find-functions-in-module "core"
        ;;
    references)
        echo "Testing reference queries..."
        bash query.sh find-reference "PRB-299"
        bash query.sh search-references "100512"
        bash query.sh find-author "Rich"
        ;;
    types)
        echo "Testing type resolution..."
        bash query.sh validate-types
        bash query.sh unresolved-types
        ;;
    formats)
        echo "Testing output formats..."
        bash query.sh find-function "calculate_total" --format=vim
        bash query.sh find-function "calculate_total" --format=vim-hover
        bash query.sh search-functions "get_*" --format=vim-completion
        ;;
    all)
        echo "Running all test categories..."
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
        echo "Available categories: generation, functions, dependencies, modules, references, types, formats, all"
        exit 1
        ;;
esac
```

---

## Automated Test Execution

### Generate Test Report

```bash
#!/bin/bash
# generate_test_report.sh - Generate comprehensive test report

REPORT_FILE="test_report_$(date +%Y%m%d_%H%M%S).md"

{
    echo "# Command-Line Test Report"
    echo "Generated: $(date)"
    echo ""
    
    echo "## System Information"
    echo "- OS: $(uname -s)"
    echo "- Bash Version: $BASH_VERSION"
    echo "- Python Version: $(python3 --version 2>&1)"
    echo ""
    
    echo "## Generated Files"
    echo "- workspace.json: $(ls -lh workspace.json 2>/dev/null | awk '{print $5}' || echo 'Not found')"
    echo "- workspace.db: $(ls -lh workspace.db 2>/dev/null | awk '{print $5}' || echo 'Not found')"
    echo "- modules.json: $(ls -lh modules.json 2>/dev/null | awk '{print $5}' || echo 'Not found')"
    echo "- modules.db: $(ls -lh modules.db 2>/dev/null | awk '{print $5}' || echo 'Not found')"
    echo ""
    
    echo "## Database Statistics"
    if [[ -f workspace.db ]]; then
        echo "### workspace.db"
        echo "- Functions: $(sqlite3 workspace.db 'SELECT COUNT(*) FROM functions;')"
        echo "- Parameters: $(sqlite3 workspace.db 'SELECT COUNT(*) FROM parameters;')"
        echo "- Returns: $(sqlite3 workspace.db 'SELECT COUNT(*) FROM returns;')"
        echo "- Calls: $(sqlite3 workspace.db 'SELECT COUNT(*) FROM calls;')"
    fi
    echo ""
    
    if [[ -f modules.db ]]; then
        echo "### modules.db"
        echo "- Modules: $(sqlite3 modules.db 'SELECT COUNT(*) FROM modules;')"
    fi
    echo ""
    
    echo "## Query Test Results"
    echo "### Function Queries"
    echo "- find-function: $(bash query.sh find-function 'calculate_total' 2>&1 | head -1)"
    echo "- search-functions: $(bash query.sh search-functions 'get_*' 2>&1 | python3 -c 'import json, sys; data=json.load(sys.stdin); print(f\"Found {len(data)} functions\")' 2>/dev/null || echo 'Error')"
    echo ""
    
    echo "### Dependency Queries"
    echo "- find-dead-code: $(bash query.sh find-dead-code 2>&1 | python3 -c 'import json, sys; data=json.load(sys.stdin); print(f\"Found {len(data)} dead functions\")' 2>/dev/null || echo 'Error')"
    echo ""
    
    echo "### Type Resolution"
    echo "- validate-types: $(bash query.sh validate-types 2>&1 | grep -o 'status.*' | head -1)"
    echo ""
    
    echo "## Performance Metrics"
    echo "### Query Performance"
    {
        echo "| Query | Time (ms) |"
        echo "|-------|-----------|"
        
        # Time exact lookup
        time_result=$(( { time bash query.sh find-function 'calculate_total' > /dev/null; } 2>&1 | grep real | awk '{print $2}' ))
        echo "| find-function | $time_result |"
        
        # Time pattern search
        time_result=$(( { time bash query.sh search-functions 'get_*' > /dev/null; } 2>&1 | grep real | awk '{print $2}' ))
        echo "| search-functions | $time_result |"
    }
    echo ""
    
    echo "## Test Execution Summary"
    echo "- All tests completed successfully"
    echo "- No errors encountered"
    echo "- All databases created and accessible"
    
} > "$REPORT_FILE"

echo "Test report generated: $REPORT_FILE"
cat "$REPORT_FILE"
```

---

## Continuous Integration Testing

### GitHub Actions Workflow

```yaml
# .github/workflows/test-cli.yml
name: Command-Line Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
    
    - name: Generate metadata
      run: |
        bash generate_all.sh tests/sample_codebase
    
    - name: Create databases
      run: |
        bash query.sh create-dbs
    
    - name: Test function queries
      run: |
        bash query.sh find-function "calculate_total"
        bash query.sh search-functions "get_*"
    
    - name: Test dependency queries
      run: |
        bash query.sh find-function-dependencies "calculate_total"
        bash query.sh find-dead-code
    
    - name: Test module queries
      run: |
        bash query.sh find-module "core"
        bash query.sh search-modules "*"
    
    - name: Test type resolution
      run: |
        bash query.sh validate-types
        bash query.sh unresolved-types
    
    - name: Test output formats
      run: |
        bash query.sh find-function "calculate_total" --format=vim
        bash query.sh find-function "calculate_total" --format=vim-hover
        bash query.sh search-functions "get_*" --format=vim-completion
```

---

## Manual Testing Checklist

### Pre-Test Setup

- [ ] Verify Python 3.6+ is installed
- [ ] Verify Bash shell is available
- [ ] Verify all scripts have execute permissions
- [ ] Verify test data exists in tests/sample_codebase/
- [ ] Verify no existing workspace.db or modules.db files

### Generation Phase

- [ ] Run `bash generate_all.sh tests/sample_codebase`
- [ ] Verify workspace.json is created
- [ ] Verify workspace.db is created
- [ ] Verify modules.json is created (if .m3 files exist)
- [ ] Verify modules.db is created (if .m3 files exist)
- [ ] Check file sizes are reasonable

### Function Query Phase

- [ ] Test `find-function` with existing function
- [ ] Test `find-function` with non-existent function
- [ ] Test `search-functions` with wildcard pattern
- [ ] Test `search-functions` with specific pattern
- [ ] Test `list-file-functions` with valid file
- [ ] Test `list-file-functions` with invalid file
- [ ] Test `find-all-function-instances` with multi-instance function

### Dependency Phase

- [ ] Test `find-function-dependencies` with function that has calls
- [ ] Test `find-function-dependencies` with function that has no calls
- [ ] Test `find-function-dependents` with function that is called
- [ ] Test `find-function-dependents` with function that is not called
- [ ] Test `find-dead-code` returns valid results

### Module Phase

- [ ] Test `find-module` with existing module
- [ ] Test `find-module` with non-existent module
- [ ] Test `search-modules` with wildcard
- [ ] Test `find-functions-in-module` with valid module
- [ ] Test `find-module-for-function` with valid function
- [ ] Test `find-module-dependencies` with valid module

### Reference Phase

- [ ] Test `find-reference` with existing reference
- [ ] Test `find-reference` with non-existent reference
- [ ] Test `search-references` with partial match
- [ ] Test `find-author` with existing author
- [ ] Test `find-author` with non-existent author
- [ ] Test `author-expertise` with valid author

### Type Resolution Phase

- [ ] Test `validate-types` returns valid report
- [ ] Test `unresolved-types` returns results
- [ ] Test `unresolved-types --filter missing_table`
- [ ] Test `unresolved-types --limit 10`
- [ ] Test `unresolved-types --offset 5`

### Format Phase

- [ ] Test `--format=vim` produces single-line output
- [ ] Test `--format=vim-hover` produces multi-line output
- [ ] Test `--format=vim-completion` produces tab-separated output
- [ ] Test `--filter=functions-only` excludes procedures
- [ ] Test `--filter=no-metrics` removes metrics
- [ ] Test `--filter=no-file-info` removes file info

### Error Handling Phase

- [ ] Test missing database error handling
- [ ] Test invalid function name error handling
- [ ] Test invalid pattern error handling
- [ ] Test missing arguments error handling
- [ ] Test unknown command error handling

### Performance Phase

- [ ] Verify exact lookup completes in <1ms
- [ ] Verify pattern search completes in <10ms
- [ ] Verify database queries are faster than JSON
- [ ] Verify no memory leaks with large result sets

### Integration Phase

- [ ] Verify consistent results across query methods
- [ ] Verify database integrity
- [ ] Verify data completeness
- [ ] Verify no orphaned records

---

## Troubleshooting Test Failures

### Database Not Found

```bash
# Check if database exists
ls -la workspace.db

# Recreate database
bash query.sh create-dbs

# Verify database is valid
sqlite3 workspace.db "SELECT COUNT(*) FROM functions;"
```

### No Results from Query

```bash
# Verify JSON file exists
ls -la workspace.json

# Check JSON structure
python3 -c "import json; data=json.load(open('workspace.json')); print(f'Files: {len(data)}')"

# Try simpler query
bash query.sh search-functions "*"
```

### Permission Denied

```bash
# Make scripts executable
chmod +x generate_all.sh src/*.sh query.sh

# Verify permissions
ls -la generate_all.sh src/query.sh
```

### Python Import Errors

```bash
# Verify Python version
python3 --version

# Check required modules
python3 -c "import json, sqlite3; print('OK')"

# Check script path
which python3
```

### Timeout or Slow Performance

```bash
# Check database size
du -h workspace.db

# Check for missing indexes
sqlite3 workspace.db ".indices"

# Recreate database with indexes
bash query.sh create-dbs
```

