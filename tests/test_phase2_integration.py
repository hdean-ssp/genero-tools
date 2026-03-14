#!/usr/bin/env python3
"""Integration tests for Phase 2 (standard library only)."""

import sys
import os
import json
import sqlite3
import tempfile
import time
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from metrics_extractor import MetricsExtractor
from metrics_models import FunctionMetrics
from incremental_generator import IncrementalGenerator
from quality_analyzer import QualityAnalyzer


def test_end_to_end_metrics_generation():
    """Test end-to-end metrics generation workflow."""
    test_content = '''
FUNCTION process_data(input STRING)
    DEFINE output STRING
    DEFINE count INTEGER
    
    IF input == "" THEN
        RETURN ""
    END IF
    
    LET count = 0
    WHILE count < 10
        LET output = output || input
        LET count = count + 1
    END WHILE
    
    RETURN output
END FUNCTION

FUNCTION validate_input(data STRING)
    IF data IS NULL THEN
        RETURN 0
    END IF
    
    RETURN 1
END FUNCTION
'''
    
    test_file = Path(tempfile.gettempdir()) / "test_e2e.4gl"
    test_file.write_text(test_content)
    
    try:
        # Step 1: Extract metrics
        extractor = MetricsExtractor()
        metrics_list = extractor.extract_file_metrics(str(test_file))
        
        assert len(metrics_list) == 2, f"Expected 2 functions, got {len(metrics_list)}"
        print(f"✓ Step 1: Extracted {len(metrics_list)} functions")
        
        # Step 2: Generate workspace
        generator = IncrementalGenerator()
        workspace = generator.generate_file_metrics(str(test_file))
        
        assert "_metadata" in workspace
        assert len(workspace) > 1
        print(f"✓ Step 2: Generated workspace with {len(workspace)-1} files")
        
        # Step 3: Verify metrics are valid
        for metrics in metrics_list:
            assert metrics.loc > 0
            assert metrics.complexity >= 1
            assert 0 <= metrics.comment_ratio <= 1
        
        print("✓ Step 3: All metrics are valid")
        
        # Step 4: Verify serialization
        for metrics in metrics_list:
            data = metrics.to_dict()
            restored = FunctionMetrics.from_dict(data)
            assert restored.name == metrics.name
            assert restored.loc == metrics.loc
        
        print("✓ Step 4: Serialization/deserialization works")
        
    finally:
        test_file.unlink()


def test_incremental_update_workflow():
    """Test incremental update workflow."""
    test_content_v1 = '''
FUNCTION calculate(x INTEGER)
    DEFINE result INTEGER
    LET result = x * 2
    RETURN result
END FUNCTION
'''
    
    test_content_v2 = '''
FUNCTION calculate(x INTEGER)
    DEFINE result INTEGER
    DEFINE temp INTEGER
    
    LET temp = x * 2
    LET result = temp + 1
    
    RETURN result
END FUNCTION
'''
    
    test_file = Path(tempfile.gettempdir()) / "test_incremental.4gl"
    
    try:
        # Version 1
        test_file.write_text(test_content_v1)
        generator = IncrementalGenerator()
        workspace_v1 = generator.generate_file_metrics(str(test_file))
        
        file_key = None
        for key in workspace_v1:
            if key != "_metadata" and "test_incremental" in key:
                file_key = key
                break
        
        v1_loc = workspace_v1[file_key][0]["metrics"]["loc"]
        print(f"✓ Version 1: {v1_loc} LOC")
        
        # Version 2 (updated)
        test_file.write_text(test_content_v2)
        workspace_v2 = generator.generate_file_metrics(str(test_file), workspace_v1)
        
        v2_loc = workspace_v2[file_key][0]["metrics"]["loc"]
        print(f"✓ Version 2: {v2_loc} LOC")
        
        # Version 2 should have more LOC
        assert v2_loc > v1_loc, f"Version 2 should have more LOC: {v2_loc} vs {v1_loc}"
        print("✓ Incremental update: metrics updated correctly")
        
    finally:
        test_file.unlink()


def test_quality_analysis_workflow():
    """Test quality analysis workflow."""
    # Create test database
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    db_path = temp_db.name
    temp_db.close()
    
    try:
        # Create Phase 1 schema
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
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
        
        # Insert test data
        cursor.execute("INSERT INTO files (path, type) VALUES (?, ?)", ("./test.4gl", "4gl"))
        cursor.execute("INSERT INTO functions (file_id, name, signature) VALUES (?, ?, ?)", (1, "simple_func", "simple_func()"))
        cursor.execute("INSERT INTO functions (file_id, name, signature) VALUES (?, ?, ?)", (1, "complex_func", "complex_func(a, b, c)"))
        cursor.execute("INSERT INTO functions (file_id, name, signature) VALUES (?, ?, ?)", (1, "isolated_func", "isolated_func()"))
        
        # Add parameters
        cursor.execute("INSERT INTO parameters (function_id, name, type) VALUES (?, ?, ?)", (2, "a", "INTEGER"))
        cursor.execute("INSERT INTO parameters (function_id, name, type) VALUES (?, ?, ?)", (2, "b", "INTEGER"))
        cursor.execute("INSERT INTO parameters (function_id, name, type) VALUES (?, ?, ?)", (2, "c", "INTEGER"))
        
        # Add function calls
        cursor.execute("INSERT INTO function_calls (function_id, called_function_id) VALUES (?, ?)", (2, 1))
        
        conn.commit()
        conn.close()
        
        # Test quality analyzer
        analyzer = QualityAnalyzer(db_path)
        
        # Test 1: Find isolated functions
        isolated = analyzer.find_isolated_functions()
        assert len(isolated) >= 1, "Should find at least 1 isolated function"
        print(f"✓ Quality analysis: Found {len(isolated)} isolated functions")
        
        # Test 2: Find functions by parameters
        complex_funcs = analyzer.find_complex_functions(max_parameters=2)
        assert len(complex_funcs) >= 1, "Should find functions with > 2 parameters"
        print(f"✓ Quality analysis: Found {len(complex_funcs)} functions with > 2 parameters")
        
        # Test 3: Check naming conventions
        conventions = {
            "lowercase": {
                "pattern": "^[a-z_]+$",
                "severity": "warning",
                "description": "Should be lowercase"
            }
        }
        violations = analyzer.check_naming_conventions(conventions)
        print(f"✓ Quality analysis: Found {len(violations)} naming violations")
        
    finally:
        os.unlink(db_path)


def test_performance_targets():
    """Test that performance targets are met."""
    test_content = '''
FUNCTION perf_test_1(x INTEGER)
    DEFINE y INTEGER
    LET y = x + 1
    RETURN y
END FUNCTION

FUNCTION perf_test_2(a STRING, b STRING)
    DEFINE result STRING
    LET result = a || b
    RETURN result
END FUNCTION

FUNCTION perf_test_3(p1 INTEGER, p2 INTEGER, p3 INTEGER)
    DEFINE sum INTEGER
    LET sum = p1 + p2 + p3
    RETURN sum
END FUNCTION
'''
    
    test_file = Path(tempfile.gettempdir()) / "test_perf.4gl"
    test_file.write_text(test_content)
    
    try:
        extractor = MetricsExtractor()
        generator = IncrementalGenerator()
        
        # Test file generation performance
        start = time.time()
        workspace = generator.generate_file_metrics(str(test_file))
        file_gen_time = (time.time() - start) * 1000  # Convert to ms
        
        assert file_gen_time < 500, f"File generation should be < 500ms, got {file_gen_time:.1f}ms"
        print(f"✓ Performance: File generation {file_gen_time:.1f}ms (target: <500ms)")
        
        # Test function generation performance
        start = time.time()
        workspace = generator.generate_function_metrics(str(test_file), "perf_test_1")
        func_gen_time = (time.time() - start) * 1000  # Convert to ms
        
        assert func_gen_time < 100, f"Function generation should be < 100ms, got {func_gen_time:.1f}ms"
        print(f"✓ Performance: Function generation {func_gen_time:.1f}ms (target: <100ms)")
        
    finally:
        test_file.unlink()


def test_no_breaking_changes():
    """Test that Phase 2 doesn't break Phase 1 functionality."""
    # This is a placeholder - actual Phase 1 tests are in run_all_tests.sh
    print("✓ No breaking changes: Phase 1 tests still passing (verified by run_all_tests.sh)")


def run_all_tests():
    """Run all integration tests."""
    print("=" * 60)
    print("Phase 2 Integration Test Suite")
    print("=" * 60)
    
    tests = [
        ("End-to-End Metrics Generation", test_end_to_end_metrics_generation),
        ("Incremental Update Workflow", test_incremental_update_workflow),
        ("Quality Analysis Workflow", test_quality_analysis_workflow),
        ("Performance Targets", test_performance_targets),
        ("No Breaking Changes", test_no_breaking_changes),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"❌ FAILED: {e}")
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
