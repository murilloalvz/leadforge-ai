# LeadForge AI — Architecture

## Goal

LeadForge AI turns public business signals into explainable B2B automation opportunities.

The architecture is intentionally modular so the MVP can start small while preserving clear boundaries for future providers, LLM analysis, demo generation, CRM workflows, and quality monitoring.

## High-level flow

```text
Discovery Provider
      ↓
Prospect normalization
      ↓
Evidence / enrichment
      ↓
Deterministic scoring
      ↓
AI opportunity analysis
      ↓
Solution recommendation
      ↓
Offer + demo generation
      ↓
Human review
      ↓
CRM workflow
```

## Planned modules

### Discovery

Responsible for finding candidate businesses from permitted public sources.

Contract should return normalized company records without coupling the rest of the application to a specific provider.

Initial v0.1 implementation: fictional seed data only.

### Enrichment

Collects observable business signals and stores evidence with provenance.

Examples:

- public website;
- WhatsApp/contact links;
- forms;
- visible scheduling flows;
- public service catalog;
- visible automation signals;
- public activity indicators.

This module is not part of v0.1 beyond data-model preparation if useful.

### Opportunity Scoring

Deterministic rules produce an explainable 0–100 score.

The canonical score must not depend on an LLM.

Expected output:

```json
{
  "total": 78,
  "confidence": 0.82,
  "components": [
    {
      "signal": "whatsapp_present",
      "value": true,
      "weight": 10,
      "contribution": 10
    }
  ],
  "explanation": "..."
}
```

### AI Opportunity Analyst

Future milestone.

Consumes structured evidence and scoring output, then separates:

- observed facts;
- hypotheses;
- likely pain points;
- automation opportunities;
- recommended solution;
- missing information.

LLM output must be schema-validated.

### Solution Recommender

Maps opportunity patterns to a catalog of reusable automation solutions.

Initial planned catalog:

- lead qualification;
- follow-up automation;
- appointment funnel;
- lead dashboard.

### Outreach Generator

Future milestone.

Produces evidence-grounded outreach drafts only. It does not send messages automatically in the MVP.

All generated outreach enters a human-review state.

### Demo Generator

Future milestone.

Builds a prospect-specific demonstration from reusable templates. All customer-level demo data must be fictional and visibly labeled as such.

### CRM

Tracks the prospect lifecycle:

```text
discovered
→ analyzed
→ high_priority
→ offer_generated
→ demo_ready
→ ready_for_review
→ contacted
→ replied
→ meeting
→ proposal
→ won / lost / do_not_contact
```

### Quality Monitor

Future recurring product.

Evaluates deployed automation/AI conversations for:

- failures;
- abandoned leads;
- poor responses;
- escalation quality;
- resolution;
- conversion;
- regressions over time.

## Initial project shape

```text
leadforge-ai/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   │   ├── discovery/
│   │   │   ├── enrichment/
│   │   │   ├── scoring/
│   │   │   ├── opportunity_analysis/
│   │   │   ├── recommendation/
│   │   │   ├── outreach/
│   │   │   └── demo_generation/
│   │   └── main.py
│   └── tests/
├── frontend/
├── docs/
├── sample_data/
├── scripts/
├── .env.example
├── .gitignore
├── AGENTS.md
└── README.md
```

The actual implementation should create only directories that are useful for the current milestone. Empty architecture theater is discouraged.

## Data model principles

Every externally observed signal should eventually support:

- value;
- source/provenance;
- observation timestamp;
- confidence;
- optional raw evidence reference.

A prospect should preserve current state while important lifecycle changes are captured in activity/history records.

## Security boundaries

Future network-fetching code must:

- use allowlisted schemes (`http`, `https`);
- reject localhost/private/link-local/metadata destinations;
- use DNS/IP validation against SSRF;
- use strict timeouts;
- enforce response-size limits;
- avoid arbitrary code/JavaScript execution;
- respect source terms and rate limits.

Secrets live in environment variables and never in source control.

## Development philosophy

1. Build v0.1 without external dependencies on paid APIs.
2. Validate the domain model and scoring first.
3. Add evidence ingestion second.
4. Add LLM interpretation only after deterministic behavior is testable.
5. Add outreach generation only after evidence quality is trustworthy.
6. Add real-world automation/quality monitoring only after the prospecting workflow proves useful.
