"""Tests for core.runs."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from core.runs import WorkflowNotRunnable, run_workflow


def _make_response(
    text: str, input_tokens: int = 100, output_tokens: int = 200
) -> MagicMock:
    response = MagicMock()
    response.content = [MagicMock(text=text)]
    response.usage.input_tokens = input_tokens
    response.usage.output_tokens = output_tokens
    return response


_PROPOSAL_INPUTS = {
    "client_name": "Acme Ltd",
    "project_type": "Energy appraisal",
    "key_needs": "Speed and clarity.",
}


def test_run_published_workflow_records_full_row(
    conn, mock_anthropic_client: MagicMock
) -> None:
    mock_anthropic_client.messages.create.return_value = _make_response(
        "Outline for Acme Ltd."
    )

    output = run_workflow(
        conn,
        workflow_id=1,
        run_by="alice",
        inputs=_PROPOSAL_INPUTS,
        client=mock_anthropic_client,
    )

    assert output == "Outline for Acme Ltd."
    row = conn.execute(
        "SELECT * FROM runs WHERE workflow_id = 1"
    ).fetchone()
    assert row is not None
    assert row["run_by"] == "alice"
    assert row["output"] == "Outline for Acme Ltd."
    assert row["model"] == "claude-sonnet-4-5"
    assert row["input_tokens"] == 100
    assert row["output_tokens"] == 200
    assert row["cost_estimate_eur"] is not None
    assert row["cost_estimate_eur"] > 0


def test_run_unpublished_workflow_raises_and_inserts_no_row(
    conn, mock_anthropic_client: MagicMock
) -> None:
    conn.execute("UPDATE workflows SET status = 'draft' WHERE id = 1")
    conn.commit()

    with pytest.raises(WorkflowNotRunnable):
        run_workflow(
            conn,
            workflow_id=1,
            run_by="alice",
            inputs=_PROPOSAL_INPUTS,
            client=mock_anthropic_client,
        )

    count = conn.execute(
        "SELECT COUNT(*) AS n FROM runs WHERE workflow_id = 1"
    ).fetchone()["n"]
    assert count == 0
    mock_anthropic_client.messages.create.assert_not_called()
