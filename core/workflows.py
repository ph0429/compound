"""Workflow CRUD, validation, and status transitions.

The transition() helper is the only path that writes to workflows.status.
Approved transitions: draft to under_review, under_review to published,
under_review to rejected. Anything else raises IllegalTransition.

There is no re-review path. A rejected workflow is resubmitted as a new
row.
"""
from __future__ import annotations

import json
import re
import sqlite3
from datetime import datetime, timezone
from typing import Any

REQUIRED_FIELDS: tuple[str, ...] = (
    "title",
    "prompt",
    "owner",
    "success_criterion",
    "inputs_json",
)

PROMPT_MIN_CHARS = 50
PROMPT_MAX_CHARS = 4000

_SECRET_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"sk-ant-"),
    re.compile(r"sk-[A-Za-z0-9]"),
    re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"),
)


class IllegalTransition(Exception):
    """Raised when a status transition is not allowed from the current state."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def validate(workflow: dict) -> tuple[bool, list[str]]:
    """Run deterministic checks on a proposed workflow.

    Returns (ok, errors). Errors are short English strings. Field names
    appear verbatim in the error so the caller can surface them.
    """
    errors: list[str] = []
    for field in REQUIRED_FIELDS:
        value = workflow.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            errors.append(f"Missing required field: {field}")

    prompt = workflow.get("prompt", "")
    if isinstance(prompt, str) and prompt.strip():
        if len(prompt) < PROMPT_MIN_CHARS:
            errors.append(
                f"Prompt must be at least {PROMPT_MIN_CHARS} characters"
            )
        if len(prompt) > PROMPT_MAX_CHARS:
            errors.append(
                f"Prompt must be no more than {PROMPT_MAX_CHARS} characters"
            )
        for pat in _SECRET_PATTERNS:
            if pat.search(prompt):
                errors.append("Prompt looks like it contains a secret or email")
                break

    return (len(errors) == 0, errors)


def submit(conn: sqlite3.Connection, workflow: dict) -> int:
    """Insert a new workflow as draft. Returns the new row id."""
    cur = conn.execute(
        "INSERT INTO workflows "
        "(title, prompt, inputs_json, owner, success_criterion, tags, status) "
        "VALUES (?, ?, ?, ?, ?, ?, 'draft')",
        (
            workflow["title"],
            workflow["prompt"],
            workflow["inputs_json"],
            workflow["owner"],
            workflow["success_criterion"],
            workflow.get("tags"),
        ),
    )
    conn.commit()
    return int(cur.lastrowid)


def request_review(conn: sqlite3.Connection, workflow_id: int) -> None:
    """Move a workflow from draft to under_review."""
    _transition(conn, workflow_id, "draft", "under_review")


def attach_review(
    conn: sqlite3.Connection, workflow_id: int, review: dict
) -> None:
    """Insert a review row. Does not change workflow status."""
    conn.execute(
        "INSERT INTO reviews "
        "(workflow_id, score, summary, suggestions_json, recommendation, "
        " raw_response, parse_ok) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            workflow_id,
            review.get("score"),
            review.get("summary"),
            json.dumps(review.get("suggestions", [])),
            review.get("recommendation"),
            review.get("raw_response"),
            1 if review.get("parse_ok", True) else 0,
        ),
    )
    conn.commit()


def approve(
    conn: sqlite3.Connection, workflow_id: int, reviewer: str
) -> None:
    """Move a workflow from under_review to published. Sets published_at."""
    _ = reviewer
    _transition(
        conn,
        workflow_id,
        "under_review",
        "published",
        fields={"published_at": _now()},
    )


def reject(
    conn: sqlite3.Connection, workflow_id: int, reason: str = ""
) -> None:
    """Move a workflow from under_review to rejected.

    The reason is accepted for API symmetry but has no dedicated column in
    v1. The model's review row carries the rationale that informed the
    decision.
    """
    _ = reason
    _transition(conn, workflow_id, "under_review", "rejected")


def list_published(conn: sqlite3.Connection) -> list[dict]:
    """Return every published workflow, newest publication first."""
    rows = conn.execute(
        "SELECT * FROM workflows WHERE status = 'published' "
        "ORDER BY published_at DESC, id DESC"
    ).fetchall()
    return [dict(r) for r in rows]


def list_drafts(conn: sqlite3.Connection) -> list[dict]:
    """Return drafts and submissions awaiting review, newest first."""
    rows = conn.execute(
        "SELECT * FROM workflows "
        "WHERE status IN ('draft', 'under_review') "
        "ORDER BY created_at DESC, id DESC"
    ).fetchall()
    return [dict(r) for r in rows]


def get(conn: sqlite3.Connection, workflow_id: int) -> dict | None:
    """Look up a workflow by id."""
    row = conn.execute(
        "SELECT * FROM workflows WHERE id = ?", (workflow_id,)
    ).fetchone()
    return dict(row) if row else None


def latest_review(
    conn: sqlite3.Connection, workflow_id: int
) -> dict | None:
    """Return the most recent review row for a workflow, or None."""
    row = conn.execute(
        "SELECT * FROM reviews WHERE workflow_id = ? "
        "ORDER BY id DESC LIMIT 1",
        (workflow_id,),
    ).fetchone()
    return dict(row) if row else None


def _transition(
    conn: sqlite3.Connection,
    workflow_id: int,
    expected_from: str,
    to_status: str,
    fields: dict[str, Any] | None = None,
) -> None:
    row = conn.execute(
        "SELECT status FROM workflows WHERE id = ?", (workflow_id,)
    ).fetchone()
    if row is None:
        raise IllegalTransition(f"Workflow {workflow_id} not found")
    current = row["status"]
    if current != expected_from:
        raise IllegalTransition(
            f"Cannot move workflow {workflow_id} from {current} to "
            f"{to_status}; expected current status {expected_from}"
        )

    set_parts: list[str] = ["status = ?"]
    params: list[Any] = [to_status]
    if fields:
        for key, value in fields.items():
            set_parts.append(f"{key} = ?")
            params.append(value)
    params.append(workflow_id)
    conn.execute(
        f"UPDATE workflows SET {', '.join(set_parts)} WHERE id = ?",
        params,
    )
    conn.commit()
