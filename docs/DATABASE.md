# Database foundation (prototype)

Run the migration and its checks locally (Python 3.10+):

```bash
python -m unittest discover -s tests -v
```

The baseline migration is SQLite-compatible for future Cloudflare D1 deployment. It has not been deployed to Cloudflare. No database credentials or downloaded municipal PDFs are included.

The records distinguish agenda proposals, committee recommendations, adopted resolutions, explicitly recorded votes, document versions, evidence claims, job runs, and retention approvals.

**Important safeguards not yet implemented:** permission-checked publication APIs, cache deletion service, polymorphic relationship existence validation, full cache/hold eligibility evaluation, link version validation and external data ingestion. Database constraints alone do not authorize publication or deletion. All operational workflows remain disabled.

All test records are synthetic, even where a municipality and meeting date are used as identifiers. For initial integration, design API-level access policies before enabling public endpoints.
