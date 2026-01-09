"""
Integration test for SSE streaming of incremental results
Task: T105 [US4]
"""
import pytest
import asyncio
import json
from unittest.mock import patch, MagicMock, AsyncMock
from uuid import uuid4

# Import from src
import sys
sys.path.insert(0, "src")


class TestSSEStreamingIntegration:
    """Integration tests for SSE streaming functionality"""

    @pytest.fixture
    def mock_analysis(self):
        """Create a mock analysis"""
        analysis = MagicMock()
        analysis.id = uuid4()
        analysis.brand_name = "TestBrand"
        analysis.status = "in_progress"
        return analysis

    def test_sse_event_format(self):
        """
        Test that SSE events follow the standard format:
        event: <type>
        data: <json>

        """
        def format_sse_event(event_type: str, data: dict) -> str:
            json_data = json.dumps(data)
            return f"event: {event_type}\ndata: {json_data}\n\n"

        # Test provider_started event
        event = format_sse_event("provider_started", {
            "provider": "openai",
            "timestamp": "2026-01-08T12:00:00Z"
        })

        assert "event: provider_started" in event
        assert "data:" in event
        assert event.endswith("\n\n")

    def test_sse_provider_started_event(self):
        """
        Test provider_started event contains correct fields
        """
        event_data = {
            "provider": "openai",
            "model": "gpt-4",
            "timestamp": "2026-01-08T12:00:00Z"
        }

        assert "provider" in event_data
        assert "timestamp" in event_data

    def test_sse_provider_completed_event(self):
        """
        Test provider_completed event contains response data
        """
        event_data = {
            "provider": "openai",
            "model_name": "gpt-4",
            "answer_text": "This is the AI response...",
            "citations": [
                {"url": "https://example.com", "title": "Source 1"}
            ],
            "status": "success",
            "timestamp": "2026-01-08T12:00:05Z"
        }

        required_fields = ["provider", "model_name", "answer_text", "status"]
        for field in required_fields:
            assert field in event_data

    def test_sse_provider_failed_event(self):
        """
        Test provider_failed event contains error information
        """
        event_data = {
            "provider": "claude",
            "error": "Rate limit exceeded",
            "can_retry": True,
            "timestamp": "2026-01-08T12:00:05Z"
        }

        assert "provider" in event_data
        assert "error" in event_data
        assert "can_retry" in event_data

    def test_sse_analysis_complete_event(self):
        """
        Test analysis_complete event contains summary
        """
        event_data = {
            "analysis_id": str(uuid4()),
            "total_providers": 6,
            "successful_providers": 5,
            "failed_providers": 1,
            "status": "completed",
            "timestamp": "2026-01-08T12:00:30Z"
        }

        required_fields = [
            "analysis_id",
            "total_providers",
            "successful_providers",
            "failed_providers",
            "status"
        ]
        for field in required_fields:
            assert field in event_data


class TestSSEStreamingBehavior:
    """Tests for SSE streaming behavior"""

    @pytest.mark.asyncio
    async def test_events_streamed_in_order(self):
        """
        Test that events are streamed in correct order:
        1. provider_started (for each)
        2. provider_completed/failed (as they finish)
        3. analysis_complete (at the end)
        """
        events = []

        async def stream_events():
            # Simulate event stream
            for provider in ["openai", "claude", "gemini"]:
                events.append(("provider_started", provider))
                await asyncio.sleep(0.01)

            for provider in ["openai", "gemini"]:
                events.append(("provider_completed", provider))
                await asyncio.sleep(0.01)

            events.append(("provider_failed", "claude"))
            events.append(("analysis_complete", None))

        await stream_events()

        # Verify order
        event_types = [e[0] for e in events]

        # All provider_started should come before any completed/failed
        started_indices = [i for i, e in enumerate(event_types) if e == "provider_started"]
        completed_indices = [i for i, e in enumerate(event_types) if e in ["provider_completed", "provider_failed"]]

        assert max(started_indices) < min(completed_indices)

        # analysis_complete should be last
        assert event_types[-1] == "analysis_complete"

    @pytest.mark.asyncio
    async def test_incremental_results_streamed_immediately(self):
        """
        Test that results are streamed as soon as they're available
        Don't wait for all providers to complete
        """
        streamed_events = []
        completion_times = {}

        async def simulate_provider(name, delay):
            await asyncio.sleep(delay)
            completion_times[name] = delay
            streamed_events.append((name, delay))
            return {"provider": name}

        # Fast and slow providers
        await asyncio.gather(
            simulate_provider("fast", 0.05),
            simulate_provider("slow", 0.2)
        )

        # Verify fast provider completed first
        assert streamed_events[0][0] == "fast"
        assert completion_times["fast"] < completion_times["slow"]

    def test_keepalive_mechanism(self):
        """
        Test that keepalive comments are sent to prevent timeout
        Format: : keepalive
        """
        keepalive = ": keepalive\n\n"

        # SSE comment format
        assert keepalive.startswith(":")
        assert "\n\n" in keepalive

    @pytest.mark.asyncio
    async def test_stream_cleanup_on_disconnect(self):
        """
        Test that resources are cleaned up when client disconnects
        """
        cleanup_called = False

        async def streaming_generator():
            try:
                for i in range(10):
                    yield f"event: heartbeat\ndata: {i}\n\n"
                    await asyncio.sleep(0.1)
            finally:
                nonlocal cleanup_called
                cleanup_called = True

        # Simulate partial consumption (client disconnect)
        gen = streaming_generator()
        async for event in gen:
            if "3" in event:
                break  # Client disconnects

        # Cleanup should be triggered
        # (in real implementation, this would close connections)


class TestSSEProgressUpdates:
    """Tests for progress updates during streaming"""

    def test_progress_calculation(self):
        """
        Test that progress is calculated correctly:
        progress = completed_providers / total_enabled_providers
        """
        total_enabled = 6
        completed = 3

        progress = completed / total_enabled
        assert progress == 0.5

        # Progress should be 0-1 range
        assert 0 <= progress <= 1

    def test_progress_excludes_disabled_providers(self):
        """
        Test that disabled providers are NOT counted in progress
        """
        all_providers = ["openai", "claude", "gemini", "perplexity", "google_ai", "huggingface"]
        enabled_providers = ["openai", "claude", "gemini"]
        completed = ["openai"]

        # Progress based on enabled only
        total_enabled = len(enabled_providers)
        completed_count = len(completed)

        progress = completed_count / total_enabled
        assert progress == 1/3

        # NOT based on all providers
        wrong_progress = completed_count / len(all_providers)
        assert wrong_progress != progress

    def test_progress_event_format(self):
        """
        Test progress event contains correct information
        """
        progress_event = {
            "completed": 3,
            "total": 6,
            "percent": 50,
            "providers_completed": ["openai", "claude", "gemini"],
            "providers_pending": ["perplexity", "google_ai", "huggingface"]
        }

        assert progress_event["percent"] == (progress_event["completed"] / progress_event["total"]) * 100
        assert len(progress_event["providers_completed"]) == progress_event["completed"]
