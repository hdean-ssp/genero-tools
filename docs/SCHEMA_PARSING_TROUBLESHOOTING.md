# Schema Parsing Troubleshooting Guide

## Common Issues and Solutions

### Issue: "Schema file does not appear to be in pipe-delimited format"

**Cause**: The schema file is not in the correct Informix IDS format.

**Expected Format**:
```
table_name^column_name^type_code^length^position^
```

**Example**:
```
users^id^2^4^1^
users^name^0^100^2^
users^email^0^255^3^
```

**Solution**:
1. Verify the file uses `^` (caret) as the delimiter, not other characters like `|`, `,`, or tabs
2. Ensure each line has at least 5 fields separated by `^`
3. Check that the file ends with `^` on each line

### Issue: "Schema file is empty"

**Cause**: The schema file exists but contains no data.

**Solution**:
1. Verify the file is not empty: `wc -l castle.sch`
2. Add schema data to the file
3. Ensure the file has proper line endings (Unix LF, not Windows CRLF)

### Issue: "Could not read schema file with any supported encoding"

**Cause**: The file is in an unsupported encoding.

**Supported Encodings**:
- UTF-8 (default)
- Latin-1 (ISO-8859-1)
- ISO-8859-1
- CP1252 (Windows)

**Solution**:
1. Convert the file to UTF-8: `iconv -f ISO-8859-1 -t UTF-8 castle.sch > castle_utf8.sch`
2. Use the converted file instead

### Issue: "Could not parse schema file (type resolution will be skipped)"

**Cause**: The schema parser encountered an error.

**Solution**:
1. Run the parser directly to see detailed error messages:
   ```bash
   python3 scripts/parse_schema.py castle.sch schema.json
   ```
2. Check the error output for specific issues
3. Refer to other issues in this guide based on the error message

## Validating Schema Files

### Manual Validation

Check the first few lines of your schema file:
```bash
head -5 castle.sch
```

Expected output:
```
table1^col1^2^4^1^
table1^col2^0^100^2^
table2^col1^2^4^1^
table2^col2^7^4^2^
```

### Using the Parser

Test the parser directly:
```bash
python3 scripts/parse_schema.py castle.sch test_output.json
```

If successful, you'll see:
```
✓ Parsed X lines from castle.sch
✓ Found Y tables
✓ Output written to test_output.json
```

## Type Code Reference

| Code | Genero Type | Example |
|------|-------------|---------|
| 0 | VARCHAR(length) | VARCHAR(100) |
| 1 | SMALLINT | SMALLINT |
| 2 | INTEGER | INTEGER |
| 5 | DECIMAL(length) | DECIMAL(10) |
| 7 | DATE | DATE |
| 10 | DATETIME | DATETIME |
| 262 | SERIAL | SERIAL |

## Debugging Tips

### Enable Verbose Output

Run generate_all.sh with verbose mode:
```bash
VERBOSE=1 bash generate_all.sh /path/to/workspace
```

### Check Generated Schema JSON

After parsing, examine the generated schema.json:
```bash
python3 scripts/parse_schema.py castle.sch schema.json
cat schema.json | python3 -m json.tool | head -50
```

### Verify Database Loading

Check if the schema was loaded into the database:
```bash
sqlite3 workspace.db "SELECT COUNT(*) FROM schema_tables;"
sqlite3 workspace.db "SELECT * FROM schema_tables LIMIT 5;"
```

## Performance Considerations

For large schema files (>10,000 lines):
1. The parser may take a few seconds
2. Database loading may take additional time
3. Type resolution will be slower

Monitor progress with:
```bash
VERBOSE=1 bash generate_all.sh /path/to/workspace
```

## Getting Help

If you encounter issues:

1. **Check the error message**: The parser now provides detailed error messages
2. **Validate the file format**: Use the validation steps above
3. **Check the documentation**: See `docs/SCHEMA_RESOLUTION_IMPLEMENTATION.md`
4. **Review test cases**: See `tests/test_schema_parsing_bug_fix.py`

## Related Documentation

- [Schema Parsing Bug Fix](SCHEMA_PARSING_BUG_FIX.md)
- [Schema Resolution Implementation](SCHEMA_RESOLUTION_IMPLEMENTATION.md)
- [Schema Parsing Guide](archive/SCHEMA_PARSING_GUIDE.md)
