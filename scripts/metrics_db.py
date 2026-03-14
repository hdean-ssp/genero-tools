#!/usr/bin/env python3
"""Database integration for metrics storage and retrieval."""

import sqlite3
from typing import List, Optional, Dict
from metrics_models import FunctionMetrics


class MetricsDatabase:
    """Store and retrieve metrics from SQLite database."""
    
    def __init__(self, db_file: str):
        """Initialize database connection."""
        self.db_file = db_file
        self.conn = None
    
    def connect(self):
        """Connect to database."""
        self.conn = sqlite3.connect(self.db_file)
        self.conn.row_factory = sqlite3.Row
    
    def disconnect(self):
        """Disconnect from database."""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def create_schema(self):
        """Create metrics tables if they don't exist."""
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        
        # Create function_metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS function_metrics (
                id INTEGER PRIMARY KEY,
                function_id INTEGER NOT NULL,
                file_path TEXT NOT NULL,
                loc INTEGER NOT NULL,
                complexity INTEGER NOT NULL,
                local_variables INTEGER NOT NULL,
                parameters INTEGER NOT NULL,
                return_count INTEGER NOT NULL,
                call_depth INTEGER NOT NULL,
                early_returns INTEGER NOT NULL,
                comment_lines INTEGER NOT NULL,
                comment_ratio REAL NOT NULL,
                is_isolated BOOLEAN NOT NULL,
                has_dependencies BOOLEAN NOT NULL,
                FOREIGN KEY (function_id) REFERENCES functions(id),
                UNIQUE(function_id)
            )
        ''')
        
        # Create naming_violations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS naming_violations (
                id INTEGER PRIMARY KEY,
                function_id INTEGER NOT NULL,
                convention_type TEXT NOT NULL,
                violation_message TEXT NOT NULL,
                severity TEXT NOT NULL,
                FOREIGN KEY (function_id) REFERENCES functions(id)
            )
        ''')
        
        # Create duplication_candidates table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS duplication_candidates (
                id INTEGER PRIMARY KEY,
                function1_id INTEGER NOT NULL,
                function2_id INTEGER NOT NULL,
                similarity REAL NOT NULL,
                FOREIGN KEY (function1_id) REFERENCES functions(id),
                FOREIGN KEY (function2_id) REFERENCES functions(id),
                UNIQUE(function1_id, function2_id)
            )
        ''')
        
        # Create indexes
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_function_metrics_complexity
            ON function_metrics(complexity)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_function_metrics_loc
            ON function_metrics(loc)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_function_metrics_isolated
            ON function_metrics(is_isolated)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_naming_violations_severity
            ON naming_violations(severity)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_duplication_similarity
            ON duplication_candidates(similarity DESC)
        ''')
        
        self.conn.commit()
    
    def store_metrics(self, metrics: FunctionMetrics, function_id: int):
        """Store function metrics in database."""
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO function_metrics
            (function_id, file_path, loc, complexity, local_variables, parameters,
             return_count, call_depth, early_returns, comment_lines, comment_ratio,
             is_isolated, has_dependencies)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            function_id,
            metrics.file_path,
            metrics.loc,
            metrics.complexity,
            metrics.local_variables,
            metrics.parameters,
            metrics.return_count,
            metrics.call_depth,
            metrics.early_returns,
            metrics.comment_lines,
            metrics.comment_ratio,
            metrics.is_isolated,
            metrics.has_dependencies,
        ))
        
        self.conn.commit()
    
    def get_metrics(self, function_id: int) -> Optional[Dict]:
        """Retrieve metrics for a function."""
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM function_metrics WHERE function_id = ?', (function_id,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    def find_complex_functions(self, max_complexity: int = 10, max_loc: int = 100) -> List[Dict]:
        """Find functions exceeding complexity thresholds."""
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT fm.*, f.name
            FROM function_metrics fm
            JOIN functions f ON fm.function_id = f.id
            WHERE fm.complexity > ? OR fm.loc > ?
            ORDER BY fm.complexity DESC
        ''', (max_complexity, max_loc))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def find_isolated_functions(self) -> List[Dict]:
        """Find functions with no dependencies."""
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT fm.*, f.name
            FROM function_metrics fm
            JOIN functions f ON fm.function_id = f.id
            WHERE fm.is_isolated = 1
            ORDER BY f.name
        ''')
        
        return [dict(row) for row in cursor.fetchall()]
    
    def find_by_metrics(self, criteria: Dict) -> List[Dict]:
        """Find functions matching metric criteria."""
        if not self.conn:
            self.connect()
        
        # Build WHERE clause from criteria
        where_parts = []
        params = []
        
        if 'min_complexity' in criteria:
            where_parts.append('fm.complexity >= ?')
            params.append(criteria['min_complexity'])
        
        if 'max_complexity' in criteria:
            where_parts.append('fm.complexity <= ?')
            params.append(criteria['max_complexity'])
        
        if 'min_loc' in criteria:
            where_parts.append('fm.loc >= ?')
            params.append(criteria['min_loc'])
        
        if 'max_loc' in criteria:
            where_parts.append('fm.loc <= ?')
            params.append(criteria['max_loc'])
        
        if 'min_parameters' in criteria:
            where_parts.append('fm.parameters >= ?')
            params.append(criteria['min_parameters'])
        
        if 'max_parameters' in criteria:
            where_parts.append('fm.parameters <= ?')
            params.append(criteria['max_parameters'])
        
        where_clause = ' AND '.join(where_parts) if where_parts else '1=1'
        
        cursor = self.conn.cursor()
        query = f'''
            SELECT fm.*, f.name
            FROM function_metrics fm
            JOIN functions f ON fm.function_id = f.id
            WHERE {where_clause}
            ORDER BY fm.complexity DESC
        '''
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def store_naming_violation(self, function_id: int, convention_type: str, message: str, severity: str):
        """Store a naming convention violation."""
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO naming_violations
            (function_id, convention_type, violation_message, severity)
            VALUES (?, ?, ?, ?)
        ''', (function_id, convention_type, message, severity))
        
        self.conn.commit()
    
    def get_naming_violations(self, function_id: Optional[int] = None) -> List[Dict]:
        """Get naming violations."""
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        
        if function_id:
            cursor.execute('''
                SELECT nv.*, f.name
                FROM naming_violations nv
                JOIN functions f ON nv.function_id = f.id
                WHERE nv.function_id = ?
                ORDER BY nv.severity DESC
            ''', (function_id,))
        else:
            cursor.execute('''
                SELECT nv.*, f.name
                FROM naming_violations nv
                JOIN functions f ON nv.function_id = f.id
                ORDER BY nv.severity DESC
            ''')
        
        return [dict(row) for row in cursor.fetchall()]
    
    def store_duplication_candidate(self, function1_id: int, function2_id: int, similarity: float):
        """Store a code duplication candidate."""
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        
        # Ensure function1_id < function2_id to avoid duplicates
        if function1_id > function2_id:
            function1_id, function2_id = function2_id, function1_id
        
        cursor.execute('''
            INSERT OR REPLACE INTO duplication_candidates
            (function1_id, function2_id, similarity)
            VALUES (?, ?, ?)
        ''', (function1_id, function2_id, similarity))
        
        self.conn.commit()
    
    def get_duplication_candidates(self, min_similarity: float = 0.8) -> List[Dict]:
        """Get code duplication candidates."""
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT dc.*, f1.name as func1_name, f2.name as func2_name
            FROM duplication_candidates dc
            JOIN functions f1 ON dc.function1_id = f1.id
            JOIN functions f2 ON dc.function2_id = f2.id
            WHERE dc.similarity >= ?
            ORDER BY dc.similarity DESC
        ''', (min_similarity,))
        
        return [dict(row) for row in cursor.fetchall()]
