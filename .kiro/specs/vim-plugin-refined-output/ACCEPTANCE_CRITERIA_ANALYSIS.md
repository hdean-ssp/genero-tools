# Acceptance Criteria Analysis: Refined Output for Vim Plugin

This document provides detailed analysis of each acceptance criterion to guide design and testing.

## Requirement 1: Concise Signature Format

### Criterion 1.1: Format Option Support
**Criterion:** WHEN a query command is executed with `--format=vim`, THE Query_Command SHALL return function signatures in concise format

**Testable:** Yes - Property
**Property:** `--format=vim` option selects concise format
**Test Type:** Unit test
**Test Approach:**
- Execute query with `--format=vim`
- Verify output is in concise format (single line, no file info)
- Verify format matches pattern: `name(params) -> return`

**Example Test Case:**
```bash
bash query.sh find-function "calculate" --format=vim
# Expected: calculate(amount: INTEGER) -> DECIMAL
```

---

### Criterion 1.2: Format Pattern
**Criterion:** THE concise format SHALL include function name, parameters with types, and return type on a single line

**Testable:** Yes - Property
**Property:** Concise format follows pattern `name(params) -> return`
**Test Type:** Unit test
**Test Approach:**
- Parse output to verify single line
- Verify function name is present
- Verify parameters with types are present
- Verify return type is present
- Verify no file path or line number

**Example Test Case:**
```
Input: function with name="calculate", params=[{name: "amount", type: "INTEGER"}], return="DECIMAL"
Expected: calculate(amount: INTEGER) -> DECIMAL
```

---

### Criterion 1.3: Format Pattern Definition
**Criterion:** THE concise format SHALL follow the pattern: `function_name(param1: TYPE1, param2: TYPE2) -> RETURN_TYPE`

**Testable:** Yes - Property
**Property:** Output matches regex: `^[a-zA-Z_][a-zA-Z0-9_]*\([^)]*\)\s*->\s*[A-Z_][A-Z0-9_,\s]*$`
**Test Type:** Unit test
**Test Approach:**
- Generate concise format for various functions
- Verify each output matches the pattern
- Test with multiple parameters
- Test with complex types

**Example Test Cases:**
```
calculate(amount: INTEGER) -> DECIMAL
process_data(id: INTEGER, name: VARCHAR) -> RECORD
validate() -> INTEGER
```

---

### Criterion 1.4: No Parameters
**Criterion:** WHEN a function has no parameters, THE concise format SHALL display: `function_name() -> RETURN_TYPE`

**Testable:** Yes - Edge Case
**Edge Case:** Function with empty parameter list
**Test Type:** Unit test
**Test Approach:**
- Create function with no parameters
- Generate concise format
- Verify output is `name() -> return`
- Verify no extra spaces or commas

**Example Test Case:**
```
Input: function with name="get_timestamp", params=[], return="DATETIME"
Expected: get_timestamp() -> DATETIME
```

---

### Criterion 1.5: No Return Type
**Criterion:** WHEN a function has no return type, THE concise format SHALL display: `function_name(param1: TYPE1, param2: TYPE2)`

**Testable:** Yes - Edge Case
**Edge Case:** Function with no return type (procedure)
**Test Type:** Unit test
**Test Approach:**
- Create function with no return type
- Generate concise format
- Verify output has no `->` or return type
- Verify parameters are present

**Example Test Case:**
```
Input: function with name="log_message", params=[{name: "msg", type: "VARCHAR"}], return=null
Expected: log_message(msg: VARCHAR)
```

---

### Criterion 1.6: Multiple Return Types
**Criterion:** WHEN a function has multiple return types, THE concise format SHALL display all return types separated by commas: `function_name() -> TYPE1, TYPE2`

**Testable:** Yes - Edge Case
**Edge Case:** Function with multiple return values
**Test Type:** Unit test
**Test Approach:**
- Create function with multiple return types
- Generate concise format
- Verify all return types are present
- Verify types are separated by commas
- Verify no extra spaces

**Example Test Case:**
```
Input: function with name="get_data", params=[], return=["INTEGER", "VARCHAR"]
Expected: get_data() -> INTEGER, VARCHAR
```

---

### Criterion 1.7: Standard Type Names
**Criterion:** THE concise format SHALL use standard Genero type names (INTEGER, VARCHAR, DECIMAL, RECORD, ARRAY, etc.)

**Testable:** Yes - Property
**Property:** Output uses only valid Genero type names
**Test Type:** Unit test
**Test Approach:**
- Test with all standard Genero types
- Verify type names are uppercase
- Verify no abbreviations or aliases
- Test with complex types (RECORD, ARRAY)

**Example Test Cases:**
```
INTEGER, VARCHAR, DECIMAL, DATETIME, BOOLEAN
RECORD, ARRAY, LIKE table.column
```

---

### Criterion 1.8: No Extra Information
**Criterion:** THE concise format SHALL NOT include line numbers, file paths, or complexity metrics

**Testable:** Yes - Property
**Property:** Output contains only name, params, and return type
**Test Type:** Unit test
**Test Approach:**
- Generate concise format
- Verify no file path in output
- Verify no line number in output
- Verify no complexity metrics
- Verify single line output

**Example Test Case:**
```
Input: function with file="src/module.4gl", line=42, complexity=5
Expected: calculate(amount: INTEGER) -> DECIMAL
# No file, line, or complexity info
```

---

### Criterion 1.9: Performance
**Criterion:** WHEN the concise format is generated, THE Query_Command SHALL complete execution within 100ms for typical codebases

**Testable:** Yes - Property
**Property:** Query execution time < 100ms
**Test Type:** Performance test
**Test Approach:**
- Execute query on typical codebase (1000+ functions)
- Measure execution time
- Verify time < 100ms
- Test with various query patterns

**Example Test Case:**
```
bash time query.sh search-functions "get_*" --format=vim
# Expected: real 0m0.050s (or less)
```

---

## Requirement 2: Hover-Friendly Output Format

### Criterion 2.1: Format Option Support
**Criterion:** WHEN a query command is executed with `--format=vim-hover`, THE Query_Command SHALL return function information in hover format

**Testable:** Yes - Property
**Property:** `--format=vim-hover` option selects hover format
**Test Type:** Unit test
**Test Approach:**
- Execute query with `--format=vim-hover`
- Verify output is in hover format (multi-line)
- Verify includes signature, file, complexity

**Example Test Case:**
```bash
bash query.sh find-function "calculate" --format=vim-hover
# Expected: multi-line output with signature, file, complexity
```

---

### Criterion 2.2: Signature Line
**Criterion:** THE hover format SHALL include the function signature on the first line

**Testable:** Yes - Property
**Property:** First line is concise format signature
**Test Type:** Unit test
**Test Approach:**
- Generate hover format
- Extract first line
- Verify it matches concise format pattern
- Verify it's the complete signature

**Example Test Case:**
```
First line: calculate(amount: INTEGER) -> DECIMAL
```

---

### Criterion 2.3: File Location Line
**Criterion:** THE hover format SHALL include the file location (file path and line number) on the second line

**Testable:** Yes - Property
**Property:** Second line contains file path and line number
**Test Type:** Unit test
**Test Approach:**
- Generate hover format
- Extract second line
- Verify format is `File: path/to/file.4gl:42`
- Verify file path is correct
- Verify line number is correct

**Example Test Case:**
```
Second line: File: src/module.4gl:42
```

---

### Criterion 2.4: Complexity Metrics Line
**Criterion:** THE hover format SHALL include complexity metrics (cyclomatic complexity and line count) on the third line

**Testable:** Yes - Property
**Property:** Third line contains complexity and LOC metrics
**Test Type:** Unit test
**Test Approach:**
- Generate hover format
- Extract third line
- Verify format is `Complexity: N, LOC: M`
- Verify complexity value is correct
- Verify LOC value is correct

**Example Test Case:**
```
Third line: Complexity: 5, LOC: 23
```

---

### Criterion 2.5: Format Pattern
**Criterion:** THE hover format SHALL follow the pattern:
```
function_name(param1: TYPE1, param2: TYPE2) -> RETURN_TYPE
File: path/to/file.4gl:42
Complexity: 5, LOC: 23
```

**Testable:** Yes - Property
**Property:** Output matches multi-line pattern
**Test Type:** Unit test
**Test Approach:**
- Generate hover format
- Verify three lines present
- Verify each line matches expected pattern
- Verify no extra lines

**Example Test Case:**
```
calculate(amount: INTEGER) -> DECIMAL
File: src/module.4gl:42
Complexity: 5, LOC: 23
```

---

### Criterion 2.6: Concise Signature
**Criterion:** THE hover format SHALL use the concise signature format from Requirement 1

**Testable:** Yes - Property
**Property:** First line matches concise format
**Test Type:** Unit test
**Test Approach:**
- Generate hover format
- Extract first line
- Verify it matches concise format exactly
- Test with various function signatures

**Example Test Case:**
```
Hover first line: calculate(amount: INTEGER) -> DECIMAL
Concise format: calculate(amount: INTEGER) -> DECIMAL
# Should be identical
```

---

### Criterion 2.7: Missing File Location
**Criterion:** WHEN file location is unavailable, THE hover format SHALL display: `File: unknown`

**Testable:** Yes - Edge Case
**Edge Case:** Function without file location metadata
**Test Type:** Unit test
**Test Approach:**
- Create function without file path or line number
- Generate hover format
- Verify second line is `File: unknown`

**Example Test Case:**
```
Input: function without file_path or line
Expected second line: File: unknown
```

---

### Criterion 2.8: Missing Complexity Metrics
**Criterion:** WHEN complexity metrics are unavailable, THE hover format SHALL display: `Complexity: unknown, LOC: unknown`

**Testable:** Yes - Edge Case
**Edge Case:** Function without complexity metrics
**Test Type:** Unit test
**Test Approach:**
- Create function without complexity or LOC data
- Generate hover format
- Verify third line is `Complexity: unknown, LOC: unknown`

**Example Test Case:**
```
Input: function without complexity or LOC
Expected third line: Complexity: unknown, LOC: unknown
```

---

### Criterion 2.9: Human-Readable Format
**Criterion:** THE hover format SHALL be human-readable and suitable for display in editor tooltips

**Testable:** Yes - Property
**Property:** Output is formatted for human reading
**Test Type:** Manual test
**Test Approach:**
- Generate hover format for various functions
- Verify output is easy to read
- Verify formatting is consistent
- Verify no excessive whitespace

**Example Test Case:**
```
calculate(amount: INTEGER) -> DECIMAL
File: src/module.4gl:42
Complexity: 5, LOC: 23
# Should be easy to read in tooltip
```

---

### Criterion 2.10: Performance
**Criterion:** WHEN the hover format is generated, THE Query_Command SHALL complete execution within 100ms for typical codebases

**Testable:** Yes - Property
**Property:** Query execution time < 100ms
**Test Type:** Performance test
**Test Approach:**
- Execute query with `--format=vim-hover`
- Measure execution time
- Verify time < 100ms

**Example Test Case:**
```bash
bash time query.sh find-function "calculate" --format=vim-hover
# Expected: real 0m0.050s (or less)
```

---

## Requirement 3: Completion-Friendly Output Format

### Criterion 3.1: Format Option Support
**Criterion:** WHEN a query command is executed with `--format=vim-completion`, THE Query_Command SHALL return function metadata in JSON format

**Testable:** Yes - Property
**Property:** `--format=vim-completion` option returns JSON
**Test Type:** Unit test
**Test Approach:**
- Execute query with `--format=vim-completion`
- Verify output is valid JSON
- Verify output is array of objects

**Example Test Case:**
```bash
bash query.sh search-functions "get_*" --format=vim-completion
# Expected: valid JSON array
```

---

### Criterion 3.2: JSON Array Format
**Criterion:** THE completion format SHALL be a JSON array of objects, one per function

**Testable:** Yes - Property
**Property:** Output is valid JSON array
**Test Type:** Unit test
**Test Approach:**
- Generate completion format
- Parse as JSON
- Verify it's an array
- Verify one object per function

**Example Test Case:**
```json
[
  {"name": "get_account", ...},
  {"name": "get_customer", ...}
]
```

---

### Criterion 3.3: Required Fields
**Criterion:** EACH JSON object SHALL include the following fields:
- `name`: Function name (string)
- `params`: Parameter list as a string (e.g., "id: INTEGER, name: VARCHAR")
- `return`: Return type(s) as a string (e.g., "DECIMAL" or "INTEGER, VARCHAR")
- `file`: File path where function is defined (string)
- `line`: Line number where function is defined (integer)
- `complexity`: Cyclomatic complexity (integer or null if unavailable)
- `loc`: Lines of code (integer or null if unavailable)

**Testable:** Yes - Property
**Property:** Each object has all required fields
**Test Type:** Unit test
**Test Approach:**
- Generate completion format
- Parse JSON
- For each object, verify all fields are present
- Verify field types are correct

**Example Test Case:**
```json
{
  "name": "calculate",
  "params": "amount: INTEGER",
  "return": "DECIMAL",
  "file": "src/module.4gl",
  "line": 42,
  "complexity": 5,
  "loc": 23
}
```

---

### Criterion 3.4: No Parameters
**Criterion:** WHEN a function has no parameters, THE `params` field SHALL be an empty string

**Testable:** Yes - Edge Case
**Edge Case:** Function with no parameters
**Test Type:** Unit test
**Test Approach:**
- Create function with no parameters
- Generate completion format
- Verify `params` field is empty string (not null)

**Example Test Case:**
```json
{
  "name": "get_timestamp",
  "params": "",
  "return": "DATETIME"
}
```

---

### Criterion 3.5: No Return Type
**Criterion:** WHEN a function has no return type, THE `return` field SHALL be an empty string

**Testable:** Yes - Edge Case
**Edge Case:** Function with no return type
**Test Type:** Unit test
**Test Approach:**
- Create function with no return type
- Generate completion format
- Verify `return` field is empty string (not null)

**Example Test Case:**
```json
{
  "name": "log_message",
  "params": "msg: VARCHAR",
  "return": ""
}
```

---

### Criterion 3.6: Missing Metadata
**Criterion:** WHEN metadata is unavailable, THE corresponding field SHALL be null

**Testable:** Yes - Edge Case
**Edge Case:** Function with missing metadata
**Test Type:** Unit test
**Test Approach:**
- Create function with missing metadata
- Generate completion format
- Verify missing fields are null (not empty string)

**Example Test Case:**
```json
{
  "name": "unknown_function",
  "params": "...",
  "return": "...",
  "file": null,
  "line": null,
  "complexity": null,
  "loc": null
}
```

---

### Criterion 3.7: Valid JSON
**Criterion:** THE completion format SHALL be valid JSON that can be parsed by standard JSON parsers

**Testable:** Yes - Property
**Property:** Output is valid JSON
**Test Type:** Unit test
**Test Approach:**
- Generate completion format
- Parse with standard JSON parser
- Verify no parse errors
- Verify structure is correct

**Example Test Case:**
```bash
bash query.sh search-functions "get_*" --format=vim-completion | python3 -m json.tool
# Should parse without errors
```

---

### Criterion 3.8: Plugin Parsing
**Criterion:** THE completion format SHALL be suitable for parsing by editor plugins

**Testable:** Yes - Property
**Property:** Output can be parsed and used by plugins
**Test Type:** Integration test
**Test Approach:**
- Generate completion format
- Parse in plugin code
- Verify all fields are accessible
- Verify data is usable

**Example Test Case:**
```python
import json
result = json.loads(output)
for func in result:
    print(f"{func['name']}({func['params']}) -> {func['return']}")
```

---

### Criterion 3.9: Performance
**Criterion:** WHEN the completion format is generated, THE Query_Command SHALL complete execution within 100ms for typical codebases

**Testable:** Yes - Property
**Property:** Query execution time < 100ms
**Test Type:** Performance test
**Test Approach:**
- Execute query with `--format=vim-completion`
- Measure execution time
- Verify time < 100ms

**Example Test Case:**
```bash
bash time query.sh search-functions "get_*" --format=vim-completion
# Expected: real 0m0.050s (or less)
```

---

## Requirement 4: Format Option for Query Commands

### Criterion 4.1-4.8: Format Options
**Criteria:** Format options work correctly and are documented

**Testable:** Yes - Property
**Property:** Format options select correct format
**Test Type:** Unit test
**Test Approach:**
- Test each format option
- Verify correct format is selected
- Test case-insensitivity
- Test error handling

**Example Test Cases:**
```bash
--format=vim          # Concise format
--format=vim-hover    # Hover format
--format=vim-completion # Completion format
--format=VIM          # Case-insensitive
--format=invalid      # Error
```

---

## Requirement 5: Filtering for Plugin Use Cases

### Criterion 5.1-5.8: Filtering Options
**Criteria:** Filtering options work correctly and reduce output

**Testable:** Yes - Property
**Property:** Filters reduce result set correctly
**Test Type:** Unit test
**Test Approach:**
- Test each filter option
- Verify correct filtering
- Test multiple filters
- Test error handling

**Example Test Cases:**
```bash
--filter=functions-only    # Exclude procedures
--filter=no-metrics        # Exclude complexity
--filter=no-file-info      # Exclude file info
```

---

## Requirement 6: Backward Compatibility

### Criterion 6.1-6.7: Backward Compatibility
**Criteria:** Existing queries work unchanged

**Testable:** Yes - Property
**Property:** Default behavior is unchanged
**Test Type:** Integration test
**Test Approach:**
- Run existing queries without format option
- Verify output is identical to before
- Run existing tests
- Verify all tests pass

**Example Test Case:**
```bash
bash query.sh find-function "calculate"
# Should produce same output as before
```

---

## Requirement 7: Comprehensive Test Coverage

### Criterion 7.1-7.15: Test Coverage
**Criteria:** >90% code coverage for all features

**Testable:** Yes - Property
**Property:** Code coverage > 90%
**Test Type:** Coverage analysis
**Test Approach:**
- Run test suite with coverage tool
- Measure code coverage
- Verify > 90% coverage
- Identify and test uncovered code

**Example Test Case:**
```bash
python3 -m pytest --cov=scripts/format_output tests/
# Expected: coverage > 90%
```

---

## Requirement 8: Documentation of Output Formats

### Criterion 8.1-8.10: Documentation
**Criteria:** Complete documentation with examples

**Testable:** Yes - Example
**Example:** Documentation includes all required sections
**Test Type:** Documentation review
**Test Approach:**
- Review documentation
- Verify all sections present
- Verify examples are correct
- Verify examples are runnable

**Example Sections:**
- Concise format examples
- Hover format examples
- Completion format examples
- Format option documentation
- Filter option documentation
- Code examples
- Reference guide
- Troubleshooting
- Performance characteristics

---

## Requirement 9: Integration with Existing Query Commands

### Criterion 9.1-9.8: Query Integration
**Criteria:** Format options work with all query commands

**Testable:** Yes - Property
**Property:** Format options work with all query commands
**Test Type:** Integration test
**Test Approach:**
- Test each query command with each format
- Verify correct output
- Verify no errors
- Test with various inputs

**Example Test Cases:**
```bash
bash query.sh find-function "calculate" --format=vim
bash query.sh search-functions "get_*" --format=vim-hover
bash query.sh list-file-functions "src/module.4gl" --format=vim-completion
```

---

## Requirement 10: Error Handling and Validation

### Criterion 10.1-10.10: Error Handling
**Criteria:** Clear error messages and validation

**Testable:** Yes - Property
**Property:** Invalid input produces error message
**Test Type:** Unit test
**Test Approach:**
- Test invalid format options
- Test invalid filter options
- Test missing database
- Test query failures
- Verify error messages are clear

**Example Test Cases:**
```bash
--format=invalid       # Error: Invalid format
--filter=invalid       # Error: Invalid filter
# Database not found   # Error: Database not found
```

---

## Summary of Testability

| Requirement | Testable | Type | Approach |
|-------------|----------|------|----------|
| 1. Concise Format | Yes | Property | Pattern matching, edge cases |
| 2. Hover Format | Yes | Property | Multi-line parsing, edge cases |
| 3. Completion Format | Yes | Property | JSON parsing, field validation |
| 4. Format Option | Yes | Property | Option parsing, error handling |
| 5. Filtering | Yes | Property | Filter logic, result validation |
| 6. Backward Compatibility | Yes | Property | Regression testing |
| 7. Test Coverage | Yes | Property | Coverage analysis |
| 8. Documentation | Yes | Example | Documentation review |
| 9. Query Integration | Yes | Property | Integration testing |
| 10. Error Handling | Yes | Property | Error condition testing |

---

**All requirements are testable and have clear test strategies.**

