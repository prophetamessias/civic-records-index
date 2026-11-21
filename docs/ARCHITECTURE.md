# Civic Records Index — architecture v0 (planned)

## System
Official municipality portals → municipality adapters → deterministic discovery → source/document version index (D1) → parsing and citation extraction → relationship/evidence validation → candidate briefings and approved public API → independent Council Office and VoterHub consumers.

## Data model planned
municipality, source_endpoint, meeting, agenda_item, document, document_version, item_document, resolution, vote, relationship, evidence_claim, agent_job, job_attempt, review_queue, cache_record, preservation_hold, deletion_manifest, audit_event. Each fact carries a citation to a source/version/page; each entity has stable local ID and source provenance.

## Agent stages
Discovery (scheduled code), Extraction (code plus optional OCR/LLM), Historical matching (retrieval/code), Verification (separate checks), Briefing (draft-only LLM), Public publishing (approval gated), Retention (dry-run, approval gated). Instrument calls and costs, provide idempotency keys, retries/backoff, injection isolation, provenance and human review.

## Storage
D1 stores metadata and verified public facts, never bulk PDF binaries. Official source URL and version fingerprint persisted. Temporary SharePoint cache optional and not configured. 90 days after associated meeting makes a cache copy eligible for review; completion of later official minutes, open research, link failure or hold blocks deletion.

## Security and publication
Public API is allowlisted fields/records with explicit verification and publication state. Council Office has independent private data storage; never use the shared index for constituent information. Source text is untrusted and cannot control agent instructions. No autonomous public publication or deletion.

## MVP milestone
Read-only Windsor discovery ingest with synthetic tests, database migrations, provenance API, daily scheduler, execution ledger and admin review dashboard. No paid AI usage by default.


## Meeting coverage and project domain (2026-11-21)
Windsor pilot indexes **every meeting shown on the official Council Agendas portal**, not merely regular Council sessions, and every public-facing linked material type. Recognize standing committees, special meetings, inaugural/orientation sessions, sessions sitting as boards, cancelled meetings, videos and item-level supporting documents. Treat cancelled meeting as an event with status, not as a decision.
The user has selected a subdomain under **dcmc.ca** for Civic Records Index. Proposed hostname: `records.dcmc.ca` for future documentation/research interface; optional `api.records.dcmc.ca` for API, subject to later confirmation and DNS planning. No DNS, zone changes or deployment are authorized by this design record.
