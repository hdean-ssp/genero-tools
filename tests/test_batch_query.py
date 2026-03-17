#!/usr/bin/env python3
"""Unit tests for batch query handler."""

import pytest
import json
import tempfile
import sqlite3
from pathlib import Path
import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from batch_query_handler import execute_batch_query, execute_single_query, load_query_module


@pytest.fixture
def sample_db():
    """Create a sample database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Create tables
    c.execute('''CREATE TABLE files (
        id INTEGER PRIMARY KEY,
        path TEXT UNIQUE NOT NULL,
        type TEXT
    )''')
    
    c.execute('''CREATE TABLE functions (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        file_id INTEGER NOT NULL,
        line_start INTEGER,
        line_end INTEGER,
        signature TEXT,
        loc INTEGER,
        complexity INTEGER,
        FOREIGN KEY(file_id) REFERENCES files(id)
    )''')
    
    c.execute('''CREATE TABLE parameters (
        id INTEGER PRIMARY KEY,
        function_id INTEGER NOT NULL,
        name TEXT,
        type TEXT,
        FOREIGN KEY(function_id) REFERENCES functions(id)
    )''')
    
    c.execute('''CREATE TABLE returns (
        id INTEGER PRIMARY KEY,
        function_id INTEGER NOT NULL,
        name TEXT,
        type TEXT,
        FOREIGN KEY(function_id) REFERENCES functions(id)
    )''')
    
    c.execute('''CREATE TABLE calls (
        id INTEGER PRIMARY KEY,
        caller_id INTEGER NOT NULL,
        callee_name TEXT NOT NULL,
        FOREIGN KEY(caller_id) REFERENCES functions(id)
    )''')
    
    # Insert test data
    c.execute("INSERT INTO files (path, type) VALUES (?, ?)", ("test.4gl", "4GL"))
    file_id = c.lastrowid
    
    # Insert functions
    c.execute('''INSERT INTO functions (name, file_id, line_start, line_end, signature, loc, complexity)
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
              ("func_a", file_id, 1, 10, "FUNCTION func_a()", 10, 1))
    func_a_id = c.lastrowid
    
    c.execute('''INSERT INTO functions (name, file_id, line_start, line_end, signature, loc, complexity)
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
              ("func_b", file_id, 11, 20, "FUNCTION func_b()", 10, 1))
    func_b_id = c.lastrowid
    
    c.execute('''INSERT INTO functions (name, file_id, line_start, line_end, signature, loc, complexity)
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
              ("func_c", file_id, 21, 30, "FUNCTION func_c()", 10, 1))
    func_c_id = c.lastrowid
    
    # Insert call relationships
    c.execute("INSERT INTO calls (caller_id, callee_name) VALUES (?, ?)", (func_a_id, "func_b"))
    c.execute("INSERT INTO calls (caller_id, callee_name) VALUES (?, ?)", (func_b_id, "func_c"))
    
    conn.commit()
    conn.close()
    
    yield db_path
    
    # Cleanup
    Path(db_path).unlink()


@pytest.fixture
def sample_modules_db():
    """Create a sample modules database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Create tables
    c.execute('''CREATE TABLE modules (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE NOT NULL
    )''')
    
    c.execute('''CREATE TABLE module_files (
        id INTEGER PRIMARY KEY,
        module_id INTEGER NOT NULL,
        file_name TEXT,
        file_path TEXT,
        category TEXT,
        FOREIGN KEY(module_id) REFERENCES modules(id)
    )''')
    
    # Insert test data
    c.execute("INSERT INTO modules (name) VALUES (?)", ("core",))
    module_id = c.lastrowid
    
    c.execute('''INSERT INTO module_files (module_id, file_name, file_path, category)
                 VALUES (?, ?, ?, ?)''',
              (module_id, "test.4gl", "src/test.4gl", "4GLS"))
    
    conn.commit()
    conn.close()
    
    yield db_path
    
    # Cleanup
    Path(db_path).unlink()


class TestExecuteSingleQuery:
    """Tests for execute_single_query function."""
    
    def test_find_function_success(self, sample_db):
        """Test successful find-function query."""
        query_db = load_query_module('.')
        
        query_request = {
            'command': 'find-function',
            'args': ['func_a']
        }
        
        result = execute_single_query(query_db, query_request, sample_db, '')
        
        assert result['status'] == 'success'
        assert 'time_ms' in result
        assert result['time_ms'] > 0
        assert 'data' in result
        assert isinstance(result['data'], list)
        assert len(result['data']) > 0
        assert result['data'][0]['name'] == 'func_a'
    
    def test_search_functions_success(self, sample_db):
        """Test successful search-functions query."""
        query_db = load_query_module('.')
        
        query_request = {
            'command': 'search-functions',
            'args': ['func_*']
        }
        
        result = execute_single_query(query_db, query_request, sample_db, '')
        
        assert result['status'] == 'success'
        assert 'time_ms' in result
        assert 'data' in result
        assert isinstance(result['data'], list)
    
    def test_unknown_command(self, sample_db):
        """Test error handling for unknown command."""
        query_db = load_query_module('.')
        
        query_request = {
            'command': 'unknown-command',
            'args': []
        }
        
        result = execute_single_query(query_db, query_request, sample_db, '')
        
        assert result['status'] == 'error'
        assert 'error' in result
        assert 'Unknown command' in result['error']
    
    def test_missing_command(self, sample_db):
        """Test error handling for missing command."""
        query_db = load_query_module('.')
        
        query_request = {
            'args': ['func_a']
        }
        
        result = execute_single_query(query_db, query_request, sample_db, '')
        
        assert result['status'] == 'error'
        assert 'error' in result
    
    def test_timing_information(self, sample_db):
        """Test that timing information is collected."""
        query_db = load_query_module('.')
        
        query_request = {
            'command': 'find-function',
            'args': ['func_a']
        }
        
        result = execute_single_query(query_db, query_request, sample_db, '')
        
        assert 'time_ms' in result
        assert isinstance(result['time_ms'], float)
        assert result['time_ms'] >= 0


class TestExecuteBatchQuery:
    """Tests for execute_batch_query function."""
    
    def test_single_query_batch(self, sample_db):
        """Test batch with single query."""
        batch_request = {
            'queries': [
                {
                    'id': 'q1',
                    'command': 'find-function',
                    'args': ['func_a']
                }
            ]
        }
        
        result = execute_batch_query(batch_request, sample_db, '', '.')
        
        assert result['status'] == 'success'
        assert 'batch_id' in result
        assert 'total_time_ms' in result
        assert 'results' in result
        assert len(result['results']) == 1
        assert result['results'][0]['query_id'] == 'q1'
        assert result['results'][0]['status'] == 'success'
    
    def test_multiple_queries_batch(self, sample_db):
        """Test batch with multiple independent queries."""
        batch_request = {
            'queries': [
                {
                    'id': 'q1',
                    'command': 'find-function',
                    'args': ['func_a']
                },
                {
                    'id': 'q2',
                    'command': 'find-function',
                    'args': ['func_b']
                },
                {
                    'id': 'q3',
                    'command': 'search-functions',
                    'args': ['func_*']
                }
            ]
        }
        
        result = execute_batch_query(batch_request, sample_db, '', '.')
        
        assert result['status'] == 'success'
        assert len(result['results']) == 3
        
        # Verify all queries executed
        for i, query_result in enumerate(result['results']):
            assert query_result['query_id'] == f'q{i+1}'
            assert 'status' in query_result
            assert 'time_ms' in query_result
    
    def test_query_ordering_preserved(self, sample_db):
        """Test that query order is preserved in results."""
        batch_request = {
            'queries': [
                {'id': 'first', 'command': 'find-function', 'args': ['func_a']},
                {'id': 'second', 'command': 'find-function', 'args': ['func_b']},
                {'id': 'third', 'command': 'find-function', 'args': ['func_c']}
            ]
        }
        
        result = execute_batch_query(batch_request, sample_db, '', '.')
        
        assert result['results'][0]['query_id'] == 'first'
        assert result['results'][1]['query_id'] == 'second'
        assert result['results'][2]['query_id'] == 'third'
    
    def test_error_isolation(self, sample_db):
        """Test that errors in one query don't affect others."""
        batch_request = {
            'queries': [
                {'id': 'q1', 'command': 'find-function', 'args': ['func_a']},
                {'id': 'q2', 'command': 'unknown-command', 'args': []},
                {'id': 'q3', 'command': 'find-function', 'args': ['func_b']}
            ]
        }
        
        result = execute_batch_query(batch_request, sample_db, '', '.')
        
        assert result['status'] == 'success'
        assert result['results'][0]['status'] == 'success'
        assert result['results'][1]['status'] == 'error'
        assert result['results'][2]['status'] == 'success'
    
    def test_timing_information_collected(self, sample_db):
        """Test that timing information is collected for batch and queries."""
        batch_request = {
            'queries': [
                {'id': 'q1', 'command': 'find-function', 'args': ['func_a']},
                {'id': 'q2', 'command': 'find-function', 'args': ['func_b']}
            ]
        }
        
        result = execute_batch_query(batch_request, sample_db, '', '.')
        
        assert 'total_time_ms' in result
        assert result['total_time_ms'] > 0
        
        for query_result in result['results']:
            assert 'time_ms' in query_result
            assert query_result['time_ms'] >= 0
    
    def test_missing_queries_array(self, sample_db):
        """Test error handling for missing queries array."""
        batch_request = {}
        
        result = execute_batch_query(batch_request, sample_db, '', '.')
        
        assert result['status'] == 'error'
        assert 'error' in result
    
    def test_empty_queries_array(self, sample_db):
        """Test error handling for empty queries array."""
        batch_request = {'queries': []}
        
        result = execute_batch_query(batch_request, sample_db, '', '.')
        
        assert result['status'] == 'error'
        assert 'error' in result
    
    def test_invalid_queries_type(self, sample_db):
        """Test error handling for invalid queries type."""
        batch_request = {'queries': 'not_an_array'}
        
        result = execute_batch_query(batch_request, sample_db, '', '.')
        
        assert result['status'] == 'error'
        assert 'error' in result
    
    def test_query_without_command(self, sample_db):
        """Test error handling for query without command."""
        batch_request = {
            'queries': [
                {'id': 'q1', 'args': ['func_a']}
            ]
        }
        
        result = execute_batch_query(batch_request, sample_db, '', '.')
        
        assert result['status'] == 'success'
        assert result['results'][0]['status'] == 'error'
    
    def test_auto_generated_query_ids(self, sample_db):
        """Test that query IDs are auto-generated if not provided."""
        batch_request = {
            'queries': [
                {'command': 'find-function', 'args': ['func_a']},
                {'command': 'find-function', 'args': ['func_b']}
            ]
        }
        
        result = execute_batch_query(batch_request, sample_db, '', '.')
        
        assert result['status'] == 'success'
        assert 'query_id' in result['results'][0]
        assert 'query_id' in result['results'][1]
    
    def test_batch_id_generation(self, sample_db):
        """Test that batch ID is generated."""
        batch_request = {
            'queries': [
                {'id': 'q1', 'command': 'find-function', 'args': ['func_a']}
            ]
        }
        
        result = execute_batch_query(batch_request, sample_db, '', '.')
        
        assert 'batch_id' in result
        assert result['batch_id'].startswith('batch_')
    
    def test_large_batch_query(self, sample_db):
        """Test batch with many queries."""
        queries = [
            {'id': f'q{i}', 'command': 'find-function', 'args': ['func_a']}
            for i in range(50)
        ]
        
        batch_request = {'queries': queries}
        
        result = execute_batch_query(batch_request, sample_db, '', '.')
        
        assert result['status'] == 'success'
        assert len(result['results']) == 50
        
        # Verify all queries executed
        for i, query_result in enumerate(result['results']):
            assert query_result['query_id'] == f'q{i}'
            assert query_result['status'] == 'success'


class TestBatchQueryPerformance:
    """Tests for batch query performance characteristics."""
    
    def test_batch_query_timing_accuracy(self, sample_db):
        """Test that timing information is accurate."""
        batch_request = {
            'queries': [
                {'id': 'q1', 'command': 'find-function', 'args': ['func_a']},
                {'id': 'q2', 'command': 'find-function', 'args': ['func_b']}
            ]
        }
        
        result = execute_batch_query(batch_request, sample_db, '', '.')
        
        # Total time should be >= sum of individual query times
        individual_times = sum(q['time_ms'] for q in result['results'])
        assert result['total_time_ms'] >= individual_times * 0.9  # Allow 10% overhead
    
    def test_batch_query_response_format(self, sample_db):
        """Test that batch query response has correct format."""
        batch_request = {
            'queries': [
                {'id': 'q1', 'command': 'find-function', 'args': ['func_a']}
            ]
        }
        
        result = execute_batch_query(batch_request, sample_db, '', '.')
        
        # Verify response structure
        assert isinstance(result, dict)
        assert 'batch_id' in result
        assert 'status' in result
        assert 'total_time_ms' in result
        assert 'results' in result
        assert isinstance(result['results'], list)
        
        # Verify query result structure
        query_result = result['results'][0]
        assert 'query_id' in query_result
        assert 'status' in query_result
        assert 'time_ms' in query_result
        assert 'data' in query_result or 'error' in query_result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
