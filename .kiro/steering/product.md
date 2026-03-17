# Product Overview

## What is genero-tools?

A comprehensive codebase analysis tool that extracts and indexes rich metadata from Genero/4GL codebases to enable IDE/editor integration, AI-powered code review, and developer tooling.

## Core Purpose

Extract function signatures, module dependencies, code metrics, and metadata from large Genero/4GL codebases and provide efficient querying capabilities for:
- IDE/editor integration (Vim, VS Code, etc.)
- AI-powered code review and analysis
- Developer tooling (impact analysis, dead code detection, refactoring support)
- Architecture understanding and documentation

## Key Capabilities

- **Function Signature Extraction** - Names, parameters, return types, line numbers
- **Call Graph Analysis** - Track which functions call which other functions
- **File Header Parsing** - Extract code references and author information for impact analysis
- **Code Quality Metrics** - Lines of code, cyclomatic complexity, variable count, parameter count, return count, call depth
- **Type Resolution** - Resolve LIKE references to actual schema types, handle multi-instance functions
- **Structured Metadata** - JSON and SQLite databases for fast querying
- **Comprehensive Type Support** - All Genero data types including complex and special types

## Target Users

- **Developers** - Understanding codebase structure and dependencies
- **Code Reviewers** - Analyzing code quality and complexity
- **IDE/Editor Plugin Developers** - Integrating rich metadata into editors
- **AI Agents** - Automated code analysis and review
- **DevOps/Build Systems** - Dependency analysis and impact assessment

## Project Status

**Phase 1 (Complete):** Core signature and module extraction
**Phase 2 (Complete):** Code quality metrics, type resolution, batch queries, pagination
**Phase 3 (In Progress):** IDE/editor integration, advanced tooling

## Non-Goals

- Code duplication analysis (requires full function body analysis)
- Unresolved call detection (compiler already handles this)
- Circular dependency detection (not a priority)
- Visualization exports (better as separate project)
