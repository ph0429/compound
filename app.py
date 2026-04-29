"""Streamlit entry point.

Two pages: Library and Submit. The sidebar is navigation only. All
business logic lives in core/. This module is responsible for
rendering, capturing user input, and wiring the two together.
"""
from __future__ import annotations

import json
import sqlite3

import streamlit as st
from openai import OpenAI

from config.settings import DB_PATH, OPENAI_API_KEY
from core import audit, copy, review, runs, workflows
from core.db import get_connection, init_db


@st.cache_resource
def get_conn() -> sqlite3.Connection:
    """Open the runtime database, initialising on first call."""
    init_db(DB_PATH)
    return get_connection(DB_PATH)


@st.cache_resource
def get_client() -> OpenAI:
    """Build a single OpenAI client for the app session."""
    return OpenAI(api_key=OPENAI_API_KEY)


def main() -> None:
    """Render the sidebar and dispatch to the chosen page."""
    st.set_page_config(page_title="Compound", layout="centered")

    if "nav" not in st.session_state:
        st.session_state["nav"] = copy.PAGE_LIBRARY

    with st.sidebar:
        st.markdown(f"### {copy.HEADER_LIBRARY}")
        default_index = (
            0 if st.session_state["nav"] == copy.PAGE_LIBRARY else 1
        )
        choice = st.radio(
            "Navigation",
            [copy.PAGE_LIBRARY, copy.PAGE_SUBMIT],
            index=default_index,
            label_visibility="collapsed",
        )
        st.session_state["nav"] = choice

    conn = get_conn()
    client = get_client()

    if choice == copy.PAGE_LIBRARY:
        page_library(conn, client)
    else:
        page_submit(conn, client)


def page_library(conn: sqlite3.Connection, client: OpenAI) -> None:
    """Render the published-workflow library."""
    st.header(copy.HEADER_LIBRARY)
    st.caption(copy.TAKEAWAY)

    published = workflows.list_published(conn)

    if not published:
        st.info(copy.LIBRARY_EMPTY)
        if st.button(copy.LIBRARY_EMPTY_BUTTON):
            st.session_state["nav"] = copy.PAGE_SUBMIT
            st.rerun()
        return

    for wf in published:
        with st.expander(wf["title"]):
            tags = wf.get("tags") or "(none)"
            st.caption(f"Owner: {wf['owner']}  ·  Tags: {tags}")

            st.markdown("**Prompt template**")
            st.code(wf["prompt"], language="text")

            st.markdown("**Success criterion**")
            st.write(wf["success_criterion"])

            st.markdown("**Run this workflow**")
            inputs_values = _render_input_form(wf)

            run_key = f"run_{wf['id']}"
            if st.button(copy.BUTTON_RUN, key=run_key):
                _handle_run(conn, client, wf, inputs_values)

            _render_run_history(conn, wf["id"])


def page_submit(conn: sqlite3.Connection, client: OpenAI) -> None:
    """Render the submission form and the four-stage review pipeline."""
    st.header(copy.HEADER_SUBMIT)
    st.caption(copy.TAKEAWAY)

    if "input_rows" not in st.session_state:
        st.session_state["input_rows"] = [
            {"key": "", "label": ""},
            {"key": "", "label": ""},
        ]

    title = st.text_input(copy.LABEL_TITLE)
    prompt = st.text_area(copy.LABEL_PROMPT, height=200)
    owner = st.text_input(copy.LABEL_OWNER)
    success_criterion = st.text_area(
        copy.LABEL_SUCCESS_CRITERION, height=80
    )
    tags = st.text_input(copy.LABEL_TAGS)

    st.markdown(f"**{copy.LABEL_INPUTS}**")
    captured_rows: list[dict] = []
    for i, row in enumerate(st.session_state["input_rows"]):
        col_key, col_label = st.columns(2)
        with col_key:
            row_key = st.text_input(
                copy.LABEL_INPUT_KEY,
                value=row["key"],
                key=f"row_key_{i}",
            )
        with col_label:
            row_label = st.text_input(
                copy.LABEL_INPUT_LABEL,
                value=row["label"],
                key=f"row_label_{i}",
            )
        captured_rows.append({"key": row_key, "label": row_label})

    if st.button(copy.BUTTON_ADD_INPUT):
        st.session_state["input_rows"] = captured_rows + [
            {"key": "", "label": ""}
        ]
        st.rerun()
    else:
        st.session_state["input_rows"] = captured_rows

    if st.button(copy.BUTTON_SUBMIT, type="primary"):
        _run_submit_pipeline(
            conn,
            client,
            title=title,
            prompt=prompt,
            owner=owner,
            success_criterion=success_criterion,
            tags=tags,
            rows=captured_rows,
        )

    if "last_review" in st.session_state:
        _render_review_panel(conn)


def _render_input_form(wf: dict) -> dict:
    fields = _parse_inputs(wf["inputs_json"])
    values: dict = {}
    for field in fields:
        key = field.get("key", "")
        label = field.get("label", key)
        if not key:
            continue
        values[key] = st.text_area(
            label,
            key=f"input_{wf['id']}_{key}",
            height=80,
        )
    return values


def _handle_run(
    conn: sqlite3.Connection,
    client: OpenAI,
    wf: dict,
    inputs_values: dict,
) -> None:
    if any(not v.strip() for v in inputs_values.values()):
        st.warning("Please fill in every input before running.")
        return
    try:
        with st.spinner("Running..."):
            output = runs.run_workflow(
                conn,
                workflow_id=wf["id"],
                run_by="demo",
                inputs=inputs_values,
                client=client,
            )
    except runs.WorkflowNotRunnable:
        st.error(copy.ERROR_NOT_PUBLISHED)
        return
    except Exception as exc:
        st.error(f"{copy.ERROR_RUN_FAILED}\n\n{exc}")
        return
    st.success("Run complete.")
    st.markdown("**Output**")
    st.write(output)


def _render_run_history(conn: sqlite3.Connection, workflow_id: int) -> None:
    st.markdown("**Recent runs**")
    history = audit.runs_by_workflow(conn, workflow_id)
    if not history:
        st.caption("No runs yet.")
        return
    for record in history[:3]:
        st.caption(f"{record['created_at']} by {record['run_by']}")
        snippet = record["output"]
        if len(snippet) > 400:
            snippet = snippet[:400] + "..."
        st.text(snippet)


def _run_submit_pipeline(
    conn: sqlite3.Connection,
    client: OpenAI,
    *,
    title: str,
    prompt: str,
    owner: str,
    success_criterion: str,
    tags: str,
    rows: list[dict],
) -> None:
    inputs_clean = [r for r in rows if r["key"].strip()]
    inputs_json = json.dumps(
        [{"key": r["key"].strip(), "label": r["label"].strip()} for r in inputs_clean]
    )
    workflow = {
        "title": title.strip(),
        "prompt": prompt,
        "owner": owner.strip(),
        "success_criterion": success_criterion.strip(),
        "tags": tags.strip(),
        "inputs_json": inputs_json,
    }

    status = st.empty()

    status.info(copy.STAGE_VALIDATE)
    ok, errors = workflows.validate(workflow)
    if not ok:
        status.error(copy.ERROR_VALIDATION_FAILED)
        for err in errors:
            st.write(f"- {err}")
        return

    status.info(copy.STAGE_SUBMIT)
    try:
        workflow_id = workflows.submit(conn, workflow)
        workflows.request_review(conn, workflow_id)
    except Exception as exc:
        status.error(f"Could not save the draft: {exc}")
        return

    status.info(copy.STAGE_REVIEW)
    try:
        review_result = review.review_workflow(workflow, client)
        workflows.attach_review(conn, workflow_id, review_result)
    except Exception as exc:
        status.error(f"{copy.ERROR_REVIEW_FAILED}\n\n{exc}")
        return

    status.success(copy.STAGE_DONE)
    st.session_state["last_review"] = {
        "workflow_id": workflow_id,
        "title": workflow["title"],
        "result": review_result,
    }


def _render_review_panel(conn: sqlite3.Connection) -> None:
    panel = st.session_state["last_review"]
    workflow_id = panel["workflow_id"]
    result = panel["result"]
    recommendation = result.get("recommendation", "revise")

    st.divider()
    st.markdown(f"### Review: {panel['title']}")
    label = copy.RECOMMENDATION_LABELS.get(recommendation, recommendation)
    if recommendation == "approve":
        st.success(label)
    elif recommendation == "reject":
        st.error(label)
    else:
        st.warning(label)

    if result.get("score") is not None:
        st.metric("Score", result["score"])
    if result.get("summary"):
        st.markdown("**Summary**")
        st.write(result["summary"])
    suggestions = result.get("suggestions") or []
    if suggestions:
        st.markdown("**Suggestions**")
        for item in suggestions:
            st.write(f"- {item}")
    if not result.get("parse_ok"):
        with st.expander("Raw model response"):
            st.code(result.get("raw_response", ""))

    col_approve, col_reject = st.columns(2)
    with col_approve:
        if st.button(copy.BUTTON_APPROVE, type="primary", key="btn_approve"):
            _handle_decision(conn, workflow_id, decision="approve")
    with col_reject:
        if st.button(copy.BUTTON_REJECT, key="btn_reject"):
            _handle_decision(conn, workflow_id, decision="reject")


def _handle_decision(
    conn: sqlite3.Connection, workflow_id: int, *, decision: str
) -> None:
    try:
        if decision == "approve":
            workflows.approve(conn, workflow_id, "demo")
            st.success("Approved and published.")
        else:
            workflows.reject(conn, workflow_id, "")
            st.warning("Rejected.")
    except workflows.IllegalTransition as exc:
        st.error(str(exc))
        return
    st.session_state.pop("last_review", None)
    st.rerun()


def _parse_inputs(inputs_json: str) -> list[dict]:
    try:
        parsed = json.loads(inputs_json)
    except (json.JSONDecodeError, TypeError):
        return []
    return parsed if isinstance(parsed, list) else []


if __name__ == "__main__":
    main()
