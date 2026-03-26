#!/usr/bin/env python3
"""
Integration test for type-resolution-improvements spec.

Tests that all components work together correctly.
"""

import sys
import json
import sqlite3
from pathlib import Path

sys.path.insert(0, 'scripts')

from query_db import (
    find_function_by_name_and_path,
    find_all_function_instances,
    find_unresolved_types
)
from resolve_types import TypeResolver


def test_empty_parameter_filtering():
    """Test that empty parameters are filtered."""
    print("\n" + "="*70)
    print("TEST 1: Empty Parameter Filtering")
    print("="*70)
    
    conn = sqlite3.connect('workspace.db')
    cursor = conn.cursor()
    
    # Check no empty parameters
    cursor.execute("SELECT COUNT(*) FROM parameters WHERE name IS NULL OR name = ''")
    empty_count = cursor.fetchone()[0]
    
    assert empty_count == 0, f"Found {empty_count} empty parameters"
    print("✓ No empty parameters found")
    
    # Check NOT NULL constraint
    cursor.execute("PRAGMA table_info(parameters)")
    columns = cursor.fetchall()
    name_column = next((col for col in columns if col[1] == 'name'), None)
    assert name_column and name_column[3] == 1, "NOT NULL constraint not enforced"
    print("✓ NOT NULL constraint enforced on parameters.name")
    
    conn.close()
    return True


def test_like_resolution():
    """Test LIKE reference resolution."""
    print("\n" + "="*70)
    print("TEST 2: LIKE Reference Resolution")
    print("="*70)
    
    resolver = TypeResolver('workspace.db')
    
    # Test LIKE table.* pattern
    result = resolver.resolve_like_reference('LIKE abi_fields.*')
    assert result['resolved'], f"Failed to resolve LIKE abi_fields.*: {result.get('error')}"
    assert result['table'] == 'abi_fields', "Wrong table name"
    assert len(result['columns']) > 0, "No columns returned"
    assert len(result['types']) > 0, "No types returned"
    print(f"✓ LIKE table.* pattern works: {len(result['columns'])} columns resolved")
    
    # Test LIKE table.column pattern
    col_name = result['columns'][0]
    result2 = resolver.resolve_like_reference(f'LIKE abi_fields.{col_name}')
    assert result2['resolved'], f"Failed to resolve LIKE abi_fields.{col_name}"
    assert result2['columns'] == [col_name], "Wrong column returned"
    print(f"✓ LIKE table.column pattern works: {col_name} resolved")
    
    # Test invalid pattern
    result3 = resolver.resolve_like_reference('LIKE invalid_table.*')
    assert not result3['resolved'], "Should not resolve invalid table"
    assert 'Table not found' in result3['error'], "Wrong error message"
    print("✓ Invalid patterns handled correctly")
    
    resolver.close()
    return True


def test_multi_instance_resolution():
    """Test multi-instance function resolution."""
    print("\n" + "="*70)
    print("TEST 3: Multi-Instance Function Resolution")
    print("="*70)
    
    # Test find_function_by_name_and_path
    result = find_function_by_name_and_path('workspace.db', 'update_account', './test.4gl')
    assert result is not None, "Function not found"
    assert result['name'] == 'update_account', "Wrong function name"
    assert result['file_path'] == './test.4gl', "Wrong file path"
    print(f"✓ find_function_by_name_and_path() works: {result['name']} in {result['file_path']}")
    
    # Test find_all_function_instances
    results = find_all_function_instances('workspace.db', 'update_account')
    assert len(results) > 0, "No instances found"
    assert all(r['name'] == 'update_account' for r in results), "Wrong function names"
    assert all('file_path' in r for r in results), "Missing file_path in results"
    print(f"✓ find_all_function_instances() works: {len(results)} instance(s) found")
    
    return True


def test_unresolved_types_query():
    """Test unresolved types query."""
    print("\n" + "="*70)
    print("TEST 4: Unresolved Types Query")
    print("="*70)
    
    # Test find_unresolved_types
    results = find_unresolved_types('workspace.db')
    assert isinstance(results, list), "Results should be a list"
    
    if results:
        print(f"✓ Found {len(results)} unresolved types")
        
        # Check result structure
        for result in results:
            assert 'function_name' in result, "Missing function_name"
            assert 'file_path' in result, "Missing file_path"
            assert 'type_name' in result, "Missing type_name"
            assert 'original_type' in result, "Missing original_type"
            assert 'error_reason' in result, "Missing error_reason"
            assert 'error_type' in result, "Missing error_type"
        
        print("✓ Result structure is correct")
        
        # Test filtering
        filtered = find_unresolved_types('workspace.db', filter_type='missing_table')
        print(f"✓ Filtering works: {len(filtered)} results with missing_table filter")
        
        # Test pagination
        paginated = find_unresolved_types('workspace.db', limit=1, offset=0)
        assert len(paginated) <= 1, "Pagination limit not respected"
        print("✓ Pagination works")
    else:
        print("ℹ No unresolved types found (may be expected)")
    
    return True


def test_data_consistency():
    """Test data consistency."""
    print("\n" + "="*70)
    print("TEST 5: Data Consistency")
    print("="*70)
    
    conn = sqlite3.connect('workspace.db')
    cursor = conn.cursor()
    
    # Check no empty parameters
    cursor.execute("SELECT COUNT(*) FROM parameters WHERE name IS NULL OR name = ''")
    assert cursor.fetchone()[0] == 0, "Found empty parameters"
    print("✓ No empty parameters")
    
    # Check all functions have file_path
    cursor.execute("SELECT COUNT(*) FROM functions WHERE file_path IS NULL")
    assert cursor.fetchone()[0] == 0, "Found functions without file_path"
    print("✓ All functions have file_path")
    
    # Check foreign key integrity
    cursor.execute("""
        SELECT COUNT(*) FROM parameters p
        WHERE NOT EXISTS (SELECT 1 FROM functions f WHERE f.id = p.function_id)
    """)
    assert cursor.fetchone()[0] == 0, "Found orphaned parameters"
    print("✓ No orphaned parameters")
    
    cursor.execute("""
        SELECT COUNT(*) FROM returns r
        WHERE NOT EXISTS (SELECT 1 FROM functions f WHERE f.id = r.function_id)
    """)
    assert cursor.fetchone()[0] == 0, "Found orphaned returns"
    print("✓ No orphaned returns")
    
    conn.close()
    return True


def main():
    """Run all integration tests."""
    print("\n" + "="*70)
    print("TYPE RESOLUTION IMPROVEMENTS - INTEGRATION TEST")
    print("="*70)
    
    tests = [
        ("Empty Parameter Filtering", test_empty_parameter_filtering),
        ("LIKE Reference Resolution", test_like_resolution),
        ("Multi-Instance Function Resolution", test_multi_instance_resolution),
        ("Unresolved Types Query", test_unresolved_types_query),
        ("Data Consistency", test_data_consistency),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except AssertionError as e:
            print(f"✗ FAILED: {e}")
            results.append((test_name, False))
        except Exception as e:
            print(f"✗ ERROR: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "="*70)
    print("INTEGRATION TEST SUMMARY")
    print("="*70)
    
    all_passed = True
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
        if not passed:
            all_passed = False
    
    print("="*70)
    
    if all_passed:
        print("\n✓ All integration tests PASSED!")
        return 0
    else:
        print("\n✗ Some integration tests FAILED")
        return 1


if __name__ == '__main__':
    sys.exit(main())
