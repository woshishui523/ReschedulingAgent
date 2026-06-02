"""Create feedback and dispatch tables (sqlite3).

This script is a basic migration helper that creates two tables used by the
system: `feedback` and `dispatch_records`.
"""
import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent.parent / "data.db"


def run():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            source TEXT,
            payload TEXT
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS dispatch_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT,
            plan TEXT,
            metadata TEXT
        )
        """
    )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    run()
