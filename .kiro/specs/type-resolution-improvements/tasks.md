# Implementation Plan: Type Resolution Improvements

## Overview

This implementation plan addresses four core issues in the type resolution system:
1. Empty parameters being stored in the database
2. LIKE references in return types not being resolved
3. Multi-instance functions not being properly disambiguated
4. Lack of visibility into unresolved types

The implementation follows a layered approach: first fixing data quality at the parsing stage, then extending type resolution for return types, then improving function disambiguation, and finally adding debugging capabilities.

## Tasks

- [ ] 1. Fix Empty Parameter Parsing
  - [x] 1.1 Modify json_to_sqlite.py to filter empty parameters
    - Add validation logic to skip parameters with null or empty names
    - Add warning logging for each skipped parameter with function name and file path
    - Update parameter insertion to check for empty names before database insert
    - _Requirements: 1.1, 1.2, 1.3, 1.5_
  
  - [x] 1.2 Add NOT NULL constraint to parameters table
    - Modify database schema to enforce non-empty parameter names
    - Add migration logic to handle existing data
    - _Requirements: 1.8_
  
  - [ ]* 1.3 Write unit tests for empty parameter filtering
    - Test that empty parameters are skipped
    - Test that warnings are logged correctly
    - Test that parameter counts are accurate
    - _Requirements: 1.1, 1.2, 1.3_

- [-] 2. Resolve LIKE References in Return Types
  - [x] 2.1 Extend resolve_types.py to handle return types
    - Add return type extraction from workspace.json
    - Implement LIKE pattern matching for "LIKE table.*" and "LIKE table.column"
    - Add resolution logic to convert LIKE references to actual schema types
    - Store resolution results with table name, column names, and column types
    - _Requirements: 2.1, 2.2, 2.3, 2.4_
  
  - [x] 2.2 Update merge_resolved_types.py to merge return type resolutions
    - Add columns to returns table: actual_type, is_like_reference, resolved, resolution_error, table_name, columns, types
    - Implement merge logic to update returns table with resolved type information
    - Handle unresolved LIKE references with error reasons
    - _Requirements: 2.6, 2.7_
  
  - [x] 2.3 Extend resolve_types.py to handle LIKE references in parameters
    - Add parameter type extraction and LIKE pattern matching
    - Implement resolution logic for parameter LIKE references
    - Store resolution results with table name, column names, and column types
    - _Requirements: 3.1, 3.2, 3.3, 3.4_
  
  - [x] 2.4 Update merge_resolved_types.py to merge parameter type resolutions
    - Add columns to parameters table: actual_type, is_like_reference, resolved, resolution_error, table_name, columns, types
    - Implement merge logic to update parameters table with resolved type information
    - _Requirements: 3.5, 3.6_
  
  - [ ]* 2.5 Write property tests for LIKE reference resolution
    - **Property 1: LIKE table.* resolves to all columns**
    - **Validates: Requirements 2.2, 3.2**
    - Test that "LIKE table.*" resolves to all columns in the table
    - Test that column types are correctly extracted
  
  - [ ]* 2.6 Write unit tests for return type resolution
    - Test LIKE pattern matching for both patterns
    - Test resolution with valid and invalid table/column references
    - Test error handling for missing tables or columns
    - _Requirements: 2.1, 2.2, 2.3, 2.4_
  
  - [ ]* 2.7 Write unit tests for parameter type resolution
    - Test LIKE pattern matching for parameters
    - Test resolution with valid and invalid references
    - Test error handling and logging
    - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [-] 3. Fix Multi-Instance Function Resolution
  - [x] 3.1 Update json_to_sqlite.py to store file_path for functions
    - Extract file_path from workspace.json for each function
    - Add file_path column to functions table
    - Store file_path during function insertion
    - _Requirements: 4.1, 4.2_
  
  - [x] 3.2 Update merge_resolved_types.py to use (function_name, file_path) for matching
    - Modify function matching logic to use both function_name and file_path
    - Update merge queries to match on both columns
    - Ensure resolved types are correctly associated with function instances
    - _Requirements: 4.4, 4.6_
  
  - [x] 3.3 Add query functions to query_db.py for function disambiguation
    - Implement `find_function_by_name_and_path(name, path)` function
    - Implement `find_all_function_instances(name)` function
    - Return results with file_path to distinguish instances
    - _Requirements: 4.7, 4.8, 4.9_
  
  - [ ]* 3.4 Write unit tests for multi-instance function resolution
    - Test that functions with same name in different files are stored correctly
    - Test that queries return correct function instance based on file_path
    - Test disambiguation logic
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [-] 4. Add Unresolved Types Query Command
  - [x] 4.1 Implement find_unresolved_types() in query_db.py
    - Query parameters table for unresolved LIKE references
    - Query returns table for unresolved LIKE references
    - Return results with function name, file path, type name, original type, and error reason
    - Support filtering by error type (missing table, missing column, invalid pattern)
    - Support pagination with limit and offset
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_
  
  - [x] 4.2 Add unresolved-types command to query.sh
    - Add shell command handler for `query.sh unresolved-types`
    - Support `--filter` parameter for error type filtering
    - Support `--limit` and `--offset` parameters for pagination
    - Format output as human-readable table with columns: function, file, type_name, original_type, error
    - Include summary line with total count and breakdown by error type
    - _Requirements: 5.7, 5.8, 5.9, 5.10, 5.11, 5.13, 5.14_
  
  - [ ]* 4.3 Write unit tests for unresolved types query
    - Test find_unresolved_types() returns correct results
    - Test filtering by error type
    - Test pagination
    - Test output formatting
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [x] 5. Add Data Consistency Validation
  - [x] 5.1 Implement validate_type_resolution() in query_db.py
    - Check for empty parameters in database
    - Check for missing file_path values in functions table
    - Check for unresolved LIKE references
    - Check for consistency between parameters and returns tables
    - Return validation report with status and issues
    - _Requirements: 6.7, 6.8, 6.9, 6.10, 6.11_
  
  - [x] 5.2 Add validation command to query.sh
    - Add shell command handler for `query.sh validate-types`
    - Display validation report with clear status indicators
    - Show specific issues found with details
    - _Requirements: 6.6_
  
  - [ ]* 5.3 Write unit tests for data consistency validation
    - Test detection of empty parameters
    - Test detection of missing file_path values
    - Test detection of unresolved LIKE references
    - _Requirements: 6.7, 6.8, 6.9, 6.10_

- [x] 6. Checkpoint - Verify all components work together
  - Ensure all tests pass
  - Verify empty parameters are filtered correctly
  - Verify LIKE references in both parameters and return types are resolved
  - Verify multi-instance functions are properly disambiguated
  - Verify unresolved types query returns correct results
  - Ask the user if questions arise.

- [x] 7. Integration and Performance Testing
  - [x] 7.1 Test with large codebase (10,000+ functions)
    - Verify type resolution completes within 5 seconds
    - Verify merge completes within 3 seconds
    - Verify memory usage stays under 500MB
    - _Requirements: 7.1, 7.2, 7.3, 7.4_
  
  - [x] 7.2 Test backward compatibility
    - Verify existing query commands work without modification
    - Verify output format of existing queries unchanged
    - Verify new columns have sensible defaults
    - _Requirements: 8.1, 8.2, 8.3, 8.4_
  
  - [ ]* 7.3 Write integration tests for end-to-end workflow
    - Test complete workflow from parsing to type resolution to querying
    - Test with sample codebase containing various LIKE patterns
    - Verify all requirements are met
    - _Requirements: 2.1, 3.1, 4.1, 5.1_

- [x] 8. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Implementation should follow the layered approach: parsing → resolution → disambiguation → querying
- All new code should maintain backward compatibility with existing scripts
- Performance requirements must be validated with actual codebase
