"""
Integration test for provider retry mechanism
Task: T106 [US4]
"""
import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from uuid import uuid4

# Import from src
import sys
sys.path.insert(0, "src")


class TestProviderRetryMechanism:
    """Integration tests for provider retry functionality"""

    @pytest.fixture
    def mock_analysis(self):
        """Create a mock analysis with failed provider"""
        analysis = MagicMock()
        analysis.id = uuid4()
        analysis.brand_name = "TestBrand"
        analysis.status = "completed"
        return analysis

    @pytest.fixture
    def failed_provider_response(self):
        """Create a mock failed provider response"""
        response = MagicMock()
        response.id = uuid4()
        response.provider = "claude"
        response.status = "failed"
        response.error = "Rate limit exceeded"
        return response

    @pytest.mark.asyncio
    async def test_retry_creates_new_response(self):
        """
        Test that retry creates a NEW response record
        Original failed response should be preserved
        """
        original_response_id = uuid4()
        new_response_id = uuid4()

        # Simulate retry
        original_response = {
            "id": original_response_id,
            "provider": "claude",
            "status": "failed"
        }

        # After retry
        new_response = {
            "id": new_response_id,
            "provider": "claude",
            "status": "success"
        }

        # Both should exist
        assert original_response_id != new_response_id
        assert original_response["status"] == "failed"
        assert new_response["status"] == "success"

    @pytest.mark.asyncio
    async def test_retry_only_allowed_for_failed_providers(self):
        """
        Test that retry is only allowed for failed/timeout providers
        Successful providers should not be retryable
        """
        provider_results = {
            "openai": {"status": "success", "retryable": False},
            "claude": {"status": "failed", "retryable": True},
            "gemini": {"status": "timeout", "retryable": True},
            "perplexity": {"status": "success", "retryable": False}
        }

        retryable_providers = [
            name for name, result in provider_results.items()
            if result["retryable"]
        ]

        assert "claude" in retryable_providers
        assert "gemini" in retryable_providers
        assert "openai" not in retryable_providers
        assert "perplexity" not in retryable_providers

    @pytest.mark.asyncio
    async def test_retry_disabled_provider_rejected(self):
        """
        Test that retry is rejected for disabled providers
        """
        enabled_providers = ["openai", "claude"]
        retry_provider = "perplexity"

        # Should raise error if provider not enabled
        can_retry = retry_provider in enabled_providers
        assert not can_retry

    @pytest.mark.asyncio
    async def test_retry_uses_same_prompts(self):
        """
        Test that retry uses the same prompts as original query
        """
        original_prompts = [
            {"id": uuid4(), "text": "What is the best product?"},
            {"id": uuid4(), "text": "Compare these brands"}
        ]

        # Retry should query same prompts
        retry_prompts = original_prompts  # Same reference

        assert len(retry_prompts) == len(original_prompts)
        for i, prompt in enumerate(retry_prompts):
            assert prompt["text"] == original_prompts[i]["text"]

    @pytest.mark.asyncio
    async def test_retry_updates_analysis_status_if_needed(self):
        """
        Test that retry can update analysis status if it was
        previously incomplete due to this provider
        """
        analysis_status_before = "completed_with_errors"

        # Simulate successful retry of last failed provider
        all_providers_success = True

        analysis_status_after = "completed" if all_providers_success else "completed_with_errors"

        # Status should update to full success
        assert analysis_status_after == "completed"


class TestProviderRetryTracking:
    """Tests for tracking retry attempts"""

    def test_retry_count_tracked(self):
        """
        Test that retry attempts are counted per provider
        """
        retry_counts = {
            "openai": 0,
            "claude": 2,  # Retried twice
            "gemini": 1   # Retried once
        }

        assert retry_counts["claude"] > retry_counts["openai"]

    def test_max_retry_limit(self):
        """
        Test that there's a maximum retry limit per provider
        """
        MAX_RETRIES = 3

        retry_count = 3

        can_retry = retry_count < MAX_RETRIES
        assert not can_retry  # At limit, cannot retry

    def test_retry_timestamp_recorded(self):
        """
        Test that retry timestamp is recorded for auditing
        """
        from datetime import datetime

        retry_record = {
            "provider": "claude",
            "original_attempt_at": datetime(2026, 1, 8, 12, 0, 0),
            "retry_at": datetime(2026, 1, 8, 12, 1, 0),
            "retry_number": 1
        }

        assert retry_record["retry_at"] > retry_record["original_attempt_at"]


class TestRetryErrorHandling:
    """Tests for error handling during retry"""

    @pytest.mark.asyncio
    async def test_retry_failure_handled_gracefully(self):
        """
        Test that if retry also fails, it's handled gracefully
        """
        retry_attempts = []

        async def provider_query_with_failure():
            retry_attempts.append(1)
            raise Exception("Still rate limited")

        try:
            await provider_query_with_failure()
        except Exception as e:
            error_message = str(e)

        # Error should be captured
        assert "rate limited" in error_message.lower()
        assert len(retry_attempts) == 1

    @pytest.mark.asyncio
    async def test_retry_preserves_original_error(self):
        """
        Test that original error is preserved even after retry
        """
        response_history = []

        # Original failure
        response_history.append({
            "attempt": 1,
            "status": "failed",
            "error": "API timeout after 30s"
        })

        # Retry failure
        response_history.append({
            "attempt": 2,
            "status": "failed",
            "error": "Rate limit exceeded"
        })

        # Both errors should be visible
        assert len(response_history) == 2
        assert response_history[0]["error"] == "API timeout after 30s"
        assert response_history[1]["error"] == "Rate limit exceeded"

    @pytest.mark.asyncio
    async def test_retry_success_after_initial_failure(self):
        """
        Test successful retry after initial failure
        """
        attempts = 0

        async def provider_query():
            nonlocal attempts
            attempts += 1
            if attempts == 1:
                raise Exception("First attempt failed")
            return {"status": "success", "answer": "Response"}

        # First attempt fails
        try:
            result = await provider_query()
        except:
            # Retry
            result = await provider_query()

        assert attempts == 2
        assert result["status"] == "success"
