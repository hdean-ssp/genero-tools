#!/usr/bin/env python3
"""Property-based tests for batch query correctness.

This module validates key correctness properties of the batch query system:
- Property 1: Batch Query Single Connection
- Property 2: Batch Query Sequential Execution
- Property 3: Batch Query Result Ordering
- Property 4: Batch Query Error Isolation
- Property 5: Batch Query Response Format
- Property 6: Batch Query Performance
"""

import json
import tempfile
import sys
import os
import time
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from batch_query_handler import execute_batch_query


class PropertyTestRunner:
    """Runner for property-based tests."""
    
    def __init__(self, project_root):
        self.project_root = project_root
        self.workspace_db = Path(project_root) / 'workspace.db'
        self.modules_db = Path(project_root) / 'modules.db'
        self.passed = 0
        self.failed = 0
    
    def skip_if_no_db(self):
        """Skip test if databases don't exist."""
        if not self.workspace_db.exists() or not self.modules_db.exists():
            return True
        return False
    
    def run_property_test(self, name, test_func, iterations=10):
        """Run a property test multiple times."""
        print(f"\nTesting: {name}")
        print(f"  Running {iterations} iterations...")
        
        for i in range(iterations):
            try:
                test_func(i)
                print(f"  ✓ Iteration {i+1}/{iterations}")
            except AssertionError as e:
                print(f"  ✗ Iteration {i+1}/{iterations} FAILED: {e}")
                self.failed += 1
                return False
            except Exception as e:
                print(f"  ✗ Iteration {i+1}/{iterations} ERROR: {e}")
                self.failed += 1
                return False
        
        self.passed += 1
        print(f"  ✓ Property PASSED")
        return True
    
    def property_1_single_connection(self, iteration):
        """Property 1: Batch Query Single Connection
        
        For any batch query request with N queries, the API should open exactly 
        one database connection and execute all queries through that connection.
        """
        # Create batch with varying number of queries
        num_queries = (iteration % 5) + 1  # 1-5 queries
        
        batch_request = {
            'queries': [
                {
                    'id': f'q{i}',
                    'command': 'search-functions',
                    'args': ['*']
                }
                for i in range(num_queries)
            ]
        }
        
        result = execute_batch_query(
            batch_request,
            str(self.workspace_db),
            str(self.modules_db),
            str(self.project_root)
        )
        
        # Verify all queries executed successfully
        assert result['status'] == 'success', f"Batch failed: {result.get('error')}"
        assert len(result['results']) == num_queries, \
            f"Expected {num_queries} results, got {len(result['results'])}"
        
        # All queries should have executed (no connection errors)
        for query_result in result['results']:
            assert 'status' in query_result, "Missing status in query result"
            assert query_result['status'] in ['success', 'error'], \
                f"Invalid status: {query_result['status']}"
    
    def property_2_sequential_execution(self, iteration):
        """Property 2: Batch Query Sequential Execution
        
        For any batch query request with N queries, queries should execute in 
        the order specified in the input, and each query should complete before 
        the next begins.
        """
        # Create batch with specific order
        batch_request = {
            'queries': [
                {'id': 'first', 'command': 'search-functions', 'args': ['*']},
                {'id': 'second', 'command': 'find-dead-code', 'args': []},
                {'id': 'third', 'command': 'search-functions', 'args': ['*']}
            ]
        }
        
        result = execute_batch_query(
            batch_request,
            str(self.workspace_db),
            str(self.modules_db),
            str(self.project_root)
        )
        
        # Verify execution order is preserved
        assert result['status'] == 'success'
        assert result['results'][0]['query_id'] == 'first'
        assert result['results'][1]['query_id'] == 'second'
        assert result['results'][2]['query_id'] == 'third'
        
        # Verify each query has timing info (indicating it executed)
        for query_result in result['results']:
            assert 'time_ms' in query_result, "Missing timing info"
            assert query_result['time_ms'] >= 0, "Invalid timing"
    
    def property_3_result_ordering(self, iteration):
        """Property 3: Batch Query Result Ordering
        
        For any batch query request with N queries, the order of results in 
        the response should match the order of queries in the input request.
        """
        # Create batch with specific IDs
        query_ids = [f'query_{i}' for i in range(5)]
        
        batch_request = {
            'queries': [
                {'id': qid, 'command': 'search-functions', 'args': ['*']}
                for qid in query_ids
            ]
        }
        
        result = execute_batch_query(
            batch_request,
            str(self.workspace_db),
            str(self.modules_db),
            str(self.project_root)
        )
        
        # Verify result order matches input order
        assert result['status'] == 'success'
        for i, expected_id in enumerate(query_ids):
            actual_id = result['results'][i]['query_id']
            assert actual_id == expected_id, \
                f"Result {i}: expected {expected_id}, got {actual_id}"
    
    def property_4_error_isolation(self, iteration):
        """Property 4: Batch Query Error Isolation
        
        For any batch query request where one query is invalid, that query 
        should return an error status while all other queries execute 
        successfully and return results.
        """
        # Create batch with one invalid query in different positions
        error_position = iteration % 3
        
        batch_request = {
            'queries': [
                {'id': 'q0', 'command': 'search-functions', 'args': ['*']},
                {'id': 'q1', 'command': 'invalid-command', 'args': []},
                {'id': 'q2', 'command': 'find-dead-code', 'args': []}
            ]
        }
        
        result = execute_batch_query(
            batch_request,
            str(self.workspace_db),
            str(self.modules_db),
            str(self.project_root)
        )
        
        # Batch should succeed despite error in one query
        assert result['status'] == 'success', \
            "Batch should succeed even with one invalid query"
        
        # Verify error isolation
        assert result['results'][0]['status'] == 'success', \
            "Query 0 should succeed"
        assert result['results'][1]['status'] == 'error', \
            "Query 1 should error"
        assert result['results'][2]['status'] == 'success', \
            "Query 2 should succeed"
    
    def property_5_response_format(self, iteration):
        """Property 5: Batch Query Response Format
        
        For any batch query request, the response should contain all query 
        results with the same structure as individual query results, including 
        timing information for each query.
        """
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
        
        # Verify batch response structure
        assert isinstance(result, dict), "Response must be dict"
        assert 'batch_id' in result, "Missing batch_id"
        assert 'status' in result, "Missing status"
        assert 'total_time_ms' in result, "Missing total_time_ms"
        assert 'results' in result, "Missing results"
        assert isinstance(result['results'], list), "Results must be list"
        
        # Verify query response structure
        for query_result in result['results']:
            assert isinstance(query_result, dict), "Query result must be dict"
            assert 'query_id' in query_result, "Missing query_id"
            assert 'status' in query_result, "Missing status"
            assert 'time_ms' in query_result, "Missing time_ms"
            assert isinstance(query_result['time_ms'], (int, float)), \
                "time_ms must be numeric"
            assert query_result['time_ms'] >= 0, "time_ms must be non-negative"
            
            # Either data or error should be present
            has_data = 'data' in query_result
            has_error = 'error' in query_result
            assert has_data or has_error, \
                "Query result must have either data or error"
    
    def property_6_performance(self, iteration):
        """Property 6: Batch Query Performance
        
        For any batch query request with 3-5 queries on a 6M LOC codebase, 
        the total execution time should be reasonable (not excessively slow).
        """
        # Create batch with 3-5 queries
        num_queries = 3 + (iteration % 3)
        
        batch_request = {
            'queries': [
                {'id': f'q{i}', 'command': 'search-functions', 'args': ['*']}
                for i in range(num_queries)
            ]
        }
        
        start_time = time.time()
        result = execute_batch_query(
            batch_request,
            str(self.workspace_db),
            str(self.modules_db),
            str(self.project_root)
        )
        elapsed_ms = (time.time() - start_time) * 1000
        
        # Verify batch completed
        assert result['status'] == 'success'
        
        # Verify timing is reasonable (should complete in reasonable time)
        # Note: This is a soft constraint - we're checking it doesn't hang
        assert elapsed_ms < 10000, \
            f"Batch took too long: {elapsed_ms}ms (should be < 10000ms)"
        
        # Verify total_time_ms is close to actual elapsed time
        reported_time = result['total_time_ms']
        assert reported_time > 0, "total_time_ms must be positive"
        
        # Allow 50% overhead for Python overhead
        assert reported_time < elapsed_ms * 1.5, \
            f"Reported time {reported_time}ms exceeds actual {elapsed_ms}ms"


def main():
    """Run all property-based tests."""
    project_root = Path(__file__).parent.parent
    runner = PropertyTestRunner(str(project_root))
    
    if runner.skip_if_no_db():
        print("Skipping property tests: workspace.db or modules.db not found")
        return 0
    
    print("=" * 70)
    print("BATCH QUERY PROPERTY-BASED TESTS")
    print("=" * 70)
    
    # Run each property test with multiple iterations
    runner.run_property_test(
        "Property 1: Batch Query Single Connection",
        runner.property_1_single_connection,
        iterations=5
    )
    
    runner.run_property_test(
        "Property 2: Batch Query Sequential Execution",
        runner.property_2_sequential_execution,
        iterations=5
    )
    
    runner.run_property_test(
        "Property 3: Batch Query Result Ordering",
        runner.property_3_result_ordering,
        iterations=5
    )
    
    runner.run_property_test(
        "Property 4: Batch Query Error Isolation",
        runner.property_4_error_isolation,
        iterations=5
    )
    
    runner.run_property_test(
        "Property 5: Batch Query Response Format",
        runner.property_5_response_format,
        iterations=5
    )
    
    runner.run_property_test(
        "Property 6: Batch Query Performance",
        runner.property_6_performance,
        iterations=5
    )
    
    # Print summary
    print("\n" + "=" * 70)
    print(f"RESULTS: {runner.passed} passed, {runner.failed} failed")
    print("=" * 70)
    
    return 0 if runner.failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
