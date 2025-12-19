#!/usr/bin/env python3
"""
Add token_usage table to the database.
"""

import sqlite3
from pathlib import Path

# Path to the database
DB_PATH = Path(__file__).parent / "ai_agent.db"

# SQL to create the token_usage table
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS token_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL,
    model VARCHAR(100) NOT NULL,
    prompt_tokens INTEGER NOT NULL DEFAULT 0,
    completion_tokens INTEGER NOT NULL DEFAULT 0,
    total_tokens INTEGER NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations (id) ON DELETE CASCADE
);
"""

def add_token_usage_table():
    """Add the token_usage table to the database."""
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute(CREATE_TABLE_SQL)
        conn.commit()
        print("Token usage table created successfully!")
    except Exception as e:
        print(f"Error creating token usage table: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    add_token_usage_table()