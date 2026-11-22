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

-- These triggers reference meetings by name and SQLite validates them
-- during ALTER TABLE RENAME. Remove them temporarily and restore afterward.
DROP TRIGGER IF EXISTS guard_item_document_insert;
DROP TRIGGER IF EXISTS guard_item_document_update;
DROP TRIGGER IF EXISTS guard_cache_eligible_insert;
DROP TRIGGER IF EXISTS guard_cache_eligible_update;

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


-- Restore all meeting-dependent guards after the parent is recreated.
CREATE TRIGGER guard_item_document_insert BEFORE INSERT ON agenda_item_documents
WHEN NOT EXISTS (
 SELECT 1 FROM agenda_items a JOIN meetings m ON m.id=a.meeting_id
 JOIN document_versions v ON v.id=NEW.version_id JOIN documents d ON d.id=v.document_id
 WHERE a.id=NEW.item_id AND m.municipality_id=d.municipality_id
) BEGIN SELECT RAISE(ABORT,'item_document_municipality_mismatch'); END;
CREATE TRIGGER guard_item_document_update BEFORE UPDATE OF item_id,version_id ON agenda_item_documents
WHEN NOT EXISTS (
 SELECT 1 FROM agenda_items a JOIN meetings m ON m.id=a.meeting_id
 JOIN document_versions v ON v.id=NEW.version_id JOIN documents d ON d.id=v.document_id
 WHERE a.id=NEW.item_id AND m.municipality_id=d.municipality_id
) BEGIN SELECT RAISE(ABORT,'item_document_municipality_mismatch'); END;
CREATE TRIGGER guard_cache_eligible_insert BEFORE INSERT ON cache_records
WHEN NEW.review_eligible_on < (SELECT date(meeting_date,'+90 days') FROM meetings WHERE id=NEW.meeting_id)
BEGIN SELECT RAISE(ABORT,'retention_review_too_early'); END;
CREATE TRIGGER guard_cache_eligible_update BEFORE UPDATE OF review_eligible_on,meeting_id ON cache_records
WHEN NEW.review_eligible_on < (SELECT date(meeting_date,'+90 days') FROM meetings WHERE id=NEW.meeting_id)
BEGIN SELECT RAISE(ABORT,'retention_review_too_early'); END;

-- The migration runner must check PRAGMA foreign_key_check and verify row
-- counts in tests BEFORE remote execution. This statement reports violations
-- but does not itself abort a migration if rows are returned.
