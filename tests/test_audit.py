"""Tests for core.audit."""
from __future__ import annotations

from core.audit import recent_runs


def test_recent_runs_returns_both_runs_newest_first(conn) -> None:
    conn.execute(
        "INSERT INTO runs "
        "(workflow_id, run_by, inputs_json, output, model) "
        "VALUES (1, 'alice', '{}', 'first', 'claude-sonnet-4-5')"
    )
    conn.execute(
        "INSERT INTO runs "
        "(workflow_id, run_by, inputs_json, output, model) "
        "VALUES (1, 'alice', '{}', 'second', 'claude-sonnet-4-5')"
    )
    conn.commit()

    rows = recent_runs(conn)

    assert len(rows) == 2
    assert rows[0]["output"] == "second"
    assert rows[1]["output"] == "first"
