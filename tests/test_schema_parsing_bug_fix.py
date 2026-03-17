#!/usr/bin/env python3
"""
Test for schema parsing bug fix.

Bug: When passing a workspace with castle.sch in its root, the schema parsing
would fail silently with message "Could not parse schema file (type resolution 
will be skipped)" without showing the actual error.

Fix: 
1. Improved error handling in parse_schema.py with better diagnostics
2. Added encoding detection (UTF-8, Latin-1, ISO-8859-1, CP1252)
3. Added format validation to detect non-pipe-delimited files
4. Added empty file detection
5. Modified generate_all.sh to capture and display error messages instead of 
   silencing them with 2>/dev/null
"""

import unittest
import tempfile
import json
import os
import sys
from pathlib import Path
import subprocess

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from parse_schema import SchemaParser


class TestSchemaParsing(unittest.TestCase):
    """Test schema parsing with various file formats."""
    
    def setUp(self):
        """Create temporary directory for test files."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_valid_schema_file(self):
        """Test parsing a valid schema file."""
        schema_file = os.path.join(self.temp_dir, "valid.sch")
        with open(schema_file, 'w') as f:
            f.write("users^id^2^4^1^\n")
            f.write("users^name^0^100^2^\n")
            f.write("users^email^0^255^3^\n")
        
        parser = SchemaParser()
        schema = parser.parse_file(schema_file)
        
        self.assertEqual(len(schema['tables']), 1)
        self.assertEqual(schema['tables'][0]['name'], 'users')
        self.assertEqual(len(schema['tables'][0]['columns']), 3)
        self.assertEqual(parser.lines_processed, 3)
    
    def test_empty_schema_file(self):
        """Test that empty schema files are detected."""
        schema_file = os.path.join(self.temp_dir, "empty.sch")
        Path(schema_file).touch()
        
        # The parser should handle empty files gracefully
        parser = SchemaParser()
        schema = parser.parse_file(schema_file)
        
        self.assertEqual(len(schema['tables']), 0)
        self.assertEqual(parser.lines_processed, 0)
    
    def test_schema_with_comments(self):
        """Test parsing schema file with comment lines."""
        schema_file = os.path.join(self.temp_dir, "comments.sch")
        with open(schema_file, 'w') as f:
            f.write("# This is a comment\n")
            f.write("users^id^2^4^1^\n")
            f.write("# Another comment\n")
            f.write("users^name^0^100^2^\n")
        
        parser = SchemaParser()
        schema = parser.parse_file(schema_file)
        
        self.assertEqual(len(schema['tables']), 1)
        self.assertEqual(parser.lines_processed, 2)
        self.assertEqual(parser.lines_skipped, 2)  # 2 comment lines
    
    def test_schema_with_invalid_lines(self):
        """Test parsing schema file with invalid lines."""
        schema_file = os.path.join(self.temp_dir, "invalid_lines.sch")
        with open(schema_file, 'w') as f:
            f.write("users^id^2^4^1^\n")
            f.write("invalid_line_without_enough_fields\n")
            f.write("users^name^0^100^2^\n")
        
        parser = SchemaParser()
        schema = parser.parse_file(schema_file)
        
        self.assertEqual(len(schema['tables']), 1)
        self.assertEqual(parser.lines_processed, 2)
        self.assertEqual(len(parser.warnings), 1)
    
    def test_schema_with_latin1_encoding(self):
        """Test parsing schema file with Latin-1 encoding."""
        schema_file = os.path.join(self.temp_dir, "latin1.sch")
        with open(schema_file, 'w', encoding='latin-1') as f:
            f.write("users^id^2^4^1^\n")
            f.write("users^name^0^100^2^\n")
        
        parser = SchemaParser()
        schema = parser.parse_file(schema_file)
        
        self.assertEqual(len(schema['tables']), 1)
        self.assertEqual(parser.lines_processed, 2)
    
    def test_parse_schema_cli_with_invalid_format(self):
        """Test CLI error handling with invalid format."""
        schema_file = os.path.join(self.temp_dir, "invalid_format.sch")
        output_file = os.path.join(self.temp_dir, "output.json")
        
        with open(schema_file, 'w') as f:
            f.write("this is not pipe delimited\n")
        
        # Run the script and capture output
        result = subprocess.run(
            ['python3', 'scripts/parse_schema.py', schema_file, output_file],
            capture_output=True,
            text=True
        )
        
        # Should fail with exit code 1
        self.assertEqual(result.returncode, 1)
        # Should show error about format
        self.assertIn("pipe-delimited format", result.stderr)
    
    def test_parse_schema_cli_with_empty_file(self):
        """Test CLI error handling with empty file."""
        schema_file = os.path.join(self.temp_dir, "empty.sch")
        output_file = os.path.join(self.temp_dir, "output.json")
        
        Path(schema_file).touch()
        
        # Run the script and capture output
        result = subprocess.run(
            ['python3', 'scripts/parse_schema.py', schema_file, output_file],
            capture_output=True,
            text=True
        )
        
        # Should fail with exit code 1
        self.assertEqual(result.returncode, 1)
        # Should show error about empty file
        self.assertIn("empty", result.stderr.lower())
    
    def test_parse_schema_cli_with_valid_file(self):
        """Test CLI with valid schema file."""
        schema_file = os.path.join(self.temp_dir, "valid.sch")
        output_file = os.path.join(self.temp_dir, "output.json")
        
        with open(schema_file, 'w') as f:
            f.write("users^id^2^4^1^\n")
            f.write("users^name^0^100^2^\n")
        
        # Run the script
        result = subprocess.run(
            ['python3', 'scripts/parse_schema.py', schema_file, output_file],
            capture_output=True,
            text=True
        )
        
        # Should succeed
        self.assertEqual(result.returncode, 0)
        # Output file should exist and be valid JSON
        self.assertTrue(os.path.exists(output_file))
        with open(output_file) as f:
            data = json.load(f)
        self.assertEqual(len(data['tables']), 1)


if __name__ == '__main__':
    unittest.main()
