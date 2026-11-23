# Windsor source discovery (Phase 1)

**Status:** deterministic read-only pilot, not deployed or scheduled. Uses only public official City of Windsor council agenda index URLs. It does not download meeting PDFs, extract contents, create decisions, or publish data.

Official portal: https://opendata.citywindsor.ca/Tools/CouncilAgendas

## Offline exercise (no network or billing)

```bash
PYTHONPATH=src python -m civic_index.discovery --fixture tests/fixtures/windsor-agendas.html --since 2026-11-01
python -m unittest discover -s tests -v
```

The output is JSON containing meetings and associated official document URL references; **dry-run never creates or changes a database**.

## Live read-only check (manual only)

```bash
PYTHONPATH=src python -m civic_index.discovery --since 2026-11-01
```

The fetch requests at most 4 MB of HTML, requires the official index URL and HTML response, uses a 15-second timeout, and performs NO requests to links found in the index. It discovers only recognized meeting document labels on allowed HTTPS citywindsor.ca hosts. There is no scheduler.

## Optional explicit LOCAL SQLite write

```bash
python - <<'PY'
import sqlite3
with sqlite3.connect('civic-index.local.sqlite') as db:
    for file in ('migrations/0001_core.sql', 'migrations/0002_meeting_documents.sql'):
        db.executescript(open(file, encoding='utf-8').read())
PY
PYTHONPATH=src python -m civic_index.discovery --fixture tests/fixtures/windsor-agendas.html --since 2026-11-01 --apply --db civic-index.local.sqlite
```

An explicit `--apply --db` is required to insert into local SQLite. Rows are idempotent; existing meeting outcomes are never overwritten, discovered version rights and verification status remain pending, and the run is logged. No remote D1 writes implemented.

## Required review before any real run or scheduling

- Confirm the live portal's markup works with the HTML parser; tests use a clearly labelled synthetic fixture, not a captured official HTML snapshot.
- Check rate limits, terms and copyright/reuse applicability before recurring access.
- Validate meeting identifiers and dates, de-duplicate corrected agendas and support version fingerprint checking in later phases.
- Audit rights to public in-camera *agenda metadata*; discovery does not imply confidential closed-session content is accessible or publishable.
- Add explicit permission-controlled publication and independent human verification. No model-generated conclusions or automatic public publishing.
- Add durable D1 repository adapter, scheduler, rate-limited retries and alerting with recorded job metrics before turning on any recurring workflow.
- Keep all cached documents subject to the 90-day **review eligibility**, not automatic deletion.


## Full portal coverage (2026-11-21 decision)
Discovery must cover **every meeting entry listed on the official CouncilAgendas portal**, including City Council, standing committees, special sessions, inaugural/orientation sessions, committees sitting as other boards, and cancelled meetings. Do not filter to regular Council meetings. Preserve the full meeting body/title and distinguish cancelled status from any legislative decision.

Index every public meeting material type that the portal exposes: agendas (original/consolidated/final), minutes, published in-camera *agenda links* (not confidential content), striking committee agenda links, publicly linked videos, and item-specific appendices and written submissions. External video metadata is allowed only from the explicitly reviewed host `csg001-harmony.sliq.net`; never follow links without separate source-policy checks. Metadata discovery is not license verification or publication approval.

**Current limitation:** a meeting identity is based on municipality, published title (minus 'CANCELLED') and date. Duplicate same-name/same-day sessions and changes to the title require a future portal-native identifier or explicit collision review. This pilot does not infer approvals or votes, nor automatically disclose closed-session materials. Live HTML compatibility remains to be verified before scheduling.


## 2026-11-22: collision safety and staged D1 upgrade
The parser now rejects a repeated identical municipality/body/day heading instead of silently combining potentially distinct sessions. This is deliberately fail-closed; full same-title/same-day session support still requires a reliable portal-native identifier and real portal validation. The new `0003_integrity_guards.sql` is an **additive, unapplied** migration for the legacy dev D1 created using the old baseline. It adds provenance/retention protections but **does not remove** the existing meetings unique constraint. Run preflight duplicate checks, reconcile migration bookkeeping, inspect D1 backup options and obtain approval before applying remotely. Do not repeat `0001` or `0002` on dev D1.
