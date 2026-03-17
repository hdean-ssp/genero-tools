#!/usr/bin/env python3
"""Unit tests for pagination handler."""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from pagination_handler import (
    apply_pagination, sort_results, validate_pagination_params,
    add_pagination_to_response, PaginationMetadata
)


class TestPaginationMetadata:
    """Tests for PaginationMetadata class."""
    
    def test_pagination_metadata_creation(self):
        """Test creating pagination metadata."""
        metadata = PaginationMetadata(limit=10, offset=0, total_count=100, returned_count=10)
        
        assert metadata.limit == 10
        assert metadata.offset == 0
        assert metadata.total_count == 100
        assert metadata.returned_count == 10
        assert metadata.has_more == True
    
    def test_pagination_metadata_has_more_false(self):
        """Test has_more flag when at end of results."""
        metadata = PaginationMetadata(limit=10, offset=90, total_count=100, returned_count=10)
        
        assert metadata.has_more == False
    
    def test_pagination_metadata_to_dict(self):
        """Test converting metadata to dictionary."""
        metadata = PaginationMetadata(limit=10, offset=0, total_count=100, returned_count=10)
        result = metadata.to_dict()
        
        assert result['limit'] == 10
        assert result['offset'] == 0
        assert result['total_count'] == 100
        assert result['returned_count'] == 10
        assert result['has_more'] == True


class TestApplyPagination:
    """Tests for apply_pagination function."""
    
    def test_pagination_with_limit_and_offset(self):
        """Test pagination with both limit and offset."""
        results = list(range(100))
        
        result = apply_pagination(results, limit=10, offset=20)
        
        assert result['data'] == list(range(20, 30))
        assert result['pagination']['limit'] == 10
        assert result['pagination']['offset'] == 20
        assert result['pagination']['total_count'] == 100
        assert result['pagination']['returned_count'] == 10
        assert result['pagination']['has_more'] == True
    
    def test_pagination_with_limit_only(self):
        """Test pagination with limit only (offset defaults to 0)."""
        results = list(range(100))
        
        result = apply_pagination(results, limit=10)
        
        assert result['data'] == list(range(10))
        assert result['pagination']['offset'] == 0
        assert result['pagination']['returned_count'] == 10
    
    def test_pagination_with_offset_only(self):
        """Test pagination with offset only (limit defaults to all)."""
        results = list(range(100))
        
        result = apply_pagination(results, offset=50)
        
        assert result['data'] == list(range(50, 100))
        assert result['pagination']['offset'] == 50
        assert result['pagination']['returned_count'] == 50
    
    def test_pagination_no_parameters(self):
        """Test pagination with no parameters (returns all)."""
        results = list(range(100))
        
        result = apply_pagination(results)
        
        assert result['data'] == results
        assert result['pagination']['returned_count'] == 100
    
    def test_pagination_offset_exceeds_total(self):
        """Test pagination when offset exceeds total results."""
        results = list(range(100))
        
        result = apply_pagination(results, limit=10, offset=150)
        
        assert result['data'] == []
        assert result['pagination']['returned_count'] == 0
        assert result['pagination']['has_more'] == False
    
    def test_pagination_limit_exceeds_remaining(self):
        """Test pagination when limit exceeds remaining results."""
        results = list(range(100))
        
        result = apply_pagination(results, limit=50, offset=80)
        
        assert result['data'] == list(range(80, 100))
        assert result['pagination']['returned_count'] == 20
        assert result['pagination']['has_more'] == False
    
    def test_pagination_empty_results(self):
        """Test pagination with empty results."""
        results = []
        
        result = apply_pagination(results, limit=10, offset=0)
        
        assert result['data'] == []
        assert result['pagination']['total_count'] == 0
        assert result['pagination']['returned_count'] == 0
        assert result['pagination']['has_more'] == False
    
    def test_pagination_negative_limit_error(self):
        """Test that negative limit raises error."""
        results = list(range(100))
        
        try:
            apply_pagination(results, limit=-1)
            assert False, "Should raise ValueError"
        except ValueError as e:
            assert "limit must be non-negative" in str(e)
    
    def test_pagination_negative_offset_error(self):
        """Test that negative offset raises error."""
        results = list(range(100))
        
        try:
            apply_pagination(results, offset=-1)
            assert False, "Should raise ValueError"
        except ValueError as e:
            assert "offset must be non-negative" in str(e)
    
    def test_pagination_zero_limit(self):
        """Test pagination with zero limit."""
        results = list(range(100))
        
        result = apply_pagination(results, limit=0, offset=0)
        
        assert result['data'] == []
        assert result['pagination']['returned_count'] == 0


class TestSortResults:
    """Tests for sort_results function."""
    
    def test_sort_by_name(self):
        """Test sorting results by name."""
        results = [
            {'name': 'charlie', 'id': 3},
            {'name': 'alice', 'id': 1},
            {'name': 'bob', 'id': 2}
        ]
        
        sorted_results = sort_results(results, sort_key='name')
        
        assert sorted_results[0]['name'] == 'alice'
        assert sorted_results[1]['name'] == 'bob'
        assert sorted_results[2]['name'] == 'charlie'
    
    def test_sort_by_secondary_key(self):
        """Test sorting by primary and secondary keys."""
        results = [
            {'name': 'alice', 'file': 'b.4gl'},
            {'name': 'alice', 'file': 'a.4gl'},
            {'name': 'bob', 'file': 'c.4gl'}
        ]
        
        sorted_results = sort_results(results, sort_key='name', secondary_key='file')
        
        assert sorted_results[0]['name'] == 'alice'
        assert sorted_results[0]['file'] == 'a.4gl'
        assert sorted_results[1]['name'] == 'alice'
        assert sorted_results[1]['file'] == 'b.4gl'
    
    def test_sort_missing_key(self):
        """Test sorting when key doesn't exist."""
        results = [
            {'id': 3},
            {'id': 1},
            {'id': 2}
        ]
        
        sorted_results = sort_results(results, sort_key='name')
        
        # Should return unchanged
        assert sorted_results == results
    
    def test_sort_empty_results(self):
        """Test sorting empty results."""
        results = []
        
        sorted_results = sort_results(results)
        
        assert sorted_results == []


class TestValidatePaginationParams:
    """Tests for validate_pagination_params function."""
    
    def test_validate_both_params(self):
        """Test validating both limit and offset."""
        limit, offset = validate_pagination_params(limit=10, offset=20)
        
        assert limit == 10
        assert offset == 20
    
    def test_validate_limit_only(self):
        """Test validating limit only."""
        limit, offset = validate_pagination_params(limit=10)
        
        assert limit == 10
        assert offset == 0
    
    def test_validate_offset_only(self):
        """Test validating offset only (limit defaults to 100)."""
        limit, offset = validate_pagination_params(offset=20)
        
        assert limit == 100
        assert offset == 20
    
    def test_validate_no_params(self):
        """Test validating with no parameters."""
        limit, offset = validate_pagination_params()
        
        assert limit is None
        assert offset == 0
    
    def test_validate_negative_limit_error(self):
        """Test that negative limit raises error."""
        try:
            validate_pagination_params(limit=-1)
            assert False, "Should raise ValueError"
        except ValueError as e:
            assert "limit must be non-negative" in str(e)
    
    def test_validate_negative_offset_error(self):
        """Test that negative offset raises error."""
        try:
            validate_pagination_params(offset=-1)
            assert False, "Should raise ValueError"
        except ValueError as e:
            assert "offset must be non-negative" in str(e)
    
    def test_validate_limit_exceeds_max(self):
        """Test that limit exceeding max raises error."""
        try:
            validate_pagination_params(limit=20000, max_limit=10000)
            assert False, "Should raise ValueError"
        except ValueError as e:
            assert "cannot exceed" in str(e)
    
    def test_validate_zero_limit(self):
        """Test validating zero limit."""
        limit, offset = validate_pagination_params(limit=0)
        
        assert limit == 0
        assert offset == 0


class TestAddPaginationToResponse:
    """Tests for add_pagination_to_response function."""
    
    def test_add_pagination_to_response(self):
        """Test adding pagination to response."""
        response = {'status': 'success'}
        results = list(range(100))
        
        result = add_pagination_to_response(response, results, limit=10, offset=20)
        
        assert result['status'] == 'success'
        assert result['data'] == list(range(20, 30))
        assert 'pagination' in result
        assert result['pagination']['limit'] == 10
        assert result['pagination']['offset'] == 20
    
    def test_add_pagination_overwrites_data(self):
        """Test that pagination overwrites existing data."""
        response = {'status': 'success', 'data': 'old_data'}
        results = list(range(100))
        
        result = add_pagination_to_response(response, results, limit=10)
        
        assert result['data'] == list(range(10))
        assert result['data'] != 'old_data'


class TestPaginationEdgeCases:
    """Tests for edge cases in pagination."""
    
    def test_pagination_single_result(self):
        """Test pagination with single result."""
        results = [{'name': 'alice'}]
        
        result = apply_pagination(results, limit=10, offset=0)
        
        assert result['data'] == results
        assert result['pagination']['returned_count'] == 1
        assert result['pagination']['has_more'] == False
    
    def test_pagination_exact_boundary(self):
        """Test pagination at exact boundary."""
        results = list(range(100))
        
        result = apply_pagination(results, limit=10, offset=90)
        
        assert result['data'] == list(range(90, 100))
        assert result['pagination']['returned_count'] == 10
        assert result['pagination']['has_more'] == False
    
    def test_pagination_large_limit(self):
        """Test pagination with very large limit."""
        results = list(range(100))
        
        result = apply_pagination(results, limit=1000000, offset=0)
        
        assert result['data'] == results
        assert result['pagination']['returned_count'] == 100
        assert result['pagination']['has_more'] == False
    
    def test_pagination_consistency(self):
        """Test that pagination is consistent across multiple calls."""
        results = list(range(100))
        
        # Get first page
        page1 = apply_pagination(results, limit=10, offset=0)
        # Get second page
        page2 = apply_pagination(results, limit=10, offset=10)
        
        # Pages should not overlap
        assert page1['data'] != page2['data']
        assert page1['data'][0] == 0
        assert page2['data'][0] == 10


def run_tests():
    """Run all tests."""
    test_classes = [
        TestPaginationMetadata,
        TestApplyPagination,
        TestSortResults,
        TestValidatePaginationParams,
        TestAddPaginationToResponse,
        TestPaginationEdgeCases
    ]
    
    passed = 0
    failed = 0
    
    for test_class in test_classes:
        print(f"\n{test_class.__name__}:")
        instance = test_class()
        
        for method_name in dir(instance):
            if method_name.startswith('test_'):
                try:
                    method = getattr(instance, method_name)
                    method()
                    print(f"  ✓ {method_name}")
                    passed += 1
                except AssertionError as e:
                    print(f"  ✗ {method_name}: {e}")
                    failed += 1
                except Exception as e:
                    print(f"  ✗ {method_name}: ERROR: {e}")
                    failed += 1
    
    print(f"\n{'='*70}")
    print(f"RESULTS: {passed} passed, {failed} failed")
    print(f"{'='*70}")
    
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(run_tests())
