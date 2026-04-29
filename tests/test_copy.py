"""Voice guard. Every user-facing string in core.copy must respect house style.

The project's voice rules forbid exclamation marks and dashes (em or en).
Catching these via assertion in CI prevents quiet regressions when new
strings are added later.
"""
from __future__ import annotations

from typing import Iterator

import core.copy as copy_module


def _all_strings() -> Iterator[tuple[str, str]]:
    for name in dir(copy_module):
        if name.startswith("_"):
            continue
        value = getattr(copy_module, name)
        if isinstance(value, str):
            yield (name, value)
        elif isinstance(value, dict):
            for key, item in value.items():
                if isinstance(item, str):
                    yield (f"{name}[{key!r}]", item)


def test_no_exclamation_marks() -> None:
    for name, value in _all_strings():
        assert "!" not in value, (
            f"copy.{name} has an exclamation mark: {value!r}"
        )


def test_no_em_or_en_dashes() -> None:
    for name, value in _all_strings():
        assert "—" not in value, (
            f"copy.{name} has an em dash: {value!r}"
        )
        assert "–" not in value, (
            f"copy.{name} has an en dash: {value!r}"
        )
