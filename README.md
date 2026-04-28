# Compound

A small library is the difference between a team that uses AI and a team that compounds it.

Compound is a shared AI workflow library. Anyone in a small team can publish, browse, and run a vetted AI workflow. New workflows go through a quick check (basic rules, then a quick AI sense-check, then a human signs off) before they are visible to the team. Every run is recorded.

## The problem this answers

Individual AI capability is strong but not compounding. Each person has their own prompts and setups; nothing is shared, vetted, or reusable across the team. The bottleneck is not the AI itself; raw Claude and ChatGPT are already strong. It is the missing layer that turns one person's good workflow into something the rest of the team can use tomorrow.

Claude is the engine. Compound is where the team learns how to drive: the prompts that work, the inputs that matter, the outputs worth keeping.

## How AI was used in this build

Claude Code wrote most of the code, with operator review on every change before it landed. The Anthropic Claude API powers the in-product review and run steps. Tests fake out the Anthropic client so the test suite is predictable and uses no live API credit.

One example of operator judgement overriding an AI suggestion: the model proposed a single `prompt` text column on the `workflows` table. The build uses a `steps_json` column instead, with v1 enforcing one step. The schema supports multi-step workflows from day one, so chained workflows are a feature flip, not a migration.

## How to run it locally

```
pip install -r requirements.txt
cp .env.example .env   # add your Anthropic key
python scripts/reset_db.py
streamlit run app.py
pytest tests/
```

## Architecture

`core/` is the logic. `app.py` is the UI. `db/` is the data. No surprises.

## The control model

Basic rules run first (required fields, no obvious secret patterns). The model returns a structured review (score, summary, suggestions, recommendation). The human is the last gate; the model's recommendation is advisory and never changes status on its own. No silent writes. Every run, sign-off, and parse failure is recorded.

## Key decisions

The build is single-step today; the data model and the UI treat every library entry as a workflow with one or more steps. SQLite ships with the repo for zero-config; Supabase is named below as the production path. The `runs` table is append-only by trigger, not by convention. All user-facing strings live in `core/copy.py`, which makes voice and language reviewable in one place.

**Why this and not Claude Projects or a team repo of prompts.** Claude Projects shares context within Claude, but it does not vet prompts, structure inputs, or log runs across the team. A GitHub repo of prompts works for engineers and excludes everyone else. Compound is the small layer that fills the gap: a vetted, run-able workflow with an audit trail, usable by every role, with the prompts themselves still version-controlled in git underneath.

## What was deliberately excluded, and what comes next (in order)

1. Multi-step workflows. The schema already supports them; the v1 UI renders one step.
2. Authentication. Single-user demo today.
3. Slack notifications and approvals.
4. Supabase as the production database.
5. Smart search across workflows (vector search).
6. Notion or Slack import path for existing prompts.

## Troubleshooting

- If the Streamlit Cloud URL is slow, refresh once. The free tier sleeps after inactivity.
- If the database is missing, run `python scripts/reset_db.py`.
- If `pytest` fails on imports, run `pip install -r requirements.txt` again.
