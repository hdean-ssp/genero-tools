#!/usr/bin/env python3
"""Pagination handler for managing large result sets."""

import sys
from typing import Dict, List, Any, Optional


class PaginationMetadata:
    """Metadata for paginated results."""
    
    def __init__(self, limit: int, offset: int, total_count: int, returned_count: int):
        self.limit = limit
        self.offset = offset
        self.total_count = total_count
        self.returned_count = returned_count
        self.has_more = (offset + returned_count) < total_count
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'limit': self.limit,
            'offset': self.offset,
            'total_count': self.total_count,
            'has_more': self.has_more,
            'returned_count': self.returned_count
        }


def apply_pagination(results: List[Any], 
                    limit: Optional[int] = None, 
                    offset: Optional[int] = None,
                    calculate_total: bool = False) -> Dict[str, Any]:
    """Apply pagination to results.
    
    Args:
        results: List of results to paginate
        limit: Maximum number of results to return (default: None = all)
        offset: Number of results to skip (default: 0)
        calculate_total: Whether to calculate total count (default: False)
    
    Returns:
        Dict with 'data' (paginated results) and 'pagination' metadata
    """
    # Validate parameters first
    if limit is not None and limit < 0:
        raise ValueError("limit must be non-negative")
    if offset is not None and offset < 0:
        raise ValueError("offset must be non-negative")
    
    # Handle defaults
    if offset is None:
        offset = 0
    
    total_count = len(results)
    
    # If no limit specified, return all results from offset
    if limit is None:
        paginated_data = results[offset:]
        returned_count = len(paginated_data)
    else:
        # Apply pagination
        paginated_data = results[offset:offset + limit]
        returned_count = len(paginated_data)
    
    # Create pagination metadata
    pagination = PaginationMetadata(
        limit=limit if limit is not None else len(results),
        offset=offset,
        total_count=total_count,
        returned_count=returned_count
    )
    
    return {
        'data': paginated_data,
        'pagination': pagination.to_dict()
    }


def sort_results(results: List[Dict[str, Any]], 
                sort_key: str = 'name',
                secondary_key: Optional[str] = None) -> List[Dict[str, Any]]:
    """Sort results by key for deterministic ordering.
    
    Args:
        results: List of result dictionaries
        sort_key: Primary sort key (default: 'name')
        secondary_key: Secondary sort key (default: None)
    
    Returns:
        Sorted list of results
    """
    if not results:
        return results
    
    # Check if sort_key exists in results
    if sort_key not in results[0]:
        return results
    
    # Sort by primary key
    sorted_results = sorted(results, key=lambda x: x.get(sort_key, ''))
    
    # Sort by secondary key if provided
    if secondary_key and secondary_key in results[0]:
        sorted_results = sorted(sorted_results, 
                              key=lambda x: (x.get(sort_key, ''), x.get(secondary_key, '')))
    
    return sorted_results


def validate_pagination_params(limit: Optional[int] = None, 
                              offset: Optional[int] = None,
                              max_limit: int = 10000) -> tuple:
    """Validate pagination parameters.
    
    Args:
        limit: Maximum number of results to return
        offset: Number of results to skip
        max_limit: Maximum allowed limit (default: 10000)
    
    Returns:
        Tuple of (limit, offset) with defaults applied
    
    Raises:
        ValueError: If parameters are invalid
    """
    # Apply defaults
    if limit is None and offset is None:
        return None, 0
    
    if offset is None:
        offset = 0
    
    if limit is None:
        limit = 100  # Default limit when offset is specified
    
    # Validate values
    if limit < 0:
        raise ValueError("limit must be non-negative")
    if offset < 0:
        raise ValueError("offset must be non-negative")
    if limit > max_limit:
        raise ValueError(f"limit cannot exceed {max_limit}")
    
    return limit, offset


def add_pagination_to_response(response: Dict[str, Any],
                              results: List[Any],
                              limit: Optional[int] = None,
                              offset: Optional[int] = None) -> Dict[str, Any]:
    """Add pagination metadata to a response.
    
    Args:
        response: Response dictionary
        results: List of results
        limit: Pagination limit
        offset: Pagination offset
    
    Returns:
        Response with pagination metadata added
    """
    paginated = apply_pagination(results, limit, offset, calculate_total=True)
    
    response['data'] = paginated['data']
    response['pagination'] = paginated['pagination']
    
    return response


def main():
    """Command-line interface for pagination testing."""
    if len(sys.argv) < 2:
        print("Usage: pagination_handler.py <command> [args...]", file=sys.stderr)
        print("Commands:", file=sys.stderr)
        print("  validate-params <limit> <offset>", file=sys.stderr)
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'validate-params':
        try:
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else None
            offset = int(sys.argv[3]) if len(sys.argv) > 3 else None
            
            validated_limit, validated_offset = validate_pagination_params(limit, offset)
            print(f"limit: {validated_limit}, offset: {validated_offset}")
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
