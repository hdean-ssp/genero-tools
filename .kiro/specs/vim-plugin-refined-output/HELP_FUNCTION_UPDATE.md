# Help Function Update - Feature 1.1

**Date:** March 25, 2026  
**Feature:** 1.1 Refined Output for Vim Plugin  
**Update:** Help function and documentation synchronized

---

## Overview

The `query.sh` help function has been updated to include all new format and filter options for the Refined Output for Vim Plugin feature. All documentation has been synchronized to reference the help function.

---

## Changes Made

### 1. Updated `src/query.sh` Help Function

**Added Sections:**

1. **Output format options**
   ```
   --format=vim                        Concise single-line function signatures
   --format=vim-hover                  Multi-line format with file location and metrics
   --format=vim-completion             Tab-separated format for Vim/Neovim completion
   ```

2. **Output filter options**
   ```
   --filter=functions-only             Exclude procedures (functions with no return type)
   --filter=no-metrics                 Remove complexity and LOC metrics
   --filter=no-file-info               Remove file path and line number
   ```

3. **Vim plugin integration examples**
   ```
   query.sh find-function "calculate" --format=vim
   query.sh find-function "calculate" --format=vim-hover
   query.sh search-functions "get_*" --format=vim-completion
   query.sh search-functions "*" --format=vim --filter=functions-only
   query.sh search-functions "get_*" --format=vim-hover --filter=no-metrics
   query.sh search-functions "*" --format=vim-completion --filter=functions-only
   ```

4. **Documentation references**
   ```
   For more information, see:
     docs/VIM_OUTPUT_FORMATS.md - Complete format reference
     docs/VIM_PLUGIN_INTEGRATION_GUIDE.md - Vim/Neovim integration guide
   ```

### 2. Updated `docs/VIM_OUTPUT_FORMATS.md`

**Added:**
- "Getting Help" section in Quick Start
- Instructions to run `bash query.sh --help`
- Note about help text including all options and examples

### 3. Updated `docs/VIM_PLUGIN_INTEGRATION_GUIDE.md`

**Added:**
- "Getting Help" section in Quick Start
- Instructions to run `bash query.sh --help`
- Description of what help text includes
- Links to detailed documentation

---

## Help Function Content

### Complete Help Output

```
Usage: query.sh <command> [args...] [--format=FORMAT] [--filter=FILTER]

Signature queries (workspace.db):
  find-function <name>                Find function by exact name
  find-function-resolved <name>       Find function with resolved LIKE types
  search-functions <pattern>          Search functions by name pattern
  list-file-functions <path>          List all functions in a file
  find-function-dependencies <name>   Find all functions called by a function
  find-function-dependents <name>     Find all functions that call a function
  find-dead-code                      Find functions that are never called

Module queries (modules.db):
  find-module <name>                  Find module by exact name
  search-modules <pattern>            Search modules by name pattern
  list-file-modules <filename>        Find modules using a file

Module-scoped queries (both databases):
  find-functions-in-module <name>     Find all functions in a module
  find-module-for-function <name>     Find which module(s) contain a function
  find-functions-calling-in-module <module> <func>  Find functions in module that call a function
  find-module-dependencies <name>     Find modules that a module depends on

Header/Reference queries (workspace.db):
  find-reference <ref>                Find files modified for a code reference
  find-author <author>                Find files modified by an author
  file-references <path>              Get all references for a file
  file-authors <path>                 Get all authors who modified a file
  author-expertise <author>           Show what areas an author has expertise in
  recent-changes [days]               Find files modified in last N days (default 30)
  search-references <pattern>         Search references by pattern (partial match)
  search-reference-prefix <prefix>    Search references by prefix (e.g., "EH100512" finds "EH100512-9a")

Type resolution queries:
  unresolved-types                    Find all unresolved LIKE type references
  unresolved-types --filter <type>    Filter by error type (missing_table, missing_column, invalid_pattern)
  unresolved-types --limit <n>        Limit results to N items
  unresolved-types --offset <n>       Skip first N items (for pagination)
  validate-types                      Validate type resolution data consistency

Batch queries:
  batch-query <json_file>             Execute multiple queries in a single batch
  batch-query --input <json_file> --output <output_file>  Execute batch with output file

Database management:
  create-dbs                          Create both databases from JSON files
  create-signatures-db                Create workspace.db from workspace.json
  create-modules-db                   Create modules.db from modules.json

Output format options (for Vim plugin integration):
  --format=vim                        Concise single-line function signatures
  --format=vim-hover                  Multi-line format with file location and metrics
  --format=vim-completion             Tab-separated format for Vim/Neovim completion

Output filter options (for Vim plugin integration):
  --filter=functions-only             Exclude procedures (functions with no return type)
  --filter=no-metrics                 Remove complexity and LOC metrics
  --filter=no-file-info               Remove file path and line number

Examples:
  query.sh find-function my_function
  query.sh search-functions "get_*"
  query.sh find-function-dependencies my_function
  query.sh find-functions-in-module core
  query.sh find-module-for-function my_function
  query.sh find-functions-calling-in-module core validate_input
  query.sh find-module-dependencies core
  query.sh find-reference PRB-299
  query.sh find-author "John Smith"
  query.sh file-references "./src/utils.4gl"
  query.sh author-expertise "John Smith"
  query.sh recent-changes 7
  query.sh unresolved-types
  query.sh unresolved-types --filter missing_table
  query.sh unresolved-types --limit 10 --offset 5
  query.sh batch-query queries.json
  query.sh batch-query --input queries.json --output results.json

Vim plugin integration examples:
  query.sh find-function "calculate" --format=vim
  query.sh find-function "calculate" --format=vim-hover
  query.sh search-functions "get_*" --format=vim-completion
  query.sh search-functions "*" --format=vim --filter=functions-only
  query.sh search-functions "get_*" --format=vim-hover --filter=no-metrics
  query.sh search-functions "*" --format=vim-completion --filter=functions-only

For more information, see:
  docs/VIM_OUTPUT_FORMATS.md - Complete format reference
  docs/VIM_PLUGIN_INTEGRATION_GUIDE.md - Vim/Neovim integration guide
```

---

## Documentation Synchronization

### Files Updated

1. **src/query.sh**
   - Added format options section
   - Added filter options section
   - Added Vim plugin integration examples
   - Added documentation references

2. **docs/VIM_OUTPUT_FORMATS.md**
   - Added "Getting Help" section
   - References help function
   - Links to help command

3. **docs/VIM_PLUGIN_INTEGRATION_GUIDE.md**
   - Added "Getting Help" section
   - References help function
   - Describes help content

### Cross-References

All documentation now includes:
- Reference to `bash query.sh --help`
- Description of what help includes
- Links to detailed documentation files

---

## User Experience

### Before

Users had to:
1. Read documentation files to learn about format options
2. Search for examples in docs
3. No built-in help for new options

### After

Users can now:
1. Run `bash query.sh --help` to see all options
2. See format and filter options in help
3. See Vim plugin integration examples in help
4. Get links to detailed documentation
5. Have everything in one place

---

## Testing

The help function has been verified to:
- ✅ Display all format options
- ✅ Display all filter options
- ✅ Include Vim plugin integration examples
- ✅ Include documentation references
- ✅ Maintain backward compatibility
- ✅ Not break existing functionality

---

## Documentation Consistency

All documentation now consistently references:
- Format options: `--format=vim|vim-hover|vim-completion`
- Filter options: `--filter=functions-only|no-metrics|no-file-info`
- Help command: `bash query.sh --help`
- Detailed docs: `docs/VIM_OUTPUT_FORMATS.md` and `docs/VIM_PLUGIN_INTEGRATION_GUIDE.md`

---

## Summary

The help function and documentation have been synchronized to provide a consistent user experience. Users can now:

✅ Run `bash query.sh --help` to see all options  
✅ See format and filter options in help  
✅ See Vim plugin integration examples  
✅ Get links to detailed documentation  
✅ Have everything documented in one place  

---

**Status:** Update Complete ✅  
**Date:** March 25, 2026  
**Version:** 1.0
