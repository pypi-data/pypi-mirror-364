#!/usr/bin/env python3
"""
TuskFlask Database Management Module
Provides database connectivity and management for elephant services
"""

import sqlite3
import threading
import time
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import logging


class TuskDb:
    """Simple database wrapper for elephant services"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or "tusk_flask.db"
        self._lock = threading.RLock()
        self._connection = None
        self._init_database()
    
    def _init_database(self):
        """Initialize database and create tables if needed"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Create basic tables for elephant services
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS elephant_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        service_name TEXT NOT NULL,
                        metric_name TEXT NOT NULL,
                        metric_value REAL,
                        timestamp INTEGER DEFAULT (strftime('%s', 'now')),
                        metadata TEXT
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS elephant_config (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        service_name TEXT NOT NULL,
                        config_key TEXT NOT NULL,
                        config_value TEXT,
                        updated_at INTEGER DEFAULT (strftime('%s', 'now')),
                        UNIQUE(service_name, config_key)
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS elephant_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        service_name TEXT NOT NULL,
                        log_level TEXT NOT NULL,
                        message TEXT NOT NULL,
                        timestamp INTEGER DEFAULT (strftime('%s', 'now')),
                        metadata TEXT
                    )
                """)
                
                conn.commit()
                
        except Exception as e:
            logging.error(f"Failed to initialize database: {e}")
    
    def _get_connection(self):
        """Get database connection"""
        if self._connection is None:
            self._connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self._connection.row_factory = sqlite3.Row
        return self._connection
    
    def execute(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Execute a query and return results"""
        with self._lock:
            try:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    if params:
                        cursor.execute(query, params)
                    else:
                        cursor.execute(query)
                    
                    if query.strip().upper().startswith('SELECT'):
                        return [dict(row) for row in cursor.fetchall()]
                    else:
                        conn.commit()
                        return [{'affected_rows': cursor.rowcount}]
                        
            except Exception as e:
                logging.error(f"Database query failed: {e}")
                return []
    
    def insert(self, table: str, data: Dict[str, Any]) -> int:
        """Insert data into table"""
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        result = self.execute(query, tuple(data.values()))
        return result[0].get('affected_rows', 0) if result else 0
    
    def update(self, table: str, data: Dict[str, Any], where: Dict[str, Any]) -> int:
        """Update data in table"""
        set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
        where_clause = ' AND '.join([f"{k} = ?" for k in where.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
        
        params = tuple(data.values()) + tuple(where.values())
        result = self.execute(query, params)
        return result[0].get('affected_rows', 0) if result else 0
    
    def delete(self, table: str, where: Dict[str, Any]) -> int:
        """Delete data from table"""
        where_clause = ' AND '.join([f"{k} = ?" for k in where.keys()])
        query = f"DELETE FROM {table} WHERE {where_clause}"
        
        result = self.execute(query, tuple(where.values()))
        return result[0].get('affected_rows', 0) if result else 0
    
    def select(self, table: str, columns: List[str] = None, where: Dict[str, Any] = None, 
               order_by: str = None, limit: int = None) -> List[Dict[str, Any]]:
        """Select data from table"""
        cols = '*' if not columns else ', '.join(columns)
        query = f"SELECT {cols} FROM {table}"
        
        params = None
        if where:
            where_clause = ' AND '.join([f"{k} = ?" for k in where.keys()])
            query += f" WHERE {where_clause}"
            params = tuple(where.values())
        
        if order_by:
            query += f" ORDER BY {order_by}"
        
        if limit:
            query += f" LIMIT {limit}"
        
        return self.execute(query, params)
    
    def table_exists(self, table: str) -> bool:
        """Check if table exists"""
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        result = self.execute(query, (table,))
        return len(result) > 0
    
    def get_table_info(self, table: str) -> List[Dict[str, Any]]:
        """Get table schema information"""
        query = f"PRAGMA table_info({table})"
        return self.execute(query)
    
    def backup(self, backup_path: str) -> bool:
        """Create database backup"""
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            return True
        except Exception as e:
            logging.error(f"Database backup failed: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        with self._lock:
            if self._connection:
                self._connection.close()
                self._connection = None


# Global database instance
_db_instance = None


def get_database(db_path: str = None) -> TuskDb:
    """Get global database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = TuskDb(db_path)
    return _db_instance


def init_database(db_path: str = None) -> TuskDb:
    """Initialize global database instance"""
    global _db_instance
    _db_instance = TuskDb(db_path)
    return _db_instance


def close_database():
    """Close global database connection"""
    global _db_instance
    if _db_instance:
        _db_instance.close()
        _db_instance = None 