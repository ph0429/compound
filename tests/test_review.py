"""Tests for core.review with a mocked OpenAI client."""
from __future__ import annotations

import json
from unittest.mock import MagicMock

from core.review import review_workflow


def _make_response(text: str) -> MagicMock:
    response = MagicMock()
    response.choices = [MagicMock()]
    response.choices[0].message.content = text
    return response


def _sample_workflow() -> dict:
    return {
        "title": "Sample",
        "prompt": "Summarise {body} in two sentences. Use plain English.",
        "inputs_json": '[{"key": "body", "label": "Body"}]',
        "owner": "Tester",
        "success_criterion": "Output is two sentences and uses plain English.",
        "tags": "test",
    }


def test_review_returns_parsed_dict_on_valid_json(
    mock_llm_client: MagicMock,
) -> None:
    valid = json.dumps(
        {
            "score": 85,
            "summary": "Looks good. Clear scope.",
            "suggestions": ["Tighten the wording."],
            "recommendation": "approve",
        }
    )
    mock_llm_client.chat.completions.create.return_value = _make_response(valid)

    result = review_workflow(_sample_workflow(), mock_llm_client)

    assert result["parse_ok"] is True
    assert result["score"] == 85
    assert result["recommendation"] == "approve"
    assert result["suggestions"] == ["Tighten the wording."]


def test_review_returns_revise_on_garbage_response(
    mock_llm_client: MagicMock,
) -> None:
    mock_llm_client.chat.completions.create.return_value = _make_response(
        "this is not json at all"
    )

    result = review_workflow(_sample_workflow(), mock_llm_client)

    assert result["parse_ok"] is False
    assert result["recommendation"] == "revise"
    assert result["raw_response"] == "this is not json at all"


def test_review_returns_revise_when_score_is_wrong_type(
    mock_llm_client: MagicMock,
) -> None:
    invalid = json.dumps(
        {
            "score": "high",
            "summary": "Looks fine.",
            "suggestions": [],
            "recommendation": "approve",
        }
    )
    mock_llm_client.chat.completions.create.return_value = _make_response(invalid)

    result = review_workflow(_sample_workflow(), mock_llm_client)

    assert result["parse_ok"] is False
    assert result["recommendation"] == "revise"
