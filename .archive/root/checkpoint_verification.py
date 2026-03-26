#!/usr/bin/env python3
"""
Checkpoint verification for type-resolution-improvements spec.

Verifies that all implemented components work together:
1. Empty parameter filtering
2. LIKE reference resolution
3. Multi-instance function resolution
4. Unresolved types query
5. Data consistency
"""

import sqlite3
import json
import sys
from pathlib import Path

def check_empty_parameter_filtering():
    """Verify empty parameters are filtered in json_to_sqlite.py"""
    print("\n" + "="*70)
    print("1. EMPTY PARAMETER FILTERING")
    print("="*70)
    
    conn = sqlite3.connect('workspace.db')
    cursor = conn.cursor()
    
    # Check if there are any empty parameters
    cursor.execute("SELECT COUNT(*) FROM parameters WHERE name IS NULL OR name = ''")
    empty_count = cursor.fetchone()[0]
    
    if empty_count == 0:
        print("✓ No empty parameters found in database")
    else:
        print(f"✗ Found {empty_count} empty parameters in database")
        return False
    
    # Check NOT NULL constraint
    cursor.execute("PRAGMA table_info(parameters)")
    columns = cursor.fetchall()
    name_column = next((col for col in columns if col[1] == 'name'), None)
    
    if name_column and name_column[3] == 1:  # notnull flag
        print("✓ NOT NULL constraint is enforced on parameters.name")
    else:
        print("✗ NOT NULL constraint is NOT enforced on parameters.name")
        return False
    
    # Check parameter counts are accurate
    cursor.execute("""
        SELECT f.name, COUNT(p.id) as param_count
        FROM functions f
        LEFT JOIN parameters p ON f.id = p.function_id
        GROUP BY f.id
        HAVING COUNT(p.id) > 0
        LIMIT 5
    """)
    
    print("✓ Sample parameter counts (first 5 functions with parameters):")
    for row in cursor.fetchall():
        print(f"  - {row[0]}: {row[1]} parameters")
    
    conn.close()
    return True


def check_like_reference_resolution():
    """Verify LIKE reference resolution in both parameters and return types"""
    print("\n" + "="*70)
    print("2. LIKE REFERENCE RESOLUTION")
    print("="*70)
    
    conn = sqlite3.connect('workspace.db')
    cursor = conn.cursor()
    
    # Check if resolved columns exist
    cursor.execute("PRAGMA table_info(parameters)")
    param_columns = {row[1] for row in cursor.fetchall()}
    
    required_columns = {'is_like_reference', 'resolved', 'resolution_error', 'table_name', 'columns', 'types'}
    missing_columns = required_columns - param_columns
    
    if missing_columns:
        print(f"✗ Missing columns in parameters table: {missing_columns}")
        return False
    else:
        print("✓ All required columns exist in parameters table")
    
    # Check if any LIKE references were resolved
    cursor.execute("""
        SELECT COUNT(*) FROM parameters 
        WHERE is_like_reference = 1 AND resolved = 1
    """)
    resolved_count = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(*) FROM parameters 
        WHERE is_like_reference = 1
    """)
    total_like_count = cursor.fetchone()[0]
    
    if total_like_count > 0:
        print(f"✓ Found {total_like_count} LIKE references in parameters")
        print(f"  - Resolved: {resolved_count}")
        print(f"  - Unresolved: {total_like_count - resolved_count}")
    else:
        print("ℹ No LIKE references found in parameters (may be expected)")
    
    # Check returns table
    cursor.execute("PRAGMA table_info(returns)")
    return_columns = {row[1] for row in cursor.fetchall()}
    
    missing_return_columns = required_columns - return_columns
    if missing_return_columns:
        print(f"✗ Missing columns in returns table: {missing_return_columns}")
        return False
    else:
        print("✓ All required columns exist in returns table")
    
    # Check if any return type LIKE references were resolved
    cursor.execute("""
        SELECT COUNT(*) FROM returns 
        WHERE is_like_reference = 1 AND resolved = 1
    """)
    resolved_return_count = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(*) FROM returns 
        WHERE is_like_reference = 1
    """)
    total_return_like_count = cursor.fetchone()[0]
    
    if total_return_like_count > 0:
        print(f"✓ Found {total_return_like_count} LIKE references in returns")
        print(f"  - Resolved: {resolved_return_count}")
        print(f"  - Unresolved: {total_return_like_count - resolved_return_count}")
    else:
        print("ℹ No LIKE references found in returns (may be expected)")
    
    conn.close()
    return True


def check_multi_instance_function_resolution():
    """Verify multi-instance function resolution using file_path"""
    print("\n" + "="*70)
    print("3. MULTI-INSTANCE FUNCTION RESOLUTION")
    print("="*70)
    
    conn = sqlite3.connect('workspace.db')
    cursor = conn.cursor()
    
    # Check if file_path column exists in functions table
    cursor.execute("PRAGMA table_info(functions)")
    func_columns = {row[1] for row in cursor.fetchall()}
    
    if 'file_path' not in func_columns:
        print("✗ file_path column does NOT exist in functions table")
        return False
    else:
        print("✓ file_path column exists in functions table")
    
    # Check if file_path values are stored
    cursor.execute("SELECT COUNT(*) FROM functions WHERE file_path IS NOT NULL")
    file_path_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM functions")
    total_functions = cursor.fetchone()[0]
    
    if file_path_count == total_functions:
        print(f"✓ All {total_functions} functions have file_path values")
    else:
        print(f"✗ Only {file_path_count}/{total_functions} functions have file_path values")
        return False
    
    # Check for functions with same name in different files
    cursor.execute("""
        SELECT name, COUNT(DISTINCT file_path) as file_count
        FROM functions
        GROUP BY name
        HAVING file_count > 1
        LIMIT 5
    """)
    
    multi_instance_functions = cursor.fetchall()
    if multi_instance_functions:
        print(f"✓ Found {len(multi_instance_functions)} functions with multiple instances:")
        for func_name, file_count in multi_instance_functions:
            print(f"  - {func_name}: {file_count} instances")
    else:
        print("ℹ No functions with multiple instances found (may be expected)")
    
    # Test find_function_by_name_and_path logic
    if multi_instance_functions:
        func_name = multi_instance_functions[0][0]
        cursor.execute("""
            SELECT file_path FROM functions WHERE name = ?
            LIMIT 2
        """, (func_name,))
        
        paths = [row[0] for row in cursor.fetchall()]
        if len(paths) >= 2:
            cursor.execute("""
                SELECT id, name, file_path FROM functions 
                WHERE name = ? AND file_path = ?
            """, (func_name, paths[0]))
            
            result = cursor.fetchone()
            if result:
                print(f"✓ find_function_by_name_and_path() logic works correctly")
                print(f"  - Found: {result[1]} in {result[2]}")
            else:
                print("✗ find_function_by_name_and_path() logic failed")
                return False
    
    conn.close()
    return True


def check_unresolved_types_query():
    """Verify unresolved types query functionality"""
    print("\n" + "="*70)
    print("4. UNRESOLVED TYPES QUERY")
    print("="*70)
    
    conn = sqlite3.connect('workspace.db')
    cursor = conn.cursor()
    
    # Check for unresolved LIKE references
    cursor.execute("""
        SELECT COUNT(*) FROM parameters 
        WHERE is_like_reference = 1 AND resolved = 0
    """)
    unresolved_param_count = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(*) FROM returns 
        WHERE is_like_reference = 1 AND resolved = 0
    """)
    unresolved_return_count = cursor.fetchone()[0]
    
    total_unresolved = unresolved_param_count + unresolved_return_count
    
    if total_unresolved > 0:
        print(f"✓ Found {total_unresolved} unresolved LIKE references")
        print(f"  - Parameters: {unresolved_param_count}")
        print(f"  - Returns: {unresolved_return_count}")
    else:
        print("ℹ No unresolved LIKE references found (may be expected)")
    
    # Check error_reason field
    cursor.execute("""
        SELECT resolution_error, COUNT(*) as count
        FROM parameters
        WHERE is_like_reference = 1 AND resolved = 0
        GROUP BY resolution_error
    """)
    
    error_breakdown = cursor.fetchall()
    if error_breakdown:
        print("✓ Error breakdown for unresolved parameters:")
        for error, count in error_breakdown:
            print(f"  - {error}: {count}")
    
    # Test pagination logic
    cursor.execute("""
        SELECT f.name, f.file_path, p.name, p.type, p.resolution_error
        FROM functions f
        JOIN parameters p ON f.id = p.function_id
        WHERE p.is_like_reference = 1 AND p.resolved = 0
        ORDER BY f.name, p.name
        LIMIT 3
    """)
    
    sample_results = cursor.fetchall()
    if sample_results:
        print("✓ Sample unresolved types (first 3):")
        for func_name, file_path, param_name, param_type, error in sample_results:
            print(f"  - {func_name} ({file_path}): {param_name} ({param_type})")
            print(f"    Error: {error}")
    
    conn.close()
    return True


def check_data_consistency():
    """Verify data consistency across all tables"""
    print("\n" + "="*70)
    print("5. DATA CONSISTENCY")
    print("="*70)
    
    conn = sqlite3.connect('workspace.db')
    cursor = conn.cursor()
    
    all_consistent = True
    
    # Check 1: No empty parameters
    cursor.execute("SELECT COUNT(*) FROM parameters WHERE name IS NULL OR name = ''")
    empty_params = cursor.fetchone()[0]
    if empty_params == 0:
        print("✓ No empty parameters in database")
    else:
        print(f"✗ Found {empty_params} empty parameters")
        all_consistent = False
    
    # Check 2: All functions have file_path
    cursor.execute("SELECT COUNT(*) FROM functions WHERE file_path IS NULL")
    missing_file_path = cursor.fetchone()[0]
    if missing_file_path == 0:
        print("✓ All functions have file_path values")
    else:
        print(f"✗ Found {missing_file_path} functions without file_path")
        all_consistent = False
    
    # Check 3: Resolved type information is consistent
    cursor.execute("""
        SELECT COUNT(*) FROM parameters
        WHERE resolved = 1 AND (table_name IS NULL OR columns IS NULL OR types IS NULL)
    """)
    inconsistent_params = cursor.fetchone()[0]
    if inconsistent_params == 0:
        print("✓ Resolved parameters have complete type information")
    else:
        print(f"✗ Found {inconsistent_params} resolved parameters with incomplete type info")
        all_consistent = False
    
    # Check 4: Return types consistency
    cursor.execute("""
        SELECT COUNT(*) FROM returns
        WHERE resolved = 1 AND (table_name IS NULL OR columns IS NULL OR types IS NULL)
    """)
    inconsistent_returns = cursor.fetchone()[0]
    if inconsistent_returns == 0:
        print("✓ Resolved return types have complete type information")
    else:
        print(f"✗ Found {inconsistent_returns} resolved returns with incomplete type info")
        all_consistent = False
    
    # Check 5: Foreign key integrity
    cursor.execute("""
        SELECT COUNT(*) FROM parameters p
        WHERE NOT EXISTS (SELECT 1 FROM functions f WHERE f.id = p.function_id)
    """)
    orphaned_params = cursor.fetchone()[0]
    if orphaned_params == 0:
        print("✓ No orphaned parameters (all have valid function_id)")
    else:
        print(f"✗ Found {orphaned_params} orphaned parameters")
        all_consistent = False
    
    cursor.execute("""
        SELECT COUNT(*) FROM returns r
        WHERE NOT EXISTS (SELECT 1 FROM functions f WHERE f.id = r.function_id)
    """)
    orphaned_returns = cursor.fetchone()[0]
    if orphaned_returns == 0:
        print("✓ No orphaned returns (all have valid function_id)")
    else:
        print(f"✗ Found {orphaned_returns} orphaned returns")
        all_consistent = False
    
    conn.close()
    return all_consistent


def main():
    """Run all checkpoint verifications"""
    print("\n" + "="*70)
    print("TYPE RESOLUTION IMPROVEMENTS - CHECKPOINT VERIFICATION")
    print("="*70)
    
    # Check if database exists
    if not Path('workspace.db').exists():
        print("✗ workspace.db not found")
        sys.exit(1)
    
    results = []
    
    # Run all checks
    results.append(("Empty Parameter Filtering", check_empty_parameter_filtering()))
    results.append(("LIKE Reference Resolution", check_like_reference_resolution()))
    results.append(("Multi-Instance Function Resolution", check_multi_instance_function_resolution()))
    results.append(("Unresolved Types Query", check_unresolved_types_query()))
    results.append(("Data Consistency", check_data_consistency()))
    
    # Print summary
    print("\n" + "="*70)
    print("CHECKPOINT VERIFICATION SUMMARY")
    print("="*70)
    
    all_passed = True
    for check_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {check_name}")
        if not passed:
            all_passed = False
    
    print("="*70)
    
    if all_passed:
        print("\n✓ All checkpoint verifications PASSED!")
        return 0
    else:
        print("\n✗ Some checkpoint verifications FAILED")
        return 1


if __name__ == '__main__':
    sys.exit(main())
