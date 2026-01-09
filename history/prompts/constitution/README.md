# Product Name

**Promptly** — AI Search Visibility & Competitive Insight Platform

## Product Intent

Promptly helps brands understand how they appear inside AI-generated answers, compare themselves against competitors, and receive evidence-backed, actionable recommendations to improve their mentions, visibility, and sentiment in AI systems.

The product analyzes AI answers and their citations, not the open web, and focuses on how AI models represent brands for a given user location and context.

## Target Users

Brand, marketing, and SEO teams

Startup founders and product marketers

## Problem Statement

Brands do not know:

Whether they are mentioned in AI answers

How visible or prominent they are compared to competitors

Whether AI sentiment about them is positive, neutral, or negative

What concrete actions would improve their presence in AI-generated results

Existing tools focus on web SEO or social listening, not location-aware AI answer ecosystems.

## Core User Journey (MVP)
### Entry & Access

User lands on a public landing page with a Sign Up option.

User registers for a free trial.

User completes verification and is redirected to Login.

User logs in successfully and lands on a Dashboard.

### Analysis Flow

Dashboard presents a Start Analysis action.

User initiates analysis.

User enters a Brand Name and proceeds.

System suggests up to 3 competitor brands using an LLM.

User may add up to 2 additional competitors.

System suggests up to 5 natural-language prompts that users might ask about the brand.

User may add up to 2 additional prompts.

User confirms prompts and starts analysis.

### Location-Aware Data Collection

The system determines the user’s effective location (e.g., country or region) for analysis purposes.

All AI queries must be location-aware, ensuring responses reflect how AI systems answer questions for users in that location.

### AI Querying & Evidence Collection

Backend queries multiple AI systems with the selected prompts.

For each AI system:

The system must enable or invoke web-search / citation-generating tools where supported.

The system collects:

Answer text

Citations or references (URLs, titles, snippets when available)

Provider and model metadata

If a provider cannot return citations reliably, the system must:

Still capture the answer

Explicitly mark citation coverage as incomplete

Backend returns a normalized response collection to the frontend.

### Exploration & Insights

UI displays AI answers and citations in a clear, comparable format.

User selects Get Insights.

Backend analyzes brand vs competitors across all AI responses to derive:

Mentions and mention frequency

Visibility / prominence

Sentiment (positive / neutral / negative)

Key themes and gaps

User is presented with:

Summary insights

Evidence-linked findings

Actionable recommendations to improve AI presence

## Supported AI Systems (MVP)

OpenAI

Google Gemini

Anthropic Claude

Perplexity

Google AI Search / AI Overview (where supported)

Each AI system should be queried in a way that maximizes citation availability, including the use of search or grounding tools when supported.

## Core Capabilities (MVP)

Multi-provider AI querying

Location-aware AI responses

Tool-assisted citation generation

Prompt-driven competitive analysis

Citation-aware result normalization

Brand vs competitor comparison

Evidence-grounded insight generation

Actionable recommendation generation

## Non-Goals (MVP)

No traditional web crawling or SEO rank tracking

No social media listening

No paid subscriptions or billing

No long-term historical trend analysis

## Quality & Reliability Requirements

Partial provider failures must not block the analysis.

Provider errors and missing citation coverage must be visible to the user.

Insights must always reference underlying AI responses and/or citations.

Results should appear incrementally where possible.

## Data & Privacy Constraints

API keys must never be exposed to the client.

Analysis data is accessible only to the owning user.

Sensitive user or provider data must not appear in logs.

## Success Criteria (MVP)

A user can complete the full flow from sign-up to insights.

The system returns responses from at least one AI provider.

At least one provider returns responses with citations.

The insights screen includes:

Brand vs competitor comparison

Mentions, visibility, and sentiment indicators

A minimum of five actionable recommendations

Location context materially influences the AI responses used for analysis.

## Open Questions for Clarification

(To be resolved in /sp.clarify)

How is user location determined and overridden (IP, user-selected, account setting)?

How is “visibility” defined and scored across providers?

How is sentiment evaluated and validated?

Are insights generated synchronously or via background jobs?

How long are analysis reports retained?

What authentication/session mechanism is used?

## Clarifications and Answers:
Clarification Decisions — Promptly

AI Search Visibility & Competitive Insight Platform

This document captures all clarification decisions required to unblock architecture planning and task breakdown.
All decisions are MVP-safe, explicit, and explainable.

1. Visibility / Prominence Definition

Decision
Visibility is a composite score representing how prominently a brand appears in AI responses relative to competitors.

Rules

Visibility is calculated per prompt and per provider, then aggregated.

The score combines:

Presence (whether the brand is mentioned)

Frequency (how often it is mentioned relative to competitors)

Position / Emphasis (where the mention appears in the response)

Early mentions are weighted more heavily than later mentions.

Scores are normalized to allow comparison across prompts and providers.

Rationale
This approach is deterministic, explainable, works across providers, and reflects how users perceive AI-generated answers.

2. Sentiment Evaluation Method

Decision
Sentiment is evaluated using LLM-based classification with a strict rubric.

Rules

Sentiment values: Positive, Neutral, Negative

Sentiment is assigned per brand mention.

Ambiguous or mixed sentiment defaults to Neutral.

Sentiment is aggregated:

Per prompt (majority of mentions)

Per provider (majority of prompts)

Across providers (majority of providers)

Every sentiment result must reference the underlying AI response (and citation if available).

Rationale
This provides nuanced understanding while remaining conservative and explainable.

3. Insight Generation Timing

Decision
Insight generation follows a two-phase synchronous model.

Rules

AI provider querying and citation collection occur synchronously with incremental results shown.

Insight generation is triggered explicitly by the user via a “Get Insights” action.

Insight generation runs synchronously for MVP.

Users may retry insight generation without re-running provider queries.

Rationale
Avoids background job complexity while matching user expectations and UI flow.

4. Location Determination Rules

Decision
User location is determined per analysis using server-side IP geolocation.

Rules

Location is determined once at analysis start.

Granularity is country-level.

Location remains fixed for the entire analysis.

If location cannot be determined, a global context is used.

Effective location is displayed to the user for transparency.

Rationale
Ensures reproducibility, consistency across providers, and user trust.

5. Citation Coverage Expectations

Decision
An analysis is valid if at least one provider returns citations.

Rules

Providers without citations are included but do not increase confidence.

Insights are labeled with confidence levels:

High: multiple citations

Medium: at least one citation

Low: no citation support

Missing or broken citations are displayed and marked.

Rationale
Preserves value despite uneven provider capabilities while maintaining transparency.

6. Provider Capability Differences

Decision
All providers contribute equally to analysis; citation-capable providers increase confidence only.

Rules

All providers contribute to visibility, sentiment, and themes.

Citation capability affects confidence, not inclusion.

Provider differences are surfaced via metadata and UI indicators.

No implicit provider ranking or favoritism.

Rationale
Ensures fairness, avoids bias, and keeps comparisons meaningful.

7. Partial Failure Handling

Decision
An analysis is successful if at least one provider returns a usable response.

Rules

Provider failures are visible and non-blocking.

Users may retry failed providers only.

Insight generation proceeds with available data.

Confidence reflects partial coverage.

Rationale
Maximizes resilience and user value without hiding failures.

8. Ambiguous Brand Names

Decision
Infer brand context first; request user clarification only if ambiguity remains high.

Rules

Context is inferred using competitors and prompts.

If providers return conflicting interpretations, the user is prompted to disambiguate.

Applied context is shown to the user and used consistently.

Rationale
Balances accuracy with minimal user friction.

9. Prompt Quality & Guardrails

Decision
Validate and sanitize prompts; do not auto-rewrite them.

Rules

Block empty, nonsensical, unsafe, or malicious prompts.

Allow low-quality prompts with guidance.

Prompts are sent unchanged to all providers.

Brand context and location are applied outside the user prompt.

Rationale
Protects system integrity while preserving user intent.

10. Insight Explainability

Decision
Every insight must be explainable and traceable to evidence.

Rules

Each insight includes:

Summary

Explanation

Evidence (AI responses and/or citations)

Insights without citations are allowed but marked lower confidence.

No insight may be shown without an explanation.

Rationale
Builds trust and prevents “black box” conclusions.

11. Data Retention & Report Lifecycle

Decision
Reports are retained indefinitely with user-controlled deletion.

Rules

Reports are stored until deleted by the user.

Deletion is soft delete for MVP.

Deleted reports are hidden from UI and analysis.

No automatic expiration or archival.

Rationale
Simple, predictable, and user-friendly for MVP.

Status

All clarification questions resolved

Ready for /sp.plan

Decisions are safe to store in README.md or docs/clarify.md

## Plan:
Architecture & Implementation Plan — Promptly

AI Search Visibility & Competitive Insight Platform

This plan translates the approved Specification and Clarification decisions into a concrete architecture, technology stack, and execution strategy suitable for iterative development.

1. High-Level Architecture Overview

Promptly is implemented as a single-product monorepo with two primary applications:

Backend API: A FastAPI-based service that owns all business logic, AI provider orchestration, analysis, and insight generation.

Frontend Web App: A Next.js-based application that provides the user interface, workflows, and visualizations.

The backend API is the source of truth for:

Data models and validation

Analysis lifecycle

AI provider access and orchestration

Visibility, sentiment, and insight computation

Security and data isolation

The frontend consumes backend APIs and never communicates directly with AI providers.

2. Repository Structure
promptly/
├── apps/
│   ├── api/        # FastAPI backend
│   └── web/        # Next.js frontend
├── docker-compose.yml
├── README.md
└── docs/
    ├── specify.md
    ├── clarify.md


Rules

No application logic exists at the repo root.

All backend logic lives in apps/api.

All UI logic lives in apps/web.

3. Technology Choices (MVP)
3.1 Frontend — apps/web

The frontend MUST be scaffolded using create-next-app with:

Next.js (latest stable)

App Router

TypeScript

Tailwind CSS

Tailwind CSS is the primary styling mechanism for all UI components.

The frontend focuses on:

Guided workflows

Incremental result rendering

Insight visualization and explainability

3.2 Backend — apps/api

The backend MUST be implemented using FastAPI.

The API MUST run on an ASGI server using Uvicorn for local development and production parity.

The backend should:

Use async endpoints where appropriate

Support concurrent AI provider calls

Enable incremental progress reporting

4. Backend Responsibilities — apps/api
4.1 Core Responsibilities

The backend is responsible for:

Authentication and session enforcement

User ownership and access control

Analysis lifecycle management

Location-aware AI querying

Citation collection and normalization

Visibility and sentiment computation

Insight and recommendation generation

4.2 API Boundary (Conceptual)

The backend exposes versioned HTTP APIs grouped conceptually as:

Authentication

Register

Verify email

Login

Session management

Analysis

Create analysis

Submit brand, competitors, and prompts

Start AI querying

Retrieve provider results incrementally

Retry failed providers

Insights

Generate insights (user-triggered)

Retrieve insights and recommendations

Metadata

Analysis progress

Provider status

Location context

Exact endpoints and schemas will be defined during implementation.

4.3 Provider Orchestration
Provider Adapter Pattern

Each AI provider implements a shared adapter interface.

Adapters are responsible for:

Prompt submission

Location context injection

Enabling web-search / citation tools where supported

Normalizing provider-specific responses

All provider outputs are normalized into a single internal schema before further processing.

4.4 Location Handling

Location is determined once per analysis using server-side IP geolocation.

Location is stored as part of the analysis record.

All provider queries for an analysis share the same location context.

4.5 Analysis & Insight Pipeline

Phase 1: Data Collection

Persist analysis inputs (brand, competitors, prompts, location)

Query AI providers concurrently

Store normalized AI responses and citations

Update analysis progress incrementally

Phase 2: Insight Generation

Triggered explicitly by the user

Compute:

Brand and competitor mentions

Visibility scores

Sentiment classifications

Themes and gaps

Generate actionable recommendations

Link all insights to evidence

Persist insight results

5. Frontend Responsibilities — apps/web
5.1 Core Responsibilities

The frontend is responsible for:

Authentication flows

Guided analysis wizard

Display of incremental AI responses

Citation exploration

Insight visualization and explainability

5.2 Key Screens (MVP)

Landing Page

Sign Up / Login

Dashboard

Analysis Wizard

Brand entry

Competitor selection

Prompt selection

Results Viewer

Provider responses

Citations

Provider status

Insights View

Summary insights

Evidence drill-down

Actionable recommendations

5.3 Data Flow Rules

The frontend never accesses AI providers directly.

All sensitive operations go through the backend API.

API keys and credentials remain server-side.

6. Data Model (Conceptual)

Primary entities:

User

Analysis

Brand

Prompt

AIResponse

Citation

Insight

Recommendation

Relationships:

User → many Analyses

Analysis → many Prompts

Prompt → many AIResponses

AIResponse → many Citations

Analysis → many Insights & Recommendations

Exact schemas are defined during implementation.

7. Development & Execution Strategy
7.1 Iterative Milestones

Milestone 1

Project scaffolding

Authentication

Dashboard

Analysis creation flow

Milestone 2

Provider adapter interface

Single provider integration

Normalized response storage

Results UI

Milestone 3

Multi-provider querying

Citation handling

Partial failure handling

Incremental progress display

Milestone 4

Visibility scoring

Sentiment analysis

Insight generation

Recommendation engine

7.2 Local Development

Web and API run simultaneously using:

Docker Compose, or

A single-command dev workflow

Stable local URLs for frontend and backend.

8. Security & Privacy

AI provider keys are stored server-side only

User data isolation enforced at API layer

HTTPS required for all communication

Sensitive data excluded from logs

9. Observability (MVP)

Provider success/failure tracking

Analysis progress tracking

Error logging (non-sensitive)

Advanced tracing and metrics are deferred.

10. Constraints (MVP)

No background workers

No scheduled jobs

No billing or payments

No team or organization features

No third-party API access

11. Output of This Plan

This plan provides:

Clear frontend/backend boundaries

Enforced modern technology choices

A safe path to generate /sp.tasks

Minimal architectural churn during iteration

Status

Architecture approved

Tech stack locked

Ready for /sp.tasks

