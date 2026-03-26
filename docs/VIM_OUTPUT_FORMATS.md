# Vim Output Formats - Complete Reference

**Feature:** 1.1 Refined Output for Vim Plugin  
**Version:** 1.0  
**Date:** March 25, 2026

---

## Overview

The Refined Output for Vim Plugin feature provides three optimized output formats for Vim/Neovim integration:

1. **Concise Format** - Single-line function signatures for tooltips
2. **Hover Format** - Multi-line with file location and metrics for hover tooltips
3. **Completion Format** - Tab-separated for Vim/Neovim completion API

All formats are optimized for editor integration and provide excellent performance (<100ms for typical codebases).

---

## Quick Start

### Using Concise Format

```bash
bash query.sh find-function "calculate" --format=vim
```

**Output:**
```
calculate(amount: DECIMAL, rate: DECIMAL) -> DECIMAL
```

### Using Hover Format

```bash
bash query.sh find-function "calculate" --format=vim-hover
```

**Output:**
```
calculate(amount: DECIMAL, rate: DECIMAL) -> DECIMAL
File: src/math.4gl:42
Complexity: 5, LOC: 23
```

### Using Completion Format

```bash
bash query.sh search-functions "get_*" --format=vim-completion
```

**Output:**
```
calculate	function(amount: DECIMAL, rate: DECIMAL) -> DECIMAL	src/math.4gl:42 | Complexity: 5, LOC: 23
get_account	function(id: INTEGER) -> RECORD	src/queries.4gl:128 | Complexity: 3, LOC: 15
```

### Getting Help

To see all available options and examples, run:

```bash
bash query.sh --help
```

This displays the complete help text including all format and filter options with examples.

---

## Format 1: Concise Format (`--format=vim`)

### Purpose

Display compact function signatures for tooltips, status bar, or quick reference.

### Format Specification

```
function_name(param1: TYPE1, param2: TYPE2, ...) -> RETURN_TYPE
```

### Characteristics

- **Single line** - One signature per line
- **Compact** - No file path or metrics
- **Fast** - Minimal output size
- **Readable** - Clear parameter and return type information

### Examples

#### Basic Function

```bash
$ bash query.sh find-function "calculate" --format=vim
calculate(amount: DECIMAL, rate: DECIMAL) -> DECIMAL
```

#### Function with No Parameters

```bash
$ bash query.sh find-function "get_timestamp" --format=vim
get_timestamp() -> DATETIME
```

#### Procedure (No Return Type)

```bash
$ bash query.sh find-function "my_procedure" --format=vim
my_procedure(id: INTEGER, name: VARCHAR)
```

#### Multiple Return Types

```bash
$ bash query.sh find-function "get_data" --format=vim
get_data(id: INTEGER) -> INTEGER, VARCHAR, DECIMAL
```

#### Complex Types

```bash
$ bash query.sh find-function "process_record" --format=vim
process_record(data: RECORD, items: ARRAY[100]) -> RECORD
```

#### Multiple Functions

```bash
$ bash query.sh search-functions "get_*" --format=vim
get_account(id: INTEGER) -> RECORD
get_balance(account_id: INTEGER) -> DECIMAL
get_customer_name(customer_id: INTEGER) -> VARCHAR(100)
```

### Use Cases

- **Editor tooltips** - Show signature when hovering over function name
- **Status bar** - Display current function signature
- **Quick reference** - Show function signature in command output
- **Completion menu** - Display function signature in completion menu

### Vim Integration Example

```vim
" Show function signature in status bar
function! ShowFunctionSignature(func_name)
  let cmd = 'bash query.sh find-function "' . a:func_name . '" --format=vim'
  let signature = system(cmd)
  echo signature
endfunction

" Map to a key
nnoremap <leader>fs :call ShowFunctionSignature(expand('<cword>'))<CR>
```

---

## Format 2: Hover Format (`--format=vim-hover`)

### Purpose

Display detailed function information for editor hover tooltips with file location and complexity metrics.

### Format Specification

```
function_name(param1: TYPE1, param2: TYPE2, ...) -> RETURN_TYPE
File: path/to/file.4gl:line_number
Complexity: N, LOC: M
```

### Characteristics

- **Three lines** - Signature, file location, metrics
- **Detailed** - Includes file path, line number, and complexity
- **Readable** - Multi-line format for easy scanning
- **Informative** - Shows code quality metrics

### Examples

#### Basic Function

```bash
$ bash query.sh find-function "calculate" --format=vim-hover
calculate(amount: DECIMAL, rate: DECIMAL) -> DECIMAL
File: src/math.4gl:42
Complexity: 5, LOC: 23
```

#### Multiple Functions

```bash
$ bash query.sh search-functions "get_*" --format=vim-hover
get_account(id: INTEGER) -> RECORD
File: src/queries.4gl:128
Complexity: 3, LOC: 15

get_balance(account_id: INTEGER) -> DECIMAL
File: src/queries.4gl:156
Complexity: 2, LOC: 8

get_customer_name(customer_id: INTEGER) -> VARCHAR(100)
File: src/queries.4gl:201
Complexity: 1, LOC: 5
```

#### Missing Metrics

```bash
$ bash query.sh find-function "unknown_func" --format=vim-hover
unknown_func(param: INTEGER) -> DECIMAL
File: unknown
Complexity: unknown, LOC: unknown
```

### Use Cases

- **Editor hover tooltips** - Show detailed info when hovering over function
- **Go-to-definition preview** - Show function info before jumping
- **Code review** - Display function complexity and size
- **Documentation** - Generate function documentation

### Vim Integration Example

```vim
" Show function info in preview window
function! ShowFunctionInfo(func_name)
  let cmd = 'bash query.sh find-function "' . a:func_name . '" --format=vim-hover'
  let info = system(cmd)
  
  " Create preview window
  pclose
  new +setlocal\ previewwindow
  call append(0, split(info, "\n"))
  setlocal nomodifiable
  wincmd p
endfunction

" Map to a key
nnoremap <leader>fi :call ShowFunctionInfo(expand('<cword>'))<CR>
```

### Neovim Integration Example

```lua
-- Show function info in floating window
local function show_function_info(func_name)
  local cmd = 'bash query.sh find-function "' .. func_name .. '" --format=vim-hover'
  local info = vim.fn.system(cmd)
  
  -- Create floating window
  local buf = vim.api.nvim_create_buf(false, true)
  vim.api.nvim_buf_set_lines(buf, 0, -1, false, vim.split(info, "\n"))
  
  local opts = {
    relative = "cursor",
    width = 50,
    height = 3,
    col = 0,
    row = 1,
    style = "minimal",
    border = "rounded"
  }
  
  vim.api.nvim_open_win(buf, false, opts)
end

-- Map to a key
vim.keymap.set('n', '<leader>fi', function()
  show_function_info(vim.fn.expand('<cword>'))
end)
```

---

## Format 3: Completion Format (`--format=vim-completion`)

### Purpose

Provide function metadata in tab-separated format for Vim/Neovim completion API integration.

### Format Specification

```
word<TAB>menu<TAB>info
```

**Columns:**
- **Column 1 (word):** Function name (the completion word)
- **Column 2 (menu):** Function signature (displayed in completion menu)
- **Column 3 (info):** File location and metrics (displayed in info window)

### Characteristics

- **Tab-separated** - Native Vim completion format
- **Three columns** - Word, menu, info
- **Vim-native** - Compatible with Vim's `complete()` function
- **Neovim-native** - Compatible with Neovim's LSP completion items

### Examples

#### Single Function

```bash
$ bash query.sh find-function "calculate" --format=vim-completion
calculate	function(amount: DECIMAL, rate: DECIMAL) -> DECIMAL	src/math.4gl:42 | Complexity: 5, LOC: 23
```

#### Multiple Functions

```bash
$ bash query.sh search-functions "get_*" --format=vim-completion
get_account	function(id: INTEGER) -> RECORD	src/queries.4gl:128 | Complexity: 3, LOC: 15
get_balance	function(account_id: INTEGER) -> DECIMAL	src/queries.4gl:156 | Complexity: 2, LOC: 8
get_customer_name	function(customer_id: INTEGER) -> VARCHAR(100)	src/queries.4gl:201 | Complexity: 1, LOC: 5
```

#### Tab-Separated Breakdown

For the line:
```
calculate	function(amount: DECIMAL, rate: DECIMAL) -> DECIMAL	src/math.4gl:42 | Complexity: 5, LOC: 23
```

| Column | Value |
|--------|-------|
| 1 (word) | `calculate` |
| 2 (menu) | `function(amount: DECIMAL, rate: DECIMAL) -> DECIMAL` |
| 3 (info) | `src/math.4gl:42 \| Complexity: 5, LOC: 23` |

### Use Cases

- **Vim completion** - Autocomplete suggestions
- **Neovim LSP** - Language server protocol completion
- **Plugin integration** - Custom completion plugins
- **Editor integration** - IDE/editor plugins

### Vim Integration Example

```vim
" Autocomplete using completion format
function! GetFunctionCompletions(prefix)
  let cmd = 'bash query.sh search-functions "' . a:prefix . '*" --format=vim-completion'
  let output = system(cmd)
  let completions = []
  
  for line in split(output, "\n")
    if !empty(line)
      let parts = split(line, "\t")
      call add(completions, {
        \ 'word': parts[0],
        \ 'menu': parts[1],
        \ 'info': parts[2]
      \ })
    endif
  endfor
  
  return completions
endfunction

" Use in completion
set completefunc=GetFunctionCompletions
```

### Neovim Integration Example

```lua
-- Autocomplete using completion format
local function get_function_completions(prefix)
  local cmd = 'bash query.sh search-functions "' .. prefix .. '*" --format=vim-completion'
  local output = vim.fn.system(cmd)
  local completions = {}
  
  for line in output:gmatch("[^\n]+") do
    if line ~= "" then
      local parts = vim.split(line, "\t")
      table.insert(completions, {
        label = parts[1],
        detail = parts[2],
        documentation = parts[3],
        kind = vim.lsp.protocol.CompletionItemKind.Function
      })
    end
  end
  
  return completions
end
```

---

## Filtering Options

All formats support filtering to customize output:

### Filter: `--filter=functions-only`

Exclude procedures (functions with no return type).

**Example:**
```bash
$ bash query.sh search-functions "*" --format=vim --filter=functions-only
# Returns only functions, excludes procedures
```

### Filter: `--filter=no-metrics`

Remove complexity and LOC metrics.

**Example:**
```bash
$ bash query.sh search-functions "get_*" --format=vim-hover --filter=no-metrics
get_account(id: INTEGER) -> RECORD
File: src/queries.4gl:128

get_balance(account_id: INTEGER) -> DECIMAL
File: src/queries.4gl:156
```

### Filter: `--filter=no-file-info`

Remove file path and line number.

**Example:**
```bash
$ bash query.sh search-functions "get_*" --format=vim-hover --filter=no-file-info
get_account(id: INTEGER) -> RECORD
Complexity: 3, LOC: 15

get_balance(account_id: INTEGER) -> DECIMAL
Complexity: 2, LOC: 8
```

### Multiple Filters

Combine multiple filters:

```bash
$ bash query.sh search-functions "*" --format=vim-hover \
  --filter=functions-only --filter=no-metrics
```

---

## Command Reference

### Syntax

```bash
bash query.sh <command> <args> [--format=FORMAT] [--filter=FILTER]
```

### Format Options

| Option | Format | Use Case |
|--------|--------|----------|
| `--format=vim` | Concise | Tooltips, status bar |
| `--format=vim-hover` | Hover | Hover tooltips, preview |
| `--format=vim-completion` | Tab-separated | Completion, LSP |

### Filter Options

| Option | Effect |
|--------|--------|
| `--filter=functions-only` | Exclude procedures |
| `--filter=no-metrics` | Remove complexity/LOC |
| `--filter=no-file-info` | Remove file path/line |

### Examples

```bash
# Concise format
bash query.sh find-function "calculate" --format=vim

# Hover format
bash query.sh find-function "calculate" --format=vim-hover

# Completion format
bash query.sh search-functions "get_*" --format=vim-completion

# With filters
bash query.sh search-functions "*" --format=vim --filter=functions-only

# Multiple filters
bash query.sh search-functions "*" --format=vim-hover \
  --filter=functions-only --filter=no-metrics
```

---

## Performance Characteristics

### Query Execution Time

| Format | Typical | Large Codebase |
|--------|---------|----------------|
| Concise | <10ms | <50ms |
| Hover | <15ms | <75ms |
| Completion | <20ms | <100ms |

All formats meet the <100ms target for typical codebases.

### Output Size

| Format | Single Function | 100 Functions |
|--------|-----------------|---------------|
| Concise | ~50 bytes | ~5 KB |
| Hover | ~100 bytes | ~10 KB |
| Completion | ~150 bytes | ~15 KB |

---

## Error Handling

### Invalid Format

```bash
$ bash query.sh find-function "calculate" --format=invalid
Error: Invalid format 'invalid'. Supported formats: vim, vim-hover, vim-completion
```

### Invalid Filter

```bash
$ bash query.sh find-function "calculate" --filter=invalid
Error: Invalid filter 'invalid'. Supported filters: functions-only, no-metrics, no-file-info
```

### Function Not Found

```bash
$ bash query.sh find-function "nonexistent" --format=vim
# Returns empty result (not an error)
```

### Database Not Found

```bash
$ bash query.sh find-function "calculate" --format=vim
Error: Database not found. Run 'bash generate_all.sh /path/to/code' to create database.
```

---

## Backward Compatibility

- **Default behavior unchanged** - Queries without `--format` option return JSON (current behavior)
- **All existing queries work** - No breaking changes
- **Fully compatible** - Works with v2.1.0 and later

---

## Troubleshooting

### Format not recognized

**Problem:** "Invalid format" error

**Solution:** Use one of the supported formats:
- `--format=vim` (concise)
- `--format=vim-hover` (hover)
- `--format=vim-completion` (completion)

### Filter not working

**Problem:** Filter doesn't seem to have effect

**Solution:** Verify filter name and syntax:
- `--filter=functions-only` (exclude procedures)
- `--filter=no-metrics` (remove metrics)
- `--filter=no-file-info` (remove file info)

### Empty output

**Problem:** No results returned

**Solution:** Check if:
- Function exists in database
- Database is created: `bash generate_all.sh /path/to/code`
- Query pattern is correct

### Performance issues

**Problem:** Queries are slow

**Solution:**
- Use concise format for faster output
- Apply filters to reduce result size
- Ensure database is created (faster than JSON)

---

## Related Documentation

- [Requirements Document](requirements.md)
- [Completion Format Rationale](COMPLETION_FORMAT_RATIONALE.md)
- [Format Examples](FORMAT_EXAMPLES.md)
- [QUERYING.md](QUERYING.md)
- [FEATURES.md](FEATURES.md)

---

**Version:** 1.0  
**Last Updated:** March 25, 2026  
**Status:** Complete
