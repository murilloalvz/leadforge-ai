# LeadForge AI

**AI-powered B2B opportunity intelligence platform for discovering businesses with automation potential, explaining why they are promising prospects, generating personalized outreach, and preparing tailored demos.**

> Status: early-stage portfolio project / MVP in development.

## Why this project exists

Small businesses often run lead capture, qualification, follow-up, scheduling, and reporting through fragmented manual workflows. LeadForge AI is designed to identify those automation opportunities using public business information, rank prospects transparently, and help prepare relevant, evidence-based outreach.

The project is intentionally built as a real product engineering exercise rather than a generic demo. It combines AI engineering, data engineering, automation, B2B intelligence, software architecture, and evaluation.

## Core workflow

```text
Business discovery
      ↓
Public-data enrichment
      ↓
Evidence collection
      ↓
Opportunity scoring
      ↓
AI opportunity analysis
      ↓
Recommended automation
      ↓
Personalized offer
      ↓
Tailored demo
      ↓
Human review
      ↓
CRM pipeline
```

## Product principles

- Facts, inferences, hypotheses, and recommendations must remain clearly separated.
- The scoring system should be deterministic and explainable.
- No outreach is sent without human review in the MVP.
- No private or sensitive personal data should be collected.
- No bypassing logins, CAPTCHAs, anti-bot protections, or platform restrictions.
- Demos must use fictitious customer data.
- The application must run in demo mode without external credentials.

## Initial target market

The first vertical is **Brazilian aesthetics clinics and local aesthetics businesses**.

The architecture should later support other verticals such as:

- real estate agencies;
- gyms;
- dental clinics;
- schools and courses;
- workshops;
- solar-energy companies;
- professional services;
- e-commerce businesses.

## MVP scope

### v0.1 — Foundation

- project structure;
- FastAPI backend;
- database and migrations;
- prospect models;
- fictional seed data;
- deterministic Opportunity Scoring v1;
- minimal API for prospect listing/detail;
- tests and linting.

### v0.2 — Evidence & enrichment

- provider interfaces;
- public-source enrichment;
- evidence storage;
- confidence scoring;
- deduplication improvements.

### v0.3 — AI Opportunity Analyst

- structured LLM analysis;
- observed facts vs. hypotheses;
- recommended automations;
- Pydantic-validated outputs;
- mock and real LLM providers.

### v0.4 — Personalized outreach

- evidence-grounded offer generation;
- WhatsApp and email variants;
- human-review queue;
- outreach history.

### v0.5 — Demo Generator

- reusable solution templates;
- prospect-specific demo views;
- fictional lead datasets;
- demo preview links.

### v0.6 — CRM workflow

- prospect stages;
- notes;
- follow-up dates;
- activity history;
- pipeline metrics.

### v1.0 — Real-world validation

- first production-like prospect workflow;
- real prospect research from permitted sources;
- measured outreach and response outcomes;
- documented case study.

### Future

- Automation Engine;
- AI Conversation Quality Monitor;
- recurring automation health reports;
- multi-tenant SaaS architecture.

## Planned stack

**Backend**

- Python 3.12+
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic
- SQLite for local MVP, PostgreSQL-ready architecture

**Frontend**

- Next.js + TypeScript, once the backend foundation is stable

**Quality**

- pytest
- Ruff
- type checking
- structured logging

## Opportunity scoring

LeadForge does not rely on a mysterious LLM-generated score. The main opportunity score is intended to be deterministic and auditable.

Example signals may include:

- WhatsApp as a visible lead channel;
- multiple services;
- absence of a visible booking flow;
- simple contact forms;
- active public presence;
- apparent demand signals;
- visible advanced automation;
- insufficient evidence;
- inactivity signals.

Each result should expose the individual score components, confidence, evidence, and explanation.

## AI-assisted development

This project is developed with extensive AI-assisted software engineering using Codex. Product direction, architecture, evaluation criteria, security constraints, testing strategy, and final validation are human-directed.

The goal is not to hide AI usage, but to demonstrate the ability to use modern engineering tools while maintaining technical understanding and ownership of the system.

## Safety and privacy

LeadForge is intended for legitimate B2B prospecting and automation consulting.

It should not be used for:

- collecting private personal information;
- bypassing access controls;
- automated mass spam;
- fake identities;
- deceptive claims;
- fabricated business metrics;
- manipulation of ratings or reviews.

A `do_not_contact` state will be part of the CRM model.

## Architecture

Architecture decisions and module boundaries are documented in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

Development rules for AI coding agents are documented in [`AGENTS.md`](AGENTS.md).

## Running locally

The application is not implemented yet. Local setup instructions will be added as part of v0.1.

## Roadmap philosophy

The project will be developed incrementally. Each version must remain testable and understandable before the next capability is added.

The first success criterion is not “build a huge AI platform”. It is:

> Build a small, reliable system that can identify and rank plausible automation opportunities, then validate whether those rankings help produce real conversations with businesses.
