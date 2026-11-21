# Development D1 and restricted Worker preview

**Status: 2026-11-21.** This is a *non-production* setup. No Worker, route, schedule or DNS is deployed yet.

## Isolated D1 database — created and schema validated

- Cloudflare account: existing account containing the active `dcmc.ca` zone.
- D1 name: `civic-records-index-dev`
- D1 ID (non-secret resource identifier): `78b3d94a-4a43-4e9c-a8bf-9a7517e1c55b`
- Region hint: `enam`; read replicas disabled at creation.
- Installed directly through the authenticated Cloudflare D1 query API: `migrations/0001_core.sql` and `migrations/0002_meeting_documents.sql`. The schema has 18 application tables (plus Cloudflare internal table).
- Verified counts as of 2026-11-21: 0 municipalities, 0 meetings, 0 documents, 0 job runs. There is no imported civic content.
- **Migration caveat:** direct API execution does not necessarily create Cloudflare CLI migration bookkeeping. Before adopting CLI-managed migrations, inspect its migration table and reconcile the existing development database. Do not blindly reapply the same `CREATE TABLE` statements or invent a migration history.
- Other databases (`voterhub-next-dev`, `operations-control-db`, `jeremy-renaud-campaign-db`, `voterhub-v3-dev`) were not changed.

## Future private preview (not enabled)

Cloudflare Worker source: `src/worker.mjs`. The preview entry point accepts a third, **exact** hostname only when all three secrets/settings are supplied:

- `PREVIEW_ENABLED=true`
- `PREVIEW_HOST=<exact assigned private-preview hostname>`
- `PREVIEW_TOKEN=<random secret of at least 24 characters, created in Cloudflare secret storage>`

Every request on that hostname must carry `Authorization: Bearer <token>`. Failed authentication returns 404. The token is never committed or sent in a URL/query string. Use Cloudflare Access as an additional edge-level gate before any preview goes live. Test strict hostname matching: production `records.dcmc.ca` and `api.records.dcmc.ca` remain separately approved but **unconfigured** DNS names.

The Worker serves only `GET`/`HEAD` and does not expose research drafts, internal agent state, caches or private records. D1 `DB` binding must reference the **development database only**. The public API query requires verified outcomes, review approval and rights-cleared evidence and returns no content while the dev database is empty.

Do not copy the preview token to GitHub, source comments, screenshots, or public logs.

## Before preview deployment

1. Review PR #1 (foundation) → #2 (schema) → #3 (discovery) → #4 (public API) → #5 (private preview), preserving branch dependencies.
2. Confirm the chosen Cloudflare deployment CLI and configuration from **current official documentation**. Do not guess account IDs, routes, DB IDs or generate a `workers.dev` address.
3. Verify Node and Python test runs actually executed their tests. This PR fixes an earlier Node CI glob bug where green output included **zero** Node tests.
4. Perform independent security review of preview bearer secret, CORS, source-rights publication query, and actual D1 binding.
5. Test in a protected development Worker environment with Cloudflare Access; only then configure any staging hostname/route, with explicit deployment approval.
6. Establish source-specific fetch rate limiting and validate the actual Windsor portal HTML before enabling a recurring discovery schedule.
7. Keep production DNS untouched until public release is separately approved. No paid AI, automatic publication or document deletion.

## Read-only D1 checks

Use authenticated Cloudflare API read queries (not production data):

```sql
SELECT name FROM sqlite_master
WHERE type='table' AND name NOT LIKE 'sqlite_%'
ORDER BY name;

SELECT COUNT(*) AS meetings FROM meetings;
SELECT COUNT(*) AS documents FROM documents;
SELECT COUNT(*) AS job_runs FROM job_runs;
```

Cloudflare free-tier D1 limits apply. Avoid paid inference until separately approved.
