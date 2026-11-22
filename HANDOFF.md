# Engineering handoff — Civic Records Index
Updated: 2026-11-21

## State
New independent public MIT-licensed repository. `main` retains original README/LICENSE/.gitignore. `dev` created for project setup. Repository operating docs established on `dev`; no application code, D1 database, automated agent or Cloudflare deployment yet.

## Decisions
See DECISIONS.md and AGENTS.md. Initial architecture: Cloudflare Workers + D1 metadata/index, temporary SharePoint cache later, source-specific municipality adapters, deterministic discovery/extraction before optional LLM analysis. Public data service feeds Council Office and VoterHub through distinct consumers and authorization boundaries. A human approves public publication and cached file deletion.

## Existing research
Google Drive research folder: https://drive.google.com/drive/folders/1Z-DOVaUXD2n0sn2NBTA_HPQ717gi9h4v
Historical decisions register: https://docs.google.com/document/d/1OJuRgLmmuHVfZAoF88858qS3x6tb95L9YW7WzKgUDOQ/edit
Prior local proof-of-concept ZIP was generated in chat, NOT committed; inspect/licence-review before importing.

## Next steps
1. Review and merge bootstrap PR after verifying files/branch controls.
2. Define schema/migrations for municipalities, meetings, agenda items, source documents/versions, relationships, decisions, recorded votes, jobs, verification and retention holds.
3. Add synthetic fixtures and tests; import only traceable/public Windsor references.
4. Implement read-only Windsor adapter with scheduler, rate limiting, idempotent ingest, monitored no-AI run.
5. Add dashboard and agent workflow stages after ingestion tests.

## Risks
Official portal/link changes; source-licence ambiguity; large PDFs; model hallucination; operating costs; final meeting outcomes not yet established. No deletion or public publishing enabled.

## 2026-11-21 — Schema feature branch progress
Feature branch `feature/source-index-schema` branched from `dev`; added migrations/0001_core.sql, tests/test_schema.py, docs/DATABASE.md and GitHub Actions schema test workflow. Local SQLite baseline tests passed (seven checks). No D1 instance created, no API, no agent deployed. PR awaiting review; bootstrap draft PR #1 is still open/unmerged. Follow-up: run CI, review schema privacy, source version uniqueness, retention authorization and cross-entity references; implement Windsor read-only adapter after branch integration.

## 2026-11-21 — Windsor discovery pilot
Feature `feature/windsor-source-discovery` stacked atop schema branch. Added Python stdlib Windsor HTML index reader, URL allowlist, bounded read-only HTTP fetch, dry-run JSON CLI, explicit local-only idempotent SQLite writes, 0002 meeting_documents migration, synthetic fixtures/tests and operations guide. No schedule, cloud API or SharePoint access activated. Run CI and independently validate actual portal HTML prior to use; keep PR stacked until schema branch review. No paid AI and no deletion/public publishing.

## 2026-11-21 — Scope expansion and verification
User confirmed **all meeting types listed on Windsor's CouncilAgendas portal** are in scope, not just regular Council meetings. The future project domain must be a subdomain of dcmc.ca (records.dcmc.ca proposed, not configured). Expanded adapter to mark cancelled meetings, recognize item-level appendices/submissions and videos from the official listed provider, preserve unusual committee/board session titles, and retain discovery-only status. GitHub Actions [run 44946117505](https://github.com/prophetamessias/civic-records-index/actions/runs/44946117505) completed successfully (16 tests). Earlier failed incremental runs were addressed by regex/test fixes. No live portal fetch by application, D1 deployment, scheduler, DNS change, data publication, or deletion. Prior review order PR #2 into dev, then PR #3 (stacked), then PR #1 dev into main after review.


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
