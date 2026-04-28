"""All user-facing strings.

British English. No em dashes. No exclamation marks. Plain words.
Every string the UI shows comes from this module.
"""
from __future__ import annotations

PAGE_LIBRARY = "Library"
PAGE_SUBMIT = "Submit"

HEADER_LIBRARY = "Compound"
HEADER_SUBMIT = "Submit a workflow"

TAKEAWAY = (
    "A small library is the difference between a team that uses AI and a "
    "team that compounds it."
)

LIBRARY_EMPTY = "No workflows are published yet."
LIBRARY_EMPTY_BUTTON = "Submit the first one"

STAGE_VALIDATE = "Running deterministic checks..."
STAGE_SUBMIT = "Saving the draft..."
STAGE_REVIEW = "Asking the model for a review..."
STAGE_DONE = "Review complete. Awaiting your decision."

LABEL_TITLE = "Title"
LABEL_PROMPT = "Prompt"
LABEL_OWNER = "Owner"
LABEL_SUCCESS_CRITERION = "Success criterion"
LABEL_TAGS = "Tags (comma-separated)"
LABEL_INPUTS = "Inputs"
LABEL_INPUT_KEY = "Key"
LABEL_INPUT_LABEL = "Label"

BUTTON_SUBMIT = "Submit for review"
BUTTON_RUN = "Run"
BUTTON_APPROVE = "Approve"
BUTTON_REJECT = "Reject"
BUTTON_ADD_INPUT = "Add row"

RECOMMENDATION_LABELS = {
    "approve": "Approve recommended",
    "revise": "Revise recommended",
    "reject": "Reject recommended",
}

ERROR_VALIDATION_FAILED = "The submission has issues. Fix these and try again:"
ERROR_REVIEW_FAILED = (
    "The model review could not complete. The submission is saved as under review."
)
ERROR_RUN_FAILED = "The run did not complete. No row was added to the audit log."
ERROR_NOT_PUBLISHED = "This workflow is not published. It cannot be run."
