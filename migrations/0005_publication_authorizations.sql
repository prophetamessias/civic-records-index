-- 0005: Version-bound, revocable publication authorization.
-- A publication decision is a review of an exact item snapshot and current
-- evidence version, not a blanket standing approval of an item.
-- Applied ONLY after migration-ledger reconciliation and independent review.
CREATE TABLE publication_authorizations (
  id TEXT PRIMARY KEY,
  item_id TEXT NOT NULL REFERENCES agenda_items(id),
  source_version_id TEXT NOT NULL REFERENCES document_versions(id),
  source_sha256 TEXT NOT NULL CHECK(length(source_sha256)=64),
  approved_item_number TEXT NOT NULL,
  approved_title TEXT NOT NULL,
  approved_disposition TEXT NOT NULL,
  approved_meeting_body TEXT NOT NULL,
  approved_meeting_date TEXT NOT NULL,
  approved_meeting_status TEXT NOT NULL CHECK(approved_meeting_status IN ('scheduled','completed')),
  status TEXT NOT NULL CHECK(status IN('approved','revoked')),
  reviewer TEXT NOT NULL CHECK(length(trim(reviewer))>0),
  reviewed_at TEXT NOT NULL CHECK(length(trim(reviewed_at))>0),
  revoked_by TEXT,
  revoked_at TEXT,
  CHECK((status='approved' AND revoked_by IS NULL AND revoked_at IS NULL)
     OR (status='revoked' AND revoked_by IS NOT NULL AND revoked_at IS NOT NULL))
);
CREATE UNIQUE INDEX uq_active_publication_item
  ON publication_authorizations(item_id) WHERE status='approved';
CREATE INDEX idx_publication_auth_source ON publication_authorizations(source_version_id,status);
CREATE TRIGGER guard_publication_auth_insert BEFORE INSERT ON publication_authorizations
WHEN NEW.status != 'approved' OR NOT EXISTS (
  SELECT 1 FROM agenda_items ai
  JOIN meetings m ON m.id=ai.meeting_id
  JOIN agenda_item_documents aid ON aid.item_id=ai.id
  JOIN document_versions dv ON dv.id=aid.version_id
  JOIN documents d ON d.id=dv.document_id
  WHERE ai.id=NEW.item_id AND dv.id=NEW.source_version_id
    AND d.current_version_id=dv.id AND dv.sha256=NEW.source_sha256
    AND dv.verification_status='verified' AND dv.rights_review='approved'
    AND ai.disposition_verified=1
    AND ai.item_number=NEW.approved_item_number AND ai.title=NEW.approved_title
    AND ai.disposition=NEW.approved_disposition
    AND m.body=NEW.approved_meeting_body AND m.meeting_date=NEW.approved_meeting_date
    AND m.status=NEW.approved_meeting_status
) BEGIN SELECT RAISE(ABORT,'publication_snapshot_not_verified'); END;
-- Authorization cannot be retargeted or revived; only revocation is allowed.
CREATE TRIGGER guard_publication_auth_update BEFORE UPDATE ON publication_authorizations
WHEN NOT (
  OLD.status='approved' AND NEW.status='revoked'
  AND NEW.revoked_by IS NOT NULL AND length(trim(NEW.revoked_by))>0
  AND NEW.revoked_at IS NOT NULL AND length(trim(NEW.revoked_at))>0
  AND NEW.id=OLD.id AND NEW.item_id=OLD.item_id
  AND NEW.source_version_id=OLD.source_version_id
  AND NEW.source_sha256=OLD.source_sha256
  AND NEW.approved_item_number=OLD.approved_item_number
  AND NEW.approved_title=OLD.approved_title
  AND NEW.approved_disposition=OLD.approved_disposition
  AND NEW.approved_meeting_body=OLD.approved_meeting_body
  AND NEW.approved_meeting_date=OLD.approved_meeting_date
  AND NEW.approved_meeting_status=OLD.approved_meeting_status
  AND NEW.reviewer=OLD.reviewer AND NEW.reviewed_at=OLD.reviewed_at
) BEGIN SELECT RAISE(ABORT,'publication_authorization_immutable'); END;

-- Retain approval/revocation history; cleanup must never erase the audit trail.
CREATE TRIGGER guard_publication_auth_delete BEFORE DELETE ON publication_authorizations
BEGIN SELECT RAISE(ABORT,'publication_authorization_history_immutable'); END;

-- On any reviewed-item correction, permanently invalidate prior approvals.
CREATE TRIGGER revoke_publication_item_change AFTER UPDATE OF
  item_number,title,disposition,disposition_verified,meeting_id ON agenda_items
WHEN OLD.item_number IS NOT NEW.item_number OR OLD.title IS NOT NEW.title
  OR OLD.disposition IS NOT NEW.disposition
  OR OLD.disposition_verified IS NOT NEW.disposition_verified
  OR OLD.meeting_id IS NOT NEW.meeting_id
BEGIN
  UPDATE publication_authorizations
  SET status='revoked',revoked_by='system_item_mutation',revoked_at=CURRENT_TIMESTAMP
  WHERE item_id=OLD.id AND status='approved';
END;
-- If a meeting changes or is cancelled, its previous approvals never revive.
CREATE TRIGGER revoke_publication_meeting_change AFTER UPDATE OF
  body,meeting_date,status,municipality_id ON meetings
WHEN OLD.body IS NOT NEW.body OR OLD.meeting_date IS NOT NEW.meeting_date
  OR OLD.status IS NOT NEW.status OR OLD.municipality_id IS NOT NEW.municipality_id
BEGIN
  UPDATE publication_authorizations
  SET status='revoked',revoked_by='system_meeting_mutation',revoked_at=CURRENT_TIMESTAMP
  WHERE item_id IN (SELECT id FROM agenda_items WHERE meeting_id=OLD.id)
    AND status='approved';
END;
