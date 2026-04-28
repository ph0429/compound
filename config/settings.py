"""Canonical environment variable reference.

Loads .env via python-dotenv and exposes typed module-level constants.
Every other module reads config from here, never from os.environ directly.
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent

DB_PATH: str = os.environ.get("COMPOUND_DB_PATH", "db/compound.db")
ANTHROPIC_API_KEY: str | None = os.environ.get("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL: str = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-5")
USE_CACHE: bool = os.environ.get("COMPOUND_USE_CACHE", "false").lower() == "true"
