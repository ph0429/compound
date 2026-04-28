"""Drop the runtime database and recreate it from schema and seed."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.settings import DB_PATH  # noqa: E402
from core.db import init_db  # noqa: E402


def main() -> None:
    target = Path(DB_PATH)
    if target.exists():
        target.unlink()
    init_db(DB_PATH)
    print(f"Recreated {DB_PATH}")


if __name__ == "__main__":
    main()
