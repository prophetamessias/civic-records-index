# Architecture and product decisions

## 2026-11-21 — Independent shared service
Civic Records Index is a separate open-source project. Council Office and VoterHub consume verified public information via different interfaces and permissions. Do not share Council Office private data with VoterHub.

## 2026-11-21 — Open-source boundary
Code MIT-licensed; repository contains synthetic fixtures and documented links, not scraped PDF bundles or private credentials. Data reuse/copyright assessed separately by source.

## 2026-11-21 — Source-first retention
Official public URL is primary reference. Database persists metadata, evidence links, relationships and version identities; SharePoint may cache PDFs. The 90-day clock starts on meeting date and triggers eligibility REVIEW only. Holds, source validation and human approval required before any deletion.

## 2026-11-21 — Initial runtime and cost posture
Plan Cloudflare Workers + D1 for indexes; only build/deploy after verification. Discovery, checksum, parsing and link checks are deterministic first. Optional specialized AI agents later, bounded budgets, provenance checks and publication gates. No live services deployed at bootstrap.

## 2026-11-21 — Branches and agent collaboration
`main` stable and `dev` active integration. Feature branches/PR review recommended. One writing agent at a time; shared AGENTS.md and lightweight CLAUDE.md/GEMINI.md.


## 2026-11-21 — Portal-wide meeting scope and domain
Windsor discovery encompasses all meeting entries and published source links on the official Council Agendas portal, not just City Council. Must include committee and board sittings, special and inaugural/orientation meetings, cancelled events and item-level attachments/videos with provenance. Future service will use a subdomain of dcmc.ca; records.dcmc.ca is the current proposal, not configured. No live DNS change or deployment.

## 2026-11-21 — Hostnames confirmed
The user approved **records.dcmc.ca** for the Civic Records Index public interface and **api.records.dcmc.ca** for its separately hosted API. Domain names are final choices, but no DNS records are provisioned or traffic routes deployed pending service readiness, source verification and rollout review.


## 2026-11-22 — Version-bound publication authorization (proposed, feature branch)
A public release requires an explicit reviewer-identified authorization for the exact current, verified, rights-cleared source version and its SHA-256, together with the exact published item/meeting field snapshot. Legacy per-item review flags cannot authorize public release by themselves. Authorized snapshots are revocable and their history immutable. No reviewer write endpoint exists yet; independent security review and development deployment approvals are required. The evidence completeness policy must evaluate all pertinent documents, not just one qualifying version.


## 2026-11-26 — Prioritize working records-and-councillor MVP over municipal suite
Maintain Civic Records Index as independent public-records integration layer; do **not** fork it for the immediate deliverable. Build the councillor-facing meeting/agenda/document workspace in the separate Council Office project, with private user notes/tasks stored there; VoterHub Next remains a separate public-only consumer. First deliver reliable Windsor all-meetings ingestion, agenda and supporting-document tracking with revisions/source links, protected preview and a usable authorized councillor pilot. Vendor-neutral formats/API adapters and a future larger legislative management suite are important but defer broader suite development and procurements-specific functionality. Do not wait for FOI documents before implementing verified public-data ingestion. Protect security and publication gates rather than bypassing them for speed.
