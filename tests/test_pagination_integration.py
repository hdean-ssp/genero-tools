#!/usr/bin/env python3
"""Integration tests for pagination with real databases."""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from query_with_pagination import execute_query_with_pagination


class PaginationIntegrationTests:
    """Integration tests for pagination functionality."""
    
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
    
    def test_pagination_with_limit(self):
        """Test pagination with limit parameter."""
        result = execute_query_with_pagination(
            'search-functions',
            ['*'],
            str(self.workspace_db),
            str(self.modules_db),
            limit=10,
            project_root=str(self.project_root)
        )
        
        assert 'data' in result
        assert 'pagination' in result
        assert len(result['data']) <= 10
        assert result['pagination']['limit'] == 10
        assert result['pagination']['offset'] == 0
    
    def test_pagination_with_offset(self):
        """Test pagination with offset parameter."""
        result = execute_query_with_pagination(
            'search-functions',
            ['*'],
            str(self.workspace_db),
            str(self.modules_db),
            limit=10,
            offset=20,
            project_root=str(self.project_root)
        )
        
        assert 'data' in result
        assert result['pagination']['offset'] == 20
        assert result['pagination']['limit'] == 10
    
    def test_pagination_with_total_count(self):
        """Test pagination with total count."""
        result = execute_query_with_pagination(
            'search-functions',
            ['*'],
            str(self.workspace_db),
            str(self.modules_db),
            limit=10,
            total_count=True,
            project_root=str(self.project_root)
        )
        
        assert 'pagination' in result
        assert 'total_count' in result['pagination']
        # Total count should be >= 0
        assert result['pagination']['total_count'] >= 0
    
    def test_pagination_consistency(self):
        """Test that pagination is consistent across queries."""
        # Get first page
        page1 = execute_query_with_pagination(
            'search-functions',
            ['*'],
            str(self.workspace_db),
            str(self.modules_db),
            limit=10,
            offset=0,
            project_root=str(self.project_root)
        )
        
        # Get second page
        page2 = execute_query_with_pagination(
            'search-functions',
            ['*'],
            str(self.workspace_db),
            str(self.modules_db),
            limit=10,
            offset=10,
            project_root=str(self.project_root)
        )
        
        # Pages should not overlap
        if page1['data'] and page2['data']:
            assert page1['data'] != page2['data']
    
    def test_pagination_large_result_set(self):
        """Test pagination with large result set."""
        result = execute_query_with_pagination(
            'search-functions',
            ['*'],
            str(self.workspace_db),
            str(self.modules_db),
            limit=100,
            offset=0,
            total_count=True,
            project_root=str(self.project_root)
        )
        
        assert len(result['data']) <= 100
        # Total count should be >= 0
        assert result['pagination']['total_count'] >= 0
    
    def test_pagination_offset_exceeds_total(self):
        """Test pagination when offset exceeds total results."""
        result = execute_query_with_pagination(
            'search-functions',
            ['*'],
            str(self.workspace_db),
            str(self.modules_db),
            limit=10,
            offset=1000000,
            project_root=str(self.project_root)
        )
        
        assert result['data'] == []
        assert result['pagination']['returned_count'] == 0
        assert result['pagination']['has_more'] == False
    
    def test_pagination_no_parameters(self):
        """Test query without pagination parameters."""
        result = execute_query_with_pagination(
            'search-functions',
            ['*'],
            str(self.workspace_db),
            str(self.modules_db),
            project_root=str(self.project_root)
        )
        
        assert 'data' in result
        assert 'pagination' in result
        # Should return results (may be empty if database is empty)
        assert result['pagination']['returned_count'] >= 0
    
    def test_pagination_with_modules_db(self):
        """Test pagination with modules database."""
        result = execute_query_with_pagination(
            'search-modules',
            ['*'],
            str(self.workspace_db),
            str(self.modules_db),
            limit=10,
            project_root=str(self.project_root)
        )
        
        assert 'data' in result
        assert 'pagination' in result
        assert len(result['data']) <= 10


def main():
    """Run all integration tests."""
    project_root = Path(__file__).parent.parent
    tests = PaginationIntegrationTests(str(project_root))
    
    if tests.skip_if_no_db():
        print("Skipping integration tests: workspace.db or modules.db not found")
        return 0
    
    print("=" * 70)
    print("PAGINATION INTEGRATION TESTS")
    print("=" * 70)
    
    tests.run_test(
        "Pagination with limit parameter",
        tests.test_pagination_with_limit
    )
    
    tests.run_test(
        "Pagination with offset parameter",
        tests.test_pagination_with_offset
    )
    
    tests.run_test(
        "Pagination with total count",
        tests.test_pagination_with_total_count
    )
    
    tests.run_test(
        "Pagination consistency",
        tests.test_pagination_consistency
    )
    
    tests.run_test(
        "Pagination with large result set",
        tests.test_pagination_large_result_set
    )
    
    tests.run_test(
        "Pagination offset exceeds total",
        tests.test_pagination_offset_exceeds_total
    )
    
    tests.run_test(
        "Query without pagination parameters",
        tests.test_pagination_no_parameters
    )
    
    tests.run_test(
        "Pagination with modules database",
        tests.test_pagination_with_modules_db
    )
    
    # Print summary
    print("\n" + "=" * 70)
    print(f"RESULTS: {tests.passed} passed, {tests.failed} failed")
    print("=" * 70)
    
    return 0 if tests.failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
