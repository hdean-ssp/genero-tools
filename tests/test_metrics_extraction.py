#!/usr/bin/env python3
"""Tests for metrics extraction (standard library only)."""

import sys
import os
import tempfile
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from metrics_extractor import MetricsExtractor
from metrics_models import FunctionMetrics


def test_loc_counting():
    """Test LOC counting excludes blanks and comments."""
    test_content = '''
FUNCTION test_loc()
    # This is a comment
    DEFINE x INTEGER
    
    LET x = 1
    LET x = x + 1
    
    RETURN x
END FUNCTION
'''
    
    test_file = Path(tempfile.gettempdir()) / "test_loc.4gl"
    test_file.write_text(test_content)
    
    try:
        extractor = MetricsExtractor()
        metrics = extractor.extract_function_metrics(str(test_file), "test_loc")
        
        # Should count only code lines, not blanks or comments
        assert metrics.loc > 0, "LOC should be > 0"
        assert metrics.loc <= 5, f"LOC should be <= 5, got {metrics.loc}"
        print(f"✓ LOC counting: {metrics.loc} lines")
    finally:
        test_file.unlink()


def test_complexity_calculation():
    """Test cyclomatic complexity calculation."""
    test_content = '''
FUNCTION test_complexity(x INTEGER)
    DEFINE result INTEGER
    
    IF x > 0 THEN
        LET result = x
    ELSE IF x < 0 THEN
        LET result = -x
    ELSE
        LET result = 0
    END IF
    
    RETURN result
END FUNCTION
'''
    
    test_file = Path(tempfile.gettempdir()) / "test_complexity.4gl"
    test_file.write_text(test_content)
    
    try:
        extractor = MetricsExtractor()
        metrics = extractor.extract_function_metrics(str(test_file), "test_complexity")
        
        # Should have complexity > 1 due to IF/ELSE IF
        assert metrics.complexity >= 2, f"Complexity should be >= 2, got {metrics.complexity}"
        print(f"✓ Complexity calculation: {metrics.complexity}")
    finally:
        test_file.unlink()


def test_variable_counting():
    """Test local variable counting."""
    test_content = '''
FUNCTION test_variables(param1 INTEGER, param2 STRING)
    DEFINE var1 INTEGER
    DEFINE var2 STRING
    DEFINE var3 DECIMAL
    
    LET var1 = param1
    LET var2 = param2
    
    RETURN var1
END FUNCTION
'''
    
    test_file = Path(tempfile.gettempdir()) / "test_variables.4gl"
    test_file.write_text(test_content)
    
    try:
        extractor = MetricsExtractor()
        metrics = extractor.extract_function_metrics(str(test_file), "test_variables")
        
        # Should count 3 DEFINE statements
        assert metrics.local_variables == 3, f"Expected 3 variables, got {metrics.local_variables}"
        assert metrics.parameters == 2, f"Expected 2 parameters, got {metrics.parameters}"
        print(f"✓ Variable counting: {metrics.local_variables} local, {metrics.parameters} parameters")
    finally:
        test_file.unlink()


def test_comment_extraction():
    """Test comment line counting."""
    test_content = '''
FUNCTION test_comments()
    # This is a comment
    DEFINE x INTEGER
    # Another comment
    
    LET x = 1  # Inline comment
    
    RETURN x
END FUNCTION
'''
    
    test_file = Path(tempfile.gettempdir()) / "test_comments.4gl"
    test_file.write_text(test_content)
    
    try:
        extractor = MetricsExtractor()
        metrics = extractor.extract_function_metrics(str(test_file), "test_comments")
        
        # Should count comment lines
        assert metrics.comment_lines >= 2, f"Expected >= 2 comment lines, got {metrics.comment_lines}"
        assert 0 <= metrics.comment_ratio <= 1, f"Comment ratio should be in [0,1], got {metrics.comment_ratio}"
        print(f"✓ Comment extraction: {metrics.comment_lines} comment lines, ratio {metrics.comment_ratio:.2f}")
    finally:
        test_file.unlink()


def test_early_returns():
    """Test early return detection."""
    test_content = '''
FUNCTION test_returns(x INTEGER)
    IF x < 0 THEN
        RETURN -1
    END IF
    
    IF x == 0 THEN
        RETURN 0
    END IF
    
    RETURN x
END FUNCTION
'''
    
    test_file = Path(tempfile.gettempdir()) / "test_returns.4gl"
    test_file.write_text(test_content)
    
    try:
        extractor = MetricsExtractor()
        metrics = extractor.extract_function_metrics(str(test_file), "test_returns")
        
        # Should count early returns
        assert metrics.early_returns >= 2, f"Expected >= 2 early returns, got {metrics.early_returns}"
        assert metrics.return_count >= 3, f"Expected >= 3 total returns, got {metrics.return_count}"
        print(f"✓ Early returns: {metrics.early_returns} early, {metrics.return_count} total")
    finally:
        test_file.unlink()


def test_metrics_validation():
    """Test FunctionMetrics validation."""
    # Valid metrics
    metrics = FunctionMetrics(
        name="test",
        file_path="./test.4gl",
        line_start=1,
        line_end=10,
        loc=5,
        complexity=2,
        local_variables=2,
        parameters=1,
        return_count=1,
        call_depth=0,
        early_returns=0,
        comment_lines=1,
        comment_ratio=0.2,
    )
    
    assert metrics.name == "test"
    assert metrics.is_isolated == True  # No calls made
    print("✓ Metrics validation: valid metrics accepted")
    
    # Invalid metrics should raise
    try:
        bad_metrics = FunctionMetrics(
            name="test",
            file_path="./test.4gl",
            line_start=1,
            line_end=10,
            loc=-1,  # Invalid: negative LOC
            complexity=1,
            local_variables=0,
            parameters=0,
            return_count=0,
            call_depth=0,
            early_returns=0,
            comment_lines=0,
            comment_ratio=0.0,
        )
        assert False, "Should have raised ValueError for negative LOC"
    except ValueError:
        print("✓ Metrics validation: invalid metrics rejected")


def test_serialization():
    """Test metrics serialization and deserialization."""
    metrics = FunctionMetrics(
        name="test_func",
        file_path="./test.4gl",
        line_start=1,
        line_end=10,
        loc=8,
        complexity=2,
        local_variables=2,
        parameters=1,
        return_count=1,
        call_depth=0,
        early_returns=0,
        comment_lines=1,
        comment_ratio=0.125,
        calls_made=["helper"],
        called_by=["main"],
    )
    
    # Serialize
    data = metrics.to_dict()
    assert data["name"] == "test_func"
    assert data["metrics"]["loc"] == 8
    assert data["calls_made"] == ["helper"]
    print("✓ Serialization: to_dict() works")
    
    # Deserialize
    restored = FunctionMetrics.from_dict(data)
    assert restored.name == metrics.name
    assert restored.loc == metrics.loc
    assert restored.calls_made == metrics.calls_made
    print("✓ Deserialization: from_dict() works")


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("Metrics Extraction Test Suite")
    print("=" * 60)
    
    tests = [
        ("LOC Counting", test_loc_counting),
        ("Complexity Calculation", test_complexity_calculation),
        ("Variable Counting", test_variable_counting),
        ("Comment Extraction", test_comment_extraction),
        ("Early Returns", test_early_returns),
        ("Metrics Validation", test_metrics_validation),
        ("Serialization", test_serialization),
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
