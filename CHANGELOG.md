# Changelog

## 2026-11-21
- Added a proposed D1/SQLite core schema and seven synthetic schema tests on feature/source-index-schema; added a PR test workflow and database notes. No deployed changes.

- Initialized shared multi-agent engineering continuity on the new independent public repository's dev branch.
- Documented scope, licence/data boundaries, 90-day review-only cache policy, planned Workers/D1 architecture and integration isolation.
- No application code, database deployment, scheduled agents, file migrations or deletions performed.


## 2026-11-22 — PR #2 integrity remediation
- Updated fresh-install 0001 schema on feature/source-index-schema for meeting ID flexibility, unhashed source uniqueness, owned document pointers, cross-record validity, +90-day cache review floor, and fail-closed deletion transitions.
- Added eight regression tests alongside original seven; GitHub Actions schema CI run 45066799032 passed.
- Clarified that existing Cloudflare dev D1 (old 0001+0002) requires separate reviewed forward-only upgrade and migration-ledger reconciliation. No D1/Worker/DNS/publishing/deletion actions; PR still draft.
