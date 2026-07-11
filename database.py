"""
Database Manager for VANGUARD AI Assistant.
Manages local SQLite database storage for conversations, logs, and state persistence.
"""
import os
import sqlite3
import logging
from typing import List, Dict, Any, Tuple, Optional

logger = logging.getLogger("vanguard.database")


class DatabaseManager:
    """Handles connection, creation, and operations on the VANGUARD local SQLite database."""

    def __init__(self, db_dir: str = "database", db_name: str = "memory.db"):
        self.db_dir = db_dir
        self.db_path = os.path.join(db_dir, db_name)
        self.conn: Optional[sqlite3.Connection] = None
        self.init_db()

    def init_db(self) -> None:
        """Initializes directories and SQLite tables."""
        try:
            os.makedirs(self.db_dir, exist_ok=True)
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            self._create_tables()
            logger.info(f"Database initialized successfully at {self.db_path}")
        except sqlite3.Error as e:
            logger.critical(f"Database initialization failed: {e}")
            raise

    def _create_tables(self) -> None:
        """Creates tables if they do not exist."""
        cursor = self.conn.cursor()
        
        # Conversation history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                role TEXT CHECK(role IN ('user', 'assistant', 'system')),
                message TEXT NOT NULL
            )
        """)
        
        # Command execution log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS commands_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                command_name TEXT NOT NULL,
                arguments TEXT,
                status TEXT CHECK(status IN ('success', 'failure', 'skipped')),
                execution_time_ms INTEGER
            )
        """)
        
        self.conn.commit()

    def add_message(self, role: str, message: str) -> bool:
        """Adds a message to the conversation history database."""
        if not self.conn:
            logger.error("Database connection unavailable.")
            return False
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO conversations (role, message) VALUES (?, ?)",
                (role, message)
            )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error adding message to database: {e}")
            return False

    def get_recent_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Retrieves recent conversation history."""
        if not self.conn:
            logger.error("Database connection unavailable.")
            return []
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT role, message, timestamp FROM conversations ORDER BY id DESC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()
            # Return in chronological order
            return [{"role": r["role"], "message": r["message"], "timestamp": r["timestamp"]} for r in reversed(rows)]
        except sqlite3.Error as e:
            logger.error(f"Error retrieving history: {e}")
            return []

    def log_command(self, name: str, args: str, status: str, duration_ms: int) -> bool:
        """Logs a command execution event."""
        if not self.conn:
            logger.error("Database connection unavailable.")
            return False
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO commands_log (command_name, arguments, status, execution_time_ms) VALUES (?, ?, ?, ?)",
                (name, args, status, duration_ms)
            )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error logging command: {e}")
            return False

    def clear_history(self) -> bool:
        """Clears all conversations stored in the database."""
        if not self.conn:
            return False
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM conversations")
            self.conn.commit()
            logger.info("Conversation history cleared from database.")
            return True
        except sqlite3.Error as e:
            logger.error(f"Error clearing conversation history: {e}")
            return False

    def close(self) -> None:
        """Closes the connection to database."""
        if self.conn:
            self.conn.close()
            self.conn = None
            logger.info("Database connection closed.")
