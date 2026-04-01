# Genero-Review: Agentic Code Review Framework

Documentation index for the genero-review project - a framework for agentic code reviews in large Genero/4GL codebases using genero-tools.

## Quick Start

The genero-review project provides an agentic framework for automated code reviews. It leverages genero-tools to understand codebase structure, analyze code quality, and provide intelligent review feedback.

### For Agents

Start with [AGENT_INTEGRATION_GUIDE.md](AGENT_INTEGRATION_GUIDE.md) to understand:
- How to query genero-tools
- Available agent capabilities
- Workflow examples for common review tasks
- Python API for direct database access

### For Developers

Start with [README.md](README.md) for:
- Project overview
- Quick start guide
- Feature list
- Integration examples

---

## Documentation Structure

### Core Documentation

| Document | Purpose | Audience |
|----------|---------|----------|
| [README.md](README.md) | Project overview and quick start | Everyone |
| [AGENT_INTEGRATION_GUIDE.md](AGENT_INTEGRATION_GUIDE.md) | Agent capabilities and workflows | Agents, Agent Developers |
| [QUERYING.md](QUERYING.md) | Complete query reference | Agents, Developers |
| [FEATURES.md](FEATURES.md) | Feature overview with examples | Everyone |

### Advanced Documentation

| Document | Purpose | Audience |
|----------|---------|----------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | System design and components | Developers, Architects |
| [TYPE_RESOLUTION_GUIDE.md](TYPE_RESOLUTION_GUIDE.md) | Type resolution system | Developers, Advanced Users |
| [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) | Development workflow | Developers |
| [SECURITY.md](SECURITY.md) | Security practices | Developers, DevOps |

### Testing & Execution

| Document | Purpose | Audience |
|----------|---------|----------|
| [COMMAND_LINE_TESTING_GUIDE.md](COMMAND_LINE_TESTING_GUIDE.md) | Sequential testing guide | QA, Testers |
| [COMMAND_LINE_ADVANCED_SCENARIOS.md](COMMAND_LINE_ADVANCED_SCENARIOS.md) | Real-world scenarios | Advanced Users |
| [COMMAND_LINE_EXECUTION_GUIDE.md](COMMAND_LINE_EXECUTION_GUIDE.md) | Execution scripts and automation | DevOps, CI/CD |

---

## Agent Workflow Quick Reference

### 1. Setup (One-Time)

```bash
# Generate metadata from codebase
bash generate_all.sh /path/to/codebase

# Create indexed databases
bash query.sh create-dbs
```

### 2. Function Review

```bash
# Get function details
bash query.sh find-function "function_name"

# Analyze dependencies
bash query.sh find-function-dependencies "function_name"
bash query.sh find-function-dependents "function_name"

# Check quality metrics
python3 -c "from scripts.quality_analyzer import QualityAnalyzer; qa = QualityAnalyzer('workspace.db'); print(qa.get_function_metrics('function_name'))"
```

### 3. Impact Analysis

```bash
# Find all functions affected by a change
bash query.sh find-function-dependents "changed_function"

# Analyze ripple effects
bash query.sh find-function-dependents "dependent_function"
```

### 4. Code Quality Assessment

```bash
# Find complex functions
python3 -c "from scripts.quality_analyzer import QualityAnalyzer; qa = QualityAnalyzer('workspace.db'); print(qa.find_complex_functions(threshold=10))"

# Find long functions
python3 -c "from scripts.quality_analyzer import QualityAnalyzer; qa = QualityAnalyzer('workspace.db'); print(qa.find_long_functions(threshold=100))"
```

### 5. Type Validation

```bash
# Get function with resolved types
bash query.sh find-function-resolved "function_name"

# Find unresolved types
bash query.sh unresolved-types

# Validate type consistency
bash query.sh validate-types
```

### 6. Code Reference Tracking

```bash
# Find code references
bash query.sh find-reference "PRB-299"

# Find code ownership
bash query.sh find-author "Author Name"

# Get author expertise
bash query.sh author-expertise "Author Name"
```

---

## Key Capabilities for Agents

### Function Analysis
- Extract function signatures, parameters, return types
- Analyze function complexity and metrics
- Track function dependencies and call graphs
- Identify dead code

### Code Quality
- Measure cyclomatic complexity
- Track lines of code
- Count parameters and return values
- Analyze call depth

### Type Resolution
- Resolve LIKE references to schema types
- Validate type consistency
- Identify unresolved types
- Handle multi-instance functions

### Code References
- Track code references (PRB-299, EH100512, etc.)
- Identify code ownership
- Track author expertise areas
- Link code to requirements

### Module Analysis
- Understand module structure
- Analyze module dependencies
- Identify cross-module relationships
- Assess modularity

---

## Common Agent Tasks

### Task 1: Review New Function

```python
def review_new_function(function_name):
    """Review a newly added function."""
    # 1. Get function details
    # 2. Analyze dependencies
    # 3. Check quality metrics
    # 4. Validate types
    # 5. Generate review report
```

See [AGENT_INTEGRATION_GUIDE.md](AGENT_INTEGRATION_GUIDE.md#example-1-review-new-function) for full example.

### Task 2: Analyze Change Impact

```python
def analyze_impact(function_name):
    """Analyze impact of changes to a function."""
    # 1. Find all dependents
    # 2. Trace ripple effects
    # 3. Calculate risk level
    # 4. Generate impact report
```

See [AGENT_INTEGRATION_GUIDE.md](AGENT_INTEGRATION_GUIDE.md#example-2-impact-analysis) for full example.

### Task 3: Generate Quality Report

```python
def generate_quality_report(file_path):
    """Generate quality report for a file."""
    # 1. Get all functions in file
    # 2. Analyze each function
    # 3. Calculate file-level metrics
    # 4. Generate report
```

See [AGENT_INTEGRATION_GUIDE.md](AGENT_INTEGRATION_GUIDE.md#example-3-code-quality-report) for full example.

### Task 4: Validate Type Resolution

```python
def validate_types_for_function(function_name):
    """Validate type resolution for a function."""
    # 1. Get function with resolved types
    # 2. Check for unresolved types
    # 3. Generate validation report
```

See [AGENT_INTEGRATION_GUIDE.md](AGENT_INTEGRATION_GUIDE.md#example-4-type-resolution-validation) for full example.

---

## Query Examples

### Find Functions

```bash
# Exact match
bash query.sh find-function "calculate_total"

# Pattern search
bash query.sh search-functions "get_*"

# All functions in file
bash query.sh list-file-functions "path/to/file.4gl"

# All instances of function
bash query.sh find-all-function-instances "calculate_total"
```

### Analyze Dependencies

```bash
# What does this function call?
bash query.sh find-function-dependencies "process_order"

# What calls this function?
bash query.sh find-function-dependents "validate_input"

# Find unused functions
bash query.sh find-dead-code
```

### Track Code References

```bash
# Find files with reference
bash query.sh find-reference "PRB-299"

# Find files by author
bash query.sh find-author "John Smith"

# Get author expertise
bash query.sh author-expertise "John Smith"
```

### Validate Types

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

## Performance Characteristics

| Operation | Time | Use Case |
|-----------|------|----------|
| Exact lookup | <1ms | Find specific function |
| Pattern search | <10ms | Find similar functions |
| Dependency query | <10ms | Impact analysis |
| Metrics query | <1ms | Quality assessment |
| Type validation | <1s | Comprehensive validation |

**Optimization Tips:**
- Cache results for repeated queries
- Use pattern searches instead of full scans
- Batch multiple queries together
- Use pagination for large result sets

---

## Integration Examples

### With CI/CD Pipeline

```bash
# Generate metadata
bash generate_all.sh /path/to/codebase

# Run quality checks
python3 scripts/quality_analyzer.py workspace.db
```

### With Git Hooks

```bash
# Check changed functions
for file in $(git diff --cached --name-only | grep '\.4gl$'); do
    bash query.sh list-file-functions "$file"
done
```

### With IDE Plugins

```python
# Get hover information
bash query.sh find-function "function_name" --format=vim-hover

# Get completions
bash query.sh search-functions "pattern_*" --format=vim-completion
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

## Document Navigation

### For Getting Started
1. [README.md](README.md) - Overview and quick start
2. [AGENT_INTEGRATION_GUIDE.md](AGENT_INTEGRATION_GUIDE.md) - Agent capabilities
3. [QUERYING.md](QUERYING.md) - Query reference

### For Understanding the System
1. [FEATURES.md](FEATURES.md) - Feature overview
2. [ARCHITECTURE.md](ARCHITECTURE.md) - System design
3. [TYPE_RESOLUTION_GUIDE.md](TYPE_RESOLUTION_GUIDE.md) - Type resolution

### For Development
1. [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) - Development workflow
2. [SECURITY.md](SECURITY.md) - Security practices
3. [COMMAND_LINE_EXECUTION_GUIDE.md](COMMAND_LINE_EXECUTION_GUIDE.md) - Execution scripts

### For Testing
1. [COMMAND_LINE_TESTING_GUIDE.md](COMMAND_LINE_TESTING_GUIDE.md) - Testing guide
2. [COMMAND_LINE_ADVANCED_SCENARIOS.md](COMMAND_LINE_ADVANCED_SCENARIOS.md) - Advanced scenarios

---

## Key Concepts

### Function Signatures
Extracted metadata about functions including name, parameters, return types, and line numbers.

### Call Graphs
Relationships between functions showing which functions call which other functions.

### Code Quality Metrics
Measurements including cyclomatic complexity, lines of code, parameter count, return count, and call depth.

### Type Resolution
Process of resolving LIKE references to actual database schema types.

### Code References
Tracked references like PRB-299, EH100512 that link code to requirements and issues.

### Module Dependencies
Relationships between modules showing which modules depend on which other modules.

---

## Next Steps

1. **For Agents:** Read [AGENT_INTEGRATION_GUIDE.md](AGENT_INTEGRATION_GUIDE.md)
2. **For Developers:** Read [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)
3. **For Testing:** Read [COMMAND_LINE_TESTING_GUIDE.md](COMMAND_LINE_TESTING_GUIDE.md)
4. **For Queries:** Read [QUERYING.md](QUERYING.md)

---

## Support

For issues or questions:
1. Check [QUERYING.md](QUERYING.md) for query examples
2. Review [AGENT_INTEGRATION_GUIDE.md](AGENT_INTEGRATION_GUIDE.md) for workflow examples
3. See [COMMAND_LINE_TESTING_GUIDE.md](COMMAND_LINE_TESTING_GUIDE.md) for testing procedures
4. Check [ARCHITECTURE.md](ARCHITECTURE.md) for system design details

