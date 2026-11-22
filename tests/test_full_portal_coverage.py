"""Expanded portal coverage: all listed meeting bodies; synthetic fixtures only."""
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from civic_index.windsor import discover, official_url
from civic_index.discovery import apply_to_local_db

SAMPLE = """<html><main>
<div>Environment, Transportation &amp; Public Safety Standing Committee Sitting as the Transit Windsor Board of Directors - Wednesday, September 23, 2026</div>
<a href="https://www.citywindsor.ca/documents/TEST-ONLY/transit.pdf">Agenda</a>
<a href="https://csg001-harmony.sliq.net/TEST-ONLY/video">Video</a>
<div>Community Services Standing Committee - CANCELLED - Wednesday, November 04, 2026</div>
<div>Meeting Cancelled</div>
<div>Development &amp; Heritage Standing Committee - Special Meeting - Monday, November 09, 2026</div>
<a href="https://www.citywindsor.ca/documents/TEST-ONLY/dev.pdf">Consolidated Agenda</a>
<a href="https://www.citywindsor.ca/documents/TEST-ONLY/appendix-c.pdf">Item 10.1 - Appendix C</a>
<a href="https://www.citywindsor.ca/documents/TEST-ONLY/letter.pdf">Item 10.1 - Written Submission - Public Comment</a>
<div>Inaugural Meeting of Council - Monday, November 16, 2026</div>
<a href="https://www.citywindsor.ca/documents/TEST-ONLY/inaugural.pdf">Minutes</a>
<div>Special Meeting of Council - Orientation - Finance &amp; Budget 101 - Thursday, November 19, 2026</div>
<a href="https://www.citywindsor.ca/documents/TEST-ONLY/orientation.pdf">Agenda</a>
</main></html>"""

class ExpandedCoverageTests(unittest.TestCase):
    def test_all_published_meeting_bodies_and_materials(self):
        result = discover(SAMPLE, since="2026-01-01")
        self.assertEqual(len(result), 5)
        self.assertTrue(any("Transit Windsor Board" in x.body for x in result))
        self.assertTrue(any("Orientation - Finance" in x.body for x in result))
        cancelled = next(x for x in result if "Community Services" in x.body)
        self.assertEqual(cancelled.status, "cancelled")
        self.assertEqual(cancelled.documents, ())
        dev = next(x for x in result if "Development" in x.body)
        self.assertEqual(len(dev.documents), 3)
        self.assertTrue(any(d.label.startswith("Item 10.1") for d in dev.documents))
        transit = result[0]
        self.assertEqual(len(transit.documents), 2)
        self.assertEqual(transit.documents[1].label, "Video")
    def test_limits_fail_closed_instead_of_truncating(self):
        dates = [f"<div>City Council Session {n} - Monday, November 23, 2026</div>"
                 for n in range(121)]
        with self.assertRaisesRegex(ValueError, "Meeting discovery limit exceeded"):
            discover("".join(dates), since="2026-01-01")
        links = "".join(
            f'<a href="https://www.citywindsor.ca/documents/TEST-ONLY/a{n}.pdf">Agenda</a>'
            for n in range(41))
        html = "<div>City Council - Monday, November 23, 2026</div>" + links
        with self.assertRaisesRegex(ValueError, "Meeting document discovery limit exceeded"):
            discover(html, since="2026-01-01")
    def test_numbered_in_camera_agenda_sessions_preserved(self):
        html = """<div>City Council - Monday, July 27, 2026</div>
        <a href="https://www.citywindsor.ca/documents/TEST-ONLY/one.pdf">In-Camera Agenda (Session 1)</a>
        <a href="https://www.citywindsor.ca/documents/TEST-ONLY/two.pdf">In-Camera Agenda (Session 2)</a>"""
        meetings = discover(html, since="2026-01-01")
        self.assertEqual(len(meetings), 1)
        self.assertEqual([d.label for d in meetings[0].documents],
                         ["In-Camera Agenda (Session 1)", "In-Camera Agenda (Session 2)"])
    def test_video_host_is_exact_allowlist(self):
        self.assertIsNotNone(official_url("https://csg001-harmony.sliq.net/TEST-ONLY/video"))
        self.assertIsNone(official_url("https://fake-csg001-harmony.sliq.net/TEST-ONLY/video"))
        self.assertIsNone(official_url("https://csg001-harmony.sliq.net.evil.test/vid"))
    def test_cancelled_meetings_are_saved_and_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"index.sqlite"
            with sqlite3.connect(p) as db:
                db.executescript((ROOT/"migrations/0001_core.sql").read_text())
                db.executescript((ROOT/"migrations/0002_meeting_documents.sql").read_text())
            records=discover(SAMPLE,since="2026-01-01")
            first=apply_to_local_db(str(p),records)
            second=apply_to_local_db(str(p),records)
            self.assertEqual(first["meetings_new"],5)
            self.assertEqual(second["meetings_new"],0)
            with sqlite3.connect(p) as db:
                self.assertEqual(db.execute("SELECT status FROM meetings WHERE body LIKE 'Community Services%'").fetchone()[0],"cancelled")
                self.assertEqual(db.execute("SELECT COUNT(*) FROM meeting_documents").fetchone()[0],7)

if __name__=="__main__":
    unittest.main()
