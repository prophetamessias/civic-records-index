# Changelog

## 2026-11-21
- Confirmed records.dcmc.ca and api.records.dcmc.ca as future hostnames; implemented a non-deployed public-only Cloudflare Worker skeleton, publish-gated D1 read query, offline tests and hosting readiness documentation on a stacked feature branch. No DNS changes.

- Expanded the Windsor discovery adapter and fixtures to index all portal-listed meeting types, cancelled records, item-specific public attachments and published video links. GitHub Actions test suite: 16 passed (run 44946117505). No deployments.

- Created manual-only, code-first Windsor agenda discovery pilot with offline fixtures, local-only optional ingest, meeting-document relationship migration and tests on a stacked feature branch. No deployment or scheduled jobs.

- Added a proposed D1/SQLite core schema and seven synthetic schema tests on feature/source-index-schema; added a PR test workflow and database notes. No deployed changes.

- Initialized shared multi-agent engineering continuity on the new independent public repository's dev branch.
- Documented scope, licence/data boundaries, 90-day review-only cache policy, planned Workers/D1 architecture and integration isolation.
- No application code, database deployment, scheduled agents, file migrations or deletions performed.
