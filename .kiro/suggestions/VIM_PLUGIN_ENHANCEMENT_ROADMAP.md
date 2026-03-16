# Vim Plugin Enhancement Roadmap

How genero-tools API enhancements enable new vim-genero-tools features.

## Current Capabilities (Today)

```vim
:GeneroLookup myFunction           " Find function definition
:GeneroListFunctions %             " List functions in file
:GeneroFunctionSignature myFunc    " Get function signature
:GeneroFileMetadata %              " Get file metadata
:GeneroCompile                     " Compile file
```

**Limitations:**
- Single query per command
- All results at once (memory issues)
- No code quality metrics
- Slow on large codebases

---

## Phase 1: Performance & Scale (With Batch Queries + Pagination)

### New Commands

```vim
" Hover information (fetch definition + dependencies + dependents in one call)
:GeneroHover                       " Show rich hover info

" Smart search with pagination
:GeneroSearch pattern              " Search with pagination
<C-n>                              " Next page
<C-p>                              " Previous page

" Async operations (non-blocking)
:GeneroLookupAsync myFunction      " Async lookup
```

### Benefits
- ✅ 10x faster (batch queries)
- ✅ Handles 6M+ LOC codebases (pagination)
- ✅ Non-blocking operations (async)
- ✅ Progressive UI updates

---

## Phase 2: Advanced Navigation (With Relationship Queries)

### New Commands

```vim
" Advanced navigation
:GeneroFindCallers myFunc          " Find all functions that call this
:GeneroFindCallersInModule myFunc  " Find callers in current module
:GeneroCallChain from to           " Show call path between functions
:GeneroCommonCallers func1 func2   " Find functions calling both

" Show in sign column
:GeneroShowCallers                 " Highlight functions that call this
```

### Benefits
- ✅ Advanced navigation
- ✅ Visual indicators
- ✅ Better understanding of code

---

## Phase 3: Code Quality (With Metrics Queries)

### New Commands

```vim
" Show code metrics
:GeneroFunctionMetrics myFunc      " Show complexity, LOC, parameters, etc.
:GeneroModuleMetrics core          " Show module statistics

" Find problematic code
:GeneroFindComplex [threshold]     " Find complex functions
:GeneroFindHighCoupling            " Find functions with high coupling
:GeneroFindDeadCode                " Find unused functions

" Highlight in editor
:GeneroHighlightComplex            " Highlight complex functions
:GeneroHighlightCoupling           " Highlight high-coupling functions
```

### Benefits
- ✅ Code quality analysis
- ✅ Identify refactoring candidates
- ✅ Visual indicators
- ✅ Improve code health

---

## Phase 4: Advanced Search & Filtering (With Advanced Search)

### New Commands

```vim
" Advanced search
:GeneroAdvancedSearch              " Open search dialog
  --author John
  --reference 'PRB%'
  --complexity_min 10
  --module core

" Quick filters
:GeneroSearchByAuthor John         " Find files modified by John
:GeneroSearchByReference PRB-123   " Find files for reference
```

### Benefits
- ✅ Powerful filtering
- ✅ Find related code
- ✅ Understand code ownership

---

## Phase 5: Analysis & Reports (With Export/Reports)

### New Commands

```vim
" Generate reports
:GeneroGenerateReport quality      " Generate code quality report
:GeneroGenerateReport complexity   " Generate complexity report
:GeneroGenerateReport dependencies " Generate dependency report

" Export for visualization
:GeneroExportCallGraph             " Export as DOT for graphviz
:GeneroExportCallGraph --module    " Export module call graph
```

### Benefits
- ✅ Analysis tools
- ✅ Visualization
- ✅ Documentation
- ✅ Metrics tracking

---

## Complete Feature Matrix

| Feature | Current | Phase 1 | Phase 2 | Phase 3 | Phase 4 | Phase 5 |
|---------|---------|---------|---------|---------|---------|---------|
| Function lookup | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Module exploration | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Autocomplete | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Compiler integration | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Batch operations** | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Pagination** | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Hover info** | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Find callers** | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| **Call chains** | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| **Code metrics** | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| **Find complex** | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| **Advanced search** | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Reports** | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |

---

## Implementation Timeline

### Phase 1: Performance & Scale (1-2 weeks)
- Batch queries
- Pagination
- Async operations
- **Impact:** 10x faster, handles large codebases

### Phase 2: Advanced Navigation (2-3 weeks)
- Relationship queries
- Visual indicators
- **Impact:** Rich IDE features

### Phase 3: Code Quality (1-2 weeks)
- Metrics queries
- Quality analysis
- Highlighting
- **Impact:** Code quality features

### Phase 4: Advanced Search (1 week)
- Advanced search
- Filtering
- **Impact:** Powerful search

### Phase 5: Analysis & Reports (1-2 weeks)
- Export/reports
- Visualization
- **Impact:** Analysis tools

**Total: 6-10 weeks** to full IDE-like capabilities

---

## User Experience Evolution

### Today
```
User: :GeneroLookup myFunc
Plugin: Shows function definition
User: Manually searches for callers
```

### Phase 1
```
User: :GeneroLookup myFunc
Plugin: Shows definition + dependencies + dependents (fast!)
User: Navigates with pagination
```

### Phase 2
```
User: Hovers over function
Plugin: Shows definition + callers (rich hover)
User: Clicks to navigate to caller
```

### Phase 3
```
User: Opens file
Plugin: Highlights complex functions
User: Sees code quality metrics
```

### Phase 4
```
User: :GeneroSearch --author John --reference 'PRB%'
Plugin: Shows all files modified by John for PRB tickets
User: Filters by reference, module, complexity
```

### Phase 5
```
User: :GeneroGenerateReport quality
Plugin: Generates HTML report with metrics
User: Shares report with team
```

---

## Conclusion

The genero-tools API enhancements would transform vim-genero-tools from a simple lookup tool into a full IDE backend, enabling:

- ✅ **Performance:** 10x faster operations
- ✅ **Scale:** Handle 6M+ LOC codebases
- ✅ **Navigation:** Advanced code exploration
- ✅ **Quality:** Code quality analysis
- ✅ **Search:** Powerful filtering
- ✅ **Analysis:** Reports and visualization

This would position vim-genero-tools as a professional IDE for Genero development.

**Note:** Version control (SVN diff markers) is handled separately via SVN integration.
