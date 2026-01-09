# Promptly API

FastAPI backend for the AI Search Visibility Platform.

## Setup

### Prerequisites

- Python 3.12+
- Poetry (dependency manager)
- PostgreSQL 15+
- Redis 7+

### Installation

```bash
# Install dependencies
poetry install

# Copy environment file
cp .env.example .env

# Edit .env with your configuration
# - Add database credentials
# - Add AI provider API keys
# - Set ENABLED_PROVIDERS
```

### Database Setup

```bash
# Run migrations
poetry run alembic upgrade head

# Create new migration (after model changes)
poetry run alembic revision --autogenerate -m "description"

# Rollback last migration
poetry run alembic downgrade -1
```

### Running the Server

```bash
# Development (with hot reload)
PYTHONPATH=src poetry run uvicorn main:app --reload --port 8000

# Production (with Gunicorn)
PYTHONPATH=src poetry run gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

## Project Structure

```
apps/api/
├── src/
│   ├── api/                    # Route handlers
│   │   ├── v1/                 # API v1 endpoints
│   │   │   ├── __init__.py     # Router aggregation
│   │   │   ├── auth.py         # Authentication routes
│   │   │   ├── analyses.py     # Analysis CRUD
│   │   │   ├── responses.py    # Provider responses
│   │   │   └── insights.py     # Insights endpoints
│   │   └── health.py           # Health check endpoints
│   │
│   ├── core/                   # Core infrastructure
│   │   ├── config.py           # Pydantic settings
│   │   ├── database.py         # SQLAlchemy session
│   │   ├── redis.py            # Redis client
│   │   ├── security.py         # Password hashing
│   │   ├── providers.py        # AI provider config
│   │   ├── rate_limit.py       # Rate limiting
│   │   ├── middleware.py       # Request ID, metrics
│   │   ├── logging.py          # Structured logging
│   │   ├── exceptions.py       # Custom exceptions
│   │   └── session_store.py    # Redis sessions
│   │
│   ├── models/                 # SQLAlchemy models
│   │   ├── user.py             # User model
│   │   ├── analysis.py         # Analysis model
│   │   ├── competitor.py       # Competitor model
│   │   ├── prompt.py           # Prompt model
│   │   ├── ai_response.py      # AIResponse model
│   │   ├── citation.py         # Citation model
│   │   └── insight.py          # Insight/Recommendation
│   │
│   ├── schemas/                # Pydantic schemas
│   │   ├── common.py           # Shared schemas
│   │   ├── auth.py             # Auth DTOs
│   │   ├── analysis.py         # Analysis DTOs
│   │   ├── response.py         # Response DTOs
│   │   └── insight.py          # Insight DTOs
│   │
│   ├── services/               # Business logic
│   │   ├── user_service.py     # User operations
│   │   ├── analysis_service.py # Analysis operations
│   │   ├── provider_service.py # Provider orchestration
│   │   ├── insight_service.py  # Insight generation
│   │   └── scoring_service.py  # Visibility scoring
│   │
│   ├── adapters/               # AI provider adapters
│   │   ├── base.py             # Base adapter interface
│   │   ├── openai_adapter.py   # OpenAI GPT
│   │   ├── claude_adapter.py   # Anthropic Claude
│   │   ├── gemini_adapter.py   # Google Gemini
│   │   ├── perplexity_adapter.py
│   │   ├── google_ai_adapter.py
│   │   └── huggingface_adapter.py
│   │
│   └── main.py                 # Application entry
│
├── tests/
│   ├── conftest.py             # Pytest fixtures
│   ├── unit/                   # Unit tests
│   │   ├── test_user_service.py
│   │   ├── test_scoring_service.py
│   │   └── test_session_store.py
│   ├── contract/               # OpenAPI contract tests
│   │   ├── test_auth_contract.py
│   │   ├── test_analysis_contract.py
│   │   ├── test_streaming_contract.py
│   │   └── test_insights_contract.py
│   └── integration/            # Integration tests
│       ├── test_auth_flow.py
│       ├── test_analysis_flow.py
│       └── test_provider_orchestration.py
│
├── alembic/                    # Database migrations
│   ├── versions/               # Migration files
│   └── env.py                  # Migration config
│
├── pyproject.toml              # Project config & deps
└── .env.example                # Environment template
```

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login |
| POST | `/api/v1/auth/logout` | Logout |
| GET | `/api/v1/auth/me` | Get current user |
| GET | `/api/v1/auth/verify/{token}` | Verify email |

### Analyses

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/analyses` | Create analysis |
| GET | `/api/v1/analyses` | List user's analyses |
| GET | `/api/v1/analyses/{id}` | Get analysis by ID |
| POST | `/api/v1/analyses/{id}/start` | Start analysis (stream) |
| GET | `/api/v1/analyses/{id}/progress` | Get progress |

### Responses

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/analyses/{id}/responses` | Get AI responses |
| POST | `/api/v1/responses/{id}/retry` | Retry failed provider |

### Insights

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/analyses/{id}/insights` | Generate insights |
| GET | `/api/v1/analyses/{id}/insights` | Get insights |
| GET | `/api/v1/analyses/{id}/recommendations` | Get recommendations |

### Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Basic health check |
| GET | `/ready` | Readiness (DB + Redis) |
| GET | `/live` | Liveness check |

## Testing

```bash
# Run all tests
poetry run pytest

# Run with verbose output
poetry run pytest -v

# Run specific test file
poetry run pytest tests/unit/test_user_service.py

# Run specific test
poetry run pytest tests/unit/test_user_service.py::test_create_user

# Run tests matching pattern
poetry run pytest -k "auth"

# Run with coverage
poetry run pytest --cov=src --cov-report=html

# Run contract tests only
poetry run pytest tests/contract/

# Run integration tests only
poetry run pytest tests/integration/
```

## Code Quality

```bash
# Format code
poetry run black src/ tests/

# Check linting
poetry run ruff check src/ tests/

# Fix auto-fixable issues
poetry run ruff check --fix src/ tests/

# Type checking
poetry run mypy src/
```

## Configuration

### Required Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/promptly

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-min-32-chars

# Providers (comma-separated)
ENABLED_PROVIDERS=openai,claude,gemini
```

### AI Provider Configuration

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-...

# Google Gemini
GOOGLE_API_KEY=AIza...

# Perplexity
PERPLEXITY_API_KEY=pplx-...

# Google AI Search
GOOGLE_AI_API_KEY=...
GOOGLE_AI_CX=...

# HuggingFace
HUGGINGFACE_API_KEY=hf_...
```

### Provider Selection

Only providers listed in `ENABLED_PROVIDERS` will be queried. API keys for disabled providers are not required.

Example: `ENABLED_PROVIDERS=openai,claude` will only query OpenAI and Claude, ignoring other providers even if their API keys are configured.

## Rate Limiting

- Analysis creation: 10 per hour per user
- Enforced via Redis-backed sliding window
- Rate limit info included in response headers:
  - `X-RateLimit-Limit`
  - `X-RateLimit-Remaining`
  - `X-RateLimit-Reset`

## Logging

Structured JSON logging with context:
- `request_id`: Unique ID for request tracing
- `user_id`: Authenticated user ID
- `operation`: Type of operation
- `duration_ms`: Request duration

Slow requests (>200ms) are logged as warnings.

## Health Checks

- `/health`: Basic API health
- `/ready`: Database and Redis connectivity
- `/live`: Process liveness

Use `/ready` for Kubernetes readiness probes and `/live` for liveness probes.
