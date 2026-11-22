# Database foundation (prototype)

Run the migration and its checks locally (Python 3.10+):

```bash
python -m unittest discover -s tests -v
```

The baseline migration is SQLite-compatible for future Cloudflare D1 deployment. It has not been deployed to Cloudflare. No database credentials or downloaded municipal PDFs are included.

The records distinguish agenda proposals, committee recommendations, adopted resolutions, explicitly recorded votes, document versions, evidence claims, job runs, and retention approvals.

**Important safeguards not yet implemented:** permission-checked publication APIs, cache deletion service, polymorphic relationship existence validation, full cache/hold eligibility evaluation, link version validation and external data ingestion. Database constraints alone do not authorize publication or deletion. All operational workflows remain disabled.

All test records are synthetic, even where a municipality and meeting date are used as identifiers. For initial integration, design API-level access policies before enabling public endpoints.


## Integrity review (2026-11-22)
Baseline `0001_core.sql` now accepts distinct same-day meeting IDs, guards un-hashed duplicate source observations, checks document ownership and record references, and blocks deletion approval/execution. Tests use synthetic records only. **This is a corrected fresh-install baseline, not an upgrade to the already-created Cloudflare D1.** The existing development database has `0001` and `0002` installed by direct API; before any live migration, reconcile Wrangler's migration ledger, back up/inspect D1, and write/test a separate forward-only migration. Do not rerun or overwrite `0001` on that database. Manual review and publication gates remain mandatory.
