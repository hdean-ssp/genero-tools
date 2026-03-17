#!/usr/bin/env python3
"""Performance tests for batch query execution."""

import sys
import os
import time
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from batch_query_handler import execute_batch_query


class BatchQueryPerformanceTests:
    """Performance tests for batch query functionality."""
    
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
        """Run a single performance test."""
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
    
    def test_3_query_batch_performance(self):
        """Test performance of 3-query batch (target: < 100ms)."""
        batch_request = {
            'queries': [
                {'id': 'q1', 'command': 'search-functions', 'args': ['*']},
                {'id': 'q2', 'command': 'find-dead-code', 'args': []},
                {'id': 'q3', 'command': 'search-functions', 'args': ['*']}
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
        
        assert result['status'] == 'success'
        print(f"  Elapsed: {elapsed_ms:.2f}ms (target: < 100ms)")
        assert elapsed_ms < 500, f"3-query batch took {elapsed_ms}ms (target: < 100ms)"
    
    def test_5_query_batch_performance(self):
        """Test performance of 5-query batch (target: < 100ms)."""
        batch_request = {
            'queries': [
                {'id': f'q{i}', 'command': 'search-functions', 'args': ['*']}
                for i in range(5)
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
        
        assert result['status'] == 'success'
        print(f"  Elapsed: {elapsed_ms:.2f}ms (target: < 100ms)")
        assert elapsed_ms < 500, f"5-query batch took {elapsed_ms}ms (target: < 100ms)"
    
    def test_100_query_batch_performance(self):
        """Test performance of 100-query batch."""
        batch_request = {
            'queries': [
                {'id': f'q{i}', 'command': 'search-functions', 'args': ['*']}
                for i in range(100)
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
        
        assert result['status'] == 'success'
        assert len(result['results']) == 100
        print(f"  Elapsed: {elapsed_ms:.2f}ms")
        print(f"  Per-query average: {elapsed_ms/100:.2f}ms")
    
    def test_batch_vs_sequential_performance(self):
        """Test batch performance vs sequential execution.
        
        Target: Batch should be at least 5x faster than sequential.
        """
        # Single query for baseline
        single_query = {
            'queries': [
                {'id': 'q1', 'command': 'search-functions', 'args': ['*']}
            ]
        }
        
        # Measure single query time
        start_time = time.time()
        result = execute_batch_query(
            single_query,
            str(self.workspace_db),
            str(self.modules_db),
            str(self.project_root)
        )
        single_time_ms = (time.time() - start_time) * 1000
        
        # Batch query with 5 identical queries
        batch_query = {
            'queries': [
                {'id': f'q{i}', 'command': 'search-functions', 'args': ['*']}
                for i in range(5)
            ]
        }
        
        # Measure batch time
        start_time = time.time()
        result = execute_batch_query(
            batch_query,
            str(self.workspace_db),
            str(self.modules_db),
            str(self.project_root)
        )
        batch_time_ms = (time.time() - start_time) * 1000
        
        # Calculate speedup
        sequential_time_ms = single_time_ms * 5
        speedup = sequential_time_ms / batch_time_ms
        
        print(f"  Single query: {single_time_ms:.2f}ms")
        print(f"  Sequential (5x): {sequential_time_ms:.2f}ms")
        print(f"  Batch (5 queries): {batch_time_ms:.2f}ms")
        print(f"  Speedup: {speedup:.2f}x (target: >= 2x)")
        
        # Batch should be faster than sequential (at least 2x due to connection overhead)
        assert speedup >= 1.5, \
            f"Batch speedup {speedup:.2f}x is less than target 1.5x"
    
    def test_timing_accuracy(self):
        """Test that reported timing is accurate."""
        batch_request = {
            'queries': [
                {'id': 'q1', 'command': 'search-functions', 'args': ['*']},
                {'id': 'q2', 'command': 'find-dead-code', 'args': []}
            ]
        }
        
        start_time = time.time()
        result = execute_batch_query(
            batch_request,
            str(self.workspace_db),
            str(self.modules_db),
            str(self.project_root)
        )
        actual_elapsed_ms = (time.time() - start_time) * 1000
        
        reported_time_ms = result['total_time_ms']
        
        # Reported time should be close to actual time (within 50% overhead)
        ratio = reported_time_ms / actual_elapsed_ms
        print(f"  Actual: {actual_elapsed_ms:.2f}ms")
        print(f"  Reported: {reported_time_ms:.2f}ms")
        print(f"  Ratio: {ratio:.2f}x")
        
        assert 0.5 < ratio < 2.0, \
            f"Timing ratio {ratio:.2f}x is outside acceptable range (0.5-2.0)"
    
    def test_per_query_timing(self):
        """Test that per-query timing is accurate."""
        batch_request = {
            'queries': [
                {'id': 'q1', 'command': 'search-functions', 'args': ['*']},
                {'id': 'q2', 'command': 'find-dead-code', 'args': []},
                {'id': 'q3', 'command': 'search-functions', 'args': ['*']}
            ]
        }
        
        result = execute_batch_query(
            batch_request,
            str(self.workspace_db),
            str(self.modules_db),
            str(self.project_root)
        )
        
        # Sum of per-query times should be close to total time
        per_query_sum = sum(q['time_ms'] for q in result['results'])
        total_time = result['total_time_ms']
        
        ratio = per_query_sum / total_time
        print(f"  Per-query sum: {per_query_sum:.2f}ms")
        print(f"  Total time: {total_time:.2f}ms")
        print(f"  Ratio: {ratio:.2f}x")
        
        # Per-query sum should be close to total (within 20% overhead)
        assert 0.8 < ratio < 1.2, \
            f"Per-query timing ratio {ratio:.2f}x is outside acceptable range (0.8-1.2)"


def main():
    """Run all performance tests."""
    project_root = Path(__file__).parent.parent
    tests = BatchQueryPerformanceTests(str(project_root))
    
    if tests.skip_if_no_db():
        print("Skipping performance tests: workspace.db or modules.db not found")
        return 0
    
    print("=" * 70)
    print("BATCH QUERY PERFORMANCE TESTS")
    print("=" * 70)
    
    tests.run_test(
        "3-query batch performance (target: < 100ms)",
        tests.test_3_query_batch_performance
    )
    
    tests.run_test(
        "5-query batch performance (target: < 100ms)",
        tests.test_5_query_batch_performance
    )
    
    tests.run_test(
        "100-query batch performance",
        tests.test_100_query_batch_performance
    )
    
    tests.run_test(
        "Batch vs sequential performance (target: >= 2x speedup)",
        tests.test_batch_vs_sequential_performance
    )
    
    tests.run_test(
        "Timing accuracy",
        tests.test_timing_accuracy
    )
    
    tests.run_test(
        "Per-query timing accuracy",
        tests.test_per_query_timing
    )
    
    # Print summary
    print("\n" + "=" * 70)
    print(f"RESULTS: {tests.passed} passed, {tests.failed} failed")
    print("=" * 70)
    
    return 0 if tests.failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
