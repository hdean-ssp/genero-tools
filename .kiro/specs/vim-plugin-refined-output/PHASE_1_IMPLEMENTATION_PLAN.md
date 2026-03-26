# Phase 1: Design & Planning - Implementation Plan

**Date:** March 25, 2026  
**Feature:** 1.1 Refined Output for Vim Plugin  
**Phase:** 1 (Design & Planning)  
**Effort:** 0.5 days  
**Status:** In Progress

---

## Overview

Phase 1 establishes the design foundation for implementing three optimized output formats (concise, hover, completion) for Vim plugin integration. This phase focuses on design decisions, architecture, and planning before implementation begins.

---

## Task 1.1: Review Requirements with Team

### Objective
Ensure all requirements are understood and aligned before implementation.

### Deliverables

1. **Requirements Review Checklist**
   - [ ] All 10 requirements understood
   - [ ] Acceptance criteria clear
   - [ ] Edge cases identified
   - [ ] Performance targets confirmed (<100ms)
   - [ ] Backward compatibility requirements confirmed

2. **Key Requirements Summary**
   - Requirement 1: Concise format (single-line signatures)
   - Requirement 2: Hover format (multi-line with metadata)
   - Requirement 3: Completion format (tab-separated for Vim/Neovim)
   - Requirement 4: Format option (`--format=vim|vim-hover|vim-completion`)
   - Requirement 5: Filtering options (`--filter=functions-only|no-metrics|no-file-info`)
   - Requirement 6: Backward compatibility (default behavior unchanged)
   - Requirement 7: Test coverage (>90%)
   - Requirement 8: Documentation with examples
   - Requirement 9: Query command integration
   - Requirement 10: Error handling and validation

3. **Clarifications Needed**
   - [ ] Confirm tab-separated format for completion (APPROVED - see COMPLETION_FORMAT_RATIONALE.md)
   - [ ] Confirm performance targets
   - [ ] Confirm backward compatibility approach
   - [ ] Confirm test coverage target

### Acceptance Criteria
- All requirements documented and understood
- No ambiguities in acceptance criteria
- Team aligned on approach
- Ready to proceed with design

---

## Task 1.2: Design Output Format Specifications

### Objective
Define precise specifications for each output format.

### Deliverables

1. **Concise Format Specification**
   ```
   Pattern: function_name(param1: TYPE1, param2: TYPE2, ...) -> RETURN_TYPE
   
   Examples:
   - calculate(amount: DECIMAL, rate: DECIMAL) -> DECIMAL
   - get_account(id: INTEGER) -> RECORD
   - my_procedure() -> DECIMAL
   - my_procedure(param1: INTEGER, param2: VARCHAR)
   
   Rules:
   - Single line only
   - No file path or line number
   - No complexity metrics
   - Standard Genero type names
   - Comma-separated parameters
   - Arrow separator for return type
   ```

2. **Hover Format Specification**
   ```
   Pattern:
   function_name(params) -> return_type
   File: path/to/file.4gl:line_number
   Complexity: N, LOC: M
   
   Examples:
   - calculate(amount: DECIMAL, rate: DECIMAL) -> DECIMAL
     File: src/math.4gl:42
     Complexity: 5, LOC: 23
   
   Rules:
   - Three lines per function
   - Line 1: Concise signature
   - Line 2: File location (file:line)
   - Line 3: Complexity metrics
   - Blank line between functions (when multiple)
   - Handle missing metadata gracefully
   ```

3. **Completion Format Specification**
   ```
   Pattern: word<TAB>menu<TAB>info
   
   Columns:
   - Column 1 (word): Function name (completion word)
   - Column 2 (menu): Function signature
   - Column 3 (info): File location and metrics
   
   Example:
   calculate	function(amount: DECIMAL, rate: DECIMAL) -> DECIMAL	src/math.4gl:42 | Complexity: 5, LOC: 23
   
   Rules:
   - Tab-separated (not spaces)
   - One function per line
   - Compatible with Vim complete() function
   - Compatible with Neovim LSP completion items
   - Handle missing metadata gracefully
   ```

4. **Format Specification Document**
   - Create `FORMAT_SPECIFICATION.md` with detailed specs
   - Include regex patterns for validation
   - Include examples for each format
   - Include edge case handling

### Acceptance Criteria
- All three formats precisely specified
- Examples provided for each format
- Edge cases documented
- Validation rules defined
- Ready for implementation

---

## Task 1.3: Design Command-Line Interface

### Objective
Define the command-line interface for format and filter options.

### Deliverables

1. **Format Option Design**
   ```bash
   # Syntax
   bash query.sh <command> <args> --format=<format>
   
   # Supported formats
   --format=vim              # Concise format
   --format=vim-hover        # Hover format
   --format=vim-completion   # Completion format (tab-separated)
   
   # Default (no option)
   # Uses current default format (backward compatible)
   
   # Case-insensitive
   --format=VIM              # Same as --format=vim
   --format=Vim-Hover        # Same as --format=vim-hover
   ```

2. **Filter Option Design**
   ```bash
   # Syntax
   bash query.sh <command> <args> --filter=<filter>
   
   # Supported filters
   --filter=functions-only   # Exclude procedures
   --filter=no-metrics       # Exclude complexity metrics
   --filter=no-file-info     # Exclude file path and line number
   
   # Multiple filters
   --filter=functions-only --filter=no-metrics
   
   # Case-insensitive
   --filter=Functions-Only   # Same as --filter=functions-only
   ```

3. **Combined Usage Examples**
   ```bash
   # Format only
   bash query.sh find-function "calculate" --format=vim
   
   # Filter only
   bash query.sh find-function "calculate" --filter=functions-only
   
   # Format and filter
   bash query.sh search-functions "get_*" --format=vim-hover --filter=no-metrics
   
   # Multiple filters
   bash query.sh search-functions "*" --format=vim-completion --filter=functions-only --filter=no-metrics
   ```

4. **Error Handling Design**
   ```bash
   # Invalid format
   Error: Invalid format 'invalid'. Supported formats: vim, vim-hover, vim-completion
   
   # Invalid filter
   Error: Invalid filter 'invalid'. Supported filters: functions-only, no-metrics, no-file-info
   
   # Database not found
   Error: Database not found. Run 'bash generate_all.sh /path/to/code' to create database.
   ```

5. **Help Text Design**
   ```bash
   bash query.sh find-function --help
   
   Usage: bash query.sh find-function <name> [OPTIONS]
   
   Options:
     --format=FORMAT    Output format (vim, vim-hover, vim-completion)
     --filter=FILTER    Filter results (functions-only, no-metrics, no-file-info)
     --help             Show this help message
   
   Examples:
     bash query.sh find-function "calculate" --format=vim
     bash query.sh find-function "calculate" --format=vim-hover --filter=no-metrics
   ```

### Acceptance Criteria
- Format option design complete
- Filter option design complete
- Combined usage examples provided
- Error handling strategy defined
- Help text templates created
- Ready for implementation

---

## Task 1.4: Design Filtering Logic

### Objective
Define how filtering will be implemented and applied.

### Deliverables

1. **Filter Logic Design**
   ```
   Filter: functions-only
   - Exclude procedures (functions with no return type)
   - Keep functions with return types
   - Applied after query execution
   
   Filter: no-metrics
   - Remove complexity and LOC fields
   - Keep signature and file info
   - Applied during format generation
   
   Filter: no-file-info
   - Remove file path and line number
   - Keep signature and metrics
   - Applied during format generation
   ```

2. **Filter Application Order**
   ```
   1. Execute query (get all results)
   2. Apply functions-only filter (if specified)
   3. Apply format (concise, hover, or completion)
   4. Apply no-metrics filter (if specified)
   5. Apply no-file-info filter (if specified)
   6. Return formatted results
   ```

3. **Filter Combination Rules**
   ```
   - Multiple filters can be combined
   - Filters are applied in order
   - Filters are cumulative (AND logic)
   - Invalid filter combinations are rejected
   
   Examples:
   - functions-only + no-metrics = functions only, no metrics
   - functions-only + no-file-info = functions only, no file info
   - no-metrics + no-file-info = no metrics, no file info
   - All three = functions only, no metrics, no file info
   ```

4. **Filter Implementation Strategy**
   ```
   Option A: Implement in Python (query_db.py)
   - Pros: Centralized, reusable
   - Cons: Requires Python changes
   
   Option B: Implement in Bash (query.sh)
   - Pros: Simpler, no Python changes
   - Cons: Less efficient
   
   Recommendation: Option A (Python)
   - Implement filter functions in query_db.py
   - Call from query.sh wrapper
   - Reusable across all query commands
   ```

5. **Filter Validation**
   ```
   - Validate filter names
   - Reject invalid filters
   - Provide helpful error messages
   - Support case-insensitive matching
   ```

### Acceptance Criteria
- Filter logic precisely defined
- Application order documented
- Combination rules specified
- Implementation strategy chosen
- Validation approach defined
- Ready for implementation

---

## Task 1.5: Create Implementation Plan

### Objective
Create a detailed implementation plan for Phase 2 (Core Implementation).

### Deliverables

1. **Phase 2 Implementation Plan**
   - Task breakdown for each format generator
   - Task breakdown for option parser
   - Task breakdown for filtering logic
   - Task breakdown for query integration
   - Task breakdown for error handling
   - Estimated effort for each task
   - Dependencies between tasks

2. **Implementation Architecture**
   ```
   query.sh (Bash wrapper)
   ├── Parse --format option
   ├── Parse --filter options
   └── Call query_db.py with options
   
   query_db.py (Python)
   ├── Execute query
   ├── Apply functions-only filter
   ├── Generate format (concise, hover, or completion)
   ├── Apply no-metrics filter
   ├── Apply no-file-info filter
   └── Return formatted results
   
   Format Generators (Python)
   ├── generate_concise_format()
   ├── generate_hover_format()
   └── generate_completion_format()
   
   Filter Functions (Python)
   ├── filter_functions_only()
   ├── filter_no_metrics()
   └── filter_no_file_info()
   ```

3. **File Changes Required**
   ```
   Modify:
   - scripts/query_db.py (add format and filter logic)
   - query.sh (add --format and --filter options)
   
   Create:
   - scripts/format_generators.py (new file for format functions)
   - scripts/filter_functions.py (new file for filter functions)
   
   Test:
   - tests/test_format_generators.py (new test file)
   - tests/test_filter_functions.py (new test file)
   - tests/test_query_integration.py (update existing)
   ```

4. **Implementation Sequence**
   ```
   Phase 2 (Core Implementation):
   1. Create format_generators.py with three format functions
   2. Create filter_functions.py with three filter functions
   3. Update query_db.py to use format and filter functions
   4. Update query.sh to parse --format and --filter options
   5. Add error handling and validation
   
   Phase 3 (Testing):
   1. Write unit tests for each format generator
   2. Write unit tests for each filter function
   3. Write integration tests with query commands
   4. Write backward compatibility tests
   5. Write performance tests
   
   Phase 4 (Documentation):
   1. Document all formats with examples
   2. Document format and filter options
   3. Create Vim plugin integration guide
   4. Update existing documentation
   ```

5. **Risk Mitigation**
   ```
   Risk: Performance degradation
   - Mitigation: Performance tests in Phase 3
   - Target: <100ms for typical codebases
   
   Risk: Backward compatibility issues
   - Mitigation: Comprehensive backward compatibility tests
   - Ensure default behavior unchanged
   
   Risk: Incomplete documentation
   - Mitigation: Documentation review before release
   - Include examples for all formats
   
   Risk: Missing edge cases
   - Mitigation: Comprehensive test coverage (>90%)
   - Test all edge cases in Phase 3
   ```

6. **Success Criteria**
   - [ ] All Phase 1 design tasks complete
   - [ ] Implementation plan documented
   - [ ] Architecture defined
   - [ ] File changes identified
   - [ ] Implementation sequence clear
   - [ ] Risk mitigation strategies defined
   - [ ] Ready to begin Phase 2

### Acceptance Criteria
- Detailed implementation plan created
- Architecture documented
- File changes identified
- Implementation sequence clear
- Risk mitigation strategies defined
- Ready to begin Phase 2 (Core Implementation)

---

## Phase 1 Completion Checklist

### Task 1.1: Review Requirements
- [x] Requirements understood
- [x] Acceptance criteria clear
- [x] Edge cases identified
- [x] Performance targets confirmed
- [x] Backward compatibility confirmed

### Task 1.2: Design Output Formats
- [x] Concise format specified
- [x] Hover format specified
- [x] Completion format specified (tab-separated)
- [x] Examples provided
- [x] Edge cases documented

### Task 1.3: Design Command-Line Interface
- [x] Format option design complete
- [x] Filter option design complete
- [x] Combined usage examples provided
- [x] Error handling strategy defined
- [x] Help text templates created

### Task 1.4: Design Filtering Logic
- [x] Filter logic defined
- [x] Application order documented
- [x] Combination rules specified
- [x] Implementation strategy chosen
- [x] Validation approach defined

### Task 1.5: Create Implementation Plan
- [x] Phase 2 plan created
- [x] Architecture documented
- [x] File changes identified
- [x] Implementation sequence clear
- [x] Risk mitigation strategies defined

---

## Next Steps

1. **Complete Phase 1 Tasks**
   - Mark all Phase 1 tasks as complete
   - Review and approve design documents

2. **Begin Phase 2 (Core Implementation)**
   - Create format_generators.py
   - Create filter_functions.py
   - Update query_db.py
   - Update query.sh
   - Add error handling

3. **Proceed to Phase 3 (Testing)**
   - Write comprehensive tests
   - Verify >90% coverage
   - Performance testing

4. **Complete Phase 4 (Documentation)**
   - Document all formats
   - Create integration guide
   - Update existing docs

---

## References

- [Requirements Document](requirements.md)
- [Specification Summary](SPEC_SUMMARY.md)
- [Completion Format Rationale](COMPLETION_FORMAT_RATIONALE.md)
- [Format Examples](FORMAT_EXAMPLES.md)
- [Implementation Roadmap](.kiro/docs/IMPLEMENTATION_ROADMAP.md)

---

**Status:** Phase 1 In Progress  
**Created:** March 25, 2026  
**Version:** 1.0
