# Engineering Handoff — Civic Records Index

**Checkpoint:** 2026-11-21 (/wrap)
**Authoritative repository:** https://github.com/prophetamessias/civic-records-index
**Shared operating contract:** AGENTS.md

## Where we left off
Independent open-source civic records research service, first adapter Windsor. All meeting types on the Windsor Council Agendas portal, including special/committee/board and cancelled meetings, are in scope. Separate verified public-data feeds to Council Office and VoterHub, no private cross-project sharing.

## Git/PR state (remote verified)
- main stable and unmodified since initial commit; dev contains bootstrap documents.
- #1 dev→main: https://github.com/prophetamessias/civic-records-index/pull/1
- #2 feature/source-index-schema→dev: https://github.com/prophetamessias/civic-records-index/pull/2
- #3 feature/windsor-source-discovery→feature/source-index-schema: https://github.com/prophetamessias/civic-records-index/pull/3
- #4 feature/api-readiness-dcmc→feature/windsor-source-discovery: https://github.com/prophetamessias/civic-records-index/pull/4
- #5 feature/dev-preview-d1→feature/api-readiness-dcmc: https://github.com/prophetamessias/civic-records-index/pull/5
All OPEN DRAFT and UNMERGED as of checkpoint; feature/dev-preview-d1 head before this documentation commit 597bea35c9de5d91410e58f0c9786d26f93c996e. Do not merge or reorder without independent review/rebase plan. Local working tree/uncommitted state not inspected (only remote GitHub access).

## Files materially added/modified
migrations/0001_core.sql, migrations/0002_meeting_documents.sql, src/civic_index/windsor.py, src/civic_index/discovery.py, src/worker.mjs, tests/test_schema.py, tests/test_discovery.py, tests/test_full_portal_coverage.py, tests/test_worker.mjs, tests/test_preview.mjs, CI workflows, docs/ARCHITECTURE.md, docs/ROADMAP.md, docs/DATABASE.md, docs/WINDSOR_DISCOVERY.md, docs/HOSTING_AND_D1.md, docs/DEV_PREVIEW.md, AGENTS.md, CLAUDE.md, GEMINI.md, DECISIONS.md, CHANGELOG.md, HANDOFF.md.

## Deployment and tests
- Cloudflare D1 **civic-records-index-dev** (non-production), ID 78b3d94a-4a43-4e9c-a8bf-9a7517e1c55b, created. 0001/0002 schema applied directly via authenticated Cloudflare API; 18 application tables verified; latest check confirmed 0 meetings, 0 documents, 0 job runs.
- Exact Worker public-data SQL query executed read-only against dev D1, returned [] without error.
- Latest PR #5 head GitHub CI checks both SUCCESS (Node, SQLite/Python). Verified real Node tests: 11/11 in run 44948318689; Python suite previously verified 16 tests. **Earlier PR #4 Worker green checks executed zero tests** owing to glob mismatch; fixed on #5.
- No Worker deployed; no D1 binding; no preview hostname/Cloudflare Access/token configured; no DNS at approved records.dcmc.ca or api.records.dcmc.ca; no scheduler/AI inference; no public publishing; no SharePoint migration or deletion. Only empty dev D1 exists in Cloudflare.

## Decisions and watch-outs
- Public source-first metadata and provenance index. MIT code; source/document reuse rights assessed separately. All official meetings on portal; source URLs and versions preserved; no assumed votes or adopted outcomes.
- Downloaded files become eligible for **retention review** 90 days after meeting; no automatic deletion. Holds, source validation and human approval mandatory.
- Both final service hostnames approved: records.dcmc.ca and api.records.dcmc.ca; no DNS change yet.
- Source HTML currently validated only with synthetic fixtures; raw live portal parser compatibility is outstanding.
- Direct API D1 migration application may not create Wrangler migration bookkeeping. Reconcile ledger before invoking Wrangler migrate; do not re-run existing CREATE TABLE migrations blindly.
- Admin/preview requires strong authenticated access (Cloudflare Access plus secret), independent security review. No paid model usage without explicit approval.

## Exact next steps
1. Review PRs #1–#5 and integrate in dependency order: #2 into dev; #3 then #4 then #5 into dev, retargeting/rebasing as needed; finally #1 dev→main after review. No unreviewed merge.
2. Validate source parser against real HTML of official City of Windsor CouncilAgendas portal, including non-Council bodies, cancellations, attachments and video links. Review identity collisions, changes/version drift, provenance and rate limits.
3. Reconcile existing D1 schema with Wrangler migration tracking and independently review D1/Worker security and publication gates.
4. After explicit deployment approval, prepare protected development Worker with Cloudflare Access, dev D1 binding, hostname/secret, and non-public preview smoke tests.
5. Build job log/monitoring dashboard and only then authorize bounded scheduled discovery. Preserve cost caps, source rights and human publication/deletion controls.

## Continuity
Canonical ChatGPT Library /Projects/civic-records-index/ stores PROJECT.md, CURRENT_STATE.md, HANDOFF.md, CONTEXT_INDEX.md, DECISIONS.md, CHANGELOG.md, CHAT_LOG.md. GitHub authoritative for code, branches, tests and deployments.


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


## 2026-11-26 — Product delivery priority and calendar checkpoint
- User explicitly prioritized getting a working Windsor public-meetings/agendas/supporting-documents tracker into use quickly, followed by a councillor-friendly Council Office workspace and ongoing VoterHub Next work. Do not fork Civic Records Index or start a replacement legislative suite for this MVP; build later municipal-suite modules separately as appropriate.
- Product boundary: Civic Records Index ingests and verifies authoritative *public* meetings/agenda/items/files, timestamps and revisions, with source links; Council Office consumes that via separately secured authentication and stores councillors' private notes/tasks/review state in its *own* datastore; VoterHub receives only public verified information. Never transfer private office data to VoterHub.
- MVP acceptance: councillor signs in; sees all upcoming public Windsor meetings including committees/boards; opens official agendas and item-linked supporting documents; sees revisions/cancellations; records private preparation notes/tasks. First priority is real Windsor source ingestion and safe protected preview; next dashboard integration; then pilot with authorized user. Public video chapters, official report authoring, voting, comprehensive legislative suite and vendor-specific integration are later milestones.
- City procurement research: Windsor RFP 119-26 (Electronic Agenda Management) and 120-26 (Meeting Management Software) closed in November 2026. Informal Purchasing request declined; user sent formal FOI inquiry to foi@citywindsor.ca. Do not treat any vendor as selected; maintain standards-based, vendor-independent adapters and avoid delaying MVP for FOI response.
- Google Calendar Main updated 2026-11-26: recurring daytime blocks starting Monday 2026-11-30, Monday+Thursday Civic Records Index (~8.5 h/week), Tuesday+Friday Council Office (~6.5 h/week), Wednesday+Friday VoterHub (~6.25 h/week). Existing 10:00–15:15 sessions repurposed; late-afternoon career/income blocks, appointments, hockey and weekends preserved. First-week duplicate legacy events cleaned; week of Dec 14 spot-checked. Future calendar adjustments should be conflict-aware.
- Work completed in this conversation: calendar scheduling and strategic prioritization only. NO repository application code, migrations, D1 data, Cloudflare deployment, DNS or public publishing changed. Repository docs are being checkpointed on feature/dev-preview-d1; main/dev remain outside this documentation change. Last known engineering blockers remain migration ledger/recovery, independent security re-review, real source HTML and historical coverage validation, and release authorization. Do not imply previous 42 Python/11 Node tests were rerun today.
- Immediate next session: (1) inspect latest PR ancestry and issue #6 Gemini findings; (2) reproduce/validate current Windsor portal HTML across meeting types and attachments with tests; (3) resolve dev-D1 migration/backup and approval-gate blockers before writes; (4) obtain deployment approval for restricted preview; (5) implement Council Office minimum meeting/document dashboard against safe source API and pilot it; (6) continue weekly VoterHub delivery.
