#!/bin/bash
# desc:
# Complete generation pipeline: parse schema, load into database, generate signatures, resolve types
#       -       -       -       -       -       -       -       -       -       -       -       -       -       -       -
#       13/03/2026              hdean           Initial
#       -       -       -       -       -       -       -       -       -       -       -       -       -       -       -

set -euo pipefail

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Get the parent directory (project root)
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Configuration
VERBOSE="${VERBOSE:-0}"
CODEBASE_DIR="${1:-.}"
SCHEMA_FILE="${SCHEMA_FILE:-}"
WORKSPACE_DIR="${WORKSPACE_DIR:-.}"

# Output files
SCHEMA_JSON="${WORKSPACE_DIR}/schema.json"
WORKSPACE_DB="${WORKSPACE_DIR}/workspace.db"
WORKSPACE_JSON="${WORKSPACE_DIR}/workspace.json"
WORKSPACE_RESOLVED="${WORKSPACE_DIR}/workspace_resolved.json"

# Validate codebase directory
if [[ ! -d "$CODEBASE_DIR" ]]; then
    echo "Error: Codebase directory not found: $CODEBASE_DIR" >&2
    exit 1
fi

# Function to print verbose output
verbose() {
    if [[ "$VERBOSE" == "1" ]]; then
        echo "$@" >&2
    fi
}

# Step 1: Find and parse schema files
verbose "Step 1: Parsing schema files..."

if [[ -z "$SCHEMA_FILE" ]]; then
    # Find schema files in codebase
    SCHEMA_FILES=$(find "$CODEBASE_DIR" -name "*.sch" -type f)
    if [[ -z "$SCHEMA_FILES" ]]; then
        verbose "Warning: No .sch schema files found in $CODEBASE_DIR"
        verbose "Type resolution will be skipped"
        SKIP_TYPE_RESOLUTION=1
    else
        # Parse first schema file found
        SCHEMA_FILE=$(echo "$SCHEMA_FILES" | head -1)
        verbose "Found schema file: $SCHEMA_FILE"
    fi
else
    if [[ ! -f "$SCHEMA_FILE" ]]; then
        echo "Error: Schema file not found: $SCHEMA_FILE" >&2
        exit 1
    fi
fi

# Parse schema if found
if [[ -n "$SCHEMA_FILE" && ! -v SKIP_TYPE_RESOLUTION ]]; then
    verbose "Parsing schema: $SCHEMA_FILE"
    python3 "$PROJECT_ROOT/scripts/parse_schema.py" "$SCHEMA_FILE" "$SCHEMA_JSON"
    verbose "✓ Schema parsed: $SCHEMA_JSON"
    
    # Step 2: Load schema into database
    verbose "Step 2: Loading schema into database..."
    python3 "$PROJECT_ROOT/scripts/json_to_sqlite_schema.py" "$SCHEMA_JSON" "$WORKSPACE_DB"
    verbose "✓ Schema loaded: $WORKSPACE_DB"
fi

# Step 3: Generate function signatures
verbose "Step 3: Generating function signatures..."
bash "$PROJECT_ROOT/src/generate_signatures.sh" "$CODEBASE_DIR"
verbose "✓ Signatures generated: $WORKSPACE_JSON"

# Step 4: Resolve LIKE types (if schema was loaded)
if [[ ! -v SKIP_TYPE_RESOLUTION && -f "$WORKSPACE_DB" ]]; then
    verbose "Step 4: Resolving LIKE types..."
    python3 "$PROJECT_ROOT/scripts/resolve_types.py" "$WORKSPACE_DB" "$WORKSPACE_JSON" "$WORKSPACE_RESOLVED"
    verbose "✓ Types resolved: $WORKSPACE_RESOLVED"
else
    verbose "Step 4: Skipping type resolution (no schema available)"
fi

# Step 5: Create functions database (optional)
if [[ "${CREATE_DB:-0}" == "1" ]]; then
    verbose "Step 5: Creating functions database..."
    DB_FILE="${WORKSPACE_JSON%.json}.db"
    rm -f "$DB_FILE"
    python3 "$PROJECT_ROOT/scripts/json_to_sqlite.py" signatures "$WORKSPACE_JSON" "$DB_FILE"
    verbose "✓ Functions database created: $DB_FILE"
fi

verbose "✓ Complete generation pipeline finished"
echo "Generated files:"
echo "  - $WORKSPACE_JSON (function signatures)"
if [[ ! -v SKIP_TYPE_RESOLUTION && -f "$WORKSPACE_RESOLVED" ]]; then
    echo "  - $WORKSPACE_RESOLVED (resolved types)"
fi
if [[ -f "$WORKSPACE_DB" ]]; then
    echo "  - $WORKSPACE_DB (schema database)"
fi
