"""Tests for core.runs."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from core.runs import WorkflowNotRunnable, run_workflow


def _make_response(
    text: str, prompt_tokens: int = 100, completion_tokens: int = 200
) -> MagicMock:
    response = MagicMock()
    response.choices = [MagicMock()]
    response.choices[0].message.content = text
    response.usage.prompt_tokens = prompt_tokens
    response.usage.completion_tokens = completion_tokens
    return response


_PROPOSAL_INPUTS = {
    "client_name": "Acme Ltd",
    "project_type": "Energy appraisal",
    "key_needs": "Speed and clarity.",
}


def test_run_published_workflow_records_full_row(
    conn, mock_llm_client: MagicMock
) -> None:
    mock_llm_client.chat.completions.create.return_value = _make_response(
        "Outline for Acme Ltd."
    )

    output = run_workflow(
        conn,
        workflow_id=1,
        run_by="alice",
        inputs=_PROPOSAL_INPUTS,
        client=mock_llm_client,
    )

    assert output == "Outline for Acme Ltd."
    row = conn.execute(
        "SELECT * FROM runs WHERE workflow_id = 1"
    ).fetchone()
    assert row is not None
    assert row["run_by"] == "alice"
    assert row["output"] == "Outline for Acme Ltd."
    assert row["model"] == "gpt-4o-mini"
    assert row["input_tokens"] == 100
    assert row["output_tokens"] == 200
    assert row["cost_estimate_eur"] is not None
    assert row["cost_estimate_eur"] > 0


def test_run_unpublished_workflow_raises_and_inserts_no_row(
    conn, mock_llm_client: MagicMock
) -> None:
    conn.execute("UPDATE workflows SET status = 'draft' WHERE id = 1")
    conn.commit()

    with pytest.raises(WorkflowNotRunnable):
        run_workflow(
            conn,
            workflow_id=1,
            run_by="alice",
            inputs=_PROPOSAL_INPUTS,
            client=mock_llm_client,
        )

    count = conn.execute(
        "SELECT COUNT(*) AS n FROM runs WHERE workflow_id = 1"
    ).fetchone()["n"]
    assert count == 0
    mock_llm_client.chat.completions.create.assert_not_called()
