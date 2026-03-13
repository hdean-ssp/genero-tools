# File Header Comment Parsing Analysis

## Overview

Analysis of the file header format in `tests/sample_codebase/simple_functions.4gl` to understand the structure and variations needed for parsing code references and author information.

## Current Format Structure

### Header Layout

```
#----------------------------------------------------------------------------------------
#  Program      : commshub.42r
#  $Header
#  Date : 20/03/2024                                                            Author  : richard
#----------------------------------------------------------------------------------------
#  Description:
#  [Description text...]
#
#  [Additional documentation...]
#----------------------------------------------------------------------------------------
#  Modifications:
# Ref        For                Date            Who                     Description
# [Change history rows...]
#----------------------------------------------------------------------------------------
```

### Key Sections

1. **Program/File Info** - Program name, date, author
2. **Description** - File purpose and documentation
3. **Modifications** - Change history table with columns

## Change History Table Format

### Column Structure

The modifications table has the following columns:
- **Ref** - Code reference (e.g., EH100466-4, PRB-299, SR-40356-3)
- **For** - Version/build number (e.g., 1410.05, 1410.10)
- **Date** - Change date (e.g., 20/03/2024)
- **Who** - Author name (e.g., Rich, Greg, Chilly, MartinB)
- **Description** - Change description

### Example Rows

```
#EH100466-4      1410.05        20/03/2024  Rich                Initial
#EH100539-4      1410.10        30/05/2024      Greg            Ad-hoc SMS Messaging
#EH100512-2  1410.16    19/08/2024      Chilly          Email integration
#PRB-299         1410.16        28/08/2024      MartinB         Enhanced MailMerge Error Handling
#EH100512-9  1410.16    29/08/2024      Chilly          Job scheduler send file attachments
#PRB-337         1410.17        05/09/2024      MartinB         Removed changes for PRB-299
#EH100512-15 1410.17    06/09/2024  Chris P     Don't run SMS/Email if not active
#EH100512-9a 1410.18    19/09/2024      Chilly          Use job_task_params for commshub for passing file attachments
#EH100512        1410.20    16/10/2024  Chris P     No background form required
#SR-40356-3      1410.30        01/04/2025      Rich            Error email service
```

## Identified Variations & Challenges

### 1. Inconsistent Spacing
- **Issue:** Mix of tabs and spaces for column alignment
- **Examples:**
  - `#EH100466-4      1410.05` (multiple spaces)
  - `#EH100512-2  1410.16` (fewer spaces)
  - `#EH100512-15 1410.17` (single space)
- **Impact:** Cannot rely on fixed column positions

### 2. Variable Column Widths
- **Issue:** Column content width varies, affecting alignment
- **Examples:**
  - Reference: `EH100512` vs `EH100512-15` vs `SR-40356-3` (different lengths)
  - Author: `Rich` vs `MartinB` vs `Chris P` (different lengths)
  - Description: Single line vs multi-line (e.g., PRB-299 has continuation)
- **Impact:** Column boundaries are not fixed

### 3. Optional Columns
- **Issue:** Not all files may have the "For" column
- **Mentioned:** "in other files the columns may be different, e.g. no 'For' column is common"
- **Impact:** Parser must handle missing columns gracefully

### 4. Multi-line Descriptions
- **Issue:** Some descriptions span multiple lines
- **Example:** PRB-299 entry has description continuing on next line
- **Impact:** Need to detect continuation lines (typically indented or starting with spaces)

### 5. Reference ID Patterns
- **Identified Patterns:**
  - `EH100512` - Alphanumeric prefix + numbers
  - `EH100512-4` - With numeric suffix
  - `EH100512-9a` - With alphanumeric suffix
  - `PRB-299` - Prefix-number format
  - `SR-40356-3` - Prefix-number-number format
- **Regex Pattern:** `[A-Z]+\d+(-\d+)?(-\d+)?[a-z]?` or similar

### 6. Author Name Variations
- **Formats:** Single names (Rich, Greg), Last names (MartinB, Chilly), Full names (Chris P)
- **Spacing:** Names may have leading/trailing spaces due to column alignment
- **Impact:** Need to trim and normalize author names

### 7. Date Format
- **Format:** DD/MM/YYYY (e.g., 20/03/2024)
- **Consistency:** Appears consistent in this file
- **Note:** May vary in other files

## Parsing Requirements

### Must Handle

1. **Reference Extraction**
   - Extract code references using pattern matching
   - Support multiple reference formats
   - Handle references with suffixes (numeric and alphanumeric)

2. **Author Extraction**
   - Extract author names from "Who" column
   - Normalize whitespace (trim leading/trailing spaces)
   - Handle various name formats (single, multiple words, initials)

3. **Flexible Column Parsing**
   - Don't assume fixed column positions
   - Parse by identifying column headers first
   - Use delimiter-based or position-range parsing
   - Handle missing columns gracefully

4. **Whitespace Normalization**
   - Convert tabs to spaces
   - Collapse multiple spaces
   - Handle variable spacing between columns

5. **Multi-line Handling**
   - Detect continuation lines
   - Merge multi-line descriptions
   - Preserve description content

### Should Handle

1. **Optional Columns** - Some files may not have "For" column
2. **Different Table Formats** - Column order may vary
3. **Various Date Formats** - Normalize to ISO 8601
4. **Comment Styles** - Different comment markers or formats

## Proposed Implementation Approach

### Phase 1: Header Detection
1. Find "Modifications:" section marker
2. Identify column header row (contains "Ref", "Date", "Who", etc.)
3. Extract column positions/names from header

### Phase 2: Row Parsing
1. Identify data rows (start with reference pattern)
2. Parse columns based on detected header positions
3. Handle multi-line descriptions
4. Extract reference, author, date, description

### Phase 3: Data Extraction
1. Extract code references using regex
2. Extract and normalize author names
3. Parse dates to ISO 8601 format
4. Store in structured format

### Phase 4: Storage
1. Store in `file_references` table (reference_id, author, date, description)
2. Store in `file_authors` table (author, change count, date range)
3. Include in workspace.json output

## Example Extracted Data

For the sample file, extraction should yield:

```json
{
  "file_references": [
    {"reference": "EH100466-4", "author": "Rich", "date": "2024-03-20", "description": "Initial"},
    {"reference": "EH100539-4", "author": "Greg", "date": "2024-05-30", "description": "Ad-hoc SMS Messaging"},
    {"reference": "EH100512-2", "author": "Chilly", "date": "2024-08-19", "description": "Email integration"},
    {"reference": "PRB-299", "author": "MartinB", "date": "2024-08-28", "description": "Enhanced MailMerge Error Handling - extra 11th parameter passed to commshub_control"},
    {"reference": "EH100512-9", "author": "Chilly", "date": "2024-08-29", "description": "Job scheduler send file attachments"},
    {"reference": "PRB-337", "author": "MartinB", "date": "2024-09-05", "description": "Removed changes for PRB-299"},
    {"reference": "EH100512-15", "author": "Chris P", "date": "2024-09-06", "description": "Don't run SMS/Email if not active"},
    {"reference": "EH100512-9a", "author": "Chilly", "date": "2024-09-19", "description": "Use job_task_params for commshub for passing file attachments"},
    {"reference": "EH100512", "author": "Chris P", "date": "2024-10-16", "description": "No background form required"},
    {"reference": "SR-40356-3", "author": "Rich", "date": "2025-04-01", "description": "Error email service"}
  ],
  "file_authors": [
    {"author": "Rich", "first_change": "2024-03-20", "last_change": "2025-04-01", "count": 2},
    {"author": "Greg", "first_change": "2024-05-30", "last_change": "2024-05-30", "count": 1},
    {"author": "Chilly", "first_change": "2024-08-19", "last_change": "2024-09-19", "count": 3},
    {"author": "MartinB", "first_change": "2024-08-28", "last_change": "2024-09-05", "count": 2},
    {"author": "Chris P", "first_change": "2024-09-06", "last_change": "2024-10-16", "count": 2}
  ]
}
```

## Next Steps

1. Implement flexible header parser in AWK/Python
2. Test with sample file
3. Collect additional sample files with variations
4. Refine parser based on real-world variations
5. Add database schema and queries
6. Update documentation with examples
