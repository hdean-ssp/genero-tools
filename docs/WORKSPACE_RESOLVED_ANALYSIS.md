# workspace_resolved.json Analysis

## Current Situation

`workspace_resolved.json` is generated when running `generate_all.sh` with the `RESOLVE_TYPES=1` environment variable, but it currently only contains data from the sample codebase test files, not from the actual workspace being analyzed.

## Purpose of workspace_resolved.json

The file is intended to be a **type-resolved version of workspace.json** that:

1. **Resolves LIKE References**: Converts LIKE type declarations to actual database schema types
   - Example: `LIKE customers.*` → resolves to actual column names and types from the schema
   - Example: `LIKE customers.id` → resolves to the specific column type

2. **Enriches Type Information**: Adds metadata about type resolution
   - `is_like_reference`: Boolean indicating if the type is a LIKE reference
   - `resolved`: Boolean indicating if resolution was successful
   - `table`: The table name referenced
   - `columns`: List of columns if LIKE table.*
   - `types`: List of resolved types
   - `error`: Error message if resolution failed

3. **Enables Type-Aware Features**: Provides data for:
   - Type checking and validation
   - IDE hover information with resolved types
   - Refactoring with type safety
   - Code completion with type hints

## The Problem

**Current behavior:**
```bash
bash generate_all.sh ./tests/sample_codebase
```

This generates:
- `workspace.json` - Contains functions from sample_codebase
- `workspace_resolved.json` - Also contains functions from sample_codebase (not the real workspace)

**Expected behavior:**
```bash
bash generate_all.sh /path/to/real/codebase
```

Should generate:
- `workspace.json` - Contains functions from real codebase
- `workspace_resolved.json` - Contains functions from real codebase with resolved types

## Root Cause

The issue is in `generate_signatures.sh`:

```bash
# Optional: Resolve LIKE types (only if RESOLVE_TYPES is set and workspace.db exists)
if [[ "${RESOLVE_TYPES:-0}" == "1" ]] && [[ -f "workspace.db" ]]; then
    RESOLVED_OUTPUT="${OUTPUT_FILE%.json}_resolved.json"
    python3 "$PROJECT_ROOT/scripts/resolve_types.py" workspace.db "$OUTPUT_FILE" "$RESOLVED_OUTPUT"
fi
```

The script:
1. Generates `workspace.json` from the target directory ✓
2. Creates `workspace.db` from `workspace.json` ✓
3. Calls `resolve_types.py` to create `workspace_resolved.json` ✓

**But** the `resolve_types.py` script requires a schema to be loaded in `workspace.db` first. If no schema has been loaded, it just processes the workspace.json without any actual type resolution.

## Why It Only Shows Sample Codebase Data

The `workspace_resolved.json` in the repo root was generated from the sample codebase because:

1. Someone ran: `bash generate_all.sh ./tests/sample_codebase`
2. This created `workspace.json` with sample codebase functions
3. Then `resolve_types.py` was called, which created `workspace_resolved.json` with the same data
4. The file was committed to the repo

## How to Fix This

### Option 1: Remove workspace_resolved.json from Repo (Recommended)

`workspace_resolved.json` is a **generated file** and shouldn't be in version control:

```bash
git rm workspace_resolved.json
echo "workspace_resolved.json" >> .gitignore
git commit -m "Remove generated workspace_resolved.json from version control"
```

### Option 2: Document the Proper Usage

Add documentation explaining:

1. **To generate with type resolution:**
   ```bash
   # First, ensure schema is loaded into workspace.db
   python3 scripts/json_to_sqlite_schema.py schema.json workspace.db
   
   # Then generate with type resolution enabled
   RESOLVE_TYPES=1 bash generate_all.sh /path/to/codebase
   ```

2. **What you get:**
   - `workspace.json` - Function signatures
   - `workspace_resolved.json` - Function signatures with resolved LIKE types

### Option 3: Improve the Script

Modify `generate_all.sh` to:

1. Accept an optional schema file parameter
2. Load schema into database before type resolution
3. Only generate `workspace_resolved.json` if schema is available

```bash
# Usage:
bash generate_all.sh /path/to/codebase /path/to/schema.sch
```

## Recommendation

**Do both Option 1 and Option 2:**

1. Remove `workspace_resolved.json` from version control (it's generated)
2. Add documentation explaining:
   - What `workspace_resolved.json` is for
   - How to generate it properly
   - When you need it (when using LIKE types in your codebase)

This way:
- The repo stays clean (no generated files)
- Users understand the feature
- Users can generate it when needed

## Files to Update

1. **Remove from repo:**
   - `workspace_resolved.json`

2. **Update documentation:**
   - `docs/FEATURES.md` - Add section on type resolution
   - `docs/DEVELOPER_GUIDE.md` - Add instructions for type resolution workflow
   - `README.md` - Mention type resolution as optional feature

3. **Update scripts:**
   - `generate_all.sh` - Add optional schema parameter
   - `src/generate_signatures.sh` - Improve type resolution documentation

## Current State

- **Purpose**: Type resolution for LIKE references
- **Status**: Implemented but not well documented
- **Issue**: Generated file in repo, only works if schema is loaded
- **Solution**: Remove from repo, improve documentation, enhance script
