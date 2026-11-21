"""Schema checks using only Python's standard sqlite3 module (compatible with D1 SQL)."""
import sqlite3
import unittest
from pathlib import Path
from datetime import date, timedelta

SCHEMA = (Path(__file__).resolve().parents[1] / "migrations" / "0001_core.sql").read_text()

class SchemaTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.db.executescript(SCHEMA)
        self.db.execute("INSERT INTO municipalities(id,name,province,official_homepage) VALUES('windsor','Windsor','ON','https://www.citywindsor.ca')")
        self.db.execute("INSERT INTO meetings(id,municipality_id,body,meeting_date) VALUES('m1','windsor','City Council','2026-11-23')")
        self.db.execute("INSERT INTO agenda_items(id,meeting_id,item_number,title) VALUES('a1','m1','11.3','Investigator appointment')")
        self.db.execute("INSERT INTO documents(id,municipality_id,document_type,title) VALUES('d1','windsor','agenda','Agenda PDF')")
        self.db.execute("INSERT INTO document_versions(id,document_id,source_url,source_host) VALUES('v1','d1','https://www.citywindsor.ca/agenda.pdf','www.citywindsor.ca')")
    def tearDown(self):
        self.db.close()
    def test_meeting_idempotency(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("INSERT INTO meetings(id,municipality_id,body,meeting_date) VALUES('m2','windsor','City Council','2026-11-23')")
    def test_foreign_keys(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("INSERT INTO agenda_items(id,meeting_id,item_number,title) VALUES('bad','missing','7.1','Bad')")
    def test_claim_needs_reviewer(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("INSERT INTO evidence_claims(id,item_id,claim_text,source_version_id,status) VALUES('e1','a1','Claim','v1','verified')")
    def test_no_assumed_votes(self):
        self.db.execute("INSERT INTO resolutions(id,meeting_id,resolution_number,decision_status,source_version_id) VALUES('r1','m1','CR1','adopted','v1')")
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("INSERT INTO recorded_votes(id,resolution_id,member_name,vote,source_version_id) VALUES('v','r1','Someone','assumed_yes','v1')")
    def test_review_due_not_auto_delete(self):
        due = (date(2026,11,23) + timedelta(days=90)).isoformat()
        self.assertEqual(due, "2027-02-21")
        self.db.execute("INSERT INTO cache_records(id,version_id,meeting_id,storage_provider,storage_locator,cached_at,review_eligible_on) VALUES('c','v1','m1','sharepoint','synthetic','2026-11-23',?)", (due,))
        self.assertEqual(self.db.execute("SELECT status FROM cache_records WHERE id='c'").fetchone()[0], "active")
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("INSERT INTO deletion_reviews(id,cache_id,status) VALUES('x','c','executed')")
    def test_hold_release_requires_identity(self):
        self.db.execute("INSERT INTO cache_records(id,version_id,meeting_id,storage_provider,storage_locator,cached_at,review_eligible_on) VALUES('c','v1','m1','sharepoint','synthetic','2026-11-23','2027-02-21')")
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("INSERT INTO preservation_holds(id,cache_id,reason,created_by,active) VALUES('h','c','active research','reviewer',0)")
    def test_duplicate_agenda_item_rejected(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("INSERT INTO agenda_items(id,meeting_id,item_number,title) VALUES('a2','m1','11.3','Duplicate')")

if __name__ == "__main__":
    unittest.main()
