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


## 2026-11-22 — PR #2 schema remediation
The feature/source-index-schema branch now has strengthened baseline SQL guards and 8 additional regression tests, with schema CI SUCCESS (GitHub Actions run 45066799032). New baseline allows two distinct meeting IDs for the same body/date while preserving primary-key idempotency; blocks duplicate unhashed document versions, wrong document/current-version ownership, mismatched meeting/resolution links, cross-municipality agenda-document links, dangling polymorphic relationship targets, retention-review dates before meeting+90 days and deletion-review approval/execution or marking a cache deleted. PR #2 remains DRAFT; no merges/deploys.

CRITICAL: the actual Cloudflare dev D1 already has older 0001 and 0002 migrations applied directly by API. Fresh baseline amendments on this PR are NOT applied to it. Do not rerun 0001. Reconcile the migration ledger, take a verified backup, and develop/test a forward-only upgrade (including the existing meetings uniqueness constraint) before future deployment or live ingestion. Downstream stacked branches #3/#4/#5 still contain their earlier ancestry and must be rebased/retargeted after review; review discovery.py stable_id handling for two same-day same-body sessions. No D1 changes authorized/executed in this remediation.
