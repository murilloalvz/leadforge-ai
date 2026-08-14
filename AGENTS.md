# AGENTS.md

This file defines the working rules for AI coding agents contributing to LeadForge AI.

## Mission

Build LeadForge AI incrementally as a real B2B opportunity intelligence product. Favor correctness, evidence, maintainability, and testability over feature volume.

## Current scope

The current milestone is **v0.2 — Site Analyzer**.

Do not implement later roadmap items unless explicitly requested.

v0.2 includes:

- the v0.1 backend foundation;
- deterministic Automation Opportunity Scoring;
- deterministic AI Discoverability scoring;
- one-URL-at-a-time public site analysis;
- safe HTTP fetching with SSRF-oriented validation;
- redirect, timeout, and response-size limits;
- `robots.txt`, `noindex`, `X-Robots-Tag`, HTML text, headings, and JSON-LD analysis;
- persisted site audits that may optionally reference a prospect;
- site-audit API endpoints;
- tests, migrations, CI, and accurate documentation.

Do **not** implement broad web crawling, automatic business discovery, JavaScript execution, LLM analysis, outreach sending, demo generation, or production deployment yet.

## Engineering rules

1. Inspect the repository before making changes.
2. Write a short implementation plan before broad changes.
3. Keep changes small and reviewable.
4. Prefer simple, readable code over premature abstractions.
5. Run tests and linting after meaningful changes.
6. Never hide failing tests or errors.
7. Avoid placeholder TODOs when a small real implementation is possible.
8. Keep external providers behind interfaces when credentials would otherwise be required.
9. The project must remain runnable in demo mode without secrets.
10. Do not deploy, merge, send outreach, or perform destructive actions without explicit human authorization.

## Data integrity

The product must distinguish:

- observed facts;
- inference;
- hypothesis;
- recommendation.

Never turn absence of evidence into evidence of absence.

Every externally derived fact should preserve provenance such as source URL, observation time, and confidence when applicable.

## Automation Opportunity Scoring

The commercial opportunity score must be deterministic, explainable, and versioned.

LLMs may later interpret evidence, but they must not silently generate the canonical score.

Scoring output should expose:

- total score;
- confidence;
- version;
- components;
- explanation.

`confidence` represents evidence coverage, not probability of closing a sale.

Weights must be documented and should eventually be recalibrated from real outcomes.

## AI Discoverability

AI Discoverability is a separate diagnostic from Automation Opportunity Scoring.

Never blend both into one opaque score.

The site diagnostic may measure verifiable readiness signals such as:

- public accessibility;
- indexability;
- relevant crawler access;
- important content available as text;
- clear business identity, services, and location;
- descriptive page titles;
- useful structured data that matches visible content.

Do not claim that a score predicts whether ChatGPT, Google, or another AI system will recommend a business.

Do not award points for speculative "AI SEO hacks", `llms.txt`, invented markup, or other signals without reliable evidence that they matter.

Store score version, confidence, supporting signals, and evidence separately from the automation score.

## Site fetching and SSRF

Any server-side fetcher that accepts user-controlled URLs must be treated as security-sensitive.

At minimum:

- allow only HTTP/HTTPS;
- reject credentials embedded in URLs;
- reject localhost, loopback, private, link-local, reserved, and metadata destinations;
- validate DNS results before requests;
- revalidate every redirect target;
- use timeouts;
- cap redirects;
- cap response size;
- avoid inheriting arbitrary proxy configuration;
- do not execute JavaScript in v0.2.

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
- Do not bypass authentication, CAPTCHAs, paywalls, rate limits, or anti-bot systems.
- Prefer official APIs and permitted public sources.

## Privacy and outreach

LeadForge is for legitimate B2B prospecting.

Do not build features for:

- collecting private personal data;
- scraping unnecessary individual-level information;
- deceptive identities;
- fabricated claims;
- automated mass spam;
- review manipulation;
- unsolicited sending without a human-review layer.

Any future outreach feature must default to `awaiting_human_review`.

Support a `do_not_contact` state.

## Demo data

All customer/lead data shown in demos must be fictional.

Seed/demo companies should also be clearly marked fictional unless explicitly created from permitted public sources in a later milestone.

## Git workflow

- Do not push, merge, or create releases without explicit user authorization.
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
