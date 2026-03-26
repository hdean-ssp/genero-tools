# Vim Plugin Integration Guide

**Feature:** 1.1 Refined Output for Vim Plugin  
**Version:** 1.0  
**Date:** March 25, 2026

---

## Overview

This guide provides step-by-step instructions for integrating genero-tools output formats into Vim and Neovim plugins.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Vim Integration](#vim-integration)
3. [Neovim Integration](#neovim-integration)
4. [Common Patterns](#common-patterns)
5. [Advanced Usage](#advanced-usage)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Basic Vim Plugin Structure

```vim
" plugin/genero_tools.vim
if exists('g:loaded_genero_tools')
  finish
endif
let g:loaded_genero_tools = 1

" Define commands
command! -nargs=1 GeneroFind call genero_tools#find_function(<f-args>)
command! -nargs=1 GeneroSearch call genero_tools#search_functions(<f-args>)

" Define mappings
nnoremap <leader>gf :GeneroFind <C-R><C-W><CR>
nnoremap <leader>gs :GeneroSearch <C-R><C-W><CR>
```

### Basic Neovim Plugin Structure

```lua
-- plugin/genero_tools.lua
if vim.g.loaded_genero_tools then
  return
end
vim.g.loaded_genero_tools = true

-- Define commands
vim.api.nvim_create_user_command('GeneroFind', function(opts)
  require('genero_tools').find_function(opts.args)
end, { nargs = 1 })

-- Define mappings
vim.keymap.set('n', '<leader>gf', function()
  require('genero_tools').find_function(vim.fn.expand('<cword>'))
end)
```

### Getting Help

To see all available format and filter options with examples, run:

```bash
bash query.sh --help
```

This displays the complete help text including:
- All output format options (`--format=vim|vim-hover|vim-completion`)
- All filter options (`--filter=functions-only|no-metrics|no-file-info`)
- Vim plugin integration examples
- Links to detailed documentation

---

## Vim Integration

### 1. Function Signature Lookup (Concise Format)

Display function signature in status bar or echo area.

**Vim Script:**
```vim
function! genero_tools#find_function(func_name)
  let cmd = 'bash query.sh find-function "' . a:func_name . '" --format=vim'
  let signature = system(cmd)
  
  if v:shell_error == 0 && !empty(signature)
    echo signature
  else
    echohl ErrorMsg
    echo 'Function not found: ' . a:func_name
    echohl None
  endif
endfunction
```

**Usage:**
```vim
:GeneroFind calculate
" Output: calculate(amount: DECIMAL, rate: DECIMAL) -> DECIMAL
```

### 2. Hover Information (Hover Format)

Display detailed function information in preview window.

**Vim Script:**
```vim
function! genero_tools#show_hover_info(func_name)
  let cmd = 'bash query.sh find-function "' . a:func_name . '" --format=vim-hover'
  let info = system(cmd)
  
  if v:shell_error == 0 && !empty(info)
    " Close existing preview
    pclose
    
    " Create new preview window
    new +setlocal\ previewwindow
    call append(0, split(info, "\n"))
    setlocal nomodifiable
    setlocal nobuflisted
    setlocal buftype=nofile
    
    " Return to previous window
    wincmd p
  endif
endfunction

" Map to key
nnoremap <leader>fi :call genero_tools#show_hover_info(expand('<cword>'))<CR>
```

**Usage:**
```vim
" Position cursor on function name and press <leader>fi
" Preview window shows:
" calculate(amount: DECIMAL, rate: DECIMAL) -> DECIMAL
" File: src/math.4gl:42
" Complexity: 5, LOC: 23
```

### 3. Autocomplete Integration (Completion Format)

Integrate with Vim's completion system.

**Vim Script:**
```vim
function! genero_tools#complete_functions(findstart, base)
  if a:findstart
    " Find start of word
    let line = getline('.')
    let start = col('.') - 1
    while start > 0 && line[start - 1] =~ '\w'
      let start -= 1
    endwhile
    return start
  else
    " Find matching functions
    let cmd = 'bash query.sh search-functions "' . a:base . '*" --format=vim-completion'
    let output = system(cmd)
    let completions = []
    
    for line in split(output, "\n")
      if !empty(line)
        let parts = split(line, "\t")
        if len(parts) >= 3
          call add(completions, {
            \ 'word': parts[0],
            \ 'menu': parts[1],
            \ 'info': parts[2]
          \ })
        endif
      endif
    endfor
    
    return completions
  endif
endfunction

" Set completion function
set completefunc=genero_tools#complete_functions
```

**Usage:**
```vim
" In insert mode, type function name prefix and press Ctrl-X Ctrl-U
" Completion menu shows:
" calculate    function(amount: DECIMAL, rate: DECIMAL) -> DECIMAL
" get_account  function(id: INTEGER) -> RECORD
```

### 4. Search and Display Results

Search for functions and display results in quickfix list.

**Vim Script:**
```vim
function! genero_tools#search_functions(pattern)
  let cmd = 'bash query.sh search-functions "' . a:pattern . '" --format=vim-hover'
  let output = system(cmd)
  
  if v:shell_error == 0 && !empty(output)
    " Parse output and create quickfix list
    let items = []
    let lines = split(output, "\n")
    
    for line in lines
      if line =~ '^[a-zA-Z_]'
        " This is a function signature line
        let parts = split(line, '(')
        let func_name = parts[0]
        
        call add(items, {
          \ 'text': line,
          \ 'type': 'I'
        \ })
      endif
    endfor
    
    call setqflist(items)
    copen
  else
    echohl ErrorMsg
    echo 'No functions found matching: ' . a:pattern
    echohl None
  endif
endfunction
```

**Usage:**
```vim
:GeneroSearch get_*
" Quickfix list shows all matching functions
```

---

## Neovim Integration

### 1. Function Signature Lookup (Concise Format)

Display function signature using Neovim's notification system.

**Lua:**
```lua
local M = {}

function M.find_function(func_name)
  local cmd = 'bash query.sh find-function "' .. func_name .. '" --format=vim'
  local output = vim.fn.system(cmd)
  
  if vim.v.shell_error == 0 and output ~= '' then
    vim.notify(output, vim.log.levels.INFO)
  else
    vim.notify('Function not found: ' .. func_name, vim.log.levels.ERROR)
  end
end

return M
```

**Usage:**
```lua
require('genero_tools').find_function('calculate')
-- Notification shows: calculate(amount: DECIMAL, rate: DECIMAL) -> DECIMAL
```

### 2. Hover Information (Hover Format)

Display detailed function information in floating window.

**Lua:**
```lua
function M.show_hover_info(func_name)
  local cmd = 'bash query.sh find-function "' .. func_name .. '" --format=vim-hover'
  local output = vim.fn.system(cmd)
  
  if vim.v.shell_error == 0 and output ~= '' then
    local lines = vim.split(output, '\n')
    
    -- Create buffer
    local buf = vim.api.nvim_create_buf(false, true)
    vim.api.nvim_buf_set_lines(buf, 0, -1, false, lines)
    
    -- Create floating window
    local opts = {
      relative = 'cursor',
      width = math.max(50, #lines[1] + 2),
      height = #lines,
      col = 0,
      row = 1,
      style = 'minimal',
      border = 'rounded'
    }
    
    vim.api.nvim_open_win(buf, false, opts)
  else
    vim.notify('Function not found: ' .. func_name, vim.log.levels.ERROR)
  end
end
```

**Usage:**
```lua
require('genero_tools').show_hover_info('calculate')
-- Floating window shows function info
```

### 3. LSP Completion Integration (Completion Format)

Integrate with Neovim's LSP completion system.

**Lua:**
```lua
function M.get_completions(prefix)
  local cmd = 'bash query.sh search-functions "' .. prefix .. '*" --format=vim-completion'
  local output = vim.fn.system(cmd)
  local completions = {}
  
  for line in output:gmatch('[^\n]+') do
    if line ~= '' then
      local parts = vim.split(line, '\t')
      if #parts >= 3 then
        table.insert(completions, {
          label = parts[1],
          detail = parts[2],
          documentation = parts[3],
          kind = vim.lsp.protocol.CompletionItemKind.Function
        })
      end
    end
  end
  
  return completions
end
```

**Usage:**
```lua
-- Use in LSP completion source
local completions = require('genero_tools').get_completions('get_')
-- Returns completion items for LSP
```

### 4. Telescope Integration

Integrate with Telescope for fuzzy search.

**Lua:**
```lua
local telescope = require('telescope.builtin')
local pickers = require('telescope.pickers')
local finders = require('telescope.finders')
local conf = require('telescope.config').values

function M.telescope_functions()
  local cmd = 'bash query.sh search-functions "*" --format=vim-hover'
  local output = vim.fn.system(cmd)
  local lines = vim.split(output, '\n')
  
  pickers.new({}, {
    prompt_title = 'Genero Functions',
    finder = finders.new_table({
      results = lines
    }),
    sorter = conf.generic_sorter({})
  }):find()
end
```

**Usage:**
```lua
require('genero_tools').telescope_functions()
-- Opens Telescope picker with all functions
```

---

## Common Patterns

### Pattern 1: Show Info on Hover

**Vim:**
```vim
function! genero_tools#on_hover()
  let word = expand('<cword>')
  call genero_tools#show_hover_info(word)
endfunction

" Show info when hovering over function name
nnoremap <silent> K :call genero_tools#on_hover()<CR>
```

**Neovim:**
```lua
vim.keymap.set('n', 'K', function()
  require('genero_tools').show_hover_info(vim.fn.expand('<cword>'))
end, { silent = true })
```

### Pattern 2: Go to Definition

**Vim:**
```vim
function! genero_tools#goto_definition()
  let word = expand('<cword>')
  let cmd = 'bash query.sh find-function "' . word . '" --format=vim-hover'
  let output = system(cmd)
  
  " Parse file and line from output
  let lines = split(output, "\n")
  for line in lines
    if line =~ '^File:'
      let file_info = split(line, ':')
      let file = file_info[1]
      let line_num = file_info[2]
      
      " Open file and go to line
      execute 'edit ' . file
      execute ':' . line_num
      break
    endif
  endfor
endfunction

nnoremap <leader>gd :call genero_tools#goto_definition()<CR>
```

### Pattern 3: Find References

**Vim:**
```vim
function! genero_tools#find_references()
  let word = expand('<cword>')
  let cmd = 'bash query.sh find-function-dependents "' . word . '" --format=vim'
  let output = system(cmd)
  
  " Display in quickfix list
  let items = []
  for line in split(output, "\n")
    call add(items, { 'text': line })
  endfor
  
  call setqflist(items)
  copen
endfunction

nnoremap <leader>gr :call genero_tools#find_references()<CR>
```

### Pattern 4: Show Complexity

**Vim:**
```vim
function! genero_tools#show_complexity()
  let word = expand('<cword>')
  let cmd = 'bash query.sh find-function "' . word . '" --format=vim-hover'
  let output = system(cmd)
  
  " Extract complexity from output
  for line in split(output, "\n")
    if line =~ '^Complexity:'
      echo line
      break
    endif
  endfor
endfunction

nnoremap <leader>gc :call genero_tools#show_complexity()<CR>
```

---

## Advanced Usage

### Custom Output Formatting

**Vim:**
```vim
function! genero_tools#format_custom(func_name)
  let cmd = 'bash query.sh find-function "' . a:func_name . '" --format=vim-hover'
  let output = system(cmd)
  
  " Custom formatting
  let lines = split(output, "\n")
  let formatted = []
  
  for line in lines
    if line =~ '^File:'
      call add(formatted, '📁 ' . line)
    elseif line =~ '^Complexity:'
      call add(formatted, '⚙️  ' . line)
    else
      call add(formatted, '📝 ' . line)
    endif
  endfor
  
  return formatted
endfunction
```

### Caching Results

**Vim:**
```vim
let g:genero_cache = {}

function! genero_tools#find_cached(func_name)
  if has_key(g:genero_cache, a:func_name)
    return g:genero_cache[a:func_name]
  endif
  
  let cmd = 'bash query.sh find-function "' . a:func_name . '" --format=vim'
  let result = system(cmd)
  
  let g:genero_cache[a:func_name] = result
  return result
endfunction
```

### Error Handling

**Vim:**
```vim
function! genero_tools#safe_find(func_name)
  try
    let cmd = 'bash query.sh find-function "' . a:func_name . '" --format=vim'
    let result = system(cmd)
    
    if v:shell_error != 0
      throw 'Query failed: ' . result
    endif
    
    if empty(result)
      throw 'Function not found: ' . a:func_name
    endif
    
    return result
  catch
    echohl ErrorMsg
    echo 'Error: ' . v:exception
    echohl None
    return ''
  endtry
endfunction
```

---

## Troubleshooting

### Issue: "Command not found"

**Problem:** `bash query.sh` command not found

**Solution:**
1. Ensure genero-tools is installed
2. Add genero-tools directory to PATH
3. Use full path: `/path/to/genero-tools/query.sh`

### Issue: "Database not found"

**Problem:** Query returns "Database not found" error

**Solution:**
1. Generate database: `bash generate_all.sh /path/to/code`
2. Ensure database files exist: `workspace.db`, `modules.db`
3. Check database location matches query.sh expectations

### Issue: Empty results

**Problem:** Query returns no results

**Solution:**
1. Verify function exists in codebase
2. Check function name spelling
3. Try wildcard search: `search-functions "func_*"`

### Issue: Slow performance

**Problem:** Queries are slow

**Solution:**
1. Use concise format (`--format=vim`) for faster output
2. Apply filters to reduce result size
3. Ensure database is created (faster than JSON)
4. Check system resources

### Issue: Format not recognized

**Problem:** "Invalid format" error

**Solution:**
Use one of the supported formats:
- `--format=vim` (concise)
- `--format=vim-hover` (hover)
- `--format=vim-completion` (completion)

---

## Performance Tips

1. **Use concise format** - Fastest output format
2. **Apply filters** - Reduce result size
3. **Cache results** - Avoid repeated queries
4. **Use database** - Faster than JSON parsing
5. **Limit results** - Use pagination for large result sets

---

## Related Documentation

- [VIM_OUTPUT_FORMATS.md](VIM_OUTPUT_FORMATS.md)
- [QUERYING.md](QUERYING.md)
- [FEATURES.md](FEATURES.md)

---

**Version:** 1.0  
**Last Updated:** March 25, 2026  
**Status:** Complete
