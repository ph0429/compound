"""Smoke test that app.py imports cleanly without starting Streamlit.

Streamlit-specific behaviour (rendering, session state) is not unit-tested.
This guard catches syntax errors and broken imports that would otherwise
only surface at deploy time.
"""
from __future__ import annotations

import importlib


def test_app_imports() -> None:
    importlib.import_module("app")
