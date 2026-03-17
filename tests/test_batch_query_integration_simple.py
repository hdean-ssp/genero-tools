#!/usr/bin/env python3
"""Simple integration test for batch query handler with real databases."""

import json
import tempfile
import sys
import os
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from batch_query_handler import execute_batch_query


def test_batch_query_with_sample_codebase():
    """Test batch query with sample codebase databases."""
    
    # Use the sample codebase databases if they exist
    project_root = Path(__file__).parent.parent
    workspace_db = project_root / 'workspace.db'
    modules_db = project_root / 'modules.db'
    
    if not workspace_db.exists() or not modules_db.exists():
        print("Skipping test: workspace.db or modules.db not found")
        return
    
    # Create a batch query request
    batch_request = {
        'queries': [
            {
                'id': 'q1',
                'command': 'search-functions',
                'args': ['*']
            },
            {
                'id': 'q2',
                'command': 'find-dead-code',
                'args': []
            }
        ]
    }
    
    # Execute batch query
    result = execute_batch_query(
        batch_request,
        str(workspace_db),
        str(modules_db),
        str(project_root)
    )
    
    # Verify results
    assert result['status'] == 'success', f"Batch query failed: {result.get('error')}"
    assert 'batch_id' in result
    assert 'total_time_ms' in result
    assert 'results' in result
    assert len(result['results']) == 2
    
    # Verify first query
    assert result['results'][0]['query_id'] == 'q1'
    assert result['results'][0]['status'] == 'success'
    assert 'time_ms' in result['results'][0]
    assert 'data' in result['results'][0]
    
    # Verify second query
    assert result['results'][1]['query_id'] == 'q2'
    assert result['results'][1]['status'] == 'success'
    assert 'time_ms' in result['results'][1]
    assert 'data' in result['results'][1]
    
    print("✓ Batch query integration test passed")
    print(f"  Batch ID: {result['batch_id']}")
    print(f"  Total time: {result['total_time_ms']:.2f}ms")
    print(f"  Query 1 time: {result['results'][0]['time_ms']:.2f}ms")
    print(f"  Query 2 time: {result['results'][1]['time_ms']:.2f}ms")


def test_batch_query_json_file():
    """Test batch query with JSON file input."""
    
    project_root = Path(__file__).parent.parent
    workspace_db = project_root / 'workspace.db'
    modules_db = project_root / 'modules.db'
    
    if not workspace_db.exists() or not modules_db.exists():
        print("Skipping test: workspace.db or modules.db not found")
        return
    
    # Create a temporary batch query file
    batch_request = {
        'queries': [
            {
                'id': 'search_all',
                'command': 'search-functions',
                'args': ['*']
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(batch_request, f)
        batch_file = f.name
    
    try:
        # Execute batch query from file
        result = execute_batch_query(
            batch_request,
            str(workspace_db),
            str(modules_db),
            str(project_root)
        )
        
        assert result['status'] == 'success'
        assert len(result['results']) == 1
        assert result['results'][0]['query_id'] == 'search_all'
        
        print("✓ Batch query JSON file test passed")
    finally:
        Path(batch_file).unlink()


def test_batch_query_error_handling():
    """Test batch query error handling."""
    
    project_root = Path(__file__).parent.parent
    workspace_db = project_root / 'workspace.db'
    modules_db = project_root / 'modules.db'
    
    if not workspace_db.exists() or not modules_db.exists():
        print("Skipping test: workspace.db or modules.db not found")
        return
    
    # Create a batch query with an invalid command
    batch_request = {
        'queries': [
            {
                'id': 'valid',
                'command': 'search-functions',
                'args': ['*']
            },
            {
                'id': 'invalid',
                'command': 'nonexistent-command',
                'args': []
            },
            {
                'id': 'valid2',
                'command': 'find-dead-code',
                'args': []
            }
        ]
    }
    
    # Execute batch query
    result = execute_batch_query(
        batch_request,
        str(workspace_db),
        str(modules_db),
        str(project_root)
    )
    
    # Verify batch succeeded despite error in one query
    assert result['status'] == 'success'
    assert len(result['results']) == 3
    
    # Verify error isolation
    assert result['results'][0]['status'] == 'success'
    assert result['results'][1]['status'] == 'error'
    assert result['results'][2]['status'] == 'success'
    
    print("✓ Batch query error handling test passed")
    print(f"  Query 1 status: {result['results'][0]['status']}")
    print(f"  Query 2 status: {result['results'][1]['status']} (expected error)")
    print(f"  Query 3 status: {result['results'][2]['status']}")


if __name__ == '__main__':
    print("Running batch query integration tests...\n")
    
    try:
        test_batch_query_with_sample_codebase()
        print()
        test_batch_query_json_file()
        print()
        test_batch_query_error_handling()
        print("\n✓ All integration tests passed!")
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
