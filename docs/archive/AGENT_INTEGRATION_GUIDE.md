# Genero-Tools Agent Integration Guide

Framework for integrating genero-tools into agentic code review systems for large Genero/4GL codebases.

## Overview

This guide explains how to leverage genero-tools capabilities within an agentic code review framework. Agents can use genero-tools to:

- Understand codebase structure and dependencies
- Analyze code quality metrics
- Track function relationships and call graphs
- Identify code references and ownership
- Resolve type information
- Perform impact analysis

## Quick Reference for Agents

### Essential Commands

```bash
# Setup (one-time)
bash generate_all.sh /path/to/codebase
bash query.sh create-dbs

# Function Analysis
bash query.sh find-function "function_name"
bash query.sh search-functions "pattern_*"
bash query.sh find-function-dependencies "function_name"
bash query.sh find-function-dependents "function_name"

# Code Quality
bash query.sh search-functions "*" | python3 -c "import json, sys; data=json.load(sys.stdin); print(f'Complex: {len([f for f in data if f.get(\"complexity\", 0) > 10])}')"

# Type Resolution
bash query.sh find-function-resolved "function_name"
bash query.sh unresolved-types

# Code References
bash query.sh find-reference "PRB-299"
bash query.sh find-author "Author Name"
```

---

## Agent Capabilities

### 1. Function Analysis

**Use Case:** Review a specific function and understand its context.

```bash
# Get function signature and metadata
bash query.sh find-function "process_order"

# Understand what it calls
bash query.sh find-function-dependencies "process_order"

# Understand what calls it
bash query.sh find-function-dependents "process_order"

# Get all instances if multiple exist
bash query.sh find-all-function-instances "process_order"
```

**Agent Action:** Extract function signature, parameters, return types, complexity metrics, and dependency information for review.

### 2. Code Quality Assessment

**Use Case:** Identify functions that may need refactoring.

```python
from scripts.quality_analyzer import QualityAnalyzer

qa = QualityAnalyzer('workspace.db')

# Find complex functions
complex_funcs = qa.find_complex_functions(threshold=10)

# Find long functions
long_funcs = qa.find_long_functions(threshold=100)

# Get specific metrics
metrics = qa.get_function_metrics('function_name')
```

**Agent Action:** Flag functions exceeding complexity/LOC thresholds for review, suggest refactoring.

### 3. Dependency Analysis

**Use Case:** Understand impact of changes.

```bash
# Find all functions a function calls
bash query.sh find-function-dependencies "update_database"

# Find all functions that call a function
bash query.sh find-function-dependents "validate_input"

# Find dead code
bash query.sh find-dead-code
```

**Agent Action:** Analyze change impact, identify affected functions, detect unused code.

### 4. Type Resolution

**Use Case:** Validate type consistency and resolve LIKE references.

```bash
# Get function with resolved types
bash query.sh find-function-resolved "process_contract"

# Find unresolved types
bash query.sh unresolved-types

# Filter by error type
bash query.sh unresolved-types --filter missing_table
```

**Agent Action:** Validate type consistency, identify type mismatches, flag unresolved references.

### 5. Code Reference Tracking

**Use Case:** Track code ownership and requirements.

```bash
# Find files with a reference
bash query.sh find-reference "PRB-299"

# Find files by author
bash query.sh find-author "John Smith"

# Get author expertise
bash query.sh author-expertise "John Smith"
```

**Agent Action:** Link code to requirements, identify code owners, track expertise areas.

### 6. Module Analysis

**Use Case:** Understand module structure and dependencies.

```bash
# Find module
bash query.sh find-module "core"

# Find functions in module
bash query.sh find-functions-in-module "core"

# Find module dependencies
bash query.sh find-module-dependencies "core"
```

**Agent Action:** Analyze module structure, identify cross-module dependencies, assess modularity.

---

## Agent Workflow Examples

### Example 1: Review New Function

```python
import subprocess
import json

def review_new_function(function_name):
    """Agent workflow to review a new function."""
    
    # 1. Get function details
    result = subprocess.run(
        ['bash', 'query.sh', 'find-function', function_name],
        capture_output=True, text=True
    )
    func_data = json.loads(result.stdout)
    
    # 2. Get dependencies
    result = subprocess.run(
        ['bash', 'query.sh', 'find-function-dependencies', function_name],
        capture_output=True, text=True
    )
    dependencies = json.loads(result.stdout)
    
    # 3. Get dependents
    result = subprocess.run(
        ['bash', 'query.sh', 'find-function-dependents', function_name],
        capture_output=True, text=True
    )
    dependents = json.loads(result.stdout)
    
    # 4. Analyze quality
    from scripts.quality_analyzer import QualityAnalyzer
    qa = QualityAnalyzer('workspace.db')
    metrics = qa.get_function_metrics(function_name)
    
    # 5. Generate review
    review = {
        'function': func_data,
        'dependencies': dependencies,
        'dependents': dependents,
        'metrics': metrics,
        'issues': []
    }
    
    # Check for issues
    if metrics.get('complexity', 0) > 10:
        review['issues'].append('High complexity - consider refactoring')
    if metrics.get('lines_of_code', 0) > 100:
        review['issues'].append('Long function - consider breaking into smaller functions')
    if len(func_data.get('parameters', [])) > 5:
        review['issues'].append('Too many parameters - consider using a structure')
    
    return review
```

### Example 2: Impact Analysis

```python
def analyze_impact(function_name):
    """Agent workflow to analyze impact of changes to a function."""
    
    # 1. Find all dependents
    result = subprocess.run(
        ['bash', 'query.sh', 'find-function-dependents', function_name],
        capture_output=True, text=True
    )
    dependents = json.loads(result.stdout)
    
    # 2. For each dependent, get its dependents (ripple effect)
    impact_chain = {function_name: []}
    for dependent in dependents:
        result = subprocess.run(
            ['bash', 'query.sh', 'find-function-dependents', dependent['name']],
            capture_output=True, text=True
        )
        impact_chain[dependent['name']] = json.loads(result.stdout)
    
    # 3. Analyze impact
    total_affected = sum(len(v) for v in impact_chain.values())
    
    return {
        'direct_dependents': len(dependents),
        'total_affected': total_affected,
        'impact_chain': impact_chain,
        'risk_level': 'high' if total_affected > 10 else 'medium' if total_affected > 5 else 'low'
    }
```

### Example 3: Code Quality Report

```python
def generate_quality_report(file_path):
    """Agent workflow to generate quality report for a file."""
    
    from scripts.quality_analyzer import QualityAnalyzer
    
    qa = QualityAnalyzer('workspace.db')
    
    # 1. Get all functions in file
    result = subprocess.run(
        ['bash', 'query.sh', 'list-file-functions', file_path],
        capture_output=True, text=True
    )
    functions = json.loads(result.stdout)
    
    # 2. Analyze each function
    report = {
        'file': file_path,
        'total_functions': len(functions),
        'functions': []
    }
    
    for func in functions:
        metrics = qa.get_function_metrics(func['name'])
        issues = []
        
        if metrics.get('complexity', 0) > 10:
            issues.append('High complexity')
        if metrics.get('lines_of_code', 0) > 100:
            issues.append('Long function')
        if len(func.get('parameters', [])) > 5:
            issues.append('Too many parameters')
        
        report['functions'].append({
            'name': func['name'],
            'metrics': metrics,
            'issues': issues
        })
    
    # 3. Calculate file-level metrics
    report['file_metrics'] = qa.get_file_metrics(file_path)
    
    return report
```

### Example 4: Type Resolution Validation

```python
def validate_types_for_function(function_name):
    """Agent workflow to validate type resolution for a function."""
    
    # 1. Get function with resolved types
    result = subprocess.run(
        ['bash', 'query.sh', 'find-function-resolved', function_name],
        capture_output=True, text=True
    )
    func_data = json.loads(result.stdout)
    
    # 2. Check for unresolved types
    result = subprocess.run(
        ['bash', 'query.sh', 'unresolved-types'],
        capture_output=True, text=True
    )
    unresolved = json.loads(result.stdout)
    
    # 3. Filter for this function
    func_unresolved = [u for u in unresolved if u.get('function_name') == function_name]
    
    # 4. Generate validation report
    report = {
        'function': function_name,
        'total_parameters': len(func_data.get('parameters', [])),
        'resolved_parameters': len([p for p in func_data.get('parameters', []) if p.get('resolved', False)]),
        'unresolved_types': func_unresolved,
        'validation_status': 'valid' if not func_unresolved else 'has_issues'
    }
    
    return report
```

---

## Python API for Agents

### Direct Database Queries

```python
import sqlite3
import json

def query_functions_by_complexity(db_path, threshold=10):
    """Find all functions exceeding complexity threshold."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute('''SELECT name, file_path, complexity, lines_of_code
                 FROM functions
                 WHERE complexity > ?
                 ORDER BY complexity DESC''', (threshold,))
    
    results = [dict(row) for row in c.fetchall()]
    conn.close()
    return results

def query_functions_by_type(db_path, param_type):
    """Find all functions with specific parameter type."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute('''SELECT DISTINCT f.name, f.file_path
                 FROM functions f
                 JOIN parameters p ON f.id = p.function_id
                 WHERE p.type = ?''', (param_type,))
    
    results = [dict(row) for row in c.fetchall()]
    conn.close()
    return results

def query_call_chain(db_path, function_name, depth=3):
    """Find call chain for a function."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Get direct calls
    c.execute('''SELECT called_function FROM calls
                 WHERE function_id = (SELECT id FROM functions WHERE name = ?)''',
              (function_name,))
    
    calls = [row['called_function'] for row in c.fetchall()]
    conn.close()
    return calls
```

### Quality Analysis API

```python
from scripts.quality_analyzer import QualityAnalyzer

qa = QualityAnalyzer('workspace.db')

# Find complex functions
complex_funcs = qa.find_complex_functions(threshold=10)

# Find long functions
long_funcs = qa.find_long_functions(threshold=100)

# Get function metrics
metrics = qa.get_function_metrics('my_function')

# Get file metrics
file_metrics = qa.get_file_metrics('path/to/file.4gl')
```

### Header Query API

```python
from scripts.query_headers import (
    find_reference,
    search_references,
    find_author,
    author_expertise
)

# Find files with reference
files = find_reference('workspace.db', 'PRB-299')

# Search references
results = search_references('workspace.db', '100512')

# Find files by author
files = find_author('workspace.db', 'John Smith')

# Get author expertise
expertise = author_expertise('workspace.db', 'John Smith')
```

---

## Agent Review Checklist

When reviewing code, agents should check:

- [ ] **Complexity** - Is cyclomatic complexity > 10?
- [ ] **Length** - Is function > 100 LOC?
- [ ] **Parameters** - Does function have > 5 parameters?
- [ ] **Returns** - Does function have > 3 return values?
- [ ] **Dependencies** - Are there circular dependencies?
- [ ] **Types** - Are all LIKE references resolved?
- [ ] **Calls** - Are all called functions defined?
- [ ] **Dead Code** - Is function ever called?
- [ ] **Ownership** - Is code ownership clear?
- [ ] **References** - Are code references tracked?

---

## Performance Considerations

| Operation | Time | Notes |
|-----------|------|-------|
| Exact lookup | <1ms | Use for specific function queries |
| Pattern search | <10ms | Use for finding similar functions |
| Dependency query | <10ms | Use for impact analysis |
| Metrics query | <1ms | Use for quality assessment |
| Type validation | <1s | Use for comprehensive validation |

**Optimization Tips:**
- Cache results for repeated queries
- Use pattern searches instead of full scans
- Batch multiple queries together
- Use pagination for large result sets

---

## Integration Points

### With CI/CD Pipeline

```bash
#!/bin/bash
# ci_review.sh - Run genero-tools analysis in CI/CD

CODEBASE_PATH="$1"

# Generate metadata
bash generate_all.sh "$CODEBASE_PATH"

# Run quality checks
python3 << 'EOF'
from scripts.quality_analyzer import QualityAnalyzer
qa = QualityAnalyzer('workspace.db')
complex_funcs = qa.find_complex_functions(threshold=15)
if complex_funcs:
    print(f"WARNING: {len(complex_funcs)} functions exceed complexity threshold")
    exit(1)
EOF
```

### With Git Hooks

```bash
#!/bin/bash
# pre-commit hook - Check changed functions

CHANGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.4gl$')

for file in $CHANGED_FILES; do
    bash query.sh list-file-functions "$file" | python3 -c "
import json, sys
funcs = json.load(sys.stdin)
for f in funcs:
    if f.get('complexity', 0) > 15:
        print(f'ERROR: {f[\"name\"]} has high complexity')
        exit(1)
"
done
```

### With IDE Plugins

```python
# IDE plugin integration
def get_function_hover_info(function_name):
    """Get hover information for IDE."""
    result = subprocess.run(
        ['bash', 'query.sh', 'find-function', function_name, '--format=vim-hover'],
        capture_output=True, text=True
    )
    return result.stdout

def get_function_completions(pattern):
    """Get function completions for IDE."""
    result = subprocess.run(
        ['bash', 'query.sh', 'search-functions', pattern, '--format=vim-completion'],
        capture_output=True, text=True
    )
    return result.stdout.split('\n')
```

---

## Troubleshooting

### Database Not Found

```bash
# Regenerate metadata
bash generate_all.sh /path/to/codebase
bash query.sh create-dbs
```

### No Results from Query

```bash
# Verify database has data
sqlite3 workspace.db "SELECT COUNT(*) FROM functions;"

# Try simpler query
bash query.sh search-functions "*"
```

### Type Resolution Issues

```bash
# Check unresolved types
bash query.sh unresolved-types

# Validate type resolution
bash query.sh validate-types
```

---

## Related Documentation

- [QUERYING.md](QUERYING.md) - Complete query reference
- [FEATURES.md](FEATURES.md) - Feature overview
- [ARCHITECTURE.md](ARCHITECTURE.md) - System design
- [TYPE_RESOLUTION_GUIDE.md](TYPE_RESOLUTION_GUIDE.md) - Type resolution details
- [COMMAND_LINE_TESTING_GUIDE.md](COMMAND_LINE_TESTING_GUIDE.md) - Testing guide
- [COMMAND_LINE_ADVANCED_SCENARIOS.md](COMMAND_LINE_ADVANCED_SCENARIOS.md) - Advanced scenarios

