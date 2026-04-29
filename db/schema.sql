CREATE TABLE workflows (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  prompt TEXT NOT NULL,
  inputs_json TEXT NOT NULL,
  owner TEXT NOT NULL,
  success_criterion TEXT NOT NULL,
  tags TEXT,
  status TEXT NOT NULL CHECK (status IN ('draft','under_review','published','rejected')),
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  published_at TEXT
);

CREATE TABLE reviews (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  workflow_id INTEGER NOT NULL REFERENCES workflows(id),
  score INTEGER,
  summary TEXT,
  suggestions_json TEXT,
  recommendation TEXT CHECK (recommendation IN ('approve','revise','reject')),
  raw_response TEXT,
  parse_ok INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  workflow_id INTEGER NOT NULL REFERENCES workflows(id),
  run_by TEXT NOT NULL,
  inputs_json TEXT NOT NULL,
  output TEXT NOT NULL,
  model TEXT NOT NULL,
  input_tokens INTEGER,
  output_tokens INTEGER,
  cost_estimate_usd REAL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER runs_no_update BEFORE UPDATE ON runs
BEGIN
  SELECT RAISE(ABORT, 'runs is append-only');
END;

CREATE TRIGGER runs_no_delete BEFORE DELETE ON runs
BEGIN
  SELECT RAISE(ABORT, 'runs is append-only');
END;

CREATE INDEX idx_workflows_status ON workflows(status);
CREATE INDEX idx_reviews_workflow ON reviews(workflow_id);
CREATE INDEX idx_runs_workflow ON runs(workflow_id);
