"""Regression tests for independent security audit integrity findings."""
import sqlite3
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class AuditIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.db=sqlite3.connect(":memory:")
        for name in ("0001_core.sql","0006_audit_integrity.sql"):
            self.db.executescript((ROOT/"migrations"/name).read_text())
        self.db.executescript("""
          INSERT INTO municipalities(id,name,province,official_homepage)
          VALUES('w','Windsor','ON','https://citywindsor.ca');
          INSERT INTO meetings(id,municipality_id,body,meeting_date)
          VALUES('m','w','Council','2026-11-23');
          INSERT INTO documents(id,municipality_id,document_type,title)
          VALUES('d','w','agenda','Synthetic');
          INSERT INTO document_versions(id,document_id,source_url,source_host)
          VALUES('v','d','https://citywindsor.ca/synthetic','citywindsor.ca');
          UPDATE documents SET current_version_id='v' WHERE id='d';
          INSERT INTO cache_records(id,version_id,meeting_id,storage_provider,
            storage_locator,cached_at,review_eligible_on)
          VALUES('c','v','m','local','synthetic','2026-11-23','2027-02-21');
        """)

    def tearDown(self):
        self.db.close()

    def test_cache_hard_delete_denied(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("DELETE FROM cache_records WHERE id='c'")

    def test_current_version_document_reassignment_denied(self):
        self.db.execute("INSERT INTO documents(id,municipality_id,document_type,title) VALUES('d2','w','attachment','Other')")
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("UPDATE document_versions SET document_id='d2' WHERE id='v'")
        self.assertEqual(self.db.execute("PRAGMA foreign_key_check").fetchall(), [])

    def test_meeting_date_update_cannot_shortcut_retention(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("UPDATE meetings SET meeting_date='2027-11-23' WHERE id='m'")
        self.db.execute("UPDATE meetings SET meeting_date='2026-11-22' WHERE id='m'")
        self.assertEqual(self.db.execute("PRAGMA foreign_key_check").fetchall(), [])

if __name__ == "__main__":
    unittest.main()
