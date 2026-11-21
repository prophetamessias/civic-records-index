"""Read-only Windsor official agenda-page discovery.

Parses a bounded official HTML index; NEVER downloads linked files.
Untrusted text is metadata, not instructions or validated council decisions.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, datetime
from hashlib import sha256
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit
import re

PORTAL_URL = "https://opendata.citywindsor.ca/Tools/CouncilAgendas"
DAY = r"(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)"
MONTH = r"(?:January|February|March|April|May|June|July|August|September|October|November|December)"
MEETING_RE = re.compile(
    rf"(?P<body>[^\n]{{4,180}}?)\s+-\s+(?P<day>{DAY}),?\s+"
    rf"(?P<date>{MONTH}\s+\d{{1,2}},?\s+20\d{{2}})\b",
    re.IGNORECASE,
)
LABELS = {
    "agenda", "consolidated agenda", "final consolidated agenda",
    "minutes", "video", "in-camera agenda", "striking committee agenda",
    "in-camera striking committee", "in-camera striking committee agenda",
    "consolidated striking committee agenda",
}
# The portal also publishes titled item-specific attachments and submissions.
ITEM_MATERIAL_RE = re.compile(r"^(?:item\s+\d+(?:\\.\d+)?\s*[-–:]|written submission\b|appendix\s+[a-z0-9])", re.IGNORECASE)
PUBLIC_VIDEO_HOSTS = {"csg001-harmony.sliq.net"}
MAX_HTML_BYTES = 4_000_000
MAX_MEETINGS = 120
MAX_LINKS_PER_MEETING = 40


def official_url(url: str, base: str = PORTAL_URL) -> str | None:
    absolute = urljoin(base, url)
    p = urlsplit(absolute)
    host = (p.hostname or "").lower()
    if p.scheme != "https" or not (host == "citywindsor.ca" or host.endswith(".citywindsor.ca") or host in PUBLIC_VIDEO_HOSTS):
        return None
    if p.username or p.password or p.port not in (None, 443):
        return None
    return absolute.split("#", 1)[0]


def stable_id(prefix: str, *parts: str) -> str:
    return prefix + ":" + sha256("|".join(parts).encode("utf-8")).hexdigest()[:24]


@dataclass(frozen=True)
class DocumentLink:
    label: str
    url: str
    record_id: str


@dataclass(frozen=True)
class Meeting:
    meeting_id: str
    body: str
    meeting_date: str
    status: str
    documents: tuple[DocumentLink, ...]


class PortalParser(HTMLParser):
    """Flatten the public portal into text/anchor events, preserving their order."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.events: list[tuple[str, str, str]] = []
        self.link_href: str | None = None
        self.link_text: list[str] = []
        self.in_ignored = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "noscript"}:
            self.in_ignored += 1
        if self.in_ignored:
            return
        if tag == "a":
            self.link_href = dict(attrs).get("href", "")
            self.link_text = []
        if tag in {"br", "p", "div", "tr", "td", "li", "button", "h1", "h2", "h3", "h4"}:
            self.events.append(("break", "", ""))

    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript"}:
            self.in_ignored = max(0, self.in_ignored - 1)
            return
        if self.in_ignored:
            return
        if tag == "a" and self.link_href is not None:
            self.events.append(("link", " ".join(" ".join(self.link_text).split()), self.link_href))
            self.link_href = None
            self.link_text = []
        if tag in {"p", "div", "tr", "td", "li", "button", "h1", "h2", "h3", "h4"}:
            self.events.append(("break", "", ""))

    def handle_data(self, data):
        if self.in_ignored:
            return
        if self.link_href is not None:
            self.link_text.append(data)
        elif data.strip():
            self.events.append(("text", " ".join(data.split()), ""))


def discover(html: str, *, since: str = "2026-01-01", base_url: str = PORTAL_URL) -> list[Meeting]:
    date.fromisoformat(since)
    parser = PortalParser()
    parser.feed(html)
    current = None
    found: list[dict] = []
    seen: set[str] = set()
    text_parts: list[str] = []
    def process_text():
        nonlocal current
        line = " ".join(text_parts).strip()
        text_parts.clear()
        match = MEETING_RE.search(line)
        if match:
            try:
                when = datetime.strptime(match.group("date").replace(",", ""), "%B %d %Y").date()
            except ValueError:
                return
            if when < date.fromisoformat(since):
                current = None
                return
            body = " ".join(match.group("body").split()).strip()
            cancelled = bool(re.search(r"\s+-\s+cancelled\s*$", body, re.IGNORECASE))
            # Remove the cancellation tag from the stable identity, so status changes do not create a second meeting.
            body = re.sub(r"\s+-\s+cancelled\s*$", "", body, flags=re.IGNORECASE).strip()
            if len(body) < 4:
                return
            key = stable_id("meeting", "windsor", body.lower(), when.isoformat())
            if key not in seen and len(found) < MAX_MEETINGS:
                current = {"meeting_id": key, "body": body, "meeting_date": when.isoformat(), "status": "cancelled" if cancelled else "unknown", "documents": []}
                found.append(current)
                seen.add(key)
            else:
                current = next((m for m in found if m["meeting_id"] == key), None)
                if current and cancelled:
                    current["status"] = "cancelled"
    for kind, label, href in parser.events:
        if kind == "text":
            text_parts.append(label)
        elif kind == "break":
            process_text()
        elif kind == "link":
            process_text()
            if current is None or len(current["documents"]) >= MAX_LINKS_PER_MEETING:
                continue
            normalized = " ".join(label.lower().replace("–", "-").split())
            if normalized not in LABELS and not ITEM_MATERIAL_RE.match(label.strip()):
                continue
            url = official_url(href, base_url)
            if not url:
                continue
            rid = stable_id("document", url)
            if not any(d.record_id == rid for d in current["documents"]):
                current["documents"].append(DocumentLink(label=label, url=url, record_id=rid))
    process_text()
    return [Meeting(meeting_id=m["meeting_id"], body=m["body"], meeting_date=m["meeting_date"], status=m["status"], documents=tuple(m["documents"])) for m in found]


def to_jsonable(meetings: list[Meeting]) -> list[dict]:
    return [asdict(m) for m in meetings]
