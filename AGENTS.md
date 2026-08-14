# AGENTS.md

This file defines working rules for AI coding agents contributing to LeadForge AI.

## Canonical product vision

LeadForge is a **commercial copilot for freelancers**.

Do not redefine LeadForge as a web-development-only, automation-only, SEO-only or lead-list product. `web_development` is only the first active OpportunityModule.

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

Current implementation version: **v0.3.6 — Discovery Provider hardening**.

Implemented in this milestone:

- Google Places API (New) Text Search provider;
- OpenStreetMap/Overpass preserved as experimental fallback;
- deterministic mock provider preserved;
- `provider="auto"` selects Google Places when its API key exists and Overpass otherwise;
- explicit Google FieldMask and bounded page size;
- provider credentials only through environment/configuration;
- deterministic Google provider tests without real secrets;
- CI automatic on PR/main, not every feature-branch push.

A real Google Places coverage/latency validation is still pending a configured API key outside the repository.

Do **not** implement FreelancerProfile, compatibility scoring, pricing, LLM/chat, outreach, proposals, demos, extra service modules, bulk crawling or production deployment during this gate.

## Architectural boundaries

Shared infrastructure must remain service-category agnostic:

- Prospect;
- Evidence;
- DiscoveryProvider;
- Site Analyzer / future analyzers;
- OpportunityAssessment;
- export contracts.

Service-specific rules belong under `services/opportunity/<service_category>/`.

Do not put new service-category scores directly on `Prospect`; those legacy score fields predate OpportunityAssessment.

## Evidence integrity

The product must distinguish:

- `confirmed`;
- `strong_signal`;
- `inference`;
- `unknown`.

Never turn absence of evidence into evidence of absence. Scope claims to what the collector actually observed.

Do not invent Core Web Vitals, real responsiveness, conversion rate, business budget or internal operational pain from static HTML.

## Discovery provider rules

Providers must remain replaceable behind the common contract.

### Google Places

- API keys must never be committed or logged.
- Keep FieldMask explicit; never use `*` in production code.
- Adding a field is also a cost/privacy decision and requires review.
- Persist only the normalized business fields needed by LeadForge plus minimal provenance.
- Do not persist reviews, photos or unrelated atmosphere data for the current MVP.
- Respect provider terms and current pricing documentation.
- Treat 429/5xx/timeouts as provider failures, not empty search results.

### OpenStreetMap/Overpass

Overpass is experimental, not production infrastructure.

- queries must remain small, sequential and user-triggered;
- no bulk harvesting from shared public infrastructure;
- no indefinite timeout increases to hide instability;
- external 5xx/timeouts must remain observable;
- missing OSM fields remain unknown.

### Mock provider

Keep a deterministic mock provider so the project and tests can run without secrets or external network access.

## Calibration and live validation

Small samples are smoke benchmarks, not proof of general accuracy.

Prefer fixing detector/collector errors before changing scoring weights. Add regression tests for concrete bugs discovered from real examples.

Workflows that depend on live third-party websites or paid providers should be manual or credential-gated; normal CI must remain deterministic.

## Export rules

Exports are snapshots of persisted Discovery Runs.

- never re-run discovery or Site Analyzer during export;
- preserve certainty/evidence, not only a final score;
- keep AI Discoverability separate from service opportunity;
- protect external text against CSV formula injection;
- version public JSON contracts when their structure changes.

## Site fetching and SSRF

User-controlled URLs are security-sensitive.

At minimum:

- HTTP/HTTPS only;
- reject embedded credentials;
- reject localhost, private, link-local, reserved and metadata destinations;
- validate DNS results;
- revalidate redirects;
- use timeouts;
- cap redirects and response size;
- avoid arbitrary proxy inheritance;
- do not execute third-party JavaScript in the current milestone.

Current DNS-before-connect validation is MVP protection, not perfect network isolation.

## Engineering rules

1. Inspect the repository before broad changes.
2. Keep milestones small, functional and testable.
3. Prefer readable code over speculative abstractions.
4. Run lint/tests after meaningful changes.
5. Never hide failures or weaken tests just to pass CI.
6. Keep external providers behind interfaces.
7. The project must run without secrets in demo/test mode.
8. Do not deploy, create PRs, merge, send outreach or perform destructive actions without explicit human authorization.

## Security and privacy

Never commit secrets or private customer data.

Do not bypass authentication, CAPTCHA, paywalls, rate limits or anti-bot systems.

Do not build deceptive identities, fabricated claims, automated mass spam or review manipulation.

## Definition of done

A milestone is done only when behavior matches scope, lint/tests pass, migrations work from a clean database, docs match reality, no secrets are present and future features are not disguised as complete.
