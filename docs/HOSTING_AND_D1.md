# Approved service hostnames and deployment plan

**Decision (2026-11-21):**
- `records.dcmc.ca` — future public-facing index information/research interface.
- `api.records.dcmc.ca` — future read-only API of verified and explicitly publication-approved public civic data.

These are the **approved final hostnames**; they are not DNS records yet. User approval of names is not approval to direct traffic to an unavailable service.

## Current implementation
`src/worker.mjs` contains a non-deployed Cloudflare Workers-compatible module. It serves:
- `GET /health` on the API hostname without exposing database contents.
- `GET /v1/agenda-items`, read-only D1 query, returning only records with verified meeting dispositions, reviewer-approved publication, and at least one evidence document verified and rights-cleared.
- A static informational landing page on `records.dcmc.ca`; no live documents or searches are published.

No administrative dashboard is exposed publicly. No private Council Office or VoterHub information is stored in the shared D1 schema. Both consumers should use this shared *public* API with independent private-domain data stores.

The API is explicitly **not deployed or bound**; no database instance exists. Source discovery Python code is also not scheduled or deployed, and its local SQLite write flag is unrelated to D1.

## Pre-deployment checklist
1. Merge/review stacked PRs in dependency order; run tests and independent review.
2. Confirm Cloudflare account and `dcmc.ca` zone access, existing DNS records, billing state and certificate availability.
3. Review current Cloudflare Workers/D1 CLI and deployment configuration. The project has not selected/deployed a runtime config; do not invent database IDs, secrets, or hostnames.
4. Create a separate non-production D1 instance using a reviewed migration plan. Verify migrations with `PRAGMA foreign_keys=ON` and schema tests. No production data migration without backup.
5. Configure `DB` binding; validate API only on intended hostnames, and add authentication/Cloudflare Access for any future admin/agent operations.
6. Test service endpoints and errors in a restricted preview environment. Add a *real* live-portal HTML fixture only after verifying source fetch/legal terms; assess timeouts, pagination, title collisions, redirects and version drift.
7. Confirm route/domain mappings, TLS, and DNS record values derived from actual deployed Worker routes.
8. Obtain explicit human approval before enabling routes, schedule, automated publishing, or any paid LLM inference. No automatic deletion.
9. Monitor usage/costs, failure alerts, access and provenance. Roll back when checks fail.

## Test locally with zero network/billing
```bash
node --test tests/*.test.mjs
python -m unittest discover -s tests -v
```

## Source publication rule
Schema-level rights approval is **not** a substitute for a comprehensive publication policy; before production, approve exact fields and data sets, moderation/review procedure, permitted reuse, evidence version integrity and cache/HTTP semantics. No public PDF redistribution without explicit licence analysis.

## Read-only Cloudflare DNS inventory — 2026-11-21
- Connected Cloudflare account includes an **active** zone for `dcmc.ca`.
- An exact-name lookup found **zero existing DNS records** at `records.dcmc.ca` and **zero** at `api.records.dcmc.ca`.
- No DNS records were created, updated or removed. No Worker route or D1 database was provisioned.
- This snapshot must be rechecked immediately before any deployment; absent records are not themselves routing configuration. Do not pre-create CNAME records pointing to guessed Worker destinations.
