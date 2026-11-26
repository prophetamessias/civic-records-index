# Changelog

## 2026-11-21
- Provisioned isolated Cloudflare development D1 `civic-records-index-dev`, applied 0001/0002 migrations and verified empty application tables and working read-only Worker SQL query.
- Added draft PR #5: authenticated fail-closed preview host, Node preview tests, fix for Worker CI zero-test glob, and development deployment documentation. Actual 11 Node tests and inherited Python/SQLite suite passed in CI. No Worker/DNS/scheduler deployment.

- Confirmed records.dcmc.ca and api.records.dcmc.ca as future hostnames; implemented a non-deployed public-only Cloudflare Worker skeleton, publish-gated D1 read query, offline tests and hosting readiness documentation on a stacked feature branch. No DNS changes.

- Expanded the Windsor discovery adapter and fixtures to index all portal-listed meeting types, cancelled records, item-specific public attachments and published video links. GitHub Actions test suite: 16 passed (run 44946117505). No deployments.

- Created manual-only, code-first Windsor agenda discovery pilot with offline fixtures, local-only optional ingest, meeting-document relationship migration and tests on a stacked feature branch. No deployment or scheduled jobs.

- Added a proposed D1/SQLite core schema and seven synthetic schema tests on feature/source-index-schema; added a PR test workflow and database notes. No deployed changes.

- Initialized shared multi-agent engineering continuity on the new independent public repository's dev branch.
- Documented scope, licence/data boundaries, 90-day review-only cache policy, planned Workers/D1 architecture and integration isolation.
- No application code, database deployment, scheduled agents, file migrations or deletions performed.

## 2026-11-21 — /wrap continuity checkpoint
- Re-verified all five stacked draft PRs unmerged, GitHub CI success at latest preview head, and Cloudflare dev D1 still empty (0 meetings/documents/job runs).
- Updated HANDOFF.md with verified repository/Cloudflare state, known blockers, explicit deployment safeguards, and exact next steps. No production changes, merges, DNS, schedules, AI usage, data import, publishing or deletion during checkpoint.


## 2026-11-22 — PR #4 integration into restricted preview
- Merged the complete API branch 32f65f53faec3f16f05d18b225c5bf25221163ce as second parent into preview branch 3c19cdcbd09303cbbe8d1870e5adc7b0d06de9a4, bringing corrected fresh schema, legacy baseline fixture, proven migrations 0003 and 0004, discovery collision guard, and integrated Python test suite to preview ancestry.
- Preserved preview-specific bearer authorization, Worker entry point, and Node tests. The actual dev D1 remains untouched; no Worker or DNS deployment.
- PUBLIC API release remains blocked pending review of current evidence/version identity, approval revocation and data rights. Preview access still requires separate Cloudflare Access and explicitly configured secret.


## 2026-11-22 — Publication query hardening and downstream CI
- PR #4 and #5 Worker SQL now only accepts verified, rights-cleared versions that equal `documents.current_version_id`; superseded version evidence is no longer sufficient to publish an item.
- Added `tests/test_publication_gate.py`, executing actual Worker SQL against synthetic SQLite and validating unset-current, superseded-current, reapproved-current, rights restriction, and disposition/review gate behaviour.
- PR #4 latest CI: Python 31 tests and Node Worker tests passed (runs 45082908873 and 45082908861). PR #5 latest CI: Python 31 and Node 11 passed (runs 45082912131 and 45082912202).
- Residual release blocker: approvals are not yet bound to an immutable evidence/version snapshot or an explicit revocation policy. `documents.current_version_id` is an application-managed pointer; source updates and publication-review versioning need independent review before public deployment.
- No feature PR merged into dev/main, no Worker, DNS, or existing dev D1 changes. Disposable migration test database from previous session already deleted.


## 2026-11-22 — Security architecture review and release-gate checkpoint
- Current draft PR stack remains #1 dev→main, #2 schema→dev, #3 discovery→schema, #4 API→discovery, #5 preview→API. No PR merged; dev/main unchanged.
- PR #4 adds migration `0005_publication_authorizations.sql` and Worker SQL requiring explicit reviewer-identified current evidence version, SHA-256, exact reviewed item/meeting snapshot and nonrevoked approval. Legacy `publication_reviews` entries are not sufficient. Database triggers prevent forged/outdated authorization based on changed/uncleared versions, prevent reactivation/retargeting and disallow deleting authorization history. There is no live reviewer mutation API.
- PR #3 recognizes official numbered in-camera agenda session links and fails closed on meeting/document discovery caps (no silent truncation). Real portal read-only inspection found numbered sessions and varied meeting types; raw HTML parser compatibility remains unverified, as do full-history backfill and authoritative duplicate-session identity.
- Integration initially overwrote preview-specific auth on PR #5; Node CI caught failure (run 45084793326). Restored preview auth while preserving new authorization SQL (commit 8b43c9684e71ccbe431b27a0b0e5d69aba18f95e).
- Final checked PR #5 merged tip `0b0269329e655fb00b74ecba45c52d2f03f2adaa`: schema/discovery/publication **35 Python tests passed** (run 45084877195), Worker/preview **11 Node tests passed** (run 45084877199).
- Review record: `docs/SECURITY_ARCHITECTURE_REVIEW.md`. This was a ChatGPT implementer self-review, NOT independent Gemini/third-party review; report verdict HOLD DEV MERGE pending independent review and resolution/acceptance of listed HIGH findings.
- Outstanding before live operation: reviewer authentication/authorization, complete multi-document evidence manifest policy, raw portal HTML coverage verification and full historical backfill, 0005 disposable D1 compatibility validation, existing dev D1 migration ledger reconciliation and restorable recovery point, Cloudflare Access and secrets for preview. Public domains/DNS/Worker routes remain undeployed.
- No changes to the existing `civic-records-index-dev` D1, other Cloudflare resources, public output, DNS, data imports, automated publishing, paid inference or cached record deletions.

**Next:** obtain actual independent review, resolve or explicitly accept findings for integration into dev, verify PR ancestry/CI on current heads, then seek explicit human approval to merge sequentially. Do NOT deploy, migrate dev D1, or enable ingestion before separate reviews.


## 2026-11-22 — Gemini review handoff and D1 0005 test
- Independent Gemini review request created as GitHub issue https://github.com/prophetamessias/civic-records-index/issues/6. Gemini is NOT connected to this ChatGPT session: issue is a review package, **not a completed Gemini review**. Pending user action in Antigravity/Gemini; no reviewer verdict yet.
- Tested a disposable Cloudflare D1 `civic-records-0005-review-test-20261122` against the **legacy upgrade sequence**: original 0001 fixture → 0002 → 0003 → 0004 → 0005; every schema SQL step succeeded.
- In that isolated D1, inserted synthetic meeting/item/document/version and old `publication_reviews` approval. Exact current Worker public SQL returned zero rows; a new, matching version-bound `publication_authorizations` approval produced one public row; revoking the authorization made public SQL return zero rows again. The revoked record remained for audit and `PRAGMA foreign_key_check` reported no violations.
- Verified the disposable D1 name/UUID then deleted **only** that test instance (UUID `55377533-cd89-4b8f-a75d-c6e09dc49af8`), Cloudflare deletion API success. The existing dev database was not modified.
- PRs #1–#5 remain draft/unmerged; no Worker/DNS deployments, real ingestion, paid AI, autonomous publishing or document deletion.
- Next: have Gemini independently inspect issue #6 read-only and return actionable findings. Evaluate findings and remediate on feature branches, rerun CI, then separately authorize any dev merge. Development D1 migration ledger/backup/recovery still unresolved.


## 2026-11-22 — Independent Gemini audit remediation (REQUEST CHANGES)
- User supplied Gemini Antigravity review (verdict REQUEST CHANGES); major findings summarized on [issue #6](https://github.com/prophetamessias/civic-records-index/issues/6). Gemini's independent finding status is NOT an approval for current code.
- PR #3 now handles hyphen/en-dash/em-dash and split semantic heading elements, with regression tests; CI schema coverage includes `src/civic_index/**` and stacked feature branches.
- PR #4 and PR #5 publication query now rejects cancelled/unknown meetings, requires a matching approved meeting-status snapshot, and fails closed if any linked document lacks a current, verified, rights-cleared, hash-identified version linked to that item. Correction triggers revoke previously approved item/meeting snapshots irreversibly.
- Added additive `migrations/0006_audit_integrity.sql`: hard cache delete prevention, current document-version reassignment guard and meeting-date retention floor; added regression tests. No data deletion workflow enabled.
- Reconciled PR #3 → #4 → #5 with preview bearer authentication preserved. Latest integrated PR #5 commit before docs `72eb7d52c0538c9376712d3ef68de047db2f7aee`, Python **42 tests passed** (Actions run 45092004309), Node **11 tests passed** (run 45092004305).
- **Outstanding HIGH:** migration ledger and provenance reconciliation for old direct-API D1, plus verifiable backup/recovery before dev D1 write. See runbook. Actual live Windsor HTML and full historical coverage remain unverified; schedule and publishing disabled.
- **Outstanding release design:** binding approval to all relevant source documents and controlling post-review additions/removals; reviewer identity authentication; permissioned editorial workflow; possible browser CORS preview preflight; in-place PDF version tracking; independent Gemini re-review of new changes. Current companion check is fail-closed for restricted linked documents, not a complete reviewed-evidence manifest.
- No merges, deployments, DNS changes, live database migrations, scheduled ingestion or public publication.


## 2026-11-26 — Priority, delivery scope and schedule checkpoint
- Agreed near-term delivery sequence: live Windsor meeting/agenda/supporting-document indexing → restricted preview → Council Office councillor workspace → authorized pilot, while VoterHub Next development continues weekly.
- Deferred fork/full legislative-management suite; retained public/private consumer boundaries and vendor-neutral design.
- Reallocated recurring Google Calendar work blocks beginning 2026-11-30: Civic Records Index ~8.5 h/week, Council Office ~6.5 h/week, VoterHub ~6.25 h/week. Preserved existing late-afternoon career/income time, fixed commitments and hockey; cleaned first-week duplicates and verified future week.
- No implementation, deployment, database migrations or code test runs performed in this checkpoint. Existing security, ingestion and D1 recovery blockers remain open.
