"""Windsor discovery CLI. Default mode: read-only JSON output.

Run with --fixture for offline development. --apply requires explicit --db
and an initialized migration database; no remote D1 writes are implemented.
"""
from __future__ import annotations
import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
from .windsor import PORTAL_URL, MAX_HTML_BYTES, discover, to_jsonable, stable_id


def fetch_html() -> str:
    req = Request(PORTAL_URL, headers={"User-Agent": "CivicRecordsIndex/0.1 (+https://github.com/prophetamessias/civic-records-index)", "Accept": "text/html"})
    with urlopen(req, timeout=15) as resp:
        if resp.url.split("?", 1)[0] != PORTAL_URL:
            raise ValueError("Unexpected source redirect")
        if "text/html" not in resp.headers.get("Content-Type", "").lower():
            raise ValueError("Unexpected source content type")
        data = resp.read(MAX_HTML_BYTES + 1)
        if len(data) > MAX_HTML_BYTES:
            raise ValueError("Source exceeds bounded HTML size")
        return data.decode("utf-8", errors="replace")


def apply_to_local_db(db_path: str, meetings: list) -> dict[str, int]:
    """Explicit local SQLite insert; idempotent, no updates to meeting outcomes."""
    counts = {"meetings_new": 0, "documents_new": 0, "links_new": 0}
    with sqlite3.connect(db_path) as db:
        db.execute("PRAGMA foreign_keys=ON")
        expected = {"municipalities", "meetings", "documents", "document_versions", "meeting_documents", "job_runs"}
        actual = {x[0] for x in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if not expected.issubset(actual):
            raise ValueError("Database migrations 0001 and 0002 must be applied first")
        db.execute("INSERT OR IGNORE INTO municipalities(id,name,province,country,official_homepage) VALUES ('windsor','Windsor','ON','CA','https://www.citywindsor.ca')")
        now = datetime.now(timezone.utc).isoformat()
        run_id = stable_id("job", now, str(len(meetings)))
        for meeting in meetings:
            cur = db.execute(
                "INSERT OR IGNORE INTO meetings(id,municipality_id,body,meeting_date,status,official_url) VALUES (?,?,?,?,?,?)",
                (meeting.meeting_id, "windsor", meeting.body, meeting.meeting_date, "unknown", PORTAL_URL),
            )
            counts["meetings_new"] += cur.rowcount
            for document in meeting.documents:
                cur = db.execute(
                    "INSERT OR IGNORE INTO documents(id,municipality_id,document_type,title) VALUES (?,?,?,?)",
                    (document.record_id, "windsor", "meeting_material", document.label),
                )
                counts["documents_new"] += cur.rowcount
                vid = stable_id("version", document.record_id, document.url)
                db.execute(
                    "INSERT OR IGNORE INTO document_versions(id,document_id,source_url,source_host,verification_status,rights_review) VALUES (?,?,?,?,?,?)",
                    (vid, document.record_id, document.url, urlsplit(document.url).hostname, "unverified", "pending"),
                )
                cur = db.execute(
                    "INSERT OR IGNORE INTO meeting_documents(meeting_id,version_id,label) VALUES (?,?,?)",
                    (meeting.meeting_id, vid, document.label),
                )
                counts["links_new"] += cur.rowcount
        db.execute(
            "INSERT INTO job_runs(id,kind,trigger_type,status,started_at,finished_at,input_count,output_count) VALUES (?,?,?,?,?,?,?,?)",
            (run_id, "source_discovery", "manual", "succeeded", now, now, len(meetings),
             sum(len(m.documents) for m in meetings)),
        )
    return counts


def main(argv=None):
    ap = argparse.ArgumentParser(description="Read-only Windsor public agenda index discovery")
    ap.add_argument("--fixture", type=Path, help="Offline HTML fixture, no HTTP requests")
    ap.add_argument("--since", default=(datetime.now(timezone.utc).date() - timedelta(days=45)).isoformat(), help="Inclusive YYYY-MM-DD earliest meeting (default: past 45 days)")
    ap.add_argument("--apply", action="store_true", help="Explicit local-only database write")
    ap.add_argument("--db", help="Path to initialized local SQLite database (required for --apply)")
    args = ap.parse_args(argv)
    if args.apply and not args.db:
        ap.error("--apply requires --db")
    try:
        html = args.fixture.read_text(encoding="utf-8") if args.fixture else fetch_html()
        if len(html.encode("utf-8")) > MAX_HTML_BYTES:
            raise ValueError("Source exceeds HTML size limit")
        meetings = discover(html, since=args.since)
        result = {"mode": "local_write" if args.apply else "dry_run", "source": PORTAL_URL,
                  "meetings_found": len(meetings),
                  "documents_found": sum(len(m.documents) for m in meetings),
                  "meetings": to_jsonable(meetings)}
        if args.apply:
            result["local_write"] = apply_to_local_db(args.db, meetings)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, sqlite3.Error) as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
