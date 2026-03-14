# Querying Guide

Query extracted metadata using the shell interface or Python API.

## Shell Interface

```bash
# Create indexed databases (one-time setup)
bash query.sh create-dbs

# Find a function
bash query.sh find-function "my_function"

# Search functions by pattern
bash query.sh search-functions "get_*"

# List functions in a file
bash query.sh list-file-functions "path/to/file.4gl"

# Find function dependencies
bash query.sh find-function-dependencies "process_request"

# Find function dependents
bash query.sh find-function-dependents "log_message"

# Find code references
bash query.sh find-reference "PRB-299"

# Find files by author
bash query.sh find-author "Rich"
```

## Python API

```python
import sqlite3
import json

# Query functions
conn = sqlite3.connect('workspace.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

# Find all functions with STRING parameters
c.execute('''SELECT DISTINCT f.name FROM functions f 
  JOIN parameters p ON f.id = p.function_id 
  WHERE p.type = 'STRING' ''')

results = [dict(row) for row in c.fetchall()]
print(json.dumps(results, indent=2))
conn.close()
```

## Quality Analysis

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

## Performance

- Exact lookup: <1ms
- Pattern search: <10ms
- Metrics queries: <10ms

See [FEATURES.md](FEATURES.md) for more examples.
