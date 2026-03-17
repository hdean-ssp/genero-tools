# Phase 1 API Enhancements - Tasks

## Overview

This document outlines the implementation tasks for Phase 1 API Enhancements. Tasks are organized by implementation phase (1a-1e) and follow the design roadmap. Each task includes acceptance criteria, file paths, and dependencies.

## Phase 1a: Batch Query Execution

### 1. Batch Query Handler Implementation

- [ ] 1.1 Create batch query handler module
  - [ ] 1.1.1 Implement `execute_batch_query()` function in Python API
  - [ ] 1.1.2 Add batch query request validation
  - [ ] 1.1.3 Add batch query response formatting
  - [ ] 1.1.4 Add timing information collection
  - **Files**: `scripts/batch_query_handler.py`
  - **Acceptance Criteria**: 
    - Accepts batch request with multiple queries
    - Executes queries sequentially in order
    - Returns results with timing information
    - Handles errors gracefully

- [ ] 1.2 Add batch-query command to shell interface
  - [ ] 1.2.1 Add batch-query command to query.sh
  - [ ] 1.2.2 Add JSON input file parsing
  - [ ] 1.2.3 Add output file writing capability
  - **Files**: `src/query.sh`
  - **Acceptance Criteria**:
    - Accepts JSON file as input
    - Supports --input and --output parameters
    - Returns batch results in JSON format

- [ ] 1.3 Write unit tests for batch query execution
  - [ ] 1.3.1 Test single query in batch
  - [ ] 1.3.2 Test multiple independent queries
  - [ ] 1.3.3 Test query ordering preservation
  - [ ] 1.3.4 Test error isolation (one query fails, others succeed)
  - [ ] 1.3.5 Test timing information accuracy
  - [ ] 1.3.6 Test batch query with all command types
  - **Files**: `tests/test_batch_query.py`
  - **Acceptance Criteria**:
    - All unit tests pass
    - Coverage > 90%
    - Tests cover success and error cases

- [ ] 1.4 Write property-based tests for batch query correctness
  - [ ] 1.4.1 Property 1: Batch Query Correctness (single connection, sequential execution, result ordering, error isolation, timing, performance)
  - **Files**: `tests/test_batch_query_properties.py`
  - **Acceptance Criteria**:
    - Property test passes with 100+ iterations
    - Validates all aspects of batch query correctness
    - Tests with various batch sizes (1-100 queries)

- [ ] 1.5 Integration tests for batch queries
  - [ ] 1.5.1 Test batch queries with real workspace.db
  - [ ] 1.5.2 Test batch queries with real modules.db
  - [ ] 1.5.3 Test batch queries with mixed command types
  - [ ] 1.5.4 Test batch query performance (3-5 queries < 100ms)
  - **Files**: `tests/test_batch_query_integration.py`
  - **Acceptance Criteria**:
    - All integration tests pass
    - Performance targets met
    - Works with real databases

- [ ] 1.6 Performance testing for batch queries
  - [ ] 1.6.1 Measure 3-5 query batch execution time
  - [ ] 1.6.2 Measure 100 query batch execution time
  - [ ] 1.6.3 Compare batch vs. sequential execution (target: 5x faster)
  - [ ] 1.6.4 Measure memory usage for 100 query batch
  - **Files**: `tests/test_batch_query_performance.py`
  - **Acceptance Criteria**:
    - Batch queries execute at least 5x faster than sequential
    - 3-5 query batch completes within 100ms
    - Memory usage acceptable for 100 query batch

## Phase 1b: Pagination Support

### 2. Pagination System Implementation

- [ ] 2.1 Create pagination module
  - [ ] 2.1.1 Implement `apply_pagination()` function
  - [ ] 2.1.2 Implement pagination metadata generation
  - [ ] 2.1.3 Implement sorting logic for deterministic ordering
  - [ ] 2.1.4 Implement total count calculation
  - **Files**: `scripts/pagination_handler.py`
  - **Acceptance Criteria**:
    - Respects limit parameter
    - Respects offset parameter
    - Returns accurate pagination metadata
    - Maintains consistent ordering

- [ ] 2.2 Add pagination parameters to shell interface
  - [ ] 2.2.1 Add --limit parameter to all query commands
  - [ ] 2.2.2 Add --offset parameter to all query commands
  - [ ] 2.2.3 Add --total-count flag to all query commands
  - [ ] 2.2.4 Add parameter validation
  - **Files**: `src/query.sh`
  - **Acceptance Criteria**:
    - All query commands accept pagination parameters
    - Parameters are optional with sensible defaults
    - Validation prevents invalid values

- [ ] 2.3 Write unit tests for pagination
  - [ ] 2.3.1 Test limit parameter
  - [ ] 2.3.2 Test offset parameter
  - [ ] 2.3.3 Test total_count calculation
  - [ ] 2.3.4 Test has_more flag
  - [ ] 2.3.5 Test sorting consistency
  - [ ] 2.3.6 Test edge cases (offset > total, limit = 0, etc.)
  - [ ] 2.3.7 Test default values
  - **Files**: `tests/test_pagination.py`
  - **Acceptance Criteria**:
    - All unit tests pass
    - Coverage > 90%
    - Edge cases handled correctly

- [ ] 2.4 Write property-based tests for pagination correctness
  - [ ] 2.4.1 Property 2: Pagination Correctness (limit, offset, metadata accuracy, consistent ordering, non-overlapping results, defaults)
  - **Files**: `tests/test_pagination_properties.py`
  - **Acceptance Criteria**:
    - Property test passes with 100+ iterations
    - Validates all pagination aspects
    - Tests with various result set sizes

- [ ] 2.5 Integration tests for pagination
  - [ ] 2.5.1 Test pagination on large result sets (10,000+ results)
  - [ ] 2.5.2 Test pagination consistency across multiple queries
  - [ ] 2.5.3 Test pagination with all query types
  - [ ] 2.5.4 Test pagination query performance (< 50ms)
  - **Files**: `tests/test_pagination_integration.py`
  - **Acceptance Criteria**:
    - All integration tests pass
    - Performance targets met
    - Works with large result sets

- [ ] 2.6 Performance testing for pagination
  - [ ] 2.6.1 Measure pagination query time (target: < 50ms)
  - [ ] 2.6.2 Measure total_count calculation time (target: < 50ms)
  - [ ] 2.6.3 Test with 10,000+ result sets
  - [ ] 2.6.4 Measure memory usage for large result sets
  - **Files**: `tests/test_pagination_performance.py`
  - **Acceptance Criteria**:
    - Pagination queries complete within 50ms
    - Total count calculation within 50ms
    - Memory usage acceptable for large result sets

## Phase 1c: Relationship Queries

### 3. Find Dependents in Module

- [ ] 3.1 Implement find-dependents-in-module algorithm
  - [ ] 3.1.1 Create relationship query module
  - [ ] 3.1.2 Implement module validation
  - [ ] 3.1.3 Implement function validation
  - [ ] 3.1.4 Implement dependent finding logic
  - [ ] 3.1.5 Implement result sorting
  - **Files**: `scripts/relationship_queries.py`
  - **Acceptance Criteria**:
    - Returns only functions in specified module
    - Returns only functions that call target function
    - Results sorted by name
    - Handles missing module/function errors

- [ ] 3.2 Add find-dependents-in-module command to shell interface
  - [ ] 3.2.1 Add command to query.sh
  - [ ] 3.2.2 Add parameter validation
  - [ ] 3.2.3 Add pagination support
  - **Files**: `src/query.sh`
  - **Acceptance Criteria**:
    - Command accepts module and function names
    - Supports pagination parameters
    - Returns function objects with signatures

- [ ] 3.3 Write unit tests for find-dependents-in-module
  - [ ] 3.3.1 Test with various module/function combinations
  - [ ] 3.3.2 Test error cases (missing module, missing function)
  - [ ] 3.3.3 Test pagination support
  - [ ] 3.3.4 Test result sorting
  - **Files**: `tests/test_find_dependents_in_module.py`
  - **Acceptance Criteria**:
    - All unit tests pass
    - Coverage > 90%
    - Error cases handled correctly

### 4. Find Call Chain

- [ ] 4.1 Implement find-call-chain algorithm
  - [ ] 4.1.1 Implement BFS path finding
  - [ ] 4.1.2 Implement cycle detection
  - [ ] 4.1.3 Implement depth limiting
  - [ ] 4.1.4 Implement path formatting
  - **Files**: `scripts/relationship_queries.py`
  - **Acceptance Criteria**:
    - Finds valid call paths from source to target
    - Limits depth to max_depth parameter
    - Avoids cycles
    - Returns paths as ordered lists

- [ ] 4.2 Add find-call-chain command to shell interface
  - [ ] 4.2.1 Add command to query.sh
  - [ ] 4.2.2 Add max-depth parameter support
  - [ ] 4.2.3 Add pagination support
  - **Files**: `src/query.sh`
  - **Acceptance Criteria**:
    - Command accepts source and target function names
    - Supports max-depth parameter (default 5, max 20)
    - Supports pagination parameters

- [ ] 4.3 Write unit tests for find-call-chain
  - [ ] 4.3.1 Test with different depths
  - [ ] 4.3.2 Test with no path (verify empty results)
  - [ ] 4.3.3 Test with depth exceeded (verify partial paths)
  - [ ] 4.3.4 Test cycle detection
  - [ ] 4.3.5 Test pagination support
  - **Files**: `tests/test_find_call_chain.py`
  - **Acceptance Criteria**:
    - All unit tests pass
    - Coverage > 90%
    - Edge cases handled correctly

### 5. Find Common Callers

- [ ] 5.1 Implement find-common-callers algorithm
  - [ ] 5.1.1 Implement caller intersection logic
  - [ ] 5.1.2 Implement validation for 2+ functions
  - [ ] 5.1.3 Implement result sorting
  - **Files**: `scripts/relationship_queries.py`
  - **Acceptance Criteria**:
    - Returns only functions that call all specified functions
    - Validates at least 2 functions specified
    - Results sorted by name

- [ ] 5.2 Add find-common-callers command to shell interface
  - [ ] 5.2.1 Add command to query.sh
  - [ ] 5.2.2 Add parameter validation
  - [ ] 5.2.3 Add pagination support
  - **Files**: `src/query.sh`
  - **Acceptance Criteria**:
    - Command accepts 2+ function names
    - Supports pagination parameters
    - Returns function objects with signatures

- [ ] 5.3 Write unit tests for find-common-callers
  - [ ] 5.3.1 Test with 2+ functions
  - [ ] 5.3.2 Test error cases (< 2 functions, missing functions)
  - [ ] 5.3.3 Test pagination support
  - [ ] 5.3.4 Test result sorting
  - **Files**: `tests/test_find_common_callers.py`
  - **Acceptance Criteria**:
    - All unit tests pass
    - Coverage > 90%
    - Error cases handled correctly

### 6. Relationship Query Integration

- [ ] 6.1 Write property-based tests for relationship query correctness
  - [ ] 6.1.1 Property 3: Relationship Query Correctness (find-dependents-in-module, find-call-chain, find-common-callers)
  - **Files**: `tests/test_relationship_queries_properties.py`
  - **Acceptance Criteria**:
    - Property test passes with 100+ iterations
    - Validates all relationship query aspects
    - Tests with various call graphs

- [ ] 6.2 Integration tests for relationship queries
  - [ ] 6.2.1 Test find-dependents-in-module with real call graphs
  - [ ] 6.2.2 Test find-call-chain with complex call graphs
  - [ ] 6.2.3 Test find-common-callers with multiple functions
  - [ ] 6.2.4 Test relationship queries with pagination
  - **Files**: `tests/test_relationship_queries_integration.py`
  - **Acceptance Criteria**:
    - All integration tests pass
    - Works with real databases
    - Performance targets met

- [ ] 6.3 Performance testing for relationship queries
  - [ ] 6.3.1 Measure find-dependents-in-module time (target: < 50ms)
  - [ ] 6.3.2 Measure find-call-chain time (target: < 200ms)
  - [ ] 6.3.3 Measure find-common-callers time (target: < 100ms)
  - [ ] 6.3.4 Test with complex call graphs
  - **Files**: `tests/test_relationship_queries_performance.py`
  - **Acceptance Criteria**:
    - All performance targets met
    - Memory usage acceptable
    - Scales to 6M+ LOC codebases

## Phase 1d: Error Handling

### 7. Error Handling Framework

- [ ] 7.1 Create error handling module
  - [ ] 7.1.1 Define error codes (E001-E009)
  - [ ] 7.1.2 Implement error response formatting
  - [ ] 7.1.3 Implement error code mapping
  - [ ] 7.1.4 Implement error diagnostics
  - **Files**: `scripts/error_handler.py`
  - **Acceptance Criteria**:
    - All error codes defined
    - Error responses include code, message, suggestion, query, timestamp
    - Error codes consistent across invocations

- [ ] 7.2 Add error handling to shell interface
  - [ ] 7.2.1 Add error response formatting to query.sh
  - [ ] 7.2.2 Add error code mapping
  - [ ] 7.2.3 Add error diagnostics
  - **Files**: `src/query.sh`
  - **Acceptance Criteria**:
    - All errors return structured response
    - Error codes match E001-E009 mapping
    - Error messages are helpful

- [ ] 7.3 Implement validate-database command
  - [ ] 7.3.1 Check all required tables exist
  - [ ] 7.3.2 Check all required indexes exist
  - [ ] 7.3.3 Check foreign key relationships
  - [ ] 7.3.4 Return validation report
  - **Files**: `scripts/database_validator.py`, `src/query.sh`
  - **Acceptance Criteria**:
    - Validates all required tables
    - Validates all required indexes
    - Validates foreign key relationships
    - Returns detailed report

- [ ] 7.4 Implement get-error-details command
  - [ ] 7.4.1 Return error code description
  - [ ] 7.4.2 Return common causes
  - [ ] 7.4.3 Return suggested resolutions
  - [ ] 7.4.4 Return examples
  - **Files**: `scripts/error_handler.py`, `src/query.sh`
  - **Acceptance Criteria**:
    - Returns all required information
    - Examples are relevant
    - Suggestions are helpful

- [ ] 7.5 Write unit tests for error handling
  - [ ] 7.5.1 Test each error code (E001-E009)
  - [ ] 7.5.2 Test error response format
  - [ ] 7.5.3 Test error message quality
  - [ ] 7.5.4 Test error suggestion quality
  - [ ] 7.5.5 Test error query field
  - [ ] 7.5.6 Test error timestamp
  - **Files**: `tests/test_error_handling.py`
  - **Acceptance Criteria**:
    - All unit tests pass
    - Coverage > 90%
    - All error codes tested

- [ ] 7.6 Write property-based tests for error handling correctness
  - [ ] 7.6.1 Property 4: Error Handling Correctness (structured response, correct codes, consistency, validation, diagnostics)
  - **Files**: `tests/test_error_handling_properties.py`
  - **Acceptance Criteria**:
    - Property test passes with 100+ iterations
    - Validates all error handling aspects
    - Tests all error codes

- [ ] 7.7 Integration tests for error handling
  - [ ] 7.7.1 Test error handling with real databases
  - [ ] 7.7.2 Test validate-database with various database states
  - [ ] 7.7.3 Test get-error-details for all error codes
  - **Files**: `tests/test_error_handling_integration.py`
  - **Acceptance Criteria**:
    - All integration tests pass
    - Works with real databases
    - Error handling is robust

## Phase 1e: Integration & Performance

### 8. Database Schema Optimization

- [ ] 8.1 Add performance indexes
  - [ ] 8.1.1 Create index on functions.name
  - [ ] 8.1.2 Create index on functions.file
  - [ ] 8.1.3 Create index on calls.caller_id
  - [ ] 8.1.4 Create index on calls.callee_name
  - [ ] 8.1.5 Create index on module_files.module_id
  - [ ] 8.1.6 Create index on module_files.file_path
  - [ ] 8.1.7 Create composite indexes
  - **Files**: `scripts/create_indexes.py`
  - **Acceptance Criteria**:
    - All indexes created successfully
    - Indexes improve query performance
    - No duplicate indexes

### 9. Backward Compatibility Validation

- [ ] 9.1 Write property-based tests for backward compatibility
  - [ ] 9.1.1 Property 5: Backward Compatibility (existing commands, response format, defaults, batch support, no modifications)
  - **Files**: `tests/test_backward_compatibility_properties.py`
  - **Acceptance Criteria**:
    - Property test passes with 100+ iterations
    - Validates all backward compatibility aspects
    - Tests all existing commands

- [ ] 9.2 Integration tests for backward compatibility
  - [ ] 9.2.1 Test all existing commands work unchanged
  - [ ] 9.2.2 Test response format unchanged
  - [ ] 9.2.3 Test default behavior unchanged
  - [ ] 9.2.4 Test with existing scripts
  - **Files**: `tests/test_backward_compatibility_integration.py`
  - **Acceptance Criteria**:
    - All integration tests pass
    - No breaking changes
    - Existing code continues to work

### 10. Vim Plugin Integration

- [ ] 10.1 Integration tests for vim plugin use cases
  - [ ] 10.1.1 Test hover information batch query
  - [ ] 10.1.2 Test search results pagination
  - [ ] 10.1.3 Test navigation queries
  - [ ] 10.1.4 Test error handling in plugin context
  - **Files**: `tests/test_vim_plugin_integration.py`
  - **Acceptance Criteria**:
    - All vim plugin use cases work
    - Performance targets met
    - Error handling is robust

### 11. Performance Validation

- [ ] 11.1 Write property-based tests for performance requirements
  - [ ] 11.1.1 Property 6: Performance Requirements (batch queries, pagination, relationship queries, memory usage)
  - **Files**: `tests/test_performance_properties.py`
  - **Acceptance Criteria**:
    - Property test passes with 100+ iterations
    - Validates all performance aspects
    - Tests with various codebase sizes

- [ ] 11.2 Comprehensive performance testing
  - [ ] 11.2.1 Measure batch query performance (3-5 queries < 100ms)
  - [ ] 11.2.2 Measure pagination performance (< 50ms)
  - [ ] 11.2.3 Measure relationship query performance
  - [ ] 11.2.4 Measure memory usage
  - [ ] 11.2.5 Test with 6M+ LOC codebase simulation
  - **Files**: `tests/test_comprehensive_performance.py`
  - **Acceptance Criteria**:
    - All performance targets met
    - Memory usage acceptable
    - Scales to 6M+ LOC codebases

### 12. Documentation

- [ ] 12.1 Create API documentation
  - [ ] 12.1.1 Document batch-query command
  - [ ] 12.1.2 Document pagination parameters
  - [ ] 12.1.3 Document relationship queries
  - [ ] 12.1.4 Document error codes
  - [ ] 12.1.5 Document validate-database command
  - [ ] 12.1.6 Document get-error-details command
  - **Files**: `docs/API_PHASE_1_ENHANCEMENTS.md`
  - **Acceptance Criteria**:
    - All commands documented
    - All parameters documented
    - Examples provided

- [ ] 12.2 Create usage examples
  - [ ] 12.2.1 Create batch query examples
  - [ ] 12.2.2 Create pagination examples
  - [ ] 12.2.3 Create relationship query examples
  - [ ] 12.2.4 Create error handling examples
  - **Files**: `docs/PHASE_1_EXAMPLES.md`
  - **Acceptance Criteria**:
    - Examples are clear and runnable
    - Examples cover typical use cases
    - Examples show best practices

- [ ] 12.3 Create migration guide
  - [ ] 12.3.1 Document new features
  - [ ] 12.3.2 Document backward compatibility
  - [ ] 12.3.3 Document upgrade path
  - [ ] 12.3.4 Document performance improvements
  - **Files**: `docs/PHASE_1_MIGRATION_GUIDE.md`
  - **Acceptance Criteria**:
    - Guide is clear and comprehensive
    - Upgrade path is straightforward
    - Benefits are clearly explained

- [ ] 12.4 Create performance tuning guide
  - [ ] 12.4.1 Document index usage
  - [ ] 12.4.2 Document query optimization
  - [ ] 12.4.3 Document caching strategies
  - [ ] 12.4.4 Document scaling recommendations
  - **Files**: `docs/PHASE_1_PERFORMANCE_TUNING.md`
  - **Acceptance Criteria**:
    - Guide is practical and actionable
    - Recommendations are evidence-based
    - Examples are provided

### 13. Final Integration & Testing

- [ ] 13.1 End-to-end integration tests
  - [ ] 13.1.1 Test all features together
  - [ ] 13.1.2 Test with real vim plugin
  - [ ] 13.1.3 Test with real codebases
  - [ ] 13.1.4 Test error scenarios
  - **Files**: `tests/test_e2e_integration.py`
  - **Acceptance Criteria**:
    - All end-to-end tests pass
    - All features work together
    - Real-world scenarios work

- [ ] 13.2 Regression testing
  - [ ] 13.2.1 Run all existing tests
  - [ ] 13.2.2 Verify no regressions
  - [ ] 13.2.3 Verify backward compatibility
  - **Files**: `tests/run_all_tests.sh`
  - **Acceptance Criteria**:
    - All tests pass
    - No regressions detected
    - Backward compatibility maintained

- [ ] 13.3 Final performance validation
  - [ ] 13.3.1 Verify all performance targets met
  - [ ] 13.3.2 Verify memory usage acceptable
  - [ ] 13.3.3 Verify scalability to 6M+ LOC
  - **Files**: `tests/test_final_performance.py`
  - **Acceptance Criteria**:
    - All performance targets met
    - Memory usage acceptable
    - Scales as expected

- [ ] 13.4 Release preparation
  - [ ] 13.4.1 Update version numbers
  - [ ] 13.4.2 Update changelog
  - [ ] 13.4.3 Create release notes
  - [ ] 13.4.4 Tag release
  - **Files**: `VERSION`, `CHANGELOG.md`, `RELEASE_NOTES.md`
  - **Acceptance Criteria**:
    - Version numbers updated
    - Changelog complete
    - Release notes comprehensive

## Task Dependencies

```
Phase 1a (Batch Query Execution)
├── 1.1 Batch Query Handler Implementation
├── 1.2 Add batch-query command
├── 1.3 Unit tests
├── 1.4 Property-based tests
├── 1.5 Integration tests
└── 1.6 Performance tests

Phase 1b (Pagination Support)
├── 2.1 Pagination Module
├── 2.2 Add pagination parameters
├── 2.3 Unit tests
├── 2.4 Property-based tests
├── 2.5 Integration tests
└── 2.6 Performance tests

Phase 1c (Relationship Queries)
├── 3.1 Find Dependents in Module
│   ├── 3.1 Implementation
│   ├── 3.2 Shell command
│   └── 3.3 Unit tests
├── 4.1 Find Call Chain
│   ├── 4.1 Implementation
│   ├── 4.2 Shell command
│   └── 4.3 Unit tests
├── 5.1 Find Common Callers
│   ├── 5.1 Implementation
│   ├── 5.2 Shell command
│   └── 5.3 Unit tests
├── 6.1 Property-based tests
├── 6.2 Integration tests
└── 6.3 Performance tests

Phase 1d (Error Handling)
├── 7.1 Error Handling Framework
├── 7.2 Add error handling to shell
├── 7.3 Implement validate-database
├── 7.4 Implement get-error-details
├── 7.5 Unit tests
├── 7.6 Property-based tests
└── 7.7 Integration tests

Phase 1e (Integration & Performance)
├── 8.1 Database Schema Optimization
├── 9.1 Backward Compatibility Validation
├── 10.1 Vim Plugin Integration
├── 11.1 Performance Validation
├── 12.1 Documentation
├── 13.1 End-to-end Integration Tests
├── 13.2 Regression Testing
├── 13.3 Final Performance Validation
└── 13.4 Release Preparation
```

## Complexity Estimates

| Task | Complexity | Estimated Hours |
|------|-----------|-----------------|
| 1.1 Batch Query Handler | Medium | 8 |
| 1.2 Shell Command | Low | 4 |
| 1.3-1.6 Testing | Medium | 12 |
| 2.1 Pagination Module | Medium | 8 |
| 2.2 Shell Parameters | Low | 4 |
| 2.3-2.6 Testing | Medium | 12 |
| 3.1-3.3 Find Dependents | Medium | 12 |
| 4.1-4.3 Find Call Chain | High | 16 |
| 5.1-5.3 Find Common Callers | Medium | 12 |
| 6.1-6.3 Relationship Testing | Medium | 12 |
| 7.1-7.7 Error Handling | Medium | 16 |
| 8.1 Database Optimization | Low | 4 |
| 9.1-9.2 Backward Compatibility | Low | 8 |
| 10.1 Vim Plugin Integration | Medium | 8 |
| 11.1-11.2 Performance | Medium | 12 |
| 12.1-12.4 Documentation | Low | 12 |
| 13.1-13.4 Final Integration | Medium | 16 |
| **Total** | | **172 hours** |

## Testing Summary

### Unit Tests
- Batch Query: 6 test cases
- Pagination: 7 test cases
- Find Dependents: 4 test cases
- Find Call Chain: 5 test cases
- Find Common Callers: 4 test cases
- Error Handling: 6 test cases
- **Total Unit Tests**: 32 test cases

### Property-Based Tests
- Property 1: Batch Query Correctness
- Property 2: Pagination Correctness
- Property 3: Relationship Query Correctness
- Property 4: Error Handling Correctness
- Property 5: Backward Compatibility
- Property 6: Performance Requirements
- **Total Properties**: 6 properties

### Integration Tests
- Batch Query Integration: 4 test cases
- Pagination Integration: 4 test cases
- Relationship Query Integration: 4 test cases
- Error Handling Integration: 3 test cases
- Backward Compatibility Integration: 4 test cases
- Vim Plugin Integration: 4 test cases
- End-to-End Integration: 4 test cases
- **Total Integration Tests**: 27 test cases

### Performance Tests
- Batch Query Performance: 4 test cases
- Pagination Performance: 4 test cases
- Relationship Query Performance: 4 test cases
- Performance Requirements: 8 test cases
- Final Performance: 3 test cases
- **Total Performance Tests**: 23 test cases

**Total Test Cases**: 82 test cases + 6 property-based tests
