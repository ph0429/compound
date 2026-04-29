"""Shared test fixtures: seeded temp database, mocked LLM client."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock
from typing import Iterator

import pytest

from core.db import get_connection, init_db


@pytest.fixture
def conn(tmp_path: Path) -> Iterator:
    """Open a fresh seeded database in a per-test temp file."""
    db_path = str(tmp_path / "compound.db")
    init_db(db_path)
    connection = get_connection(db_path)
    try:
        yield connection
    finally:
        connection.close()


@pytest.fixture
def mock_llm_client() -> MagicMock:
    """Stand-in for the OpenAI client.

    Tests configure responses by setting
    `client.chat.completions.create.return_value` to a mock with a
    populated `.choices[0].message.content` and, where relevant,
    `.usage.prompt_tokens` and `.usage.completion_tokens`.
    """
    return MagicMock()
