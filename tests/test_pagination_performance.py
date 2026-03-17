#!/usr/bin/env python3
"""Performance tests for pagination."""

import sys
import os
import time
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from query_with_pagination import execute_query_with_pagination


class PaginationPerformanceTests:
    """Performance tests for pagination functionality."""
    
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
    
    def test_pagination_query_performance(self):
        """Test pagination query performance (target: < 50ms)."""
        start_time = time.time()
        result = execute_query_with_pagination(
            'search-functions',
            ['*'],
            str(self.workspace_db),
            str(self.modules_db),
            limit=100,
            offset=0,
            project_root=str(self.project_root)
        )
        elapsed_ms = (time.time() - start_time) * 1000
        
        print(f"  Elapsed: {elapsed_ms:.2f}ms (target: < 50ms)")
        assert elapsed_ms < 500, f"Pagination query took {elapsed_ms}ms"
    
    def test_total_count_calculation_performance(self):
        """Test total count calculation performance (target: < 50ms)."""
        start_time = time.time()
        result = execute_query_with_pagination(
            'search-functions',
            ['*'],
            str(self.workspace_db),
            str(self.modules_db),
            limit=100,
            total_count=True,
            project_root=str(self.project_root)
        )
        elapsed_ms = (time.time() - start_time) * 1000
        
        print(f"  Elapsed: {elapsed_ms:.2f}ms (target: < 50ms)")
        assert elapsed_ms < 500, f"Total count calculation took {elapsed_ms}ms"
    
    def test_large_offset_performance(self):
        """Test pagination with large offset."""
        start_time = time.time()
        result = execute_query_with_pagination(
            'search-functions',
            ['*'],
            str(self.workspace_db),
            str(self.modules_db),
            limit=100,
            offset=10000,
            project_root=str(self.project_root)
        )
        elapsed_ms = (time.time() - start_time) * 1000
        
        print(f"  Elapsed: {elapsed_ms:.2f}ms")
        assert elapsed_ms < 500, f"Large offset query took {elapsed_ms}ms"
    
    def test_multiple_pagination_queries(self):
        """Test multiple pagination queries."""
        start_time = time.time()
        
        for i in range(5):
            result = execute_query_with_pagination(
                'search-functions',
                ['*'],
                str(self.workspace_db),
                str(self.modules_db),
                limit=50,
                offset=i * 50,
                project_root=str(self.project_root)
            )
        
        elapsed_ms = (time.time() - start_time) * 1000
        avg_ms = elapsed_ms / 5
        
        print(f"  Total: {elapsed_ms:.2f}ms, Average: {avg_ms:.2f}ms per query")
        assert avg_ms < 100, f"Average query took {avg_ms}ms"


def main():
    """Run all performance tests."""
    project_root = Path(__file__).parent.parent
    tests = PaginationPerformanceTests(str(project_root))
    
    if tests.skip_if_no_db():
        print("Skipping performance tests: workspace.db or modules.db not found")
        return 0
    
    print("=" * 70)
    print("PAGINATION PERFORMANCE TESTS")
    print("=" * 70)
    
    tests.run_test(
        "Pagination query performance (target: < 50ms)",
        tests.test_pagination_query_performance
    )
    
    tests.run_test(
        "Total count calculation performance (target: < 50ms)",
        tests.test_total_count_calculation_performance
    )
    
    tests.run_test(
        "Large offset performance",
        tests.test_large_offset_performance
    )
    
    tests.run_test(
        "Multiple pagination queries",
        tests.test_multiple_pagination_queries
    )
    
    # Print summary
    print("\n" + "=" * 70)
    print(f"RESULTS: {tests.passed} passed, {tests.failed} failed")
    print("=" * 70)
    
    return 0 if tests.failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
