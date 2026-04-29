"""OpenAI-backed review of a submitted workflow.

Returns a structured dict with score, summary, suggestions, and a
recommendation. The recommendation is advisory only. Status only ever
changes through workflows.approve or workflows.reject.

On JSON parse failure or schema drift the function falls back to a
recommendation of revise with parse_ok=False and the raw response
preserved. The caller is expected to attach the result via
workflows.attach_review and surface it to the human approver.
"""
from __future__ import annotations

import json
from typing import Any

from config.settings import OPENAI_MODEL

REVIEW_SYSTEM_PROMPT = (
    "You review proposed AI workflow templates for a small team library. "
    "You receive a workflow definition with title, prompt, inputs, owner, "
    "and a stated success criterion.\n\n"
    "Reply with valid JSON only, with this exact shape:\n"
    "{\n"
    '  "score": <integer between 0 and 100>,\n'
    '  "summary": "<one or two sentences>",\n'
    '  "suggestions": ["<short string>", ...],\n'
    '  "recommendation": "approve" | "revise" | "reject"\n'
    "}\n\n"
    "No prose outside the JSON."
)

_VALID_RECOMMENDATIONS = {"approve", "revise", "reject"}


def review_workflow(workflow: dict, client: Any) -> dict:
    """Ask the model to review a workflow. Returns a normalised dict.

    On JSON parse or schema validation failure, returns
    recommendation='revise' with parse_ok=False and the raw response
    preserved for the operator.
    """
    user_msg = json.dumps(
        {
            "title": workflow.get("title"),
            "prompt": workflow.get("prompt"),
            "inputs_json": workflow.get("inputs_json"),
            "owner": workflow.get("owner"),
            "success_criterion": workflow.get("success_criterion"),
            "tags": workflow.get("tags"),
        },
        indent=2,
    )

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": REVIEW_SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        max_tokens=1024,
        response_format={"type": "json_object"},
    )
    raw = response.choices[0].message.content or ""

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return _fallback("Model response could not be parsed.", raw)

    if not _validate_review_shape(parsed):
        return _fallback(
            "Model response did not match the expected schema.", raw
        )

    return {
        "score": parsed["score"],
        "summary": parsed["summary"],
        "suggestions": parsed["suggestions"],
        "recommendation": parsed["recommendation"],
        "parse_ok": True,
        "raw_response": raw,
    }


def _validate_review_shape(d: Any) -> bool:
    if not isinstance(d, dict):
        return False
    score = d.get("score")
    if not isinstance(score, int) or isinstance(score, bool):
        return False
    if not 0 <= score <= 100:
        return False
    if not isinstance(d.get("summary"), str):
        return False
    suggestions = d.get("suggestions")
    if not isinstance(suggestions, list):
        return False
    if not all(isinstance(s, str) for s in suggestions):
        return False
    if d.get("recommendation") not in _VALID_RECOMMENDATIONS:
        return False
    return True


def _fallback(summary: str, raw: str) -> dict:
    return {
        "score": None,
        "summary": summary,
        "suggestions": [],
        "recommendation": "revise",
        "parse_ok": False,
        "raw_response": raw,
    }
