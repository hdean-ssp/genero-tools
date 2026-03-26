# Completion Format Rationale: Tab-Separated vs JSON

## Decision: Use Vim-Native Tab-Separated Format

**Date:** March 25, 2026  
**Status:** Approved  
**Rationale:** Optimized for Vim/Neovim native completion API

---

## Why Tab-Separated Format?

### 1. Native Vim/Neovim Compatibility

Vim's `complete()` function and Neovim's completion API expect tab-separated format:

```vim
" Vim completion item structure
{
  'word': 'my_function',           " Column 1: The completion word
  'menu': 'function(...) -> TYPE',  " Column 2: Menu text (signature)
  'info': 'file:line | metrics'    " Column 3: Info text (details)
}
```

Tab-separated format maps directly to this structure with zero parsing overhead.

### 2. Performance Benefits

- **No JSON parsing** - Direct tab-split is faster
- **Streaming-friendly** - Can process line-by-line
- **Lower memory** - No JSON object overhead
- **Faster plugin integration** - Vim plugins can use native `split()` function

### 3. Simplicity

Tab-separated is simpler than JSON:
- One line per completion item
- Three columns: word, menu, info
- No escaping needed for most content
- Easy to debug (human-readable)

### 4. Neovim LSP Compatibility

Modern Neovim LSP completion items use this exact structure:

```lua
-- Neovim LSP completion item
{
  label = "my_function",
  kind = CompletionItemKind.Function,
  detail = "function(param1: INTEGER, param2: VARCHAR) -> DECIMAL",
  documentation = "src/module.4gl:42 | Complexity: 5, LOC: 23"
}
```

Tab-separated format maps directly to LSP completion items.

---

## Format Specification

### Tab-Separated Format

```
word<TAB>menu<TAB>info
```

**Example:**
```
my_function	function(param1: INTEGER, param2: VARCHAR) -> DECIMAL	src/module.4gl:42 | Complexity: 5, LOC: 23
get_account	function(id: INTEGER) -> RECORD	src/queries.4gl:128 | Complexity: 3, LOC: 15
calculate	function(amount: DECIMAL, rate: DECIMAL) -> DECIMAL	src/math.4gl:5 | Complexity: 2, LOC: 8
```

### Column Definitions

| Column | Name | Content | Example |
|--------|------|---------|---------|
| 1 | word | Function name (completion word) | `my_function` |
| 2 | menu | Function signature | `function(param1: INTEGER, param2: VARCHAR) -> DECIMAL` |
| 3 | info | File location and metrics | `src/module.4gl:42 \| Complexity: 5, LOC: 23` |

### Edge Cases

**No parameters:**
```
my_function	function() -> DECIMAL	src/module.4gl:42 | Complexity: 5, LOC: 23
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

## Vim Plugin Integration

### Vim Script Example

```vim
" Parse completion format in Vim
function! ParseCompletion(line)
  let parts = split(a:line, "\t")
  return {
    \ 'word': parts[0],
    \ 'menu': parts[1],
    \ 'info': parts[2]
  \ }
endfunction

" Use in completion
let completions = []
for line in split(system('bash query.sh search-functions "get_*" --format=vim-completion'), "\n")
  if !empty(line)
    call add(completions, ParseCompletion(line))
  endif
endfor
```

### Neovim Lua Example

```lua
-- Parse completion format in Neovim
local function parse_completion(line)
  local parts = vim.split(line, "\t")
  return {
    label = parts[1],
    detail = parts[2],
    documentation = parts[3],
    kind = vim.lsp.protocol.CompletionItemKind.Function
  }
end

-- Use in completion
local completions = {}
local output = vim.fn.system('bash query.sh search-functions "get_*" --format=vim-completion')
for line in output:gmatch("[^\n]+") do
  if line ~= "" then
    table.insert(completions, parse_completion(line))
  end
end
```

---

## Comparison: Tab-Separated vs JSON

| Aspect | Tab-Separated | JSON |
|--------|---------------|------|
| **Parsing** | Native `split()` | JSON parser required |
| **Performance** | Faster | Slower |
| **Memory** | Lower | Higher |
| **Vim Integration** | Native | Requires parsing |
| **Neovim LSP** | Direct mapping | Requires conversion |
| **Readability** | Human-readable | Human-readable |
| **Escaping** | Minimal | Required for special chars |
| **Streaming** | Line-by-line | Full parse required |
| **Complexity** | Simple | Complex |

---

## Why Not JSON?

1. **Unnecessary complexity** - JSON adds parsing overhead for simple data
2. **Vim incompatibility** - Vim's `complete()` expects tab-separated, not JSON
3. **Performance** - JSON parsing is slower than tab-split
4. **Memory** - JSON objects use more memory than simple strings
5. **Neovim LSP** - LSP completion items don't use JSON format

---

## Backward Compatibility

- Tab-separated format is **new** - no existing code depends on it
- Default format (without `--format` option) remains unchanged
- Existing queries continue to work as before
- No breaking changes to existing API

---

## Future Extensibility

If additional metadata is needed in the future:

1. **Add more columns** - Tab-separated can easily extend to 4+ columns
2. **Structured info column** - The info column can contain pipe-separated sub-fields
3. **Optional columns** - Plugins can ignore columns they don't need

Example with extended columns:
```
word	menu	file	line	complexity	loc	info
my_function	function(...) -> TYPE	src/module.4gl	42	5	23	Additional metadata
```

---

## Conclusion

Tab-separated format is the optimal choice for Vim/Neovim completion because it:
- Maps directly to Vim's `complete()` function
- Maps directly to Neovim's LSP completion items
- Requires no parsing overhead
- Is simpler and more efficient than JSON
- Maintains backward compatibility
- Provides excellent performance

This decision aligns with Vim/Neovim best practices and provides the best user experience for plugin developers.

---

**Status:** Approved  
**Implementation:** Ready to proceed with tab-separated format  
**Testing:** Verify Vim/Neovim integration with sample plugins
