# Promptly

AI Search Visibility & Competitive Insight Platform

## Overview

Promptly helps brands understand how they appear in AI-generated answers. Query multiple AI providers simultaneously, collect citations, and get evidence-backed insights comparing your brand visibility against competitors.

## Key Features

- **Multi-Provider Analysis**: Query OpenAI, Claude, Gemini, Perplexity, Google AI, and HuggingFace simultaneously
- **Real-time Streaming**: SSE-based streaming shows results as they arrive from each provider
- **Visibility Scoring**: Quantitative scores based on presence (40%), frequency (30%), and position (30%)
- **Sentiment Analysis**: Primary analysis via Claude with HuggingFace fallback
- **Competitive Insights**: Side-by-side comparison of brand visibility vs competitors
- **Actionable Recommendations**: Prioritized suggestions with evidence links

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js)                      │
│  - App Router with TypeScript                                   │
│  - Tailwind CSS + Brand Theme                                   │
│  - React Context for Auth State                                 │
│  - SSE Client for Streaming                                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         API Gateway (FastAPI)                   │
│  - Session-based Authentication                                 │
│  - Rate Limiting (10 analyses/hour)                             │
│  - Request ID Propagation                                       │
│  - Structured JSON Logging                                      │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  PostgreSQL   │    │    Redis      │    │ AI Providers  │
│  - Users      │    │  - Sessions   │    │  - OpenAI     │
│  - Analyses   │    │  - Rate Limit │    │  - Claude     │
│  - Responses  │    │  - Cache      │    │  - Gemini     │
│  - Insights   │    │               │    │  - Perplexity │
└───────────────┘    └───────────────┘    │  - Google AI  │
                                          │  - HuggingFace│
                                          └───────────────┘
```

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Next.js 14 (App Router), TypeScript, Tailwind CSS |
| **Backend** | FastAPI, Python 3.12+, SQLAlchemy 2.0, Pydantic |
| **Database** | PostgreSQL 15+ with Alembic migrations |
| **Cache** | Redis 7+ for sessions and rate limiting |
| **Infrastructure** | Docker Compose |

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for local development)
- Python 3.12+ (for local development)
- Poetry (Python dependency manager)

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd promptly

# Copy environment files
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env.local

# Add your AI provider API keys to apps/api/.env

# Start all services
docker-compose up

# Access:
# - Frontend: http://localhost:3000
# - API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - ReDoc: http://localhost:8000/redoc
```

### Option 2: Local Development

**1. Start infrastructure:**
```bash
docker-compose up postgres redis
```

**2. Start the API:**
```bash
cd apps/api
cp .env.example .env
# Edit .env and add your API keys
poetry install
poetry run alembic upgrade head
poetry run uvicorn src.main:app --reload --port 8000
```

**3. Start the Frontend:**
```bash
cd apps/web
cp .env.example .env.local
npm install
npm run dev
```

## Project Structure

```
promptly/
├── apps/
│   ├── api/                    # FastAPI backend
│   │   ├── src/
│   │   │   ├── api/            # Route handlers
│   │   │   │   ├── v1/         # API v1 endpoints
│   │   │   │   └── health.py   # Health checks
│   │   │   ├── core/           # Core infrastructure
│   │   │   │   ├── config.py   # Settings management
│   │   │   │   ├── database.py # SQLAlchemy setup
│   │   │   │   ├── redis.py    # Redis client
│   │   │   │   ├── security.py # Password hashing
│   │   │   │   └── providers.py# Provider config
│   │   │   ├── models/         # SQLAlchemy models
│   │   │   ├── schemas/        # Pydantic schemas
│   │   │   ├── services/       # Business logic
│   │   │   └── adapters/       # AI provider adapters
│   │   ├── tests/
│   │   │   ├── unit/           # Unit tests
│   │   │   ├── contract/       # OpenAPI contract tests
│   │   │   └── integration/    # Integration tests
│   │   ├── alembic/            # Database migrations
│   │   └── pyproject.toml
│   │
│   └── web/                    # Next.js frontend
│       ├── app/                # App Router pages
│       │   ├── login/          # Authentication
│       │   ├── register/
│       │   ├── dashboard/      # Protected pages
│       │   └── analysis/       # Analysis workflow
│       ├── components/         # React components
│       │   ├── analysis/       # Analysis UI components
│       │   └── insights/       # Insights display
│       ├── lib/                # Utilities
│       │   ├── api-client.ts   # API wrapper
│       │   └── auth-context.tsx# Auth state
│       └── package.json
│
├── specs/                      # Feature specifications
│   └── 001-ai-visibility-platform/
│       ├── spec.md             # Requirements
│       ├── plan.md             # Architecture
│       ├── tasks.md            # Implementation tasks
│       └── contracts/          # OpenAPI specs
│
├── docker-compose.yml
└── README.md
```

## Configuration

### Backend Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `REDIS_URL` | Redis connection string | Yes |
| `SECRET_KEY` | Session encryption key | Yes |
| `ENABLED_PROVIDERS` | Comma-separated provider list | Yes |
| `OPENAI_API_KEY` | OpenAI API key | If enabled |
| `ANTHROPIC_API_KEY` | Anthropic Claude API key | If enabled |
| `GOOGLE_API_KEY` | Google Gemini API key | If enabled |
| `PERPLEXITY_API_KEY` | Perplexity API key | If enabled |
| `GOOGLE_AI_API_KEY` | Google AI Search API key | If enabled |
| `HUGGINGFACE_API_KEY` | HuggingFace API key | If enabled |

See `apps/api/.env.example` for complete list.

### Frontend Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | Yes |
| `NEXT_PUBLIC_SITE_URL` | Site URL for SEO | No |

## Development

### Running Tests

```bash
# All backend tests
cd apps/api
poetry run pytest

# Contract tests only
poetry run pytest tests/contract/

# Integration tests only
poetry run pytest tests/integration/

# With coverage
poetry run pytest --cov=src --cov-report=html

# Frontend tests
cd apps/web
npm test
```

### Code Quality

```bash
# Backend
cd apps/api
poetry run black src/ tests/
poetry run ruff check src/ tests/

# Frontend
cd apps/web
npm run lint
npm run type-check
```

### Database Migrations

```bash
cd apps/api

# Create new migration
poetry run alembic revision --autogenerate -m "description"

# Apply migrations
poetry run alembic upgrade head

# Rollback one migration
poetry run alembic downgrade -1
```

## API Documentation

Interactive API documentation is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Implementation Status

### Completed Phases

| Phase | Description | Tasks |
|-------|-------------|-------|
| Phase 1 | Project Setup | 9/9 |
| Phase 2 | Foundational Infrastructure | 27/27 |
| Phase 3 | User Authentication (US1) | 24/24 |
| Phase 4 | Brand/Competitor Setup (US2) | 17/17 |
| Phase 5 | Prompt Configuration (US3) | 14/14 |
| Phase 6 | Multi-Provider Query (US4) | 30/30 |
| Phase 7 | Response Viewing (US5) | 31/31 |
| Phase 8 | Insights Generation (US6) | 27/27 |
| Phase 9 | Polish & Production | In Progress |

### Test Coverage

- **Contract Tests**: OpenAPI schema validation
- **Integration Tests**: End-to-end API flows
- **Unit Tests**: Services, scoring algorithms, adapters

## Contributing

1. Create a feature branch from `main`
2. Write tests first (TDD)
3. Implement the feature
4. Ensure all tests pass
5. Submit a pull request

## License

Proprietary
