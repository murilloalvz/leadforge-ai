# AGENTS.md

This file defines the working rules for AI coding agents contributing to LeadForge AI.

## Mission

Build LeadForge AI incrementally as a real B2B opportunity intelligence product. Favor correctness, evidence, maintainability, and testability over feature volume.

## Current scope

The current milestone is **v0.3 — Discovery Engine**.

Do not implement later roadmap items unless explicitly requested.

v0.3 includes:

- the v0.2 backend and Site Analyzer;
- a provider abstraction for business discovery;
- a deterministic mock provider;
- a small interactive OpenStreetMap/Overpass provider;
- discovery runs by niche, city, state and result limit;
- prospect deduplication and reuse;
- preservation of source/provenance;
- limited, opt-in site audits during a discovery run;
- independent Automation Opportunity and AI Discoverability diagnostics;
- explicit priority buckets instead of one blended opaque score;
- persisted discovery runs and candidates;
- API endpoints, tests, migrations, CI and accurate documentation.

Do **not** implement broad crawling, bulk harvesting, JavaScript execution, LLM analysis, automated outreach, demo generation or production deployment yet.

## Discovery rules

Discovery providers must remain replaceable. The orchestration layer must not depend on provider-specific response shapes.

Public sources must be used conservatively and in accordance with their usage policies. In particular:

- do not turn public Overpass infrastructure into a bulk lead database;
- keep discovery queries user-triggered, small and sequential;
- do not parallelize provider calls merely to increase throughput;
- preserve source attribution where required;
- store only the business fields needed by the product;
- avoid persisting unrelated or unnecessary personal/contact fields from raw provider payloads.

Provider absence is not evidence of business absence. A missing website, WhatsApp or phone tag from a discovery source must remain unknown unless another explicit check establishes absence.

## Engineering rules

1. Inspect the repository before making changes.
2. Write a short implementation plan before broad changes.
3. Keep changes small and reviewable.
4. Prefer simple, readable code over premature abstractions.
5. Run tests and linting after meaningful changes.
6. Never hide failing tests or errors.
7. Avoid placeholder TODOs when a small real implementation is possible.
8. Keep external providers behind interfaces.
9. The project must remain runnable in demo mode without secrets.
10. Do not deploy, merge, send outreach or perform destructive actions without explicit human authorization.

## Data integrity

The product must distinguish:

- observed facts;
- inference;
- hypothesis;
- recommendation.

Never turn absence of evidence into evidence of absence.

Every externally derived fact should preserve provenance such as source URL, observation time and confidence when applicable.

## Automation Opportunity Scoring

The commercial opportunity score must be deterministic, explainable and versioned.

LLMs may later interpret evidence, but they must not silently generate the canonical score.

Scoring output should expose total score, confidence, version, components and explanation.

`confidence` represents evidence coverage, not probability of closing a sale.

Discovery may contribute only signals actually supported by the source. Do not manufacture negative signals from missing provider fields.

## AI Discoverability

AI Discoverability is a separate diagnostic from Automation Opportunity Scoring.

Never blend both into one opaque score.

The site diagnostic may measure verifiable readiness signals such as public accessibility, indexability, relevant crawler access, textual content, clear identity/services/location, descriptive titles and useful structured data.

Do not claim that a score predicts whether ChatGPT, Google or another AI system will recommend a business.

The Discovery Engine may order candidates with explicit priority buckets, but the underlying scores and confidence values must remain independently visible.

## Site fetching and SSRF

Any server-side fetcher that accepts user-controlled URLs must be treated as security-sensitive.

At minimum:

- allow only HTTP/HTTPS;
- reject credentials embedded in URLs;
- reject localhost, loopback, private, link-local, reserved and metadata destinations;
- validate DNS results before requests;
- revalidate every redirect target;
- use timeouts;
- cap redirects;
- cap response size;
- avoid inheriting arbitrary proxy configuration;
- do not execute JavaScript in the current milestone.

The current DNS-before-connect validation is MVP protection, not perfect network isolation. Before exposing the fetcher as a public production service, harden it against DNS rebinding / TOCTOU and infrastructure-specific proxy behavior.

## LLM rules

When LLM functionality is introduced later:

- use structured outputs;
- validate responses with Pydantic;
- keep prompts versioned;
- separate provider interface from provider implementation;
- include a deterministic mock provider;
- never present model hypotheses as facts;
- test unsupported-claim behavior.

## Security

Never commit secrets.

- `.env` must remain ignored.
- `.env.example` contains placeholders only.
- Do not log tokens or credentials.
- Do not bypass authentication, CAPTCHAs, paywalls, rate limits or anti-bot systems.
- Prefer official APIs and permitted public sources.

## Privacy and outreach

LeadForge is for legitimate B2B prospecting.

Do not build features for collecting private personal data, scraping unnecessary individual-level information, deceptive identities, fabricated claims, automated mass spam or review manipulation.

Any future outreach feature must default to `awaiting_human_review` and support `do_not_contact`.

## Demo data

All customer/lead data shown in demos must be fictional.

Seed/demo companies should be clearly marked fictional unless explicitly created from permitted public sources.

## Git workflow

- Do not push, merge or create releases without explicit user authorization.
- Prefer focused commits with meaningful messages.
- Do not rewrite history unless explicitly requested.
- Before proposing a commit, summarize changed files and tests run.

## Definition of done for a milestone

A milestone is done only when:

- implemented behavior matches the requested scope;
- tests pass;
- linting passes;
- migrations work from a clean database;
- setup instructions are accurate;
- no secrets are present;
- major architecture decisions are documented;
- unfinished future features are not disguised as complete.
