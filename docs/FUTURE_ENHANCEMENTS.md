# Future Enhancements

This document outlines planned improvements and features for the Genero Function Signatures project.

## 1. Enhanced Type Parser

### Current State
- Extracts basic Genero data types (INTEGER, STRING, DECIMAL, etc.)
- Handles simple parameter and return types
- Limited support for complex types

### Planned Improvements

#### 1.1 Database-Like Types Detection
- **Goal:** Recognize and parse database-specific types
- **Examples:** 
  - `LIKE table_name.column_name`
  - `LIKE schema.table.column`
  - Database cursor types
  - Result set types
- **Implementation:**
  - Extend type parser to detect LIKE keyword
  - Extract table/column references
  - Store as structured type information
  - Enable cross-referencing with database schema

#### 1.2 Record Type Parsing
- **Goal:** Parse and decompose RECORD types
- **Examples:**
  - `RECORD { id INTEGER, name STRING }`
  - `RECORD LIKE table_name`
  - Nested records
- **Implementation:**
  - Parse record field definitions
  - Extract field names and types
  - Handle nested structures
  - Store as structured record metadata

#### 1.3 Complex Type Support
- **Goal:** Better handling of complex types
- **Examples:**
  - `DYNAMIC ARRAY OF RECORD`
  - `ARRAY OF LIKE table_name`
  - Generic types with parameters
- **Implementation:**
  - Recursive type parsing
  - Type composition tracking
  - Generic type parameters

## 2. Database Schema Integration

### Current State
- No integration with actual database schema
- Type information is static from source code

### Planned Improvements

#### 2.1 Schema File Parsing
- **Goal:** Parse database schema files to understand actual types
- **Supported Formats:**
  - SQL DDL files (CREATE TABLE statements)
  - Genero schema files (.sch)
  - Database metadata exports
- **Implementation:**
  - Create schema parser module
  - Extract table definitions
  - Map column types to Genero types
  - Build schema index

#### 2.2 Database Introspection Tool
- **Goal:** Query live database for schema information
- **Capabilities:**
  - Connect to database (PostgreSQL, MySQL, Oracle, etc.)
  - Extract table definitions
  - Get column types and constraints
  - Retrieve indexes and relationships
- **Implementation:**
  - Create `scripts/introspect_db.py`
  - Support multiple database drivers
  - Cache schema information
  - Generate schema index JSON

#### 2.3 Type Validation
- **Goal:** Validate function types against actual database schema
- **Features:**
  - Check if LIKE references exist in schema
  - Validate column types match function parameters
  - Detect type mismatches
  - Generate validation reports
- **Implementation:**
  - Create validation engine
  - Compare function signatures with schema
  - Generate compatibility matrix
  - Report discrepancies

## 3. Advanced Query Functionality

### Current Queries
- `find-function` - Exact function lookup
- `search-functions` - Pattern search
- `find-module` - Exact module lookup
- `search-modules` - Pattern search
- `list-file-functions` - Functions in file
- `list-file-modules` - Modules using file

### Planned Queries

#### 3.1 Module Content Queries
- **`find-modules-with-file <filename>`**
  - Find all modules containing a specific file
  - Show file category (L4GLS, U4GLS, 4GLS)
  - List all modules using the file

- **`find-modules-with-function <function_name>`**
  - Find modules containing a specific function
  - Show which file in module contains function
  - List all modules with that function

#### 3.2 Fuzzy/Approximate Matching
- **`find-closest-function <name>`**
  - Find functions with similar names
  - Use Levenshtein distance or similar algorithm
  - Return ranked results by similarity
  - Useful for typos or partial names

- **`find-closest-module <name>`**
  - Find modules with similar names
  - Return ranked results

#### 3.3 Dependency Queries
- **`find-function-dependencies <function_name>`**
  - Find all functions called by a function
  - Build call graph
  - Show dependency chain

- **`find-function-dependents <function_name>`**
  - Find all functions that call a function
  - Show reverse dependencies
  - Impact analysis

- **`find-module-dependencies <module_name>`**
  - Find all modules this module depends on
  - Show dependency graph
  - Identify circular dependencies

#### 3.4 Type-Based Queries
- **`find-functions-with-type <type_name>`**
  - Find all functions using a specific type
  - Filter by parameter or return type
  - Show usage patterns

- **`find-functions-with-database-type <table_name>`**
  - Find functions using LIKE references to a table
  - Show which columns are referenced
  - Identify schema dependencies

- **`find-functions-with-record <record_name>`**
  - Find functions using a specific record type
  - Show record field usage

#### 3.5 Cross-Reference Queries
- **`find-file-usage <filename>`**
  - Show all modules using a file
  - Show all functions in the file
  - Show all functions calling functions in file

- **`find-type-usage <type_name>`**
  - Show all functions using a type
  - Show all modules affected
  - Generate usage report

#### 3.6 Analysis Queries
- **`analyze-module <module_name>`**
  - Generate comprehensive module report
  - Show all files, functions, dependencies
  - Calculate metrics (complexity, size, etc.)

- **`analyze-function <function_name>`**
  - Generate comprehensive function report
  - Show signature, parameters, returns
  - Show dependencies and dependents
  - Show type information

- **`find-unused-functions`**
  - Find functions never called
  - Show functions only called from tests
  - Identify dead code

- **`find-unused-files`**
  - Find files not used by any module
  - Identify orphaned code

## 4. Implementation Priority

### Phase 1 (High Priority)
- [ ] Enhanced type parser for LIKE types
- [ ] Record type parsing
- [ ] `find-modules-with-file` query
- [ ] `find-closest-function` query

### Phase 2 (Medium Priority)
- [ ] Database schema file parsing
- [ ] Type validation engine
- [ ] `find-function-dependencies` query
- [ ] `find-functions-with-type` query
- [ ] Module analysis query

### Phase 3 (Lower Priority)
- [ ] Live database introspection
- [ ] Dependency graph visualization
- [ ] Circular dependency detection
- [ ] Dead code analysis
- [ ] Performance metrics

## 5. Technical Considerations

### Type Parser Enhancement
- Use recursive descent parser for complex types
- Build type AST for better representation
- Support type aliases and custom types
- Handle generic/parameterized types

### Schema Integration
- Support multiple schema formats
- Cache schema information for performance
- Validate schema consistency
- Handle schema versioning

### Query Performance
- Index frequently searched fields
- Use database views for complex queries
- Implement query result caching
- Consider full-text search for large codebases

### Backward Compatibility
- Maintain existing query interface
- Add new queries without breaking old ones
- Version query API
- Provide migration guide

## 6. Testing Strategy

### Unit Tests
- Type parser tests with various type combinations
- Schema parser tests with different formats
- Query functionality tests
- Edge case handling

### Integration Tests
- End-to-end type validation
- Schema integration with real databases
- Query result accuracy
- Performance benchmarks

### Test Data
- Expand test codebase with complex types
- Add sample schema files
- Create test databases
- Generate performance test data

## 7. Documentation Updates

### New Documentation Files
- `TYPE_PARSER.md` - Type parsing documentation
- `SCHEMA_INTEGRATION.md` - Schema integration guide
- `ADVANCED_QUERIES.md` - Advanced query documentation
- `PERFORMANCE.md` - Performance tuning guide

### Updated Documentation
- `README.md` - Add new features section
- `ARCHITECTURE.md` - Update with new components
- `QUERYING.md` - Add new query examples

## 8. Related Issues & Considerations

### Database Support
- Which databases to support initially?
- How to handle database-specific types?
- Schema versioning and migrations?

### Performance
- How to handle very large codebases (100K+ functions)?
- Query optimization strategies?
- Caching strategies?

### Usability
- CLI vs. API vs. Web interface?
- Integration with IDEs?
- Export formats for reports?

## 9. Success Criteria

- [ ] Type parser handles 95%+ of Genero types
- [ ] Schema integration works with major databases
- [ ] New queries execute in <100ms on typical codebases
- [ ] All new features have >90% test coverage
- [ ] Documentation is comprehensive and up-to-date
- [ ] Performance benchmarks show <10% overhead
