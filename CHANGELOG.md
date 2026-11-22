# Changelog

## 2026-11-21
- Expanded the Windsor discovery adapter and fixtures to index all portal-listed meeting types, cancelled records, item-specific public attachments and published video links. GitHub Actions test suite: 16 passed (run 44946117505). No deployments.

- Created manual-only, code-first Windsor agenda discovery pilot with offline fixtures, local-only optional ingest, meeting-document relationship migration and tests on a stacked feature branch. No deployment or scheduled jobs.

- Added a proposed D1/SQLite core schema and seven synthetic schema tests on feature/source-index-schema; added a PR test workflow and database notes. No deployed changes.

- Initialized shared multi-agent engineering continuity on the new independent public repository's dev branch.
- Documented scope, licence/data boundaries, 90-day review-only cache policy, planned Workers/D1 architecture and integration isolation.
- No application code, database deployment, scheduled agents, file migrations or deletions performed.



## 2026-11-22 — D1 migration preparation and discovery collision guard
- PR #3 now includes `migrations/0003_integrity_guards.sql`, an ADDITIVE, NOT APPLIED migration for legacy dev D1 (0001+0002) with guarded indexes/triggers for provenance, integrity, retention minimum and deletion blocking.
- Discovery now fails closed on duplicate municipality/body/day headings; it does NOT yet resolve two legitimately separate same-name/same-day sessions without an official source session ID. Manual identity review required before recurring ingestion.
- Fresh Cloudflare read-only preflight: 0 meetings, 0 document versions, 0 duplicate unhashed-version groups, and NO migration ledger table detected. The old `meetings` UNIQUE(municipality_id,body,meeting_date) still exists. No DB writes performed.
- DO NOT apply migrations remotely or replay `0001`/`0002`; first verify CLI bookkeeping, snapshot D1, and independently review a compatible strategy for removing the old meetings constraint without risking foreign keys. PR #2 changes are NOT yet in PR #3 ancestry; stacked branches need intentional reconciliation after review.
- Tests added for idempotent 0003 application on legacy local SQLite and duplicate-heading fail-closed behaviour. CI result to verify on new PR #3 head; prior green runs apply to older code.
