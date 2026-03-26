# workspace_resolved.json - Purpose and Current State

## TL;DR

`workspace_resolved.json` is a **generated file** that contains function signatures with resolved LIKE type references. It's currently in the repo but shouldn't be - it's generated output, not source code.

## What It Is

A type-enriched version of `workspace.json` where LIKE database type references are resolved to actual schema types.

**Example:**
```json
// workspace.json
{
  "parameters": [
    {"name": "customer", "type": "LIKE customers.*"}
  ]
}

// workspace_resolved.json
{
  "parameters": [
    {
      "name": "customer",
      "type": "LIKE customers.*",
      "is_like_reference": true,
      "resolved": true,
      "table": "customers",
      "columns": ["id", "name", "email"],
      "types": ["INTEGER", "STRING", "STRING"]
    }
  ]
}
```

## Current Problem

1. **It's in version control** - `workspace_resolved.json` is a generated file and shouldn't be committed
2. **It only has sample data** - It was generated from `./tests/sample_codebase`, not from a real workspace
3. **It requires schema** - Type resolution only works if a schema file has been loaded into the database first
4. **It's not documented** - Users don't know what it is or how to generate it

## How It's Generated

```bash
# Step 1: Generate function signatures
bash generate_all.sh ./tests/sample_codebase

# This creates:
# - workspace.json (function signatures)
# - workspace.db (SQLite database)

# Step 2: Enable type resolution (optional)
RESOLVE_TYPES=1 bash generate_all.sh ./tests/sample_codebase

# This additionally creates:
# - workspace_resolved.json (signatures with resolved types)
```

## Why It Only Has Sample Data

The file in the repo was generated from the sample codebase:
```bash
bash generate_all.sh ./tests/sample_codebase
```

This is why it contains functions like `display_message()` and `update_database()` from the test files, not from a real production codebase.

## When You'd Use It

**You need `workspace_resolved.json` if:**

1. Your codebase uses LIKE type declarations
   ```genero
   DEFINE customer LIKE customers.*
   DEFINE customer_id LIKE customers.id
   ```

2. You want type-aware IDE features
   - Type checking
   - Type hints in hover information
   - Type-safe refactoring

3. You're building tools that need resolved type information
   - LSP server with type support
   - Code analysis tools
   - Documentation generators

**You don't need it if:**

- Your codebase uses explicit types only
  ```genero
  DEFINE customer RECORD
    id INTEGER,
    name STRING
  END RECORD
  ```

- You're not building type-aware tools

## How to Generate It Properly

### Prerequisites

1. Have a schema file (`.sch`) for your codebase
2. Have a codebase with LIKE type references

### Steps

```bash
# 1. Generate initial workspace
bash generate_all.sh /path/to/your/codebase

# 2. Load schema into database
python3 scripts/json_to_sqlite_schema.py /path/to/schema.sch workspace.db

# 3. Generate resolved types
RESOLVE_TYPES=1 bash src/generate_signatures.sh /path/to/your/codebase

# Result: workspace_resolved.json with resolved types
```

## What Should Happen

The `workspace_resolved.json` in the repo should be:

1. **Removed from version control** - It's generated output
2. **Added to .gitignore** - So it's not accidentally committed
3. **Documented** - Users should know how to generate it
4. **Generated on-demand** - Only when needed for type resolution

## Recommended Actions

### 1. Clean Up the Repository

```bash
# Remove the generated file
git rm workspace_resolved.json

# Add to gitignore
echo "workspace_resolved.json" >> .gitignore

# Commit
git commit -m "Remove generated workspace_resolved.json from version control"
```

### 2. Document the Feature

Add to `docs/FEATURES.md`:

```markdown
## Type Resolution (Optional)

Resolve LIKE database type references to actual schema types.

**Prerequisites:**
- Schema file (.sch) for your codebase
- Codebase using LIKE type declarations

**Usage:**
```bash
# Load schema
python3 scripts/json_to_sqlite_schema.py schema.sch workspace.db

# Generate with type resolution
RESOLVE_TYPES=1 bash generate_all.sh /path/to/codebase
```

**Output:**
- `workspace_resolved.json` - Signatures with resolved types
```

### 3. Improve the Script

Enhance `generate_all.sh` to:
- Accept optional schema file parameter
- Automatically load schema if provided
- Only generate `workspace_resolved.json` if schema is available

```bash
# Usage:
bash generate_all.sh /path/to/codebase /path/to/schema.sch
```

## Current State Summary

| Aspect | Status |
|--------|--------|
| **Purpose** | Type resolution for LIKE references |
| **Implementation** | ✓ Complete (resolve_types.py) |
| **Documentation** | ✗ Missing |
| **In Version Control** | ✗ Should not be |
| **Generated From** | Sample codebase (not real workspace) |
| **Requires Schema** | ✓ Yes |
| **Actively Used** | ? Unknown |

## Next Steps

1. Decide if type resolution is a priority feature
2. If yes: Clean up repo, document, improve script
3. If no: Remove the feature and clean up code

**Recommendation:** Keep the feature but clean up the repo and documentation. It's useful for teams using LIKE types, but needs proper documentation and shouldn't be in version control.
