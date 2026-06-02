# genero-tools Improvement Tasklist

## High Priority

- [x] 1. **Wire metrics into pipeline** — Integrate `metrics_extractor.py` into `generate_all.sh` so `function_metrics` table is populated in workspace.db automatically. Quality analyzer works without fallback paths.
- [x] 2. **Incremental signature generation** — Track file content hashes in `.genero-manifest.json`; re-process only changed `.4gl` files and merge into existing workspace.json. Full rebuild when no manifest exists or `FORCE_FULL=1`. Disable with `INCREMENTAL=0`.
- [ ] 3. **Cross-file call resolution** — Resolve called function names to their actual `function_id` in the DB. Enrich `calls` table with `resolved_function_id` to enable true file-to-file dependency graphs and reliable dead code detection.
- [ ] 4. **Reverse schema impact query** — Add `find-functions-using-column <table> <column>` query to answer "which functions are affected if I change this schema column?" Essential for schema migration planning.

## Medium Priority

- [ ] 5. **Packaged Neovim plugin** — Ship a minimal `genero.nvim` plugin (lua/ directory + plugin/ entry point) using the existing `--format=vim-*` output options. Cover: hover, go-to-definition, find-references, completion.
- [ ] 6. **Function body storage** — Store full function body text (or hash) in the DB to enable real duplication detection, body diffing between runs, and AI code review with full context.
- [ ] 7. **GLOBALS/IMPORT dependency linking** — Connect `modulars.json` data (GLOBALS file refs, IMPORT statements) into the query layer so you can answer "what files does this file depend on?" and "what files depend on this globals file?"
- [ ] 8. **Complexity trend tracking** — Store historical metrics snapshots (date + function + metrics) to track codebase complexity over time. Useful for tech debt visibility.

## Lower Priority

- [ ] 9. **Watch mode** — Add `--watch` flag to `generate_all.sh` using `inotifywait` to re-process files on save. Depends on incremental generation (#2).
- [ ] 10. **Multi-schema support** — Support a schema directory or multiple `.sch` files for type resolution instead of a single file.
- [ ] 11. **Procedure vs Function distinction** — Track whether a definition is a FUNCTION (has RETURN values) vs a procedure/MAIN/REPORT for better type accuracy.
- [ ] 12. **Standard format exports** — Generate DOT/Graphviz (call graphs), SARIF (quality issues), or LSIF/SCIP (editor integration) from the existing data.

## Completed (Previous Sprint)

- [x] RETURN expression resolution
- [x] Multi-variable DEFINE handling
- [x] Multi-line RECORD field tracking
- [x] First RETURN capture (not last)
- [x] RETURN without space pattern
- [x] Function calls in RETURN expressions
- [x] Comment-safe parameter accumulation
- [x] Schema-qualified LIKE references
- [x] Case-insensitive column lookup
- [x] Schema load failure reporting
- [x] Path normalization in merge
- [x] Case-insensitive parameter name match
- [x] Error suppression removal
- [x] Subshell variable loss detection
- [x] RESOLVE_TYPES flag fallback
- [x] Duplicate header extraction fix
- [x] Inline RECORD type preservation
- [x] DYNAMIC ARRAY OF RECORD preservation
