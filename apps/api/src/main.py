"""
Promptly API - AI Search Visibility Platform
FastAPI backend application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from contextlib import asynccontextmanager

from core.logging import setup_logging, get_logger
from core.redis import close_redis
from core.config import settings
from core.providers import provider_config
from core.exceptions import (
    AppException,
    app_exception_handler,
    validation_exception_handler,
    database_exception_handler,
    general_exception_handler,
)
from core.middleware import (
    RequestIDMiddleware,
    PerformanceMetricsMiddleware,
    LogContextMiddleware,
)
from api.v1 import router as v1_router
from api.health import router as health_router

# Setup logging
setup_logging(level="DEBUG" if settings.DEBUG else "INFO")
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Promptly API", extra={"operation": "startup"})

    # Log enabled/disabled provider status (T200)
    logger.info(
        "Provider configuration loaded",
        extra={
            "operation": "startup",
            "enabled_providers": provider_config.enabled_providers,
            "disabled_providers": [
                p for p in ["openai", "claude", "gemini", "perplexity", "google_ai", "huggingface"]
                if p not in provider_config.enabled_providers
            ]
        }
    )

    yield
    # Shutdown
    logger.info("Shutting down Promptly API", extra={"operation": "shutdown"})
    await close_redis()


app = FastAPI(
    title="Promptly API",
    description="""
## AI Search Visibility & Competitive Insight Platform

Promptly helps you understand how your brand appears in AI-generated answers across multiple AI providers.

### Features

- **Multi-Provider Analysis**: Query OpenAI, Claude, Gemini, Perplexity, and more simultaneously
- **Visibility Scoring**: Get quantitative scores on brand presence, frequency, and position
- **Sentiment Analysis**: Understand how AI models perceive your brand
- **Competitive Insights**: Compare your visibility against competitors
- **Actionable Recommendations**: Get prioritized suggestions to improve AI visibility

### Authentication

Most endpoints require authentication via session cookies. Use `/api/v1/auth/login` to authenticate.

### Rate Limits

- Analysis creation: 10 per hour per user
- API calls: Standard rate limits apply

### Support

For API support, contact support@promptly.ai
    """,
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=[
        {"name": "health", "description": "Health check endpoints"},
        {"name": "auth", "description": "Authentication and user management"},
        {"name": "analyses", "description": "Brand visibility analysis operations"},
        {"name": "responses", "description": "AI provider response management"},
        {"name": "insights", "description": "Analysis insights and recommendations"},
    ],
    contact={
        "name": "Promptly Support",
        "email": "support@promptly.ai",
    },
    license_info={
        "name": "Proprietary",
    },
)

# Register exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, database_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# CORS configuration
allowed_origins = ["http://localhost:3000", "http://127.0.0.1:3000"]

# Add origins from CORS_ORIGINS env var
if settings.CORS_ORIGINS:
    allowed_origins.extend([o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()])

# In development, allow Codespaces URLs
allow_origin_regex = None
if settings.ENVIRONMENT == "development":
    # Allow GitHub Codespaces URLs (*.app.github.dev)
    allow_origin_regex = r"https://.*\.app\.github\.dev"

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=allow_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware (order matters - last added runs first)
app.add_middleware(LogContextMiddleware)
app.add_middleware(PerformanceMetricsMiddleware)
app.add_middleware(RequestIDMiddleware)

# Include API v1 router
app.include_router(v1_router)

# Include health check endpoints
app.include_router(health_router)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "Promptly API is running", "version": "0.1.0"}


@app.get("/api/v1/health")
async def health():
    """API health check"""
    return {"status": "healthy", "service": "promptly-api"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=settings.DEBUG)
