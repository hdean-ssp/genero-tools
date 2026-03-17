#!/bin/bash
# Convenient wrapper for querying the codebase databases

set -euo pipefail

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Get the parent directory (project root)
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Default database files - look in current directory first, then project root
if [[ -f "workspace.db" ]]; then
    SIGNATURES_DB="${SIGNATURES_DB:-workspace.db}"
else
    SIGNATURES_DB="${SIGNATURES_DB:-$PROJECT_ROOT/workspace.db}"
fi

if [[ -f "modules.db" ]]; then
    MODULES_DB="${MODULES_DB:-modules.db}"
else
    MODULES_DB="${MODULES_DB:-$PROJECT_ROOT/modules.db}"
fi

# Show usage
usage() {
    cat << 'EOF'
Usage: query.sh <command> [args...]

Signature queries (workspace.db):
  find-function <name>                Find function by exact name
  find-function-resolved <name>       Find function with resolved LIKE types
  search-functions <pattern>          Search functions by name pattern
  list-file-functions <path>          List all functions in a file
  find-function-dependencies <name>   Find all functions called by a function
  find-function-dependents <name>     Find all functions that call a function
  find-dead-code                      Find functions that are never called

Module queries (modules.db):
  find-module <name>                  Find module by exact name
  search-modules <pattern>            Search modules by name pattern
  list-file-modules <filename>        Find modules using a file

Module-scoped queries (both databases):
  find-functions-in-module <name>     Find all functions in a module
  find-module-for-function <name>     Find which module(s) contain a function
  find-functions-calling-in-module <module> <func>  Find functions in module that call a function
  find-module-dependencies <name>     Find modules that a module depends on

Header/Reference queries (workspace.db):
  find-reference <ref>                Find files modified for a code reference
  find-author <author>                Find files modified by an author
  file-references <path>              Get all references for a file
  file-authors <path>                 Get all authors who modified a file
  author-expertise <author>           Show what areas an author has expertise in
  recent-changes [days]               Find files modified in last N days (default 30)
  search-references <pattern>         Search references by pattern (partial match)
  search-reference-prefix <prefix>    Search references by prefix (e.g., "EH100512" finds "EH100512-9a")

Type resolution queries:
  unresolved-types                    Find all unresolved LIKE type references
  unresolved-types --filter <type>    Filter by error type (missing_table, missing_column, invalid_pattern)
  unresolved-types --limit <n>        Limit results to N items
  unresolved-types --offset <n>       Skip first N items (for pagination)
  validate-types                      Validate type resolution data consistency

Batch queries:
  batch-query <json_file>             Execute multiple queries in a single batch
  batch-query --input <json_file> --output <output_file>  Execute batch with output file

Database management:
  create-dbs                          Create both databases from JSON files
  create-signatures-db                Create workspace.db from workspace.json
  create-modules-db                   Create modules.db from modules.json

Examples:
  query.sh find-function my_function
  query.sh search-functions "get_*"
  query.sh find-function-dependencies my_function
  query.sh find-functions-in-module core
  query.sh find-module-for-function my_function
  query.sh find-functions-calling-in-module core validate_input
  query.sh find-module-dependencies core
  query.sh find-reference PRB-299
  query.sh find-author "John Smith"
  query.sh file-references "./src/utils.4gl"
  query.sh author-expertise "John Smith"
  query.sh recent-changes 7
  query.sh unresolved-types
  query.sh unresolved-types --filter missing_table
  query.sh unresolved-types --limit 10 --offset 5
  query.sh batch-query queries.json
  query.sh batch-query --input queries.json --output results.json
EOF
}

# Create databases
create_dbs() {
    echo "Creating databases..."
    
    # Use current directory if files exist there, otherwise use project root
    WS_JSON="${WS_JSON:-workspace.json}"
    MOD_JSON="${MOD_JSON:-modules.json}"
    
    if [[ ! -f "$WS_JSON" && -f "$PROJECT_ROOT/workspace.json" ]]; then
        WS_JSON="$PROJECT_ROOT/workspace.json"
    fi
    if [[ ! -f "$MOD_JSON" && -f "$PROJECT_ROOT/modules.json" ]]; then
        MOD_JSON="$PROJECT_ROOT/modules.json"
    fi
    
    python3 "$PROJECT_ROOT/scripts/json_to_sqlite.py" signatures "$WS_JSON" "$SIGNATURES_DB"
    python3 "$PROJECT_ROOT/scripts/json_to_sqlite.py" modules "$MOD_JSON" "$MODULES_DB"
    echo "Done. Databases created:"
    ls -lh "$SIGNATURES_DB" "$MODULES_DB"
}

# Format unresolved types as human-readable table with summary
format_unresolved_types() {
    python3 -c "
import json
import sys

try:
    data = json.loads(sys.stdin.read())
except json.JSONDecodeError:
    print('Error: Invalid JSON output from query')
    sys.exit(1)

if not data:
    print('No unresolved types found.')
    sys.exit(0)

# Calculate column widths
func_width = max(len('function'), max(len(r.get('function_name', '')) for r in data))
file_width = max(len('file'), max(len(r.get('file_path', '')) for r in data))
type_width = max(len('type_name'), max(len(r.get('type_name', '')) for r in data))
orig_width = max(len('original_type'), max(len(r.get('original_type', '')) for r in data))
error_width = max(len('error'), max(len(r.get('error_reason', '')) for r in data))

# Ensure minimum widths for readability
func_width = max(func_width, 20)
file_width = max(file_width, 25)
type_width = max(type_width, 15)
orig_width = max(orig_width, 20)
error_width = max(error_width, 30)

# Print header
print(f\"{'function':<{func_width}} | {'file':<{file_width}} | {'type_name':<{type_width}} | {'original_type':<{orig_width}} | {'error':<{error_width}}\")
print('-' * (func_width + file_width + type_width + orig_width + error_width + 12))

# Print rows
for row in data:
    func = row.get('function_name', '')[:func_width]
    file_path = row.get('file_path', '')[:file_width]
    type_name = row.get('type_name', '')[:type_width]
    orig_type = row.get('original_type', '')[:orig_width]
    error = row.get('error_reason', '')[:error_width]
    
    print(f\"{func:<{func_width}} | {file_path:<{file_width}} | {type_name:<{type_width}} | {orig_type:<{orig_width}} | {error:<{error_width}}\")

# Print summary
print()
print(f'Total unresolved types: {len(data)}')

# Count by error type
error_counts = {}
for row in data:
    error_type = row.get('error_type', 'unknown')
    error_counts[error_type] = error_counts.get(error_type, 0) + 1

if error_counts:
    print('Breakdown by error type:')
    for error_type in sorted(error_counts.keys()):
        count = error_counts[error_type]
        print(f'  {error_type}: {count}')
"
}

# Format validation report as human-readable output
format_validation_report() {
    python3 -c "
import json
import sys

try:
    report = json.loads(sys.stdin.read())
except json.JSONDecodeError:
    print('Error: Invalid JSON output from validation')
    sys.exit(1)

# Print status
status = report.get('status', 'unknown')
status_symbol = '✓' if status == 'valid' else '✗'
print(f'{status_symbol} Validation Status: {status.upper()}')
print()

# Print summary statistics
summary = report.get('summary', {})
print('Summary Statistics:')
print(f'  Total functions: {summary.get(\"total_functions\", 0)}')
print(f'  Functions with file_path: {summary.get(\"functions_with_file_path\", 0)}')
print(f'  Functions without file_path: {summary.get(\"functions_without_file_path\", 0)}')
print()
print(f'  Total parameters: {summary.get(\"total_parameters\", 0)}')
print(f'  Empty parameters: {summary.get(\"empty_parameters\", 0)}')
print(f'  Parameters with LIKE reference: {summary.get(\"parameters_with_like_reference\", 0)}')
print(f'  Parameters resolved: {summary.get(\"parameters_resolved\", 0)}')
print(f'  Parameters unresolved: {summary.get(\"parameters_unresolved\", 0)}')
print()
print(f'  Total return types: {summary.get(\"total_returns\", 0)}')
print(f'  Return types with LIKE reference: {summary.get(\"returns_with_like_reference\", 0)}')
print(f'  Return types resolved: {summary.get(\"returns_resolved\", 0)}')
print(f'  Return types unresolved: {summary.get(\"returns_unresolved\", 0)}')
print()

# Print issues if any
issues = report.get('issues', [])
if issues:
    print('Issues Found:')
    for issue in issues:
        severity = issue.get('severity', 'unknown').upper()
        issue_type = issue.get('type', 'unknown')
        message = issue.get('message', 'No message')
        count = issue.get('count', '')
        
        if count:
            print(f'  [{severity}] {issue_type}: {message}')
        else:
            print(f'  [{severity}] {issue_type}: {message}')
else:
    print('No issues found. Database is consistent.')
"
}

# Main command routing
if [ $# -eq 0 ]; then
    usage
    exit 1
fi

command="$1"
shift

case "$command" in
    find-function)
        python3 "$PROJECT_ROOT/scripts/query_db.py" find_function "$SIGNATURES_DB" "$@"
        ;;
    find-function-resolved)
        # Query function with resolved types from workspace_resolved.json
        WORKSPACE_RESOLVED="${WORKSPACE_RESOLVED:-workspace_resolved.json}"
        if [[ ! -f "$WORKSPACE_RESOLVED" && -f "$PROJECT_ROOT/workspace_resolved.json" ]]; then
            WORKSPACE_RESOLVED="$PROJECT_ROOT/workspace_resolved.json"
        fi
        python3 "$PROJECT_ROOT/scripts/query_db.py" find_function_resolved "$WORKSPACE_RESOLVED" "$@"
        ;;
    search-functions)
        python3 "$PROJECT_ROOT/scripts/query_db.py" search_functions "$SIGNATURES_DB" "$@"
        ;;
    list-file-functions)
        python3 "$PROJECT_ROOT/scripts/query_db.py" list_file_functions "$SIGNATURES_DB" "$@"
        ;;
    find-function-dependencies)
        python3 "$PROJECT_ROOT/scripts/query_db.py" find_function_dependencies "$SIGNATURES_DB" "$@"
        ;;
    find-function-dependents)
        python3 "$PROJECT_ROOT/scripts/query_db.py" find_function_dependents "$SIGNATURES_DB" "$@"
        ;;
    find-dead-code)
        python3 "$PROJECT_ROOT/scripts/query_db.py" find_dead_code "$SIGNATURES_DB"
        ;;
    find-functions-in-module)
        python3 "$PROJECT_ROOT/scripts/query_db.py" find_functions_in_module "$MODULES_DB" "$SIGNATURES_DB" "$@"
        ;;
    find-module-for-function)
        python3 "$PROJECT_ROOT/scripts/query_db.py" find_module_for_function "$MODULES_DB" "$SIGNATURES_DB" "$@"
        ;;
    find-functions-calling-in-module)
        python3 "$PROJECT_ROOT/scripts/query_db.py" find_functions_calling_in_module "$MODULES_DB" "$SIGNATURES_DB" "$@"
        ;;
    find-module-dependencies)
        python3 "$PROJECT_ROOT/scripts/query_db.py" find_module_dependencies "$MODULES_DB" "$SIGNATURES_DB" "$@"
        ;;
    find-module)
        python3 "$PROJECT_ROOT/scripts/query_db.py" find_module "$MODULES_DB" "$@"
        ;;
    search-modules)
        python3 "$PROJECT_ROOT/scripts/query_db.py" search_modules "$MODULES_DB" "$@"
        ;;
    list-file-modules)
        python3 "$PROJECT_ROOT/scripts/query_db.py" list_file_modules "$MODULES_DB" "$@"
        ;;
    create-dbs)
        create_dbs
        ;;
    create-signatures-db)
        WS_JSON="${WS_JSON:-workspace.json}"
        if [[ ! -f "$WS_JSON" && -f "$PROJECT_ROOT/workspace.json" ]]; then
            WS_JSON="$PROJECT_ROOT/workspace.json"
        fi
        python3 "$PROJECT_ROOT/scripts/json_to_sqlite.py" signatures "$WS_JSON" "$SIGNATURES_DB"
        ;;
    create-modules-db)
        MOD_JSON="${MOD_JSON:-modules.json}"
        if [[ ! -f "$MOD_JSON" && -f "$PROJECT_ROOT/modules.json" ]]; then
            MOD_JSON="$PROJECT_ROOT/modules.json"
        fi
        python3 "$PROJECT_ROOT/scripts/json_to_sqlite.py" modules "$MOD_JSON" "$MODULES_DB"
        ;;
    find-reference)
        python3 "$PROJECT_ROOT/scripts/query_headers.py" find-reference "$SIGNATURES_DB" "$@"
        ;;
    find-author)
        python3 "$PROJECT_ROOT/scripts/query_headers.py" find-author "$SIGNATURES_DB" "$@"
        ;;
    file-references)
        python3 "$PROJECT_ROOT/scripts/query_headers.py" file-references "$SIGNATURES_DB" "$@"
        ;;
    file-authors)
        python3 "$PROJECT_ROOT/scripts/query_headers.py" file-authors "$SIGNATURES_DB" "$@"
        ;;
    author-expertise)
        python3 "$PROJECT_ROOT/scripts/query_headers.py" author-expertise "$SIGNATURES_DB" "$@"
        ;;
    recent-changes)
        python3 "$PROJECT_ROOT/scripts/query_headers.py" recent-changes "$SIGNATURES_DB" "$@"
        ;;
    search-references)
        python3 "$PROJECT_ROOT/scripts/query_headers.py" search-references "$SIGNATURES_DB" "$@"
        ;;
    search-reference-prefix)
        python3 "$PROJECT_ROOT/scripts/query_headers.py" search-reference-prefix "$SIGNATURES_DB" "$@"
        ;;
    batch-query)
        # Handle batch query with optional input/output parameters
        input_file=""
        output_file=""
        
        # Parse --input and --output parameters
        while [[ $# -gt 0 ]]; do
            case "$1" in
                --input)
                    input_file="$2"
                    shift 2
                    ;;
                --output)
                    output_file="$2"
                    shift 2
                    ;;
                *)
                    # First positional argument is the input file
                    if [[ -z "$input_file" ]]; then
                        input_file="$1"
                    fi
                    shift
                    ;;
            esac
        done
        
        if [[ -z "$input_file" ]]; then
            echo "Error: batch-query requires an input JSON file" >&2
            echo "Usage: query.sh batch-query <json_file>" >&2
            echo "       query.sh batch-query --input <json_file> --output <output_file>" >&2
            exit 1
        fi
        
        # Execute batch query
        result=$(python3 "$PROJECT_ROOT/scripts/batch_query_handler.py" "$input_file" "$SIGNATURES_DB" "$MODULES_DB" "$PROJECT_ROOT")
        
        # Write to output file if specified, otherwise print to stdout
        if [[ -n "$output_file" ]]; then
            echo "$result" > "$output_file"
            echo "Batch query results written to: $output_file"
        else
            echo "$result"
        fi
        ;;
    find-dependents-in-module)
        python3 "$PROJECT_ROOT/scripts/relationship_queries.py" find-dependents-in-module "$MODULES_DB" "$SIGNATURES_DB" "$@"
        ;;
    find-call-chain)
        python3 "$PROJECT_ROOT/scripts/relationship_queries.py" find-call-chain "$SIGNATURES_DB" "$@"
        ;;
    find-common-callers)
        python3 "$PROJECT_ROOT/scripts/relationship_queries.py" find-common-callers "$SIGNATURES_DB" "$@"
        ;;
    unresolved-types)
        # Parse command line arguments for unresolved-types
        filter_type=""
        limit=""
        offset=""
        
        while [[ $# -gt 0 ]]; do
            case "$1" in
                --filter)
                    filter_type="$2"
                    shift 2
                    ;;
                --limit)
                    limit="$2"
                    shift 2
                    ;;
                --offset)
                    offset="$2"
                    shift 2
                    ;;
                *)
                    echo "Unknown option: $1" >&2
                    exit 1
                    ;;
            esac
        done
        
        # Build arguments for Python script
        python_args=("$SIGNATURES_DB")
        [[ -n "$filter_type" ]] && python_args+=("--filter" "$filter_type")
        [[ -n "$limit" ]] && python_args+=("--limit" "$limit")
        [[ -n "$offset" ]] && python_args+=("--offset" "$offset")
        
        # Execute query and format output
        python3 "$PROJECT_ROOT/scripts/query_db.py" find_unresolved_types "${python_args[@]}" | format_unresolved_types
        ;;
    validate-types)
        # Validate type resolution data consistency
        python3 "$PROJECT_ROOT/scripts/query_db.py" validate_type_resolution "$SIGNATURES_DB" | format_validation_report
        ;;
    *)
        echo "Unknown command: $command" >&2
        usage
        exit 1
        ;;
esac
