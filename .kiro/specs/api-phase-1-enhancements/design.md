# Phase 1 API Enhancements - Design Document

## Overview

Phase 1 API Enhancements extends genero-tools with four major capabilities: batch query execution, pagination support, complex relationship queries, and structured error handling. These enhancements enable 10x performance improvements and support for massive codebases (6M+ LOC) while maintaining full backward compatibility.

The design introduces:
- **Batch Query API**: Execute multiple independent queries in a single database connection
- **Pagination System**: Return large result sets in manageable chunks with metadata
- **Relationship Query Algorithms**: Complex traversals (find-dependents-in-module, find-call-chain, find-common-callers)
- **Error Handling Framework**: Structured error codes (E001-E009) with diagnostic information

## Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────────────┐
│                    Query Interface Layer                     │
│  (query.sh / Python API / Batch Query Handler)              │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│              Query Execution Engine                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Single Query │  │ Batch Query  │  │ Relationship │      │
│  │  Executor    │  │  Executor    │  │   Executor   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│           Pagination & Result Formatting                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Limit/Offset │  │ Sorting      │  │ Metadata     │      │
│  │  Application │  │  Engine      │  │  Generator   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│              Error Handling Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Error Code   │  │ Validation   │  │ Diagnostics  │      │
│  │  Mapping     │  │  Engine      │  │  Generator   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│         SQLite Database Layer                               │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │ workspace.db │  │ modules.db   │                        │
│  └──────────────┘  └──────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

### Key Design Principles

1. **Single Database Connection**: Batch queries use one connection for all queries to minimize overhead
2. **Sequential Execution**: Queries execute in order to ensure consistency and predictable behavior
3. **Deterministic Ordering**: All queries return results in consistent order for reliable pagination
4. **Backward Compatibility**: All new features are optional; existing code works unchanged
5. **Error Isolation**: Errors in one query don't affect others in a batch
6. **Performance First**: Optimized for 6M+ LOC codebases with sub-100ms latency targets

## Components and Interfaces

### 1. Batch Query Handler

**Purpose**: Execute multiple queries in a single database connection

**Input Format** (JSON):
```json
{
  "queries": [
    {
      "id": "query_1",
      "command": "find-function",
      "args": ["my_function"]
    },
    {
      "id": "query_2",
      "command": "find-function-dependencies",
      "args": ["my_function"]
    }
  ]
}
```

**Output Format** (JSON):
```json
{
  "batch_id": "batch_20240115_001",
  "status": "success",
  "total_time_ms": 45,
  "results": [
    {
      "query_id": "query_1",
      "status": "success",
      "time_ms": 12,
      "data": [...]
    },
    {
      "query_id": "query_2",
      "status": "success",
      "time_ms": 33,
      "data": [...]
    }
  ]
}
```

**Python API**:
```python
def execute_batch_query(batch_request: Dict, 
                       signatures_db: str, 
                       modules_db: str) -> Dict:
    """Execute multiple queries in a single batch.
    
    Args:
        batch_request: Dict with 'queries' array
        signatures_db: Path to workspace.db
        modules_db: Path to modules.db
    
    Returns:
        Dict with batch results and timing information
    """
```

**Shell Interface**:
```bash
query.sh batch-query <json_file>
query.sh batch-query --input <json_file> --output <output_file>
```

### 2. Pagination System

**Purpose**: Return large result sets in manageable chunks

**Parameters**:
- `--limit N`: Maximum results to return (default: 100, max: 10000)
- `--offset N`: Number of results to skip (default: 0)
- `--total-count`: Include total count in response (default: false)

**Pagination Metadata** (added to all responses):
```json
{
  "pagination": {
    "limit": 100,
    "offset": 0,
    "total_count": 2543,
    "has_more": true,
    "returned_count": 100
  }
}
```

**Sorting Strategy**:
- Functions: sorted by name (primary), then file path (secondary)
- Modules: sorted by name
- Dependencies: sorted by name
- Dependents: sorted by name

**Python API**:
```python
def apply_pagination(results: List[Dict], 
                    limit: int = 100, 
                    offset: int = 0,
                    calculate_total: bool = False) -> Dict:
    """Apply pagination to results.
    
    Returns:
        Dict with 'data' (paginated results) and 'pagination' metadata
    """
```

### 3. Relationship Query Algorithms

#### 3.1 Find Dependents in Module

**Purpose**: Find all functions in a module that call a specific function

**Algorithm**:
```
1. Validate module exists (error E005 if not)
2. Validate function exists (error E004 if not)
3. Get all functions in module
4. For each function, check if it calls the target function
5. Return matching functions sorted by name
```

**SQL Query**:
```sql
SELECT DISTINCT f.* FROM functions f
JOIN module_files mf ON f.file_id = mf.file_id
WHERE mf.module_id = (SELECT id FROM modules WHERE name = ?)
  AND f.id IN (
    SELECT caller_id FROM calls 
    WHERE callee_name = ?
  )
ORDER BY f.name
```

**Python API**:
```python
def find_dependents_in_module(modules_db: str,
                             signatures_db: str,
                             module_name: str,
                             function_name: str,
                             limit: int = 100,
                             offset: int = 0) -> Dict:
    """Find functions in module that call a function."""
```

#### 3.2 Find Call Chain

**Purpose**: Find all call paths from one function to another

**Algorithm**:
```
1. Validate both functions exist (error E004 if not)
2. Use BFS to find all paths from source to target
3. Limit depth to max_depth parameter (default 5, max 20)
4. Return paths as ordered lists of function names
5. Support pagination on results
```

**Pseudocode**:
```
function find_call_chain(source, target, max_depth):
    paths = []
    queue = [(source, [source], 0)]
    
    while queue not empty:
        current, path, depth = queue.pop()
        
        if current == target:
            paths.append(path)
            continue
        
        if depth >= max_depth:
            continue
        
        for callee in get_callees(current):
            if callee not in path:  # Avoid cycles
                queue.append((callee, path + [callee], depth + 1))
    
    return paths
```

**Python API**:
```python
def find_call_chain(signatures_db: str,
                   source_function: str,
                   target_function: str,
                   max_depth: int = 5,
                   limit: int = 100,
                   offset: int = 0) -> Dict:
    """Find call paths between two functions."""
```

#### 3.3 Find Common Callers

**Purpose**: Find all functions that call all specified functions

**Algorithm**:
```
1. Validate at least 2 functions specified (error E003 if not)
2. Validate all functions exist (error E004 if not)
3. Get callers of first function
4. Intersect with callers of second function
5. Continue intersection for remaining functions
6. Return common callers sorted by name
```

**SQL Query**:
```sql
SELECT DISTINCT f.* FROM functions f
WHERE f.id IN (
  SELECT caller_id FROM calls WHERE callee_name = ?
  INTERSECT
  SELECT caller_id FROM calls WHERE callee_name = ?
  -- Repeat INTERSECT for each additional function
)
ORDER BY f.name
```

**Python API**:
```python
def find_common_callers(signatures_db: str,
                       function_names: List[str],
                       limit: int = 100,
                       offset: int = 0) -> Dict:
    """Find functions that call all specified functions."""
```

## Data Models

### Query Request Format

```python
@dataclass
class QueryRequest:
    id: str                    # Unique identifier for this query
    command: str              # Command name (e.g., "find-function")
    args: List[str]           # Command arguments
    options: Dict[str, Any]   # Optional parameters (limit, offset, etc.)
```

### Query Response Format

```python
@dataclass
class QueryResponse:
    query_id: str
    status: str               # "success" or "error"
    time_ms: float
    data: Optional[List[Dict]]
    error: Optional[ErrorInfo]
    pagination: Optional[PaginationMetadata]
```

### Function Object

```python
@dataclass
class FunctionObject:
    id: int
    name: str
    file: str
    line_start: int
    line_end: int
    signature: str
    loc: int
    complexity: int
    parameters: List[Parameter]
    returns: List[Return]
```

### Pagination Metadata

```python
@dataclass
class PaginationMetadata:
    limit: int
    offset: int
    total_count: int
    has_more: bool
    returned_count: int
```

### Error Information

```python
@dataclass
class ErrorInfo:
    code: str                 # E001-E009
    message: str
    suggestion: str
    query: str
    timestamp: str
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Batch Query Atomicity

For any batch query request with N queries, either all queries execute successfully and return results, or individual query failures are isolated and reported without affecting other queries in the batch.

**Validates: Requirements 1.8, 1.10**

### Property 2: Batch Query Ordering

For any batch query request, the order of results in the response matches the order of queries in the input request.

**Validates: Requirements 1.7**

### Property 3: Pagination Consistency

For any query with pagination parameters, executing the same query with different limit/offset combinations should return consistent, non-overlapping result sets that together contain all results.

**Validates: Requirements 2.7, 2.9**

### Property 4: Pagination Metadata Accuracy

For any paginated query result, the pagination metadata (limit, offset, total_count, has_more) accurately reflects the actual results returned.

**Validates: Requirements 2.6, 2.8**

### Property 5: Deterministic Ordering

For any query executed multiple times without modification, results are returned in the same order.

**Validates: Requirements 2.7**

### Property 6: Find Dependents in Module Correctness

For any module and function, all returned results are functions that (1) exist in the specified module, and (2) call the specified function.

**Validates: Requirements 3.2, 3.3**

### Property 7: Find Call Chain Completeness

For any two functions with a call path, find-call-chain returns at least one valid path from source to target, or returns empty if no path exists within max_depth.

**Validates: Requirements 3.8, 3.12, 3.13**

### Property 8: Find Common Callers Correctness

For any set of functions, all returned results are functions that call every function in the input set.

**Validates: Requirements 3.15, 3.16**

### Property 9: Error Code Consistency

For any error condition, the returned error code matches the defined mapping (E001-E009) and is consistent across multiple invocations of the same error condition.

**Validates: Requirements 4.1-4.10**

### Property 10: Backward Compatibility

For any existing query command executed without new parameters, the response format and data are identical to the current implementation.

**Validates: Requirements 1.14, 1.15, 2.14, 2.15, 8.1-8.7**

## Error Handling

### Error Code Definitions

| Code | Condition | HTTP Status | Recovery |
|------|-----------|-------------|----------|
| E001 | Database not found | 404 | Create database with create-dbs command |
| E002 | Database corrupted | 500 | Rebuild database from JSON source |
| E003 | Query syntax error | 400 | Check command syntax and arguments |
| E004 | Function not found | 404 | Verify function name exists in codebase |
| E005 | Module not found | 404 | Verify module name exists in codebase |
| E006 | Invalid parameter | 400 | Check parameter values and types |
| E007 | Database connection error | 500 | Check database file permissions |
| E008 | Query timeout | 504 | Reduce result set size or increase timeout |
| E009 | Insufficient permissions | 403 | Check file permissions on database |

### Error Response Format

```json
{
  "status": "error",
  "error": {
    "code": "E004",
    "message": "Function 'my_function' not found in database",
    "suggestion": "Use 'search-functions' to find similar function names",
    "query": "find-function my_function",
    "timestamp": "2024-01-15T10:30:45Z"
  }
}
```

### Database Validation

The `validate-database` command checks:
1. All required tables exist (functions, calls, modules, module_files, etc.)
2. All required indexes exist
3. Foreign key relationships are valid
4. No orphaned records
5. Database file is readable and writable

### Error Diagnostics

The `get-error-details` command returns:
```json
{
  "code": "E004",
  "description": "Function not found",
  "common_causes": [
    "Function name is misspelled",
    "Function is in a different module",
    "Function was removed in recent changes"
  ],
  "suggested_resolutions": [
    "Use search-functions to find similar names",
    "Check function name in source code",
    "Regenerate database if codebase changed"
  ],
  "examples": [
    "query.sh find-function nonexistent_func"
  ]
}
```

## Testing Strategy

### Unit Testing Approach

**Batch Query Tests**:
- Test single query in batch
- Test multiple independent queries
- Test query ordering preservation
- Test error isolation (one query fails, others succeed)
- Test timing information accuracy

**Pagination Tests**:
- Test limit parameter
- Test offset parameter
- Test total_count calculation
- Test has_more flag accuracy
- Test edge cases (offset > total, limit = 0, etc.)
- Test sorting consistency

**Relationship Query Tests**:
- Test find-dependents-in-module with various module/function combinations
- Test find-call-chain with different depths
- Test find-common-callers with 2+ functions
- Test error cases (missing module, missing function, etc.)

**Error Handling Tests**:
- Test each error code (E001-E009)
- Test error response format
- Test error diagnostics
- Test database validation

### Integration Testing Approach

**Batch Query Integration**:
- Test batch queries with real workspace.db
- Test batch queries with real modules.db
- Test batch queries with mixed command types
- Test performance with 3-5 query batches

**Pagination Integration**:
- Test pagination on large result sets (10,000+ results)
- Test pagination consistency across multiple queries
- Test pagination with relationship queries

**Relationship Query Integration**:
- Test find-dependents-in-module with real call graphs
- Test find-call-chain with complex call graphs
- Test find-common-callers with multiple functions

**Vim Plugin Integration**:
- Test hover information batch query
- Test search results pagination
- Test navigation queries

### Performance Testing Approach

**Batch Query Performance**:
- Measure 3-5 query batch execution time (target: <100ms)
- Measure 100 query batch execution time
- Compare batch vs. sequential execution (target: 5x faster)

**Pagination Performance**:
- Measure pagination query time (target: <50ms)
- Measure total_count calculation time (target: <50ms)
- Test with 10,000+ result sets

**Relationship Query Performance**:
- Measure find-dependents-in-module time (target: <50ms)
- Measure find-call-chain time (target: <200ms)
- Measure find-common-callers time (target: <100ms)

### Test Configuration

**Property-Based Testing**:
- Minimum 100 iterations per property test
- Use hypothesis library for Python
- Tag format: `Feature: api-phase-1-enhancements, Property {number}: {property_text}`

**Unit Test Framework**:
- pytest for Python tests
- Fixtures for database setup/teardown
- Mock databases for isolated testing

**Integration Test Framework**:
- Real databases from test fixtures
- Sample codebases (small, medium, large)
- Performance benchmarking with timeit

## Database Schema Changes

### New Indexes

To support efficient pagination and relationship queries, add these indexes:

```sql
-- Improve pagination performance
CREATE INDEX IF NOT EXISTS idx_functions_name ON functions(name);
CREATE INDEX IF NOT EXISTS idx_functions_file ON functions(file);

-- Improve relationship query performance
CREATE INDEX IF NOT EXISTS idx_calls_caller_id ON calls(caller_id);
CREATE INDEX IF NOT EXISTS idx_calls_callee_name ON calls(callee_name);

-- Improve module queries
CREATE INDEX IF NOT EXISTS idx_module_files_module_id ON module_files(module_id);
CREATE INDEX IF NOT EXISTS idx_module_files_file_path ON module_files(file_path);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_calls_caller_callee ON calls(caller_id, callee_name);
```

### Backward Compatibility

- No schema changes required
- New indexes are additive only
- Existing queries continue to work
- Database file format unchanged

## API Design

### Shell Command Interface

```bash
# Batch queries
query.sh batch-query <json_file>
query.sh batch-query --input <json_file> --output <output_file>

# Pagination parameters (work with all commands)
query.sh find-function my_func --limit 50 --offset 0 --total-count

# Relationship queries
query.sh find-dependents-in-module core validate_input
query.sh find-call-chain func1 func2 --max-depth 10
query.sh find-common-callers func1 func2 func3

# Error handling
query.sh validate-database
query.sh get-error-details E004
```

### Python API Functions

```python
# Batch queries
def execute_batch_query(batch_request: Dict, 
                       signatures_db: str, 
                       modules_db: str) -> Dict

# Pagination
def apply_pagination(results: List[Dict], 
                    limit: int = 100, 
                    offset: int = 0,
                    calculate_total: bool = False) -> Dict

# Relationship queries
def find_dependents_in_module(modules_db: str,
                             signatures_db: str,
                             module_name: str,
                             function_name: str,
                             limit: int = 100,
                             offset: int = 0) -> Dict

def find_call_chain(signatures_db: str,
                   source_function: str,
                   target_function: str,
                   max_depth: int = 5,
                   limit: int = 100,
                   offset: int = 0) -> Dict

def find_common_callers(signatures_db: str,
                       function_names: List[str],
                       limit: int = 100,
                       offset: int = 0) -> Dict

# Error handling
def validate_database(signatures_db: str, 
                     modules_db: str) -> Dict

def get_error_details(error_code: str) -> Dict
```

### JSON Request/Response Formats

**Batch Query Request**:
```json
{
  "queries": [
    {
      "id": "q1",
      "command": "find-function",
      "args": ["my_function"]
    },
    {
      "id": "q2",
      "command": "find-function-dependencies",
      "args": ["my_function"],
      "options": {
        "limit": 50,
        "offset": 0
      }
    }
  ]
}
```

**Batch Query Response**:
```json
{
  "batch_id": "batch_20240115_001",
  "status": "success",
  "total_time_ms": 45,
  "results": [
    {
      "query_id": "q1",
      "status": "success",
      "time_ms": 12,
      "data": [...],
      "pagination": {
        "limit": 100,
        "offset": 0,
        "total_count": 1,
        "has_more": false,
        "returned_count": 1
      }
    },
    {
      "query_id": "q2",
      "status": "success",
      "time_ms": 33,
      "data": [...],
      "pagination": {
        "limit": 50,
        "offset": 0,
        "total_count": 5,
        "has_more": false,
        "returned_count": 5
      }
    }
  ]
}
```

## Performance Optimization

### Query Optimization Strategies

1. **Index Usage**: Leverage indexes on frequently queried columns (name, file, caller_id, callee_name)
2. **Query Planning**: Use EXPLAIN QUERY PLAN to verify index usage
3. **Connection Pooling**: Reuse database connections for batch queries
4. **Result Limiting**: Apply LIMIT/OFFSET at SQL level, not in Python
5. **Lazy Loading**: Load related data only when needed

### Caching Considerations

1. **Query Result Caching**: Cache frequently accessed queries (e.g., find-function)
2. **Module Cache**: Cache module definitions and file lists
3. **Call Graph Cache**: Cache call graph for relationship queries
4. **TTL Strategy**: Invalidate cache when database is updated

### Index Usage

- Primary indexes on `functions.name`, `modules.name`
- Foreign key indexes on `calls.caller_id`, `calls.callee_name`
- Composite indexes for common query patterns
- Regular ANALYZE to update statistics

## Implementation Roadmap

### Phase 1a: Batch Query Execution
- Implement batch query handler
- Add batch-query command to query.sh
- Add execute_batch_query() to Python API
- Add unit tests for batch queries

### Phase 1b: Pagination Support
- Implement pagination logic
- Add --limit, --offset, --total-count parameters
- Add apply_pagination() to Python API
- Add unit tests for pagination

### Phase 1c: Relationship Queries
- Implement find-dependents-in-module
- Implement find-call-chain
- Implement find-common-callers
- Add unit tests for relationship queries

### Phase 1d: Error Handling
- Define error codes and messages
- Implement error response formatting
- Add validate-database command
- Add get-error-details command
- Add unit tests for error handling

### Phase 1e: Integration & Performance
- Integration tests with real databases
- Performance testing and optimization
- Documentation and examples
- Vim plugin integration testing


## Correctness Properties (Detailed)

Based on the prework analysis, here are the key correctness properties that will be validated through property-based testing:

### Property 1: Batch Query Single Connection

*For any* batch query request with N queries, the API should open exactly one database connection and execute all queries through that connection.

**Validates: Requirements 1.1**

### Property 2: Batch Query Sequential Execution

*For any* batch query request with N queries, queries should execute in the order specified in the input, and each query should complete before the next begins.

**Validates: Requirements 1.4**

### Property 3: Batch Query Result Ordering

*For any* batch query request with N queries, the order of results in the response should match the order of queries in the input request.

**Validates: Requirements 1.7**

### Property 4: Batch Query Error Isolation

*For any* batch query request where one query is invalid, that query should return an error status while all other queries execute successfully and return results.

**Validates: Requirements 1.8, 1.10**

### Property 5: Batch Query Response Format

*For any* batch query request, the response should contain all query results with the same structure as individual query results, including timing information for each query.

**Validates: Requirements 1.5, 1.6**

### Property 6: Batch Query Performance

*For any* batch query request with 3-5 queries on a 6M LOC codebase, the total execution time should be at least 5x faster than executing the same queries sequentially via separate invocations.

**Validates: Requirements 1.11, 1.13**

### Property 7: Pagination Limit Parameter

*For any* query with a limit parameter, the number of results returned should not exceed the specified limit.

**Validates: Requirements 2.1**

### Property 8: Pagination Offset Parameter

*For any* query with an offset parameter, the first result returned should be the (offset+1)th result from the complete result set.

**Validates: Requirements 2.2**

### Property 9: Pagination Metadata Accuracy

*For any* paginated query result, the pagination metadata (limit, offset, total_count, has_more, returned_count) should accurately reflect the actual results returned.

**Validates: Requirements 2.6, 2.8, 2.9**

### Property 10: Pagination Deterministic Ordering

*For any* query executed multiple times with the same pagination parameters, results should be returned in the same order.

**Validates: Requirements 2.7**

### Property 11: Pagination Consistency

*For any* query with pagination, executing with different limit/offset combinations should return consistent, non-overlapping result sets that together contain all results.

**Validates: Requirements 2.7, 2.9**

### Property 12: Find Dependents in Module Correctness

*For any* module and function, all returned results from find-dependents-in-module should be functions that (1) exist in the specified module, and (2) call the specified function.

**Validates: Requirements 3.2, 3.3**

### Property 13: Find Call Chain Validity

*For any* two functions with a call path, find-call-chain should return at least one valid path from source to target where each consecutive pair of functions has a direct call relationship.

**Validates: Requirements 3.8, 3.10**

### Property 14: Find Call Chain Depth Limiting

*For any* find-call-chain query with max-depth parameter, all returned paths should have length <= max-depth + 1.

**Validates: Requirements 3.9**

### Property 15: Find Common Callers Correctness

*For any* set of functions, all returned results from find-common-callers should be functions that call every function in the input set.

**Validates: Requirements 3.15, 3.16**

### Property 16: Error Response Format

*For any* error condition, the API should return a structured error response containing error code, message, suggestion, query, and timestamp fields.

**Validates: Requirements 4.11-4.15**

### Property 17: Error Code Consistency

*For any* error condition, the returned error code should match the defined mapping (E001-E009) and be consistent across multiple invocations of the same error condition.

**Validates: Requirements 4.1-4.10**

### Property 18: Database Validation Completeness

*For any* database, the validate-database command should check that all required tables exist, all required indexes exist, and foreign key relationships are valid.

**Validates: Requirements 4.17-4.20**

### Property 19: Error Details Completeness

*For any* error code, the get-error-details command should return description, common causes, suggested resolutions, and examples.

**Validates: Requirements 4.23, 4.24**

### Property 20: Backward Compatibility - Existing Commands

*For any* existing query command executed without new parameters, the response format and data should be identical to the current implementation.

**Validates: Requirements 1.14, 1.15, 2.14, 2.15, 3.22, 3.23, 8.1-8.7**

### Property 21: Backward Compatibility - Default Behavior

*For any* query executed without pagination parameters, the API should return all results (equivalent to no limit).

**Validates: Requirements 2.15**

### Property 22: Pagination Default Offset

*For any* query with limit parameter but no offset parameter, the offset should default to 0.

**Validates: Requirements 2.4**

### Property 23: Pagination Default Limit

*For any* query with offset parameter but no limit parameter, the limit should default to 100.

**Validates: Requirements 2.5**

### Property 24: Relationship Query Pagination Support

*For any* relationship query (find-dependents-in-module, find-call-chain, find-common-callers), pagination parameters should work correctly and return paginated results with metadata.

**Validates: Requirements 3.4, 3.11, 3.17**

### Property 25: All Query Types Support Pagination

*For any* query type (function search, pattern search, dependency queries, relationship queries), pagination parameters should be supported and work correctly.

**Validates: Requirements 2.10**

### Property 26: Batch Query Supports All Commands

*For any* existing query command, it should be executable within a batch query and return the same results as when executed individually.

**Validates: Requirements 1.9**

### Property 27: Large Batch Query Support

*For any* batch query request with up to 100 individual queries, the API should execute all queries successfully without memory issues.

**Validates: Requirements 1.12**

### Property 28: Large Result Set Pagination

*For any* query that would return 10,000+ results, pagination should work correctly without memory issues.

**Validates: Requirements 2.12**

### Property 29: Total Count Calculation Performance

*For any* query with --total-count flag, the total count should be calculated within 50ms even for large result sets.

**Validates: Requirements 2.13**

### Property 30: Relationship Query Performance

*For any* relationship query on a 6M LOC codebase, execution time should meet performance targets (find-dependents-in-module: <50ms, find-call-chain: <200ms, find-common-callers: <100ms).

**Validates: Requirements 3.19-3.21**

## Property Reflection and Consolidation

After reviewing all 30 properties, the following consolidations were made to eliminate redundancy:

**Consolidated Properties**:
- Properties 7, 8, 9, 10, 11 were consolidated into a single comprehensive "Pagination Correctness" property that covers all pagination aspects
- Properties 12, 13, 14, 15 were consolidated into a single "Relationship Query Correctness" property
- Properties 1, 2, 3, 4, 5 were consolidated into a single "Batch Query Correctness" property
- Properties 16, 17, 18, 19 were consolidated into a single "Error Handling Correctness" property
- Properties 20, 21, 22, 23 were consolidated into a single "Backward Compatibility" property

**Final Consolidated Properties**:

### Property 1: Batch Query Correctness

*For any* batch query request, the API should:
1. Open exactly one database connection
2. Execute queries sequentially in input order
3. Return results in the same order as input queries
4. Isolate errors so one query failure doesn't affect others
5. Include timing information for each query
6. Execute at least 5x faster than sequential invocations

**Validates: Requirements 1.1, 1.4, 1.5, 1.6, 1.7, 1.8, 1.10, 1.11, 1.13**

### Property 2: Pagination Correctness

*For any* paginated query, the API should:
1. Respect limit parameter (results <= limit)
2. Respect offset parameter (skip first offset results)
3. Return accurate pagination metadata (limit, offset, total_count, has_more, returned_count)
4. Return results in consistent order across multiple executions
5. Return non-overlapping result sets across different limit/offset combinations
6. Default offset to 0 when not specified
7. Default limit to 100 when not specified
8. Set has_more=false when results < limit or offset >= total_count

**Validates: Requirements 2.1-2.9, 2.14, 2.15**

### Property 3: Relationship Query Correctness

*For any* relationship query, the API should:
1. For find-dependents-in-module: return only functions in the module that call the target function
2. For find-call-chain: return valid call paths where each consecutive pair has a direct call relationship
3. For find-call-chain: limit path depth to max_depth parameter
4. For find-common-callers: return only functions that call all specified functions
5. Support pagination on all relationship query results
6. Return function objects with complete signatures

**Validates: Requirements 3.2, 3.3, 3.4, 3.8, 3.9, 3.10, 3.11, 3.15, 3.16, 3.17**

### Property 4: Error Handling Correctness

*For any* error condition, the API should:
1. Return structured error response with code, message, suggestion, query, timestamp
2. Use correct error code from E001-E009 mapping
3. Be consistent across multiple invocations of same error
4. For database validation: check tables, indexes, and foreign keys
5. For error details: return description, causes, resolutions, and examples

**Validates: Requirements 4.1-4.15, 4.17-4.24**

### Property 5: Backward Compatibility

*For any* existing query command, the API should:
1. Continue to work without modification
2. Return identical response format and data when new parameters not used
3. Return all results when pagination parameters not specified
4. Support all existing commands within batch queries
5. Not modify existing query commands or output format

**Validates: Requirements 1.14, 1.15, 1.16, 2.14, 2.15, 2.16, 3.22, 3.23, 8.1-8.7**

### Property 6: Performance Requirements

*For any* query on a 6M LOC codebase, the API should:
1. Execute batch queries (3-5 queries) within 100ms
2. Execute pagination queries within 50ms
3. Execute find-dependents-in-module within 50ms
4. Execute find-call-chain within 200ms
5. Execute find-common-callers within 100ms
6. Calculate total count within 50ms
7. Support batch queries with up to 100 queries without memory issues
8. Support pagination on 10,000+ result sets without memory issues

**Validates: Requirements 1.11, 1.12, 1.13, 2.11, 2.12, 2.13, 3.19, 3.20, 3.21, 5.1-5.7**

### Property 7: Feature Completeness

*For any* feature requirement, the API should:
1. Support all existing query commands within batch queries
2. Support pagination on all query types
3. Support relationship queries (find-dependents-in-module, find-call-chain, find-common-callers)
4. Support error codes E001-E009
5. Support validate-database command
6. Support get-error-details command

**Validates: Requirements 1.9, 2.10, 3.1, 3.7, 3.14, 4.1-4.10, 4.16, 4.22**

## Testing Strategy (Detailed)

### Unit Testing Approach

**Batch Query Unit Tests**:
- Test single query in batch (verify result matches individual execution)
- Test multiple independent queries (verify all execute)
- Test query ordering preservation (verify order matches input)
- Test error isolation (one query fails, others succeed)
- Test timing information accuracy (verify timing fields are positive)
- Test batch query with all command types

**Pagination Unit Tests**:
- Test limit parameter (verify result count <= limit)
- Test offset parameter (verify correct results skipped)
- Test total_count calculation (verify accuracy)
- Test has_more flag (verify correct for various scenarios)
- Test sorting consistency (verify same order on multiple runs)
- Test edge cases (offset > total, limit = 0, limit > total, etc.)
- Test default values (offset defaults to 0, limit defaults to 100)

**Relationship Query Unit Tests**:
- Test find-dependents-in-module with various module/function combinations
- Test find-dependents-in-module error cases (missing module, missing function)
- Test find-call-chain with different depths
- Test find-call-chain with no path (verify empty results)
- Test find-call-chain with depth exceeded (verify partial paths)
- Test find-common-callers with 2+ functions
- Test find-common-callers error cases (< 2 functions, missing functions)

**Error Handling Unit Tests**:
- Test each error code (E001-E009) is returned for correct condition
- Test error response format (all fields present)
- Test error message is human-readable
- Test error suggestion is helpful
- Test error query field contains original query
- Test error timestamp is valid

### Integration Testing Approach

**Batch Query Integration Tests**:
- Test batch queries with real workspace.db
- Test batch queries with real modules.db
- Test batch queries with mixed command types
- Test batch queries with 3-5 queries (typical use case)
- Test batch queries with 100 queries (stress test)
- Test batch query performance (measure 5x speedup)

**Pagination Integration Tests**:
- Test pagination on large result sets (10,000+ results)
- Test pagination consistency across multiple queries
- Test pagination with relationship queries
- Test pagination with all query types

**Relationship Query Integration Tests**:
- Test find-dependents-in-module with real call graphs
- Test find-call-chain with complex call graphs
- Test find-common-callers with multiple functions
- Test relationship queries with pagination

**Vim Plugin Integration Tests**:
- Test hover information batch query (find-function + dependencies + dependents)
- Test search results pagination (search-functions with limit/offset)
- Test navigation queries (find-dependents-in-module, find-call-chain)

### Performance Testing Approach

**Batch Query Performance Tests**:
- Measure 3-5 query batch execution time (target: <100ms)
- Measure 100 query batch execution time
- Compare batch vs. sequential execution (target: 5x faster)
- Measure memory usage for 100 query batch

**Pagination Performance Tests**:
- Measure pagination query time (target: <50ms)
- Measure total_count calculation time (target: <50ms)
- Test with 10,000+ result sets
- Measure memory usage for large result sets

**Relationship Query Performance Tests**:
- Measure find-dependents-in-module time (target: <50ms)
- Measure find-call-chain time (target: <200ms)
- Measure find-common-callers time (target: <100ms)
- Test with complex call graphs

### Test Configuration

**Property-Based Testing**:
- Minimum 100 iterations per property test
- Use hypothesis library for Python
- Tag format: `Feature: api-phase-1-enhancements, Property {number}: {property_text}`
- Each property test validates one consolidated property

**Unit Test Framework**:
- pytest for Python tests
- Fixtures for database setup/teardown
- Mock databases for isolated testing
- Parametrized tests for multiple scenarios

**Integration Test Framework**:
- Real databases from test fixtures
- Sample codebases (small, medium, large)
- Performance benchmarking with timeit
- Memory profiling with memory_profiler

**Test Data**:
- Small codebase: 100 functions, 50 modules
- Medium codebase: 10,000 functions, 500 modules
- Large codebase: 100,000+ functions, 5,000+ modules (simulated)
