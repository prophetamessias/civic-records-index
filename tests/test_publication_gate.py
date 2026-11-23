"""Version-bound publication tests against exact Worker SQL (synthetic only)."""
import re
import sqlite3
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKER = (ROOT / "src" / "worker.mjs").read_text(encoding="utf-8")
MATCH = re.search(r"const PUBLIC_ITEMS_SQL = `(.*?)`;", WORKER, re.DOTALL)
if not MATCH:
    raise RuntimeError("Worker public query not found")
QUERY = MATCH.group(1).replace("?1", "?")
H1 = "a" * 64
H2 = "b" * 64


class PublicGateTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        for name in ("0001_core.sql", "0005_publication_authorizations.sql"):
            self.db.executescript((ROOT / "migrations" / name).read_text())
        self.db.executescript(f"""
            INSERT INTO municipalities(id,name,province,official_homepage)
            VALUES ('w','Windsor','ON','https://citywindsor.ca');
            INSERT INTO meetings(id,municipality_id,body,meeting_date)
            VALUES ('m1','w','Council','2026-11-23');
            INSERT INTO agenda_items(id,meeting_id,item_number,title,disposition,disposition_verified)
            VALUES ('a1','m1','1','Synthetic example','adopted',1);
            INSERT INTO documents(id,municipality_id,document_type,title)
            VALUES ('d1','w','agenda','Synthetic document');
            INSERT INTO document_versions(id,document_id,source_url,source_host,sha256,rights_review,verification_status)
            VALUES ('v1','d1','https://citywindsor.ca/synthetic','citywindsor.ca','{H1}','approved','verified');
            INSERT INTO agenda_item_documents(item_id,version_id,relation_type)
            VALUES ('a1','v1','agenda');
            INSERT INTO publication_reviews(id,item_id,status,reviewer,reviewed_at)
            VALUES ('legacy','a1','approved','old-reviewer','2026-11-22');
        """)

    def tearDown(self):
        self.db.close()

    def published(self):
        return self.db.execute(QUERY, (50,)).fetchall()

    def approve(self, version="v1", sha=H1, authorization="auth1"):
        self.db.execute("""
            INSERT INTO publication_authorizations
            (id,item_id,source_version_id,source_sha256,approved_item_number,
             approved_title,approved_disposition,approved_meeting_body,
             approved_meeting_date,approved_meeting_status,status,reviewer,reviewed_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,'approved','synthetic-reviewer','2026-11-23T10:00:00Z')
        """, (authorization, "a1", version, sha, "1", "Synthetic example",
              "adopted", "Council", "2026-11-23", "scheduled"))

    def test_legacy_review_not_sufficient_and_no_current_denied(self):
        self.assertEqual(self.published(), [])
        with self.assertRaises(sqlite3.IntegrityError):
            self.approve()
        self.db.execute("UPDATE documents SET current_version_id='v1' WHERE id='d1'")
        self.assertEqual(self.published(), [])
        self.approve()
        self.assertEqual(len(self.published()), 1)

    def test_changed_evidence_requires_fresh_authorization(self):
        self.db.execute("UPDATE documents SET current_version_id='v1' WHERE id='d1'")
        self.approve()
        self.db.execute("INSERT INTO document_versions(id,document_id,source_url,source_host,sha256,rights_review,verification_status) VALUES('v2','d1','https://citywindsor.ca/synthetic2','citywindsor.ca',?,'approved','verified')", (H2,))
        self.db.execute("INSERT INTO agenda_item_documents(item_id,version_id,relation_type) VALUES('a1','v2','agenda')")
        self.db.execute("UPDATE documents SET current_version_id='v2' WHERE id='d1'")
        self.assertEqual(self.published(), [])
        with self.assertRaises(sqlite3.IntegrityError):
            self.approve(version="v2",sha=H2,authorization="auth2")
        self.db.execute("UPDATE publication_authorizations SET status='revoked',revoked_by='reviewer',revoked_at='2026-11-24T00:00:00Z' WHERE id='auth1'")
        self.approve(version="v2", sha=H2, authorization="auth2")
        self.assertEqual(len(self.published()), 1)
        self.db.execute("UPDATE document_versions SET rights_review='restricted' WHERE id='v2'")
        self.assertEqual(self.published(), [])

    def test_item_or_meeting_edit_invalidates_snapshot(self):
        self.db.execute("UPDATE documents SET current_version_id='v1' WHERE id='d1'")
        self.approve()
        self.db.execute("UPDATE agenda_items SET title='Corrected item' WHERE id='a1'")
        self.assertEqual(self.published(), [])
        self.db.execute("UPDATE agenda_items SET title='Synthetic example' WHERE id='a1'")
        self.db.execute("UPDATE meetings SET body='Corrected council' WHERE id='m1'")
        self.assertEqual(self.published(), [])

    def test_revocation_is_irreversible_and_cannot_retarget(self):
        self.db.execute("UPDATE documents SET current_version_id='v1' WHERE id='d1'")
        self.approve()
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("UPDATE publication_authorizations SET source_sha256=? WHERE id='auth1'", (H2,))
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("UPDATE publication_authorizations SET status='revoked' WHERE id='auth1'")
        self.db.execute("UPDATE publication_authorizations SET status='revoked', revoked_by='reviewer',revoked_at='2026-11-24' WHERE id='auth1'")
        self.assertEqual(self.published(), [])
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("UPDATE publication_authorizations SET status='approved', revoked_by=NULL, revoked_at=NULL WHERE id='auth1'")
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("DELETE FROM publication_authorizations WHERE id='auth1'")
        self.approve(authorization="auth2")
        self.assertEqual(len(self.published()), 1)

    def test_cancelled_meeting_revokes_and_cannot_resurrect(self):
        self.db.execute("UPDATE documents SET current_version_id='v1' WHERE id='d1'")
        self.approve()
        self.assertEqual(len(self.published()), 1)
        self.db.execute("UPDATE meetings SET status='cancelled' WHERE id='m1'")
        self.assertEqual(self.published(), [])
        self.assertEqual(self.db.execute("SELECT status FROM publication_authorizations WHERE id='auth1'").fetchone()[0], 'revoked')
        self.db.execute("UPDATE meetings SET status='scheduled' WHERE id='m1'")
        self.assertEqual(self.published(), [])

    def test_reverted_title_never_restores_authorization(self):
        self.db.execute("UPDATE documents SET current_version_id='v1' WHERE id='d1'")
        self.approve()
        self.db.execute("UPDATE agenda_items SET title='Corrected' WHERE id='a1'")
        self.db.execute("UPDATE agenda_items SET title='Synthetic example' WHERE id='a1'")
        self.assertEqual(self.published(), [])
        self.assertEqual(self.db.execute("SELECT status FROM publication_authorizations WHERE id='auth1'").fetchone()[0], 'revoked')

    def test_unverified_companion_blocks_publication(self):
        self.db.execute("UPDATE documents SET current_version_id='v1' WHERE id='d1'")
        self.approve()
        self.db.execute("INSERT INTO documents(id,municipality_id,document_type,title) VALUES ('d2','w','attachment','Synthetic companion')")
        self.db.execute("INSERT INTO document_versions(id,document_id,source_url,source_host,sha256,rights_review,verification_status) VALUES ('v2','d2','https://citywindsor.ca/companion','citywindsor.ca',?,'restricted','verified')", (H2,))
        self.db.execute("UPDATE documents SET current_version_id='v2' WHERE id='d2'")
        self.db.execute("INSERT INTO agenda_item_documents(item_id,version_id,relation_type) VALUES ('a1','v2','attachment')")
        self.assertEqual(self.published(), [])
        self.db.execute("UPDATE document_versions SET rights_review='approved' WHERE id='v2'")
        self.assertEqual(len(self.published()), 1)

    def test_unverified_disposition_or_reviewed_rights_fail_closed(self):
        self.db.execute("UPDATE documents SET current_version_id='v1' WHERE id='d1'")
        self.approve()
        self.db.execute("UPDATE agenda_items SET disposition_verified=0 WHERE id='a1'")
        self.assertEqual(self.published(), [])
        self.db.execute("UPDATE agenda_items SET disposition_verified=1 WHERE id='a1'")
        self.db.execute("UPDATE document_versions SET verification_status='changed' WHERE id='v1'")
        self.assertEqual(self.published(), [])


if __name__ == "__main__":
    unittest.main()
