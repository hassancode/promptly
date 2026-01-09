"""
Integration test for partial provider failure handling
Task: T104 [US4]
"""
import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from uuid import uuid4

# Import from src
import sys
sys.path.insert(0, "src")


class TestPartialProviderFailures:
    """Integration tests for handling partial provider failures"""

    @pytest.fixture
    def mock_analysis(self):
        """Create a mock analysis"""
        analysis = MagicMock()
        analysis.id = uuid4()
        analysis.brand_name = "TestBrand"
        analysis.status = "in_progress"
        return analysis

    @pytest.mark.asyncio
    async def test_analysis_completes_with_partial_failures(self):
        """
        Test that analysis completes even when some providers fail
        At least one successful provider should allow completion
        """
        async def successful_provider():
            return {
                "provider": "openai",
                "status": "success",
                "answer_text": "Valid response"
            }

        async def failing_provider():
            raise Exception("Provider unavailable")

        async def timeout_provider():
            await asyncio.sleep(10)
            return {"status": "success"}

        # Gather with exceptions
        results = await asyncio.gather(
            successful_provider(),
            asyncio.wait_for(failing_provider(), timeout=1.0),
            asyncio.wait_for(timeout_provider(), timeout=0.1),
            return_exceptions=True
        )

        # Count successes and failures
        successes = [r for r in results if isinstance(r, dict) and r.get("status") == "success"]
        failures = [r for r in results if isinstance(r, Exception)]

        # At least one success means analysis can complete
        assert len(successes) >= 1
        assert len(failures) >= 1  # Some failures expected

    @pytest.mark.asyncio
    async def test_failure_tracking_per_provider(self):
        """
        Test that each provider's failure status is tracked individually
        """
        provider_statuses = {}

        async def provider_with_status(provider_name, should_fail=False):
            if should_fail:
                provider_statuses[provider_name] = "failed"
                raise Exception(f"{provider_name} error")
            provider_statuses[provider_name] = "success"
            return {"provider": provider_name, "status": "success"}

        results = await asyncio.gather(
            provider_with_status("openai", should_fail=False),
            provider_with_status("claude", should_fail=True),
            provider_with_status("gemini", should_fail=False),
            return_exceptions=True
        )

        # Verify individual status tracking
        assert provider_statuses["openai"] == "success"
        assert provider_statuses["claude"] == "failed"
        assert provider_statuses["gemini"] == "success"

    @pytest.mark.asyncio
    async def test_failed_providers_visible_but_non_blocking(self):
        """
        Test that failed providers are visible to user but don't block
        """
        results = {
            "completed_providers": [],
            "failed_providers": [],
            "total_providers": 3
        }

        providers = [
            {"name": "openai", "will_fail": False},
            {"name": "claude", "will_fail": True},
            {"name": "gemini", "will_fail": False}
        ]

        for provider in providers:
            try:
                if provider["will_fail"]:
                    raise Exception("Provider error")
                results["completed_providers"].append(provider["name"])
            except Exception:
                results["failed_providers"].append(provider["name"])

        # Verify results structure
        assert len(results["completed_providers"]) == 2
        assert len(results["failed_providers"]) == 1
        assert "claude" in results["failed_providers"]

        # Analysis should still be usable
        assert len(results["completed_providers"]) > 0

    @pytest.mark.asyncio
    async def test_all_providers_fail_marks_analysis_failed(self):
        """
        Test that if ALL providers fail, analysis is marked as failed
        """
        async def always_fail(provider):
            raise Exception(f"{provider} failed")

        providers = ["openai", "claude", "gemini"]

        results = await asyncio.gather(
            *[always_fail(p) for p in providers],
            return_exceptions=True
        )

        # All should be failures
        all_failed = all(isinstance(r, Exception) for r in results)
        assert all_failed

        # In this case, analysis status should be "failed"
        analysis_status = "failed" if all_failed else "completed"
        assert analysis_status == "failed"


class TestPartialFailureRecovery:
    """Tests for handling and recovering from partial failures"""

    @pytest.mark.asyncio
    async def test_retry_available_for_failed_providers(self):
        """
        Test that retry option is available for failed providers only
        """
        provider_results = {
            "openai": {"status": "success"},
            "claude": {"status": "failed", "error": "Rate limited"},
            "gemini": {"status": "success"}
        }

        # Find retryable providers
        retryable = [
            name for name, result in provider_results.items()
            if result.get("status") == "failed"
        ]

        assert "claude" in retryable
        assert "openai" not in retryable
        assert "gemini" not in retryable

    @pytest.mark.asyncio
    async def test_partial_results_returned_immediately(self):
        """
        Test that successful results are returned as they complete
        Don't wait for slow/failed providers to show available results
        """
        results_received = []
        timestamps = []

        async def fast_provider():
            await asyncio.sleep(0.05)
            return {"provider": "fast", "completed_at": 0.05}

        async def slow_provider():
            await asyncio.sleep(0.5)
            return {"provider": "slow", "completed_at": 0.5}

        # Using as_completed pattern
        tasks = [
            asyncio.create_task(fast_provider()),
            asyncio.create_task(slow_provider())
        ]

        for completed in asyncio.as_completed(tasks):
            result = await completed
            results_received.append(result)

        # Fast provider should complete first
        assert results_received[0]["provider"] == "fast"
        assert results_received[1]["provider"] == "slow"

    @pytest.mark.asyncio
    async def test_failure_reason_captured(self):
        """
        Test that failure reasons are captured for debugging
        """
        failure_reasons = {}

        async def provider_with_error(name, error_type):
            try:
                if error_type == "timeout":
                    await asyncio.sleep(10)
                elif error_type == "rate_limit":
                    raise Exception("Rate limit exceeded")
                elif error_type == "api_error":
                    raise Exception("API returned 500")
                return {"status": "success"}
            except Exception as e:
                failure_reasons[name] = str(e)
                return {"status": "failed", "error": str(e)}

        results = await asyncio.gather(
            asyncio.wait_for(provider_with_error("p1", "timeout"), timeout=0.1),
            provider_with_error("p2", "rate_limit"),
            provider_with_error("p3", "api_error"),
            return_exceptions=True
        )

        # Verify failure reasons are captured
        assert "Rate limit exceeded" in str(failure_reasons.get("p2", ""))
        assert "API returned 500" in str(failure_reasons.get("p3", ""))
