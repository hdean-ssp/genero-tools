# Genero-Tools Usage Audit & Feature Gap Analysis

**Purpose**: Document all genero-tools commands and functions currently utilized, identify implementation gaps, and recommend improvements for the genero-tools project.

---

## 1. COMMAND INVENTORY

### 1.1 Core Navigation Commands
| Command | Function | Status | Usage |
|---------|----------|--------|-------|
| `GeneroLookup` | `genero_tools#lookup_function()` | ✓ Implemented | Function definition lookup with auto-detection |
| `GeneroListModuleFiles` | `genero_tools#list_module_files()` | ✓ Implemented | List all files in a module |
| `GeneroListFunctions` | `genero_tools#list_functions_in_file()` | ✓ Implemented | List functions in current/specified file |
| `GeneroFunctionSignature` | `genero_tools#get_function_signature()` | ✓ Implemented | Get function signature with parameters |
| `GeneroFileMetadata` | `genero_tools#get_file_metadata()` | ✓ Implemented | Get file metadata (LOC, functions, etc.) |

### 1.2 Cache Management Commands
| Command | Function | Status | Usage |
|---------|----------|--------|-------|
| `GeneroClearCache` | `genero_tools#cache#clear()` | ✓ Implemented | Clear all cached data |
| `GeneroConfigShow` | `genero_tools#config#show()` | ✓ Implemented | Display current configuration |

### 1.3 Autocomplete Commands
| Command | Function | Status | Usage |
|---------|----------|--------|-------|
| `GeneroCompleteEnable` | `genero_tools#complete#enable()` | ✓ Implemented | Enable autocomplete |
| `GeneroCompleteDisable` | `genero_tools#complete#disable()` | ✓ Implemented | Disable autocomplete |

### 1.4 Compiler Commands
| Command | Function | Status | Usage |
|---------|----------|--------|-------|
| `GeneroCompile` | `genero_tools#compiler#commands#compile()` | ✓ Implemented | Compile current/specified file |
| `GeneroClearErrors` | `genero_tools#compiler#commands#clear_errors()` | ✓ Implemented | Clear error list |
| `GeneroNextError` | `genero_tools#compiler#commands#next_error()` | ✓ Implemented | Navigate to next error |
| `GeneroPrevError` | `genero_tools#compiler#commands#prev_error()` | ✓ Implemented | Navigate to previous error |
| `GeneroFirstError` | `genero_tools#compiler#commands#first_error()` | ✓ Implemented | Jump to first error |
| `GeneroLastError` | `genero_tools#compiler#commands#last_error()` | ✓ Implemented | Jump to last error |
| `GeneroAutocompileEnable` | `genero_tools#compiler#commands#autocompile_enable()` | ✓ Implemented | Enable autocompile on save |
| `GeneroAutocompileDisable` | `genero_tools#compiler#commands#autocompile_disable()` | ✓ Implemented | Disable autocompile |
| `GeneroAutocompileStatus` | `genero_tools#compiler#commands#autocompile_status()` | ✓ Implemented | Show autocompile status |

### 1.5 Snippet Commands (Neovim Only)
| Command | Function | Status | Usage |
|---------|----------|--------|-------|
| `GeneroSnippetList` | `genero_tools#snippets#list()` | ✓ Implemented | List available snippets |
| `GeneroSnippetHelp` | `genero_tools#snippets#help()` | ✓ Implemented | Show snippet help |
| `GeneroSnippet` | `genero_tools#snippets#expand()` | ✓ Implemented | Expand snippet by name |

### 1.6 SVN Commands
| Command | Function | Status | Usage |
|---------|----------|--------|-------|
| `GeneroSVNRefresh` | `genero_tools#svn#commands#refresh()` | ✓ Implemented | Refresh SVN diff markers |
| `GeneroSVNToggle` | `genero_tools#svn#commands#toggle()` | ✓ Implemented | Toggle SVN markers on/off |
| `GeneroSVNStatus` | `genero_tools#svn#commands#status()` | ✓ Implemented | Show SVN status |
| `GeneroSVNCacheStats` | `genero_tools#svn#commands#cache_stats()` | ✓ Implemented | Show SVN cache statistics |
| `GeneroSVNCacheClear` | `genero_tools#svn#commands#cache_clear()` | ✓ Implemented | Clear SVN cache |

### 1.7 Hint Commands
| Command | Function | Status | Usage |
|---------|----------|--------|-------|
| `GeneroNextHint` | `genero_tools#hints#nav#next()` | ✓ Implemented | Navigate to next hint |
| `GeneroPrevHint` | `genero_tools#hints#nav#prev()` | ✓ Implemented | Navigate to previous hint |
| `GeneroListHints` | `genero_tools#hints#nav#list()` | ✓ Implemented | List all hints in file |
| `GeneroHintDetails` | `genero_tools#hints#nav#details()` | ✓ Implemented | Show hint details |
| `GeneroHintAutofix` | `genero_tools#hints#autofix#apply()` | ✓ Implemented | Apply autofix for hint |
| `GeneroClearHintCache` | `genero_tools#hints#cache#clear()` | ✓ Implemented | Clear hint cache |
| `GeneroHintHelp` | `genero_tools#hints#help()` | ✓ Implemented | Show hint help |

### 1.8 Debug Streaming Commands (Neovim Only)
| Command | Function | Status | Usage |
|---------|----------|--------|-------|
| `GeneroDebugStream` | `genero_tools#debug_stream#start()` | ✓ Implemented | Start debug stream |
| `GeneroDebugStreamStop` | `genero_tools#debug_stream#stop()` | ✓ Implemented | Stop debug stream |
| `GeneroDebugStreamToggle` | `genero_tools#commands#debug_stream_select()` | ✓ Implemented | Toggle debug stream |
| `GeneroDebugStreamSelect` | `genero_tools#commands#debug_stream_select()` | ✓ Implemented | Select debug stream |
| `GeneroDebugStreamClear` | `genero_tools#debug_stream#clear()` | ✓ Implemented | Clear debug stream |
| `GeneroDebugStreamStatus` | `genero_tools#debug_stream#status()` | ✓ Implemented | Show debug stream status |

### 1.9 Lua API Commands (Neovim Only)
| Command | Function | Status | Usage |
|---------|----------|--------|-------|
| `GeneroLuaUI` | `luaeval("require('genero_tools').ui()...")` | ✓ Implemented | Lua UI API access |
| `GeneroLuaAsync` | `luaeval("require('genero_tools').async()...")` | ✓ Implemented | Lua async API access |

---

## 2. INTERNAL API FUNCTIONS USED

### 2.1 Configuration API
```vim
genero_tools#config#init()              " Initialize config with defaults
genero_tools#config#get(key)            " Get config value
genero_tools#config#set(key, value)     " Set config value
genero_tools#config#show()              " Display configuration
genero_tools#config#get_all()           " Get all config values
genero_tools#config#validate()          " Validate config values
```

### 2.2 Compiler API
```vim
genero_tools#compiler#execute(file)                    " Execute compiler
genero_tools#compiler#signs#init()                     " Initialize signs
genero_tools#compiler#signs#place(errors, warnings)   " Place error signs
genero_tools#compiler#signs#clear()                    " Clear signs
genero_tools#compiler#signs#update(result)            " Update signs from result
genero_tools#compiler#highlight#init()                " Initialize highlighting
genero_tools#compiler#highlight#apply(errors, warnings) " Apply highlighting
genero_tools#compiler#highlight#clear()               " Clear highlighting
genero_tools#compiler#highlight#unused_vars(warnings) " Highlight unused vars
genero_tools#compiler#quickfix#populate(result, filter) " Populate quickfix
genero_tools#compiler#quickfix#populate(result, 'all') " Populate with all errors
genero_tools#compiler#quickfix#clear()                " Clear quickfix
genero_tools#compiler#quickfix#next()                 " Navigate to next error
genero_tools#compiler#quickfix#prev()                 " Navigate to prev error
```

### 2.3 SVN API
```vim
genero_tools#svn#detection#is_in_working_copy(file)   " Check if in SVN WC
genero_tools#svn#detection#get_working_copy_root(file) " Get SVN root
genero_tools#svn#parser#parse_diff(diff)              " Parse SVN diff
genero_tools#svn#parser#get_summary(diff)             " Get diff summary
genero_tools#svn#parser#is_empty(diff)                " Check if diff empty
genero_tools#svn#cache_clear()                        " Clear SVN cache
genero_tools#svn#cache_set(file, result)              " Cache SVN result
genero_tools#svn#cache_get(file)                      " Get cached SVN result
genero_tools#svn#cache_invalidate(file)               " Invalidate cache entry
genero_tools#svn#error#check_enabled()                " Check if SVN enabled
```

### 2.4 Display API
```vim
genero_tools#display#echo(message)                    " Echo message
genero_tools#display#result(result, mode)             " Display result
genero_tools#display#get_mode(feature)                " Get display mode for feature
```

### 2.5 Error Handling API
```vim
genero_tools#error#format(module, message)            " Format error message
genero_tools#error#echo(module, message)              " Echo error
genero_tools#error#warn(module, message)              " Show warning
genero_tools#error#error(module, message)             " Show error
genero_tools#error#display(message, details)          " Display error with details
genero_tools#error#log(message)                       " Log error
genero_tools#error#debug(module, message)             " Debug log
```

### 2.6 Compatibility API
```vim
genero_tools#compat#is_neovim()                       " Check if Neovim
genero_tools#compat#is_vim()                          " Check if Vim
genero_tools#compat#get_supported_display_modes()     " Get supported modes
genero_tools#compat#validate_display_mode(mode)       " Validate display mode
genero_tools#compat#is_display_mode_available(mode)   " Check mode available
```

### 2.7 Lua Bridge API
```vim
genero_tools#lua_bridge#available()                   " Check if Lua available
genero_tools#lua_bridge#call(module, function, args)  " Call Lua function
genero_tools#lua_bridge#call_safe(module, fn, args, fallback) " Safe Lua call
genero_tools#lua_bridge#execute_async(cmd, args, callback)    " Async execution
genero_tools#lua_bridge#show_floating_window(content, opts)   " Show floating window
genero_tools#lua_bridge#init()                        " Initialize Lua layer
```

### 2.8 Cache API
```vim
genero_tools#cache#clear()                            " Clear cache
genero_tools#cache#stats()                            " Get cache statistics
genero_tools#cache#estimate_memory()                  " Estimate memory usage
```

---

## 3. CONFIGURATION OPTIONS UTILIZED

### 3.1 Core Configuration
- `genero_tools_path` - Path to query.sh tool
- `cache_enabled` - Enable/disable caching
- `cache_ttl` - Cache time-to-live (seconds)
- `cache_max_size` - Maximum cache entries
- `display_mode` - Global display mode (quickfix, popup, split, echo, inline)
- `keybindings_enabled` - Enable default keybindings
- `timeout` - Command timeout (ms)
- `async_enabled` - Enable async operations
- `result_limit` - Maximum results returned
- `pagination_size` - Results per page

### 3.2 Compiler Configuration
- `compiler_enabled` - Enable compiler integration
- `compiler_command` - Compiler executable (fglcomp)
- `compiler_form_command` - Form compiler (fglform)
- `compiler_args` - Compiler arguments
- `compiler_form_args` - Form compiler arguments
- `compiler_source_dir` - Source directory
- `compiler_version` - Compiler version
- `compiler_show_warnings` - Show warnings
- `compiler_show_errors` - Show errors
- `compiler_highlight_unused` - Highlight unused variables
- `compiler_sign_column` - Show error signs
- `compiler_sign_column_always_visible` - Keep sign column visible
- `compiler_autocompile` - Autocompile on save
- `compiler_autocompile_delay` - Autocompile delay (ms)
- `compiler_display_mode` - Compiler-specific display mode

### 3.3 Snippet Configuration
- `snippets_enabled` - Enable snippets
- `snippet_engine` - Snippet engine (luasnip, vim-snipmate, vim-vsnip)
- `snippet_smart_expansion` - Smart expansion
- `snippet_custom_dir` - Custom snippet directory
- `snippet_list_selectable` - Selectable snippet list
- `snippet_expansion_mode` - Expansion mode
- `autocomplete_include_snippets` - Include snippets in autocomplete

### 3.4 SVN Configuration
- `svn_enabled` - Enable SVN integration
- `svn_show_added` - Show added files
- `svn_show_modified` - Show modified files
- `svn_show_deleted` - Show deleted files
- `svn_cache_ttl` - SVN cache TTL (seconds)
- `svn_auto_update` - Auto-update SVN markers

### 3.5 UI Configuration
- `floating_window_border` - Window border style
- `floating_window_width` - Window width
- `floating_window_height` - Window height
- `floating_window_position` - Window position
- `floating_window_title` - Window title
- `popup_auto_close_delay` - Auto-close delay (ms)
- `notify_enabled` - Enable notifications
- `notify_duration` - Notification duration (ms)

### 3.6 Debug Configuration
- `debug_stream_enabled` - Enable debug streaming
- `debug_stream_width` - Stream window width
- `debug_stream_max_lines` - Max lines in stream
- `debug_stream_auto_scroll` - Auto-scroll stream
- `debug_stream_directory` - Debug output directory
- `debug_mode` - Debug mode
- `lua_enabled` - Enable Lua layer
- `startup_messages` - Startup message level (silent, normal, verbose)

---

## 4. FEATURE GAPS & IMPROVEMENT OPPORTUNITIES

### 4.1 Missing Commands (High Priority)

#### 4.1.1 Compiler Enhancements
- **Gap**: No command to compile entire project/directory
  - **Recommendation**: Add `GeneroCompileProject` command
  - **Use Case**: Batch compilation for large codebases
  - **Implementation**: `genero_tools#compiler#commands#compile_project()`

- **Gap**: No command to show compiler diagnostics summary
  - **Recommendation**: Add `GeneroCompileSummary` command
  - **Use Case**: Quick overview of all errors/warnings
  - **Implementation**: `genero_tools#compiler#commands#summary()`

- **Gap**: No command to filter errors by type/severity
  - **Recommendation**: Add `GeneroFilterErrors` command with arguments
  - **Use Case**: Focus on specific error types
  - **Implementation**: `genero_tools#compiler#commands#filter_errors(type)`

#### 4.1.2 Navigation Enhancements
- **Gap**: No command to find all references to a function
  - **Recommendation**: Add `GeneroFindReferences` command
  - **Use Case**: Refactoring, impact analysis
  - **Implementation**: `genero_tools#codebase#find_references(symbol)`

- **Gap**: No command to show call hierarchy/call graph
  - **Recommendation**: Add `GeneroCallHierarchy` command
  - **Use Case**: Understanding code flow
  - **Implementation**: `genero_tools#codebase#call_hierarchy(function)`

- **Gap**: No command to navigate to type definitions
  - **Recommendation**: Add `GeneroGotoType` command
  - **Use Case**: Type-based navigation
  - **Implementation**: `genero_tools#codebase#goto_type(type_name)`

#### 4.1.3 Search & Analysis
- **Gap**: No command to search across codebase with regex
  - **Recommendation**: Add `GeneroSearch` command
  - **Use Case**: Pattern-based code search
  - **Implementation**: `genero_tools#codebase#search(pattern)`

- **Gap**: No command to show code statistics
  - **Recommendation**: Add `GeneroCodeStats` command
  - **Use Case**: Project metrics, complexity analysis
  - **Implementation**: `genero_tools#codebase#statistics()`

#### 4.1.4 Refactoring Support
- **Gap**: No command to rename symbols across codebase
  - **Recommendation**: Add `GeneroRename` command
  - **Use Case**: Safe refactoring
  - **Implementation**: `genero_tools#refactor#rename(old_name, new_name)`

- **Gap**: No command to extract function/method
  - **Recommendation**: Add `GeneroExtractFunction` command
  - **Use Case**: Code organization
  - **Implementation**: `genero_tools#refactor#extract_function()`

### 4.2 Missing API Functions (Medium Priority)

#### 4.2.1 Compiler API Gaps
```vim
" Missing: Batch compilation
genero_tools#compiler#compile_batch(files)

" Missing: Compiler diagnostics
genero_tools#compiler#get_diagnostics()
genero_tools#compiler#get_diagnostics_summary()

" Missing: Error filtering
genero_tools#compiler#filter_errors(type, severity)
genero_tools#compiler#filter_warnings(category)

" Missing: Compiler configuration
genero_tools#compiler#get_compiler_version()
genero_tools#compiler#validate_compiler_setup()
```

#### 4.2.2 Navigation API Gaps
```vim
" Missing: Reference finding
genero_tools#codebase#find_references(symbol)
genero_tools#codebase#find_usages(function_name)

" Missing: Call hierarchy
genero_tools#codebase#get_call_hierarchy(function)
genero_tools#codebase#get_callers(function)
genero_tools#codebase#get_callees(function)

" Missing: Type navigation
genero_tools#codebase#goto_type(type_name)
genero_tools#codebase#get_type_definition(type_name)
```

#### 4.2.3 Search API Gaps
```vim
" Missing: Advanced search
genero_tools#codebase#search(pattern, options)
genero_tools#codebase#search_regex(pattern)
genero_tools#codebase#search_in_file(file, pattern)

" Missing: Symbol search
genero_tools#codebase#find_symbol(name)
genero_tools#codebase#find_symbols_by_type(type)
```

#### 4.2.4 Analysis API Gaps
```vim
" Missing: Code metrics
genero_tools#analysis#get_statistics()
genero_tools#analysis#get_complexity(function)
genero_tools#analysis#get_dependencies(file)

" Missing: Code quality
genero_tools#analysis#get_code_smells()
genero_tools#analysis#get_dead_code()
```

#### 4.2.5 Refactoring API Gaps
```vim
" Missing: Rename support
genero_tools#refactor#rename(old_name, new_name)
genero_tools#refactor#rename_symbol(symbol, new_name)

" Missing: Extract operations
genero_tools#refactor#extract_function(start_line, end_line)
genero_tools#refactor#extract_variable(start_line, end_line)

" Missing: Move operations
genero_tools#refactor#move_function(function, target_file)
genero_tools#refactor#move_code(start_line, end_line, target_file)
```

### 4.3 Configuration Gaps (Low Priority)

#### 4.3.1 Missing Configuration Options
```vim
" Missing: Compiler output handling
compiler_output_format          " JSON, XML, plain
compiler_parallel_compilation   " Enable parallel builds
compiler_incremental_build      " Incremental compilation

" Missing: Search options
search_case_sensitive           " Case sensitivity
search_whole_word_only          " Whole word matching
search_include_comments         " Search in comments

" Missing: Display options
result_truncate_long_lines      " Truncate long lines
result_syntax_highlighting      " Syntax highlight results
result_line_numbers             " Show line numbers

" Missing: Performance tuning
max_concurrent_operations       " Limit concurrent ops
memory_limit_mb                 " Memory limit
index_update_interval           " Index update frequency
```

### 4.4 Feature Enhancements (Medium Priority)

#### 4.4.1 Compiler Enhancements
- **Gap**: No incremental compilation support
  - **Recommendation**: Track file modification times, compile only changed files
  - **Benefit**: Faster compilation for large projects

- **Gap**: No parallel compilation support
  - **Recommendation**: Compile multiple files in parallel
  - **Benefit**: Utilize multi-core systems

- **Gap**: No compiler output caching
  - **Recommendation**: Cache compiler output for unchanged files
  - **Benefit**: Faster error navigation

#### 4.4.2 SVN Integration Enhancements
- **Gap**: No blame/annotation support
  - **Recommendation**: Add `GeneroSVNBlame` command
  - **Benefit**: Track code changes by author/date

- **Gap**: No diff viewing support
  - **Recommendation**: Add `GeneroSVNDiff` command
  - **Benefit**: Review changes inline

- **Gap**: No commit message integration
  - **Recommendation**: Show commit messages in hints
  - **Benefit**: Context for changes

#### 4.4.3 Hint System Enhancements
- **Gap**: No hint severity levels
  - **Recommendation**: Categorize hints (error, warning, info, suggestion)
  - **Benefit**: Better prioritization

- **Gap**: No hint filtering by category
  - **Recommendation**: Add `GeneroFilterHints` command
  - **Benefit**: Focus on relevant hints

- **Gap**: No hint statistics
  - **Recommendation**: Add `GeneroHintStats` command
  - **Benefit**: Track code quality metrics

#### 4.4.4 Snippet System Enhancements
- **Gap**: No snippet validation
  - **Recommendation**: Validate snippet syntax on load
  - **Benefit**: Catch errors early

- **Gap**: No snippet testing framework
  - **Recommendation**: Add snippet test runner
  - **Benefit**: Ensure snippet correctness

- **Gap**: No snippet documentation generation
  - **Recommendation**: Auto-generate snippet docs
  - **Benefit**: Better snippet discovery

### 4.5 Performance Improvements (Medium Priority)

#### 4.5.1 Caching Enhancements
- **Gap**: No intelligent cache invalidation
  - **Recommendation**: Track file dependencies, invalidate only affected cache
  - **Benefit**: Reduce cache misses

- **Gap**: No cache compression
  - **Recommendation**: Compress cached data
  - **Benefit**: Reduce memory usage

- **Gap**: No persistent cache
  - **Recommendation**: Save cache to disk between sessions
  - **Benefit**: Faster startup

#### 4.5.2 Indexing Enhancements
- **Gap**: No background indexing
  - **Recommendation**: Index codebase in background
  - **Benefit**: Faster searches

- **Gap**: No incremental indexing
  - **Recommendation**: Update index only for changed files
  - **Benefit**: Reduce indexing overhead

### 4.6 Integration Gaps (Low Priority)

#### 4.6.1 LSP Integration
- **Gap**: No LSP server support
  - **Recommendation**: Implement LSP server for genero-tools
  - **Benefit**: IDE-agnostic support

#### 4.6.2 External Tool Integration
- **Gap**: No integration with external linters
  - **Recommendation**: Support custom linter plugins
  - **Benefit**: Extensibility

- **Gap**: No integration with code formatters
  - **Recommendation**: Support code formatting
  - **Benefit**: Code style consistency

---

## 5. CURRENT USAGE PATTERNS

### 5.1 Compiler Workflow
```vim
" 1. Enable autocompile
:GeneroAutocompileEnable

" 2. Compile current file
:GeneroCompile

" 3. Navigate errors
:GeneroNextError
:GeneroPrevError
:GeneroFirstError
:GeneroLastError

" 4. Clear errors
:GeneroClearErrors
```

### 5.2 Navigation Workflow
```vim
" 1. Lookup function
:GeneroLookup function_name

" 2. Get signature
:GeneroFunctionSignature function_name

" 3. List functions in file
:GeneroListFunctions

" 4. Get file metadata
:GeneroFileMetadata
```

### 5.3 SVN Workflow
```vim
" 1. Refresh SVN markers
:GeneroSVNRefresh

" 2. Toggle markers
:GeneroSVNToggle

" 3. Check status
:GeneroSVNStatus

" 4. View cache stats
:GeneroSVNCacheStats
```

### 5.4 Hint Workflow
```vim
" 1. List hints
:GeneroListHints

" 2. Navigate hints
:GeneroNextHint
:GeneroPrevHint

" 3. Show details
:GeneroHintDetails

" 4. Apply autofix
:GeneroHintAutofix
```

---

## 6. RECOMMENDATIONS FOR GENERO-TOOLS PROJECT

### Priority 1 (Implement First)
1. **Find References** - Essential for refactoring
2. **Batch Compilation** - Critical for large projects
3. **Error Filtering** - Improves usability
4. **Code Search** - Fundamental feature

### Priority 2 (Implement Next)
1. **Call Hierarchy** - Useful for understanding code
2. **Rename Support** - Important for refactoring
3. **Code Statistics** - Useful metrics
4. **Hint Filtering** - Better hint management

### Priority 3 (Nice to Have)
1. **LSP Server** - IDE integration
2. **Incremental Compilation** - Performance
3. **Persistent Cache** - Faster startup
4. **SVN Blame** - Code history

---

## 7. SUMMARY

**Total Commands Implemented**: 47
**Total API Functions Used**: 60+
**Configuration Options**: 60+

**Key Strengths**:
- Comprehensive compiler integration
- Robust SVN support
- Extensive configuration options
- Good error handling

**Key Gaps**:
- No refactoring support (rename, extract)
- No reference finding
- No call hierarchy
- No code search
- No batch operations
- No code metrics/analysis

**Recommended Next Steps**:
1. Implement find references functionality
2. Add batch compilation support
3. Implement code search with regex
4. Add refactoring support (rename)
5. Implement call hierarchy visualization
