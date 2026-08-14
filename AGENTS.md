# AGENTS.md

This file defines working rules for AI coding agents contributing to LeadForge AI.

## Canonical product vision

LeadForge is a **commercial copilot for freelancers**.

The long-term product should help a freelancer describe what they can do, find companies that may need those skills, explain the evidence behind each opportunity, and later assist with compatibility, pricing, outreach, proposals and demos.

Do not redefine LeadForge as a web-development-only, automation-only, SEO-only or lead-list product.

Read before broad changes:

- `docs/PRODUCT_VISION.md`
- `docs/ROADMAP.md`
- `docs/ARCHITECTURE.md`
- `docs/WEB_EVIDENCE.md`
- `docs/CALIBRATION.md`
- `docs/EXPORT.md`

## Current scope

The latest completed milestone is **v0.3.4 — Export**.

The next planned milestone is **v0.3.5 — end-to-end MVP validation**, but it must not be started without explicit authorization.

The product vision is broad; the implementation scope is intentionally narrow.

Current active service module:

- `web_development`

Current market used for validation:

- local businesses.

v0.3.4 includes:

- everything implemented through v0.3.3;
- deterministic CSV and JSON export of persisted Discovery Runs;
- a versioned JSON contract (`discovery-export-v1`);
- flattened CSV for manual use;
- OpportunityAssessment findings and relevant Site Audit evidence in exports;
- AI Discoverability preserved as a separate diagnostic;
- CSV formula-injection protection for public text values;
- tests for export content, determinism, endpoint behavior and CSV safety;
- export documentation.

Do **not** implement FreelancerProfile, compatibility scoring, pricing, LLM/chat, outreach generation, proposals, demos, extra service modules, bulk crawling or production deployment unless explicitly requested in a later milestone.

Do **not** invent performance data, Core Web Vitals, real responsive behavior, conversion rate, budget or internal business pain from static HTML.

## Architectural boundaries

### Shared core

The following concepts are shared infrastructure and must not be tied to one freelancer category:

- Prospect;
- Evidence;
- Discovery Provider;
- Site Analyzer / future analyzers;
- OpportunityAssessment;
- Discovery export contracts.

### Service-specific modules

Service-specific rules belong under `services/opportunity/<service_category>/`.

Do not create empty directories for future categories. Add a new module only when it is actually being implemented.

A service module should consume structured evidence/signals and return a common `OpportunityAssessmentResult`.

### Scores

Do not put new service-category scores directly on `Prospect`.

`Prospect.score*` fields are legacy fields from the old automation-specific design. New opportunity scores belong in `OpportunityAssessment`.

Automation should eventually become its own OpportunityModule if that category is reintroduced.

## Evidence integrity

The product must distinguish:

- `confirmed`;
- `strong_signal`;
- `inference`;
- `unknown`.

Never turn absence of evidence into evidence of absence.

Never label a signal as confirmed unless the current collector actually observes it.

Static-page findings must be scoped correctly. For example:

- acceptable: "no form was found on the analyzed page";
- unacceptable: "the company has no form anywhere".

Examples of claims that must remain unknown until a suitable collector exists:

- real mobile responsiveness across breakpoints;
- Core Web Vitals;
- runtime performance score;
- real conversion rate;
- internal operational pain;
- company budget.

Every externally derived fact should preserve source/provenance, observation time and confidence when applicable.

## Calibration rules

Calibration exists to improve evidence quality, not to manufacture impressive accuracy numbers.

- Human labels must describe only what was actually reviewed.
- `null` means the reviewer did not establish a label and must not be counted as correct/incorrect.
- Real websites are mutable; calibration results must include dataset/version/date context.
- A small calibration set is a smoke benchmark, not proof of general real-world accuracy.
- Prefer fixing collection/detection errors before changing scoring weights.
- Do not change `web-development-v2` weights without a documented calibration rationale.
- Add a regression test for every detector bug fixed from a calibration case.
- Keep the live calibration workflow manual; external-site availability must not make normal CI flaky.
- Do not copy third-party website HTML into the repository just to create a dataset.

The first v0.3.3 sample reached 25/25 labeled matches after correcting Brazilian city/UF location detection. This result is specific to that five-site, mostly-positive sample and must never be described as 100% real-world accuracy.

## Export rules

Exports are snapshots of already persisted Discovery Runs.

- Export must not re-run Discovery Providers.
- Export must not fetch websites.
- Export must not recalculate Site Audits or OpportunityAssessments.
- JSON export contracts must be versioned when their public structure changes.
- Candidate ordering must remain deterministic by discovery `rank`.
- Preserve certainty and evidence instead of exporting only a final score.
- Do not promote legacy Automation Opportunity fields into the new export contract.
- Keep AI Discoverability separate from service opportunity.
- CSV values derived from external/public text must be protected from spreadsheet formula injection.
- JSON should preserve original public text because it is not executed as a spreadsheet formula.

## Web development module

`web_development` is the first MVP module, not the product identity.

Its score must remain deterministic, explainable and versioned.

Raw observations do not automatically become commercial problems.

Example: `form_present=false` is useful evidence, but it should not automatically create a scored problem when another clear contact/capture path exists.

Prefer combined, defensible signals such as `lead_capture_path_present` when the product meaning depends on multiple observations.

## AI Discoverability

AI Discoverability remains a separate diagnostic from service opportunity.

It answers whether a site has observable readiness signals for search/AI discovery. It does not answer whether the company is a good client for a freelancer.

Never combine AI Discoverability and OpportunityAssessment into one opaque score.

## Future freelancer compatibility

A future Compatibility Engine will answer whether an opportunity matches a specific freelancer's skills, experience, constraints and availability.

Keep this separate from the service opportunity score.

Do not introduce FreelancerProfile before the core opportunity detection flow is validated.

## Future pricing

Pricing must eventually use structured data, scope, freshness and source confidence.

An LLM may explain a price estimate; it must not invent the canonical market range.

Do not implement pricing in the current milestone.

## Future chat

When chat is introduced, it must be grounded in persisted system data.

The LLM must query/receive Prospect, Evidence, OpportunityAssessment and later FreelancerProfile/Compatibility/Pricing data. It must not invent companies, contacts, problems, evidence or prices.

## Discovery rules

Discovery providers must remain replaceable.

Public sources must be used conservatively and according to their policies:

- no bulk harvesting from shared public infrastructure;
- keep public Overpass queries small, sequential and user-triggered;
- preserve attribution where required;
- persist only data needed by the product;
- avoid unnecessary personal-level enrichment.

Missing provider fields remain unknown.

## Site fetching and SSRF

User-controlled server-side URLs are security-sensitive.

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
2. Keep milestones small and testable.
3. Prefer readable code over speculative abstractions.
4. Run lint/tests after meaningful changes.
5. Never hide failures or weaken tests just to pass CI.
6. Keep external providers behind interfaces.
7. The project must run without secrets in demo/test mode.
8. Do not deploy, merge, send outreach or perform destructive actions without explicit human authorization.

## Security and privacy

Never commit secrets or private customer data.

Do not bypass authentication, CAPTCHA, paywalls, rate limits or anti-bot systems.

Do not build deceptive identities, fabricated claims, automated mass spam or review manipulation.

Future outreach defaults to human review and must support `do_not_contact`.

## Definition of done

A milestone is done only when:

- behavior matches the requested scope;
- lint passes;
- tests pass;
- migrations work from a clean database;
- documentation matches actual behavior;
- no secrets are present;
- future features are not disguised as complete.
