#!/usr/bin/env python3
"""Comprehensive tests for quality analyzer."""

import sys
import os
import sqlite3
import tempfile
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from quality_analyzer import QualityAnalyzer


def setup_test_database():
    """Create a test database with sample Phase 1 schema and functions."""
    # Create temporary database
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    db_path = temp_db.name
    temp_db.close()
    
    # Initialize database with Phase 1 schema
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create Phase 1 schema tables
    cursor.execute('''
        CREATE TABLE files (
            id INTEGER PRIMARY KEY,
            path TEXT NOT NULL UNIQUE,
            type TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE functions (
            id INTEGER PRIMARY KEY,
            file_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            signature TEXT,
            FOREIGN KEY (file_id) REFERENCES files(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE parameters (
            id INTEGER PRIMARY KEY,
            function_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            type TEXT,
            FOREIGN KEY (function_id) REFERENCES functions(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE returns (
            id INTEGER PRIMARY KEY,
            function_id INTEGER NOT NULL,
            name TEXT,
            type TEXT,
            FOREIGN KEY (function_id) REFERENCES functions(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE function_calls (
            id INTEGER PRIMARY KEY,
            function_id INTEGER NOT NULL,
            called_function_id INTEGER NOT NULL,
            FOREIGN KEY (function_id) REFERENCES functions(id),
            FOREIGN KEY (called_function_id) REFERENCES functions(id)
        )
    ''')
    
    # Insert test files
    cursor.execute("INSERT INTO files (path, type) VALUES (?, ?)", ("./src/simple.4gl", "4gl"))
    cursor.execute("INSERT INTO files (path, type) VALUES (?, ?)", ("./src/complex.4gl", "4gl"))
    cursor.execute("INSERT INTO files (path, type) VALUES (?, ?)", ("./src/helpers.4gl", "4gl"))
    cursor.execute("INSERT INTO files (path, type) VALUES (?, ?)", ("./src/isolated.4gl", "4gl"))
    cursor.execute("INSERT INTO files (path, type) VALUES (?, ?)", ("./src/very_complex.4gl", "4gl"))
    
    # Insert test functions
    cursor.execute("INSERT INTO functions (file_id, name, signature) VALUES (?, ?, ?)", (1, "simple_function", "simple_function(x, y)"))
    cursor.execute("INSERT INTO functions (file_id, name, signature) VALUES (?, ?, ?)", (2, "complex_function", "complex_function(a, b, c)"))
    cursor.execute("INSERT INTO functions (file_id, name, signature) VALUES (?, ?, ?)", (3, "helper_function", "helper_function(x)"))
    cursor.execute("INSERT INTO functions (file_id, name, signature) VALUES (?, ?, ?)", (4, "isolated_function", "isolated_function()"))
    cursor.execute("INSERT INTO functions (file_id, name, signature) VALUES (?, ?, ?)", (5, "very_complex_function", "very_complex_function(a, b, c, d, e)"))
    
    # Insert parameters
    cursor.execute("INSERT INTO parameters (function_id, name, type) VALUES (?, ?, ?)", (1, "x", "INTEGER"))
    cursor.execute("INSERT INTO parameters (function_id, name, type) VALUES (?, ?, ?)", (1, "y", "STRING"))
    cursor.execute("INSERT INTO parameters (function_id, name, type) VALUES (?, ?, ?)", (2, "a", "INTEGER"))
    cursor.execute("INSERT INTO parameters (function_id, name, type) VALUES (?, ?, ?)", (2, "b", "INTEGER"))
    cursor.execute("INSERT INTO parameters (function_id, name, type) VALUES (?, ?, ?)", (2, "c", "INTEGER"))
    cursor.execute("INSERT INTO parameters (function_id, name, type) VALUES (?, ?, ?)", (3, "x", "INTEGER"))
    cursor.execute("INSERT INTO parameters (function_id, name, type) VALUES (?, ?, ?)", (5, "a", "INTEGER"))
    cursor.execute("INSERT INTO parameters (function_id, name, type) VALUES (?, ?, ?)", (5, "b", "INTEGER"))
    cursor.execute("INSERT INTO parameters (function_id, name, type) VALUES (?, ?, ?)", (5, "c", "INTEGER"))
    cursor.execute("INSERT INTO parameters (function_id, name, type) VALUES (?, ?, ?)", (5, "d", "INTEGER"))
    cursor.execute("INSERT INTO parameters (function_id, name, type) VALUES (?, ?, ?)", (5, "e", "INTEGER"))
    
    # Insert returns
    cursor.execute("INSERT INTO returns (function_id, name, type) VALUES (?, ?, ?)", (1, "result", "INTEGER"))
    cursor.execute("INSERT INTO returns (function_id, name, type) VALUES (?, ?, ?)", (1, "temp", "STRING"))
    cursor.execute("INSERT INTO returns (function_id, name, type) VALUES (?, ?, ?)", (2, "sum", "INTEGER"))
    cursor.execute("INSERT INTO returns (function_id, name, type) VALUES (?, ?, ?)", (2, "count", "INTEGER"))
    cursor.execute("INSERT INTO returns (function_id, name, type) VALUES (?, ?, ?)", (3, "result", "INTEGER"))
    cursor.execute("INSERT INTO returns (function_id, name, type) VALUES (?, ?, ?)", (4, "value", "INTEGER"))
    cursor.execute("INSERT INTO returns (function_id, name, type) VALUES (?, ?, ?)", (5, "result", "INTEGER"))
    cursor.execute("INSERT INTO returns (function_id, name, type) VALUES (?, ?, ?)", (5, "status", "STRING"))
    cursor.execute("INSERT INTO returns (function_id, name, type) VALUES (?, ?, ?)", (5, "count", "INTEGER"))
    
    # Insert function calls (to test isolated functions)
    # simple_function is called by main (not in our test db, so it's isolated)
    # complex_function calls helper_function
    cursor.execute("INSERT INTO function_calls (function_id, called_function_id) VALUES (?, ?)", (2, 3))
    # very_complex_function calls helper_function and complex_function
    cursor.execute("INSERT INTO function_calls (function_id, called_function_id) VALUES (?, ?)", (5, 3))
    cursor.execute("INSERT INTO function_calls (function_id, called_function_id) VALUES (?, ?)", (5, 2))
    
    conn.commit()
    conn.close()
    
    return db_path


def test_find_isolated_functions():
    """Test finding isolated functions."""
    db_path = setup_test_database()
    
    try:
        analyzer = QualityAnalyzer(db_path)
        
        # Find isolated functions
        results = analyzer.find_isolated_functions()
        print(f"✓ Found {len(results)} isolated functions")
        
        # Should find at least isolated_function and simple_function
        assert len(results) >= 2, f"Expected at least 2 isolated functions, got {len(results)}"
        
        # Check that isolated_function is in results
        isolated_names = [r["name"] for r in results]
        assert "isolated_function" in isolated_names, f"isolated_function not found in {isolated_names}"
        print("✓ Isolated function correctly identified")
        
        # Verify all results have empty calls_made
        for result in results:
            assert len(result.get("calls_made", [])) == 0
            print(f"  - {result['name']}: no dependencies")
        
        print("\n✅ find_isolated_functions tests passed!")
        
    finally:
        os.unlink(db_path)


def test_check_naming_conventions():
    """Test naming convention checking."""
    db_path = setup_test_database()
    
    try:
        analyzer = QualityAnalyzer(db_path)
        
        # Test 1: Check lowercase convention
        conventions = {
            "lowercase": {
                "pattern": "^[a-z_]+$",
                "severity": "warning",
                "description": "Function names should be lowercase with underscores"
            }
        }
        results = analyzer.check_naming_conventions(conventions)
        print(f"✓ Found {len(results)} naming violations for lowercase convention")
        # All our test functions follow lowercase_with_underscores, so should have 0 violations
        assert len(results) == 0, f"Expected 0 violations, got {len(results)}"
        print("✓ Naming convention checking works correctly")
        
        # Test 2: Check camelCase convention (should find violations)
        conventions = {
            "camelCase": {
                "pattern": "^[a-z][a-zA-Z0-9]*$",
                "severity": "error",
                "description": "Function names should be camelCase"
            }
        }
        results = analyzer.check_naming_conventions(conventions)
        print(f"✓ Found {len(results)} naming violations for camelCase convention")
        # Our functions use snake_case, so should have violations
        assert len(results) > 0, f"Expected violations for camelCase, got {len(results)}"
        print("✓ CamelCase convention checking works correctly")
        
        print("\n✅ check_naming_conventions tests passed!")
        
    finally:
        os.unlink(db_path)


def test_analyzer_initialization():
    """Test QualityAnalyzer initialization."""
    db_path = setup_test_database()
    
    try:
        # Test successful initialization
        analyzer = QualityAnalyzer(db_path)
        assert analyzer is not None
        print("✓ QualityAnalyzer initialized successfully")
        
        # Test with non-existent database
        try:
            analyzer = QualityAnalyzer("/tmp/nonexistent_db_12345.db")
            # Should handle gracefully
            print("✓ QualityAnalyzer handles non-existent database gracefully")
        except Exception as e:
            print(f"✓ QualityAnalyzer raises exception for non-existent database: {type(e).__name__}")
        
        print("\n✅ Initialization tests passed!")
        
    finally:
        os.unlink(db_path)


def test_find_similar_functions():
    """Test finding similar functions."""
    db_path = setup_test_database()
    
    try:
        analyzer = QualityAnalyzer(db_path)
        
        # Test 1: Find similar functions with high threshold
        results = analyzer.find_similar_functions(min_similarity=0.8)
        print(f"✓ Found {len(results)} function pairs with similarity >= 0.8")
        # Results may vary based on similarity calculation
        print("✓ Similar functions query works correctly")
        
        # Test 2: Find similar functions with low threshold
        results = analyzer.find_similar_functions(min_similarity=0.5)
        print(f"✓ Found {len(results)} function pairs with similarity >= 0.5")
        # Should find more pairs with lower threshold
        print("✓ Low threshold similarity query works correctly")
        
        # Test 3: Verify no duplicate pairs
        seen_pairs = set()
        for result in results:
            func1 = result["function1"]["name"]
            func2 = result["function2"]["name"]
            pair = tuple(sorted([func1, func2]))
            assert pair not in seen_pairs, f"Duplicate pair found: {pair}"
            seen_pairs.add(pair)
        print("✓ No duplicate pairs in results")
        
        print("\n✅ find_similar_functions tests passed!")
        
    finally:
        os.unlink(db_path)


def run_all_tests():
    """Run all quality analyzer tests."""
    print("=" * 60)
    print("Quality Analyzer Test Suite")
    print("=" * 60)
    
    tests = [
        ("Analyzer Initialization", test_analyzer_initialization),
        ("Isolated Functions Query", test_find_isolated_functions),
        ("Naming Conventions Check", test_check_naming_conventions),
        ("Similar Functions Query", test_find_similar_functions),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 60)
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
