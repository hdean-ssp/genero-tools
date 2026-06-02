#!/usr/bin/env python3
"""Data models for code quality metrics. Compatible with Python 3.6+."""

from typing import List


class FunctionMetrics:
    """Metrics for a single function."""
    
    def __init__(self, name, file_path, line_start, line_end, loc, complexity,
                 local_variables, parameters, return_count, call_depth,
                 early_returns, comment_lines, comment_ratio,
                 calls_made=None, called_by=None):
        self.name = name
        self.file_path = file_path
        self.line_start = line_start
        self.line_end = line_end
        self.loc = loc                        # Lines of code (excluding comments/blanks)
        self.complexity = complexity           # Cyclomatic complexity
        self.local_variables = local_variables # Count of DEFINE statements
        self.parameters = parameters           # Parameter count
        self.return_count = return_count       # Number of RETURN statements
        self.call_depth = call_depth           # Maximum nesting depth of calls
        self.early_returns = early_returns     # Count of early RETURN statements
        self.comment_lines = comment_lines     # Lines with comments
        self.comment_ratio = comment_ratio     # comment_lines / loc
        self.calls_made = calls_made if calls_made is not None else []
        self.called_by = called_by if called_by is not None else []
        
        # Derived fields
        self.is_isolated = len(self.calls_made) == 0
        self.has_dependencies = len(self.called_by) > 0
        
        # Validate
        if self.loc < 0:
            raise ValueError("LOC must be >= 0, got {}".format(self.loc))
        if self.complexity < 1:
            raise ValueError("Complexity must be >= 1, got {}".format(self.complexity))
        if not (0 <= self.comment_ratio <= 1):
            raise ValueError("Comment ratio must be in [0, 1], got {}".format(self.comment_ratio))
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "file_path": self.file_path,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "metrics": {
                "loc": self.loc,
                "complexity": self.complexity,
                "local_variables": self.local_variables,
                "parameters": self.parameters,
                "return_count": self.return_count,
                "call_depth": self.call_depth,
                "early_returns": self.early_returns,
                "comment_lines": self.comment_lines,
                "comment_ratio": round(self.comment_ratio, 2),
                "is_isolated": self.is_isolated,
                "has_dependencies": self.has_dependencies,
            },
            "calls_made": self.calls_made,
            "called_by": self.called_by,
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create from dictionary."""
        metrics = data.get("metrics", {})
        return cls(
            name=data["name"],
            file_path=data["file_path"],
            line_start=data["line_start"],
            line_end=data["line_end"],
            loc=metrics.get("loc", 0),
            complexity=metrics.get("complexity", 1),
            local_variables=metrics.get("local_variables", 0),
            parameters=metrics.get("parameters", 0),
            return_count=metrics.get("return_count", 0),
            call_depth=metrics.get("call_depth", 0),
            early_returns=metrics.get("early_returns", 0),
            comment_lines=metrics.get("comment_lines", 0),
            comment_ratio=metrics.get("comment_ratio", 0.0),
            calls_made=data.get("calls_made", []),
            called_by=data.get("called_by", []),
        )
