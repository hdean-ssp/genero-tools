#!/usr/bin/env python3
"""
Process modular data from AWK output and generate modulars.json.

This script:
1. Reads raw modular data from AWK (GLOBALS and IMPORT statements)
2. Aggregates by file
3. Generates modulars.json with metadata
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any


def process_modulars(input_file: str, output_file: str, version: str, timestamp: str, total_files: int) -> None:
    """
    Process modular data and generate output JSON.
    
    Input format (one JSON object per line):
    {"file":"path/to/file.4gl","globals":["GLOBAL1","GLOBAL2"],"imports":["IMPORT1"]}
    
    Output format:
    {
        "_metadata": {...},
        "path/to/file.4gl": {
            "globals": ["GLOBAL1", "GLOBAL2"],
            "imports": ["IMPORT1"]
        }
    }
    """
    modulars_data = {
        "_metadata": {
            "version": version,
            "generated": timestamp,
            "files_processed": total_files
        }
    }
    
    # Read and process input
    try:
        with open(input_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                try:
                    obj = json.loads(line)
                    file_path = obj.get('file', '')
                    
                    if file_path:
                        modulars_data[file_path] = {
                            'globals': obj.get('globals', []),
                            'imports': obj.get('imports', [])
                        }
                except json.JSONDecodeError as e:
                    print(f"Warning: Could not parse line: {line}", file=sys.stderr)
                    continue
    except FileNotFoundError:
        print(f"Error: Input file not found: {input_file}", file=sys.stderr)
        sys.exit(1)
    
    # Write output
    try:
        with open(output_file, 'w') as f:
            json.dump(modulars_data, f, indent=2)
        print(f"Generated {output_file} with {len(modulars_data) - 1} files", file=sys.stderr)
    except IOError as e:
        print(f"Error: Could not write output file: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main entry point."""
    if len(sys.argv) < 5:
        print("Usage: process_modulars.py <input_file> <output_file> <version> <timestamp> <total_files>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    version = sys.argv[3]
    timestamp = sys.argv[4]
    total_files = int(sys.argv[5])
    
    process_modulars(input_file, output_file, version, timestamp, total_files)


if __name__ == '__main__':
    main()
