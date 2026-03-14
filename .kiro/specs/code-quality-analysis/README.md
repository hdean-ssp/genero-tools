# Phase 2: Code Quality Analysis & Metrics Specification

## Overview

This directory contains the complete Phase 2 specification for the "Code Quality Analysis & Metrics" feature. Phase 2 extends Phase 1 (database schema parsing and type resolution) with comprehensive code quality metrics extraction, analysis queries, and incremental generation for IDE/AI agent integration.

## Documents

### 1. [PHASE_2_SUMMARY.md](PHASE_2_SUMMARY.md)
**Start here** - Executive summary of Phase 2 with key features, architecture, and timeline.

**Contents:**
- Executive summary
- Key features overview
- Architecture diagram
- Data models
- Performance targets
- Implementation phases
- Success criteria

**Read this if:** You want a high-level overview of Phase 2

---

### 2. [design.md](design.md)
**Detailed technical design** - Complete system architecture, components, algorithms, and data models.

**Contents:**
- System architecture with data flow
- Component interfaces and responsibilities
- Data models (FunctionMetrics, FileMetrics, etc.)
- Algorithmic pseudocode with formal specifications
- Key functions with preconditions/postconditions
- Example usage for all major features
- Correctness properties
- Error handling strategies
- Testing strategy
- Performance considerations
- Security considerations
- Database schema
- Configuration examples

**Read this if:** You're implementing Phase 2 or need detailed technical understanding

---

### 3. [requirements.md](requirements.md)
**Functional and non-functional requirements** - Detailed requirements derived from the design.

**Contents:**
- 19 functional requirements (FR1-FR5)
  - FR1: Metrics Extraction (6 sub-requirements)
  - FR2: Code Quality Analysis Queries (5 sub-requirements)
  - FR3: Incremental Generation (4 sub-requirements)
  - FR4: Data Storage and Querying (2 sub-requirements)
  - FR5: Configuration Management (2 sub-requirements)
- 5 non-functional requirements (NFR1-NFR5)
  - NFR1: Performance
  - NFR2: Scalability
  - NFR3: Reliability
  - NFR4: Maintainability
  - NFR5: Security
- Acceptance criteria for each requirement
- Test cases
- Traceability matrix

**Read this if:** You need to validate implementation against requirements

---

### 4. [tasks.md](tasks.md)
**Implementation tasks** - Concrete, actionable tasks organized by component.

**Contents:**
- 30 implementation tasks organized into 5 phases
  - Phase 2a: Core Metrics Extraction Engine (8 tasks)
  - Phase 2b: Code Quality Analysis Queries (6 tasks)
  - Phase 2c: Incremental Generation Engine (4 tasks)
  - Phase 2d: Database Integration & Optimization (4 tasks)
  - Phase 2e: Testing & Documentation (10 tasks)
- Task dependencies graph
- Implementation timeline (4-5 weeks)
- Effort estimates
- Success criteria

**Read this if:** You're planning implementation or assigning work

---

## Quick Reference

### Key Metrics Extracted
1. **Lines of Code (LOC)** - Executable code lines (excludes comments/blanks)
2. **Cyclomatic Complexity** - Control flow complexity (IF/ELSE/WHILE/FOR/CASE)
3. **Local Variables** - Count of DEFINE statements
4. **Comments** - Comment lines and comment ratio
5. **Call Depth** - Maximum nesting depth of function calls
6. **Early Returns** - Count of early RETURN statements

### Query Types
1. **Find Complex Functions** - Query by complexity, LOC, parameters
2. **Find Similar Functions** - Detect code duplication candidates
3. **Find Isolated Functions** - Functions with no dependencies
4. **Find by Metrics** - Query with multiple metric criteria
5. **Naming Conventions** - Validate against configurable patterns

### Performance Targets
- File metrics extraction: <500ms
- Function metrics extraction: <100ms
- Database queries: <100ms
- Incremental generation: 10x faster than full

### Implementation Timeline
- **Week 1:** Core Metrics Extraction (Phase 2a)
- **Week 2:** Quality Analysis & Database (Phase 2b-2d)
- **Week 3:** Incremental Generation & Testing (Phase 2c, 2e.1-2e.6)
- **Week 4:** Documentation & Polish (Phase 2e.7-2e.10)

**Total: 4-5 weeks**

---

## Architecture Overview

```
Source Code Files (.4gl)
    ↓
Enhanced Parser with Metrics
    ├── LOC Counting
    ├── Complexity Calculation
    ├── Variable Counting
    ├── Comment Extraction
    ├── Call Depth Analysis
    └── Early Return Detection
    ↓
Metrics Data
    ↓
workspace.json (Enhanced)
    ↓
workspace.db (Metrics Tables)
    ↓
Query Layer
    ├── Complex Functions Query
    ├── Similar Functions Query
    ├── Isolated Functions Query
    ├── Metrics Threshold Query
    └── Naming Conventions Query
    ↓
IDE/AI Agents (Real-time Analysis)
```

---

## Files to Create

### Python Scripts (6 files)
- `scripts/metrics_extractor.py` - Core metrics extraction
- `scripts/metrics_models.py` - Data classes
- `scripts/quality_analyzer.py` - Quality analysis queries
- `scripts/incremental_generator.py` - Incremental generation
- `scripts/create_metrics_schema.py` - Database schema
- `scripts/metrics_db.py` - Database integration

### Tests (6 files)
- `tests/test_metrics_extraction.py`
- `tests/test_quality_analyzer.py`
- `tests/test_incremental_generator.py`
- `tests/test_phase2_integration.py`
- `tests/test_phase2_properties.py`
- `tests/test_phase2_performance.py`

### Configuration (2 files)
- `config/naming_conventions.example.json`
- `config/quality_thresholds.example.json`

### Documentation (5 files)
- `docs/METRICS_USER_GUIDE.md`
- `docs/METRICS_API.md`
- `docs/METRICS_CONFIG.md`
- `docs/METRICS_ARCHITECTURE.md`
- `docs/METRICS_TESTING.md`

### Files to Modify (4 files)
- `scripts/query_db.py` - Add metrics queries
- `README.md` - Update with Phase 2 features
- `docs/ARCHITECTURE.md` - Update with Phase 2 components
- `docs/CHANGELOG.md` - Document Phase 2 changes

---

## Key Data Models

### FunctionMetrics
```python
@dataclass
class FunctionMetrics:
    name: str
    file_path: str
    line_start: int
    line_end: int
    loc: int                    # Lines of code
    complexity: int             # Cyclomatic complexity
    local_variables: int        # DEFINE count
    parameters: int             # Parameter count
    return_count: int           # RETURN count
    call_depth: int             # Max nesting depth
    early_returns: int          # Early RETURN count
    comment_lines: int          # Comment line count
    comment_ratio: float        # comment_lines / loc
    calls_made: List[str]       # Functions this calls
    called_by: List[str]        # Functions that call this
    is_isolated: bool           # No dependencies
    has_dependencies: bool      # Called by others
```

### FileMetrics
```python
@dataclass
class FileMetrics:
    file_path: str
    total_loc: int              # Total lines of code
    comment_loc: int            # Lines with comments
    blank_loc: int              # Blank lines
    function_count: int         # Number of functions
    average_complexity: float   # Average complexity
    max_complexity: int         # Highest complexity
    average_function_loc: int   # Average LOC per function
    max_function_loc: int       # Largest function LOC
```

---

## Database Schema

### New Tables
- `function_metrics` - Function-level metrics
- `naming_violations` - Naming convention violations
- `duplication_candidates` - Code duplication candidates

### Indexes
- `idx_function_metrics_complexity` - For complexity queries
- `idx_function_metrics_loc` - For LOC queries
- `idx_function_metrics_isolated` - For isolated functions
- `idx_file_metrics_avg_complexity` - For file-level queries
- `idx_naming_violations_severity` - For violation queries
- `idx_duplication_similarity` - For duplication queries

---

## Success Criteria

### Functional Completeness
- [ ] All 19 functional requirements implemented
- [ ] All 5 non-functional requirements met
- [ ] All 30 tasks completed
- [ ] All acceptance criteria satisfied

### Quality Metrics
- [ ] >90% test coverage
- [ ] All tests passing
- [ ] No critical bugs
- [ ] Code review approved

### Performance
- [ ] File metrics: <500ms
- [ ] Function metrics: <100ms
- [ ] Database queries: <100ms
- [ ] Incremental generation: 10x faster than full

### Documentation
- [ ] User guide complete
- [ ] API documentation complete
- [ ] Configuration guide complete
- [ ] Developer documentation complete

### Compatibility
- [ ] No breaking changes to Phase 1
- [ ] Backward compatible with existing workspace.json
- [ ] Existing queries continue to work

---

## Related Documents

### Phase 1 (Foundation)
- `.kiro/specs/PHASE_1_SPECIFICATION.md` - Phase 1 design and requirements

### Project Documentation
- `README.md` - Project overview
- `docs/ARCHITECTURE.md` - System architecture
- `docs/DEVELOPER_GUIDE.md` - Developer guide
- `docs/QUERY_LAYER_GUIDE.md` - Query layer documentation

---

## Getting Started

### For Project Managers
1. Read [PHASE_2_SUMMARY.md](PHASE_2_SUMMARY.md) for overview
2. Review [tasks.md](tasks.md) for timeline and effort estimates
3. Use success criteria to track progress

### For Developers
1. Read [PHASE_2_SUMMARY.md](PHASE_2_SUMMARY.md) for overview
2. Study [design.md](design.md) for technical details
3. Review [requirements.md](requirements.md) for acceptance criteria
4. Use [tasks.md](tasks.md) to plan implementation

### For QA/Testers
1. Read [PHASE_2_SUMMARY.md](PHASE_2_SUMMARY.md) for overview
2. Review [requirements.md](requirements.md) for acceptance criteria
3. Study [design.md](design.md) for testing strategy
4. Use [tasks.md](tasks.md) for test planning

---

## Questions?

Refer to the appropriate document:
- **What is Phase 2?** → [PHASE_2_SUMMARY.md](PHASE_2_SUMMARY.md)
- **How does it work?** → [design.md](design.md)
- **What needs to be built?** → [requirements.md](requirements.md)
- **How do I implement it?** → [tasks.md](tasks.md)
- **What are the acceptance criteria?** → [requirements.md](requirements.md)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-13 | Initial Phase 2 specification |

---

## Approval

- [ ] Design approved
- [ ] Requirements approved
- [ ] Tasks approved
- [ ] Ready for implementation

---

## Contact

For questions or clarifications about this specification, please refer to the project documentation or contact the development team.
