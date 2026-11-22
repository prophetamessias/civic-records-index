# Civic Records Index — Security & Architecture Review

**Date:** 2026-11-22. **Status:** SELF-REVIEW COMPLETE; INDEPENDENT REVIEW AND MERGE APPROVAL PENDING.

This report is a repository/CI and primary-source inspection performed by ChatGPT while coordinating the implementation. It is **not** an independent security attestation by Gemini, another reviewer, or a qualified external auditor. No merge, Worker deployment, DNS change, live ingestion or migration of the existing dev D1 is authorized by this report.

## Scope inspected
- Draft stacked PRs #2 (schema), #3 (source discovery), #4 (public API), #5 (restricted preview); #1 is bootstrap `dev → main`.
- Current PR #5 branch has propagated upstream migration and discovery fixes.
- Python SQL/discovery/publication tests and Node Worker/preview tests, including test failures during integration and subsequent correction.
- Live official Windsor public portal index: https://opendata.citywindsor.ca/Tools/CouncilAgendas (read-only public page inspection only; no PDFs fetched).
- Deployment and D1 migration boundaries from AGENTS.md and docs/D1_MIGRATION_RUNBOOK.md.

## Remediation completed this session
1. **Version-bound publication approval:** `migrations/0005_publication_authorizations.sql` introduces reviewer-identified, revocable authorizations linked to a current version ID and SHA-256 and an exact item/meeting text snapshot. Public API SQL now requires this authorization; older `publication_reviews` entries are not accepted as sufficient publication authority. SQL triggers disallow approval against a non-current/uncleared version, retargeting, resurrection of revoked approvals, and deletion of authorization history. There is currently no reviewer-facing write API.
2. **Negative regression tests:** Synthetic tests exercise legacy-approval rejection, current-version and evidence-hash matching, authorization revocation, item/meeting corrections, document restrictions, and nondeletable audit history. API Worker tests assert the new query predicates.
3. **Source coverage:** The parser now recognizes official `In-Camera Agenda (Session N)` links as distinct public metadata (not a grant to fetch or publish confidential closed-session content).
4. **No silent truncation:** Meeting and per-meeting document bounds now raise explicit errors rather than quietly omitting official records.
5. **Stacked integration failure caught and fixed:** Initial propagation of PR #4's Worker into PR #5 replaced the preview-specific authentication function; the preview test failed (404 instead of 200). The preview auth logic was restored while retaining new publication SQL. Both latest PR #5 workflows now pass.

## Findings and merge/release gates

### HIGH — Independent review and authorization workflow remain open
- Independent reviewer must scrutinize migration 0005, Worker authorization and public query, privacy/copyright boundaries, source discovery, cross-repository isolation, dependency/branch integration, and all test fixtures. This audit was conducted by an implementation participant; it is not independent.
- Reviewer identity is currently stored as text in the database. No authenticated reviewer workflow exists; **do not expose mutation endpoints, import actual approvals, or publish live records** until identity verification, review authority, immutable provenance, and explicit reapproval rules are designed and security-tested.
- Public endpoint uses a single authorized current evidence version as a qualifying witness. A complex item with several supporting documents may need a complete reviewed evidence manifest; current single-version authorization alone is not proof that all pertinent supporting materials were reviewed. Define publication completeness policy before live release.
- Review/approval must be linked to a source version, content checksum, item and meeting fields and revoked on corrections. The new query and snapshot model improve the boundary but do not replace a real independent editorial policy.

### HIGH — Existing development D1 upgrade is separately blocked
- `civic-records-index-dev` contains legacy 0001/0002 executed directly through the Cloudflare API and no observed migration ledger. The new 0003–0005 migrations have **not** been applied there.
- Prerequisites: migration-ledger reconciliation; verified, restorable snapshot/Time Travel recovery point; schema preflight, FK and row-count checks; isolated D1 test of the **new 0005** as well as 0003/0004; explicit authorization for dev migration; transaction-aware process. Never rerun original 0001/0002 over existing tables.
- Previous disposable D1 verified 0003/0004 with synthetic linked records and was deleted. That test did not cover 0005.

### HIGH — Live Windsor ingest is not ready
- Official index publicly lists cancelled meetings, committees acting as boards, and numbered in-camera agenda session links. Matching labels is now improved.
- No capture-and-compare regression against the raw live HTML has been completed. The parser's `MAX_MEETINGS` and `MAX_LINKS_PER_MEETING` are safety bounds, not full historical coverage. CLI defaults to recent 45 days, not a historical backfill.
- Implement source-native session identifiers or explicit collision review, history/backfill windows, source change detection, coverage reconciliation, source-policy/rate-limit review, and auditable failures before scheduled ingest.
- Do not assume metadata for public in-camera agenda links authorizes distribution of closed-session contents.

### MEDIUM — Worker/public preview readiness
- Preview token authorization is non-deployed; Cloudflare Access, exact route and D1 dev-only binding, token rotation, secret storage and logging still require external configuration and assessment.
- PUBLIC API hostname access is intentionally unrestricted for verified public records; this does not authorize private datasets. No actual production route exists.
- No independent runtime penetration test, load test, operating budget guardrails, or live D1 compatibility validation of 0005 yet.

## Verified CI evidence
- PR #4 current integration (as of inspection): Schema and Worker runs passed after source and authorization changes.
- PR #5 merged integration commit `0b0269329e655fb00b74ecba45c52d2f03f2adaa`: Schema run 45084877195 and Worker run 45084877199 both **passed**.
- Earlier PR #5 integration run 45084793326 failed on a preview-auth regression; corrected in commit `8b43c9684e71ccbe431b27a0b0e5d69aba18f95e`. Preserve this regression history.

## Recommended independent reviewer checklist
- Inspect exact current heads of all five PRs, especially merge ancestry and README/docs inaccuracies.
- Independently execute full Python and Node tests, attempt publication-gate bypasses (approval revocation, stale evidence, forged reviewer, mutable item/meeting data, multiple documents), malicious portal content, SSRF/redirection tests and cross-host preview bypass tests.
- Review 0003–0005 SQL migration order and guarantee a clean fresh install plus legacy upgrade path without destructive table/FK side effects.
- Produce written PASS/REQUEST CHANGES verdict with reproducible evidence. **Do not merge, deploy, or modify live databases during review.**

## Integration decision
**REQUEST CHANGES / HOLD dev merge** until independent review is recorded, publication scope is explicitly approved for development-only integration, and any HIGH findings relevant to dev integration are closed or explicitly accepted by the project owner. Deployment, public publishing, paid inference and document deletion remain prohibited.
