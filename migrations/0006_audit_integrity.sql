-- 0006: Additional integrity and retention safeguards identified by independent audit.
-- Forward-only, additive; does not grant permission to delete files or publish records.
CREATE TRIGGER IF NOT EXISTS block_cache_hard_delete
BEFORE DELETE ON cache_records
BEGIN SELECT RAISE(ABORT,'cache_hard_delete_disabled'); END;

CREATE TRIGGER IF NOT EXISTS guard_version_document_reassignment
BEFORE UPDATE OF document_id ON document_versions
WHEN NEW.document_id IS NOT OLD.document_id
 AND EXISTS (SELECT 1 FROM documents d WHERE d.current_version_id=OLD.id)
BEGIN SELECT RAISE(ABORT,'version_current_owner_immutable'); END;

CREATE TRIGGER IF NOT EXISTS guard_meeting_date_retention
BEFORE UPDATE OF meeting_date ON meetings
WHEN EXISTS (
  SELECT 1 FROM cache_records c
  WHERE c.meeting_id=OLD.id AND
    c.review_eligible_on < date(NEW.meeting_date,'+90 days')
)
BEGIN SELECT RAISE(ABORT,'meeting_change_would_violate_cache_retention'); END;
