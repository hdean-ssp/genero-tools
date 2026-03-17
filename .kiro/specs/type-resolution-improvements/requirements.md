# Type Resolution Improvements Requirements

## Introduction

The genero-tools type resolution system currently has several data quality issues that limit its effectiveness for IDE features and code analysis. Empty parameters are stored in the database, LIKE references in return types are not resolved, function instances are not properly disambiguated when they exist in multiple files, and there is no visibility into unresolved types for debugging. These issues result in incomplete type information, incorrect function resolution, and difficulty diagnosing type resolution failures.

Type Resolution Improvements will fix parameter parsing to eliminate empty parameters, resolve all LIKE references in both parameters and return types, implement multi-instance function resolution using both function name and file path, and add debugging capabilities to query unresolved types. These improvements will ensure data quality, enable accurate type resolution, and provide visibility into the type resolution process.

## Glossary

- **Type_Resolution**: The process of converting LIKE references to actual database schema types
- **LIKE_Reference**: A type specification using the pattern "LIKE table.column" or "LIKE table.*"
- **Parameter**: A function input with a name and type specification
- **Return_Type**: The type specification for a function's return value
- **Empty_Parameter**: A parameter with a null or empty name stored in the database
- **Resolved_Type**: A LIKE reference that has been successfully converted to actual schema types
- **Unresolved_Type**: A LIKE reference that could not be converted due to missing table or column
- **Function_Instance**: A specific occurrence of a function definition in a particular file
- **Function_Disambiguation**: The process of identifying which function instance is being referenced
- **File_Path**: The complete path to a source file containing function definitions
- **Schema_Type**: An actual type from the database schema (table name, column name, column type)
- **Type_Information**: Complete type data including original type, resolved type, and resolution status
- **Data_Quality**: The accuracy and completeness of data stored in the database
- **Debugging_Visibility**: The ability to inspect and understand type resolution failures
- **Workspace_Database**: The SQLite database (workspace.db) containing parsed function signatures
- **Workspace_JSON**: The JSON file (workspace.json) containing raw parsed function data
- **Workspace_Resolved**: The JSON file (workspace_resolved.json) containing type-resolved function data

## Requirements

### Requirement 1: Fix Empty Parameter Parsing

**User Story:** As a database analyst, I want to ensure all parameters have valid names, so that the database contains only valid data and queries don't return incomplete parameter information.

#### Acceptance Criteria

1. WHEN json_to_sqlite.py processes workspace.json, THE Parser SHALL skip parameters with empty or null names
2. WHEN json_to_sqlite.py processes workspace.json, THE Parser SHALL log a warning for each skipped empty parameter including the function name and file path
3. THE Parser SHALL not insert any parameters with null or empty names into the parameters table
4. WHEN a function has all empty parameters, THE Parser SHALL insert the function with zero parameters
5. THE Parser SHALL maintain accurate parameter counts in the function signature
6. WHEN processing is complete, THE Parser SHALL report the total number of empty parameters skipped

#### Acceptance Criteria - Data Validation

7. WHEN querying the parameters table, THE Query_Engine SHALL never return parameters with null or empty names
8. THE Database SHALL enforce that all parameter names are non-empty strings (NOT NULL constraint)
9. WHEN a query attempts to insert an empty parameter, THE Database SHALL reject the insert with a clear error message

### Requirement 2: Resolve LIKE References in Return Types

**User Story:** As a type analyst, I want return types with LIKE references to be resolved to actual schema types, so that function return types are complete and accurate.

#### Acceptance Criteria

1. WHEN resolve_types.py processes a function with a return_type containing a LIKE reference, THE Resolver SHALL resolve the LIKE reference to actual schema types
2. THE Resolver SHALL handle LIKE patterns: "LIKE table.*" (all columns) and "LIKE table.column" (specific column)
3. WHEN a LIKE reference is resolved, THE Resolver SHALL store the table name, column names, and column types
4. WHEN a LIKE reference cannot be resolved (missing table or column), THE Resolver SHALL store the error reason and mark as unresolved
5. THE Resolver SHALL process all return types in workspace.json, not just parameters
6. WHEN merge_resolved_types.py merges resolved types, THE Merger SHALL update the returns table with resolved type information
7. THE Merger SHALL add columns to the returns table: actual_type, is_like_reference, resolved, resolution_error, table_name, columns, types

#### Acceptance Criteria - Return Type Storage

8. THE returns table SHALL store resolved return type information with the same structure as parameters
9. WHEN querying return types, THE Query_Engine SHALL return both original type and resolved type information
10. THE Query_Engine SHALL indicate whether a return type is a LIKE reference and whether it was successfully resolved

### Requirement 3: Resolve LIKE References in Parameters

**User Story:** As a type analyst, I want parameter types with LIKE references to be resolved to actual schema types, so that function parameters are complete and accurate.

#### Acceptance Criteria

1. WHEN resolve_types.py processes a function with parameters containing LIKE references, THE Resolver SHALL resolve each LIKE reference to actual schema types
2. THE Resolver SHALL handle LIKE patterns: "LIKE table.*" (all columns) and "LIKE table.column" (specific column)
3. WHEN a LIKE reference is resolved, THE Resolver SHALL store the table name, column names, and column types
4. WHEN a LIKE reference cannot be resolved (missing table or column), THE Resolver SHALL store the error reason and mark as unresolved
5. WHEN merge_resolved_types.py merges resolved types, THE Merger SHALL update the parameters table with resolved type information
6. THE Merger SHALL add columns to the parameters table: actual_type, is_like_reference, resolved, resolution_error, table_name, columns, types

#### Acceptance Criteria - Parameter Storage

7. THE parameters table SHALL store resolved parameter type information including original type and resolved types
8. WHEN querying parameters, THE Query_Engine SHALL return both original type and resolved type information
9. THE Query_Engine SHALL indicate whether a parameter type is a LIKE reference and whether it was successfully resolved

### Requirement 4: Fix Multi-Instance Function Resolution

**User Story:** As a code analyst, I want functions with the same name in different files to be properly distinguished, so that function resolution is accurate and unambiguous.

#### Acceptance Criteria

1. WHEN json_to_sqlite.py processes functions, THE Parser SHALL store the file_path for each function instance
2. THE functions table SHALL have a file_path column to store the source file path
3. WHEN querying functions by name, THE Query_Engine SHALL return all instances of the function across all files
4. WHEN resolving function calls, THE Resolver SHALL match on both function name AND file_path to identify the correct instance
5. WHEN a function call is ambiguous (multiple instances with same name), THE Resolver SHALL use file_path to disambiguate
6. THE Resolver SHALL store the resolved file_path for each function call reference

#### Acceptance Criteria - Function Disambiguation

7. WHEN querying for a specific function instance, THE Query_Engine SHALL support queries like "find function 'foo' in file 'path/to/file.4gl'"
8. THE Query_Engine SHALL return the correct function instance when multiple instances exist
9. WHEN displaying function information, THE Query_Engine SHALL include the file_path to distinguish instances

### Requirement 5: Add Unresolved Types Query Command

**User Story:** As a type resolution debugger, I want to query unresolved types, so that I can identify and fix type resolution failures.

#### Acceptance Criteria

1. THE query_db.py module SHALL provide a function `find_unresolved_types()` that returns all unresolved LIKE references
2. WHEN find_unresolved_types() is called, THE Query_Engine SHALL return all parameters with unresolved LIKE references
3. WHEN find_unresolved_types() is called, THE Query_Engine SHALL return all return types with unresolved LIKE references
4. THE Query_Engine SHALL return results including: function name, file path, parameter/return name, original type, and error reason
5. THE Query_Engine SHALL support filtering by error type (missing table, missing column, invalid pattern)
6. THE Query_Engine SHALL support pagination on unresolved types results

#### Acceptance Criteria - Shell Command

7. THE query.sh script SHALL provide a new command `unresolved-types` that invokes find_unresolved_types()
8. WHEN `query.sh unresolved-types` is invoked, THE Shell SHALL return all unresolved types in a formatted output
9. THE Shell SHALL support `--filter` parameter to filter by error type
10. THE Shell SHALL support `--limit` and `--offset` parameters for pagination
11. THE Shell SHALL display results in a human-readable format with columns: function, file, type_name, original_type, error

#### Acceptance Criteria - Output Format

12. THE Query_Engine SHALL return unresolved types as a JSON array with objects containing: function_name, file_path, parameter_name, return_name, original_type, error_reason, error_type
13. THE Shell output SHALL be formatted as a table with clear column headers
14. THE Shell output SHALL include a summary line showing total unresolved types and breakdown by error type

### Requirement 6: Ensure Data Consistency

**User Story:** As a database administrator, I want to ensure type resolution data is consistent across all tables, so that queries return accurate results.

#### Acceptance Criteria

1. WHEN type resolution is complete, THE System SHALL verify that all LIKE references have been processed
2. THE System SHALL verify that no parameters have empty names
3. THE System SHALL verify that all function instances have file_path values
4. THE System SHALL verify that resolved type information is consistent between parameters and returns tables
5. WHEN inconsistencies are detected, THE System SHALL report them with specific details
6. THE System SHALL provide a validation command to check data consistency

#### Acceptance Criteria - Validation

7. THE query_db.py module SHALL provide a function `validate_type_resolution()` that checks data consistency
8. WHEN validate_type_resolution() is called, THE Validator SHALL check for empty parameters
9. WHEN validate_type_resolution() is called, THE Validator SHALL check for missing file_path values
10. WHEN validate_type_resolution() is called, THE Validator SHALL check for unresolved LIKE references
11. THE Validator SHALL return a report with status and any issues found

### Requirement 7: Performance Requirements

**User Story:** As a system operator, I want type resolution to complete efficiently, so that the system remains responsive.

#### Acceptance Criteria

1. THE Resolver SHALL process workspace.json with 10,000+ functions within 5 seconds
2. THE Merger SHALL merge resolved types into workspace.db within 3 seconds
3. THE Query_Engine SHALL return unresolved types query results within 100ms
4. THE System SHALL not consume more than 500MB of memory during type resolution
5. THE System SHALL support incremental type resolution for large codebases

### Requirement 8: Backward Compatibility

**User Story:** As a genero-tools user, I want existing scripts and integrations to continue working, so that I don't need to update my code.

#### Acceptance Criteria

1. THE System SHALL continue to support existing query commands without modification
2. THE System SHALL not change the output format of existing queries
3. THE System SHALL make new columns optional with sensible defaults
4. WHEN existing code does not use new features, THE System SHALL behave identically to the current implementation
5. THE System SHALL not introduce breaking changes to the database schema (only additive changes)

