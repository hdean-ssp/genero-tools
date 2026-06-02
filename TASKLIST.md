# genero-tools Improvement Tasklist

## Completed

- [x] 1. **Wire metrics into pipeline** — Integrate `metrics_extractor.py` into `generate_all.sh` so `function_metrics` table is populated in workspace.db automatically. Quality analyzer works without fallback paths.
- [x] 2. **Incremental signature generation** — Track file content hashes in `.genero-manifest.json`; re-process only changed `.4gl` files and merge into existing workspace.json. Full rebuild when no manifest exists or `FORCE_FULL=1`. Disable with `INCREMENTAL=0`.
- [x] 3. **Cross-file call resolution** — Resolve called function names to their actual `function_id` in the DB. Enrich `calls` table with `resolved_function_id` to enable true file-to-file dependency graphs and reliable dead code detection.
- [x] 4. **Reverse schema impact query** — Add `find-functions-using <table> [column]` query to answer "which functions are affected if I change this schema column?" Searches parameters, returns, and variables.

## Active

- [x] 5. **Function body hashing** — Store an MD5 hash of each function body to detect logic changes between runs (without storing full source). Also stores `body_loc` (line count) for size tracking.
- [x] 6. **GLOBALS/IMPORT dependency linking** — Connect `modulars.json` data (GLOBALS file refs, IMPORT statements) into the query layer. Query with `file-deps <file>` and `file-dependents <name>`.

## Backburner

- [ ] 7. **Watch mode** — `--watch` flag using `inotifywait` to re-process on save. Nice-to-have for future.
- [ ] 8. **Multi-schema support** — Support multiple `.sch` files for type resolution.

## Won't Do / Out of Scope

- ~~Packaged Neovim plugin~~ — Separate project: genero-vim
- ~~Complexity trend tracking~~ — Not needed at this stage
- ~~Procedure vs Function distinction~~ — Not needed
- ~~Standard format exports (DOT/SARIF/LSIF)~~ — JSON and SQLite are sufficient

## Completed (Previous Sprint - Parser Fixes)

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
