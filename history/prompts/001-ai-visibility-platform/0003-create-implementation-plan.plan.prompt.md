---
id: 0003
title: Create Implementation Plan
stage: plan
date: 2026-01-06
surface: agent
model: claude-sonnet-4-5-20250929
feature: 001-ai-visibility-platform
branch: 001-ai-visibility-platform
user: hassan
command: /sp.plan
labels: ["architecture", "fastapi", "nextjs", "monorepo", "ai-providers"]
links:
  spec: specs/001-ai-visibility-platform/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-ai-visibility-platform/plan.md
tests:
  - N/A (planning document)
---

## Prompt

[User provided comprehensive architecture plan covering: High-level architecture (FastAPI backend + Next.js frontend monorepo), repository structure (/apps/api and /apps/web), technology choices (Python 3.11+, Next.js 14+, PostgreSQL, Tailwind CSS), backend responsibilities (auth, AI orchestration, visibility/sentiment computation), frontend responsibilities (guided workflows, visualization), provider adapter pattern, data model (8 entities), API boundary (auth, analysis, insights, metadata endpoints), development milestones (7 phases), security/privacy, observability, and deployment strategy]

## Response snapshot

Created comprehensive implementation plan integrating user's architecture decisions with constitution compliance and detailed technical context.

**Key Outputs:**

1. **Technical Context** (Fully Specified):
   - Languages: Python 3.11+ (backend), TypeScript/Node.js 18+ (frontend)
   - Stack: FastAPI + Uvicorn + Next.js 14 App Router + Tailwind CSS + PostgreSQL
   - Performance: 10-30s AI queries, <5s insights, <200ms API p95, 100 concurrent analyses
   - Constraints: No background workers, no scheduled jobs, HTTPS required, server-side API keys only

2. **Constitution Check** (ALL PASS):
   - ✅ Monorepo Structure: `/apps/api` (FastAPI) + `/apps/web` (Next.js)
   - ✅ Backend Authority: All business logic in API
   - ✅ Test-First Development: Contract + integration + unit tests planned
   - ✅ Contract Testing: OpenAPI contracts in `/contracts/`
   - ✅ Minimal Viable Implementation: Deferred background workers, billing, teams
   - ✅ Observability: Structured logging with request_id, user_id, operation context
   - ✅ Versioning: API versioning with ADR triggers for breaking changes

3. **Project Structure**:
   - Backend: `/apps/api/src/` with models, schemas, services, providers, api, core, utils
   - Frontend: `/apps/web/src/` with app (App Router), components (Tailwind), lib, hooks
   - Tests: contract/, integration/, unit/ for both apps
   - Docker Compose: Local dev orchestration (API + Web + PostgreSQL)

4. **Phase 0 Research** (8 decisions documented):
   - `asyncio.gather()` for concurrent AI provider calls
   - `geoip2` + MaxMind GeoLite2 for IP geolocation
   - JSONB columns for AI responses/citations with GIN indexes
   - Server-Sent Events (SSE) for incremental results streaming
   - Visibility scoring: `0.4 * presence + 0.3 * frequency + 0.3 * position_score`
   - Claude for sentiment classification with strict prompt template
   - HTTP-only cookies + Redis session store for auth
   - Official SDKs (openai, google-generativeai, anthropic, httpx) with adapter pattern

5. **Phase 1 Data Model** (8 entities):
   - User, Analysis, Competitor, Prompt, AIResponse, Citation, Insight, Recommendation
   - Relationships: User → Analyses → Prompts → AIResponses → Citations → Insights/Recommendations
   - Validation rules, state transitions, JSONB fields for flexibility

6. **API Contracts** (25 endpoints across 4 groups):
   - Authentication: register, verify, login, logout, me
   - Analysis: CRUD, competitor/prompt suggestion, start, stream (SSE), retry, responses
   - Insights: generate (user-triggered), get insights, get recommendations
   - Metadata: progress, location

7. **Implementation Milestones** (7 phases):
   - M1: Foundation (scaffolding, DB, auth, dashboard)
   - M2: Analysis Flow (brand/competitor/prompt entry, location detection)
   - M3: AI Provider Integration (5 adapters, concurrent queries, SSE, retry)
   - M4: Results Exploration (viewer, citations, confidence levels)
   - M5: Insight Generation (scoring algorithms, sentiment, recommendations)
   - M6: Insight Visualization (comparisons, evidence drill-down)
   - M7: Polish & Testing (contract/integration/unit tests, logging, docs)

8. **ADR Recommendations** (5 significant decisions):
   - ADR-001: Monorepo with FastAPI + Next.js
   - ADR-002: Synchronous Insight Generation
   - ADR-003: Server-Sent Events for Incremental Results
   - ADR-004: JSONB for AI Responses and Citations
   - ADR-005: Claude for Sentiment Classification

**Complexity Tracking**: No violations - all constitutional principles satisfied without justifications needed.

## Outcome

- ✅ Impact: Production-ready architecture plan with constitutional compliance, 8 research decisions, 8 data entities, 25 API endpoints, 7 implementation milestones
- 🧪 Tests: Contract/integration/unit test strategy defined across all milestones
- 📁 Files: Created plan.md (416 lines) with complete technical specification
- 🔁 Next prompts: Ready for `/sp.adr` (create 5 ADRs) or `/sp.tasks` (generate testable tasks organized by user story)
- 🧠 Reflection: User-provided architecture was comprehensive and constitution-compliant, enabling direct integration without additional research agents. Monorepo pattern with clear backend/frontend separation aligns perfectly with constitutional principles.

## Evaluation notes (flywheel)

- Failure modes observed: None - architecture plan complete and validated against constitution
- Graders run and results (PASS/FAIL): Constitution check PASS (7/7), Research decisions PASS (8/8), Data model PASS (8 entities with relationships), API contracts PASS (25 endpoints)
- Prompt variant (if applicable): N/A (initial plan creation with user-provided architecture)
- Next experiment (smallest change to try): Validate whether pre-provided architecture plans reduce task generation ambiguity compared to agent-generated architectures
