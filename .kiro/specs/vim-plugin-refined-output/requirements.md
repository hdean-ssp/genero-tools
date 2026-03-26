# Requirements Document: Refined Output for Vim Plugin

## Introduction

This document specifies requirements for Feature 1.1: Refined Output for Vim Plugin. The feature creates optimized output formats for Vim plugin integration, enabling better editor integration with concise, hover-friendly, and completion-friendly output formats. This feature builds on the completed Type Resolution v2.1.0 and provides the foundation for IDE/editor integration.

## Glossary

- **Query_Command**: A shell command that retrieves metadata from the genero-tools database (e.g., `bash query.sh find-function`)
- **Output_Format**: A structured representation of query results optimized for specific use cases (concise, hover, completion)
- **Vim_Plugin**: An editor plugin for Vim that uses genero-tools output to provide code intelligence features
- **Function_Signature**: The complete declaration of a function including name, parameters, and return types
- **Concise_Format**: A compact single-line representation of a function signature
- **Hover_Format**: A multi-line format with signature, file location, and complexity metrics for editor hover tooltips
- **Completion_Format**: A JSON format optimized for autocomplete suggestions in editors
- **Parameter**: A function input with name and type information
- **Return_Type**: The data type returned by a function
- **Complexity_Metric**: A measure of function complexity (cyclomatic complexity)
- **Line_Count**: The number of lines of code in a function
- **File_Location**: The file path and line number where a function is defined
- **Format_Option**: A command-line flag that specifies the output format (e.g., `--format=vim`)
- **Query_Result**: The output data returned by a query command
- **Filtering**: The process of selecting specific fields or records from query results
- **Performance_Target**: The maximum acceptable execution time for a query (<100ms)

## Requirements

### Requirement 1: Concise Signature Format

**User Story:** As a Vim plugin developer, I want concise function signatures in a single-line format, so that I can display them efficiently in editor tooltips and completion menus.

#### Acceptance Criteria

1. WHEN a query command is executed with `--format=vim`, THE Query_Command SHALL return function signatures in concise format
2. THE concise format SHALL include function name, parameters with types, and return type on a single line
3. THE concise format SHALL follow the pattern: `function_name(param1: TYPE1, param2: TYPE2) -> RETURN_TYPE`
4. WHEN a function has no parameters, THE concise format SHALL display: `function_name() -> RETURN_TYPE`
5. WHEN a function has no return type, THE concise format SHALL display: `function_name(param1: TYPE1, param2: TYPE2)`
6. WHEN a function has multiple return types, THE concise format SHALL display all return types separated by commas: `function_name() -> TYPE1, TYPE2`
7. THE concise format SHALL use standard Genero type names (INTEGER, VARCHAR, DECIMAL, RECORD, ARRAY, etc.)
8. THE concise format SHALL NOT include line numbers, file paths, or complexity metrics
9. WHEN the concise format is generated, THE Query_Command SHALL complete execution within 100ms for typical codebases

### Requirement 2: Hover-Friendly Output Format

**User Story:** As a Vim plugin developer, I want detailed function information for hover tooltips, so that users can see comprehensive metadata when hovering over function names.

#### Acceptance Criteria

1. WHEN a query command is executed with `--format=vim-hover`, THE Query_Command SHALL return function information in hover format
2. THE hover format SHALL include the function signature on the first line
3. THE hover format SHALL include the file location (file path and line number) on the second line
4. THE hover format SHALL include complexity metrics (cyclomatic complexity and line count) on the third line
5. THE hover format SHALL follow the pattern:
   ```
   function_name(param1: TYPE1, param2: TYPE2) -> RETURN_TYPE
   File: path/to/file.4gl:42
   Complexity: 5, LOC: 23
   ```
6. THE hover format SHALL use the concise signature format from Requirement 1
7. WHEN file location is unavailable, THE hover format SHALL display: `File: unknown`
8. WHEN complexity metrics are unavailable, THE hover format SHALL display: `Complexity: unknown, LOC: unknown`
9. THE hover format SHALL be human-readable and suitable for display in editor tooltips
10. WHEN the hover format is generated, THE Query_Command SHALL complete execution within 100ms for typical codebases

### Requirement 3: Completion-Friendly Output Format

**User Story:** As a Vim plugin developer, I want function metadata in a native Vim completion format, so that I can efficiently integrate with Vim/Neovim's built-in completion system.

#### Acceptance Criteria

1. WHEN a query command is executed with `--format=vim-completion`, THE Query_Command SHALL return function metadata in tab-separated format
2. THE completion format SHALL be tab-separated with three columns: word, menu, info
3. EACH line SHALL represent one function with the following columns:
   - Column 1 (word): Function name (the completion word)
   - Column 2 (menu): Function signature (e.g., "function(INTEGER, VARCHAR) -> DECIMAL")
   - Column 3 (info): File location and metrics (e.g., "src/module.4gl:42 | Complexity: 5, LOC: 23")
4. THE format SHALL follow the pattern: `function_name\tfunction(param_types) -> return_type\tfile:line | Complexity: N, LOC: M`
5. WHEN a function has no parameters, THE menu column SHALL display: `function_name() -> RETURN_TYPE`
6. WHEN a function has no return type, THE menu column SHALL display: `function_name(param_types)`
7. WHEN file location is unavailable, THE info column SHALL display: `unknown:0 | Complexity: unknown, LOC: unknown`
8. THE completion format SHALL be compatible with Vim's `complete()` function and Neovim's completion API
9. THE completion format SHALL use tab characters (not spaces) as column separators
10. WHEN the completion format is generated, THE Query_Command SHALL complete execution within 100ms for typical codebases

### Requirement 4: Format Option for Query Commands

**User Story:** As a Vim plugin developer, I want to specify output format using a command-line option, so that I can easily switch between different output formats.

#### Acceptance Criteria

1. WHEN a query command is executed with `--format=vim`, THE Query_Command SHALL return output in concise format
2. WHEN a query command is executed with `--format=vim-hover`, THE Query_Command SHALL return output in hover format
3. WHEN a query command is executed with `--format=vim-completion`, THE Query_Command SHALL return output in completion format
4. WHEN a query command is executed without a `--format` option, THE Query_Command SHALL return output in the default format (current behavior)
5. WHEN an invalid format option is provided, THE Query_Command SHALL return an error message and exit with non-zero status
6. THE format option SHALL be supported by all query commands that return function metadata
7. THE format option SHALL be case-insensitive (e.g., `--format=VIM` and `--format=vim` are equivalent)
8. THE format option SHALL be documented in the query command help text

### Requirement 5: Filtering for Plugin Use Cases

**User Story:** As a Vim plugin developer, I want to filter query results by specific criteria, so that I can retrieve only the metadata needed for plugin features.

#### Acceptance Criteria

1. WHEN a query command is executed with `--filter=functions-only`, THE Query_Command SHALL return only function definitions (excluding procedures)
2. WHEN a query command is executed with `--filter=no-metrics`, THE Query_Command SHALL return results without complexity metrics
3. WHEN a query command is executed with `--filter=no-file-info`, THE Query_Command SHALL return results without file path and line number
4. WHEN multiple filters are applied, THE Query_Command SHALL apply all filters in combination
5. WHEN an invalid filter is provided, THE Query_Command SHALL return an error message and exit with non-zero status
6. THE filtering SHALL reduce output size and improve performance for plugin use cases
7. THE filtering SHALL be compatible with all output formats (concise, hover, completion)
8. THE filtering options SHALL be documented in the query command help text

### Requirement 6: Backward Compatibility

**User Story:** As a genero-tools user, I want existing queries to continue working without changes, so that I don't need to update my scripts and tools.

#### Acceptance Criteria

1. WHEN a query command is executed without a `--format` option, THE Query_Command SHALL return output in the current default format
2. THE default output format SHALL be identical to the current behavior
3. WHEN existing scripts use query commands, THE Query_Command SHALL produce the same results as before
4. THE new format options SHALL NOT affect existing query commands that don't use them
5. THE new filtering options SHALL NOT affect existing query commands that don't use them
6. ALL existing tests SHALL pass without modification
7. THE changes SHALL be fully backward compatible with v2.1.0

### Requirement 7: Comprehensive Test Coverage

**User Story:** As a developer, I want comprehensive tests for output formats, so that I can verify correctness and prevent regressions.

#### Acceptance Criteria

1. WHEN concise format tests are executed, THE tests SHALL verify correct formatting of function signatures
2. WHEN concise format tests are executed, THE tests SHALL verify handling of functions with no parameters
3. WHEN concise format tests are executed, THE tests SHALL verify handling of functions with no return types
4. WHEN concise format tests are executed, THE tests SHALL verify handling of multiple return types
5. WHEN hover format tests are executed, THE tests SHALL verify correct formatting of all required fields
6. WHEN hover format tests are executed, THE tests SHALL verify handling of missing metadata
7. WHEN completion format tests are executed, THE tests SHALL verify valid JSON output
8. WHEN completion format tests are executed, THE tests SHALL verify all required fields are present
9. WHEN format option tests are executed, THE tests SHALL verify correct format selection
10. WHEN format option tests are executed, THE tests SHALL verify error handling for invalid formats
11. WHEN filtering tests are executed, THE tests SHALL verify correct filtering behavior
12. WHEN filtering tests are executed, THE tests SHALL verify error handling for invalid filters
13. WHEN backward compatibility tests are executed, THE tests SHALL verify existing behavior is unchanged
14. WHEN performance tests are executed, THE tests SHALL verify query execution time is <100ms
15. THE test suite SHALL achieve >90% code coverage for format and filtering logic

### Requirement 8: Documentation of Output Formats

**User Story:** As a Vim plugin developer, I want clear documentation of output formats, so that I can correctly parse and use the output in my plugin.

#### Acceptance Criteria

1. THE documentation SHALL include examples of concise format output
2. THE documentation SHALL include examples of hover format output
3. THE documentation SHALL include examples of completion format output
4. THE documentation SHALL document the `--format` option and all supported values
5. THE documentation SHALL document the `--filter` option and all supported values
6. THE documentation SHALL include code examples showing how to use each format
7. THE documentation SHALL include a reference guide for all output fields
8. THE documentation SHALL include troubleshooting tips for common issues
9. THE documentation SHALL include performance characteristics for each format
10. THE documentation SHALL be written in Markdown and included in the docs/ directory

### Requirement 9: Integration with Existing Query Commands

**User Story:** As a Vim plugin developer, I want format options to work with all query commands, so that I can use them consistently across my plugin.

#### Acceptance Criteria

1. WHEN `find-function` is executed with `--format=vim`, THE Query_Command SHALL return output in the specified format
2. WHEN `search-functions` is executed with `--format=vim`, THE Query_Command SHALL return output in the specified format
3. WHEN `list-file-functions` is executed with `--format=vim`, THE Query_Command SHALL return output in the specified format
4. WHEN `find-function-resolved` is executed with `--format=vim`, THE Query_Command SHALL return output in the specified format
5. WHEN `find-all-function-instances` is executed with `--format=vim`, THE Query_Command SHALL return output in the specified format
6. THE format options SHALL work with all query commands that return function metadata
7. THE format options SHALL NOT affect query commands that don't return function metadata
8. THE integration SHALL NOT break existing query command functionality

### Requirement 10: Error Handling and Validation

**User Story:** As a Vim plugin developer, I want clear error messages when something goes wrong, so that I can debug issues in my plugin.

#### Acceptance Criteria

1. WHEN an invalid format option is provided, THE Query_Command SHALL return a descriptive error message
2. WHEN an invalid filter option is provided, THE Query_Command SHALL return a descriptive error message
3. WHEN a query fails, THE Query_Command SHALL return an error message with the reason for failure
4. WHEN database is not found, THE Query_Command SHALL return a helpful error message suggesting database creation
5. WHEN no results are found, THE Query_Command SHALL return an empty result set (not an error)
6. WHEN an unexpected error occurs, THE Query_Command SHALL return a descriptive error message
7. ALL error messages SHALL be written to stderr
8. ALL error messages SHALL include the command that failed and the reason for failure
9. THE error handling SHALL NOT crash the query command
10. THE error handling SHALL allow the Vim plugin to handle errors gracefully

## Acceptance Criteria Analysis

### Testability Assessment

**Requirement 1 (Concise Format):** Testable as property
- Property: For any function, concise format SHALL follow pattern `name(params) -> return`
- Example: `calculate(amount: INTEGER) -> DECIMAL`
- Edge case: Functions with no parameters, no return types, multiple returns

**Requirement 2 (Hover Format):** Testable as example
- Example: Multi-line format with signature, file location, complexity
- Edge case: Missing metadata, unknown values

**Requirement 3 (Completion Format):** Testable as property
- Property: Output SHALL be valid JSON with required fields
- Example: JSON array with name, params, return, file, line, complexity, loc
- Edge case: Missing fields, null values

**Requirement 4 (Format Option):** Testable as property
- Property: `--format=X` SHALL select format X
- Example: `--format=vim` selects concise format
- Edge case: Invalid format, case-insensitive matching

**Requirement 5 (Filtering):** Testable as property
- Property: Filters SHALL reduce result set correctly
- Example: `--filter=functions-only` excludes procedures
- Edge case: Multiple filters, invalid filters

**Requirement 6 (Backward Compatibility):** Testable as property
- Property: Default behavior SHALL be unchanged
- Example: Queries without `--format` produce same output
- Edge case: Existing tests pass without modification

**Requirement 7 (Test Coverage):** Testable as property
- Property: Test suite SHALL achieve >90% coverage
- Example: All format types tested, all filters tested
- Edge case: Error conditions, missing data

**Requirement 8 (Documentation):** Testable as example
- Example: Documentation includes all format examples
- Edge case: Complex types, edge cases documented

**Requirement 9 (Query Integration):** Testable as property
- Property: Format options SHALL work with all query commands
- Example: `find-function --format=vim` works
- Edge case: Commands that don't return functions

**Requirement 10 (Error Handling):** Testable as property
- Property: Invalid input SHALL produce error message
- Example: Invalid format produces error
- Edge case: Database not found, no results

