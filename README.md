# Compound

A small library is the difference between a team that uses AI and a team that compounds it.

Compound is a shared AI workflow library. Anyone in a small team can publish, browse, and run a vetted AI workflow. New submissions go through a light review queue: deterministic checks, then a model review, then a human approval. Every run is recorded with prompt, output, model, token counts, and a cost estimate.

Live demo: https://compound-demo.streamlit.app/

## The problem this answers

Individual AI use is strong but not compounding. Each person has their own prompts; nothing is vetted, shared, or reusable. The bottleneck is not the model. It is the missing layer that turns one person's good workflow into something the rest of the team can run tomorrow.

## How AI was used in this build

The Streamlit app, the data layer, the tests, and the UI were written with Claude Code, with operator review on every commit before it landed. The commit history on the main branch is the audit trail of that pairing.

The in-product review and run steps call OpenAI's gpt-5.4-mini through the standard chat completions API. JSON mode constrains the review output to a fixed schema. Tests mock the LLM client so the suite is predictable and uses no live credit.

## How to run it locally

```
pip install -r requirements.txt
cp .env.example .env   # add your OPENAI_API_KEY
python scripts/reset_db.py
streamlit run app.py
pytest tests/
```

## Architecture

- `core/` holds the pure-Python logic. No Streamlit imports.
- `app.py` is the UI, and the only place Streamlit lives.
- `db/` holds the schema, the seed, and the runtime SQLite file.

## The control model

- Deterministic checks run first: required fields, prompt length, and obvious secret-pattern detection.
- The model returns a structured review (score, summary, suggestions, recommendation) constrained by JSON mode. The recommendation is advisory.
- The human is the last gate. Status only changes on human action. The `runs` table is append-only by SQL trigger; the `reviews` table records every attempt including parse failures.

## Key decisions

SQLite ships with the repo for zero-config and seeds two workflows on first run. The `runs` table is append-only by SQL trigger, not by convention. All user-facing strings live in `core/copy.py`, which makes voice reviewable in one place. The submit pipeline shows a four-stage status line so the user is never staring at silence during the model call.

Two trade-offs are accepted and worth naming. First, the deterministic checks catch missing fields and accidental secret leakage. They do not catch prompt-injection attempts. The threat model is a trusted small team, not the open internet; the model reviewer plus the human approver are the two layers that matter for adversarial inputs in this build. A stronger deterministic layer is named under what comes next. Second, the empty-state UI is unreachable on the seeded demo path. It exists for fresh installs and clean first-run behaviour. The seeded demo opens with two preloaded workflows on purpose.

The build plan locked Anthropic Claude as the LLM. The deployed instance uses OpenAI's gpt-5.4-mini at the operator's direction. The interface in `core/review.py` and `core/runs.py` made the swap a single commit; the rest of the architecture did not need to change.

## What was deliberately excluded, and what comes next

1. A stronger deterministic layer with explicit prompt-injection patterns and a shared secret-pattern library.
2. Authentication and per-user audit, including a reviewer column on `workflows` so approvals are attributable.
3. Slack notifications when a workflow lands in review and again when it is approved.
4. A demo response cache behind `COMPOUND_USE_CACHE=true`, for offline recordings and CI.
5. Supabase as the production database, keeping the same SQL surface.
6. Vector search across prompt and success-criterion fields.
7. A Notion or Slack import path for existing team prompts.
8. Bump `actions/checkout` and `actions/setup-python` to their Node 24 lines before September 2026.

## Troubleshooting

- If the Streamlit Cloud URL is slow on first load, refresh once. The free tier sleeps after inactivity.
- The Streamlit Cloud filesystem is ephemeral. Anything submitted on the public URL is reset on the next redeploy; the seeded workflows reload on cold start.
- Locally, if `pytest` fails on imports, run `pip install -r requirements.txt` against your active virtual environment.
