# Feature 1.1: Refined Output for Vim Plugin - Specification Summary

## Overview

This specification defines Feature 1.1: Refined Output for Vim Plugin from the genero-tools implementation roadmap. The feature creates optimized output formats for Vim plugin integration, enabling better editor integration with concise, hover-friendly, and completion-friendly output formats.

## Feature Context

- **Project:** genero-tools v2.1.0+
- **Feature ID:** 1.1
- **Priority:** HIGH
- **Effort:** 1-2 days
- **Business Value:** Better Vim plugin integration with concise output
- **Dependencies:** Phase 2 (Type Resolution v2.1.0) - COMPLETE

## Problem Statement

The current genero-tools query interface returns output in a single format that is not optimized for Vim plugin use. Vim plugins need:
1. **Concise signatures** for efficient display in tooltips and completion menus
2. **Hover-friendly output** with file location and complexity metrics
3. **Completion-friendly JSON** for easy parsing and autocomplete suggestions

Currently, Vim plugins must parse the default output format and extract relevant information, which is inefficient and error-prone.

## Solution Overview

Implement three new output formats optimized for Vim plugin use:

1. **Concise Format** (`--format=vim`): Single-line function signatures
   - Example: `my_function(param1: INTEGER, param2: VARCHAR) -> DECIMAL`

2. **Hover Format** (`--format=vim-hover`): Multi-line with metadata
   - Example:
     ```
     my_function(param1: INTEGER, param2: VARCHAR) -> DECIMAL
     File: src/module.4gl:42
     Complexity: 5, LOC: 23
     ```

3. **Completion Format** (`--format=vim-completion`): Tab-separated for Vim/Neovim completion
   - Example:
     ```
     my_function	function(param1: INTEGER, param2: VARCHAR) -> DECIMAL	src/module.4gl:42 | Complexity: 5, LOC: 23
     get_account	function(id: INTEGER) -> RECORD	src/queries.4gl:128 | Complexity: 3, LOC: 15
     ```

## Key Features

### 1. Output Formats
- **Concise Format**: Compact single-line signatures for tooltips
- **Hover Format**: Multi-line with file location and metrics
- **Completion Format**: JSON for autocomplete parsing

### 2. Format Options
- `--format=vim`: Concise format
- `--format=vim-hover`: Hover format
- `--format=vim-completion`: Completion format
- Default (no option): Current behavior (backward compatible)

### 3. Filtering Options
- `--filter=functions-only`: Exclude procedures
- `--filter=no-metrics`: Exclude complexity metrics
- `--filter=no-file-info`: Exclude file path and line number
- Multiple filters can be combined

### 4. Query Command Integration
- Works with all query commands that return function metadata
- `find-function`, `search-functions`, `list-file-functions`, etc.
- Fully backward compatible with existing queries

### 5. Error Handling
- Clear error messages for invalid format/filter options
- Helpful suggestions for common issues
- Graceful handling of missing metadata

## Requirements Summary

### 10 Core Requirements

1. **Concise Signature Format** - Single-line function signatures with name, params, and return type
2. **Hover-Friendly Format** - Multi-line format with signature, file location, and complexity metrics
3. **Completion-Friendly Format** - JSON format with all metadata for autocomplete
4. **Format Option** - Command-line `--format` option to select output format
5. **Filtering** - Command-line `--filter` option to customize output
6. **Backward Compatibility** - Existing queries work unchanged
7. **Comprehensive Tests** - >90% code coverage for all formats and filters
8. **Documentation** - Complete documentation with examples
9. **Query Integration** - Format options work with all query commands
10. **Error Handling** - Clear error messages and validation

## Success Criteria

- ✅ Concise output format for Vim
- ✅ Hover-friendly format with metadata
- ✅ Completion-friendly JSON format
- ✅ Format options work with all query commands
- ✅ Filtering options reduce output size
- ✅ Backward compatibility maintained
- ✅ Comprehensive tests pass (>90% coverage)
- ✅ Complete documentation with examples
- ✅ Query execution time <100ms
- ✅ Error handling and validation

## Implementation Phases

### Phase 1: Design & Planning (0.5 days)
- Review requirements with team
- Design output format specifications
- Design command-line interface
- Create implementation plan

### Phase 2: Core Implementation (0.5 days)
- Implement format generators (concise, hover, completion)
- Implement format option parser
- Implement filtering logic
- Integrate with query commands
- Add error handling

### Phase 3: Testing (0.5 days)
- Unit tests for each format
- Integration tests with query commands
- Backward compatibility tests
- Performance tests
- Verify >90% coverage

### Phase 4: Documentation (0.5 days)
- Document all formats with examples
- Document format and filter options
- Create Vim plugin integration guide
- Update existing documentation

**Total Effort: 1-2 days**

## Testing Strategy

### Unit Tests
- Test each format generator independently
- Test edge cases (no params, no returns, multiple returns)
- Test format option parsing
- Test filtering logic
- Test error handling

### Integration Tests
- Test with all query commands
- Test with real function data
- Test backward compatibility
- Test performance (<100ms)

### Test Coverage
- Target: >90% code coverage
- All format types tested
- All filters tested
- All error conditions tested

## Documentation Deliverables

1. **Format Reference** - Complete documentation of all output formats
2. **Usage Guide** - How to use format and filter options
3. **Code Examples** - Examples for each format and use case
4. **Vim Plugin Guide** - Integration guide for Vim plugin developers
5. **API Documentation** - Python API for format generators
6. **Troubleshooting** - Common issues and solutions

## Performance Targets

- Query execution time: <100ms for typical codebases
- Output generation time: <10ms
- Memory usage: <10MB for typical result sets
- No performance degradation for existing queries

## Backward Compatibility

- ✅ Existing queries work unchanged
- ✅ Default output format unchanged
- ✅ All existing tests pass
- ✅ No breaking changes to API
- ✅ Fully compatible with v2.1.0

## Dependencies

- **Required:** Type Resolution v2.1.0 (COMPLETE)
- **Optional:** Vim plugin for testing

## Risks & Mitigation

| Risk | Mitigation |
|------|-----------|
| Performance degradation | Performance tests, optimization if needed |
| Backward compatibility issues | Comprehensive backward compatibility tests |
| Incomplete documentation | Documentation review before release |
| Missing edge cases | Comprehensive test coverage (>90%) |

## Next Steps

1. Review and approve requirements
2. Begin Phase 1: Design & Planning
3. Implement core functionality (Phase 2)
4. Execute comprehensive testing (Phase 3)
5. Complete documentation (Phase 4)
6. Verify and release

## Related Features

- **1.2 Table Definition Queries** - Complementary feature for table/column lookups
- **1.3 RECORD/ARRAY Type Resolution** - Enhanced type support
- **3.2 Vim Plugin Integration** - Uses these output formats

## References

- [Implementation Roadmap](.kiro/docs/IMPLEMENTATION_ROADMAP.md)
- [Requirements Document](requirements.md)
- [Completion Format Rationale](COMPLETION_FORMAT_RATIONALE.md)
- [QUERYING.md](docs/QUERYING.md)
- [FEATURES.md](docs/FEATURES.md)
- [TYPE_RESOLUTION_RELEASE_NOTES_v2_1_0.md](docs/TYPE_RESOLUTION_RELEASE_NOTES_v2_1_0.md)

---

**Status:** Requirements Complete - Ready for Design Phase  
**Created:** 2026-03-24  
**Version:** 1.0
