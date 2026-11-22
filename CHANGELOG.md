# Changelog

## 2026-11-21
- Confirmed records.dcmc.ca and api.records.dcmc.ca as future hostnames; implemented a non-deployed public-only Cloudflare Worker skeleton, publish-gated D1 read query, offline tests and hosting readiness documentation on a stacked feature branch. No DNS changes.

- Expanded the Windsor discovery adapter and fixtures to index all portal-listed meeting types, cancelled records, item-specific public attachments and published video links. GitHub Actions test suite: 16 passed (run 44946117505). No deployments.

- Created manual-only, code-first Windsor agenda discovery pilot with offline fixtures, local-only optional ingest, meeting-document relationship migration and tests on a stacked feature branch. No deployment or scheduled jobs.

- Added a proposed D1/SQLite core schema and seven synthetic schema tests on feature/source-index-schema; added a PR test workflow and database notes. No deployed changes.

- Initialized shared multi-agent engineering continuity on the new independent public repository's dev branch.
- Documented scope, licence/data boundaries, 90-day review-only cache policy, planned Workers/D1 architecture and integration isolation.
- No application code, database deployment, scheduled agents, file migrations or deletions performed.


## 2026-11-22 — PR #3 reconciliation into API foundation
- Git merge parent: feature/windsor-source-discovery at 1cd0a4796c6b5b6f5401c78a7391b3cce109239f. Corrected fresh 0001, legacy migration fixtures, 0003/0004, full portal discovery and 28-test integration suite are now present in the PR #4 branch tree. The API remains undeployed, publication remains manually gated, and existing dev D1 remains untouched.
- Open release blocker: PUBLIC_ITEMS_SQL permits any approved review + any rights-cleared evidence version, not necessarily the latest or contemporaneously reviewed version. Before public release enforce current evidence/version and revocation semantics, and independent code review.
- Existing dev D1 migration ledger and verified backup/recovery still pending. No merges to dev/main.
