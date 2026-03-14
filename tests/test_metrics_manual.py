#!/usr/bin/env python3
"""Manual test for metrics extraction."""

import sys
import os
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from metrics_extractor import MetricsExtractor
from metrics_models import FunctionMetrics


def test_basic_extraction():
    """Test basic metrics extraction."""
    # Create a test file
    test_content = '''
FUNCTION simple_function(x INTEGER, y STRING)
    DEFINE result INTEGER
    DEFINE temp STRING
    
    LET result = x + 1
    LET temp = y || " processed"
    
    RETURN result, temp
END FUNCTION

FUNCTION complex_function(a INTEGER, b INTEGER, c INTEGER)
    DEFINE i INTEGER
    DEFINE sum INTEGER
    DEFINE count INTEGER
    
    LET sum = 0
    LET count = 0
    
    IF a > 0 THEN
        LET sum = sum + a
        LET count = count + 1
    END IF
    
    IF b > 0 THEN
        LET sum = sum + b
        LET count = count + 1
    ELSE IF c > 0 THEN
        LET sum = sum + c
        LET count = count + 1
    END IF
    
    WHILE count < 10
        LET count = count + 1
    END WHILE
    
    FOR i = 1 TO 5
        LET sum = sum + i
    END FOR
    
    RETURN sum
END FUNCTION

FUNCTION no_params()
    RETURN 42
END FUNCTION
'''
    
    # Write test file
    test_file = Path("/tmp/test_metrics.4gl")
    test_file.write_text(test_content)
    
    # Extract metrics
    extractor = MetricsExtractor()
    metrics_list = extractor.extract_file_metrics(str(test_file))
    
    print(f"✓ Extracted metrics for {len(metrics_list)} functions")
    
    # Check simple function
    simple = metrics_list[0]
    print(f"\nSimple Function: {simple.name}")
    print(f"  Parameters: {simple.parameters}")
    print(f"  Local Variables: {simple.local_variables}")
    print(f"  LOC: {simple.loc}")
    print(f"  Complexity: {simple.complexity}")
    print(f"  Returns: {simple.return_count}")
    print(f"  Comment Lines: {simple.comment_lines}")
    print(f"  Calls Made: {simple.calls_made}")
    
    assert simple.name == "simple_function"
    assert simple.parameters == 2
    assert simple.local_variables == 2
    print("✓ Simple function metrics correct")
    
    # Check complex function
    complex_func = metrics_list[1]
    print(f"\nComplex Function: {complex_func.name}")
    print(f"  Parameters: {complex_func.parameters}")
    print(f"  Local Variables: {complex_func.local_variables}")
    print(f"  LOC: {complex_func.loc}")
    print(f"  Complexity: {complex_func.complexity}")
    print(f"  Returns: {complex_func.return_count}")
    print(f"  Comment Lines: {complex_func.comment_lines}")
    
    assert complex_func.name == "complex_function"
    assert complex_func.parameters == 3
    assert complex_func.local_variables == 3
    assert complex_func.complexity > 1  # Has control flow
    print("✓ Complex function metrics correct")
    
    # Check no params function
    no_params = metrics_list[2]
    print(f"\nNo Params Function: {no_params.name}")
    print(f"  Parameters: {no_params.parameters}")
    print(f"  LOC: {no_params.loc}")
    
    assert no_params.name == "no_params"
    assert no_params.parameters == 0
    print("✓ No params function metrics correct")
    
    # Test to_dict
    data = simple.to_dict()
    assert data["name"] == "simple_function"
    assert data["metrics"]["loc"] == simple.loc
    print("\n✓ to_dict() works correctly")
    
    # Test from_dict
    restored = FunctionMetrics.from_dict(data)
    assert restored.name == simple.name
    assert restored.loc == simple.loc
    print("✓ from_dict() works correctly")
    
    print("\n✅ All tests passed!")


if __name__ == "__main__":
    test_basic_extraction()
