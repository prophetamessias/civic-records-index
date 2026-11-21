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
