# Implementation Plan: AI Search Visibility & Competitive Insight Platform

**Branch**: `001-ai-visibility-platform` | **Date**: 2026-01-06 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-ai-visibility-platform/spec.md`

## Summary

Promptly is an AI Search Visibility & Competitive Insight Platform that helps brands understand how they appear in AI-generated answers. The platform queries multiple AI providers (OpenAI, Google Gemini with grounding / AI Overview where supported, Anthropic Claude, Perplexity, Google AI Search/AI Overview where supported, and Hugging Face for classification/theme analysis) with location-aware context, collects citations, and generates evidence-backed insights comparing brand visibility against competitors.

**Technical Approach**: Monorepo with FastAPI backend (business logic authority) and Next.js frontend (UI only). Backend orchestrates concurrent AI provider queries, normalizes responses, computes visibility/sentiment scores using deterministic algorithms, and generates actionable recommendations. Frontend provides guided workflows with incremental result rendering and insight visualization.

## Technical Context

**Language/Version**: Python 3.12+ (backend), TypeScript/Node.js 18+ (frontend)
**Primary Dependencies**: FastAPI, Uvicorn, Next.js 14+ (App Router), Tailwind CSS
**Storage**: PostgreSQL (relational data: users, analyses, insights), Object storage or JSON fields (AI responses, citations)
**Testing**: pytest (backend), Jest/React Testing Library (frontend), contract tests for API boundaries
**Target Platform**: Linux server (backend), Modern web browsers (frontend)
**Project Type**: Web application (monorepo with `/apps/api` and `/apps/web`)
**Performance Goals**:
  - AI provider queries: 10-30 seconds with incremental results
  - Insight generation: <5 seconds synchronously
  - API response time: <200ms p95 for non-AI endpoints
  - Support 100 concurrent analyses
**Constraints**:
  - No background workers (synchronous processing only for MVP)
  - No scheduled jobs or automation
  - HTTPS required for all communication
  - API keys server-side only
**Scale/Scope**:
  - MVP: 100-1000 users
  - The platform queries multiple AI providers per analysis:
      - OpenAI
      - Google Gemini (with grounding / AI Overview where supported)
      - Anthropic Claude
      - Perplexity
      - Hugging Face (classification and theme analysis; no native citations)
  - Up to 7 prompts per analysis (5 suggested + 2 custom)
  - Up to 5 competitors per brand (3 suggested + 2 custom)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Monorepo Structure (NON-NEGOTIABLE)
✅ **PASS**: Architecture enforces `/apps/api` (FastAPI backend) and `/apps/web` (Next.js frontend) with no root-level application code.

### Principle II: Backend Authority
✅ **PASS**: All business logic (AI orchestration, visibility scoring, sentiment analysis, insight generation) resides in `/apps/api`. Frontend only handles UI workflows and visualization.

### Principle III: Test-First Development (NON-NEGOTIABLE)
✅ **PASS**: Plan includes contract tests, integration tests, and unit tests. Red-Green-Refactor cycle will be enforced during `/sp.tasks` and `/sp.implement`.

### Principle IV: Contract Testing for API Integration
✅ **PASS**: Phase 1 generates OpenAPI contracts in `/contracts/`. Frontend and backend contract tests will validate request/response schemas.

### Principle V: Minimal Viable Implementation
✅ **PASS**: Plan explicitly defers background workers, scheduled jobs, billing, team features, and third-party API access. Architecture focuses on MVP scope only.

### Principle VI: Observability and Debuggability
✅ **PASS**: Plan includes structured logging for provider success/failure tracking, analysis progress tracking, and error logging (non-sensitive). Request IDs and context will be included.

### Principle VII: Versioning and Breaking Changes
✅ **PASS**: API contracts will be versioned. Breaking changes will trigger ADR creation and migration planning (deferred to post-MVP).

**Gate Result**: ✅ ALL CHECKS PASS - Proceed to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/001-ai-visibility-platform/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   ├── openapi.yaml     # OpenAPI 3.0 specification
│   └── schemas/         # Request/response schemas
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
apps/
├── api/                 # FastAPI backend (Python 3.12+)
│   ├── src/
│   │   ├── models/      # SQLAlchemy models (User, Analysis, AIResponse, Citation, Insight)
│   │   ├── schemas/     # Pydantic schemas for request/response validation
│   │   ├── services/    # Business logic (analysis, insight generation, scoring)
│   │   ├── providers/   # AI provider adapters (OpenAI, Gemini, Claude, Perplexity, Google AI, HuggingFace)
│   │   ├── api/         # FastAPI routers (auth, analysis, insights)
│   │   ├── core/        # Configuration, dependencies, security
│   │   └── utils/       # Location detection, logging, error handling
│   ├── tests/
│   │   ├── contract/    # API contract tests (OpenAPI validation)
│   │   ├── integration/ # End-to-end analysis flow tests
│   │   └── unit/        # Service and adapter unit tests
│   ├── pyproject.toml   # Poetry dependencies
│   └── README.md
│
└── web/                 # Next.js frontend (TypeScript)
    ├── src/
    │   ├── app/         # App Router pages (landing, auth, dashboard, analysis, insights)
    │   ├── components/  # Reusable UI components (Tailwind CSS)
    │   ├── lib/         # API client, types, utilities
    │   └── hooks/       # React hooks for state management
    ├── tests/
    │   ├── contract/    # API contract tests (frontend perspective)
    │   └── integration/ # Component integration tests
    ├── package.json
    └── README.md

docker-compose.yml       # Local development orchestration (API + Web + PostgreSQL)
README.md                # Monorepo overview and quickstart
```

**Structure Decision**: Web application pattern with monorepo organization. Backend (`/apps/api`) owns all business logic and data access. Frontend (`/apps/web`) consumes backend APIs and handles UI only. Docker Compose orchestrates local development with stable URLs (e.g., API at http://localhost:8000, Web at http://localhost:3000).

## Complexity Tracking

**No violations identified.** All constitutional principles are satisfied without requiring complexity justifications.

## Phase 0: Research & Technology Validation

### Research Tasks

1. **FastAPI Best Practices for Async AI Provider Calls**
   - Decision: Use `asyncio.gather()` for concurrent provider queries with timeout handling
   - Rationale: Enables parallel provider calls while maintaining request-scoped context
   - Alternatives considered: Celery (rejected - adds background worker complexity violating MVP constraints)

2. **Location Detection via IP Geolocation**
   - Decision: Use `geoip2` library with MaxMind GeoLite2 database (free tier)
   - Rationale: Server-side, country-level accuracy sufficient for MVP, no external API dependencies
   - Alternatives considered: ipapi.co (rejected - external API dependency, rate limits)

3. **PostgreSQL Schema Design for AI Responses and Citations**
   - Decision: Use JSONB columns for AI response text and citation arrays
   - Rationale: Flexible schema for provider-specific metadata, efficient indexing with GIN indexes
   - Alternatives considered: Separate tables per provider (rejected - over-normalized for MVP)

4. **Next.js App Router Patterns for Incremental Results**
   - Decision: Use Server-Sent Events (SSE) for streaming provider results
   - Rationale: Native browser support, unidirectional data flow, simpler than WebSockets for MVP
   - Alternatives considered: Polling (rejected - inefficient), WebSockets (rejected - over-engineered)

5. **Visibility Scoring Algorithm Implementation**
   - Decision: Weighted composite score: `visibility = 0.4 * presence + 0.3 * frequency + 0.3 * position_score`
   - Rationale: Deterministic, explainable, normalizable across providers
   - Position scoring: First mention = 1.0, decay by 0.1 per subsequent mention (min 0.5)

6. **Sentiment Analysis via LLM**
   - Decision: Use Anthropic Claude as the primary sentiment classifier, with Hugging Face as a fallback for sentiment or theme classification if Claude is unavailable or rate-limited with strict prompt template.
   - Rationale: Best-in-class reasoning, structured output support, already integrated as provider
   - Prompt template: "Classify sentiment (Positive/Neutral/Negative) for brand mention: {mention_context}"

7. **Session-Based Authentication**
   - Decision: Use HTTP-only cookies with FastAPI's session middleware + Redis session store
   - Rationale: Secure, stateless backend, prevents XSS attacks on tokens
   - Alternatives considered: JWT (rejected - stateless not required for MVP, harder to revoke)

8. **AI Provider SDK Integration**
   - Decision: Use official SDKs (openai, google-generativeai, anthropic, httpx for Perplexity/Google AI)
   - Rationale: Native support for streaming, citations, and model-specific features
   - Adapter pattern abstracts provider differences

9. **AI Provider Configuration Management**
   - Decision: Use environment variables to enable/disable providers at deployment/startup
   - Rationale: Allows cost control, rate limit management, and provider selection without code changes
   - Configuration format: `ENABLED_PROVIDERS=openai,claude,gemini,perplexity,google_ai,huggingface` (comma-separated list)
   - Default behavior: All providers enabled if environment variable not set
   - Validation: At least one provider must be enabled; system fails fast at startup if invalid configuration
   - Query behavior: Only enabled providers are queried during analysis; disabled providers are skipped entirely
   - Alternatives considered: Database configuration (rejected - over-engineered for MVP), Hard-coded (rejected - no flexibility), Per-user configuration (deferred to post-MVP)

**Research Output**: [research.md](./research.md) (to be generated)

## Phase 1: Data Model & API Contracts

### Data Model

**Primary Entities** (detailed in [data-model.md](./data-model.md)):

1. **User**
   - Fields: id (UUID), email (unique), password_hash, verified (boolean), created_at, updated_at
   - Relationships: One-to-many with Analysis
   - Validation: Email format, password strength (min 8 chars, complexity rules)

2. **Analysis**
   - Fields: id (UUID), user_id (FK), brand_name, brand_context (optional, for disambiguation), location (country code), status (enum: pending, in_progress, completed, failed), created_at, updated_at
   - Relationships: One-to-many with Competitor, Prompt, AIResponse, Insight, Recommendation
   - State transitions: pending → in_progress → completed/failed
   - Validation: brand_name non-empty, max 3 AI-suggested competitors + 2 custom

3. **Competitor**
   - Fields: id (UUID), analysis_id (FK), name, is_suggested (boolean), created_at
   - Relationships: Many-to-one with Analysis
   - Validation: name non-empty, max 5 per analysis

4. **Prompt**
   - Fields: id (UUID), analysis_id (FK), text, is_suggested (boolean), validation_status (enum: valid, malicious, low_quality), created_at
   - Relationships: Many-to-one with Analysis, One-to-many with AIResponse
   - Validation: text non-empty, max 500 chars, safety checks for malicious content

5. **AIResponse**
   - Fields: id (UUID), prompt_id (FK), provider (enum: openai, gemini, claude, perplexity, google_ai, huggingface), model_name, answer_text (JSONB), metadata (JSONB: capability_flags, failure_reason), citation_coverage (enum: none, partial, complete), status (enum: success, failed, timeout), created_at
   - Relationships: Many-to-one with Prompt, One-to-many with Citation
   - Indexes: GIN index on answer_text for full-text search

6. **Citation**
   - Fields: id (UUID), ai_response_id (FK), url, title, snippet (optional), source_type, validity_status (enum: valid, broken, unknown), position (integer), created_at
   - Relationships: Many-to-one with AIResponse
   - Validation: URL format, position >= 0

7. **Insight**
   - Fields: id (UUID), analysis_id (FK), insight_type (enum: mention, visibility, sentiment, theme, gap), brand_name, competitor_name (optional), summary, explanation, evidence_references (JSONB: [{"ai_response_id": UUID, "citation_id": UUID}]), confidence_level (enum: high, medium, low), scores (JSONB: {"visibility": float, "sentiment": string, "mention_count": int}), created_at
   - Relationships: Many-to-one with Analysis
   - Validation: summary non-empty, confidence_level required

8. **Recommendation**
   - Fields: id (UUID), analysis_id (FK), text, rationale, expected_impact, confidence_level (enum: high, medium, low), evidence_references (JSONB), priority (integer: 1-5), created_at
   - Relationships: Many-to-one with Analysis
   - Validation: text non-empty, min 5 recommendations per analysis

### API Contracts

**Base URL**: `/api/v1`

**Authentication Endpoints**:
- `POST /auth/register` - User registration (email, password) → 201 Created
- `POST /auth/verify` - Email verification (token) → 200 OK
- `POST /auth/login` - User login (email, password) → 200 OK + session cookie
- `POST /auth/logout` - User logout → 204 No Content
- `GET /auth/me` - Get current user → 200 OK + User schema

**Analysis Endpoints**:
- `POST /analyses` - Create analysis (brand_name) → 201 Created + Analysis schema
- `GET /analyses/{id}` - Get analysis details → 200 OK + Analysis schema (includes brand, competitors, prompts, location)
- `POST /analyses/{id}/competitors/suggest` - Get AI-suggested competitors (brand_name) → 200 OK + [Competitor] schemas (max 3)
- `POST /analyses/{id}/competitors` - Add custom competitor (name) → 201 Created + Competitor schema
- `POST /analyses/{id}/prompts/suggest` - Get AI-suggested prompts (brand_name, competitors) → 200 OK + [Prompt] schemas (max 5)
- `POST /analyses/{id}/prompts` - Add custom prompt (text) → 201 Created + Prompt schema
- `POST /analyses/{id}/start` - Start AI provider queries → 202 Accepted + Analysis schema (status: in_progress)
- `GET /analyses/{id}/stream` - Server-Sent Events stream for incremental results → 200 OK + text/event-stream
- `POST /analyses/{id}/providers/{provider}/retry` - Retry failed provider → 202 Accepted + AIResponse schema
- `GET /analyses/{id}/responses` - Get all AI responses → 200 OK + [AIResponse] schemas (includes citations)

**Insights Endpoints**:
- `POST /analyses/{id}/insights/generate` - Generate insights (user-triggered) → 202 Accepted + Analysis schema (insight_status: in_progress)
- `GET /analyses/{id}/insights` - Get all insights → 200 OK + [Insight] schemas
- `GET /analyses/{id}/recommendations` - Get all recommendations → 200 OK + [Recommendation] schemas

**Metadata Endpoints**:
- `GET /analyses/{id}/progress` - Get analysis progress → 200 OK + Progress schema (providers_completed, providers_total, status)
- `GET /analyses/{id}/location` - Get effective location → 200 OK + Location schema (country_code, display_name)

**Contract Output**: OpenAPI 3.0 specification in `/contracts/openapi.yaml` with request/response schemas in `/contracts/schemas/`

### Quickstart Guide

**Local Development Setup** (detailed in [quickstart.md](./quickstart.md)):

1. **Prerequisites**: Docker, Docker Compose, Python 3.12+, Node.js 18+
2. **Clone and setup**:
   ```bash
   git clone <repo-url>
   cd promptly
   docker-compose up -d  # Starts PostgreSQL, API, Web
   ```
3. **Backend setup**:
   ```bash
   cd apps/api
   poetry install
   poetry run alembic upgrade head  # Database migrations
   poetry run pytest  # Run tests
   ```
4. **Configure environment variables** (create `.env` file in `apps/api/`):
   ```bash
   # AI Provider API Keys (required)
   OPENAI_API_KEY=your_key_here
   ANTHROPIC_API_KEY=your_key_here
   GOOGLE_API_KEY=your_key_here
   PERPLEXITY_API_KEY=your_key_here
   HUGGINGFACE_API_KEY=your_key_here

   # Provider Configuration (optional - defaults to all enabled)
   ENABLED_PROVIDERS=openai,claude,gemini,perplexity,google_ai,huggingface

   # Or enable only specific providers for testing:
   # ENABLED_PROVIDERS=openai,claude
   ```
5. **Frontend setup**:
   ```bash
   cd apps/web
   npm install
   npm run dev  # Starts Next.js dev server
   ```
6. **Access**:
   - Web UI: http://localhost:3000
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs (Swagger UI)

## Phase 2: Implementation Milestones (Reference for /sp.tasks)

### Milestone 1: Foundation
- Project scaffolding (FastAPI + Next.js + Docker Compose + PostgreSQL)
- Database schema and migrations (Alembic)
- Authentication (registration, email verification, login, session management)
- Dashboard (empty state with "Start Analysis" action)

### Milestone 2: Analysis Flow
- Brand and competitor entry
- AI-suggested competitors (using Claude)
- Custom competitor addition
- Prompt suggestion (using Claude)
- Custom prompt addition with validation
- Location detection (IP geolocation)

### Milestone 3: AI Provider Integration
- Provider adapter interface
- Provider configuration management (environment variable parsing, validation, fail-fast on invalid config)
- OpenAI adapter (with web search/citations)
- Gemini adapter (with grounding/citations)
- Claude adapter (with search/citations)
- Perplexity adapter (native citations)
- Google AI Search adapter (AI Overview)
- Hugging Face adapter (classification/theme analysis; no native citations)
- Concurrent provider queries with timeout
- Response normalization
- Incremental progress (SSE streaming)
- Partial failure handling
- Provider retry capability

### Milestone 4: Results Exploration
- AI response viewer (organized by provider and prompt)
- Citation display (URL, title, snippet, validity status)
- Provider capability indicators
- Confidence level badges (High/Medium/Low)
- Compare responses across providers

### Milestone 5: Insight Generation
- Visibility scoring algorithm (presence + frequency + position)
- Sentiment classification (Claude-based with strict rubric)
- Mention frequency calculation
- Theme and gap identification
- Recommendation engine (min 5 actionable recommendations)
- Evidence linking (AI responses → citations)
- Confidence level computation
- Insight retry without re-querying providers

### Milestone 6: Insight Visualization
- Summary insights view
- Brand vs competitor comparison
- Visibility/sentiment indicators
- Evidence drill-down
- Recommendations list with rationale and expected impact

### Milestone 7: Polish & Testing
- Contract tests (API schema validation)
- Integration tests (end-to-end analysis flow)
- Unit tests (services, adapters, scoring algorithms)
- Error handling and validation
- Structured logging
- API documentation (OpenAPI/Swagger)

## Architecture Decision Records (ADRs)

Significant architectural decisions requiring ADR documentation:

1. **ADR-001: Monorepo with FastAPI + Next.js**
   - Decision: Use monorepo structure with `/apps/api` (FastAPI) and `/apps/web` (Next.js)
   - Rationale: Clear separation of concerns, independent scaling, constitution compliance
   - Alternatives: Separate repos (rejected - coordination overhead)

2. **ADR-002: Synchronous Insight Generation**
   - Decision: Generate insights synchronously (no background workers)
   - Rationale: Simplifies MVP, user explicitly triggers insights, <5s processing time acceptable
   - Alternatives: Background jobs with Celery (rejected - violates MVP constraints)

3. **ADR-003: Server-Sent Events for Incremental Results**
   - Decision: Use SSE for streaming provider results to frontend
   - Rationale: Native browser support, unidirectional flow sufficient, simpler than WebSockets
   - Alternatives: Polling (inefficient), WebSockets (over-engineered)

4. **ADR-004: JSONB for AI Responses and Citations**
   - Decision: Store AI response text and citation arrays in PostgreSQL JSONB columns
   - Rationale: Flexible schema, efficient GIN indexing, avoids over-normalization
   - Alternatives: Separate tables per provider (rejected - excessive complexity)

5. **ADR-005: Claude for Sentiment Classification**
   - Decision: Use Anthropic Claude as primary sentiment classifier, with Hugging Face as fallback
   - Rationale: reliability under quota/rate limits; keeps deterministic rubric
   - Alternatives: Custom ML model (rejected - training overhead, accuracy concerns)

**ADR Creation**: Recommend creating ADRs for decisions 1-5 using `/sp.adr` command after plan approval.

## Security & Privacy Considerations

1. **API Key Management**: All AI provider keys stored in backend environment variables, never exposed to client
2. **Session Security**: HTTP-only cookies, secure flag in production, SameSite=Lax
3. **Data Isolation**: Row-level security enforced via user_id FK constraints
4. **Input Validation**: Pydantic schemas validate all API requests, prompt safety checks block malicious inputs
5. **HTTPS Enforcement**: Required for all production communication
6. **Logging**: Structured logs exclude sensitive data (API keys, passwords, PII)
7. **Rate Limiting**: API rate limits per user (e.g., 10 analyses/hour) to prevent abuse
8. **Email Verification**: Required before accessing protected features
9. **Provider Configuration**: Enabled providers configured via environment variables at startup, validated before accepting requests, not exposed in API responses to clients

## Observability & Monitoring (MVP)

1. **Structured Logging**: JSON-formatted logs with request_id, user_id, operation, timestamp
2. **Provider Tracking**: Success/failure rates per provider, timeout tracking, enabled/disabled status logged at startup
3. **Analysis Progress**: Real-time status updates (providers_completed/providers_total, based on enabled providers only)
4. **Error Logging**: Exception traces with context (non-sensitive), error codes for debugging
5. **Performance Metrics**: Response times for API endpoints (p50, p95, p99)

**Deferred to Post-MVP**: Distributed tracing (OpenTelemetry), Metrics dashboards (Prometheus/Grafana), Alerting (PagerDuty)

## Deployment Strategy (Reference)

**MVP Deployment** (Fly.io or Railway recommended):
- Backend: Single container (Gunicorn + Uvicorn workers)
- Frontend: Static export or Next.js server
- Database: Managed PostgreSQL (Fly.io Postgres or Railway Postgres)
- Environment variables: Secure secrets management
- HTTPS: Automatic via platform

**Scaling Considerations** (Post-MVP):
- Horizontal scaling: Multiple API instances behind load balancer
- Caching: Redis for session store and response caching
- Background jobs: Migrate to Celery for async insight generation
- CDN: CloudFront or Cloudflare for static assets

## Open Questions for /sp.tasks

None. All clarifications resolved in spec and clarify phases. Ready to generate tasks.

## Next Steps

1. ✅ Constitution Check: All principles satisfied
2. ✅ Phase 0: Research complete (documented above)
3. ✅ Phase 1: Data model and API contracts defined (to be generated in separate files)
4. ⏭️ **Next Command**: `/sp.tasks` - Generate dependency-ordered, testable tasks organized by user story

**Recommendation**: Create ADRs for significant decisions (ADR-001 through ADR-005) using `/sp.adr` command before proceeding to `/sp.tasks`.
