#!/usr/bin/env python3
"""Incremental metrics generation for IDE/AI agent integration."""

import json
from pathlib import Path
from typing import Dict, List, Optional
from metrics_extractor import MetricsExtractor
from metrics_models import FunctionMetrics


class IncrementalGenerator:
    """Generate metrics incrementally for single files or functions."""
    
    def __init__(self):
        """Initialize the incremental generator."""
        self.extractor = MetricsExtractor()
    
    def generate_file_metrics(self, file_path: str, existing_workspace: Optional[Dict] = None) -> Dict:
        """Generate metrics for a single file and merge with existing data."""
        # Extract metrics for all functions in file
        metrics_list = self.extractor.extract_file_metrics(file_path)
        
        # Normalize file path
        normalized_path = self._normalize_path(file_path)
        
        # Start with existing data or empty dict
        if existing_workspace is None:
            workspace = {"_metadata": {"version": "1.0.0"}}
        else:
            workspace = self._deep_copy(existing_workspace)
        
        # Remove old entries for this file
        if normalized_path in workspace:
            del workspace[normalized_path]
        
        # Add new metrics
        workspace[normalized_path] = [m.to_dict() for m in metrics_list]
        
        return workspace
    
    def generate_function_metrics(
        self, file_path: str, func_name: str, existing_workspace: Optional[Dict] = None
    ) -> Dict:
        """Generate metrics for a single function and merge with existing data."""
        # Extract metrics for specific function
        metrics = self.extractor.extract_function_metrics(file_path, func_name)
        
        # Normalize file path
        normalized_path = self._normalize_path(file_path)
        
        # Start with existing data or empty dict
        if existing_workspace is None:
            workspace = {"_metadata": {"version": "1.0.0"}}
        else:
            workspace = self._deep_copy(existing_workspace)
        
        # Get existing functions for this file
        if normalized_path not in workspace:
            workspace[normalized_path] = []
        
        # Find and replace the function, or add if not found
        file_functions = workspace[normalized_path]
        found = False
        for i, func_data in enumerate(file_functions):
            if func_data.get("name", "").lower() == func_name.lower():
                file_functions[i] = metrics.to_dict()
                found = True
                break
        
        if not found:
            file_functions.append(metrics.to_dict())
        
        return workspace
    
    def merge_with_existing(self, new_metrics: Dict, existing_workspace: Dict) -> Dict:
        """Merge new metrics with existing workspace data."""
        # Deep copy existing workspace
        merged = self._deep_copy(existing_workspace)
        
        # Merge new metrics
        for file_path, functions in new_metrics.items():
            if file_path == "_metadata":
                continue
            
            merged[file_path] = functions
        
        return merged
    
    def _normalize_path(self, file_path: str) -> str:
        """Normalize file path to relative with ./ prefix."""
        path = Path(file_path)
        
        # Convert to relative path if absolute
        try:
            path = path.relative_to(Path.cwd())
        except ValueError:
            pass
        
        # Ensure ./ prefix
        path_str = str(path).replace('\\', '/')
        if not path_str.startswith('./'):
            path_str = './' + path_str
        
        return path_str
    
    def _deep_copy(self, obj: Dict) -> Dict:
        """Deep copy a dictionary."""
        return json.loads(json.dumps(obj))
