#!/bin/bash
# desc:
# Extract GLOBALS and IMPORT statements from .4gl files
# Generates modulars.json with file-level modular information
#       -       -       -       -       -       -       -       -       -       -       -       -       -       -       -
#       04/01/2026              hdean           Initial
#       -       -       -       -       -       -       -       -       -       -       -       -       -       -       -

set -euo pipefail

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Get the parent directory (project root)
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Configuration
VERSION="1.0.0"
VERBOSE="${VERBOSE:-0}"
OUTPUT_FILE="${OUTPUT_FILE:-modulars.json}"

# Accept directory/file as parameter, default to current directory
TARGET="${1:-.}"

# Validate target exists
if [[ ! -e "$TARGET" ]]; then
    echo "Error: Target '$TARGET' does not exist" >&2
    exit 1
fi

# Create temp file and ensure cleanup
TEMP_FILE=$(mktemp)
trap 'rm -f "$TEMP_FILE"' EXIT

# Count total files for metadata
TOTAL_FILES=$(find "$TARGET" -name "*.4gl" -type f | wc -l)
if [[ "$VERBOSE" == "1" ]]; then
    echo "Found $TOTAL_FILES .4gl files to process" >&2
fi

# Process all .4gl files in the target
find "$TARGET" -name "*.4gl" -type f -print0 | while IFS= read -r -d '' file; do
    if [[ "$VERBOSE" == "1" ]]; then
        echo "Processing: $file" >&2
    fi
    
    # Strip the TARGET path from the file path to get relative path
    if [[ -d "$TARGET" ]]; then
        # TARGET is a directory
        relative_file="${file#$TARGET/}"
        if [[ "$relative_file" == "$file" ]]; then
            # If stripping didn't work, try without trailing slash
            relative_file="${file#$TARGET}"
            if [[ "$relative_file" == /* ]]; then
                relative_file="${relative_file#/}"
            fi
        fi
    else
        # TARGET is a file, just use the basename
        relative_file=$(basename "$file")
    fi
    
    # Extract GLOBALS and IMPORT statements
    sed 's/[^[:print:]\t]//g' "$file" | awk -v file="$relative_file" '
    BEGIN {
        globals_count = 0
        imports_count = 0
    }
    
    /^GLOBALS/ {
        globals_count++
        global_name = $0
        sub(/^GLOBALS[ \t]+/, "", global_name)
        gsub(/^[ \t]+|[ \t]+$/, "", global_name)
        if (global_name != "") {
            globals[globals_count] = global_name
        }
        next
    }
    
    /^IMPORT/ {
        imports_count++
        import_name = $0
        sub(/^IMPORT[ \t]+/, "", import_name)
        gsub(/^[ \t]+|[ \t]+$/, "", import_name)
        if (import_name != "") {
            imports[imports_count] = import_name
        }
        next
    }
    
    END {
        # Build globals array
        globals_json = ""
        for (i = 1; i <= globals_count; i++) {
            globals_json = globals_json (i > 1 ? ", " : "")
            globals_json = globals_json sprintf("\"%s\"", globals[i])
        }
        
        # Build imports array
        imports_json = ""
        for (i = 1; i <= imports_count; i++) {
            imports_json = imports_json (i > 1 ? ", " : "")
            imports_json = imports_json sprintf("\"%s\"", imports[i])
        }
        
        # Print structured JSON
        printf "{\"file\":\"%s\",\"globals\":[%s],\"imports\":[%s]}\n",
               file, globals_json, imports_json
    }
    ' "$file" >> "$TEMP_FILE" 2>/dev/null || true
done

# Generate timestamp in ISO 8601 format
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Process modulars using Python script
python3 "$PROJECT_ROOT/scripts/process_modulars.py" "$TEMP_FILE" "$OUTPUT_FILE" "$VERSION" "$TIMESTAMP" "$TOTAL_FILES"

if [[ "$VERBOSE" == "1" ]]; then
    echo "Generated $OUTPUT_FILE successfully" >&2
fi
