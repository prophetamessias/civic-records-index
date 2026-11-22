"""Executable publication-gate regression against actual Worker SQL.

Synthetic database only; no network, API key, paid inference, or live content.
"""
import re
import sqlite3
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKER = (ROOT / "src" / "worker.mjs").read_text(encoding="utf-8")
QUERY_MATCH = re.search(r"const PUBLIC_ITEMS_SQL = `(.*?)`;", WORKER, re.DOTALL)
if not QUERY_MATCH:
    raise RuntimeError("Worker public query not found")
QUERY = QUERY_MATCH.group(1).replace("?1", "?")


class PublicGateTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.db.executescript((ROOT / "migrations" / "0001_core.sql").read_text())
        self.db.executescript("""
          INSERT INTO municipalities(id,name,province,official_homepage) VALUES ('w','Windsor','ON','https://www.citywindsor.ca');
          INSERT INTO meetings(id,municipality_id,body,meeting_date) VALUES ('m1','w','Council','2026-11-23');
          INSERT INTO agenda_items(id,meeting_id,item_number,title,disposition,disposition_verified)
          VALUES ('a1','m1','1','Synthetic example','adopted',1);
          INSERT INTO documents(id,municipality_id,document_type,title) VALUES ('d1','w','agenda','Synthetic document');
          INSERT INTO document_versions(id,document_id,source_url,source_host,sha256,retrieved_at,rights_review,verification_status)
          VALUES ('v1','d1','https://www.citywindsor.ca/synthetic1','www.citywindsor.ca',
                  'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
                  '2026-11-22T00:00:00Z','approved','verified');
          INSERT INTO agenda_item_documents(item_id,version_id,relation_type) VALUES ('a1','v1','agenda');
          INSERT INTO publication_reviews(id,item_id,status,reviewer,reviewed_at)
          VALUES ('p1','a1','approved','synthetic-reviewer','2026-11-22T12:00:00Z');
        """)

    def tearDown(self):
        self.db.close()

    def published(self):
        return self.db.execute(QUERY, (50,)).fetchall()

    def test_unset_current_version_blocks_publication(self):
        self.assertEqual(self.published(), [])
        self.db.execute("UPDATE documents SET current_version_id='v1' WHERE id='d1'")
        self.assertEqual(len(self.published()), 1)

    def test_superseded_version_is_not_sufficient(self):
        self.db.execute("UPDATE documents SET current_version_id='v1' WHERE id='d1'")
        self.db.execute("""
          INSERT INTO document_versions(id,document_id,source_url,source_host,sha256,retrieved_at)
          VALUES ('v2','d1','https://www.citywindsor.ca/synthetic2','www.citywindsor.ca',
          'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb','2026-11-23T00:00:00Z')
        """)
        self.db.execute("UPDATE documents SET current_version_id='v2' WHERE id='d1'")
        self.assertEqual(self.published(), [])
        self.db.execute("INSERT INTO agenda_item_documents(item_id,version_id,relation_type) VALUES ('a1','v2','agenda')")
        self.db.execute("UPDATE document_versions SET verification_status='verified', rights_review='approved' WHERE id='v2'")
        self.assertEqual(len(self.published()), 1)
        self.db.execute("UPDATE document_versions SET rights_review='restricted' WHERE id='v2'")
        self.assertEqual(self.published(), [])

    def test_publication_needs_review_and_verified_disposition(self):
        self.db.execute("UPDATE documents SET current_version_id='v1' WHERE id='d1'")
        self.db.execute("UPDATE agenda_items SET disposition_verified=0 WHERE id='a1'")
        self.assertEqual(self.published(), [])
        self.db.execute("UPDATE agenda_items SET disposition_verified=1 WHERE id='a1'")
        self.db.execute("UPDATE publication_reviews SET status='rejected' WHERE id='p1'")
        self.assertEqual(self.published(), [])


if __name__ == "__main__":
    unittest.main()
