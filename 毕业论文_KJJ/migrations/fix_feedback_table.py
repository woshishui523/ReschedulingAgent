"""Attempt to fix feedback table schema (best-effort for sqlite).

Note: sqlite has limited ALTER TABLE support; this script demonstrates a
pattern for recreating a table if a schema change is required.
"""
import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent.parent / "data.db"


def run():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Example: ensure 'source' column exists; if not, recreate table.
    c.execute("PRAGMA table_info(feedback)")
    cols = [r[1] for r in c.fetchall()]
    if "source" not in cols:
        c.execute("ALTER TABLE feedback RENAME TO feedback_old")
        c.execute(
            """
            CREATE TABLE feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                source TEXT,
                payload TEXT
            )
            """
        )
        c.execute(
            "INSERT INTO feedback (timestamp, source, payload) SELECT timestamp, '' as source, payload FROM feedback_old"
        )
        c.execute("DROP TABLE feedback_old")
    conn.commit()
    conn.close()


if __name__ == "__main__":
    run()
