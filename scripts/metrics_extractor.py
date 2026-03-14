#!/usr/bin/env python3
"""Extract code quality metrics from Genero/4GL source files."""

import re
from pathlib import Path
from typing import List, Dict, Tuple
from metrics_models import FunctionMetrics


class MetricsExtractor:
    """Extract metrics from 4GL source files."""
    
    def __init__(self):
        """Initialize the metrics extractor."""
        self.function_pattern = re.compile(r'^FUNCTION\s+', re.IGNORECASE)
        self.end_function_pattern = re.compile(r'^END\s+FUNCTION', re.IGNORECASE)
        self.define_pattern = re.compile(r'^DEFINE\s+', re.IGNORECASE)
        self.return_pattern = re.compile(r'RETURN\s+', re.IGNORECASE)
        self.if_pattern = re.compile(r'\bIF\b', re.IGNORECASE)
        self.elseif_pattern = re.compile(r'\bELSEIF\b', re.IGNORECASE)
        self.while_pattern = re.compile(r'\bWHILE\b', re.IGNORECASE)
        self.for_pattern = re.compile(r'\bFOR\b', re.IGNORECASE)
        self.case_pattern = re.compile(r'\bCASE\b', re.IGNORECASE)
        self.when_pattern = re.compile(r'\bWHEN\b', re.IGNORECASE)
        self.call_pattern = re.compile(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(')
    
    def extract_file_metrics(self, file_path: str) -> List[FunctionMetrics]:
        """Extract metrics for all functions in a file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        except Exception as e:
            raise IOError(f"Cannot read file {file_path}: {e}")
        
        metrics_list = []
        i = 0
        
        while i < len(lines):
            if self.function_pattern.search(lines[i]):
                # Found function start
                func_start = i
                func_name = self._extract_function_name(lines[i])
                
                # Find function end
                func_end = self._find_function_end(lines, i + 1)
                if func_end is None:
                    i += 1
                    continue
                
                # Extract metrics for this function
                func_lines = lines[func_start:func_end + 1]
                metrics = self._extract_function_metrics(
                    func_name, file_path, func_start + 1, func_end + 1, func_lines
                )
                
                if metrics:
                    metrics_list.append(metrics)
                
                i = func_end + 1
            else:
                i += 1
        
        return metrics_list
    
    def extract_function_metrics(self, file_path: str, func_name: str) -> FunctionMetrics:
        """Extract metrics for a specific function."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        except Exception as e:
            raise IOError(f"Cannot read file {file_path}: {e}")
        
        # Find the function
        for i, line in enumerate(lines):
            if self.function_pattern.search(line):
                name = self._extract_function_name(line)
                if name.lower() == func_name.lower():
                    # Found it
                    func_end = self._find_function_end(lines, i + 1)
                    if func_end is None:
                        raise ValueError(f"Function {func_name} has no END FUNCTION")
                    
                    func_lines = lines[i:func_end + 1]
                    metrics = self._extract_function_metrics(
                        name, file_path, i + 1, func_end + 1, func_lines
                    )
                    
                    if metrics:
                        return metrics
                    else:
                        raise ValueError(f"Could not extract metrics for {func_name}")
        
        raise ValueError(f"Function {func_name} not found in {file_path}")
    
    def _extract_function_name(self, line: str) -> str:
        """Extract function name from FUNCTION line."""
        # Format: FUNCTION name(params)
        match = re.search(r'FUNCTION\s+([a-zA-Z_][a-zA-Z0-9_]*)', line, re.IGNORECASE)
        if match:
            return match.group(1)
        return "unknown"
    
    def _find_function_end(self, lines: List[str], start_idx: int) -> int:
        """Find the line number of END FUNCTION."""
        for i in range(start_idx, len(lines)):
            if self.end_function_pattern.search(lines[i]):
                return i
        return None
    
    def _extract_function_metrics(
        self, func_name: str, file_path: str, line_start: int, line_end: int,
        func_lines: List[str]
    ) -> FunctionMetrics:
        """Extract all metrics for a function."""
        # Count LOC (excluding comments and blanks)
        loc = self._count_loc(func_lines)
        
        # Calculate complexity
        complexity = self._calculate_complexity(func_lines)
        
        # Count local variables
        local_variables = self._count_local_variables(func_lines)
        
        # Count parameters
        parameters = self._count_parameters(func_lines[0])
        
        # Count returns
        return_count, early_returns = self._count_returns(func_lines)
        
        # Analyze call depth
        call_depth = self._analyze_call_depth(func_lines)
        
        # Extract comments
        comment_lines = self._count_comment_lines(func_lines)
        comment_ratio = comment_lines / loc if loc > 0 else 0.0
        
        # Extract function calls
        calls_made = self._extract_calls(func_lines)
        
        return FunctionMetrics(
            name=func_name,
            file_path=file_path,
            line_start=line_start,
            line_end=line_end,
            loc=loc,
            complexity=complexity,
            local_variables=local_variables,
            parameters=parameters,
            return_count=return_count,
            call_depth=call_depth,
            early_returns=early_returns,
            comment_lines=comment_lines,
            comment_ratio=comment_ratio,
            calls_made=calls_made,
        )
    
    def _count_loc(self, lines: List[str]) -> int:
        """Count lines of code (excluding comments and blanks)."""
        loc = 0
        for line in lines:
            stripped = line.strip()
            
            # Skip blank lines
            if not stripped:
                continue
            
            # Skip comment-only lines
            if stripped.startswith('*') or stripped.startswith('#'):
                continue
            
            # Count as LOC
            loc += 1
        
        return max(loc - 2, 0)  # Subtract FUNCTION and END FUNCTION lines
    
    def _calculate_complexity(self, lines: List[str]) -> int:
        """Calculate cyclomatic complexity."""
        complexity = 1  # Base complexity
        
        for line in lines:
            # Count decision points
            if self.if_pattern.search(line):
                complexity += 1
            if self.elseif_pattern.search(line):
                complexity += 1
            if self.while_pattern.search(line):
                complexity += 1
            if self.for_pattern.search(line):
                complexity += 1
            
            # Count WHEN clauses in CASE
            if self.case_pattern.search(line):
                when_count = len(self.when_pattern.findall(line))
                complexity += when_count
        
        return complexity
    
    def _count_local_variables(self, lines: List[str]) -> int:
        """Count DEFINE statements."""
        count = 0
        for line in lines:
            # Use search instead of match to find DEFINE anywhere in line
            if re.search(r'\bDEFINE\b', line, re.IGNORECASE):
                count += 1
        return count
    
    def _count_parameters(self, func_line: str) -> int:
        """Count parameters from function signature."""
        # Extract parameters from FUNCTION line
        match = re.search(r'\((.*?)\)', func_line)
        if not match:
            return 0
        
        params = match.group(1).strip()
        if not params:
            return 0
        
        # Count comma-separated parameters
        return len([p.strip() for p in params.split(',') if p.strip()])
    
    def _count_returns(self, lines: List[str]) -> Tuple[int, int]:
        """Count RETURN statements and early returns."""
        return_count = 0
        early_returns = 0
        
        for i, line in enumerate(lines):
            if self.return_pattern.search(line):
                return_count += 1
                
                # Check if it's an early return (not the last line)
                if i < len(lines) - 2:  # -2 for END FUNCTION
                    early_returns += 1
        
        return return_count, early_returns
    
    def _analyze_call_depth(self, lines: List[str]) -> int:
        """Analyze maximum nesting depth of function calls."""
        max_depth = 0
        
        for line in lines:
            # Count opening parentheses to estimate nesting
            depth = line.count('(') - line.count(')')
            max_depth = max(max_depth, depth)
        
        return max_depth
    
    def _count_comment_lines(self, lines: List[str]) -> int:
        """Count lines with comments."""
        count = 0
        for line in lines:
            stripped = line.strip()
            
            # Comment-only line
            if stripped.startswith('*') or stripped.startswith('#'):
                count += 1
            # Inline comment
            elif '*' in line or '#' in line:
                count += 1
        
        return count
    
    def _extract_calls(self, lines: List[str]) -> List[str]:
        """Extract function calls from function body."""
        calls = set()
        
        for line in lines:
            # Skip FUNCTION and END FUNCTION lines
            if self.function_pattern.search(line) or self.end_function_pattern.search(line):
                continue
            
            # Find all function calls
            matches = self.call_pattern.findall(line)
            for match in matches:
                # Filter out keywords
                if match.lower() not in ['if', 'while', 'for', 'case', 'when', 'define', 'let', 'call']:
                    calls.add(match)
        
        return sorted(list(calls))
