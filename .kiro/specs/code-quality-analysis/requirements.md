# Phase 2 Requirements: Code Quality Analysis & Metrics

## Overview

This document derives functional and non-functional requirements from the Phase 2 design document. Requirements are organized by component and include acceptance criteria for validation.

## Functional Requirements

### FR1: Metrics Extraction

#### FR1.1: Lines of Code Counting

**Description:** System shall count lines of code (LOC) for each function, excluding comments and blank lines.

**Acceptance Criteria:**
- [ ] LOC count includes only executable code lines
- [ ] Blank lines are excluded from LOC count
- [ ] Comment-only lines are excluded from LOC count
- [ ] Inline comments do not affect LOC count
- [ ] LOC count is always > 0 for valid functions
- [ ] LOC count matches manual verification on sample functions

**Test Cases:**
- Function with only comments → LOC = 0
- Function with blank lines → LOC excludes blanks
- Function with inline comments → LOC counts code line
- Multi-line statements → LOC counts correctly

#### FR1.2: Cyclomatic Complexity Calculation

**Description:** System shall calculate cyclomatic complexity for each function based on control flow statements.

**Acceptance Criteria:**
- [ ] Base complexity is 1 for all functions
- [ ] IF statement adds 1 to complexity
- [ ] ELSEIF statement adds 1 to complexity
- [ ] WHILE loop adds 1 to complexity
- [ ] FOR loop adds 1 to complexity
- [ ] CASE statement adds count of WHEN clauses
- [ ] Complexity is always >= 1
- [ ] Complexity calculation matches standard definition

**Test Cases:**
- Function with no control flow → complexity = 1
- Function with 1 IF → complexity = 2
- Function with IF/ELSEIF → complexity = 3
- Function with nested IF → complexity increases correctly
- CASE with 3 WHEN → complexity increases by 3

#### FR1.3: Local Variable Counting

**Description:** System shall count local variables (DEFINE statements) for each function.

**Acceptance Criteria:**
- [ ] Each DEFINE statement is counted as one variable
- [ ] Parameter variables are not counted as local
- [ ] Variable count is >= 0
- [ ] Variable count matches manual verification

**Test Cases:**
- Function with no DEFINE → count = 0
- Function with 5 DEFINE → count = 5
- Function with parameters → parameters not counted

#### FR1.4: Function-Level Comment Extraction

**Description:** System shall extract and count comment lines for each function.

**Acceptance Criteria:**
- [ ] Comment-only lines are counted
- [ ] Inline comments are detected
- [ ] Comment ratio is calculated (comments / LOC)
- [ ] Comment ratio is between 0 and 1
- [ ] Comment extraction works for single-line and multi-line comments

**Test Cases:**
- Function with no comments → ratio = 0
- Function with 10 LOC and 2 comment lines → ratio = 0.2
- Function with inline comments → comments counted

#### FR1.5: Call Nesting Depth Analysis

**Description:** System shall analyze the maximum nesting depth of function calls.

**Acceptance Criteria:**
- [ ] Direct calls have depth = 1
- [ ] Calls within calls have depth = 2+
- [ ] Maximum depth is tracked
- [ ] Depth is >= 0

**Test Cases:**
- Function with no calls → depth = 0
- Function calling one function → depth = 1
- Function calling function that calls function → depth = 2

#### FR1.6: Early Return Detection

**Description:** System shall detect and count early RETURN statements (returns before end of function).

**Acceptance Criteria:**
- [ ] Early returns are counted separately from final return
- [ ] Final return is not counted as early
- [ ] Early return count is >= 0
- [ ] Early returns are flagged for review

**Test Cases:**
- Function with no early returns → count = 0
- Function with 1 early return → count = 1
- Function with multiple early returns → count = N

### FR2: Code Quality Analysis Queries

#### FR2.1: Find Complex Functions

**Description:** System shall query functions exceeding complexity thresholds.

**Acceptance Criteria:**
- [ ] Query accepts max_complexity threshold
- [ ] Query accepts max_loc threshold
- [ ] Query accepts max_parameters threshold
- [ ] Results include all functions exceeding any threshold
- [ ] Results are sorted by complexity descending
- [ ] Query executes in < 100ms

**Test Cases:**
- Query with max_complexity=10 → returns functions with complexity > 10
- Query with max_loc=100 → returns functions with LOC > 100
- Query with multiple thresholds → returns union of results

#### FR2.2: Find Similar Functions

**Description:** System shall detect code duplication candidates by comparing function similarity.

**Acceptance Criteria:**
- [ ] Similarity is calculated between 0 and 1
- [ ] Query accepts similarity_threshold parameter
- [ ] Results include all pairs above threshold
- [ ] Results are sorted by similarity descending
- [ ] No duplicate pairs (i,j) and (j,i)
- [ ] Query executes in < 500ms for typical codebase

**Test Cases:**
- Query with threshold=0.9 → returns highly similar functions
- Query with threshold=0.5 → returns moderately similar functions
- Results are symmetric (func1→func2 same as func2→func1)

#### FR2.3: Find Isolated Functions

**Description:** System shall identify functions with no dependencies (not called by other functions).

**Acceptance Criteria:**
- [ ] Isolated functions have empty called_by list
- [ ] Query returns all isolated functions
- [ ] Results include function name and file path
- [ ] Query executes in < 100ms

**Test Cases:**
- Codebase with 10 isolated functions → returns all 10
- Codebase with no isolated functions → returns empty list

#### FR2.4: Find Functions by Metrics Thresholds

**Description:** System shall query functions matching specified metric criteria.

**Acceptance Criteria:**
- [ ] Query accepts multiple metric criteria
- [ ] Criteria include: complexity, LOC, parameters, variables, call_depth
- [ ] Results match all specified criteria (AND logic)
- [ ] Query executes in < 100ms

**Test Cases:**
- Query complexity > 5 AND LOC > 50 → returns matching functions
- Query parameters > 3 → returns functions with > 3 parameters

#### FR2.5: Naming Convention Checking

**Description:** System shall validate function/variable names against configured conventions.

**Acceptance Criteria:**
- [ ] Conventions are loaded from configuration file
- [ ] Each convention has regex pattern and severity
- [ ] Violations are detected and reported
- [ ] Violations include function name, convention, and message
- [ ] Query executes in < 200ms

**Test Cases:**
- Function named "ProcessContract" with lowercase convention → violation
- Function named "process_contract" with lowercase convention → no violation
- Multiple violations detected in single query

### FR3: Incremental Generation

#### FR3.1: Generate Metrics for Single File

**Description:** System shall generate metrics for a specific file without reprocessing entire codebase.

**Acceptance Criteria:**
- [ ] Single file generation completes in < 500ms
- [ ] Metrics are identical to full generation for that file
- [ ] Existing data for other files is preserved
- [ ] Call graph is updated correctly

**Test Cases:**
- Generate metrics for 500 LOC file → completes in < 500ms
- Generated metrics match full generation
- Other files' metrics unchanged

#### FR3.2: Generate Metrics for Single Function

**Description:** System shall generate metrics for a specific function within a file.

**Acceptance Criteria:**
- [ ] Single function generation completes in < 100ms
- [ ] Metrics are identical to full generation for that function
- [ ] Other functions in file are preserved
- [ ] Call graph is updated correctly

**Test Cases:**
- Generate metrics for single function → completes in < 100ms
- Generated metrics match full generation
- Other functions unchanged

#### FR3.3: Merge with Existing Data

**Description:** System shall merge incremental metrics with existing workspace.json data.

**Acceptance Criteria:**
- [ ] Merge preserves existing data for other files
- [ ] Merge replaces old data for modified file
- [ ] Merge maintains data consistency
- [ ] Merge operation is atomic (all or nothing)

**Test Cases:**
- Merge new file metrics with existing data → data consistent
- Merge updated function metrics → old data replaced
- Merge fails gracefully on invalid data

#### FR3.4: Fast Turnaround for IDE/AI Agents

**Description:** System shall support real-time metrics generation for IDE plugins and AI agents.

**Acceptance Criteria:**
- [ ] File metrics generation: < 500ms
- [ ] Function metrics generation: < 100ms
- [ ] Query execution: < 100ms
- [ ] Total IDE workflow: < 1 second

**Test Cases:**
- IDE requests metrics for modified file → response in < 500ms
- AI agent requests function metrics → response in < 100ms
- Multiple concurrent requests handled efficiently

### FR4: Data Storage and Querying

#### FR4.1: Store Metrics in Database

**Description:** System shall store all metrics in workspace.db for efficient querying.

**Acceptance Criteria:**
- [ ] function_metrics table created with all required fields
- [ ] file_metrics table created with all required fields
- [ ] Indexes created for performance
- [ ] Data is queryable via SQL

**Test Cases:**
- Metrics stored in database → queryable via SQL
- Indexes exist on complexity, LOC, file_path
- Query performance meets targets

#### FR4.2: Maintain workspace.json Format

**Description:** System shall maintain backward compatibility with existing workspace.json format.

**Acceptance Criteria:**
- [ ] Existing fields are preserved
- [ ] New metrics fields are added without breaking existing code
- [ ] workspace.json remains valid JSON
- [ ] Existing queries continue to work

**Test Cases:**
- workspace.json with new metrics fields → valid JSON
- Existing code can read workspace.json
- New metrics fields are optional

### FR5: Configuration Management

#### FR5.1: Naming Conventions Configuration

**Description:** System shall support configurable naming conventions for validation.

**Acceptance Criteria:**
- [ ] Conventions loaded from JSON configuration file
- [ ] Each convention has regex pattern and severity
- [ ] Patterns are validated (no ReDoS attacks)
- [ ] Violations are reported with severity level

**Test Cases:**
- Load conventions from config file → applied correctly
- Invalid regex pattern → error handling
- Violations reported with correct severity

#### FR5.2: Quality Thresholds Configuration

**Description:** System shall support configurable quality thresholds.

**Acceptance Criteria:**
- [ ] Thresholds loaded from JSON configuration file
- [ ] Thresholds include: max_complexity, max_loc, max_parameters, etc.
- [ ] Thresholds are validated (positive integers)
- [ ] Thresholds are applied in queries

**Test Cases:**
- Load thresholds from config file → applied correctly
- Invalid threshold values → error handling
- Thresholds used in quality queries

## Non-Functional Requirements

### NFR1: Performance

#### NFR1.1: Metrics Extraction Speed

**Requirement:** Metrics extraction shall complete in < 500ms per file.

**Rationale:** IDE integration requires fast turnaround for real-time analysis.

**Measurement:** Time from file read to metrics calculation complete.

#### NFR1.2: Query Performance

**Requirement:** Database queries shall execute in < 100ms.

**Rationale:** Real-time analysis requires fast query response.

**Measurement:** Time from query start to results returned.

#### NFR1.3: Incremental Generation Speed

**Requirement:** Incremental metrics generation shall be 10x faster than full generation.

**Rationale:** IDE/AI agent integration requires fast incremental updates.

**Measurement:** Time for incremental vs. full generation on same file.

### NFR2: Scalability

#### NFR2.1: Large Codebase Support

**Requirement:** System shall support codebases with 10,000+ functions.

**Rationale:** Enterprise codebases are large and growing.

**Measurement:** Memory usage and query performance with 10k functions.

#### NFR2.2: Concurrent Access

**Requirement:** System shall support concurrent queries without data corruption.

**Rationale:** Multiple IDE instances and AI agents may query simultaneously.

**Measurement:** Concurrent query success rate and data consistency.

### NFR3: Reliability

#### NFR3.1: Error Handling

**Requirement:** System shall handle errors gracefully without data loss.

**Rationale:** Production systems must be robust.

**Measurement:** Error recovery success rate and data integrity.

#### NFR3.2: Data Consistency

**Requirement:** Metrics data shall remain consistent across all operations.

**Rationale:** Incorrect metrics lead to incorrect analysis.

**Measurement:** Data consistency checks after all operations.

### NFR4: Maintainability

#### NFR4.1: Code Modularity

**Requirement:** Metrics extraction shall be modular and separate from existing parser.

**Rationale:** Easier to maintain and extend independently.

**Measurement:** Code organization and dependency analysis.

#### NFR4.2: Documentation

**Requirement:** All functions and algorithms shall be documented with specifications.

**Rationale:** Easier to understand and maintain code.

**Measurement:** Documentation coverage and clarity.

### NFR5: Security

#### NFR5.1: Input Validation

**Requirement:** All user inputs shall be validated before processing.

**Rationale:** Prevent injection attacks and data corruption.

**Measurement:** Input validation coverage and attack resistance.

#### NFR5.2: Path Traversal Prevention

**Requirement:** File paths shall be validated to prevent directory traversal.

**Rationale:** Prevent unauthorized file access.

**Measurement:** Path validation coverage and attack resistance.

## Acceptance Criteria Summary

### Phase 2 Completion Criteria

- [ ] All FR1 requirements implemented and tested
- [ ] All FR2 requirements implemented and tested
- [ ] All FR3 requirements implemented and tested
- [ ] All FR4 requirements implemented and tested
- [ ] All FR5 requirements implemented and tested
- [ ] All NFR requirements met or documented
- [ ] 90%+ test coverage
- [ ] All tests passing
- [ ] Documentation complete
- [ ] No breaking changes to Phase 1

### Performance Acceptance Criteria

- [ ] File metrics extraction: < 500ms
- [ ] Function metrics extraction: < 100ms
- [ ] Database queries: < 100ms
- [ ] Incremental generation: 10x faster than full
- [ ] Memory usage: < 100MB for 10k functions

### Quality Acceptance Criteria

- [ ] Code coverage: >= 90%
- [ ] All tests passing
- [ ] No critical bugs
- [ ] Documentation complete
- [ ] Code review approved

## Traceability Matrix

| Requirement | Design Section | Test Case | Status |
|-------------|-----------------|-----------|--------|
| FR1.1 | Metrics Extraction | LOC Counting | Pending |
| FR1.2 | Complexity Calculation | Complexity Tests | Pending |
| FR1.3 | Variable Counting | Variable Tests | Pending |
| FR1.4 | Comment Extraction | Comment Tests | Pending |
| FR1.5 | Call Depth Analysis | Depth Tests | Pending |
| FR1.6 | Early Return Detection | Return Tests | Pending |
| FR2.1 | Complex Functions Query | Query Tests | Pending |
| FR2.2 | Similar Functions Query | Similarity Tests | Pending |
| FR2.3 | Isolated Functions Query | Isolation Tests | Pending |
| FR2.4 | Metrics Threshold Query | Threshold Tests | Pending |
| FR2.5 | Naming Conventions | Convention Tests | Pending |
| FR3.1 | Single File Generation | File Gen Tests | Pending |
| FR3.2 | Single Function Generation | Function Gen Tests | Pending |
| FR3.3 | Merge with Existing | Merge Tests | Pending |
| FR3.4 | IDE/AI Integration | Performance Tests | Pending |
| FR4.1 | Database Storage | Storage Tests | Pending |
| FR4.2 | workspace.json Format | Format Tests | Pending |
| FR5.1 | Naming Conventions Config | Config Tests | Pending |
| FR5.2 | Quality Thresholds Config | Config Tests | Pending |

## Conclusion

Phase 2 requirements provide comprehensive coverage of code quality metrics extraction, analysis, and incremental generation. All requirements are traceable to design sections and include specific acceptance criteria for validation. Performance and scalability requirements ensure the system can support real-time IDE integration and large enterprise codebases.
