-- 0003: additive integrity hardening for D1 databases previously provisioned
-- using the original 0001 + 0002 migrations. Do NOT apply automatically.
-- Preflight: verify the old D1 schema, check duplicate unhashed versions,
-- reconcile migration ledger and snapshot the dev D1 before any remote apply.
-- Existing meetings UNIQUE(municipality_id,body,meeting_date) remains in place.
-- Removing it needs a separately reviewed FK-preserving table rebuild.
CREATE INDEX IF NOT EXISTS idx_meetings_body_day ON meetings(municipality_id, body, meeting_date);
-- An un-hashed source observation may be recorded only once per document + URL.
CREATE UNIQUE INDEX IF NOT EXISTS uq_version_unhashed_source ON document_versions(document_id,source_url) WHERE sha256 IS NULL;
-- Prevent a document's current pointer from selecting another document's version.
CREATE TRIGGER IF NOT EXISTS guard_document_current_insert BEFORE INSERT ON documents
WHEN NEW.current_version_id IS NOT NULL AND NOT EXISTS (
  SELECT 1 FROM document_versions v WHERE v.id=NEW.current_version_id AND v.document_id=NEW.id
) BEGIN SELECT RAISE(ABORT,'current_version_not_owned'); END;
CREATE TRIGGER IF NOT EXISTS guard_document_current_update BEFORE UPDATE OF current_version_id ON documents
WHEN NEW.current_version_id IS NOT NULL AND NOT EXISTS (
  SELECT 1 FROM document_versions v WHERE v.id=NEW.current_version_id AND v.document_id=NEW.id
) BEGIN SELECT RAISE(ABORT,'current_version_not_owned'); END;
-- Resolution must reference an agenda item from the same meeting.
CREATE TRIGGER IF NOT EXISTS guard_resolution_item_insert BEFORE INSERT ON resolutions
WHEN NEW.item_id IS NOT NULL AND NOT EXISTS (
  SELECT 1 FROM agenda_items a WHERE a.id=NEW.item_id AND a.meeting_id=NEW.meeting_id
) BEGIN SELECT RAISE(ABORT,'resolution_item_meeting_mismatch'); END;
CREATE TRIGGER IF NOT EXISTS guard_resolution_item_update BEFORE UPDATE OF item_id,meeting_id ON resolutions
WHEN NEW.item_id IS NOT NULL AND NOT EXISTS (
  SELECT 1 FROM agenda_items a WHERE a.id=NEW.item_id AND a.meeting_id=NEW.meeting_id
) BEGIN SELECT RAISE(ABORT,'resolution_item_meeting_mismatch'); END;
-- Documents connected to agenda items must belong to the same municipality.
CREATE TRIGGER IF NOT EXISTS guard_item_document_insert BEFORE INSERT ON agenda_item_documents
WHEN NOT EXISTS (
 SELECT 1 FROM agenda_items a JOIN meetings m ON m.id=a.meeting_id
 JOIN document_versions v ON v.id=NEW.version_id JOIN documents d ON d.id=v.document_id
 WHERE a.id=NEW.item_id AND m.municipality_id=d.municipality_id
) BEGIN SELECT RAISE(ABORT,'item_document_municipality_mismatch'); END;
CREATE TRIGGER IF NOT EXISTS guard_item_document_update BEFORE UPDATE OF item_id,version_id ON agenda_item_documents
WHEN NOT EXISTS (
 SELECT 1 FROM agenda_items a JOIN meetings m ON m.id=a.meeting_id
 JOIN document_versions v ON v.id=NEW.version_id JOIN documents d ON d.id=v.document_id
 WHERE a.id=NEW.item_id AND m.municipality_id=d.municipality_id
) BEGIN SELECT RAISE(ABORT,'item_document_municipality_mismatch'); END;
-- Polymorphic relationship targets must exist, on creation and mutation.
CREATE TRIGGER IF NOT EXISTS guard_relationship_insert BEFORE INSERT ON record_relationships
WHEN NOT (
  (NEW.from_type='agenda_item' AND EXISTS(SELECT 1 FROM agenda_items WHERE id=NEW.from_id)) OR
  (NEW.from_type='resolution' AND EXISTS(SELECT 1 FROM resolutions WHERE id=NEW.from_id)) OR
  (NEW.from_type='document' AND EXISTS(SELECT 1 FROM documents WHERE id=NEW.from_id))
) OR NOT (
  (NEW.to_type='agenda_item' AND EXISTS(SELECT 1 FROM agenda_items WHERE id=NEW.to_id)) OR
  (NEW.to_type='resolution' AND EXISTS(SELECT 1 FROM resolutions WHERE id=NEW.to_id)) OR
  (NEW.to_type='document' AND EXISTS(SELECT 1 FROM documents WHERE id=NEW.to_id))
) BEGIN SELECT RAISE(ABORT,'relationship_target_missing'); END;
CREATE TRIGGER IF NOT EXISTS guard_relationship_update BEFORE UPDATE OF from_type,from_id,to_type,to_id ON record_relationships
WHEN NOT (
  (NEW.from_type='agenda_item' AND EXISTS(SELECT 1 FROM agenda_items WHERE id=NEW.from_id)) OR
  (NEW.from_type='resolution' AND EXISTS(SELECT 1 FROM resolutions WHERE id=NEW.from_id)) OR
  (NEW.from_type='document' AND EXISTS(SELECT 1 FROM documents WHERE id=NEW.from_id))
) OR NOT (
  (NEW.to_type='agenda_item' AND EXISTS(SELECT 1 FROM agenda_items WHERE id=NEW.to_id)) OR
  (NEW.to_type='resolution' AND EXISTS(SELECT 1 FROM resolutions WHERE id=NEW.to_id)) OR
  (NEW.to_type='document' AND EXISTS(SELECT 1 FROM documents WHERE id=NEW.to_id))
) BEGIN SELECT RAISE(ABORT,'relationship_target_missing'); END;
-- Cache eligibility may not precede 90 calendar days after its meeting.
CREATE TRIGGER IF NOT EXISTS guard_cache_eligible_insert BEFORE INSERT ON cache_records
WHEN NEW.review_eligible_on < (SELECT date(meeting_date,'+90 days') FROM meetings WHERE id=NEW.meeting_id)
BEGIN SELECT RAISE(ABORT,'retention_review_too_early'); END;
CREATE TRIGGER IF NOT EXISTS guard_cache_eligible_update BEFORE UPDATE OF review_eligible_on,meeting_id ON cache_records
WHEN NEW.review_eligible_on < (SELECT date(meeting_date,'+90 days') FROM meetings WHERE id=NEW.meeting_id)
BEGIN SELECT RAISE(ABORT,'retention_review_too_early'); END;
-- No deletion workflow is implemented or authorized. Refuse approval/execution
-- even if a caller supplies forged review identities and timestamps.
CREATE TRIGGER IF NOT EXISTS block_deletion_review_insert BEFORE INSERT ON deletion_reviews
WHEN NEW.status IN ('approved','executed')
BEGIN SELECT RAISE(ABORT,'deletion_workflow_disabled'); END;
CREATE TRIGGER IF NOT EXISTS block_deletion_review_update BEFORE UPDATE OF status ON deletion_reviews
WHEN NEW.status IN ('approved','executed')
BEGIN SELECT RAISE(ABORT,'deletion_workflow_disabled'); END;
CREATE TRIGGER IF NOT EXISTS block_cache_deleted_insert BEFORE INSERT ON cache_records
WHEN NEW.status='deleted' OR NEW.deleted_at IS NOT NULL
BEGIN SELECT RAISE(ABORT,'deletion_workflow_disabled'); END;
CREATE TRIGGER IF NOT EXISTS block_cache_deleted_update BEFORE UPDATE OF status,deleted_at ON cache_records
WHEN NEW.status='deleted' OR NEW.deleted_at IS NOT NULL
BEGIN SELECT RAISE(ABORT,'deletion_workflow_disabled'); END;
