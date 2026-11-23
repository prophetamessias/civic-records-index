"""Discovery tests: no network calls, synthetic URLs, local-only database."""
import sys
import sqlite3
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from civic_index.windsor import discover, official_url
from civic_index.discovery import apply_to_local_db, main

FIXTURE = ROOT / "tests" / "fixtures" / "windsor-agendas.html"


class WindsorDiscoveryTests(unittest.TestCase):
    def test_meetings_documents_and_date_filter(self):
        records = discover(FIXTURE.read_text(), since="2026-11-01")
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0].meeting_date, "2026-11-25")
        self.assertEqual(records[1].meeting_date, "2026-11-23")
        self.assertEqual(len(records[1].documents), 4)
        self.assertEqual([x.label for x in records[1].documents],
                         ["Agenda", "Consolidated Agenda", "In-Camera Agenda", "Video"])

    def test_reject_external_and_non_https(self):
        self.assertIsNone(official_url("https://evil.example/doc.pdf"))
        self.assertIsNone(official_url("javascript:alert(1)"))
        self.assertIsNone(official_url("http://citywindsor.ca/doc.pdf"))
        self.assertIsNone(official_url("https://citywindsor.ca.evil.example/doc.pdf"))
        self.assertIsNone(official_url("https://username:password@citywindsor.ca/agenda"))
        self.assertEqual(official_url("/documents/TEST-ONLY/file.pdf"),
                         "https://opendata.citywindsor.ca/documents/TEST-ONLY/file.pdf")

    def test_deterministic_idempotent_discovery(self):
        text = FIXTURE.read_text()
        self.assertEqual(discover(text, since="2026-11-01"), discover(text, since="2026-11-01"))

    def test_db_requires_explicit_apply_and_migrations(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test.sqlite"
            with sqlite3.connect(path) as db:
                db.executescript((ROOT / "tests" / "fixtures" / "legacy_0001_core.sql").read_text())
                db.executescript((ROOT / "migrations" / "0002_meeting_documents.sql").read_text())
            records = discover(FIXTURE.read_text(), since="2026-11-01")
            self.assertEqual(len(records), 2)
            first = apply_to_local_db(str(path), records)
            second = apply_to_local_db(str(path), records)
            self.assertEqual(first, {"meetings_new": 2, "documents_new": 5, "links_new": 5})
            self.assertEqual(second, {"meetings_new": 0, "documents_new": 0, "links_new": 0})
            with sqlite3.connect(path) as db:
                self.assertEqual(db.execute("SELECT COUNT(*) FROM document_versions").fetchone()[0], 5)
                self.assertEqual(db.execute("SELECT COUNT(*) FROM job_runs").fetchone()[0], 2)
                self.assertEqual(db.execute("SELECT COUNT(*) FROM publication_reviews").fetchone()[0], 0)
                self.assertEqual(db.execute("SELECT COUNT(*) FROM deletion_reviews").fetchone()[0], 0)
                self.assertEqual(db.execute("SELECT DISTINCT verification_status FROM document_versions").fetchone()[0], "unverified")

    def test_dry_run_does_not_create_database(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "not-created.sqlite"
            self.assertEqual(main(["--fixture", str(FIXTURE), "--since", "2026-11-01", "--db", str(db_path)]), 0)
            self.assertFalse(db_path.exists())

    def test_duplicate_same_day_heading_fails_closed(self):
        html = ("<div>City Council - Monday, November 23, 2026</div>"
                "<a href='https://citywindsor.ca/a.pdf'>Agenda</a>"
                "<div>City Council - Monday, November 23, 2026</div>"
                "<a href='https://citywindsor.ca/b.pdf'>Agenda</a>")
        with self.assertRaisesRegex(ValueError, "Ambiguous repeated meeting heading"):
            discover(html, since="2026-11-01")

    def test_fresh_corrected_schema_supports_discovery(self):
        """Corrected 0001 plus 0002/0003/0004 must support the discovery importer."""
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "corrected.sqlite"
            with sqlite3.connect(db_path) as db:
                for filename in ("0001_core.sql", "0002_meeting_documents.sql",
                                 "0003_integrity_guards.sql", "0004_meetings_identity.sql"):
                    sql = (ROOT / "migrations" / filename).read_text()
                    if filename == "0004_meetings_identity.sql":
                        db.executescript("BEGIN;\n" + sql + "\nCOMMIT;")
                    else:
                        db.executescript(sql)
                self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(), [])
            records = discover(FIXTURE.read_text(), since="2026-11-01")
            first = apply_to_local_db(str(db_path), records)
            again = apply_to_local_db(str(db_path), records)
            self.assertEqual(first, {"meetings_new": 2, "documents_new": 5, "links_new": 5})
            self.assertEqual(again, {"meetings_new": 0, "documents_new": 0, "links_new": 0})
            with sqlite3.connect(db_path) as db:
                self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(), [])
                self.assertEqual(db.execute("SELECT COUNT(*) FROM meetings").fetchone()[0], 2)

    def test_existing_d1_schema_additive_upgrade(self):
        with sqlite3.connect(":memory:") as db:
            db.executescript((ROOT / "tests" / "fixtures" / "legacy_0001_core.sql").read_text())
            db.executescript((ROOT / "migrations" / "0002_meeting_documents.sql").read_text())
            upgrade = (ROOT / "migrations" / "0003_integrity_guards.sql").read_text()
            db.executescript(upgrade)
            # A repeated migration does not recreate triggers or indexes.
            db.executescript(upgrade)
            db.execute("INSERT INTO municipalities(id,name,province,official_homepage) VALUES('w','Windsor','ON','https://citywindsor.ca')")
            db.execute("INSERT INTO meetings(id,municipality_id,body,meeting_date) VALUES('m','w','Council','2026-11-23')")
            db.execute("INSERT INTO documents(id,municipality_id,document_type,title) VALUES('d','w','agenda','Agenda')")
            db.execute("INSERT INTO document_versions(id,document_id,source_url,source_host) VALUES('v','d','https://citywindsor.ca/a','citywindsor.ca')")
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute("INSERT INTO document_versions(id,document_id,source_url,source_host) VALUES('v2','d','https://citywindsor.ca/a','citywindsor.ca')")
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute("INSERT INTO cache_records(id,version_id,meeting_id,storage_provider,storage_locator,cached_at,review_eligible_on) VALUES('c','v','m','local','test','2026-11-23','2026-11-24')")
            db.execute("INSERT INTO cache_records(id,version_id,meeting_id,storage_provider,storage_locator,cached_at,review_eligible_on) VALUES('c','v','m','local','test','2026-11-23','2027-02-21')")
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute("INSERT INTO deletion_reviews(id,cache_id,status,reviewer,reviewed_at) VALUES('x','c','approved','reviewer','2027-02-21')")
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute("UPDATE cache_records SET status='deleted' WHERE id='c'")

    def test_meeting_identity_rebuild_preserves_references(self):
        """Legacy 0001+0002 -> additive 0003 -> transactional 0004 with live-like rows."""
        with sqlite3.connect(":memory:") as db:
            db.executescript((ROOT / "tests" / "fixtures" / "legacy_0001_core.sql").read_text())
            db.executescript((ROOT / "migrations" / "0002_meeting_documents.sql").read_text())
            db.executescript((ROOT / "migrations" / "0003_integrity_guards.sql").read_text())
            db.execute("INSERT INTO municipalities(id,name,province,official_homepage) VALUES ('w','Windsor','ON','https://citywindsor.ca')")
            db.execute("INSERT INTO meetings(id,municipality_id,body,meeting_date) VALUES ('m1','w','Council','2026-11-23')")
            db.execute("INSERT INTO agenda_items(id,meeting_id,item_number,title) VALUES ('a1','m1','1','Item')")
            db.execute("INSERT INTO documents(id,municipality_id,document_type,title) VALUES ('d1','w','agenda','Agenda')")
            db.execute("INSERT INTO document_versions(id,document_id,source_url,source_host) VALUES ('v1','d1','https://citywindsor.ca/a','citywindsor.ca')")
            db.execute("INSERT INTO meeting_documents(meeting_id,version_id,label) VALUES ('m1','v1','Agenda')")
            db.execute("INSERT INTO resolutions(id,meeting_id,item_id,resolution_number,decision_status,source_version_id) VALUES ('r1','m1','a1','CR1','proposed','v1')")
            db.execute("INSERT INTO cache_records(id,meeting_id,version_id,storage_provider,storage_locator,cached_at,review_eligible_on) VALUES ('c1','m1','v1','local','synthetic','2026-11-23','2027-02-21')")
            original = {table: db.execute("SELECT COUNT(*) FROM " + table).fetchone()[0]
                        for table in ("meetings","agenda_items","resolutions","meeting_documents","cache_records")}
            migration = (ROOT / "migrations" / "0004_meetings_identity.sql").read_text()
            # executescript commits an existing transaction, so explicitly
            # wrap the statements in one local test transaction.
            db.executescript("BEGIN;\n" + migration + "\nCOMMIT;")
            self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(), [])
            for table, n in original.items():
                self.assertEqual(db.execute("SELECT COUNT(*) FROM " + table).fetchone()[0], n, table)
            self.assertEqual(db.execute("SELECT meeting_id FROM agenda_items WHERE id='a1'").fetchone(), ("m1",))
            self.assertEqual(db.execute("SELECT meeting_id FROM resolutions WHERE id='r1'").fetchone(), ("m1",))
            self.assertEqual(db.execute("SELECT meeting_id FROM meeting_documents WHERE version_id='v1'").fetchone(), ("m1",))
            self.assertEqual(db.execute("SELECT meeting_id FROM cache_records WHERE id='c1'").fetchone(), ("m1",))
            db.execute("INSERT INTO meetings(id,municipality_id,body,meeting_date) VALUES ('m2','w','Council','2026-11-23')")
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute("INSERT INTO meetings(id,municipality_id,body,meeting_date) VALUES ('m2','w','Council','2026-11-23')")
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute("INSERT INTO cache_records(id,meeting_id,version_id,storage_provider,storage_locator,cached_at,review_eligible_on) VALUES ('c2','m1','v1','local','s2','2026-11-23','2026-11-24')")
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute("UPDATE cache_records SET status='deleted' WHERE id='c1'")

    def test_broken_meeting_date_not_accepted(self):
        html = "<div>City Council - Monday, November 99, 2026</div><a href='https://citywindsor.ca/test.pdf'>Agenda</a>"
        self.assertEqual(discover(html, since="2026-11-01"), [])


if __name__ == "__main__":
    unittest.main()
