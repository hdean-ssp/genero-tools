# Phase 1 Specification - Database Schema Parsing & Type Resolution

## Overview

Phase 1 establishes the foundation for a type-aware codebase analysis system by implementing database schema parsing and enhanced type resolution. This enables the system to understand what types functions are actually working with, not just their names.

## Goals

1. **Parse database schemas** - Extract table and column definitions from SQL/Genero schema files
2. **Resolve LIKE types** - Map `LIKE contract.*` references to actual table definitions
3. **Enable type-aware queries** - Query functions by the types they use

## Why Phase 1 is Critical

- **Foundation for all downstream features** - Type information is needed for validation, analysis, and AI review
- **Enables real type resolution** - Can answer "what does this function actually work with?"
- **Detects real errors** - Can find calls to non-existent tables/columns
- **Supports IDE integration** - Can show actual database types in hover information
- **Enables AI analysis** - AI agents can understand data flow and dependencies

## Architecture

### Data Flow

```
Database Schema Files (.sch - Informix IDS format)
    ↓
Schema Parser (scripts/parse_schema.py)
    ↓
Schema Index (schema.json - pipe-delimited format)
    ↓
json_to_sqlite.py
    ↓
workspace.db (new tables: schema_tables, schema_columns)
    ↓
Enhanced Type Parser (in generate_signatures.sh)
    ↓
workspace.json (enhanced with resolved types)
    ↓
Query Layer (scripts/query_db.py)
    ↓
Type Resolution Queries
```

### Schema Format (Informix IDS)

The `.sch` file uses pipe-delimited format:
```
table_name^column_name^type_code^length^position^
```

**Example:**
```
account^acc_code^0^8^1^
account^acc_type^0^2^2^
account^acc_balance^5^3842^6^
account^acc_del_date^7^4^8^
```

**Type Code Mapping:**
- `0` → VARCHAR(length)
- `1` → SMALLINT
- `2` → INTEGER
- `5` → DECIMAL(length)
- `7` → DATE
- `10` → DATETIME
- `262` → SERIAL

### Database Schema

**New Tables in workspace.db:**

```sql
-- Schema tables
schema_tables (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    source_file TEXT,
    line_number INTEGER
)

-- Schema columns
schema_columns (
    id INTEGER PRIMARY KEY,
    table_id INTEGER NOT NULL,
    column_name TEXT NOT NULL,
    column_type TEXT NOT NULL,
    FOREIGN KEY (table_id) REFERENCES schema_tables(id)
)
```

## Implementation Plan

### Step 1: Schema Parser (scripts/parse_schema.py)

**Input:** Informix IDS `.sch` files (pipe-delimited format)

**Output:** JSON schema index

**Functionality:**
- Parse pipe-delimited schema format
- Extract table names, column names, types, lengths
- Map Informix type codes to Genero types
- Handle multiple schema files
- Generate schema.json

**Type Code Mapping:**
```
0   → VARCHAR(length)
1   → SMALLINT
2   → INTEGER
5   → DECIMAL(length)
7   → DATE
10  → DATETIME
262 → SERIAL
```

**Example Input (schema.sch):**
```
account^acc_code^0^8^1^
account^acc_type^0^2^2^
account^acc_balance^5^3842^6^
account^acc_del_date^7^4^8^
```

**Example Output (schema.json):**
```json
{
  "tables": [
    {
      "name": "account",
      "columns": [
        {"name": "acc_code", "type": "VARCHAR(8)", "type_code": 0, "length": 8, "position": 1},
        {"name": "acc_type", "type": "VARCHAR(2)", "type_code": 0, "length": 2, "position": 2},
        {"name": "acc_balance", "type": "DECIMAL(3842)", "type_code": 5, "length": 3842, "position": 6},
        {"name": "acc_del_date", "type": "DATE", "type_code": 7, "length": 4, "position": 8}
      ]
    }
  ]
}
```

**Algorithm:**
```python
def parse_schema_file(filename):
    schema = {"tables": {}}
    
    with open(filename, 'r') as f:
        for line in f:
            if not line.strip():
                continue
            
            # Parse: table^column^type^length^position^
            parts = line.strip().split('^')
            if len(parts) < 5:
                continue
            
            table_name = parts[0]
            column_name = parts[1]
            type_code = int(parts[2])
            length = int(parts[3])
            position = int(parts[4])
            
            # Map type code to Genero type
            genero_type = map_type_code(type_code, length)
            
            # Add to schema
            if table_name not in schema["tables"]:
                schema["tables"][table_name] = {
                    "name": table_name,
                    "columns": []
                }
            
            schema["tables"][table_name]["columns"].append({
                "name": column_name,
                "type": genero_type,
                "type_code": type_code,
                "length": length,
                "position": position
            })
    
    return schema
```

### Step 2: Enhanced Type Parser (in generate_signatures.sh)

**Current:** Extracts parameter types as strings (e.g., "LIKE contract.id")

**Enhanced:** Resolves LIKE references to actual table definitions

**Functionality:**
- Detect LIKE references in parameter types
- Extract table and column names
- Look up in schema index
- Store resolved type information
- Flag unresolved references

**Example:**
```4gl
FUNCTION process_contract(c LIKE contract.*)
```

**Current Output:**
```json
{
  "parameters": [
    {"name": "c", "type": "LIKE contract.*"}
  ]
}
```

**Enhanced Output:**
```json
{
  "parameters": [
    {
      "name": "c",
      "type": "LIKE contract.*",
      "resolved_table": "contract",
      "resolved_columns": ["id", "name", "amount", "created_date"],
      "resolved_types": ["INTEGER", "VARCHAR(100)", "DECIMAL(10,2)", "DATE"]
    }
  ]
}
```

### Step 3: Type Validation Engine

**Functionality:**
- Check if LIKE references exist in schema
- Validate column types match function parameters
- Detect type mismatches
- Generate validation reports

**Validation Rules:**
1. LIKE references must exist in schema
2. Column types must be compatible
3. Record types must have matching fields
4. Function calls must have compatible parameter types

**Output:** Type validation report

### Step 4: Query Layer Enhancement (scripts/query_db.py)

## Implementation Phases

### Phase 1a: Schema Parser
- Create scripts/parse_schema.py
- Support SQL DDL parsing
- Support Genero .sch parsing
- Generate schema.json
- Tests for schema parsing

**Deliverables:**
- scripts/parse_schema.py
- Schema parser tests
- schema.json output

### Phase 1b: Database Integration
- Create schema tables in workspace.db
- Create scripts/json_to_sqlite_schema.py
- Integrate schema data into database
- Create indexes on schema tables

**Deliverables:**
- Updated workspace.db schema
- scripts/json_to_sqlite_schema.py
- Schema table indexes

### Phase 1c: Enhanced Type Parser
- Update generate_signatures.sh to detect LIKE references
- Resolve LIKE references to schema
- Store resolved type information
- Update workspace.json format

**Implementation Details:**
1. Create `scripts/resolve_types.py` - Type resolution engine ✅
   - Load schema from workspace.db
   - Parse LIKE references from workspace.json
   - Resolve table/column references
   - Generate resolved type information
   - Handle edge cases (missing tables, columns)

2. Update `generate_signatures.sh` ✅
   - Call resolve_types.py after generating workspace.json
   - Pass schema.db path and workspace.json path
   - Merge resolved type info back into workspace.json

3. Type Resolution Algorithm: ✅
   - Pattern: `LIKE table.column` or `LIKE table.*`
   - Extract table name and column pattern
   - Query schema_tables and schema_columns
   - Return resolved columns and types
   - Mark unresolved references

**Deliverables:**
- scripts/resolve_types.py (type resolution engine) ✅
- Updated generate_signatures.sh (integration) ✅
- Enhanced workspace.json with resolved types ✅
- Type resolution tests (tests/test_type_resolution.py) ✅
- Integration tests (tests/test_phase1c_integration.py) ✅
- Documentation (docs/TYPE_RESOLUTION_GUIDE.md) ✅

**Status: ✅ COMPLETE - 16 tests passing**

### Phase 1d: Query Layer
- Create new query functions in scripts/query_db.py
- Create shell command wrappers in src/query.sh
- Create query tests

**Deliverables:**
- Updated scripts/query_db.py
- Updated src/query.sh
- Query tests

## Data Model Changes

### workspace.json Enhancement

**Current:**
```json
{
  "name": "process_contract",
  "parameters": [
    {"name": "c", "type": "LIKE contract.*"}
  ]
}
```

**Enhanced:**
```json
{
  "name": "process_contract",
  "parameters": [
    {
      "name": "c",
      "type": "LIKE contract.*",
      "resolved_table": "contract",
      "resolved_columns": ["id", "name", "amount", "created_date"],
      "resolved_types": ["INTEGER", "VARCHAR(100)", "DECIMAL(10,2)", "DATE"],
      "is_like_reference": true
    }
  ],
  "type_issues": []
}
```

### New Files

- **schema.json** - Parsed database schema
- **scripts/parse_schema.py** - Schema parser
- **scripts/json_to_sqlite_schema.py** - Schema to SQLite converter

## Testing Strategy

### Unit Tests

1. **Schema Parser Tests**
   - Parse SQL DDL files
   - Parse Genero .sch files
   - Handle various SQL dialects
   - Handle edge cases

2. **Type Resolution Tests**
   - Resolve LIKE references
   - Handle missing tables
   - Handle missing columns
   - Handle nested types

3. **Query Tests**
   - Test all new query functions
   - Test with various inputs
   - Test error handling

### Integration Tests

1. **End-to-end Schema Parsing**
   - Parse real schema files
   - Generate schema.json
   - Load into database
   - Query results

2. **End-to-end Type Resolution**
   - Parse functions with LIKE types
   - Resolve types
   - Query resolved types

### Test Data

- Sample SQL schema files
- Sample Genero .sch files
- Sample 4GL files with LIKE types
- Expected output files

## Success Criteria

- [ ] Schema parser handles 95%+ of SQL DDL
- [ ] LIKE type resolution works for all reference patterns
- [ ] All new queries execute in <100ms
- [ ] All tests passing (>90% coverage)
- [ ] Documentation updated
- [ ] No breaking changes to existing functionality

## Timeline Estimate

- Phase 1a (Schema Parser): ✅ Complete
- Phase 1b (Database Integration): ✅ Complete
- Phase 1c (Enhanced Type Parser): ✅ Complete
- Phase 1d (Query Layer): 1-2 days
- Testing & Documentation: ✅ Complete

**Total: Phase 1 ~90% complete, Phase 1d remaining**

## Dependencies

- Python 3.6+
- SQLite 3
- Bash shell
- Standard Unix utilities

## Risks & Mitigations

### Risk: Complex SQL Dialects
**Mitigation:** Start with standard SQL, add dialect support incrementally

### Risk: Performance Impact
**Mitigation:** Index schema tables, cache schema lookups

### Risk: Breaking Changes
**Mitigation:** Keep existing queries working, add new queries only

### Risk: Schema File Format Variations
**Mitigation:** Support multiple formats, graceful error handling

## Next Steps

1. ✅ Create Phase 1 specification (this document)
2. ✅ Create scripts/parse_schema.py
3. ✅ Create test data (sample schema files)
4. ✅ Implement schema parser
5. ✅ Implement database integration
6. ✅ Implement enhanced type parser
7. 🔄 Implement query layer
8. ✅ Create comprehensive tests
9. ✅ Update documentation

## Phase 1d: Query Layer (Next)

The query layer will enable:
- Query functions by the types they use
- Find all functions using a specific table
- Detect type mismatches
- Generate type validation reports

See [PHASE_1_SPECIFICATION.md](PHASE_1_SPECIFICATION.md#phase-1d-query-layer) for details.

## Conclusion

Phase 1 establishes a strong foundation for type-aware codebase analysis. By parsing database schemas and resolving LIKE references, the system can provide real type information to IDE plugins and AI agents, enabling more sophisticated analysis and integration.

This foundation enables all downstream features (Phase 2, 3) to work with actual type information rather than just type names. Type validation is deferred to compile-time checks during development.
