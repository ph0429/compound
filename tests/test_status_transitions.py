"""Tests for workflow status transitions, including idempotency."""
from __future__ import annotations

import pytest

from core.workflows import (
    IllegalTransition,
    approve,
    request_review,
    submit,
)


def _draft_workflow() -> dict:
    return {
        "title": "Trial",
        "prompt": "Summarise the text {body} in two sentences. "
                  "Use plain English. Keep it brief.",
        "inputs_json": '[{"key": "body", "label": "Body"}]',
        "owner": "Tester",
        "success_criterion": "Output is two sentences and uses plain English.",
        "tags": "test",
    }


def test_approve_transitions_under_review_to_published(conn) -> None:
    workflow_id = submit(conn, _draft_workflow())
    request_review(conn, workflow_id)
    approve(conn, workflow_id, "alice")
    row = conn.execute(
        "SELECT status, published_at FROM workflows WHERE id = ?",
        (workflow_id,),
    ).fetchone()
    assert row["status"] == "published"
    assert row["published_at"] is not None


def test_approve_called_twice_raises_and_status_remains_published(conn) -> None:
    workflow_id = submit(conn, _draft_workflow())
    request_review(conn, workflow_id)
    approve(conn, workflow_id, "alice")
    with pytest.raises(IllegalTransition):
        approve(conn, workflow_id, "alice")
    row = conn.execute(
        "SELECT status FROM workflows WHERE id = ?", (workflow_id,)
    ).fetchone()
    assert row["status"] == "published"


def test_approve_on_draft_raises_and_status_remains_draft(conn) -> None:
    workflow_id = submit(conn, _draft_workflow())
    with pytest.raises(IllegalTransition):
        approve(conn, workflow_id, "alice")
    row = conn.execute(
        "SELECT status FROM workflows WHERE id = ?", (workflow_id,)
    ).fetchone()
    assert row["status"] == "draft"
