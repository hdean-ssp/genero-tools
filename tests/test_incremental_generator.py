#!/usr/bin/env python3
"""Tests for incremental metrics generation (standard library only)."""

import sys
import os
import json
import tempfile
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from incremental_generator import IncrementalGenerator
from metrics_extractor import MetricsExtractor
from metrics_models import FunctionMetrics


def test_file_generation():
    """Test single file metrics generation."""
    test_content = '''
FUNCTION func1(x INTEGER)
    DEFINE y INTEGER
    LET y = x + 1
    RETURN y
END FUNCTION

FUNCTION func2(a STRING, b STRING)
    DEFINE result STRING
    LET result = a || b
    RETURN result
END FUNCTION
'''
    
    test_file = Path(tempfile.gettempdir()) / "test_file_gen.4gl"
    test_file.write_text(test_content)
    
    try:
        generator = IncrementalGenerator()
        workspace = generator.generate_file_metrics(str(test_file))
        
        # Should have metadata and file entry
        assert "_metadata" in workspace
        assert len(workspace) > 1, "Should have metadata + file entry"
        
        # Should have both functions
        file_key = None
        for key in workspace:
            if key != "_metadata" and "test_file_gen" in key:
                file_key = key
                break
        
        assert file_key is not None, "Should have file entry"
        functions = workspace[file_key]
        assert len(functions) == 2, f"Expected 2 functions, got {len(functions)}"
        
        print(f"✓ File generation: {len(functions)} functions extracted")
    finally:
        test_file.unlink()


def test_function_generation():
    """Test single function metrics generation."""
    test_content = '''
FUNCTION func1(x INTEGER)
    DEFINE y INTEGER
    LET y = x + 1
    RETURN y
END FUNCTION

FUNCTION func2(a STRING)
    RETURN a
END FUNCTION
'''
    
    test_file = Path(tempfile.gettempdir()) / "test_func_gen.4gl"
    test_file.write_text(test_content)
    
    try:
        generator = IncrementalGenerator()
        workspace = generator.generate_function_metrics(str(test_file), "func1")
        
        # Should have metadata and file entry
        assert "_metadata" in workspace
        
        # Should have only func1
        file_key = None
        for key in workspace:
            if key != "_metadata" and "test_func_gen" in key:
                file_key = key
                break
        
        assert file_key is not None
        functions = workspace[file_key]
        assert len(functions) == 1, f"Expected 1 function, got {len(functions)}"
        assert functions[0]["name"] == "func1"
        
        print(f"✓ Function generation: {functions[0]['name']} extracted")
    finally:
        test_file.unlink()


def test_merge_with_existing():
    """Test merging new metrics with existing workspace."""
    # Create initial workspace
    initial_workspace = {
        "_metadata": {"version": "1.0.0"},
        "./file1.4gl": [
            {
                "name": "func1",
                "file_path": "./file1.4gl",
                "line_start": 1,
                "line_end": 5,
                "metrics": {"loc": 4, "complexity": 1},
                "calls_made": [],
                "called_by": [],
            }
        ],
        "./file2.4gl": [
            {
                "name": "func2",
                "file_path": "./file2.4gl",
                "line_start": 1,
                "line_end": 10,
                "metrics": {"loc": 8, "complexity": 2},
                "calls_made": [],
                "called_by": [],
            }
        ],
    }
    
    # New metrics for file1 (updated)
    new_metrics = {
        "./file1.4gl": [
            {
                "name": "func1",
                "file_path": "./file1.4gl",
                "line_start": 1,
                "line_end": 6,
                "metrics": {"loc": 5, "complexity": 1},
                "calls_made": [],
                "called_by": [],
            }
        ],
    }
    
    generator = IncrementalGenerator()
    merged = generator.merge_with_existing(new_metrics, initial_workspace)
    
    # Should have all files
    assert "./file1.4gl" in merged
    assert "./file2.4gl" in merged
    
    # file1 should be updated
    assert merged["./file1.4gl"][0]["metrics"]["loc"] == 5
    
    # file2 should be unchanged
    assert merged["./file2.4gl"][0]["metrics"]["loc"] == 8
    
    print("✓ Merge: new metrics merged correctly with existing data")


def test_consistency_with_full_generation():
    """Test that incremental generation matches full generation."""
    test_content = '''
FUNCTION test_func(x INTEGER, y STRING)
    DEFINE result STRING
    DEFINE count INTEGER
    
    IF x > 0 THEN
        LET count = x
    END IF
    
    LET result = y || " processed"
    
    RETURN result
END FUNCTION
'''
    
    test_file = Path(tempfile.gettempdir()) / "test_consistency.4gl"
    test_file.write_text(test_content)
    
    try:
        # Full generation
        extractor = MetricsExtractor()
        full_metrics = extractor.extract_function_metrics(str(test_file), "test_func")
        
        # Incremental generation
        generator = IncrementalGenerator()
        workspace = generator.generate_function_metrics(str(test_file), "test_func")
        
        # Extract metrics from workspace
        file_key = None
        for key in workspace:
            if key != "_metadata" and "test_consistency" in key:
                file_key = key
                break
        
        assert file_key is not None
        incremental_data = workspace[file_key][0]
        
        # Compare key metrics
        assert full_metrics.loc == incremental_data["metrics"]["loc"]
        assert full_metrics.complexity == incremental_data["metrics"]["complexity"]
        assert full_metrics.parameters == incremental_data["metrics"]["parameters"]
        assert full_metrics.local_variables == incremental_data["metrics"]["local_variables"]
        
        print("✓ Consistency: incremental generation matches full generation")
    finally:
        test_file.unlink()


def test_path_normalization():
    """Test that file paths are normalized correctly."""
    test_content = '''
FUNCTION test()
    RETURN 1
END FUNCTION
'''
    
    test_file = Path(tempfile.gettempdir()) / "test_normalize.4gl"
    test_file.write_text(test_content)
    
    try:
        generator = IncrementalGenerator()
        
        # Test with absolute path
        workspace = generator.generate_file_metrics(str(test_file))
        
        # Should have normalized path
        file_keys = [k for k in workspace if k != "_metadata"]
        assert len(file_keys) == 1
        
        # Path should start with ./
        file_key = file_keys[0]
        assert file_key.startswith("./"), f"Path should start with ./, got {file_key}"
        
        print(f"✓ Path normalization: {file_key}")
    finally:
        test_file.unlink()


def test_atomic_merge():
    """Test that merge is atomic (all or nothing)."""
    initial_workspace = {
        "_metadata": {"version": "1.0.0"},
        "./file1.4gl": [{"name": "func1"}],
    }
    
    new_metrics = {
        "./file2.4gl": [{"name": "func2"}],
    }
    
    generator = IncrementalGenerator()
    merged = generator.merge_with_existing(new_metrics, initial_workspace)
    
    # Original should be unchanged
    assert len(initial_workspace) == 2
    
    # Merged should have both
    assert len(merged) == 3  # metadata + 2 files
    assert "./file1.4gl" in merged
    assert "./file2.4gl" in merged
    
    print("✓ Atomic merge: original workspace unchanged, merged has both files")


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("Incremental Generator Test Suite")
    print("=" * 60)
    
    tests = [
        ("File Generation", test_file_generation),
        ("Function Generation", test_function_generation),
        ("Merge with Existing", test_merge_with_existing),
        ("Consistency Check", test_consistency_with_full_generation),
        ("Path Normalization", test_path_normalization),
        ("Atomic Merge", test_atomic_merge),
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
