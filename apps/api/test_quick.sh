#!/bin/bash
# Quick test script for Promptly authentication system
# This runs tests that don't require external services

set -e

echo "=================================================="
echo "  Promptly Quick Test Suite"
echo "=================================================="
echo ""

echo "✓ Running unit tests (no database required)..."
poetry run pytest tests/unit/ -v --tb=short

echo ""
echo "✓ Running OpenAPI contract validation..."
poetry run pytest tests/contract/test_openapi.py -v --tb=short

echo ""
echo "=================================================="
echo "  Quick Tests Complete!"
echo "=================================================="
echo ""
echo "To run full integration tests (requires database):"
echo "  1. Start services: docker-compose up -d"
echo "  2. Run migrations: poetry run alembic upgrade head"
echo "  3. Run all tests: poetry run pytest tests/ -v"
echo ""
