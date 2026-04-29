"""All user-facing strings.

British English. No em dashes. No exclamation marks. Plain words.
Every string the UI shows comes from this module.
"""
from __future__ import annotations

PAGE_LIBRARY = "Library"
PAGE_SUBMIT = "Submit"

HEADER_LIBRARY = "Compound"
HEADER_SUBMIT = "Submit a workflow"

LABEL_NAV = "Navigation"

TAKEAWAY = (
    "A small library is the difference between a team that uses AI and a "
    "team that compounds it."
)

LIBRARY_EMPTY = "No workflows are published yet."
LIBRARY_EMPTY_BUTTON = "Submit the first one"

STAGE_VALIDATE = "Running automatic checks..."
STAGE_SUBMIT = "Saving the draft..."
STAGE_REVIEW = "Asking the AI for a review..."
STAGE_DONE = "Review complete. Awaiting your decision."

LABEL_TITLE = "Title"
LABEL_PROMPT = "Instructions"
LABEL_OWNER = "Owner"
LABEL_SUCCESS_CRITERION = "What good output looks like"
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
    "approve": "Recommended: approve",
    "revise": "Recommended: revise",
    "reject": "Recommended: reject",
}

ERROR_VALIDATION_FAILED = "The submission has issues. Fix these and try again:"
ERROR_REVIEW_FAILED = (
    "The AI review could not complete. The submission is saved as under review."
)
ERROR_RUN_FAILED = "The run did not complete. Nothing was added to the history."
ERROR_NOT_PUBLISHED = "This workflow is not published. It cannot be run."

MESSAGE_INPUTS_REQUIRED = "Please fill in every input before running."
MESSAGE_RUN_COMPLETE = "Run complete."
MESSAGE_APPROVED = "Approved and published."
MESSAGE_REJECTED = "Rejected."
MESSAGE_RUNNING = "Running..."

LABEL_SCORE = "Score"

SECTION_INSTRUCTIONS = "Instructions"
SECTION_SUCCESS_CRITERION = "What good output looks like"
SECTION_RUN_WORKFLOW = "Run this workflow"
SECTION_OUTPUT = "Output"
SECTION_RECENT_RUNS = "Recent runs"
SECTION_SUMMARY = "Summary"
SECTION_SUGGESTIONS = "Suggestions"
SECTION_RAW_RESPONSE = "What the AI sent back"

HISTORY_EMPTY = "No runs yet."

CAPTION_METADATA_TEMPLATE = "Owner: {owner}  ·  Tags: {tags}"
HEADER_REVIEW_TEMPLATE = "Review: {title}"
RUN_RECORD_TEMPLATE = "{when} by {who}"
