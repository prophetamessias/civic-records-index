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
