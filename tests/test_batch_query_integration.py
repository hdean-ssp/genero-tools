#!/usr/bin/env python3
"""Integration tests for batch query execution with real databases."""

import json
import tempfile
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from batch_query_handler import execute_batch_query


class BatchQueryIntegrationTests:
    """Integration tests for batch query functionality."""
    
    def __init__(self, project_root):
        self.project_root = project_root
        self.workspace_db = Path(project_root) / 'workspace.db'
        self.modules_db = Path(project_root) / 'modules.db'
        self.passed = 0
        self.failed = 0
    
    def skip_if_no_db(self):
        """Skip tests if databases don't exist."""
        if not self.workspace_db.exists() or not self.modules_db.exists():
            return True
        return False
    
    def run_test(self, name, test_func):
        """Run a single integration test."""
        print(f"\nTest: {name}")
        try:
            test_func()
            print(f"  ✓ PASSED")
            self.passed += 1
            return True
        except AssertionError as e:
            print(f"  ✗ FAILED: {e}")
            self.failed += 1
            return False
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            self.failed += 1
            return False
    
    def test_batch_queries_with_real_workspace_db(self):
        """Test batch queries with real workspace.db."""
        batch_request = {
            'queries': [
                {'id': 'q1', 'command': 'search-functions', 'args': ['*']},
                {'id': 'q2', 'command': 'find-dead-code', 'args': []}
            ]
        }
        
        result = execute_batch_query(
            batch_request,
            str(self.workspace_db),
            str(self.modules_db),
            str(self.project_root)
        )
        
        assert result['status'] == 'success', f"Batch failed: {result.get('error')}"
        assert len(result['results']) == 2
        assert result['results'][0]['status'] == 'success'
        assert result['results'][1]['status'] == 'success'
    
    def test_batch_queries_with_real_modules_db(self):
        """Test batch queries with real modules.db."""
        batch_request = {
            'queries': [
                {'id': 'q1', 'command': 'search-modules', 'args': ['*']},
                {'id': 'q2', 'command': 'find-functions-in-module', 'args': ['core']}
            ]
        }
        
        result = execute_batch_query(
            batch_request,
            str(self.workspace_db),
            str(self.modules_db),
            str(self.project_root)
        )
        
        assert result['status'] == 'success'
        assert len(result['results']) == 2
    
    def test_batch_queries_mixed_command_types(self):
        """Test batch queries with mixed command types."""
        batch_request = {
            'queries': [
                {'id': 'sig1', 'command': 'search-functions', 'args': ['*']},
                {'id': 'mod1', 'command': 'search-modules', 'args': ['*']},
                {'id': 'sig2', 'command': 'find-dead-code', 'args': []},
                {'id': 'mod2', 'command': 'find-functions-in-module', 'args': ['core']}
            ]
        }
        
        result = execute_batch_query(
            batch_request,
            str(self.workspace_db),
            str(self.modules_db),
            str(self.project_root)
        )
        
        assert result['status'] == 'success'
        assert len(result['results']) == 4
        
        # Verify all queries executed
        for query_result in result['results']:
            assert query_result['status'] in ['success', 'error']
    
    def test_batch_query_performance_3_5_queries(self):
        """Test batch query performance with 3-5 queries."""
        for num_queries in [3, 4, 5]:
            batch_request = {
                'queries': [
                    {'id': f'q{i}', 'command': 'search-functions', 'args': ['*']}
                    for i in range(num_queries)
                ]
            }
            
            result = execute_batch_query(
                batch_request,
                str(self.workspace_db),
                str(self.modules_db),
                str(self.project_root)
            )
            
            assert result['status'] == 'success'
            assert result['total_time_ms'] < 1000, \
                f"Batch with {num_queries} queries took {result['total_time_ms']}ms"
    
    def test_batch_query_with_json_file(self):
        """Test batch query execution from JSON file."""
        batch_request = {
            'queries': [
                {'id': 'q1', 'command': 'search-functions', 'args': ['*']},
                {'id': 'q2', 'command': 'find-dead-code', 'args': []}
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(batch_request, f)
            batch_file = f.name
        
        try:
            result = execute_batch_query(
                batch_request,
                str(self.workspace_db),
                str(self.modules_db),
                str(self.project_root)
            )
            
            assert result['status'] == 'success'
            assert len(result['results']) == 2
        finally:
            Path(batch_file).unlink()
    
    def test_batch_query_error_handling_invalid_command(self):
        """Test batch query error handling with invalid command."""
        batch_request = {
            'queries': [
                {'id': 'valid', 'command': 'search-functions', 'args': ['*']},
                {'id': 'invalid', 'command': 'nonexistent-command', 'args': []},
                {'id': 'valid2', 'command': 'find-dead-code', 'args': []}
            ]
        }
        
        result = execute_batch_query(
            batch_request,
            str(self.workspace_db),
            str(self.modules_db),
            str(self.project_root)
        )
        
        # Batch should succeed despite error
        assert result['status'] == 'success'
        
        # Verify error isolation
        assert result['results'][0]['status'] == 'success'
        assert result['results'][1]['status'] == 'error'
        assert result['results'][2]['status'] == 'success'
    
    def test_batch_query_error_handling_missing_command(self):
        """Test batch query error handling with missing command."""
        batch_request = {
            'queries': [
                {'id': 'q1', 'command': 'search-functions', 'args': ['*']},
                {'id': 'q2', 'args': ['some_arg']},  # Missing command
                {'id': 'q3', 'command': 'find-dead-code', 'args': []}
            ]
        }
        
        result = execute_batch_query(
            batch_request,
            str(self.workspace_db),
            str(self.modules_db),
            str(self.project_root)
        )
        
        assert result['status'] == 'success'
        assert result['results'][1]['status'] == 'error'
    
    def test_batch_query_large_batch(self):
        """Test batch query with many queries."""
        num_queries = 50
        batch_request = {
            'queries': [
                {'id': f'q{i}', 'command': 'search-functions', 'args': ['*']}
                for i in range(num_queries)
            ]
        }
        
        result = execute_batch_query(
            batch_request,
            str(self.workspace_db),
            str(self.modules_db),
            str(self.project_root)
        )
        
        assert result['status'] == 'success'
        assert len(result['results']) == num_queries
        
        # Verify all queries executed
        success_count = sum(1 for q in result['results'] if q['status'] == 'success')
        assert success_count == num_queries
    
    def test_batch_query_response_structure(self):
        """Test batch query response structure."""
        batch_request = {
            'queries': [
                {'id': 'q1', 'command': 'search-functions', 'args': ['*']}
            ]
        }
        
        result = execute_batch_query(
            batch_request,
            str(self.workspace_db),
            str(self.modules_db),
            str(self.project_root)
        )
        
        # Verify response structure
        assert 'batch_id' in result
        assert 'status' in result
        assert 'total_time_ms' in result
        assert 'results' in result
        
        # Verify query result structure
        query_result = result['results'][0]
        assert 'query_id' in query_result
        assert 'status' in query_result
        assert 'time_ms' in query_result
        assert 'data' in query_result or 'error' in query_result


def main():
    """Run all integration tests."""
    project_root = Path(__file__).parent.parent
    tests = BatchQueryIntegrationTests(str(project_root))
    
    if tests.skip_if_no_db():
        print("Skipping integration tests: workspace.db or modules.db not found")
        return 0
    
    print("=" * 70)
    print("BATCH QUERY INTEGRATION TESTS")
    print("=" * 70)
    
    tests.run_test(
        "Batch queries with real workspace.db",
        tests.test_batch_queries_with_real_workspace_db
    )
    
    tests.run_test(
        "Batch queries with real modules.db",
        tests.test_batch_queries_with_real_modules_db
    )
    
    tests.run_test(
        "Batch queries with mixed command types",
        tests.test_batch_queries_mixed_command_types
    )
    
    tests.run_test(
        "Batch query performance (3-5 queries)",
        tests.test_batch_query_performance_3_5_queries
    )
    
    tests.run_test(
        "Batch query with JSON file",
        tests.test_batch_query_with_json_file
    )
    
    tests.run_test(
        "Batch query error handling (invalid command)",
        tests.test_batch_query_error_handling_invalid_command
    )
    
    tests.run_test(
        "Batch query error handling (missing command)",
        tests.test_batch_query_error_handling_missing_command
    )
    
    tests.run_test(
        "Batch query with large batch (50 queries)",
        tests.test_batch_query_large_batch
    )
    
    tests.run_test(
        "Batch query response structure",
        tests.test_batch_query_response_structure
    )
    
    # Print summary
    print("\n" + "=" * 70)
    print(f"RESULTS: {tests.passed} passed, {tests.failed} failed")
    print("=" * 70)
    
    return 0 if tests.failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
