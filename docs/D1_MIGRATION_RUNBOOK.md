# D1 schema reconciliation and meeting-identity migration runbook

Status: REVIEW REQUIRED — 2026-11-22. This document does not authorize any remote database modification.

## Confirmed non-production state
- Database: `civic-records-index-dev` (isolated D1 UUID `78b3d94a-4a43-4e9c-a8bf-9a7517e1c55b`).
- Direct API SQL application previously installed ORIGINAL `0001_core.sql` and `0002_meeting_documents.sql`.
- Read-only inspection on 2026-11-22: zero meetings, zero document versions, zero duplicate unhashed document-version groups; no table matching `%migration%`. The old `meetings` date/body uniqueness rule remains present.
- NO application has been given permission to perform remote migrations, ingestion, publication, or deletion.

## Schema upgrade files
- `0003_integrity_guards.sql`: additive uniqueness indexes and fail-closed integrity/deletion triggers. Uses IF NOT EXISTS. It does not remove the legacy meetings uniqueness constraint.
- `0004_meetings_identity.sql`: a single-transaction, forward-only SQLite parent-table rebuild that preserves `meetings.id` and data, defers FK checks, temporarily removes/re-creates meeting-dependent triggers, and recreates indexes. Tested on SQLite with synthetic child rows and foreign-key checks. Do NOT run line-by-line or as separate transactions.

## Preflight — mandatory before the first remote write
1. Independently review SQL and verify the actual installed D1 schema against the original migrations, including all indexes/triggers, `PRAGMA foreign_key_list`, and foreign-key integrity.
2. Reconcile the existing direct-API migrations with the migration manager's bookkeeping. The lack of a migration ledger means applying the migration directory unmodified could rerun `0001` and fail; do not fabricate history without a documented, reviewed baseline procedure.
3. Obtain a restorable backup/snapshot of the isolated dev D1; confirm recovery capability and the correct database ID. Cloudflare D1 Time Travel or export mechanisms are subject to current documentation and availability.
4. Query pre-migration row counts for every application table, check for duplicate unhashed document version keys, validate the former `meetings` table schema, and verify that no unexpected triggers or cascading child relationships exist.
5. Confirm approval for the isolated dev DB migration, no concurrent ingestion, and a maintenance/rollback plan. Other D1 databases and DNS must not be modified.

## Staged validation and execution boundaries
1. Run all Python schema/discovery tests on a clean checkout, plus a fresh-old-schema to `0003` to `0004` migration test on nonempty synthetic linked data.
2. Verify full stack consistency: PR #2 has a revised fresh-install `0001`, whereas PR #3 was originally based on the former `0001`. The merged tree must have one deliberate final migration order. PRs #4 and #5 must be reviewed against that exact tree.
3. Run a copy-based D1 compatibility check before executing against the actual dev DB. The local SQLite regression is necessary but does not prove D1 execution semantics or live-data safety.
4. When separately authorized: apply pending migrations with a transaction-aware migration mechanism; no manual per-statement D1 API sequence.
5. Confirm `PRAGMA foreign_key_check` is empty; record preserved table row counts and exact migration versions; verify same-body/same-day distinct IDs, duplicate protection, review-date floor, and deleted-state blocking. Roll back if any check fails.

## Known limitations
- The Windsor source parser intentionally rejects repeated indistinguishable meeting headings. The relaxed DB uniqueness constraint alone does NOT generate distinct authoritative meeting identifiers; genuine same-title/same-day session identification requires portal-native metadata or reviewed disambiguation.
- Polymorphic relationship constraints guard new/updated rows; cross-record mutation and hard-delete policies still require review.
- Source rights, publication approvals, closed-session boundaries, and cache deletion remain separately gated.
- All five PRs remain draft, and no production or staging hostname is deployed.

References: Cloudflare D1 migration and foreign-key documentation:
https://developers.cloudflare.com/d1/reference/migrations/
https://developers.cloudflare.com/d1/sql-api/foreign-keys/
