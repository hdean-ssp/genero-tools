#!/usr/bin/env python3
"""Code quality analysis queries."""

import re
import sqlite3
from typing import List, Dict, Optional


class QualityAnalyzer:
    """Analyze code quality using metrics."""
    
    def __init__(self, db_file: str):
        """Initialize analyzer with database file."""
        self.db_file = db_file
        self.conn = None
        try:
            self.connect()
        except Exception:
            # Database may not exist yet
            pass
    
    def connect(self):
        """Connect to database."""
        self.conn = sqlite3.connect(self.db_file)
        self.conn.row_factory = sqlite3.Row
    
    def disconnect(self):
        """Disconnect from database."""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def __del__(self):
        """Cleanup database connection."""
        self.disconnect()
    
    def find_complex_functions(
        self, max_complexity: int = 10, max_loc: int = 100, max_parameters: int = 5
    ) -> List[Dict]:
        """Find functions exceeding complexity thresholds."""
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        
        try:
            # Check if function_metrics table exists
            cursor.execute('''
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='function_metrics'
            ''')
            
            if cursor.fetchone():
                # Use function_metrics table if it exists
                cursor.execute('''
                    SELECT fm.*, f.name, fi.path as file_path
                    FROM function_metrics fm
                    JOIN functions f ON fm.function_id = f.id
                    JOIN files fi ON f.file_id = fi.id
                    WHERE fm.complexity > ? OR fm.loc > ? OR fm.parameters > ?
                    ORDER BY fm.complexity DESC, fm.loc DESC
                ''', (max_complexity, max_loc, max_parameters))
                
                results = []
                for row in cursor.fetchall():
                    results.append({
                        'name': row['name'],
                        'file_path': row['file_path'],
                        'complexity': row['complexity'],
                        'loc': row['loc'],
                        'parameters': row['parameters'],
                        'local_variables': row['local_variables'],
                        'early_returns': row['early_returns'],
                        'comment_ratio': row['comment_ratio'],
                    })
                return results
            else:
                # Fallback: query functions table directly
                cursor.execute('''
                    SELECT f.id, f.name, fi.path as file_path, 
                           COUNT(DISTINCT p.id) as parameters
                    FROM functions f
                    JOIN files fi ON f.file_id = fi.id
                    LEFT JOIN parameters p ON f.id = p.function_id
                    GROUP BY f.id
                    HAVING parameters > ?
                    ORDER BY f.name
                ''', (max_parameters,))
                
                results = []
                for row in cursor.fetchall():
                    results.append({
                        'name': row['name'],
                        'file_path': row['file_path'],
                        'complexity': 1,
                        'loc': 0,
                        'parameters': row['parameters'],
                        'local_variables': 0,
                        'early_returns': 0,
                        'comment_ratio': 0.0,
                    })
                return results
        except Exception as e:
            print(f"Error querying complex functions: {e}")
            return []
    
    def find_similar_functions(self, min_similarity: float = 0.8) -> List[Dict]:
        """Find similar functions (code duplication candidates)."""
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        
        try:
            # Get all functions with their metrics
            cursor.execute('''
                SELECT f.id, f.name, fi.path as file_path
                FROM functions f
                JOIN files fi ON f.file_id = fi.id
            ''')
            
            functions = {}
            for row in cursor.fetchall():
                func_id = row['id']
                
                # Get parameter count
                cursor.execute('SELECT COUNT(*) as count FROM parameters WHERE function_id = ?', (func_id,))
                param_count = cursor.fetchone()['count']
                
                # Get return count
                cursor.execute('SELECT COUNT(*) as count FROM returns WHERE function_id = ?', (func_id,))
                return_count = cursor.fetchone()['count']
                
                functions[func_id] = {
                    'id': func_id,
                    'name': row['name'],
                    'file_path': row['file_path'],
                    'parameters': param_count,
                    'returns': return_count,
                    'loc': 0,
                    'complexity': 1,
                }
            
            # Calculate similarity between all pairs
            candidates = []
            func_ids = list(functions.keys())
            
            for i in range(len(func_ids)):
                for j in range(i + 1, len(func_ids)):
                    func1_id = func_ids[i]
                    func2_id = func_ids[j]
                    func1 = functions[func1_id]
                    func2 = functions[func2_id]
                    
                    # Calculate similarity based on signature
                    similarity = self._calculate_similarity(func1, func2)
                    
                    if similarity >= min_similarity:
                        candidates.append({
                            'function1': {
                                'name': func1['name'],
                                'file_path': func1['file_path'],
                                'parameters': func1['parameters'],
                            },
                            'function2': {
                                'name': func2['name'],
                                'file_path': func2['file_path'],
                                'parameters': func2['parameters'],
                            },
                            'similarity': round(similarity, 2),
                        })
            
            # Sort by similarity descending
            candidates.sort(key=lambda x: x['similarity'], reverse=True)
            
            return candidates
        except Exception as e:
            print(f"Error finding similar functions: {e}")
            return []
    
    def find_isolated_functions(self) -> List[Dict]:
        """Find functions with no dependencies."""
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        
        try:
            # Find functions that are not called by any other function
            cursor.execute('''
                SELECT DISTINCT f.id, f.name, fi.path as file_path
                FROM functions f
                JOIN files fi ON f.file_id = fi.id
                WHERE f.id NOT IN (
                    SELECT DISTINCT function_id FROM function_calls
                )
                ORDER BY f.name
            ''')
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'name': row['name'],
                    'file_path': row['file_path'],
                    'calls_made': [],
                    'called_by': [],
                })
            
            return results
        except Exception as e:
            print(f"Error finding isolated functions: {e}")
            return []
    
    def find_by_metrics(self, criteria: Dict) -> List[Dict]:
        """Find functions matching metric criteria."""
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        
        try:
            # Build WHERE clause from criteria
            where_parts = []
            params = []
            
            # Handle different criteria formats
            for key, value in criteria.items():
                if isinstance(value, dict):
                    # Format: {"complexity": {"gt": 5, "lte": 10}}
                    for op, val in value.items():
                        if op == 'gt':
                            where_parts.append(f'fm.{key} > ?')
                            params.append(val)
                        elif op == 'gte':
                            where_parts.append(f'fm.{key} >= ?')
                            params.append(val)
                        elif op == 'lt':
                            where_parts.append(f'fm.{key} < ?')
                            params.append(val)
                        elif op == 'lte':
                            where_parts.append(f'fm.{key} <= ?')
                            params.append(val)
                        elif op == 'eq':
                            where_parts.append(f'fm.{key} = ?')
                            params.append(val)
                else:
                    # Simple equality
                    where_parts.append(f'fm.{key} = ?')
                    params.append(value)
            
            where_clause = ' AND '.join(where_parts) if where_parts else '1=1'
            
            # Check if function_metrics table exists
            cursor.execute('''
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='function_metrics'
            ''')
            
            if cursor.fetchone():
                # Use function_metrics table
                query = f'''
                    SELECT fm.*, f.name, fi.path as file_path
                    FROM function_metrics fm
                    JOIN functions f ON fm.function_id = f.id
                    JOIN files fi ON f.file_id = fi.id
                    WHERE {where_clause}
                    ORDER BY fm.complexity DESC
                '''
            else:
                # Fallback to functions table
                query = f'''
                    SELECT f.id, f.name, fi.path as file_path
                    FROM functions f
                    JOIN files fi ON f.file_id = fi.id
                    WHERE 1=1
                    ORDER BY f.name
                '''
                params = []
            
            cursor.execute(query, params)
            
            results = []
            for row in cursor.fetchall():
                # Convert sqlite3.Row to dict for safe access
                row_dict = dict(row)
                results.append({
                    'name': row_dict['name'],
                    'file_path': row_dict['file_path'],
                    'loc': row_dict.get('loc', 0),
                    'complexity': row_dict.get('complexity', 1),
                    'parameters': row_dict.get('parameters', 0),
                    'local_variables': row_dict.get('local_variables', 0),
                    'call_depth': row_dict.get('call_depth', 0),
                    'comment_ratio': row_dict.get('comment_ratio', 0.0),
                })
            
            return results
        except Exception as e:
            print(f"Error querying by metrics: {e}")
            return []
    
    def check_naming_conventions(self, conventions: Dict) -> List[Dict]:
        """Check functions against naming conventions."""
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        
        try:
            cursor.execute('SELECT id, name FROM functions')
            functions = cursor.fetchall()
            
            violations = []
            
            for func in functions:
                func_id = func['id']
                func_name = func['name']
                
                # Check each convention
                for convention_type, convention_config in conventions.items():
                    pattern = convention_config.get('pattern', '')
                    description = convention_config.get('description', '')
                    severity = convention_config.get('severity', 'warning')
                    
                    if not pattern:
                        continue
                    
                    # Check if function name matches pattern
                    try:
                        if not re.match(pattern, func_name):
                            violations.append({
                                'function_name': func_name,
                                'convention_type': convention_type,
                                'message': f"Function name '{func_name}' does not match convention: {description}",
                                'severity': severity,
                            })
                    except re.error:
                        # Invalid regex pattern
                        pass
            
            return violations
        except Exception as e:
            print(f"Error checking naming conventions: {e}")
            return []
    
    def _calculate_similarity(self, func1: Dict, func2: Dict) -> float:
        """Calculate similarity between two functions."""
        # Similarity based on signature characteristics
        # Functions with similar LOC, complexity, and parameters are considered similar
        
        loc_diff = abs(func1.get('loc', 0) - func2.get('loc', 0))
        complexity_diff = abs(func1.get('complexity', 1) - func2.get('complexity', 1))
        params_diff = abs(func1.get('parameters', 0) - func2.get('parameters', 0))
        returns_diff = abs(func1.get('returns', 0) - func2.get('returns', 0))
        
        # Normalize differences (0-1 scale)
        # Smaller differences = higher similarity
        max_loc = max(func1.get('loc', 0), func2.get('loc', 0), 1)
        loc_similarity = 1.0 - (loc_diff / max_loc)
        
        max_complexity = max(func1.get('complexity', 1), func2.get('complexity', 1), 1)
        complexity_similarity = 1.0 - (complexity_diff / max_complexity)
        
        params_similarity = 1.0 - (params_diff / 10.0)  # Assume max 10 params
        params_similarity = max(0, min(1, params_similarity))
        
        returns_similarity = 1.0 - (returns_diff / 5.0)  # Assume max 5 returns
        returns_similarity = max(0, min(1, returns_similarity))
        
        # Weighted average
        similarity = (
            loc_similarity * 0.4 +
            complexity_similarity * 0.3 +
            params_similarity * 0.2 +
            returns_similarity * 0.1
        )
        
        return similarity
