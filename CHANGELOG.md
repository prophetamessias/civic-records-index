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


## 2026-11-22 — Verified SQLite meeting identity rebuild
- Enabled push CI for the PR #3 discovery branch; new migration/discovery tests execute on each relevant commit.
- Added `migrations/0004_meetings_identity.sql` to remove the old per-body/day uniqueness rule using FK deferral and a migration snapshot. The first populated synthetic CI run caught trigger-revalidation failure; the second caught deferred FK failure. Both were resolved and tracked in GitHub Actions.
- The final populated SQLite regression passed on commit `5417ef53cc4c3339b3c749a7fd10a728f4747921`, run https://github.com/prophetamessias/civic-records-index/actions/runs/45067804159 . Child rows for agenda items, resolutions, meeting documents and cached copies were retained; `PRAGMA foreign_key_check` empty; duplicate same-body/day distinct meeting IDs permitted; original primary-key and retention guards remain enforced.
- Added `docs/D1_MIGRATION_RUNBOOK.md` with preflight, backup/recovery, migration ledger reconciliation, reference-count comparison and release gates.
- Existing dev D1 is UNCHANGED. No migration bookkeeping table was seen at last read-only check, and no D1 worker/DNS was configured.
- Important: successful SQLite CI does not establish Cloudflare D1 migration transaction compatibility. Validate in copy-based D1 environment and obtain independent review before remote application. PR #2 schema corrections remain on a different branch and are not yet reconciled into the PR #3 ancestry; keep PRs in draft. Live portal session identity still pending source verification.


## 2026-11-22 — Schema branch reconciled into discovery
- Merged schema PR #2 tip d5875daa0734 into PR #3 tip 1223920b35e1 without merging either pull request.
- Preserved legacy original 0001 as an immutable synthetic regression fixture for upgrade-path tests, while corrected 0001 is used for fresh-install tests. Both need test verification.
- Adopted the schema remediation notes from PR #2:
- Updated fresh-install 0001 schema on feature/source-index-schema for meeting ID flexibility, unhashed source uniqueness, owned document pointers, cross-record validity, +90-day cache review floor, and fail-closed deletion transitions.
- Added eight regression tests alongside original seven; GitHub Actions schema CI run 45066799032 passed.
- Clarified that existing Cloudflare dev D1 (old 0001+0002) requires separate reviewed forward-only upgrade and migration-ledger reconciliation. No D1/Worker/DNS/publishing/deletion actions; PR still draft.
