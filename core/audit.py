"""Read-only audit queries for run history."""
from __future__ import annotations

import sqlite3


def recent_runs(conn: sqlite3.Connection, limit: int = 20) -> list[dict]:
    """Return the most recent runs, newest first."""
    rows = conn.execute(
        "SELECT * FROM runs ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    return [dict(r) for r in rows]


def runs_by_workflow(
    conn: sqlite3.Connection, workflow_id: int
) -> list[dict]:
    """Return every run for a single workflow, newest first."""
    rows = conn.execute(
        "SELECT * FROM runs WHERE workflow_id = ? ORDER BY id DESC",
        (workflow_id,),
    ).fetchall()
    return [dict(r) for r in rows]
