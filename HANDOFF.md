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
