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
                db.executescript((ROOT / "migrations" / "0001_core.sql").read_text())
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

    def test_broken_meeting_date_not_accepted(self):
        html = "<div>City Council - Monday, November 99, 2026</div><a href='https://citywindsor.ca/test.pdf'>Agenda</a>"
        self.assertEqual(discover(html, since="2026-11-01"), [])


if __name__ == "__main__":
    unittest.main()
