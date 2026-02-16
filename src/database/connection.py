"""
Database connection manager for AIOps Studio - Inventory.

This module provides a centralized database connection manager with:
- WAL mode for better concurrency
- Foreign key constraints enabled
- Connection pooling
- Transaction context managers
- Automatic backup functionality
"""

import sqlite3
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional
from contextlib import contextmanager

from utils.app_paths import get_backups_dir


class DatabaseManager:
    """Manages SQLite database connections and operations."""
    
    def __init__(self, db_path: str = "inventory.db"):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self._connection: Optional[sqlite3.Connection] = None
        
    def get_connection(self) -> sqlite3.Connection:
        """
        Get or create a database connection.
        
        Returns:
            sqlite3.Connection: Active database connection
        """
        if self._connection is None:
            self._connection = sqlite3.connect(self.db_path)
            self._connection.row_factory = sqlite3.Row  # Enable column access by name
            
            # Enable foreign key constraints (disabled by default in SQLite)
            self._connection.execute("PRAGMA foreign_keys = ON")
            
            # Enable WAL mode for better concurrency
            self._connection.execute("PRAGMA journal_mode = WAL")
            
        return self._connection
    
    def close(self):
        """Close the database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
    
    @contextmanager
    def transaction(self):
        """
        Context manager for database transactions.
        
        Usage:
            with db_manager.transaction() as conn:
                conn.execute("INSERT INTO ...")
                conn.execute("UPDATE ...")
            # Automatically commits on success, rolls back on exception
        """
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
    
    def execute_script(self, script_path: str):
        """
        Execute a SQL script file.
        
        Args:
            script_path: Path to the SQL script file
        """
        with open(script_path, 'r') as f:
            script = f.read()
        
        conn = self.get_connection()
        conn.executescript(script)
        conn.commit()
    
    def backup(self, backup_dir: Optional[Path] = None) -> str:
        """
        Create a backup of the database.
        
        Args:
            backup_dir: Directory to store backups (defaults to AppData/backups)
            
        Returns:
            str: Path to the backup file
        """
        # Use AppData backups directory by default
        if backup_dir is None:
            backup_dir = get_backups_dir()
        
        # Create backup directory if it doesn't exist
        Path(backup_dir).mkdir(parents=True, exist_ok=True)
        
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"inventory_backup_{timestamp}.db")
        
        # Copy database file
        shutil.copy2(self.db_path, backup_path)
        
        return backup_path
    
    def restore(self, backup_path: str):
        """
        Restore database from a backup.
        
        Args:
            backup_path: Path to the backup file
        """
        # Close current connection
        self.close()
        
        # Restore from backup
        shutil.copy2(backup_path, self.db_path)
        
        # Reconnect
        self.get_connection()
    
    def vacuum(self):
        """
        Optimize database by reclaiming unused space.
        Should be run periodically for maintenance.
        """
        conn = self.get_connection()
        conn.execute("VACUUM")
        conn.commit()
    
    def get_database_info(self) -> dict:
        """
        Get information about the database.
        
        Returns:
            dict: Database statistics and information
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get database size
        db_size = os.path.getsize(self.db_path)
        
        # Get table counts
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        table_counts = {}
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            table_counts[table] = cursor.fetchone()[0]
        
        return {
            "database_path": self.db_path,
            "size_bytes": db_size,
            "size_mb": round(db_size / (1024 * 1024), 2),
            "tables": tables,
            "table_counts": table_counts
        }


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


def get_db_manager(db_path: str = "inventory.db") -> DatabaseManager:
    """
    Get the global database manager instance.
    
    Args:
        db_path: Path to the database file
        
    Returns:
        DatabaseManager: Global database manager instance
    """
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager(db_path)
    return _db_manager


def init_database(db_path: str = "inventory.db", schema_path: str = None):
    """
    Initialize the database with schema.
    
    Args:
        db_path: Path to the database file
        schema_path: Path to the schema SQL file
    """
    if schema_path is None:
        # Default to schema.sql in the same directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        schema_path = os.path.join(current_dir, "schema.sql")
    
    db_manager = DatabaseManager(db_path)
    db_manager.execute_script(schema_path)
    
    return db_manager
