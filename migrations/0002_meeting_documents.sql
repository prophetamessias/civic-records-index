-- Connect official source versions to a meeting (many-to-many).
-- Do not infer a document is a staff report or a decision from its filename.
CREATE TABLE meeting_documents (
    meeting_id TEXT NOT NULL REFERENCES meetings(id),
    version_id TEXT NOT NULL REFERENCES document_versions(id),
    label TEXT NOT NULL,
    discovered_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (meeting_id, version_id)
);
CREATE INDEX idx_meeting_documents_version ON meeting_documents(version_id);
