# Advanced Command-Line Scenarios

Comprehensive testing guide for advanced use cases and real-world scenarios.

## Scenario 1: Complete Codebase Analysis Workflow

This scenario demonstrates a complete workflow from generation to analysis.

### Step 1: Generate All Metadata with Verbose Output

```bash
VERBOSE=1 bash generate_all.sh /path/to/large/codebase
```

**Expected Output:**
- Progress messages for each generation step
- File counts for .4gl and .m3 files
- Schema detection and parsing
- Database creation confirmation
- Type resolution status

**Verification:**
```bash
# Check generated files exist
ls -lh workspace.json modules.json workspace.db modules.db

# Verify file sizes are reasonable
du -h workspace.json modules.json
```

### Step 2: Validate Generated Data

```bash
# Check JSON structure
python3 -c "import json; data=json.load(open('workspace.json')); print(f'Files: {len(data)}, Total functions: {sum(len(v) for v in data.values())}')"

# Check database integrity
sqlite3 workspace.db "SELECT COUNT(*) as function_count FROM functions;"
sqlite3 modules.db "SELECT COUNT(*) as module_count FROM modules;"
```

### Step 3: Comprehensive Function Analysis

```bash
# Find all functions
bash query.sh search-functions "*" > all_functions.json

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

### Step 4: Dependency Analysis

```bash
# Find functions with most dependencies
bash query.sh search-functions "*" | python3 -c "
import json, sys
data = json.load(sys.stdin)
most_called = sorted(data, key=lambda x: len(x.get('calls', [])), reverse=True)[:10]
print('Functions that call the most other functions:')
for f in most_called:
    print(f\"  {f['name']}: calls {len(f.get('calls', []))} functions\")
"

# Find most called functions
bash query.sh search-functions "*" | python3 -c "
import json, sys
data = json.load(sys.stdin)
call_counts = {}
for f in data:
    for call in f.get('calls', []):
        call_counts[call] = call_counts.get(call, 0) + 1
most_called = sorted(call_counts.items(), key=lambda x: x[1], reverse=True)[:10]
print('Most called functions:')
for func, count in most_called:
    print(f\"  {func}: called {count} times\")
"
```

---

## Scenario 2: Code Quality Assessment

This scenario focuses on code quality metrics and analysis.

### Step 1: Extract Quality Metrics

```bash
# Get all functions with metrics
bash query.sh search-functions "*" > functions_with_metrics.json

# Analyze metrics distribution
python3 -c "
import json
data = json.load(open('functions_with_metrics.json'))
complexities = [f.get('complexity', 0) for f in data]
locs = [f.get('lines_of_code', 0) for f in data]
params = [len(f.get('parameters', [])) for f in data]

print('Complexity Statistics:')
print(f'  Min: {min(complexities)}, Max: {max(complexities)}, Avg: {sum(complexities)/len(complexities):.1f}')
print('Lines of Code Statistics:')
print(f'  Min: {min(locs)}, Max: {max(locs)}, Avg: {sum(locs)/len(locs):.1f}')
print('Parameter Count Statistics:')
print(f'  Min: {min(params)}, Max: {max(params)}, Avg: {sum(params)/len(params):.1f}')
"
```

### Step 2: Identify Problem Areas

```bash
# Functions exceeding complexity threshold
python3 -c "
import json
data = json.load(open('functions_with_metrics.json'))
high_complexity = [f for f in data if f.get('complexity', 0) > 15]
print(f'Functions with complexity > 15: {len(high_complexity)}')
for f in sorted(high_complexity, key=lambda x: x.get('complexity', 0), reverse=True):
    print(f\"  {f['name']} ({f['file_path']}): {f.get('complexity', 0)}\")
"

# Functions with too many parameters
python3 -c "
import json
data = json.load(open('functions_with_metrics.json'))
many_params = [f for f in data if len(f.get('parameters', [])) > 5]
print(f'Functions with >5 parameters: {len(many_params)}')
for f in sorted(many_params, key=lambda x: len(x.get('parameters', [])), reverse=True):
    print(f\"  {f['name']}: {len(f.get('parameters', []))} parameters\")
"

# Functions with too many return values
python3 -c "
import json
data = json.load(open('functions_with_metrics.json'))
many_returns = [f for f in data if len(f.get('returns', [])) > 3]
print(f'Functions with >3 return values: {len(many_returns)}')
for f in sorted(many_returns, key=lambda x: len(x.get('returns', [])), reverse=True):
    print(f\"  {f['name']}: {len(f.get('returns', []))} return values\")
"
```

### Step 3: Generate Quality Report

```bash
# Create comprehensive quality report
python3 << 'EOF'
import json
import sys

data = json.load(open('functions_with_metrics.json'))

report = {
    'total_functions': len(data),
    'high_complexity': len([f for f in data if f.get('complexity', 0) > 15]),
    'high_loc': len([f for f in data if f.get('lines_of_code', 0) > 100]),
    'many_parameters': len([f for f in data if len(f.get('parameters', [])) > 5]),
    'many_returns': len([f for f in data if len(f.get('returns', [])) > 3]),
    'dead_code': len([f for f in data if len(f.get('called_by', [])) == 0]),
}

print(json.dumps(report, indent=2))
EOF
```

---

## Scenario 3: Author and Reference Tracking

This scenario demonstrates tracking code ownership and references.

### Step 1: Analyze Author Contributions

```bash
# Get all unique authors
bash query.sh search-functions "*" | python3 -c "
import json, sys
data = json.load(sys.stdin)
authors = set()
for f in data:
    for header in f.get('headers', []):
        if 'author' in header:
            authors.add(header['author'])
print(f'Total unique authors: {len(authors)}')
for author in sorted(authors):
    print(f'  - {author}')
"

# Get author expertise
for author in "Rich" "Chilly" "John"; do
    echo "=== $author ==="
    bash query.sh author-expertise "$author"
done
```

### Step 2: Track Code References

```bash
# Find all unique references
bash query.sh search-functions "*" | python3 -c "
import json, sys
data = json.load(sys.stdin)
references = set()
for f in data:
    for header in f.get('headers', []):
        if 'references' in header:
            for ref in header['references']:
                references.add(ref)
print(f'Total unique references: {len(references)}')
for ref in sorted(references)[:20]:
    print(f'  - {ref}')
"

# Find files by reference pattern
bash query.sh search-references "PRB" > prb_references.json
bash query.sh search-references "EH" > eh_references.json
bash query.sh search-references "BUG" > bug_references.json
```

### Step 3: Generate Ownership Report

```bash
# Create ownership matrix
python3 << 'EOF'
import json

data = json.load(open('functions_with_metrics.json'))

ownership = {}
for f in data:
    for header in f.get('headers', []):
        if 'author' in header:
            author = header['author']
            if author not in ownership:
                ownership[author] = {
                    'files': set(),
                    'functions': 0,
                    'total_loc': 0,
                    'avg_complexity': 0
                }
            ownership[author]['files'].add(f['file_path'])
            ownership[author]['functions'] += 1
            ownership[author]['total_loc'] += f.get('lines_of_code', 0)

print('Author Ownership Report:')
print('-' * 60)
for author in sorted(ownership.keys()):
    info = ownership[author]
    print(f'{author}:')
    print(f'  Files: {len(info["files"])}')
    print(f'  Functions: {info["functions"]}')
    print(f'  Total LOC: {info["total_loc"]}')
EOF
```

---

## Scenario 4: Module Dependency Analysis

This scenario analyzes module structure and dependencies.

### Step 1: Map Module Structure

```bash
# List all modules
bash query.sh search-modules "*" > all_modules.json

# Analyze module structure
python3 -c "
import json
data = json.load(open('all_modules.json'))
print(f'Total modules: {len(data)}')
for module in sorted(data, key=lambda x: x['name']):
    print(f\"  {module['name']}: {len(module.get('files', []))} files\")
"
```

### Step 2: Analyze Module Dependencies

```bash
# Find module dependency chains
for module in core utils test; do
    echo "=== Module: $module ==="
    bash query.sh find-module-dependencies "$module"
done

# Find circular dependencies
python3 << 'EOF'
import json

modules = json.load(open('all_modules.json'))

def find_cycles(module_name, visited=None, path=None):
    if visited is None:
        visited = set()
    if path is None:
        path = []
    
    if module_name in visited:
        return [path + [module_name]]
    
    visited.add(module_name)
    cycles = []
    
    module = next((m for m in modules if m['name'] == module_name), None)
    if module:
        for dep in module.get('dependencies', []):
            cycles.extend(find_cycles(dep, visited.copy(), path + [module_name]))
    
    return cycles

all_cycles = []
for module in modules:
    cycles = find_cycles(module['name'])
    all_cycles.extend(cycles)

if all_cycles:
    print('Circular dependencies found:')
    for cycle in all_cycles:
        print(f"  {' -> '.join(cycle)}")
else:
    print('No circular dependencies found')
EOF
```

### Step 3: Generate Module Report

```bash
# Create module dependency matrix
python3 << 'EOF'
import json

modules = json.load(open('all_modules.json'))

print('Module Dependency Matrix:')
print('-' * 60)
print(f'{"Module":<20} {"Files":<10} {"Dependencies":<20}')
print('-' * 60)

for module in sorted(modules, key=lambda x: x['name']):
    deps = ', '.join(module.get('dependencies', [])[:3])
    if len(module.get('dependencies', [])) > 3:
        deps += f", +{len(module.get('dependencies', [])) - 3} more"
    print(f"{module['name']:<20} {len(module.get('files', [])):<10} {deps:<20}")
EOF
```

---

## Scenario 5: Type Resolution Validation

This scenario validates type resolution and identifies issues.

### Step 1: Check Type Resolution Status

```bash
# Get type resolution statistics
bash query.sh validate-types

# Find unresolved types
bash query.sh unresolved-types > unresolved.json

# Analyze unresolved types
python3 -c "
import json
data = json.load(open('unresolved.json'))
print(f'Total unresolved types: {len(data)}')

# Group by error type
errors = {}
for item in data:
    error_type = item.get('error_type', 'unknown')
    errors[error_type] = errors.get(error_type, 0) + 1

print('Breakdown by error type:')
for error_type in sorted(errors.keys()):
    print(f'  {error_type}: {errors[error_type]}')
"
```

### Step 2: Identify Missing Schema Elements

```bash
# Find missing tables
bash query.sh unresolved-types --filter missing_table > missing_tables.json

# Find missing columns
bash query.sh unresolved-types --filter missing_column > missing_columns.json

# Analyze missing elements
python3 -c "
import json

tables = json.load(open('missing_tables.json'))
columns = json.load(open('missing_columns.json'))

print(f'Missing tables: {len(tables)}')
print(f'Missing columns: {len(columns)}')

# Find most common missing tables
table_names = {}
for item in tables:
    table = item.get('type_name', 'unknown')
    table_names[table] = table_names.get(table, 0) + 1

print('Most common missing tables:')
for table in sorted(table_names.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f'  {table[0]}: {table[1]} references')
"
```

### Step 3: Generate Type Resolution Report

```bash
# Create comprehensive type resolution report
python3 << 'EOF'
import json

resolved = json.load(open('workspace_resolved.json'))
unresolved = json.load(open('unresolved.json'))

total_params = sum(len(f.get('parameters', [])) for f in resolved.values() for f in f)
resolved_count = sum(1 for item in unresolved if item.get('resolved', False))

report = {
    'total_parameters': total_params,
    'resolved_count': resolved_count,
    'unresolved_count': len(unresolved),
    'resolution_rate': f"{(resolved_count / (resolved_count + len(unresolved)) * 100):.1f}%"
}

print(json.dumps(report, indent=2))
EOF
```

---

## Scenario 6: Batch Query Processing

This scenario demonstrates batch query execution for complex analysis.

### Step 1: Create Batch Query File

```bash
cat > batch_analysis.json << 'EOF'
{
  "queries": [
    {
      "command": "search-functions",
      "args": ["*"],
      "description": "Get all functions"
    },
    {
      "command": "find-dead-code",
      "description": "Find unused functions"
    },
    {
      "command": "search-modules",
      "args": ["*"],
      "description": "Get all modules"
    },
    {
      "command": "unresolved-types",
      "description": "Find unresolved types"
    },
    {
      "command": "validate-types",
      "description": "Validate type resolution"
    }
  ]
}
EOF
```

### Step 2: Execute Batch Query

```bash
# Execute batch query with output file
bash query.sh batch-query batch_analysis.json --output batch_results.json

# Verify results
python3 -c "
import json
results = json.load(open('batch_results.json'))
print(f'Batch query completed with {len(results)} results')
for i, result in enumerate(results):
    print(f'  Query {i+1}: {result.get(\"description\", \"Unknown\")}')
"
```

### Step 3: Process Batch Results

```bash
# Extract specific results from batch
python3 << 'EOF'
import json

results = json.load(open('batch_results.json'))

# Process each result
for result in results:
    if result.get('command') == 'search-functions':
        functions = result.get('data', [])
        print(f'Total functions: {len(functions)}')
    elif result.get('command') == 'find-dead-code':
        dead = result.get('data', [])
        print(f'Dead code functions: {len(dead)}')
    elif result.get('command') == 'unresolved-types':
        unresolved = result.get('data', [])
        print(f'Unresolved types: {len(unresolved)}')
EOF
```

---

## Scenario 7: Performance Benchmarking

This scenario measures and compares performance characteristics.

### Step 1: Benchmark Query Operations

```bash
# Benchmark exact lookup
echo "Benchmarking exact lookup..."
for i in {1..10}; do
    time bash query.sh find-function "calculate_total" > /dev/null
done

# Benchmark pattern search
echo "Benchmarking pattern search..."
for i in {1..10}; do
    time bash query.sh search-functions "get_*" > /dev/null
done

# Benchmark complex query
echo "Benchmarking complex query..."
for i in {1..10}; do
    time bash query.sh find-function-dependencies "calculate_total" > /dev/null
done
```

### Step 2: Compare JSON vs Database Performance

```bash
# JSON query performance
echo "JSON query performance:"
time python3 -c "
import json
data = json.load(open('workspace.json'))
for file_data in data.values():
    for func in file_data:
        if func['name'] == 'calculate_total':
            print(func)
"

# Database query performance
echo "Database query performance:"
time sqlite3 workspace.db "SELECT * FROM functions WHERE name = 'calculate_total'"
```

### Step 3: Generate Performance Report

```bash
# Create performance comparison
python3 << 'EOF'
import time
import json
import sqlite3

# Test JSON performance
start = time.time()
data = json.load(open('workspace.json'))
json_load_time = time.time() - start

# Test database performance
start = time.time()
conn = sqlite3.connect('workspace.db')
db_load_time = time.time() - start

report = {
    'json_load_time_ms': f"{json_load_time * 1000:.2f}",
    'database_load_time_ms': f"{db_load_time * 1000:.2f}",
    'speedup': f"{json_load_time / db_load_time:.1f}x"
}

print(json.dumps(report, indent=2))
EOF
```

---

## Scenario 8: Vim Plugin Integration Testing

This scenario tests output formats for Vim plugin integration.

### Step 1: Test Vim Format Output

```bash
# Test vim format
bash query.sh find-function "calculate_total" --format=vim

# Test vim format with search
bash query.sh search-functions "get_*" --format=vim

# Test vim format with filter
bash query.sh search-functions "*" --format=vim --filter=functions-only
```

### Step 2: Test Vim Hover Format

```bash
# Test hover format
bash query.sh find-function "calculate_total" --format=vim-hover

# Test hover format with filter
bash query.sh search-functions "get_*" --format=vim-hover --filter=no-metrics

# Test hover format without file info
bash query.sh search-functions "*" --format=vim-hover --filter=no-file-info
```

### Step 3: Test Vim Completion Format

```bash
# Test completion format
bash query.sh search-functions "*" --format=vim-completion

# Test completion format with filter
bash query.sh search-functions "get_*" --format=vim-completion --filter=functions-only

# Test completion format without metrics
bash query.sh search-functions "*" --format=vim-completion --filter=no-metrics
```

### Step 4: Validate Format Output

```bash
# Validate vim format is single-line
bash query.sh find-function "calculate_total" --format=vim | wc -l

# Validate hover format is multi-line
bash query.sh find-function "calculate_total" --format=vim-hover | wc -l

# Validate completion format is tab-separated
bash query.sh search-functions "get_*" --format=vim-completion | head -1 | grep -c $'\t'
```

---

## Scenario 9: Error Recovery and Resilience

This scenario tests error handling and recovery.

### Step 1: Test Missing Database Recovery

```bash
# Remove database
rm -f workspace.db

# Try query (should fail)
bash query.sh find-function "test" 2>&1 | head -5

# Recreate database
bash query.sh create-dbs

# Retry query (should succeed)
bash query.sh find-function "calculate_total"
```

### Step 2: Test Invalid Input Handling

```bash
# Test empty function name
bash query.sh find-function "" 2>&1

# Test invalid pattern
bash query.sh search-functions "[invalid" 2>&1

# Test non-existent file
bash query.sh list-file-functions "nonexistent.4gl" 2>&1

# Test missing arguments
bash query.sh find-function 2>&1
```

### Step 3: Test Concurrent Access

```bash
# Run multiple queries in parallel
bash query.sh find-function "calculate_total" &
bash query.sh search-functions "get_*" &
bash query.sh find-module "core" &
wait

echo "All concurrent queries completed successfully"
```

---

## Scenario 10: Data Consistency Verification

This scenario verifies data consistency across different query methods.

### Step 1: Compare Query Results

```bash
# Get function via direct query
bash query.sh find-function "calculate_total" > direct_query.json

# Get function via search
bash query.sh search-functions "calculate_total" | python3 -c "
import json, sys
data = json.load(sys.stdin)
matching = [f for f in data if f['name'] == 'calculate_total']
print(json.dumps(matching[0] if matching else {}, indent=2))
" > search_query.json

# Compare results
python3 -c "
import json
direct = json.load(open('direct_query.json'))
search = json.load(open('search_query.json'))
if direct == search:
    print('✓ Results are consistent')
else:
    print('✗ Results differ')
    print('Differences:')
    for key in set(list(direct.keys()) + list(search.keys())):
        if direct.get(key) != search.get(key):
            print(f'  {key}: {direct.get(key)} vs {search.get(key)}')
"
```

### Step 2: Verify Database Integrity

```bash
# Check for orphaned records
sqlite3 workspace.db << 'EOF'
-- Check for parameters without functions
SELECT COUNT(*) as orphaned_parameters FROM parameters 
WHERE function_id NOT IN (SELECT id FROM functions);

-- Check for returns without functions
SELECT COUNT(*) as orphaned_returns FROM returns 
WHERE function_id NOT IN (SELECT id FROM functions);

-- Check for calls without functions
SELECT COUNT(*) as orphaned_calls FROM calls 
WHERE function_id NOT IN (SELECT id FROM functions);
EOF
```

### Step 3: Validate Data Completeness

```bash
# Check all functions have required fields
python3 << 'EOF'
import json

data = json.load(open('workspace.json'))
required_fields = ['name', 'file_path', 'line_number']

missing_fields = []
for file_path, functions in data.items():
    for func in functions:
        for field in required_fields:
            if field not in func:
                missing_fields.append((file_path, func.get('name', 'unknown'), field))

if missing_fields:
    print(f'Found {len(missing_fields)} missing fields:')
    for file_path, func_name, field in missing_fields[:10]:
        print(f'  {func_name} ({file_path}): missing {field}')
else:
    print('✓ All functions have required fields')
EOF
```

