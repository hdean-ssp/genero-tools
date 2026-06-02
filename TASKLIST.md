# Generate Pipeline Fix Tasklist

## AWK Parser (src/generate_signatures.sh)

- [x] 1. **RETURN expression resolution** — Resolve base variables from expressions (`l_rec.field` → lookup `l_rec`), recognize literals (`TRUE`/`FALSE` → BOOLEAN, `0`/`1` → INTEGER), handle function calls and operators as expression types.
- [x] 2. **Multi-variable DEFINE** — Handle `DEFINE a, b, c INTEGER` by splitting on commas and assigning the trailing type to all listed variables.
- [x] 3. **Multi-line RECORD field tracking** — Accumulate fields between RECORD/END RECORD so `l_rec.field` return lookups can resolve to the field's actual type.
- [x] 4. **Last RETURN overwrites previous** — Capture the first RETURN (or the one with the most values) instead of always overwriting with the last.
- [x] 5. **RETURN without space** — Add pattern to match `RETURN(value)` in addition to `RETURN value`.
- [x] 6. **`next` prevents multi-match lines** — Extract function calls from RETURN expressions before `next`, so calls in RETURN statements are captured in the call graph.
- [x] 7. **Premature multi-line param stop** — Strip comment lines and inline comments during parameter accumulation to avoid `)` in comments stopping accumulation.

## Type Resolution (scripts/resolve_types.py)

- [x] 8. **Schema-qualified LIKE references** — Extend regex to handle `LIKE schema:table.column` and `LIKE formonly.field`.
- [x] 9. **Case-insensitive column lookup** — Use case-insensitive comparison for both table and column name matching.
- [x] 10. **Silent schema load failure** — Exit with error when schema_tables is missing, rather than silently continuing with all resolutions failing.

## Merge (scripts/merge_resolved_types.py)

- [x] 11. **Path normalization** — Normalize file paths before lookup; try multiple path variants (`./path`, `path`, normalized) to handle inconsistencies.
- [x] 12. **Case-insensitive parameter name match** — Use `COLLATE NOCASE` for parameter and return name lookups in UPDATE queries.

## Pipeline (generate_all.sh)

- [x] 13. **Remove error suppression** — Replace `2>/dev/null` with logging to temp files; display error details on failure.
- [x] 14. **Subshell variable loss** — Warn when header extraction produces no output despite files being present; reuse temp files across steps.
- [x] 15. **RESOLVE_TYPES flag dependency** — Add explicit error message and manual retry command when schema parse succeeds but DB load fails.
- [x] 16. **Duplicate header extraction** — Reuse headers temp file from Step 1b in Step 3 instead of re-extracting.

## Data Quality

- [x] 17. **Inline RECORD type preservation** — Output `record_types` field in JSON with field-level type mappings for all inline RECORD definitions.
- [x] 18. **DYNAMIC ARRAY OF RECORD preservation** — Same treatment: field definitions captured and output in `record_types` for DYNAMIC ARRAY OF RECORD and ARRAY[n] OF RECORD.
