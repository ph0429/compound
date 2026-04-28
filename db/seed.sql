INSERT INTO workflows (title, prompt, inputs_json, owner, success_criterion, tags, status, published_at)
VALUES (
  'Proposal Outline',
  'Write a one-page proposal outline for {client_name}. The work is {project_type}. The client''s stated needs are: {key_needs}. Output seven sections: Context, Proposed Approach, Scope, Deliverables, Timeline, Commercials, Next Steps. Keep each section to two or three sentences. Use British English. No exclamation marks.',
  '[{"key": "client_name", "label": "Client name"}, {"key": "project_type", "label": "Project type"}, {"key": "key_needs", "label": "Key needs"}]',
  'Brad the BI consultant',
  'Output contains all seven sections, each with two to three sentences, and uses British English.',
  'sales,proposal',
  'published',
  CURRENT_TIMESTAMP
);

INSERT INTO workflows (title, prompt, inputs_json, owner, success_criterion, tags, status, published_at)
VALUES (
  'Meeting Recap',
  'Read the following raw meeting notes and produce a structured recap. Notes: {raw_notes}. Output four sections: Decisions, Actions (with owner and date), Open questions, Next meeting. Use British English. No exclamation marks.',
  '[{"key": "raw_notes", "label": "Raw meeting notes"}]',
  'Maya the project manager',
  'Output contains four sections; every action has an owner and a date or TBD.',
  'operations,meetings',
  'published',
  CURRENT_TIMESTAMP
);
