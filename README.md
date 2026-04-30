# Compound

A small library is the difference between a team that uses AI and a team that compounds it.

Compound is a shared workflow library. New submissions go through automatic checks, then an AI review, then a human approval. Every run is recorded.

**Live demo:** https://compound-demo.streamlit.app/
**Repo:** https://github.com/ph0429/compound

## What it does

MultiBase's brief named scattered, inconsistent AI usage as a friction point and a digital workforce as the destination. Compound is the smallest piece of foundation that has to exist before either is real: a place to store, review, and reuse the prompts that actually work, with a record kept every time someone runs one.

A user opens the app, browses two preloaded workflows (Proposal Outline, Meeting Recap), submits a new one, watches it pass automatic checks, then an AI review, then human approval, then runs the approved workflow against their own inputs.

## How to run it

```
git clone https://github.com/ph0429/compound
cd compound
pip install -r requirements.txt
cp .env.example .env   # add your OPENAI_API_KEY
python scripts/reset_db.py
streamlit run app.py
```

Or open the live demo: https://compound-demo.streamlit.app/

Tests: `pytest tests/` runs 22 passing.

## Key decisions

**The control model.** Automatic checks run first: required fields, prompt length, anything that looks like a password or email pasted in by accident. If the basic shape is wrong, the AI is not asked anything; the system refuses to continue. The AI then returns a review with four parts: a score out of one hundred, a one or two sentence summary, a list of suggestions, and a recommendation. The recommendation is just a suggestion; only a human can approve, revise, or reject. The history of runs can only be added to; past runs cannot be edited or deleted. Every review attempt is recorded, including ones the AI returned in the wrong format.

**The stack.** A small built-in database (SQLite) ships with the project, preloaded with two workflows on first run. The interface is built on Streamlit and hosted on Streamlit Community Cloud. OpenAI's gpt-5.4-mini powers the review and run steps. Every word the user sees lives in one file (`core/copy.py`); a test fails the build if anyone introduces an exclamation mark or any kind of dash, so the voice stays consistent.

**How AI was used in this build.** The app, the data layer, the tests, and the interface were written with Claude Code, with my review on every change before it landed. The change history on the main branch is the audit trail of that pairing. An example of judgement during the build: the table of runs originally had a column for cost in euros, defined when the AI was still planned as Anthropic. When OpenAI's gpt-5.4-mini prices came back in dollars, I renamed the column to dollars rather than apply an exchange rate to numbers I could not actually justify. Storing values you cannot stand behind is worse than picking a less-friendly unit. Tests use a stand-in for the AI, so the test suite costs nothing to run.

**Two compromises accepted.** The automatic checks catch missing fields and obvious secrets pasted in by accident. They do not catch attempts to trick the AI itself. The audience for this is a trusted small team, not the open internet; the AI review and the human approver cover that risk in this version. The empty-library message exists for fresh installs but is never seen during the demo, because the project always preloads two workflows. Both are deliberate choices, not gaps.

## What I would add next

1. Stronger automatic checks: patterns that catch attempts to trick the AI, and a shared list of things that look like secrets.
2. Sign-in, so approvals are recorded against a real person.
3. Slack notifications when a workflow lands in review and again when approved.
4. A saved-response mode, so the demo can run offline and the test suite stays predictable.
5. Supabase as the proper database for production.
6. Smart search by meaning across prompts and standards (vector search).
7. A way to import existing team prompts from Notion or Slack.
