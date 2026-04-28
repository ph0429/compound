"""Tests for the workflow submission validator."""
from __future__ import annotations

from core.workflows import validate


def _base_workflow() -> dict:
    return {
        "title": "Test workflow",
        "prompt": "Write a short summary of the following text: {body}. "
                  "Use plain English. Keep it under 100 words.",
        "inputs_json": '[{"key": "body", "label": "Body"}]',
        "owner": "Test owner",
        "success_criterion": "The summary is under 100 words and uses plain English.",
        "tags": "test",
    }


def test_validator_rejects_missing_owner() -> None:
    workflow = _base_workflow()
    workflow.pop("owner")
    ok, errors = validate(workflow)
    assert ok is False
    assert any("owner" in e.lower() for e in errors)


def test_validator_rejects_missing_success_criterion() -> None:
    workflow = _base_workflow()
    workflow.pop("success_criterion")
    ok, errors = validate(workflow)
    assert ok is False
    assert any(
        "success_criterion" in e.lower() or "success criterion" in e.lower()
        for e in errors
    )


def test_validator_accepts_complete_workflow() -> None:
    ok, errors = validate(_base_workflow())
    assert ok is True
    assert errors == []
