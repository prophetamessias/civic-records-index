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

## 2026-11-22 — Combined schema and disposable Cloudflare D1 verification
- Merged PR #2 tip `d5875daa07345aaabb29cf7c9dabbb9f8734ada5` into PR #3 using a two-parent commit `7c25e1c50c0b8ccd3bc748996e7dec540c713182`. This **did not merge either PR into dev/main**.
- Retained corrected `migrations/0001_core.sql` for pristine databases, and preserved the previously deployed original SQL as `tests/fixtures/legacy_0001_core.sql`. Local tests cover both paths; no migration history was overwritten in Cloudflare.
- GitHub Actions on merged PR #3: runs 45078434696 and 45078441033 passed. Added a fresh-install full-migration/local-discovery-ingest regression test; run 45078593321 passed **28 tests**.
- Created a single disposable Cloudflare D1 called `civic-records-index-migration-test-20261122` (UUID `e88e3016-14b7-4018-9678-007230d7dbb5`), with synthetic rows and original 0001+0002 SQL. Applied 0003 and 0004 successfully using the API's multi-statement query facility.
- D1 post-migration: `PRAGMA foreign_key_check` returned zero violations. Preserved one linked meeting, agenda item, resolution, meeting-document link and cache record. The `meetings` legacy unique constraint was absent, the migration snapshot table was absent, and 14 integrity/deletion triggers were present.
- Verified distinct second same-body/same-date meeting ID accepted, duplicate primary key rejected, duplicate unhashed document version rejected, cache review date below meeting+90 days rejected, and both deletion approval and deleted status rejected.
- Verified disposable DB identity before deletion; Cloudflare D1 deletion API reported `success=true`. **Only the disposable D1 was deleted.** No changes to `civic-records-index-dev`, other databases, Workers, DNS or publication.
- These tests establish D1 execution compatibility with a synthetic dataset; they do not replace review of the real dev database's schema/migration ledger, backup/recovery plan, real source parser, or independent approval.


## Independent Gemini findings / remediation ledger (2026-11-22)
Gemini's independent review was REQUEST CHANGES (see GitHub issue #6). A code change is **not** equivalent to independent re-approval.

| Finding | Implementation response | Remaining gate |
| --- | --- | --- |
| 1 cancelled meetings published | Public SQL requires scheduled/completed meeting and authorization snapshots `approved_meeting_status`. Meeting state changes permanently revoke approval. | Gemini re-review, verify upstream corrections |
| 2 restricted companions | Public SQL excludes items with any linked document whose current version is unverified, not rights-approved, lacks hash, or is not itself linked. | Define a complete multi-document evidence manifest and reapproval on changes |
| 3 dash variants dropped | Parser recognizes hyphen/en/em dash and regression tests. | Validate real portal HTML |
| 4 split semantic elements dropped | Bounded parser heading candidate can span h2/p or table cells; regression tests. | Ensure unrelated text cannot accidentally join into a false heading; live portal validation |
| 5 migration history divergence | **UNRESOLVED.** Existing dev D1 has direct-applied original 0001+0002, no ledger, while fresh 0001 is revised. | Verified backup/export, migration tooling reconciliation, reversible test-run and separate authorization |
| 6 document ownership drift | 0006 blocks reassignment of a document version used as current by a document. | Independent SQL review |
| 7 hard cache delete | 0006 blocks raw DELETE on cache_records. | Independent SQL review |
| 8 approval resurrection | 0005 revokes approval on item and meeting data changes; revoked status not reversible. | Document/link set changes still require manifest policy |
| 9 CI misses parser | Schema workflow watches `src/civic_index/**` and stacked branches. | CI review and branch policy |

### Migration path decision needed before touching actual dev D1
1. Freeze existing live schema evidence and all table row counts, and record the raw `sqlite_master` definitions and schema hash; independently verify existing original 0001+0002 match expected legacy fixture. Do not rely on a 0-meetings count alone.
2. Decide **one** canonical migration manager and immutable history policy. The revised fresh 0001 and legacy original 0001 are distinct schema histories; the current `0003`/`0004` bridge does not itself establish an automated migration ledger.
3. Test a reviewed baseline/reconciliation procedure on a disposable clone or exported copy, including migration `0006`, then prove that a second migration check is a no-op, and validate FK counts/indexes/triggers and restoration from backup.
4. Obtain explicit owner approval before the first write to `civic-records-index-dev`, and log what was executed. Never forge a migration ledger or blindly run `0001`/`0002` again.
