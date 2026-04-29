# Compound — shared AI workflow library

## Purpose
A small Streamlit app where anyone in a team can publish, browse, and run a
vetted AI workflow. Submissions go through a light review queue
(deterministic checks, then model review, then human approval). Every run is
logged.

## Conventions
- Use python3, not python.
- Activate .venv before running: source .venv/bin/activate
- Config from .env via python-dotenv. Never hardcode credentials.
- config/settings.py is the canonical env var reference.
- All user-facing strings live in core/copy.py.
- Type hints on every public function in core/.
- Module-level docstrings on every file in core/.

## Repo layout
- app.py        Streamlit entry point.
- core/         Pure Python modules. No Streamlit imports here.
- config/       settings.py and any reference data.
- db/           schema.sql, seed.sql, runtime database (gitignored).
- tests/        pytest, in-memory SQLite, mocked Anthropic client.
- scripts/      Operational scripts (reset_db, export_audit, cache_demo_responses).
- demo_cache/   Pre-cached responses for demo fallback (gitignored).
- .github/      CI workflow (pytest on push).

## Safety rules
- No silent writes. Status transitions and runs go through core/workflows.py
  and core/runs.py only.
- Submissions are draft until approved. Fail closed on validator errors.
- LLM key from OPENAI_API_KEY only. Never log full keys.
- Tests must never make live model calls. Use the mock_llm_client
  fixture from tests/conftest.py.
- runs is append-only. Never UPDATE or DELETE rows in this table.

## How to run
- pip install -r requirements.txt
- cp .env.example .env   # add your Anthropic key
- python scripts/reset_db.py
- streamlit run app.py
- pytest tests/

## Voice
- British English. Plain words.
- No em dashes, no en dashes.
- No exclamation marks.
- Short sentences. One idea per paragraph.
- Declarative, not explanatory.