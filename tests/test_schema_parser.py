#!/usr/bin/env python3
"""
Unit tests for Informix IDS schema parser.

Tests the SchemaParser and InformixTypeMapper classes.
"""

import unittest
import json
import tempfile
import os
from pathlib import Path

# Add scripts directory to path
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from parse_schema import SchemaParser, InformixTypeMapper


class TestInformixTypeMapper(unittest.TestCase):
    """Test Informix type code mapping."""
    
    def test_varchar_type(self):
        """Test VARCHAR type mapping."""
        result = InformixTypeMapper.map_type(0, 8)
        self.assertEqual(result, "VARCHAR(8)")
    
    def test_varchar_large(self):
        """Test VARCHAR with large length."""
        result = InformixTypeMapper.map_type(0, 255)
        self.assertEqual(result, "VARCHAR(255)")
    
    def test_smallint_type(self):
        """Test SMALLINT type mapping."""
        result = InformixTypeMapper.map_type(1, 0)
        self.assertEqual(result, "SMALLINT")
    
    def test_integer_type(self):
        """Test INTEGER type mapping."""
        result = InformixTypeMapper.map_type(2, 0)
        self.assertEqual(result, "INTEGER")
    
    def test_decimal_type(self):
        """Test DECIMAL type mapping."""
        result = InformixTypeMapper.map_type(5, 3842)
        self.assertEqual(result, "DECIMAL(3842)")
    
    def test_date_type(self):
        """Test DATE type mapping."""
        result = InformixTypeMapper.map_type(7, 4)
        self.assertEqual(result, "DATE")
    
    def test_datetime_type(self):
        """Test DATETIME type mapping."""
        result = InformixTypeMapper.map_type(10, 8)
        self.assertEqual(result, "DATETIME")
    
    def test_serial_type(self):
        """Test SERIAL type mapping."""
        result = InformixTypeMapper.map_type(262, 4)
        self.assertEqual(result, "SERIAL")
    
    def test_unknown_type(self):
        """Test unknown type code."""
        result = InformixTypeMapper.map_type(999, 0)
        self.assertEqual(result, "UNKNOWN(999)")


class TestSchemaParser(unittest.TestCase):
    """Test schema parser functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = SchemaParser()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test files."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def _create_schema_file(self, content: str) -> str:
        """Create a temporary schema file with given content."""
        filepath = os.path.join(self.temp_dir, "test.sch")
        with open(filepath, 'w') as f:
            f.write(content)
        return filepath
    
    def test_parse_single_table(self):
        """Test parsing a single table."""
        content = "account^acc_code^0^8^1^\n"
        filepath = self._create_schema_file(content)
        
        schema = self.parser.parse_file(filepath)
        
        self.assertEqual(len(schema["tables"]), 1)
        self.assertEqual(schema["tables"][0]["name"], "account")
        self.assertEqual(len(schema["tables"][0]["columns"]), 1)
        self.assertEqual(schema["tables"][0]["columns"][0]["name"], "acc_code")
        self.assertEqual(schema["tables"][0]["columns"][0]["type"], "VARCHAR(8)")
    
    def test_parse_multiple_columns(self):
        """Test parsing multiple columns in a table."""
        content = (
            "account^acc_code^0^8^1^\n"
            "account^acc_type^0^2^2^\n"
            "account^acc_balance^5^3842^6^\n"
        )
        filepath = self._create_schema_file(content)
        
        schema = self.parser.parse_file(filepath)
        
        self.assertEqual(len(schema["tables"]), 1)
        self.assertEqual(len(schema["tables"][0]["columns"]), 3)
        
        # Check column names
        column_names = [col["name"] for col in schema["tables"][0]["columns"]]
        self.assertEqual(column_names, ["acc_code", "acc_type", "acc_balance"])
    
    def test_parse_multiple_tables(self):
        """Test parsing multiple tables."""
        content = (
            "account^acc_code^0^8^1^\n"
            "account^acc_type^0^2^2^\n"
            "customer^cust_id^2^4^1^\n"
            "customer^cust_name^0^40^2^\n"
        )
        filepath = self._create_schema_file(content)
        
        schema = self.parser.parse_file(filepath)
        
        self.assertEqual(len(schema["tables"]), 2)
        
        table_names = [table["name"] for table in schema["tables"]]
        self.assertIn("account", table_names)
        self.assertIn("customer", table_names)
    
    def test_parse_all_type_codes(self):
        """Test parsing all supported type codes."""
        content = (
            "types^varchar_col^0^8^1^\n"
            "types^smallint_col^1^2^2^\n"
            "types^integer_col^2^4^3^\n"
            "types^decimal_col^5^3842^4^\n"
            "types^date_col^7^4^5^\n"
            "types^datetime_col^10^8^6^\n"
            "types^serial_col^262^4^7^\n"
        )
        filepath = self._create_schema_file(content)
        
        schema = self.parser.parse_file(filepath)
        
        self.assertEqual(len(schema["tables"]), 1)
        self.assertEqual(len(schema["tables"][0]["columns"]), 7)
        
        types = [col["type"] for col in schema["tables"][0]["columns"]]
        self.assertEqual(types, [
            "VARCHAR(8)",
            "SMALLINT",
            "INTEGER",
            "DECIMAL(3842)",
            "DATE",
            "DATETIME",
            "SERIAL"
        ])
    
    def test_parse_empty_file(self):
        """Test parsing an empty file."""
        content = ""
        filepath = self._create_schema_file(content)
        
        schema = self.parser.parse_file(filepath)
        
        self.assertEqual(len(schema["tables"]), 0)
        self.assertEqual(self.parser.lines_processed, 0)
    
    def test_parse_file_with_empty_lines(self):
        """Test parsing file with empty lines."""
        content = (
            "account^acc_code^0^8^1^\n"
            "\n"
            "account^acc_type^0^2^2^\n"
            "\n"
        )
        filepath = self._create_schema_file(content)
        
        schema = self.parser.parse_file(filepath)
        
        self.assertEqual(len(schema["tables"]), 1)
        self.assertEqual(len(schema["tables"][0]["columns"]), 2)
        self.assertEqual(self.parser.lines_processed, 2)
        self.assertEqual(self.parser.lines_skipped, 2)
    
    def test_parse_file_with_comments(self):
        """Test parsing file with comment lines."""
        content = (
            "# This is a comment\n"
            "account^acc_code^0^8^1^\n"
            "# Another comment\n"
            "account^acc_type^0^2^2^\n"
        )
        filepath = self._create_schema_file(content)
        
        schema = self.parser.parse_file(filepath)
        
        self.assertEqual(len(schema["tables"]), 1)
        self.assertEqual(len(schema["tables"][0]["columns"]), 2)
        self.assertEqual(self.parser.lines_skipped, 2)
    
    def test_parse_invalid_format(self):
        """Test parsing line with invalid format."""
        content = (
            "account^acc_code^0^8^1^\n"
            "invalid_line\n"
            "account^acc_type^0^2^2^\n"
        )
        filepath = self._create_schema_file(content)
        
        schema = self.parser.parse_file(filepath)
        
        self.assertEqual(len(schema["tables"]), 1)
        self.assertEqual(len(schema["tables"][0]["columns"]), 2)
        self.assertEqual(len(self.parser.warnings), 1)
    
    def test_parse_invalid_type_code(self):
        """Test parsing line with invalid type code."""
        content = (
            "account^acc_code^0^8^1^\n"
            "account^bad_col^invalid^8^2^\n"
        )
        filepath = self._create_schema_file(content)
        
        schema = self.parser.parse_file(filepath)
        
        self.assertEqual(len(schema["tables"]), 1)
        self.assertEqual(len(schema["tables"][0]["columns"]), 1)
        self.assertEqual(len(self.parser.errors), 1)
    
    def test_parse_invalid_length(self):
        """Test parsing line with invalid length."""
        content = (
            "account^acc_code^0^8^1^\n"
            "account^bad_col^0^invalid^2^\n"
        )
        filepath = self._create_schema_file(content)
        
        schema = self.parser.parse_file(filepath)
        
        self.assertEqual(len(schema["tables"]), 1)
        self.assertEqual(len(schema["tables"][0]["columns"]), 1)
        self.assertEqual(len(self.parser.errors), 1)
    
    def test_parse_empty_table_name(self):
        """Test parsing line with empty table name."""
        content = (
            "account^acc_code^0^8^1^\n"
            "^col_name^0^8^2^\n"
        )
        filepath = self._create_schema_file(content)
        
        schema = self.parser.parse_file(filepath)
        
        self.assertEqual(len(schema["tables"]), 1)
        self.assertEqual(len(schema["tables"][0]["columns"]), 1)
        self.assertEqual(len(self.parser.warnings), 1)
    
    def test_parse_empty_column_name(self):
        """Test parsing line with empty column name."""
        content = (
            "account^acc_code^0^8^1^\n"
            "account^^0^8^2^\n"
        )
        filepath = self._create_schema_file(content)
        
        schema = self.parser.parse_file(filepath)
        
        self.assertEqual(len(schema["tables"]), 1)
        self.assertEqual(len(schema["tables"][0]["columns"]), 1)
        self.assertEqual(len(self.parser.warnings), 1)
    
    def test_parse_whitespace_handling(self):
        """Test parsing with extra whitespace."""
        content = "  account  ^  acc_code  ^  0  ^  8  ^  1  ^\n"
        filepath = self._create_schema_file(content)
        
        schema = self.parser.parse_file(filepath)
        
        self.assertEqual(len(schema["tables"]), 1)
        self.assertEqual(schema["tables"][0]["name"], "account")
        self.assertEqual(schema["tables"][0]["columns"][0]["name"], "acc_code")
    
    def test_parse_metadata(self):
        """Test that metadata is generated correctly."""
        content = (
            "account^acc_code^0^8^1^\n"
            "account^acc_type^0^2^2^\n"
        )
        filepath = self._create_schema_file(content)
        
        schema = self.parser.parse_file(filepath)
        
        self.assertIn("_metadata", schema)
        self.assertEqual(schema["_metadata"]["version"], "1.0.0")
        self.assertEqual(schema["_metadata"]["lines_processed"], 2)
        self.assertEqual(schema["_metadata"]["tables_count"], 1)
    
    def test_get_table(self):
        """Test get_table method."""
        content = (
            "account^acc_code^0^8^1^\n"
            "customer^cust_id^2^4^1^\n"
        )
        filepath = self._create_schema_file(content)
        
        schema = self.parser.parse_file(filepath)
        
        table = self.parser.get_table("account")
        self.assertIsNotNone(table)
        self.assertEqual(table["name"], "account")
        
        table = self.parser.get_table("nonexistent")
        self.assertIsNone(table)
    
    def test_get_column(self):
        """Test get_column method."""
        content = (
            "account^acc_code^0^8^1^\n"
            "account^acc_type^0^2^2^\n"
        )
        filepath = self._create_schema_file(content)
        
        schema = self.parser.parse_file(filepath)
        
        column = self.parser.get_column("account", "acc_code")
        self.assertIsNotNone(column)
        self.assertEqual(column["name"], "acc_code")
        self.assertEqual(column["type"], "VARCHAR(8)")
        
        column = self.parser.get_column("account", "nonexistent")
        self.assertIsNone(column)
    
    def test_parse_real_schema_file(self):
        """Test parsing the real schema.sch file."""
        schema_file = "tests/sample_codebase/schema.sch"
        
        if not os.path.exists(schema_file):
            self.skipTest(f"Schema file not found: {schema_file}")
        
        schema = self.parser.parse_file(schema_file)
        
        # Should have parsed successfully
        self.assertGreater(len(schema["tables"]), 0)
        self.assertGreater(self.parser.lines_processed, 0)
        
        # Check for expected tables
        table_names = [table["name"] for table in schema["tables"]]
        self.assertIn("account", table_names)
        self.assertIn("abi_fields", table_names)
    
    def test_file_not_found(self):
        """Test error handling for missing file."""
        with self.assertRaises(FileNotFoundError):
            self.parser.parse_file("/nonexistent/path/schema.sch")
    
    def test_column_attributes(self):
        """Test that column attributes are correctly parsed."""
        content = "account^acc_code^0^8^1^\n"
        filepath = self._create_schema_file(content)
        
        schema = self.parser.parse_file(filepath)
        column = schema["tables"][0]["columns"][0]
        
        self.assertEqual(column["name"], "acc_code")
        self.assertEqual(column["type"], "VARCHAR(8)")
        self.assertEqual(column["type_code"], 0)
        self.assertEqual(column["length"], 8)
        self.assertEqual(column["position"], 1)


class TestSchemaParserIntegration(unittest.TestCase):
    """Integration tests for schema parser."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = SchemaParser()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test files."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def _create_schema_file(self, content: str) -> str:
        """Create a temporary schema file with given content."""
        filepath = os.path.join(self.temp_dir, "test.sch")
        with open(filepath, 'w') as f:
            f.write(content)
        return filepath
    
    def test_parse_and_export_json(self):
        """Test parsing and exporting to JSON."""
        content = (
            "account^acc_code^0^8^1^\n"
            "account^acc_type^0^2^2^\n"
            "account^acc_balance^5^3842^6^\n"
        )
        filepath = self._create_schema_file(content)
        
        schema = self.parser.parse_file(filepath)
        
        # Export to JSON
        output_file = os.path.join(self.temp_dir, "output.json")
        with open(output_file, 'w') as f:
            json.dump(schema, f, indent=2)
        
        # Read back and verify
        with open(output_file, 'r') as f:
            loaded_schema = json.load(f)
        
        self.assertEqual(len(loaded_schema["tables"]), 1)
        self.assertEqual(len(loaded_schema["tables"][0]["columns"]), 3)
    
    def test_parse_complex_schema(self):
        """Test parsing a complex schema with many tables."""
        content = (
            "abi_fields^id^0^4^1^\n"
            "abi_fields^name^0^40^2^\n"
            "abi_fields^version^0^5^3^\n"
            "abi_message^id^0^6^1^\n"
            "abi_message^name^0^40^2^\n"
            "abi_message^version^0^5^3^\n"
            "account^acc_code^0^8^1^\n"
            "account^acc_type^0^2^2^\n"
            "account^acc_key^0^35^3^\n"
            "account^acc_name^0^35^4^\n"
            "account^acc_address^0^88^5^\n"
            "account^acc_balance^5^3842^6^\n"
            "account^acc_system^0^1^7^\n"
            "account^acc_del_date^7^4^8^\n"
            "account^acc_start^10^3080^9^\n"
            "account^acc_end^10^3080^10^\n"
        )
        filepath = self._create_schema_file(content)
        
        schema = self.parser.parse_file(filepath)
        
        self.assertEqual(len(schema["tables"]), 3)
        
        # Check account table
        account_table = next(t for t in schema["tables"] if t["name"] == "account")
        self.assertEqual(len(account_table["columns"]), 10)
        
        # Check column types
        types = [col["type"] for col in account_table["columns"]]
        self.assertIn("VARCHAR(8)", types)
        self.assertIn("DECIMAL(3842)", types)
        self.assertIn("DATE", types)
        self.assertIn("DATETIME", types)


if __name__ == "__main__":
    unittest.main()
