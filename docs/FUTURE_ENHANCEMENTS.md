# Future Enhancements

This document outlines planned improvements and features for the Genero Function Signatures project.

## Completed Enhancements

### ✅ Phase 0: Function Body Parsing (COMPLETED)

**Status:** Complete and tested

- ✅ Parse function bodies line-by-line to extract function calls
- ✅ Identify all function calls within a function body
- ✅ Track call locations (line numbers)
- ✅ Handle nested calls and conditional calls
- ✅ Support different call patterns (direct calls, assignments, control flow)
- ✅ Build call graph database with caller-callee relationships
- ✅ Store call metadata (line number, context)
- ✅ Enable dependency queries (find-function-dependencies, find-function-dependents)

**Implementation Details:**
- AWK parser enhanced with 4 call detection patterns
- Calls stored in JSON and SQLite database
- New `calls` table with indexed lookups
- Query functions: `find_function_dependencies()`, `find_function_dependents()`
- Shell commands: `find-function-dependencies`, `find-function-dependents`
- 61 function calls detected in test suite
- All tests passing

**See Also:**
- [CALL_GRAPH_QUERIES.md](CALL_GRAPH_QUERIES.md) - Complete documentation
- [QUICK_START_CALL_GRAPH.md](QUICK_START_CALL_GRAPH.md) - Quick start guide
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Implementation details

## 1. File Header Comment Parsing

### Current State
- No extraction of file-level metadata
- File header comments are ignored
- No tracking of code references (e.g., SR-12345, PRB-137, EH100512) or authorship

### Planned Improvements

#### 1.1 Header Comment Extraction
- **Goal:** Parse file header comments to extract metadata and change history
- **Supported Formats:**
  - Standard comment blocks at file start
  - Multi-line comments with structured change logs
  - Single-line comment sequences
- **Implementation:**
  - Extract first N lines of comments from each file
  - Parse change history tables with variable column layouts
  - Extract code references (tickets, issue IDs, etc.)
  - Extract author information from change records
  - Store metadata in JSON and database
  - Handle various comment styles and inconsistent spacing

#### 1.2 Code References Extraction
- **Goal:** Extract code references from file headers for traceability
- **Examples:** SR-12345, PRB-137, EH100512, EH100512-4, etc.
- **Use Cases:**
  - Link code changes to tickets/issues
  - Track which changes are related to specific problems
  - Enable ticket-based code queries
  - Generate change reports by reference

#### 1.3 Author & Change Tracking
- **Goal:** Extract author and change history from file headers
- **Characteristics:**
  - Change history typically in tabular format within comments
  - Columns may include: Reference, For, Date, Who, Description
  - Column order and presence varies between files
  - Spacing/alignment is inconsistent (tabs, spaces, variable widths)
  - Multiple authors may modify same file over time
- **Use Cases:**
  - Identify subject matter experts for code review
  - Track code ownership and responsibility
  - Understand change history without git
  - Generate audit trails
  - Find who last modified a file

#### 1.4 Flexible Parser Design
- **Challenge:** Headers have inconsistent structure and spacing
  - Column positions vary between files
  - Some files omit certain columns (e.g., no "For" column)
  - Spacing uses mix of tabs and spaces
  - Table alignment is not guaranteed
- **Solution Approach:**
  - Use pattern matching to identify change history sections
  - Extract rows based on reference ID patterns (e.g., `[A-Z]+-\d+`)
  - Parse columns flexibly by position or delimiter
  - Handle missing/optional columns gracefully
  - Normalize whitespace for consistent parsing
  - Support multiple table formats

#### 1.5 Database Schema Update
- **Goal:** Store file metadata in SQLite for efficient querying
- **New Tables:**
  ```sql
  file_metadata (
    id INTEGER PRIMARY KEY,
    file_id INTEGER NOT NULL,
    FOREIGN KEY (file_id) REFERENCES files(id)
  )
  
  file_references (
    id INTEGER PRIMARY KEY,
    file_id INTEGER NOT NULL,
    reference_id TEXT NOT NULL,
    author TEXT,
    change_date TEXT,
    description TEXT,
    FOREIGN KEY (file_id) REFERENCES files(id)
  )
  
  file_authors (
    id INTEGER PRIMARY KEY,
    file_id INTEGER NOT NULL,
    author TEXT NOT NULL,
    first_change_date TEXT,
    last_change_date TEXT,
    change_count INTEGER,
    FOREIGN KEY (file_id) REFERENCES files(id)
  )
  ```

#### 1.6 Query Functions
- **`find-files-by-reference <ref_id>`** - Find files modified for a specific reference
- **`find-files-by-author <author>`** - Find files authored/modified by person
- **`get-file-references <filename>`** - Get all references for a file
- **`get-file-authors <filename>`** - Get all authors who modified a file
- **`find-recent-changes <days>`** - Find recently modified files
- **`find-author-expertise <author>`** - Show what areas an author works on
- **`find-reference-changes <ref_id>`** - Get all files modified for a reference

#### 1.7 JSON Output Enhancement
- **workspace.json** now includes file-level metadata:
  - List of code references extracted from headers
  - List of authors and their change dates
  - Change history entries with reference, author, date, description

#### 1.8 Handling Shared Files
- **Challenge:** The same .4gl file can appear in multiple .m3 modules
- **Considerations:**
  - File header metadata is parsed once per file (not per module reference)
  - Metadata is associated with the file, not the module
  - Queries can find all modules using a file with specific metadata
  - File-level references/authors apply across all modules using that file
  - Module-specific context is tracked separately in module definitions

#### 1.9 Use Cases
- **Code Review Assignment** - Find experts for specific files/modules
- **Change Tracking** - Link code changes to tickets/issues
- **Audit Compliance** - Track who modified what and when
- **Onboarding** - Identify critical/complex files needing review
- **Impact Analysis** - Understand who to notify about changes
- **Knowledge Management** - Map expertise across team
- **Risk Assessment** - Identify files with frequent changes
- **Maintenance Planning** - Find files needing updates
- **Ticket-Based Queries** - Find all code changes for a specific ticket

### Implementation Details

#### Parser Enhancement
- Extend AWK parser to capture file header comments
- Extract first 50-100 lines of comments
- Identify change history sections using pattern matching
- Extract code references using regex patterns (e.g., `[A-Z]+-\d+`, `[A-Z]+\d+`)
- Parse change history rows flexibly to handle:
  - Variable column positions
  - Missing/optional columns
  - Inconsistent spacing (tabs vs spaces)
  - Different table formats
- Extract author names from change records
- Normalize whitespace and align data
- Store in JSON and database

#### Parsing Strategy
- **Reference Detection:** Use regex to find code reference patterns (SR-12345, PRB-137, EH100512, etc.)
- **Column Flexibility:** Parse by position ranges or delimiters, not fixed columns
- **Whitespace Handling:** Normalize tabs/spaces, handle variable-width columns
- **Optional Columns:** Gracefully handle missing columns (e.g., no "For" column)
- **Author Extraction:** Extract from "Who" or similar columns, normalize names
- **Date Parsing:** Handle various date formats, normalize to ISO 8601

#### Performance Considerations
- Header parsing adds minimal overhead (<1% per file)
- Index frequently searched fields (author, tags, status)
- Cache metadata for repeated queries
- Lazy load change history if needed

#### Backward Compatibility
- Existing workspace.json format preserved
- New `header_metadata` field is optional
- Files without headers have empty metadata
- All existing queries unaffected

## 2. Enhanced Type Parser

### Current State
- Extracts basic Genero data types (INTEGER, STRING, DECIMAL, etc.)
- Handles simple parameter and return types
- Limited support for complex types

### Planned Improvements

#### 2.1 Database-Like Types Detection
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

#### 2.2 Record Type Parsing
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

#### 2.3 Complex Type Support
- **Goal:** Better handling of complex types
- **Examples:**
  - `DYNAMIC ARRAY OF RECORD`
  - `ARRAY OF LIKE table_name`
  - Generic types with parameters
- **Implementation:**
  - Recursive type parsing
  - Type composition tracking
  - Generic type parameters

## 3. Database Schema Integration

### Current State
- No integration with actual database schema
- Type information is static from source code

### Planned Improvements

#### 3.1 Schema File Parsing
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

#### 3.2 Database Introspection Tool
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

#### 3.3 Type Validation
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

## 4. Advanced Query Functionality

### Current Queries
- `find-function` - Exact function lookup
- `search-functions` - Pattern search
- `find-module` - Exact module lookup
- `search-modules` - Pattern search
- `list-file-functions` - Functions in file
- `list-file-modules` - Modules using file

### Query Categories Overview

The advanced queries are organized into logical categories:

1. **Module Content Queries** - Find modules and their contents
2. **Fuzzy Matching** - Approximate/similarity-based searches
3. **Dependency Queries** - Analyze function and module relationships
4. **Type-Based Queries** - Search by data types
5. **Cross-Reference Queries** - Find usage across codebase
6. **Analysis Queries** - Generate reports and metrics
7. **Signature Pattern Queries** - Find functions by structure
8. **Naming Convention Queries** - Enforce and analyze naming patterns
9. **Complexity & Metrics Queries** - Identify code quality issues
10. **Relationship & Impact Queries** - Analyze dependencies and impact
11. **Export & Reporting Queries** - Generate various report formats
12. **Search & Filter Queries** - Advanced search capabilities
13. **Comparison & Diff Queries** - Compare code elements

### Planned Queries

#### 4.1 Module Content Queries
- **`find-modules-with-file <filename>`**
  - Find all modules containing a specific file
  - Show file category (L4GLS, U4GLS, 4GLS)
  - List all modules using the file

- **`find-modules-with-function <function_name>`**
  - Find modules containing a specific function
  - Show which file in module contains function
  - List all modules with that function

#### 4.2 Fuzzy/Approximate Matching
- **`find-closest-function <name>`**
  - Find functions with similar names
  - Use Levenshtein distance or similar algorithm
  - Return ranked results by similarity
  - Useful for typos or partial names

- **`find-closest-module <name>`**
  - Find modules with similar names
  - Return ranked results

#### 4.3 Dependency Queries
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

#### 4.4 Type-Based Queries
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

#### 4.5 Cross-Reference Queries
- **`find-file-usage <filename>`**
  - Show all modules using a file
  - Show all functions in the file
  - Show all functions calling functions in file

- **`find-type-usage <type_name>`**
  - Show all functions using a type
  - Show all modules affected
  - Generate usage report

#### 4.6 Analysis Queries
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

#### 4.7 Signature Pattern Queries
- **`find-functions-by-parameter-count <count>`**
  - Find all functions with exactly N parameters
  - Useful for identifying simple vs. complex functions
  - Help with API consistency analysis

- **`find-functions-by-return-count <count>`**
  - Find functions returning exactly N values
  - Identify functions with multiple return values
  - Useful for refactoring analysis

- **`find-functions-with-no-parameters`**
  - Find parameterless functions (procedures)
  - Identify global state dependencies
  - Useful for side-effect analysis

- **`find-functions-with-no-returns`**
  - Find void/procedure-style functions
  - Identify functions that modify state
  - Useful for pure function identification

#### 4.8 Naming Convention Queries
- **`find-functions-matching-pattern <regex>`**
  - Find functions matching naming patterns
  - Enforce naming conventions (get_*, set_*, etc.)
  - Identify non-compliant functions

- **`find-functions-by-prefix <prefix>`**
  - Find all functions starting with prefix
  - Group related functions
  - Identify function families

- **`find-functions-by-suffix <suffix>`**
  - Find functions ending with suffix
  - Identify function categories (e.g., _handler, _validator)
  - Useful for architectural analysis

#### 4.9 Complexity & Metrics Queries
- **`find-complex-functions [threshold]`**
  - Find functions exceeding complexity threshold
  - Use line count, parameter count, return count
  - Identify refactoring candidates

- **`find-large-modules [threshold]`**
  - Find modules with many files or functions
  - Identify modules needing decomposition
  - Useful for architecture review

- **`find-functions-by-line-count <min> <max>`**
  - Find functions within line count range
  - Identify very short or very long functions
  - Useful for code quality analysis

#### 4.10 Relationship & Impact Queries
- **`find-function-callers <function_name>`**
  - Find all functions that call a specific function
  - Show call chain depth
  - Useful for impact analysis before changes

- **`find-module-dependents <module_name>`**
  - Find all modules depending on a module
  - Show dependency depth
  - Identify critical modules

- **`find-shared-dependencies <module1> <module2>`**
  - Find common dependencies between modules
  - Identify coupling points
  - Useful for refactoring decisions

- **`find-isolated-functions`**
  - Find functions with no dependencies
  - Identify standalone utilities
  - Useful for library extraction

#### 4.11 Export & Reporting Queries
- **`export-module-graph <module_name> [format]`**
  - Export module dependency graph (JSON, DOT, SVG)
  - Visualize module relationships
  - Support for GraphViz rendering

- **`export-function-report <function_name> [format]`**
  - Export function details to JSON, CSV, or HTML
  - Include signature, metrics, dependencies
  - Useful for documentation generation

- **`generate-codebase-report [format]`**
  - Generate comprehensive codebase statistics
  - Show module breakdown, function counts, metrics
  - Export as JSON, CSV, or HTML report

- **`generate-dependency-matrix`**
  - Create module-to-module dependency matrix
  - Show coupling metrics
  - Identify circular dependencies

#### 4.12 Search & Filter Queries
- **`search-by-signature <pattern>`**
  - Search function signatures using regex
  - Find functions with specific parameter/return patterns
  - Useful for API discovery

- **`search-by-comment <pattern>`**
  - Search function comments/documentation
  - Find functions by description
  - Requires comment extraction enhancement

- **`filter-functions <criteria>`**
  - Combine multiple filter criteria
  - Example: `filter-functions "module=core AND type=INTEGER AND params>2"`
  - Powerful query composition

#### 4.13 Comparison & Diff Queries
- **`compare-modules <module1> <module2>`**
  - Compare two modules' structure and functions
  - Show differences in dependencies
  - Identify duplicate functionality

- **`compare-function-signatures <func1> <func2>`**
  - Compare two function signatures
  - Identify parameter/return differences
  - Useful for API compatibility checking

- **`find-duplicate-functions`**
  - Find functions with identical or similar signatures
  - Identify code duplication
  - Suggest consolidation candidates

## 5. Implementation Priority

### Phase 0 (Foundation - COMPLETED ✅)
- ✅ Function body parsing to extract function calls
- ✅ Build call graph database (calls table)
- ✅ Enable dependency queries (find-function-dependencies, find-function-dependents)
- ✅ Store call metadata (line numbers, context)

### Phase 1 (High Priority)
- [ ] File header comment parsing for metadata extraction
- [ ] Code tags and categorization from headers
- [ ] Author and change tracking from file headers
- [ ] File metadata database schema and queries
- [ ] `find-files-by-tag`, `find-files-by-author`, `find-files-by-category` queries
- [ ] Call resolution - Map called function names to actual functions
- [ ] Recursive call detection - Identify and mark recursive calls
- [ ] Enhanced type parser for LIKE types
- [ ] Record type parsing
- [ ] `find-modules-with-file` query
- [ ] `find-closest-function` query
- [ ] `find-functions-by-parameter-count` query
- [ ] `find-functions-matching-pattern` query

### Phase 2 (Medium Priority)
- [ ] Database schema file parsing
- [ ] Type validation engine
- [ ] `find-functions-with-type` query
- [ ] Module analysis query
- [ ] `find-complex-functions` query
- [ ] `find-function-callers` query
- [ ] `export-module-graph` query

### Phase 3 (Lower Priority)
- [ ] Live database introspection
- [ ] Dependency graph visualization
- [ ] Circular dependency detection
- [ ] Dead code analysis
- [ ] Performance metrics
- [ ] `search-by-signature` query
- [ ] `compare-modules` query
- [ ] `find-duplicate-functions` query
- [ ] `generate-dependency-matrix` query

## 6. Technical Considerations

### File Header Parser
- Extract first N lines of file comments (configurable, default 100)
- Parse structured tag information from file headers
- Handle multi-line values and arrays
- Store metadata in new `file_metadata`, `file_tags`, `file_changes` tables
- Index frequently searched fields (author, tags, status, category)
- Performance: <1% overhead per file

### Function Body Parser Enhancement
- Extend AWK parser to capture function body lines between FUNCTION and END FUNCTION
- Use regex patterns to identify function calls (e.g., `function_name(`, `CALL function_name`)
- Handle edge cases: comments, string literals, nested parentheses
- Store call information in new `calls` table with caller_id, callee_name, line_number
- Performance: Consider line-by-line streaming for large functions

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

## 7. Testing Strategy

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

## 8. Documentation Updates

### New Documentation Files
- `TYPE_PARSER.md` - Type parsing documentation
- `SCHEMA_INTEGRATION.md` - Schema integration guide
- `ADVANCED_QUERIES.md` - Advanced query documentation
- `PERFORMANCE.md` - Performance tuning guide

### Updated Documentation
- `README.md` - Add new features section
- `ARCHITECTURE.md` - Update with new components
- `QUERYING.md` - Add new query examples

## 9. Related Issues & Considerations

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

## 10. Success Criteria

- [ ] Type parser handles 95%+ of Genero types
- [ ] Schema integration works with major databases
- [ ] New queries execute in <100ms on typical codebases
- [ ] All new features have >90% test coverage
- [ ] Documentation is comprehensive and up-to-date
- [ ] Performance benchmarks show <10% overhead
