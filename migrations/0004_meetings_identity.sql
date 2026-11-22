-- 0004_meetings_identity.sql
-- Upgrade ONLY after 0001, 0002 and 0003 have been reconciled and applied.
-- Cloudflare D1 processes migrations transactionally. Do not execute these
-- statements one by one or run them outside a single transaction.
-- PRAGMA foreign_keys=OFF is not supported for D1 migrations.
-- Defer validation while rebuilding the parent table; child FK references
-- will resolve to the new table called meetings at transaction commit.
-- IMPORTANT: defer_foreign_keys does NOT suppress ON DELETE CASCADE.
-- Preflight backup, row counts, migration bookkeeping and independent review
-- are mandatory. No remote application is authorized by this source file.
PRAGMA defer_foreign_keys = ON;

CREATE TABLE meetings_rebuilt (
  id TEXT PRIMARY KEY,
  municipality_id TEXT NOT NULL REFERENCES municipalities(id),
  body TEXT NOT NULL CHECK(length(trim(body)) > 0),
  meeting_date TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'scheduled'
    CHECK(status IN('scheduled','completed','cancelled','unknown')),
  official_url TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO meetings_rebuilt
  (id, municipality_id, body, meeting_date, status, official_url, created_at)
SELECT id, municipality_id, body, meeting_date, status, official_url, created_at
FROM meetings;

DROP TABLE meetings;
ALTER TABLE meetings_rebuilt RENAME TO meetings;

-- Indexes belonging to the dropped table need to be recreated.
CREATE INDEX idx_meetings_date ON meetings(meeting_date);
CREATE INDEX idx_meetings_body_day ON meetings(municipality_id, body, meeting_date);

-- The migration runner must check PRAGMA foreign_key_check and verify row
-- counts in tests BEFORE remote execution. This statement reports violations
-- but does not itself abort a migration if rows are returned.
