"""
FastAPI middleware for cross-cutting concerns
Tasks: T197, T201 [Phase 9]

Implements:
- Request ID generation and propagation
- Performance metrics logging
"""
import time
import uuid
from contextvars import ContextVar
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from core.logging import logger

# Context variable for request ID
request_id_var: ContextVar[str] = ContextVar("request_id", default="")


def get_request_id() -> str:
    """Get current request ID from context"""
    return request_id_var.get()


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to generate and propagate request IDs

    - Generates UUID for each request if not provided
    - Sets request ID in context for logging
    - Adds X-Request-ID header to response
    """

    async def dispatch(self, request: Request, call_next):
        # Get or generate request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # Set in context for logging
        request_id_var.set(request_id)

        # Add to request state for handlers to access
        request.state.request_id = request_id

        # Process request
        response = await call_next(request)

        # Add to response headers
        response.headers["X-Request-ID"] = request_id

        return response


class PerformanceMetricsMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log performance metrics

    Logs p50, p95, p99 latencies for API endpoints
    """

    # Store latencies for percentile calculation
    # In production, use proper metrics system (Prometheus, etc.)
    _latencies: dict[str, list[float]] = {}
    _max_samples = 1000  # Keep last N samples per endpoint

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000

        # Get endpoint path pattern
        endpoint = request.url.path

        # Store latency
        if endpoint not in self._latencies:
            self._latencies[endpoint] = []

        self._latencies[endpoint].append(duration_ms)

        # Keep only recent samples
        if len(self._latencies[endpoint]) > self._max_samples:
            self._latencies[endpoint] = self._latencies[endpoint][-self._max_samples:]

        # Log slow requests (>200ms for non-AI endpoints)
        if duration_ms > 200 and "/stream" not in endpoint and "/insights" not in endpoint:
            logger.warning("Slow request detected", extra={
                "operation": "slow_request",
                "endpoint": endpoint,
                "method": request.method,
                "duration_ms": round(duration_ms, 2),
                "request_id": getattr(request.state, "request_id", "unknown")
            })

        # Add timing header
        response.headers["X-Response-Time-Ms"] = str(round(duration_ms, 2))

        return response

    @classmethod
    def get_percentiles(cls, endpoint: str) -> dict:
        """
        Get latency percentiles for an endpoint

        Returns:
            Dict with p50, p95, p99 latencies in ms
        """
        latencies = cls._latencies.get(endpoint, [])

        if not latencies:
            return {"p50": 0, "p95": 0, "p99": 0}

        sorted_latencies = sorted(latencies)
        n = len(sorted_latencies)

        return {
            "p50": sorted_latencies[int(n * 0.50)],
            "p95": sorted_latencies[int(n * 0.95)] if n > 20 else sorted_latencies[-1],
            "p99": sorted_latencies[int(n * 0.99)] if n > 100 else sorted_latencies[-1]
        }

    @classmethod
    def get_all_metrics(cls) -> dict:
        """Get metrics for all endpoints"""
        return {
            endpoint: cls.get_percentiles(endpoint)
            for endpoint in cls._latencies
        }


class LogContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add context to all log messages

    Adds request_id and user_id (if authenticated) to log context
    """

    async def dispatch(self, request: Request, call_next):
        # Log incoming request
        logger.info("Request received", extra={
            "operation": "request_start",
            "method": request.method,
            "path": request.url.path,
            "request_id": getattr(request.state, "request_id", "unknown")
        })

        response = await call_next(request)

        # Log response
        logger.info("Request completed", extra={
            "operation": "request_end",
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "request_id": getattr(request.state, "request_id", "unknown")
        })

        return response
