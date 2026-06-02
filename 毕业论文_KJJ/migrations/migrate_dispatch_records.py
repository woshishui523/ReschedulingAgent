"""Migration helper to add columns to dispatch_records or normalize data."""
import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent.parent / "data.db"


def run():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Example: ensure metadata column exists
    c.execute("PRAGMA table_info(dispatch_records)")
    cols = [r[1] for r in c.fetchall()]
    if "metadata" not in cols:
        c.execute("ALTER TABLE dispatch_records RENAME TO dispatch_old")
        c.execute(
            """
            CREATE TABLE dispatch_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT,
                plan TEXT,
                metadata TEXT
            )
            """
        )
        c.execute(
            "INSERT INTO dispatch_records (created_at, plan, metadata) SELECT created_at, plan, '' FROM dispatch_old"
        )
        c.execute("DROP TABLE dispatch_old")
    conn.commit()
    conn.close()


if __name__ == "__main__":
    run()
