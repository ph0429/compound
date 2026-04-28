"""Tests for core.db: schema creation, seed loading, append-only triggers."""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from core.db import get_connection, init_db


@pytest.fixture
def db_path(tmp_path: Path) -> str:
    path = tmp_path / "compound.db"
    init_db(str(path))
    return str(path)


def test_init_db_creates_expected_tables(db_path: str) -> None:
    conn = get_connection(db_path)
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    names = {row["name"] for row in rows}
    assert {"workflows", "reviews", "runs"}.issubset(names)


def test_init_db_loads_two_published_seed_workflows(db_path: str) -> None:
    conn = get_connection(db_path)
    rows = conn.execute(
        "SELECT title, owner, status FROM workflows ORDER BY id"
    ).fetchall()
    assert len(rows) == 2
    assert rows[0]["title"] == "Proposal Outline"
    assert rows[0]["owner"] == "Brad the BI consultant"
    assert rows[0]["status"] == "published"
    assert rows[1]["title"] == "Meeting Recap"
    assert rows[1]["owner"] == "Maya the project manager"
    assert rows[1]["status"] == "published"


def test_init_db_is_idempotent(tmp_path: Path) -> None:
    path = str(tmp_path / "compound.db")
    init_db(path)
    init_db(path)
    conn = get_connection(path)
    count = conn.execute("SELECT COUNT(*) AS n FROM workflows").fetchone()["n"]
    assert count == 2


def test_runs_rejects_update(db_path: str) -> None:
    conn = get_connection(db_path)
    conn.execute(
        "INSERT INTO runs (workflow_id, run_by, inputs_json, output, model) "
        "VALUES (1, 'tester', '{}', 'hello', 'claude-sonnet-4-5')"
    )
    conn.commit()
    with pytest.raises(sqlite3.IntegrityError, match="append-only"):
        conn.execute("UPDATE runs SET output = 'changed' WHERE id = 1")


def test_runs_rejects_delete(db_path: str) -> None:
    conn = get_connection(db_path)
    conn.execute(
        "INSERT INTO runs (workflow_id, run_by, inputs_json, output, model) "
        "VALUES (1, 'tester', '{}', 'hello', 'claude-sonnet-4-5')"
    )
    conn.commit()
    with pytest.raises(sqlite3.IntegrityError, match="append-only"):
        conn.execute("DELETE FROM runs WHERE id = 1")


def test_foreign_keys_are_enforced(db_path: str) -> None:
    conn = get_connection(db_path)
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO runs (workflow_id, run_by, inputs_json, output, model) "
            "VALUES (9999, 'tester', '{}', 'orphan', 'claude-sonnet-4-5')"
        )
        conn.commit()
