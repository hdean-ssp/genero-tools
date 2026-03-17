#!/usr/bin/env python3
"""Property-based tests for pagination correctness."""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from pagination_handler import apply_pagination, sort_results, validate_pagination_params


class PropertyTestRunner:
    """Runner for property-based tests."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
    
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
    
    def property_1_limit_parameter(self, iteration):
        """Property 1: Pagination Limit Parameter
        
        For any query with a limit parameter, the number of results 
        returned should not exceed the specified limit.
        """
        total_results = 1000
        results = list(range(total_results))
        
        # Test various limits
        limit = (iteration % 5) * 100 + 50  # 50, 150, 250, 350, 450
        
        result = apply_pagination(results, limit=limit, offset=0)
        
        assert len(result['data']) <= limit, \
            f"Returned {len(result['data'])} results, limit was {limit}"
        assert result['pagination']['returned_count'] <= limit
    
    def property_2_offset_parameter(self, iteration):
        """Property 2: Pagination Offset Parameter
        
        For any query with an offset parameter, the first result returned 
        should be the (offset+1)th result from the complete result set.
        """
        total_results = 1000
        results = list(range(total_results))
        
        offset = (iteration % 5) * 100  # 0, 100, 200, 300, 400
        limit = 50
        
        result = apply_pagination(results, limit=limit, offset=offset)
        
        if result['data']:
            assert result['data'][0] == offset, \
                f"First result should be {offset}, got {result['data'][0]}"
    
    def property_3_metadata_accuracy(self, iteration):
        """Property 3: Pagination Metadata Accuracy
        
        For any paginated query result, the pagination metadata 
        (limit, offset, total_count, has_more, returned_count) should 
        accurately reflect the actual results returned.
        """
        total_results = 1000
        results = list(range(total_results))
        
        limit = 100
        offset = (iteration % 5) * 100
        
        result = apply_pagination(results, limit=limit, offset=offset)
        
        pagination = result['pagination']
        
        # Verify metadata accuracy
        assert pagination['limit'] == limit
        assert pagination['offset'] == offset
        assert pagination['total_count'] == total_results
        assert pagination['returned_count'] == len(result['data'])
        
        # Verify has_more flag
        expected_has_more = (offset + len(result['data'])) < total_results
        assert pagination['has_more'] == expected_has_more
    
    def property_4_deterministic_ordering(self, iteration):
        """Property 4: Pagination Deterministic Ordering
        
        For any query executed multiple times with the same pagination 
        parameters, results should be returned in the same order.
        """
        results = [{'name': f'item_{i}', 'id': i} for i in range(100)]
        
        limit = 10
        offset = 20
        
        # Execute twice
        result1 = apply_pagination(results, limit=limit, offset=offset)
        result2 = apply_pagination(results, limit=limit, offset=offset)
        
        # Results should be identical
        assert result1['data'] == result2['data'], \
            "Results differ between executions"
    
    def property_5_consistency(self, iteration):
        """Property 5: Pagination Consistency
        
        For any query with pagination, executing with different limit/offset 
        combinations should return consistent, non-overlapping result sets 
        that together contain all results.
        """
        total_results = 100
        results = list(range(total_results))
        
        # Get first page
        page1 = apply_pagination(results, limit=25, offset=0)
        # Get second page
        page2 = apply_pagination(results, limit=25, offset=25)
        # Get third page
        page3 = apply_pagination(results, limit=25, offset=50)
        # Get fourth page
        page4 = apply_pagination(results, limit=25, offset=75)
        
        # Combine all pages
        combined = page1['data'] + page2['data'] + page3['data'] + page4['data']
        
        # Should equal original results
        assert combined == results, \
            "Combined pages don't match original results"
        
        # Pages should not overlap
        assert page1['data'][-1] < page2['data'][0]
        assert page2['data'][-1] < page3['data'][0]
        assert page3['data'][-1] < page4['data'][0]


def main():
    """Run all property-based tests."""
    runner = PropertyTestRunner()
    
    print("=" * 70)
    print("PAGINATION PROPERTY-BASED TESTS")
    print("=" * 70)
    
    runner.run_property_test(
        "Property 1: Pagination Limit Parameter",
        runner.property_1_limit_parameter,
        iterations=5
    )
    
    runner.run_property_test(
        "Property 2: Pagination Offset Parameter",
        runner.property_2_offset_parameter,
        iterations=5
    )
    
    runner.run_property_test(
        "Property 3: Pagination Metadata Accuracy",
        runner.property_3_metadata_accuracy,
        iterations=5
    )
    
    runner.run_property_test(
        "Property 4: Pagination Deterministic Ordering",
        runner.property_4_deterministic_ordering,
        iterations=5
    )
    
    runner.run_property_test(
        "Property 5: Pagination Consistency",
        runner.property_5_consistency,
        iterations=5
    )
    
    # Print summary
    print("\n" + "=" * 70)
    print(f"RESULTS: {runner.passed} passed, {runner.failed} failed")
    print("=" * 70)
    
    return 0 if runner.failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
