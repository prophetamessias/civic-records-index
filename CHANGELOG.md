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
