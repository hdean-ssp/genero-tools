# Genero-Tools API Gaps - Executive Summary

## 9 Critical Enhancements Needed

### 🔴 Phase 1: Critical (Implement First)

| Gap | Problem | Solution | Impact |
|-----|---------|----------|--------|
| **Batch Queries** | Each lookup = separate CLI call | `query.sh batch-query` | 10x faster, parallel ops |
| **Pagination** | All results at once, memory issues | Add `--limit` `--offset` | Handle 6M+ LOC codebases |
| **Relationship Queries** | Can't ask "find callers in module" | `find-dependents-in-module`, `find-call-chain` | Advanced navigation |
| **Metrics** | No complexity/coupling data | `function-metrics`, `find-complex-functions` | Code quality analysis |
| **Error Handling** | Limited error information | `validate-database`, `get-error-details` | Better diagnostics |

### 🟡 Phase 2: Important

| Gap | Solution | Benefit |
|-----|----------|---------|
| **Advanced Search** | Multi-criteria filtering | Powerful search |
| **Diff Detection** | `diff-functions`, `diff-file` | Version tracking (SVN handled separately) |
| **Export/Reports** | `export-call-graph`, `generate-report` | Visualization |
| **Cache Invalidation** | `get-cache-info`, `invalidate-cache` | Smart caching |

## Why These Matter

### Current State
- ✅ Good for simple lookups
- ❌ Poor for IDE-like features
- ❌ Slow for large codebases (no batch ops)
- ❌ Memory issues (no pagination)
- ❌ Limited context (no history/changes)

### With Enhancements
- ✅ Full IDE backend
- ✅ Fast operations (batch queries)
- ✅ Handles large codebases (pagination)
- ✅ Rich context (history, changes, metrics)
- ✅ Code quality analysis

## Recommended Priority

1. **Batch Queries** - Biggest performance impact
2. **Pagination** - Handles large codebases
3. **Relationship Queries** - Advanced navigation
4. **Metrics** - Code quality features

## Questions for Genero-Tools Team

1. Can query.sh support batch operations?
2. Can queries support pagination (limit/offset)?
3. Can workspace.db store metrics (complexity, coupling)?
4. Can query.sh provide cache invalidation hints?
5. What's typical query time for 6M+ LOC?

## See Also

- Full analysis: `GENERO_TOOLS_API_ENHANCEMENT_SUGGESTIONS.md`
- Current API: `docs/API_INTEGRATION.md`
- Shell commands: `genero-tools-api/api/shell-commands.json`
