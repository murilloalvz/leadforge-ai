# AGENTS.md

LeadForge is a **commercial copilot for freelancers**. Do not redefine it as a web-development-only, automation-only, SEO-only or lead-list product. `web_development` is only the first active OpportunityModule.

Read before broad changes:

- `docs/PRODUCT_VISION.md`
- `docs/ROADMAP.md`
- `docs/ARCHITECTURE.md`
- `docs/DISCOVERY_PROVIDERS.md`
- `docs/WEB_EVIDENCE.md`
- `docs/CALIBRATION.md`
- `docs/EXPORT.md`
- `docs/MVP_VALIDATION.md`

## Current scope

Current implementation: **v0.3.6 — Discovery Provider hardening**.

- Geoapify is the preferred persistent provider when configured;
- OpenStreetMap/Overpass is an experimental fallback;
- `mock` remains deterministic;
- `provider="auto"` selects Geoapify when its API key exists, otherwise Overpass;
- CI runs automatically on PR/main, not every feature-branch push.

Google Places was evaluated but must not be reintroduced as the canonical persistent prospect source without resolving its current caching/storage policy mismatch with LeadForge's persistence/export model.

A real Geoapify coverage/latency validation is pending a configured API key outside the repository.

Do not implement FreelancerProfile, compatibility scoring, pricing, LLM/chat, outreach, proposals, demos, extra service modules, bulk crawling or production deployment during this gate.

## Architecture

Shared concepts remain service-category agnostic: Prospect, Evidence, DiscoveryProvider, Site Analyzer, OpportunityAssessment and export contracts. Service-specific rules belong under `services/opportunity/<service_category>/`.

New service scores belong in OpportunityAssessment, not legacy `Prospect.score*` fields.

## Evidence integrity

Distinguish `confirmed`, `strong_signal`, `inference` and `unknown`. Never turn absence of evidence into evidence of absence. Do not invent Core Web Vitals, real responsiveness, conversion rate, budget or internal pain from static HTML.

## Discovery provider rules

Providers must remain replaceable.

### Geoapify

- API keys must never be committed or logged;
- store only fields needed by LeadForge and minimal provenance;
- preserve required OpenStreetMap attribution and Geoapify attribution when applicable;
- keep queries small and user-triggered;
- treat 429/5xx/timeouts as provider failures, not empty results;
- do not expand enrichment fields/volume without reviewing cost and terms.

### OpenStreetMap/Overpass

- experimental, not production infrastructure;
- no bulk harvesting from shared public infrastructure;
- no indefinite timeout increases to hide instability;
- external failures remain observable;
- missing OSM fields remain unknown.

### Mock

Keep deterministic mock data so tests/development work without secrets or external network.

## Calibration and validation

Small samples are smoke benchmarks, not proof of general accuracy. Fix collector/detector errors before changing scoring weights and add regression tests for real bugs. Workflows dependent on live sites or paid providers should remain manual/credential-gated.

## Export

Exports are snapshots of persisted runs. Never re-run discovery or Site Analyzer during export. Preserve certainty/evidence, keep AI Discoverability separate, protect CSV text against formula injection and version public JSON contracts.

## Site fetching and SSRF

Only HTTP/HTTPS; reject embedded credentials, localhost/private/link-local/reserved/metadata destinations; validate DNS and redirects; use timeouts; cap redirects/response size; avoid arbitrary proxy inheritance; no third-party JS execution in the current milestone.

## Engineering rules

1. Inspect before broad changes.
2. Keep milestones small, functional and testable.
3. Never weaken tests to pass CI.
4. Keep external providers behind interfaces.
5. Project must run in mock/test mode without secrets.
6. Do not deploy, create PRs, merge, send outreach or perform destructive actions without explicit authorization.

## Security and privacy

Never commit secrets or private customer data. Do not bypass authentication, CAPTCHA, paywalls, rate limits or anti-bot systems. Do not build deceptive identities, fabricated claims, mass spam or review manipulation.

A milestone is done only when behavior matches scope, lint/tests pass, migrations work from a clean database, docs match reality, no secrets are present and future features are not disguised as complete.
