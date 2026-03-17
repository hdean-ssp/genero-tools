#!/usr/bin/env python3
"""Integration tests for type resolution improvements."""

import json
import sqlite3
import tempfile
import os
import sys
import time

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from json_to_sqlite import create_signatures_db
from resolve_types import TypeResolver
from merge_resolved_types import ResolvedTypeMerger
from query_db import (
    find_unresolved_types,
    find_function_by_name_and_path,
    find_all_function_instances,
    validate_type_resolution
)

def create_test_workspace_json():
    """Create a test workspace.json with various type scenarios."""
    workspace = {
        "test1.4gl": [
            {
                "name": "get_user",
                "signature": "FUNCTION get_user(user_id) RETURNS LIKE users.*",
                "line": {"start": 1, "end": 10},
                "parameters": [
                    {"name": "user_id", "type": "INTEGER"}
                ],
                "returns": [
                    {"name": "result", "type": "LIKE users.*"}
                ]
            },
            {
                "name": "validate_input",
                "signature": "FUNCTION validate_input(input_data) RETURNS STRING",
                "line": {"start": 12, "end": 20},
                "parameters": [
                    {"name": "input_data", "type": "LIKE validation_rules.*"}
                ],
                "returns": [
                    {"name": "result", "type": "STRING"}
                ]
            }
        ],
        "test2.4gl": [
            {
                "name": "get_user",
                "signature": "FUNCTION get_user(user_id) RETURNS LIKE users.*",
                "line": {"start": 1, "end": 15},
                "parameters": [
                    {"name": "user_id", "type": "INTEGER"}
                ],
                "returns": [
                    {"name": "result", "type": "LIKE users.*"}
                ]
            },
            {
                "name": "get_orders",
                "signature": "FUNCTION get_orders(user_id) RETURNS LIKE orders.*",
                "line": {"start": 17, "end": 25},
                "parameters": [
                    {"name": "user_id", "type": "INTEGER"}
                ],
                "returns": [
                    {"name": "result", "type": "LIKE orders.*"}
                ]
            }
        ]
    }
    return workspace

def create_test_schema_json():
    """Create a test schema.json with database tables."""
    schema = {
        "users": {
            "id": "INTEGER",
            "name": "STRING",
            "email": "STRING"
        },
        "orders": {
            "id": "INTEGER",
            "user_id": "INTEGER",
            "total": "DECIMAL"
        },
        "validation_rules": {
            "rule_id": "INTEGER",
            "rule_name": "STRING"
        }
    }
    return schema

def test_end_to_end_workflow():
    """Test complete workflow from parsing to validation."""
    print("\n" + "=" * 60)
    print("Testing end-to-end type resolution workflow")
    print("=" * 60)
    
    # Create temporary files
    fd_ws, ws_json_path = tempfile.mkstemp(suffix='.json')
    os.close(fd_ws)
    
    fd_schema, schema_json_path = tempfile.mkstemp(suffix='.json')
    os.close(fd_schema)
    
    fd_db, db_path = tempfile.mkstemp(suffix='.db')
    os.close(fd_db)
    
    fd_resolved, resolved_json_path = tempfile.mkstemp(suffix='.json')
    os.close(fd_resolved)
    
    try:
        # Step 1: Create test data
        print("\n1. Creating test workspace and schema...")
        workspace = create_test_workspace_json()
        schema = create_test_schema_json()
        
        with open(ws_json_path, 'w') as f:
            json.dump(workspace, f)
        
        with open(schema_json_path, 'w') as f:
            json.dump(schema, f)
        
        print(f"   ✓ Created workspace with {len(workspace)} files")
        print(f"   ✓ Created schema with {len(schema)} tables")
        
        # Step 2: Create database from workspace.json
        print("\n2. Creating SQLite database from workspace.json...")
        start_time = time.time()
        create_signatures_db(ws_json_path, db_path)
        db_creation_time = time.time() - start_time
        print(f"   ✓ Database created in {db_creation_time:.3f}s")
        
        # Verify database structure
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM functions")
        func_count = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM parameters")
        param_count = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM returns")
        return_count = c.fetchone()[0]
        conn.close()
        
        print(f"   ✓ Database contains {func_count} functions, {param_count} parameters, {return_count} return types")
        
        # Step 3: Resolve LIKE references
        print("\n3. Resolving LIKE references...")
        start_time = time.time()
        resolver = TypeResolver(db_path)
        resolved_workspace = resolver.process_workspace_json(ws_json_path)
        resolver.close()
        resolution_time = time.time() - start_time
        print(f"   ✓ Type resolution completed in {resolution_time:.3f}s")
        
        # Save resolved workspace
        with open(resolved_json_path, 'w') as f:
            json.dump(resolved_workspace, f)
        
        # Step 4: Merge resolved types into database
        print("\n4. Merging resolved types into database...")
        start_time = time.time()
        merger = ResolvedTypeMerger(db_path)
        merger.merge_resolved_types(resolved_json_path)
        merger.close()
        merge_time = time.time() - start_time
        print(f"   ✓ Merge completed in {merge_time:.3f}s")
        
        # Step 5: Query functions by name and path
        print("\n5. Testing function disambiguation...")
        result = find_function_by_name_and_path(db_path, "get_user", "test1.4gl")
        assert result is not None, "Should find get_user in test1.4gl"
        print(f"   ✓ Found get_user in test1.4gl")
        
        result = find_function_by_name_and_path(db_path, "get_user", "test2.4gl")
        assert result is not None, "Should find get_user in test2.4gl"
        print(f"   ✓ Found get_user in test2.4gl")
        
        # Step 6: Find all instances of a function
        print("\n6. Testing function instance discovery...")
        instances = find_all_function_instances(db_path, "get_user")
        assert len(instances) == 2, f"Should find 2 instances of get_user, found {len(instances)}"
        print(f"   ✓ Found {len(instances)} instances of get_user")
        
        # Step 7: Query unresolved types
        print("\n7. Testing unresolved types query...")
        unresolved = find_unresolved_types(db_path)
        print(f"   ✓ Found {len(unresolved)} unresolved types")
        
        # Step 8: Validate data consistency
        print("\n8. Validating data consistency...")
        report = validate_type_resolution(db_path)
        
        assert report['status'] == 'valid', f"Expected valid status, got {report['status']}"
        print(f"   ✓ Validation status: {report['status'].upper()}")
        
        summary = report['summary']
        print(f"   ✓ Functions: {summary['total_functions']} total, {summary['functions_with_file_path']} with file_path")
        print(f"   ✓ Parameters: {summary['total_parameters']} total, {summary['parameters_with_like_reference']} LIKE references")
        print(f"   ✓ Return types: {summary['total_returns']} total, {summary['returns_with_like_reference']} LIKE references")
        
        # Step 9: Performance summary
        print("\n9. Performance Summary:")
        print(f"   ✓ Database creation: {db_creation_time:.3f}s")
        print(f"   ✓ Type resolution: {resolution_time:.3f}s")
        print(f"   ✓ Merge resolved types: {merge_time:.3f}s")
        print(f"   ✓ Total time: {db_creation_time + resolution_time + merge_time:.3f}s")
        
        print("\n" + "=" * 60)
        print("✓ End-to-end workflow test PASSED")
        print("=" * 60)
        
        return True
        
    finally:
        # Cleanup
        for path in [ws_json_path, schema_json_path, db_path, resolved_json_path]:
            if os.path.exists(path):
                os.unlink(path)

def test_backward_compatibility():
    """Test that existing queries still work without modification."""
    print("\n" + "=" * 60)
    print("Testing backward compatibility")
    print("=" * 60)
    
    fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    try:
        # Create a simple database
        ws_json_path = tempfile.mktemp(suffix='.json')
        workspace = {
            "test.4gl": [
                {
                    "name": "my_function",
                    "signature": "FUNCTION my_function()",
                    "line": {"start": 1, "end": 5},
                    "parameters": [],
                    "returns": []
                }
            ]
        }
        
        with open(ws_json_path, 'w') as f:
            json.dump(workspace, f)
        
        create_signatures_db(ws_json_path, db_path)
        
        # Test that old queries still work
        print("\n1. Testing backward compatibility of queries...")
        
        # Query function (old style)
        from query_db import query_function
        result = query_function(db_path, "my_function")
        assert len(result) > 0, "Should find my_function"
        print("   ✓ query_function() works")
        
        # Search functions (old style)
        from query_db import search_functions
        result = search_functions(db_path, "my")
        assert len(result) > 0, "Should find functions matching 'my'"
        print("   ✓ search_functions() works")
        
        # List functions in file (old style)
        from query_db import list_functions_in_file
        result = list_functions_in_file(db_path, "test.4gl")
        assert len(result) > 0, "Should find functions in test.4gl"
        print("   ✓ list_functions_in_file() works")
        
        print("\n" + "=" * 60)
        print("✓ Backward compatibility test PASSED")
        print("=" * 60)
        
        return True
        
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)
        if os.path.exists(ws_json_path):
            os.unlink(ws_json_path)

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("Type Resolution Integration Tests")
    print("=" * 60)
    
    try:
        test_end_to_end_workflow()
        test_backward_compatibility()
        
        print("\n" + "=" * 60)
        print("✓ All integration tests PASSED")
        print("=" * 60)
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
