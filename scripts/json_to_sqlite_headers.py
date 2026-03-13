#!/usr/bin/env python3
"""Convert header JSON to SQLite database tables for efficient querying."""

import json
import sqlite3
import sys
import os
from pathlib import Path


def normalize_path(path: str) -> str:
    """Normalize path to match workspace.json format."""
    # Convert absolute paths to relative if possible
    if os.path.isabs(path):
        try:
            path = os.path.relpath(path)
        except ValueError:
            pass
    
    # Ensure relative paths start with ./
    if not path.startswith('./') and not path.startswith('/'):
        path = './' + path
    
    return path


def create_headers_db(headers_json_file: str, db_file: str) -> None:
    """
    Create or update SQLite database with header metadata tables.
    
    Args:
        headers_json_file: Path to headers JSON file (one JSON per line)
        db_file: Path to SQLite database (will be created or updated)
    """
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    
    # Create file_references table
    c.execute('''CREATE TABLE IF NOT EXISTS file_references
                 (id INTEGER PRIMARY KEY, file_id INTEGER, reference_id TEXT, 
                  author TEXT, change_date TEXT, description TEXT,
                  FOREIGN KEY(file_id) REFERENCES files(id))''')
    
    # Create file_authors table
    c.execute('''CREATE TABLE IF NOT EXISTS file_authors
                 (id INTEGER PRIMARY KEY, file_id INTEGER, author TEXT,
                  first_change_date TEXT, last_change_date TEXT, change_count INTEGER,
                  FOREIGN KEY(file_id) REFERENCES files(id))''')
    
    # Create indexes
    c.execute('CREATE INDEX IF NOT EXISTS idx_file_references_file ON file_references(file_id)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_file_references_ref ON file_references(reference_id)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_file_references_author ON file_references(author)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_file_authors_file ON file_authors(file_id)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_file_authors_author ON file_authors(author)')
    
    # Load header data
    try:
        if not os.path.exists(headers_json_file) or os.path.getsize(headers_json_file) == 0:
            # No headers to process
            conn.commit()
            conn.close()
            print(f"No header data to process")
            return
        
        with open(headers_json_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                try:
                    data = json.loads(line)
                    filepath = data.get('file')
                    
                    if not filepath:
                        continue
                    
                    # Normalize path to match database
                    normalized_path = normalize_path(filepath)
                    
                    # Get or create file entry
                    c.execute('SELECT id FROM files WHERE path = ?', (normalized_path,))
                    result = c.fetchone()
                    
                    if result:
                        file_id = result[0]
                    else:
                        # File doesn't exist in database yet, skip
                        continue
                    
                    # Insert file references
                    for ref in data.get('file_references', []):
                        try:
                            c.execute('''INSERT INTO file_references 
                                        (file_id, reference_id, author, change_date, description)
                                        VALUES (?, ?, ?, ?, ?)''',
                                     (file_id, ref.get('reference'), ref.get('author'),
                                      ref.get('date'), ref.get('description')))
                        except Exception:
                            # Skip individual reference insertion errors
                            continue
                    
                    # Insert file authors
                    for author in data.get('file_authors', []):
                        try:
                            c.execute('''INSERT INTO file_authors
                                        (file_id, author, first_change_date, last_change_date, change_count)
                                        VALUES (?, ?, ?, ?, ?)''',
                                     (file_id, author.get('author'), author.get('first_change'),
                                      author.get('last_change'), author.get('count')))
                        except Exception:
                            # Skip individual author insertion errors
                            continue
                
                except json.JSONDecodeError:
                    # Skip malformed JSON lines
                    continue
    
    except Exception as e:
        # Log error but continue
        print(f"Warning: Error processing headers: {e}", file=sys.stderr)
    
    conn.commit()
    conn.close()
    print(f"Updated {db_file} with header metadata")


def main():
    if len(sys.argv) < 3:
        print("Usage: json_to_sqlite_headers.py <headers_json_file> <db_file>", file=sys.stderr)
        sys.exit(1)
    
    headers_json_file = sys.argv[1]
    db_file = sys.argv[2]
    
    if not Path(headers_json_file).exists():
        print(f"Error: {headers_json_file} not found", file=sys.stderr)
        sys.exit(1)
    
    try:
        create_headers_db(headers_json_file, db_file)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
