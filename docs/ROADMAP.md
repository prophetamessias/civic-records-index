# Delivery plan

1. **Foundation**: repository instructions/branches, schema proposal, fixtures and unit tests.
2. **MVP ingest**: Windsor official agenda and minutes discovery, version detection, deterministic metadata extraction, D1 writes with idempotency; no AI.
3. **Evidence**: link report and decision numbers, verify against original minutes, review queue.
4. **Agent orchestration**: specialized bounded jobs, per-job metrics and cost limits, prompt-injection defenses, draft-only output.
5. **Consumers**: separately authorized public API for VoterHub and research API for Council Office; shared public index only.
6. **Cache**: SharePoint adapter, 90-day review eligibility, approval logs and safe cleanup. No automatic delete.

Acceptance: new Windsor meeting ingested without duplication, each fact traceable, failure recoverable, publication and deletion disabled without authorization, tests passing and zero unwanted paid AI activity.
