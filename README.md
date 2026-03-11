# genero-func-sigs
shell script(s) to generate and index function signatures when run in a Genero codebase

## Usage

### Generate Signatures

Run the script against your Genero/4GL codebase:

```bash
# Run against current directory (default)
bash generate_signatures.sh

# Run against a specific directory
bash generate_signatures.sh /path/to/genero/code

# Run against a single file
bash generate_signatures.sh path/to/file.4gl
```

The script will generate a `workspace.json` file containing function signatures for all `.4gl` files found.

### Output Format

The script generates a `workspace.json` file with function signatures grouped by file:

Example:
```json
{
  "./src/utils.4gl": [
    "15-42: calculate(amount INTEGER, label STRING):result DECIMAL, status INTEGER",
    "44-58: format_date(input_date DATE):formatted STRING"
  ],
  "./src/auth.4gl": [
    "10-35: validate_user(username STRING, password STRING):is_valid SMALLINT, error_msg STRING"
  ]
}
```

Each signature includes:
- Start and end line numbers (e.g., `15-42:`)
- Function name
- Parameter names and types
- Return value names and types (if any)

## Testing

Run the test suite to verify the script works correctly:

```bash
bash run_tests.sh
```

The test suite includes:
- Test 1: Validates output against expected results from test files
- Test 2: Verifies single file processing
- Test 3: Checks signature format validity

Test files are located in the `tests/` directory and include various function patterns:
- Simple functions with basic types
- Functions with multiple return values
- Functions with complex types (RECORD, DATE, ARRAY, etc.)
