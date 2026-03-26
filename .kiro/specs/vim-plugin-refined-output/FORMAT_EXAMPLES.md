# Output Format Examples

## Quick Reference

This document shows practical examples of all three output formats for the Refined Output for Vim Plugin feature.

---

## 1. Concise Format (`--format=vim`)

**Purpose:** Single-line function signatures for tooltips and quick reference  
**Use Case:** Display in editor status bar, quick info popups

### Examples

```bash
$ bash query.sh find-function "calculate" --format=vim
calculate(amount: DECIMAL, rate: DECIMAL) -> DECIMAL

$ bash query.sh search-functions "get_*" --format=vim
get_account(id: INTEGER) -> RECORD
get_balance(account_id: INTEGER) -> DECIMAL
get_customer_name(customer_id: INTEGER) -> VARCHAR(100)
```

### Format Pattern

```
function_name(param1: TYPE1, param2: TYPE2, ...) -> RETURN_TYPE
```

### Edge Cases

**No parameters:**
```
my_procedure() -> DECIMAL
```

**No return type:**
```
my_procedure(param1: INTEGER, param2: VARCHAR)
```

**Multiple return types:**
```
get_data(id: INTEGER) -> INTEGER, VARCHAR, DECIMAL
```

---

## 2. Hover Format (`--format=vim-hover`)

**Purpose:** Detailed information for editor hover tooltips  
**Use Case:** Display when hovering over function names in editor

### Examples

```bash
$ bash query.sh find-function "calculate" --format=vim-hover
calculate(amount: DECIMAL, rate: DECIMAL) -> DECIMAL
File: src/math.4gl:42
Complexity: 5, LOC: 23

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

### Format Pattern

```
function_name(params) -> return_type
File: path/to/file.4gl:line_number
Complexity: N, LOC: M
```

### Edge Cases

**Missing file information:**
```
my_function(param1: INTEGER) -> DECIMAL
File: unknown
Complexity: unknown, LOC: unknown
```

**Multiple functions (separated by blank line):**
```
function1(param1: INTEGER) -> DECIMAL
File: src/module.4gl:42
Complexity: 5, LOC: 23

function2(param2: VARCHAR) -> INTEGER
File: src/module.4gl:78
Complexity: 3, LOC: 12
```

---

## 3. Completion Format (`--format=vim-completion`)

**Purpose:** Tab-separated format for Vim/Neovim completion integration  
**Use Case:** Autocomplete suggestions in editor

### Examples

```bash
$ bash query.sh search-functions "get_*" --format=vim-completion
get_account	function(id: INTEGER) -> RECORD	src/queries.4gl:128 | Complexity: 3, LOC: 15
get_balance	function(account_id: INTEGER) -> DECIMAL	src/queries.4gl:156 | Complexity: 2, LOC: 8
get_customer_name	function(customer_id: INTEGER) -> VARCHAR(100)	src/queries.4gl:201 | Complexity: 1, LOC: 5

$ bash query.sh find-function "calculate" --format=vim-completion
calculate	function(amount: DECIMAL, rate: DECIMAL) -> DECIMAL	src/math.4gl:42 | Complexity: 5, LOC: 23
```

### Format Pattern

```
word<TAB>menu<TAB>info
```

Where:
- **word** = Function name (the completion word)
- **menu** = Function signature (displayed in completion menu)
- **info** = File location and metrics (displayed in info window)

### Tab-Separated Breakdown

For the line:
```
get_account	function(id: INTEGER) -> RECORD	src/queries.4gl:128 | Complexity: 3, LOC: 15
```

| Column | Value |
|--------|-------|
| 1 (word) | `get_account` |
| 2 (menu) | `function(id: INTEGER) -> RECORD` |
| 3 (info) | `src/queries.4gl:128 \| Complexity: 3, LOC: 15` |

### Edge Cases

**No parameters:**
```
my_procedure	function() -> DECIMAL	src/module.4gl:42 | Complexity: 5, LOC: 23
```

**No return type:**
```
my_procedure	function(param1: INTEGER, param2: VARCHAR)	src/module.4gl:42 | Complexity: 5, LOC: 23
```

**Missing metadata:**
```
my_function	function(param1: INTEGER) -> DECIMAL	unknown:0 | Complexity: unknown, LOC: unknown
```

---

## Vim Plugin Integration Examples

### Vim Script (Using Concise Format)

```vim
" Get function signature for hover
function! ShowFunctionInfo(func_name)
  let cmd = 'bash query.sh find-function "' . a:func_name . '" --format=vim'
  let signature = system(cmd)
  echo signature
endfunction

" Map to a key
nnoremap <leader>fi :call ShowFunctionInfo(expand('<cword>'))<CR>
```

### Vim Script (Using Completion Format)

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

### Neovim Lua (Using Completion Format)

```lua
-- Parse completion format
local function parse_completion(line)
  local parts = vim.split(line, "\t")
  return {
    label = parts[1],
    detail = parts[2],
    documentation = parts[3],
    kind = vim.lsp.protocol.CompletionItemKind.Function
  }
end

-- Get completions
local function get_completions(prefix)
  local cmd = 'bash query.sh search-functions "' .. prefix .. '*" --format=vim-completion'
  local output = vim.fn.system(cmd)
  local completions = {}
  
  for line in output:gmatch("[^\n]+") do
    if line ~= "" then
      table.insert(completions, parse_completion(line))
    end
  end
  
  return completions
end
```

---

## Filtering Examples

### Filter: functions-only

```bash
$ bash query.sh search-functions "*" --format=vim --filter=functions-only
# Returns only functions (excludes procedures)
```

### Filter: no-metrics

```bash
$ bash query.sh search-functions "get_*" --format=vim-hover --filter=no-metrics
get_account(id: INTEGER) -> RECORD
File: src/queries.4gl:128

get_balance(account_id: INTEGER) -> DECIMAL
File: src/queries.4gl:156
```

### Filter: no-file-info

```bash
$ bash query.sh search-functions "get_*" --format=vim-hover --filter=no-file-info
get_account(id: INTEGER) -> RECORD
Complexity: 3, LOC: 15

get_balance(account_id: INTEGER) -> DECIMAL
Complexity: 2, LOC: 8
```

### Multiple Filters

```bash
$ bash query.sh search-functions "get_*" --format=vim-hover --filter=functions-only --filter=no-metrics
get_account(id: INTEGER) -> RECORD
File: src/queries.4gl:128

get_balance(account_id: INTEGER) -> DECIMAL
File: src/queries.4gl:156
```

---

## Performance Characteristics

### Query Execution Time

| Format | Typical Time | Large Codebase |
|--------|--------------|----------------|
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

## Error Handling Examples

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

## Summary

- **Concise Format** - Best for quick reference and tooltips
- **Hover Format** - Best for detailed hover information
- **Completion Format** - Best for Vim/Neovim autocomplete integration

All formats are optimized for Vim/Neovim and provide excellent performance.
