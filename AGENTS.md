# AGENTS.md

This file defines the working rules for AI coding agents contributing to LeadForge AI.

## Mission

Build LeadForge AI incrementally as a real B2B opportunity intelligence product. Favor correctness, evidence, maintainability, and testability over feature volume.

## Current scope

The current milestone is **v0.1 — Foundation**.

Do not implement future roadmap items unless explicitly requested.

v0.1 includes:

- backend project structure;
- FastAPI application;
- SQLAlchemy models;
- Alembic migrations;
- SQLite local database;
- fictional seed data;
- deterministic Opportunity Scoring v1;
- minimal prospect list/detail API;
- tests;
- linting and typing configuration;
- updated README setup instructions.

Do **not** implement real crawling, LLM analysis, outreach sending, demo generation, or production deployment yet.

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
10. Do not deploy, publish, send outreach, or perform destructive actions without explicit human authorization.

## Data integrity

The product must distinguish:

- observed facts;
- inference;
- hypothesis;
- recommendation.

Never turn absence of evidence into evidence of absence.

Every externally derived fact should eventually support provenance metadata such as source, timestamp, and confidence.

## Opportunity scoring

The primary opportunity score must be deterministic and explainable.

LLMs may later interpret evidence, but they must not silently generate the canonical score.

Scoring output should expose:

- total score;
- confidence;
- components;
- explanation.

Weights must be configurable and documented.

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
- Network fetchers must use timeouts and response-size limits.
- Protect server-side fetchers against SSRF.
- Do not access loopback, private, link-local, or metadata-service addresses from arbitrary URLs.
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
- setup instructions are accurate;
- no secrets are present;
- major architecture decisions are documented;
- unfinished future features are not disguised as complete.
