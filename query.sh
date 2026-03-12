#!/bin/bash
# Convenient wrapper for querying the codebase databases

set -euo pipefail

# Default database files
SIGNATURES_DB="${SIGNATURES_DB:-workspace.db}"
MODULES_DB="${MODULES_DB:-modules.db}"

# Show usage
usage() {
    cat << 'EOF'
Usage: query.sh <command> [args...]

Signature queries (workspace.db):
  find-function <name>           Find function by exact name
  search-functions <pattern>     Search functions by name pattern
  list-file-functions <path>     List all functions in a file

Module queries (modules.db):
  find-module <name>             Find module by exact name
  search-modules <pattern>        Search modules by name pattern
  list-file-modules <filename>   Find modules using a file

Database management:
  create-dbs                     Create both databases from JSON files
  create-signatures-db           Create workspace.db from workspace.json
  create-modules-db              Create modules.db from modules.json

Examples:
  query.sh find-function my_function
  query.sh search-functions "get_*"
  query.sh find-module core
  query.sh list-file-modules "util.4gl"
EOF
}

# Create databases
create_dbs() {
    echo "Creating databases..."
    python3 scripts/json_to_sqlite.py signatures workspace.json "$SIGNATURES_DB"
    python3 scripts/json_to_sqlite.py modules modules.json "$MODULES_DB"
    echo "Done. Databases created:"
    ls -lh "$SIGNATURES_DB" "$MODULES_DB"
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
        python3 scripts/query_db.py find_function "$SIGNATURES_DB" "$@"
        ;;
    search-functions)
        python3 scripts/query_db.py search_functions "$SIGNATURES_DB" "$@"
        ;;
    list-file-functions)
        python3 scripts/query_db.py list_file_functions "$SIGNATURES_DB" "$@"
        ;;
    find-module)
        python3 scripts/query_db.py find_module "$MODULES_DB" "$@"
        ;;
    search-modules)
        python3 scripts/query_db.py search_modules "$MODULES_DB" "$@"
        ;;
    list-file-modules)
        python3 scripts/query_db.py list_file_modules "$MODULES_DB" "$@"
        ;;
    create-dbs)
        create_dbs
        ;;
    create-signatures-db)
        python3 scripts/json_to_sqlite.py signatures workspace.json "$SIGNATURES_DB"
        ;;
    create-modules-db)
        python3 scripts/json_to_sqlite.py modules modules.json "$MODULES_DB"
        ;;
    *)
        echo "Unknown command: $command" >&2
        usage
        exit 1
        ;;
esac
