"""Execute a published workflow and append a run record.

Order is deliberate: API call first, INSERT second. If the INSERT fails,
the failure surfaces as an exception; the audit row is never silently
lost. Running an unpublished workflow raises before any API call.
"""
from __future__ import annotations

import json
import sqlite3
from typing import Any

from config.settings import OPENAI_MODEL

# Indicative pricing per million tokens for gpt-5.4-mini, USD.
# Source: https://developers.openai.com/api/docs/models/gpt-5.4-mini
# The column is informational only; refresh if the default model changes.
INPUT_COST_PER_M_USD = 0.75
OUTPUT_COST_PER_M_USD = 4.50


class WorkflowNotRunnable(Exception):
    """Raised when a workflow cannot be run (missing or not published)."""


def run_workflow(
    conn: sqlite3.Connection,
    workflow_id: int,
    run_by: str,
    inputs: dict,
    client: Any,
) -> str:
    """Render the prompt, call the model, log the run, return the output."""
    row = conn.execute(
        "SELECT prompt, status FROM workflows WHERE id = ?",
        (workflow_id,),
    ).fetchone()
    if row is None:
        raise WorkflowNotRunnable(f"Workflow {workflow_id} not found")
    if row["status"] != "published":
        raise WorkflowNotRunnable(
            f"Workflow {workflow_id} is not published (status={row['status']})"
        )

    rendered = _render_prompt(row["prompt"], inputs)

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": rendered}],
        max_completion_tokens=2048,
    )
    output = response.choices[0].message.content or ""
    input_tokens = int(getattr(response.usage, "prompt_tokens", 0) or 0)
    output_tokens = int(getattr(response.usage, "completion_tokens", 0) or 0)
    cost = _estimate_cost_usd(input_tokens, output_tokens)

    conn.execute(
        "INSERT INTO runs "
        "(workflow_id, run_by, inputs_json, output, model, "
        " input_tokens, output_tokens, cost_estimate_usd) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            workflow_id,
            run_by,
            json.dumps(inputs),
            output,
            OPENAI_MODEL,
            input_tokens,
            output_tokens,
            cost,
        ),
    )
    conn.commit()
    return output


def _render_prompt(template: str, inputs: dict) -> str:
    return template.format(**inputs)


def _estimate_cost_usd(input_tokens: int, output_tokens: int) -> float:
    return (input_tokens / 1_000_000) * INPUT_COST_PER_M_USD + (
        output_tokens / 1_000_000
    ) * OUTPUT_COST_PER_M_USD
