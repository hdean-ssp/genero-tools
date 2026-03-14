#!/usr/bin/env python3
"""Data models for code quality metrics."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class FunctionMetrics:
    """Metrics for a single function."""
    
    name: str
    file_path: str
    line_start: int
    line_end: int
    loc: int                        # Lines of code (excluding comments/blanks)
    complexity: int                 # Cyclomatic complexity
    local_variables: int            # Count of DEFINE statements
    parameters: int                 # Parameter count
    return_count: int               # Number of RETURN statements
    call_depth: int                 # Maximum nesting depth of calls
    early_returns: int              # Count of early RETURN statements
    comment_lines: int              # Lines with comments
    comment_ratio: float            # comment_lines / loc
    calls_made: List[str] = field(default_factory=list)  # Functions this calls
    called_by: List[str] = field(default_factory=list)   # Functions that call this
    is_isolated: bool = False       # No dependencies (calls_made empty)
    has_dependencies: bool = False  # Called by other functions
    
    def __post_init__(self):
        """Validate metrics after initialization."""
        if self.loc < 0:
            raise ValueError(f"LOC must be >= 0, got {self.loc}")
        if self.complexity < 1:
            raise ValueError(f"Complexity must be >= 1, got {self.complexity}")
        if not (0 <= self.comment_ratio <= 1):
            raise ValueError(f"Comment ratio must be in [0, 1], got {self.comment_ratio}")
        if self.parameters < 0:
            raise ValueError(f"Parameters must be >= 0, got {self.parameters}")
        if self.return_count < 0:
            raise ValueError(f"Return count must be >= 0, got {self.return_count}")
        if self.early_returns < 0:
            raise ValueError(f"Early returns must be >= 0, got {self.early_returns}")
        if self.call_depth < 0:
            raise ValueError(f"Call depth must be >= 0, got {self.call_depth}")
        if self.local_variables < 0:
            raise ValueError(f"Local variables must be >= 0, got {self.local_variables}")
        
        # Update derived fields
        self.is_isolated = len(self.calls_made) == 0
        self.has_dependencies = len(self.called_by) > 0
    
    def to_dict(self) -> dict:
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
    def from_dict(cls, data: dict) -> "FunctionMetrics":
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
