
#!/bin/bash
# desc:
# a shell script to generate a large index of signatures for
# all of the functions in the current Genero/4GL codebase
#       -       -       -       -       -       -       -       -       -       -       -       -       -       -       -
#       11/03/2026              hdean           Initial
#       -       -       -       -       -       -       -       -       -       -       -       -       -       -       -

set -euo pipefail

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Get the parent directory (project root)
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Configuration
VERSION="1.0.0"
VERBOSE="${VERBOSE:-0}"
OUTPUT_FILE="${OUTPUT_FILE:-workspace.json}"

# Accept directory/file as parameter, default to current directory
TARGET="${1:-.}"

# Validate target exists
if [[ ! -e "$TARGET" ]]; then
    echo "Error: Target '$TARGET' does not exist" >&2
    exit 1
fi

# Normalize TARGET to be relative if it's absolute and starts with current directory
if [[ "$TARGET" = /* ]]; then
    # Absolute path - try to make it relative
    if [[ "$TARGET" = "$PWD"* ]]; then
        TARGET=".${TARGET#$PWD}"
    fi
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
    
    sed 's/[^[:print:]\t]//g; s/\r//g' "$file" | awk -v file="$relative_file" '


    BEGIN {
        in_function = 0
        delete vars
        delete param_order
        delete param_types
        delete return_order
        delete record_fields
        delete function_calls
        call_count = 0
        # Build ord lookup for hashing (printable ASCII)
        _ord_str = " !\"#$%&'"'"'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
        for (_oi = 1; _oi <= length(_ord_str); _oi++) {
            _ord[substr(_ord_str, _oi, 1)] = _oi + 31
        }
    }

    /^FUNCTION / {
        # If we were in a function, skip it (incomplete function)
        if (in_function) {
            in_function = 0
            delete vars
            delete param_order
            delete param_types
            delete return_order
            delete record_fields
        }
        
        in_function = 1
        function_start_line = NR  # Track start line
        body_text = ""  # Accumulate body for hashing
        current_function = substr($0, index($0, "FUNCTION ") + 9)
        sub(/\(.*/, "", current_function)
        gsub(/^[ \t]+|[ \t]+$/, "", current_function)  # Trim whitespace

        # Accumulate the full parameter list across multiple lines
        # In Genero/4GL, parameters can span multiple lines:
        #   FUNCTION foo(param1,
        #       param2, param3)
        full_line = $0
        while (index(full_line, ")") == 0) {
            if ((getline next_line) <= 0) break
            # Strip comment lines to avoid ) in comments stopping accumulation
            stripped = next_line
            gsub(/^[ \t]+/, "", stripped)
            if (substr(stripped, 1, 1) == "#") continue
            # Strip inline comments before checking for closing paren
            sub(/[ \t]*#.*/, "", next_line)
            full_line = full_line " " next_line
        }

        sub(/.*\(/, "", full_line)
        sub(/\).*/, "", full_line)
        params = full_line
        param_count = split(params, param_arr, /, */)

        delete param_order
        delete param_types
        delete return_order
        return_count = 0  # Initialize return count to 0
        actual_param_count = 0
        for (i = 1; i <= param_count; i++) {
            # Trim leading/trailing whitespace from parameter
            gsub(/^[ \t]+|[ \t]+$/, "", param_arr[i])
            
            # Skip empty parameter names (from trailing commas or blank splits)
            if (param_arr[i] == "") continue

            actual_param_count++

            # Extract name (first word) and type (everything after first word)
            if (match(param_arr[i], /^[^ \t]+/)) {
                name = substr(param_arr[i], RSTART, RLENGTH)
                # Type is everything after the name
                type = substr(param_arr[i], RLENGTH + 1)
                gsub(/^[ \t]+|[ \t]+$/, "", type)  # Trim type whitespace
            } else {
                name = param_arr[i]
                type = ""
            }
            param_order[actual_param_count] = name
            param_types[name] = type
            vars[name] = type
        }
        param_count = actual_param_count
        next
    }

    # Accumulate function body text for hashing (runs for every line inside a function)
    in_function {
        body_text = body_text $0 "\n"
    }

    in_function && /^[ \t]*DEFINE / {
        sub(/^[ \t]*DEFINE[ \t]+/, "")

        # Handle multi-line RECORD definitions:
        # Accumulate lines until END RECORD to get the full type
        define_line = $0
        if (match(define_line, /RECORD/) && !match(define_line, /RECORD[ \t]+LIKE/)) {
            # Multi-line RECORD - accumulate until END RECORD
            # Track fields inside the record for field-level type resolution
            while (index(define_line, "END RECORD") == 0) {
                if ((getline next_line) <= 0) break
                define_line = define_line "\n" next_line
            }
        }

        # Check for multi-variable DEFINE: DEFINE a, b, c INTEGER
        # Detect by looking for comma before the type keyword
        # Pattern: name1, name2, name3 TYPE
        first_part = define_line
        # Remove everything after newline for type extraction (use first line only for names)
        sub(/\n.*/, "", first_part)

        # Check if this is a multi-variable define (has commas before the type)
        # Strategy: find the last comma, check if what follows looks like a type
        if (match(first_part, /^[a-zA-Z_][a-zA-Z0-9_]*([ \t]*,[ \t]*[a-zA-Z_][a-zA-Z0-9_]*)+[ \t]+/)) {
            # Multi-variable DEFINE detected
            names_part = substr(first_part, RSTART, RLENGTH)
            var_type = substr(first_part, RSTART + RLENGTH)
            gsub(/^[ \t]+|[ \t]+$/, "", var_type)

            # Split names on comma
            n_count = split(names_part, name_arr, /[ \t]*,[ \t]*/)
            for (ni = 1; ni <= n_count; ni++) {
                gsub(/^[ \t]+|[ \t]+$/, "", name_arr[ni])
                if (name_arr[ni] == "") continue
                if (name_arr[ni] in param_types) {
                    param_types[name_arr[ni]] = var_type
                }
                vars[name_arr[ni]] = var_type
            }
        } else {
            # Single variable DEFINE
            match(first_part, /^[^ \t]+/)
            var_name = substr(first_part, RSTART, RLENGTH)
            # Extract type (everything after first whitespace, trimmed)
            type_part = substr(first_part, RSTART + RLENGTH)
            gsub(/^[ \t]+|[ \t]+$/, "", type_part)
            var_type = type_part

            # For multi-line RECORD, extract field info and store in record_fields
            if (match(define_line, /RECORD/) && !match(var_type, /^RECORD[ \t]+LIKE/)) {
                # Parse fields from the RECORD block
                rec_body = define_line
                sub(/^[^\n]*\n?/, "", rec_body)  # Remove first line (DEFINE var RECORD)
                sub(/\n[ \t]*END RECORD.*/, "", rec_body)  # Remove END RECORD line

                # Parse each field line
                fn_count = split(rec_body, field_lines, /\n/)
                for (fi = 1; fi <= fn_count; fi++) {
                    gsub(/^[ \t]+|[ \t]+$/, "", field_lines[fi])
                    sub(/,[ \t]*$/, "", field_lines[fi])  # Remove trailing comma
                    if (field_lines[fi] == "") continue
                    # Extract field name and type
                    if (match(field_lines[fi], /^[a-zA-Z_][a-zA-Z0-9_]*/)) {
                        f_name = substr(field_lines[fi], RSTART, RLENGTH)
                        f_type = substr(field_lines[fi], RSTART + RLENGTH)
                        gsub(/^[ \t]+|[ \t]+$/, "", f_type)
                        # Store as var_name.field_name for lookup
                        record_fields[var_name "." f_name] = f_type
                    }
                }
            }

            # Update parameter type if this is a parameter redefinition
            if (var_name in param_types) {
                param_types[var_name] = var_type
            }
            vars[var_name] = var_type
        }
        next
    }

    in_function && /RETURN[ \t(]/ {
        line_content = $0
        sub(/.*RETURN[ \t]*/, "", line_content)
        sub(/[ \t]*(#|;).*/, "", line_content)
        gsub(/^[ \t]+|[ \t]+$/, "", line_content)

        # Skip bare RETURN (no value)
        if (line_content == "" || line_content == ")") {
            next
        }

        # Only capture the first RETURN with values (most representative)
        if (return_count == 0) {
            return_count = split(line_content, return_arr, /, */)
            for (i = 1; i <= return_count; i++) {
                gsub(/^[ \t]+|[ \t]+$/, "", return_arr[i])
                return_order[i] = return_arr[i]
            }
        } else {
            # If a later RETURN has more values, use it instead
            tmp_count = split(line_content, tmp_arr, /, */)
            if (tmp_count > return_count) {
                return_count = tmp_count
                for (i = 1; i <= return_count; i++) {
                    gsub(/^[ \t]+|[ \t]+$/, "", tmp_arr[i])
                    return_order[i] = tmp_arr[i]
                }
            }
        }

        # Also extract function calls from RETURN expressions (no next - fall through)
        # Extract function calls: word followed by (
        ret_scan = line_content
        while (match(ret_scan, /[a-zA-Z_][a-zA-Z0-9_]*[ \t]*\(/)) {
            called_func = substr(ret_scan, RSTART, RLENGTH)
            sub(/[ \t]*\(.*/, "", called_func)
            if (called_func != current_function) {
                call_count++
                function_calls[call_count] = called_func "|" NR
            }
            ret_scan = substr(ret_scan, RSTART + RLENGTH)
        }
        next
    }

    # Pattern 1: Direct CALL statements
    in_function && /^[ \t]*CALL[ \t]+[a-zA-Z_][a-zA-Z0-9_]*[ \t]*\(/ {
        line_content = $0
        sub(/^[ \t]*CALL[ \t]+/, "", line_content)
        match(line_content, /^[a-zA-Z_][a-zA-Z0-9_]*/)
        called_func = substr(line_content, RSTART, RLENGTH)
        
        call_count++
        function_calls[call_count] = called_func "|" NR
        next
    }

    # Pattern 2: LET var = function_name(params)
    in_function && /^[ \t]*LET[ \t]+[a-zA-Z_][a-zA-Z0-9_]*[ \t]*=[ \t]*[a-zA-Z_][a-zA-Z0-9_]*[ \t]*\(/ {
        line_content = $0
        sub(/.*=[ \t]*/, "", line_content)
        match(line_content, /^[a-zA-Z_][a-zA-Z0-9_]*/)
        called_func = substr(line_content, RSTART, RLENGTH)
        
        call_count++
        function_calls[call_count] = called_func "|" NR
        next
    }

    # Pattern 3: Function calls in control flow conditions (IF, WHILE, CASE, WHEN)
    in_function && /^[ \t]*(IF|ELSEIF|WHILE|CASE|WHEN).*[a-zA-Z_][a-zA-Z0-9_]*[ \t]*\(/ {
        line_content = $0
        sub(/^[ \t]*(IF|ELSEIF|WHILE|CASE|WHEN)[ \t]+/, "", line_content)
        
        # Extract all function calls from this line
        while (match(line_content, /[a-zA-Z_][a-zA-Z0-9_]*[ \t]*\(/)) {
            called_func = substr(line_content, RSTART, RLENGTH)
            sub(/[ \t]*\(.*/, "", called_func)
            
            # Avoid duplicates and false positives
            if (called_func != current_function && called_func != "IF" && called_func != "ELSEIF" && called_func != "WHILE" && called_func != "CASE" && called_func != "WHEN") {
                call_count++
                function_calls[call_count] = called_func "|" NR
            }
            
            line_content = substr(line_content, RSTART + RLENGTH)
        }
        next
    }

    /END FUNCTION/ {
        if (!in_function) {
            next  # Skip END FUNCTION without matching FUNCTION
        }
        
        function_end_line = NR  # Track end line
        
        # Build parameters array
        params_json = ""
        params_str = ""
        for (i = 1; i <= param_count; i++) {
            name = param_order[i]
            type = param_types[name]
            params_json = params_json (i > 1 ? ", " : "")
            params_json = params_json sprintf("{\"name\":\"%s\",\"type\":\"%s\"}", name, type ? type : "unknown")
            params_str = params_str (i > 1 ? ", " : "") name " " (type ? type : "unknown")
        }

        # Build returns array with expression-aware type resolution
        returns_json = ""
        returns_str = ""
        for (i = 1; i <= return_count; i++) {
            var = return_order[i]
            type = ""

            # Strategy: resolve the return expression to a type
            # 1. Direct variable lookup
            if (var in vars) {
                type = vars[var]
            }
            # 2. Boolean literals
            else if (toupper(var) == "TRUE" || toupper(var) == "FALSE") {
                type = "BOOLEAN"
            }
            # 3. Numeric literals (integers)
            else if (match(var, /^-?[0-9]+$/)) {
                type = "INTEGER"
            }
            # 4. Numeric literals (decimals)
            else if (match(var, /^-?[0-9]+\.[0-9]+$/)) {
                type = "DECIMAL"
            }
            # 5. String literals
            else if (match(var, /^".*"$/) || match(var, /^\x27.*\x27$/)) {
                type = "STRING"
            }
            # 6. NULL literal
            else if (toupper(var) == "NULL") {
                type = "NULL"
            }
            # 7. Record field access: l_rec.field - look up in record_fields first, then base var
            else if (match(var, /^[a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*$/)) {
                if (var in record_fields) {
                    type = record_fields[var]
                } else {
                    # Try base variable lookup
                    base_var = var
                    sub(/\..*/, "", base_var)
                    if (base_var in vars) {
                        type = vars[base_var] " (field)"
                    }
                }
            }
            # 8. Array element field access: l_arr[n].field
            else if (match(var, /^[a-zA-Z_][a-zA-Z0-9_]*\[.*\]\.[a-zA-Z_][a-zA-Z0-9_]*$/)) {
                base_var = var
                sub(/\[.*/, "", base_var)
                if (base_var in vars) {
                    type = vars[base_var] " (element field)"
                }
            }
            # 9. Array element: l_arr[n]
            else if (match(var, /^[a-zA-Z_][a-zA-Z0-9_]*\[.*\]$/)) {
                base_var = var
                sub(/\[.*/, "", base_var)
                if (base_var in vars) {
                    type = vars[base_var] " (element)"
                }
            }
            # 10. Method call: l_data.getLength()
            else if (match(var, /^[a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*\(/)) {
                base_var = var
                sub(/\..*/, "", base_var)
                if (base_var in vars) {
                    type = "INTEGER"  # Most methods return INTEGER (getLength, etc.)
                }
            }
            # 11. Function call: func_name(args) - check if wrapping a known variable
            else if (match(var, /^[a-zA-Z_][a-zA-Z0-9_]*\(/)) {
                # Extract function name and try to infer type from argument
                func_call_name = var
                sub(/\(.*/, "", func_call_name)
                # Common Genero built-ins that return STRING
                if (toupper(func_call_name) == "UPSHIFT" || toupper(func_call_name) == "DOWNSHIFT" || toupper(func_call_name) == "TRIM" || toupper(func_call_name) == "LPAD" || toupper(func_call_name) == "RPAD" || toupper(func_call_name) == "SFMT" || toupper(func_call_name) == "ASCII") {
                    type = "STRING"
                }
                # Common Genero built-ins that return INTEGER
                else if (toupper(func_call_name) == "LENGTH" || toupper(func_call_name) == "ORD" || toupper(func_call_name) == "FGL_LASTKEY" || toupper(func_call_name) == "ARR_COUNT" || toupper(func_call_name) == "SCR_LINE" || toupper(func_call_name) == "NUM_ARGS") {
                    type = "INTEGER"
                }
                else {
                    type = "expression"
                }
            }
            # 12. Expression with operators: (l_count > 0), var CLIPPED, etc.
            else if (match(var, /^[(\t ]*[a-zA-Z_][a-zA-Z0-9_]*/)) {
                # Try to extract base variable from expression
                expr_var = var
                sub(/^[( \t]*/, "", expr_var)
                sub(/[) \t].*/, "", expr_var)
                sub(/\..*/, "", expr_var)  # Strip field access
                if (expr_var in vars) {
                    # Check if it looks like a boolean expression
                    if (match(var, /[><=!]/) || match(var, /AND|OR|NOT/)) {
                        type = "BOOLEAN"
                    } else if (match(var, /CLIPPED|USING/)) {
                        type = vars[expr_var]
                    } else {
                        type = vars[expr_var]
                    }
                }
            }

            if (type == "") type = "unknown"

            returns_json = returns_json (i > 1 ? ", " : "")
            returns_json = returns_json sprintf("{\"name\":\"%s\",\"type\":\"%s\"}", var, type)
            returns_str = returns_str (i > 1 ? ", " : "") var " " type
        }

        # Build calls array
        calls_json = ""
        for (i = 1; i <= call_count; i++) {
            split(function_calls[i], call_parts, "|")
            called_name = call_parts[1]
            call_line = call_parts[2]
            
            calls_json = calls_json (i > 1 ? ", " : "")
            calls_json = calls_json sprintf("{\"name\":\"%s\",\"line\":%d}", called_name, call_line)
        }

        # Build variables array (all defined variables except parameters)
        variables_json = ""
        var_count = 0
        for (var_name in vars) {
            # Skip if parameter (already in parameters array)
            is_param = 0
            for (j = 1; j <= param_count; j++) {
                if (param_order[j] == var_name) {
                    is_param = 1
                    break
                }
            }
            if (!is_param && var_name != "") {
                var_count++
                var_type = vars[var_name]
                variables_json = variables_json (var_count > 1 ? ", " : "")
                variables_json = variables_json sprintf("{\"name\":\"%s\",\"type\":\"%s\"}", var_name, var_type ? var_type : "unknown")
            }
        }

        # Create signature string with line numbers
        function_sig = function_start_line "-" function_end_line ": " current_function "(" params_str ")"
        if (returns_str != "" && return_count > 0) {
            function_sig = function_sig ":" returns_str
        }

        # Compute body hash for change detection (polynomial rolling hash)
        body_loc = function_end_line - function_start_line - 1
        _h = 0
        for (_ci = 1; _ci <= length(body_text); _ci++) {
            _ch = substr(body_text, _ci, 1)
            _cv = (_ch in _ord) ? _ord[_ch] : 10
            _h = (_h * 31 + _cv) % 2147483647
        }
        body_hash = sprintf("%08x", _h)

        # Build record_types object (field definitions for RECORD variables)
        record_types_json = ""
        rf_count = 0
        for (rf_key in record_fields) {
            rf_count++
            record_types_json = record_types_json (rf_count > 1 ? ", " : "")
            record_types_json = record_types_json sprintf("\"%s\":\"%s\"", rf_key, record_fields[rf_key])
        }

        # Print structured JSON with calls, variables, and record types
        if (rf_count > 0) {
            printf "{\"file\":\"%s\",\"name\":\"%s\",\"line\":{\"start\":%d,\"end\":%d},\"body_hash\":\"%s\",\"body_loc\":%d,\"signature\":\"%s\",\"parameters\":[%s],\"returns\":[%s],\"calls\":[%s],\"variables\":[%s],\"record_types\":{%s}}\n",
                   file, current_function, function_start_line, function_end_line, body_hash, body_loc, function_sig, params_json, returns_json, calls_json, variables_json, record_types_json
        } else {
            printf "{\"file\":\"%s\",\"name\":\"%s\",\"line\":{\"start\":%d,\"end\":%d},\"body_hash\":\"%s\",\"body_loc\":%d,\"signature\":\"%s\",\"parameters\":[%s],\"returns\":[%s],\"calls\":[%s],\"variables\":[%s]}\n",
                   file, current_function, function_start_line, function_end_line, body_hash, body_loc, function_sig, params_json, returns_json, calls_json, variables_json
        }

        in_function = 0
        body_text = ""
        delete vars
        delete param_order
        delete param_types
        delete return_order
        delete record_fields
        delete function_calls
        call_count = 0
    }
    ' >> "$TEMP_FILE" 2>/dev/null || true
done

# Generate timestamp in ISO 8601 format
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Process signatures using Python script
python3 "$PROJECT_ROOT/scripts/process_signatures.py" "$TEMP_FILE" "$OUTPUT_FILE" "$VERSION" "$TIMESTAMP" "$TOTAL_FILES"

# Optional: Generate SQLite database (only if CREATE_DB is set)
if [[ "${CREATE_DB:-0}" == "1" ]]; then
    DB_FILE="${OUTPUT_FILE%.json}.db"
    # Remove existing database to avoid UNIQUE constraint errors
    rm -f "$DB_FILE"
    python3 "$PROJECT_ROOT/scripts/json_to_sqlite.py" signatures "$OUTPUT_FILE" "$DB_FILE"
    if [[ "$VERBOSE" == "1" ]]; then
        echo "Generated $DB_FILE for fast querying" >&2
    fi
fi

# Optional: Resolve LIKE types (only if RESOLVE_TYPES is set and workspace.db exists)
if [[ "${RESOLVE_TYPES:-0}" == "1" ]] && [[ -f "workspace.db" ]]; then
    RESOLVED_OUTPUT="${OUTPUT_FILE%.json}_resolved.json"
    python3 "$PROJECT_ROOT/scripts/resolve_types.py" workspace.db "$OUTPUT_FILE" "$RESOLVED_OUTPUT"
    if [[ "$VERBOSE" == "1" ]]; then
        echo "Generated $RESOLVED_OUTPUT with type resolution" >&2
    fi
fi

if [[ "$VERBOSE" == "1" ]]; then
    echo "Generated $OUTPUT_FILE successfully" >&2
fi
