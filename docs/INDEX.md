# Documentation Index

This document provides a comprehensive index of all documentation in the genero-func-sigs project.

## Getting Started

- **[README.md](../README.md)** - Project overview, features, and quick start guide
- **[QUICK_START_CALL_GRAPH.md](QUICK_START_CALL_GRAPH.md)** - Quick start for call graph queries
- **[QUICK_START_HEADERS.md](QUICK_START_HEADERS.md)** - Quick start for file header parsing
- **[QUICK_START_TYPE_RESOLUTION.md](QUICK_START_TYPE_RESOLUTION.md)** - Quick start for type resolution

## Core Documentation

### Architecture & Design

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture and component design
- **[DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)** - Guide for developers contributing to the project
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and changes

### Features & Capabilities

- **[QUERYING.md](QUERYING.md)** - Complete guide to querying the database
- **[QUERY_LAYER_GUIDE.md](QUERY_LAYER_GUIDE.md)** - Guide to Phase 2 query layer and metrics
- **[CALL_GRAPH_QUERIES.md](CALL_GRAPH_QUERIES.md)** - Detailed call graph query documentation
- **[SCHEMA_PARSING_GUIDE.md](SCHEMA_PARSING_GUIDE.md)** - Guide to database schema parsing
- **[TYPE_RESOLUTION_GUIDE.md](TYPE_RESOLUTION_GUIDE.md)** - Guide to type resolution system

### Implementation Details

- **[MODULE_GENERATOR.md](MODULE_GENERATOR.md)** - Module generation implementation
- **[SECURITY.md](SECURITY.md)** - Security practices and considerations

## Archived Documentation

The following documents have been archived as they document completed phases:

- `archive/DOCUMENTATION_AUDIT.md` - Phase 1 documentation audit
- `archive/REVIEW_FINDINGS.md` - Phase 1 review findings
- `archive/HEADER_PARSING_ANALYSIS.md` - Phase 1 header parsing analysis
- `archive/HEADER_PARSING_IMPLEMENTATION.md` - Phase 1 header parsing implementation
- `archive/IMPLEMENTATION_SUMMARY.md` - Phase 1 implementation summary
- `archive/FUTURE_ENHANCEMENTS.md` - Phase 1 future enhancements (superseded by Phase 2)
- `archive/AUTOMATED_WORKFLOW.md` - Phase 1 automated workflow documentation

See [archive/](archive/) for complete archived documentation.

## Spec Documentation

Detailed specifications and implementation plans are located in `.kiro/specs/`:

- `.kiro/specs/PHASE_1_SPECIFICATION.md` - Phase 1 specification
- `.kiro/specs/code-quality-analysis/` - Phase 2 specification and implementation details

Archived specs are in `.kiro/specs/archive/`:
- Phase 1 completion reports
- Phase 1 implementation checklists
- Phase 1 test results

## Documentation Organization

### By Topic

**Function Signatures & Metadata:**
- README.md (overview)
- ARCHITECTURE.md (design)
- QUERYING.md (usage)

**Call Graphs & Dependencies:**
- QUICK_START_CALL_GRAPH.md (quick start)
- CALL_GRAPH_QUERIES.md (detailed guide)
- ARCHITECTURE.md (design)

**File Headers & References:**
- QUICK_START_HEADERS.md (quick start)
- ARCHITECTURE.md (design)

**Code Quality & Metrics (Phase 2):**
- QUERY_LAYER_GUIDE.md (complete guide)
- ARCHITECTURE.md (design)
- README.md (overview)

**Type Resolution & Schema:**
- QUICK_START_TYPE_RESOLUTION.md (quick start)
- TYPE_RESOLUTION_GUIDE.md (detailed guide)
- SCHEMA_PARSING_GUIDE.md (schema parsing)
- ARCHITECTURE.md (design)

**Development & Contribution:**
- DEVELOPER_GUIDE.md (contribution guide)
- ARCHITECTURE.md (system design)
- CHANGELOG.md (version history)

**Security & Best Practices:**
- SECURITY.md (security practices)
- README.md (requirements and setup)

### By Audience

**For End Users:**
- README.md - Start here
- QUICK_START_*.md - Feature-specific quick starts
- QUERYING.md - How to query the database
- QUERY_LAYER_GUIDE.md - How to use metrics

**For Developers:**
- DEVELOPER_GUIDE.md - Contributing guide
- ARCHITECTURE.md - System design
- CHANGELOG.md - Version history

**For DevOps/Integration:**
- README.md - Setup and requirements
- ARCHITECTURE.md - System design
- SECURITY.md - Security practices

**For Security Review:**
- SECURITY.md - Security practices
- README.md - Requirements
- ARCHITECTURE.md - Design decisions

## Key Concepts

### Metadata Extraction
The project extracts rich metadata from Genero/4GL codebases:
- Function signatures (names, parameters, returns)
- Call graphs (which functions call which)
- File headers (code references, authors)
- Code metrics (complexity, LOC, parameters)

### Database Approach
For efficient querying of large codebases:
- JSON files for initial extraction
- SQLite databases for indexed queries
- Query layer for convenient access

### Phase-Based Development
The project is developed in phases:
- **Phase 1:** Function signatures, call graphs, file headers
- **Phase 2:** Code quality metrics and analysis (COMPLETE)
- **Phase 3:** Advanced analysis (planned)

## Finding Information

### I want to...

**Get started quickly:**
→ Start with [README.md](../README.md)

**Learn about a specific feature:**
→ See "By Topic" section above

**Understand the system architecture:**
→ Read [ARCHITECTURE.md](ARCHITECTURE.md)

**Contribute to the project:**
→ Read [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)

**Query the database:**
→ Read [QUERYING.md](QUERYING.md)

**Analyze code metrics:**
→ Read [QUERY_LAYER_GUIDE.md](QUERY_LAYER_GUIDE.md)

**Understand security practices:**
→ Read [SECURITY.md](SECURITY.md)

**See what's changed:**
→ Read [CHANGELOG.md](CHANGELOG.md)

## Documentation Maintenance

This documentation is maintained alongside the code:
- Updated with each feature release
- Archived when superseded by newer documentation
- Reviewed for accuracy and completeness
- Organized for easy navigation

For questions or suggestions about documentation, please open an issue or contact the maintainers.
