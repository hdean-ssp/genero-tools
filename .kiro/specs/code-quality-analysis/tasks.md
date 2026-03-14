# Phase 2 Tasks: Code Quality Analysis & Metrics

## Overview

This document breaks down Phase 2 implementation into concrete, actionable tasks organized by component. Each task includes acceptance criteria and dependencies.

## Task Structure

Tasks are organized into phases:
- **Phase 2a:** Core Metrics Extraction Engine
- **Phase 2b:** Code Quality Analysis Queries
- **Phase 2c:** Incremental Generation Engine
- **Phase 2d:** Database Integration & Optimization
- **Phase 2e:** Testing & Documentation

---

## Phase 2a: Core Metrics Extraction Engine

### 2a.1: Create MetricsExtractor Class

**Description:** Implement core metrics extraction engine with modular design.

**Acceptance Criteria:**
- [ ] MetricsExtractor class created in scripts/metrics_extractor.py
- [ ] extract_file_metrics() method implemented
- [ ] extract_function_metrics() method implemented
- [ ] extract_incremental() method implemented
- [ ] All methods have proper error handling
- [ ] Code follows existing project style

**Dependencies:** None

**Files to Create:**
- scripts/metrics_extractor.py

**Files to Modify:**
- None

---

### 2a.2: Implement LOC Counting

**Description:** Implement lines of code counting (excluding comments and blanks).

**Acceptance Criteria:**
- [ ] LOC counting excludes blank lines
- [ ] LOC counting excludes comment-only lines
- [ ] LOC counting includes inline comments
- [ ] LOC count is always > 0 for valid functions
- [ ] Unit tests pass (>95% coverage)
- [ ] Performance: < 10ms per function

**Dependencies:** 2a.1

**Test Cases:**
- Function with only comments → LOC = 0
- Function with blank lines → LOC excludes blanks
- Function with inline comments → LOC counts code line
- Multi-line statements → LOC counts correctly

---

### 2a.3: Implement Cyclomatic Complexity Calculation

**Description:** Implement cyclomatic complexity calculation based on control flow.

**Acceptance Criteria:**
- [ ] Base complexity is 1 for all functions
- [ ] IF statement adds 1 to complexity
- [ ] ELSEIF statement adds 1 to complexity
- [ ] WHILE loop adds 1 to complexity
- [ ] FOR loop adds 1 to complexity
- [ ] CASE statement adds count of WHEN clauses
- [ ] Complexity is always >= 1
- [ ] Unit tests pass (>95% coverage)
- [ ] Performance: < 10ms per function

**Dependencies:** 2a.1

**Test Cases:**
- Function with no control flow → complexity = 1
- Function with 1 IF → complexity = 2
- Function with IF/ELSEIF → complexity = 3
- Function with nested IF → complexity increases correctly
- CASE with 3 WHEN → complexity increases by 3

---

### 2a.4: Implement Local Variable Counting

**Description:** Count DEFINE statements for local variables.

**Acceptance Criteria:**
- [ ] Each DEFINE statement counted as one variable
- [ ] Parameter variables not counted as local
- [ ] Variable count is >= 0
- [ ] Unit tests pass (>95% coverage)
- [ ] Performance: < 5ms per function

**Dependencies:** 2a.1

**Test Cases:**
- Function with no DEFINE → count = 0
- Function with 5 DEFINE → count = 5
- Function with parameters → parameters not counted

---

### 2a.5: Implement Comment Extraction

**Description:** Extract and count comment lines for each function.

**Acceptance Criteria:**
- [ ] Comment-only lines counted
- [ ] Inline comments detected
- [ ] Comment ratio calculated (comments / LOC)
- [ ] Comment ratio between 0 and 1
- [ ] Unit tests pass (>95% coverage)
- [ ] Performance: < 10ms per function

**Dependencies:** 2a.1, 2a.2

**Test Cases:**
- Function with no comments → ratio = 0
- Function with 10 LOC and 2 comment lines → ratio = 0.2
- Function with inline comments → comments counted

---

### 2a.6: Implement Call Nesting Depth Analysis

**Description:** Analyze maximum nesting depth of function calls.

**Acceptance Criteria:**
- [ ] Direct calls have depth = 1
- [ ] Calls within calls have depth = 2+
- [ ] Maximum depth tracked
- [ ] Depth is >= 0
- [ ] Unit tests pass (>95% coverage)
- [ ] Performance: < 20ms per function

**Dependencies:** 2a.1

**Test Cases:**
- Function with no calls → depth = 0
- Function calling one function → depth = 1
- Function calling function that calls function → depth = 2

---

### 2a.7: Implement Early Return Detection

**Description:** Detect and count early RETURN statements.

**Acceptance Criteria:**
- [ ] Early returns counted separately from final return
- [ ] Final return not counted as early
- [ ] Early return count is >= 0
- [ ] Early returns flagged for review
- [ ] Unit tests pass (>95% coverage)
- [ ] Performance: < 10ms per function

**Dependencies:** 2a.1

**Test Cases:**
- Function with no early returns → count = 0
- Function with 1 early return → count = 1
- Function with multiple early returns → count = N

---

### 2a.8: Create FunctionMetrics Data Class

**Description:** Create data class for function metrics with validation.

**Acceptance Criteria:**
- [ ] FunctionMetrics dataclass created
- [ ] All fields properly typed
- [ ] Validation methods implemented
- [ ] Serialization to JSON working
- [ ] Unit tests pass

**Dependencies:** 2a.1-2a.7

**Files to Create:**
- scripts/metrics_models.py

---

## Phase 2b: Code Quality Analysis Queries

### 2b.1: Create QualityAnalyzer Class

**Description:** Implement code quality analysis query engine.

**Acceptance Criteria:**
- [ ] QualityAnalyzer class created in scripts/quality_analyzer.py
- [ ] find_complex_functions() method implemented
- [ ] find_similar_functions() method implemented
- [ ] find_isolated_functions() method implemented
- [ ] find_by_metrics() method implemented
- [ ] check_naming_conventions() method implemented
- [ ] All methods have proper error handling

**Dependencies:** 2a.8

**Files to Create:**
- scripts/quality_analyzer.py

---

### 2b.2: Implement Find Complex Functions Query

**Description:** Query functions exceeding complexity thresholds.

**Acceptance Criteria:**
- [ ] Query accepts max_complexity threshold
- [ ] Query accepts max_loc threshold
- [ ] Query accepts max_parameters threshold
- [ ] Results include all functions exceeding any threshold
- [ ] Results sorted by complexity descending
- [ ] Query executes in < 100ms
- [ ] Unit tests pass

**Dependencies:** 2b.1

**Test Cases:**
- Query with max_complexity=10 → returns functions with complexity > 10
- Query with max_loc=100 → returns functions with LOC > 100
- Query with multiple thresholds → returns union of results

---

### 2b.3: Implement Find Similar Functions Query

**Description:** Detect code duplication candidates by comparing function similarity.

**Acceptance Criteria:**
- [ ] Similarity calculated between 0 and 1
- [ ] Query accepts similarity_threshold parameter
- [ ] Results include all pairs above threshold
- [ ] Results sorted by similarity descending
- [ ] No duplicate pairs (i,j) and (j,i)
- [ ] Query executes in < 500ms for typical codebase
- [ ] Unit tests pass

**Dependencies:** 2b.1

**Test Cases:**
- Query with threshold=0.9 → returns highly similar functions
- Query with threshold=0.5 → returns moderately similar functions
- Results are symmetric

---

### 2b.4: Implement Find Isolated Functions Query

**Description:** Identify functions with no dependencies.

**Acceptance Criteria:**
- [ ] Isolated functions have empty called_by list
- [ ] Query returns all isolated functions
- [ ] Results include function name and file path
- [ ] Query executes in < 100ms
- [ ] Unit tests pass

**Dependencies:** 2b.1

**Test Cases:**
- Codebase with 10 isolated functions → returns all 10
- Codebase with no isolated functions → returns empty list

---

### 2b.5: Implement Find Functions by Metrics Query

**Description:** Query functions matching specified metric criteria.

**Acceptance Criteria:**
- [ ] Query accepts multiple metric criteria
- [ ] Criteria include: complexity, LOC, parameters, variables, call_depth
- [ ] Results match all specified criteria (AND logic)
- [ ] Query executes in < 100ms
- [ ] Unit tests pass

**Dependencies:** 2b.1

**Test Cases:**
- Query complexity > 5 AND LOC > 50 → returns matching functions
- Query parameters > 3 → returns functions with > 3 parameters

---

### 2b.6: Implement Naming Convention Checking

**Description:** Validate function/variable names against configured conventions.

**Acceptance Criteria:**
- [ ] Conventions loaded from configuration file
- [ ] Each convention has regex pattern and severity
- [ ] Violations detected and reported
- [ ] Violations include function name, convention, and message
- [ ] Query executes in < 200ms
- [ ] Unit tests pass

**Dependencies:** 2b.1

**Test Cases:**
- Function named "ProcessContract" with lowercase convention → violation
- Function named "process_contract" with lowercase convention → no violation
- Multiple violations detected in single query

---

## Phase 2c: Incremental Generation Engine

### 2c.1: Create IncrementalGenerator Class

**Description:** Implement incremental metrics generation engine.

**Acceptance Criteria:**
- [ ] IncrementalGenerator class created in scripts/incremental_generator.py
- [ ] generate_file_metrics() method implemented
- [ ] generate_function_metrics() method implemented
- [ ] merge_with_existing() method implemented
- [ ] All methods have proper error handling

**Dependencies:** 2a.8

**Files to Create:**
- scripts/incremental_generator.py

---

### 2c.2: Implement Single File Generation

**Description:** Generate metrics for a specific file without reprocessing entire codebase.

**Acceptance Criteria:**
- [ ] Single file generation completes in < 500ms
- [ ] Metrics identical to full generation for that file
- [ ] Existing data for other files preserved
- [ ] Call graph updated correctly
- [ ] Unit tests pass

**Dependencies:** 2c.1

**Test Cases:**
- Generate metrics for 500 LOC file → completes in < 500ms
- Generated metrics match full generation
- Other files' metrics unchanged

---

### 2c.3: Implement Single Function Generation

**Description:** Generate metrics for a specific function within a file.

**Acceptance Criteria:**
- [ ] Single function generation completes in < 100ms
- [ ] Metrics identical to full generation for that function
- [ ] Other functions in file preserved
- [ ] Call graph updated correctly
- [ ] Unit tests pass

**Dependencies:** 2c.1

**Test Cases:**
- Generate metrics for single function → completes in < 100ms
- Generated metrics match full generation
- Other functions unchanged

---

### 2c.4: Implement Merge with Existing Data

**Description:** Merge incremental metrics with existing workspace.json data.

**Acceptance Criteria:**
- [ ] Merge preserves existing data for other files
- [ ] Merge replaces old data for modified file
- [ ] Merge maintains data consistency
- [ ] Merge operation is atomic (all or nothing)
- [ ] Unit tests pass

**Dependencies:** 2c.1

**Test Cases:**
- Merge new file metrics with existing data → data consistent
- Merge updated function metrics → old data replaced
- Merge fails gracefully on invalid data

---

## Phase 2d: Database Integration & Optimization

### 2d.1: Create Database Schema

**Description:** Create metrics tables in workspace.db.

**Acceptance Criteria:**
- [ ] function_metrics table created with all required fields
- [ ] file_metrics table created with all required fields
- [ ] naming_violations table created
- [ ] duplication_candidates table created
- [ ] All tables have proper indexes
- [ ] Schema migration script created

**Dependencies:** None (can run in parallel with Phase 2a-c)

**Files to Create:**
- scripts/create_metrics_schema.py

---

### 2d.2: Create Database Integration Layer

**Description:** Implement database storage and retrieval for metrics.

**Acceptance Criteria:**
- [ ] Metrics stored in database
- [ ] Metrics retrievable via SQL queries
- [ ] Data consistency maintained
- [ ] Transactions used for atomic operations
- [ ] Unit tests pass

**Dependencies:** 2d.1, 2a.8

**Files to Create:**
- scripts/metrics_db.py

---

### 2d.3: Create Database Indexes

**Description:** Create indexes for query performance optimization.

**Acceptance Criteria:**
- [ ] Index on function_metrics.complexity
- [ ] Index on function_metrics.loc
- [ ] Index on function_metrics.is_isolated
- [ ] Index on file_metrics.average_complexity
- [ ] Index on naming_violations.severity
- [ ] Index on duplication_candidates.similarity
- [ ] Query performance meets targets (< 100ms)

**Dependencies:** 2d.1

---

### 2d.4: Integrate with Existing Query Layer

**Description:** Extend scripts/query_db.py with metrics queries.

**Acceptance Criteria:**
- [ ] New query functions added to query_db.py
- [ ] Existing queries continue to work
- [ ] New queries follow existing patterns
- [ ] All queries have proper error handling
- [ ] Unit tests pass

**Dependencies:** 2b.1, 2d.2

**Estimated Effort:** 1 day

**Files to Modify:**
- scripts/query_db.py

---

## Phase 2e: Testing & Documentation

### 2e.1: Create Unit Tests for Metrics Extraction

**Description:** Comprehensive unit tests for metrics extraction engine (using standard library only).

**Acceptance Criteria:**
- [ ] Tests for LOC counting (>95% coverage)
- [ ] Tests for complexity calculation (>95% coverage)
- [ ] Tests for variable counting (>95% coverage)
- [ ] Tests for comment extraction (>95% coverage)
- [ ] Tests for call depth analysis (>95% coverage)
- [ ] Tests for early return detection (>95% coverage)
- [ ] All tests passing
- [ ] Edge cases covered
- [ ] No external dependencies (standard library only)

**Dependencies:** 2a.1-2a.7

**Files to Create:**
- tests/test_metrics_extraction.py

---

### 2e.2: Create Unit Tests for Quality Analysis

**Description:** Comprehensive unit tests for quality analysis queries (using standard library only).

**Acceptance Criteria:**
- [ ] Tests for find_complex_functions (>95% coverage)
- [ ] Tests for find_similar_functions (>95% coverage)
- [ ] Tests for find_isolated_functions (>95% coverage)
- [ ] Tests for find_by_metrics (>95% coverage)
- [ ] Tests for check_naming_conventions (>95% coverage)
- [ ] All tests passing
- [ ] Edge cases covered
- [ ] No external dependencies (standard library only)

**Dependencies:** 2b.1-2b.6

**Files to Create:**
- tests/test_quality_analyzer.py

---

### 2e.3: Create Unit Tests for Incremental Generation

**Description:** Comprehensive unit tests for incremental generation engine (using standard library only).

**Acceptance Criteria:**
- [ ] Tests for generate_file_metrics (>95% coverage)
- [ ] Tests for generate_function_metrics (>95% coverage)
- [ ] Tests for merge_with_existing (>95% coverage)
- [ ] Tests for consistency with full generation
- [ ] All tests passing
- [ ] Edge cases covered
- [ ] No external dependencies (standard library only)

**Dependencies:** 2c.1-2c.4

**Files to Create:**
- tests/test_incremental_generator.py

---

### 2e.4: Create Integration Tests

**Description:** End-to-end integration tests for Phase 2 (using standard library only).

**Acceptance Criteria:**
- [ ] End-to-end metrics generation test
- [ ] Incremental update workflow test
- [ ] Quality analysis workflow test
- [ ] Naming convention validation test
- [ ] Performance benchmarks meet targets
- [ ] All tests passing
- [ ] No external dependencies (standard library only)

**Dependencies:** 2a.1-2d.4

**Files to Create:**
- tests/test_phase2_integration.py

---

### 2e.5: Create Property-Based Tests

**Description:** Property-based tests using standard library only (no hypothesis).

**Acceptance Criteria:**
- [ ] Property: Metrics consistency (all metrics valid)
- [ ] Property: Complexity calculation correctness
- [ ] Property: LOC calculation correctness
- [ ] Property: Incremental generation consistency
- [ ] Property: Similarity symmetry
- [ ] Property: Threshold filtering correctness
- [ ] All properties passing
- [ ] No external dependencies (standard library only)

**Dependencies:** 2a.1-2c.4

**Files to Create:**
- tests/test_phase2_properties.py

---

### 2e.6: Create Performance Benchmarks

**Description:** Performance benchmarks for Phase 2 components (using standard library only).

**Acceptance Criteria:**
- [ ] Benchmark: LOC counting performance
- [ ] Benchmark: Complexity calculation performance
- [ ] Benchmark: File metrics generation performance
- [ ] Benchmark: Function metrics generation performance
- [ ] Benchmark: Query performance
- [ ] Benchmark: Incremental generation performance
- [ ] All benchmarks meet targets
- [ ] No external dependencies (standard library only)

**Dependencies:** 2a.1-2d.4

**Files to Create:**
- tests/test_phase2_performance.py

---

### 2e.7: Create Configuration Examples

**Description:** Create example configuration files for naming conventions and thresholds.

**Acceptance Criteria:**
- [ ] Example naming conventions config created
- [ ] Example quality thresholds config created
- [ ] Configs are well-documented
- [ ] Configs follow JSON schema

**Dependencies:** None

**Files to Create:**
- config/naming_conventions.example.json
- config/quality_thresholds.example.json

---

### 2e.8: Create User Documentation

**Description:** Create comprehensive user documentation for Phase 2.

**Acceptance Criteria:**
- [ ] User guide created (docs/METRICS_USER_GUIDE.md)
- [ ] API documentation created (docs/METRICS_API.md)
- [ ] Configuration guide created (docs/METRICS_CONFIG.md)
- [ ] Examples provided for all major features
- [ ] Troubleshooting guide created

**Dependencies:** 2a.1-2d.4

**Files to Create:**
- docs/METRICS_USER_GUIDE.md
- docs/METRICS_API.md
- docs/METRICS_CONFIG.md

---

### 2e.9: Create Developer Documentation

**Description:** Create developer documentation for Phase 2 architecture and design.

**Acceptance Criteria:**
- [ ] Architecture guide created (docs/METRICS_ARCHITECTURE.md)
- [ ] Design decisions documented
- [ ] Extension points documented
- [ ] Code examples provided
- [ ] Testing guide created

**Dependencies:** 2a.1-2d.4

**Files to Create:**
- docs/METRICS_ARCHITECTURE.md
- docs/METRICS_TESTING.md

---

### 2e.10: Update Main Documentation

**Description:** Update main project documentation with Phase 2 information.

**Acceptance Criteria:**
- [ ] README.md updated with Phase 2 features
- [ ] ARCHITECTURE.md updated with Phase 2 components
- [ ] CHANGELOG.md updated with Phase 2 changes
- [ ] Quick start guide updated

**Dependencies:** 2e.8, 2e.9

**Files to Modify:**
- README.md
- docs/ARCHITECTURE.md
- docs/CHANGELOG.md

---

## Task Dependencies Graph

```
2a.1 (MetricsExtractor)
├── 2a.2 (LOC Counting)
├── 2a.3 (Complexity)
├── 2a.4 (Variables)
├── 2a.5 (Comments)
├── 2a.6 (Call Depth)
└── 2a.7 (Early Returns)
    └── 2a.8 (FunctionMetrics)
        ├── 2b.1 (QualityAnalyzer)
        │   ├── 2b.2 (Complex Functions)
        │   ├── 2b.3 (Similar Functions)
        │   ├── 2b.4 (Isolated Functions)
        │   ├── 2b.5 (Metrics Query)
        │   └── 2b.6 (Naming Conventions)
        │       └── 2d.4 (Query Layer Integration)
        └── 2c.1 (IncrementalGenerator)
            ├── 2c.2 (File Generation)
            ├── 2c.3 (Function Generation)
            └── 2c.4 (Merge)

2d.1 (Database Schema)
├── 2d.2 (Database Integration)
├── 2d.3 (Indexes)
└── 2d.4 (Query Layer Integration)

2e.1-2e.10 (Testing & Documentation)
    └── Depends on all Phase 2a-2d tasks
```

---

## Implementation Phases

Tasks are organized into 5 phases (2a-2e) with dependencies shown in the dependency graph below. Implementation can proceed in parallel where dependencies allow.

---

## Success Criteria

- [ ] All tasks completed
- [ ] All tests passing (>90% coverage)
- [ ] Performance targets met
- [ ] Documentation complete
- [ ] No breaking changes to Phase 1
- [ ] Code review approved
- [ ] Ready for production deployment

---

## Notes

- Tasks can be parallelized where dependencies allow
- Database schema (2d.1) can be created early in parallel with Phase 2a
- Testing (2e.1-2e.6) should be done incrementally as components are completed
- Documentation (2e.7-2e.10) can be started after core implementation is complete
- Performance benchmarks (2e.6) should be run on representative sample codebase
