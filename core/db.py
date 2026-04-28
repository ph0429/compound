"""SQLite lifecycle. Owns connection setup and one-time schema init.

This module is purely about opening a connection and creating the schema
on first run. It contains no business logic and does not import Streamlit.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

_DB_DIR = Path(__file__).resolve().parent.parent / "db"
SCHEMA_PATH = _DB_DIR / "schema.sql"
SEED_PATH = _DB_DIR / "seed.sql"


def get_connection(path: str) -> sqlite3.Connection:
    """Open a SQLite connection with foreign keys on and Row factory set."""
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(path: str) -> None:
    """Create schema and load seed data if the database is uninitialised.

    Idempotent: if the workflows table already exists, this returns
    without touching the database. Callers wanting a fresh state should
    delete the file first (see scripts/reset_db.py).
    """
    db_path = Path(path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = get_connection(path)
    try:
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='workflows'"
        )
        if cursor.fetchone() is not None:
            return
        conn.executescript(SCHEMA_PATH.read_text())
        conn.executescript(SEED_PATH.read_text())
        conn.commit()
    finally:
        conn.close()
