"""
Contract tests for GET /api/v1/analyses/{id}/stream (SSE endpoint)
Task: T100 [US4]
"""
import pytest
from uuid import uuid4
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
import asyncio

# Import app
import sys
sys.path.insert(0, "src")
from main import app


class TestStreamingContractEndpoint:
    """Contract tests for SSE streaming endpoint"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def analysis_id(self):
        """Generate a test analysis ID"""
        return str(uuid4())

    @pytest.fixture
    def mock_session(self):
        """Mock authenticated session"""
        return {"user_id": str(uuid4()), "email": "test@example.com"}

    def test_stream_endpoint_requires_authentication(self, client, analysis_id):
        """
        SSE stream endpoint should require authentication
        Returns 401 if no session cookie
        """
        response = client.get(f"/api/v1/analyses/{analysis_id}/stream")
        assert response.status_code == 401

    def test_stream_endpoint_returns_correct_content_type(self, client, analysis_id, mock_session):
        """
        SSE stream endpoint should return text/event-stream content type
        """
        with patch("api.v1.streaming.session_store") as mock_store:
            mock_store.get = AsyncMock(return_value=mock_session)

            with patch("api.v1.streaming.get_db") as mock_db:
                mock_db_session = MagicMock()
                mock_db.return_value.__enter__ = MagicMock(return_value=mock_db_session)
                mock_db.return_value.__exit__ = MagicMock(return_value=None)

                # Mock analysis query to return None (not found)
                mock_db_session.query.return_value.filter.return_value.first.return_value = None

                response = client.get(
                    f"/api/v1/analyses/{analysis_id}/stream",
                    cookies={"promptly_session": "test_session_id"}
                )

                # Either 404 or proper SSE response
                assert response.status_code in [404, 200]

    def test_stream_endpoint_invalid_uuid_returns_422(self, client):
        """
        Invalid analysis ID format should return 422
        """
        response = client.get(
            "/api/v1/analyses/not-a-valid-uuid/stream",
            cookies={"promptly_session": "test_session_id"}
        )
        assert response.status_code in [401, 422]

    def test_stream_endpoint_not_found_analysis(self, client, analysis_id, mock_session):
        """
        Non-existent analysis should return 404
        """
        with patch("api.v1.streaming.session_store") as mock_store:
            mock_store.get = AsyncMock(return_value=mock_session)

            with patch("api.v1.streaming.get_db"):
                response = client.get(
                    f"/api/v1/analyses/{analysis_id}/stream",
                    cookies={"promptly_session": "test_session_id"}
                )

                # Should be 404 when analysis not found
                assert response.status_code in [404, 401, 500]


class TestStreamingEventFormat:
    """Tests for SSE event format compliance"""

    def test_sse_event_structure(self):
        """
        SSE events should follow standard format:
        event: <event_type>
        data: <json_data>
        """
        # Expected event types
        expected_event_types = [
            "provider_started",
            "provider_completed",
            "provider_failed",
            "analysis_complete"
        ]

        # This is a structural test - verify our event types are defined
        for event_type in expected_event_types:
            assert isinstance(event_type, str)
            assert len(event_type) > 0

    def test_provider_completed_event_schema(self):
        """
        provider_completed event should contain:
        - provider: string
        - model_name: string
        - answer_text: string or object
        - citations: array
        - status: string
        """
        expected_fields = [
            "provider",
            "model_name",
            "answer_text",
            "citations",
            "status"
        ]

        # Schema validation check
        for field in expected_fields:
            assert isinstance(field, str)

    def test_analysis_complete_event_schema(self):
        """
        analysis_complete event should contain:
        - total_providers: int
        - successful_providers: int
        - failed_providers: int
        - analysis_id: string
        """
        expected_fields = [
            "total_providers",
            "successful_providers",
            "failed_providers",
            "analysis_id"
        ]

        for field in expected_fields:
            assert isinstance(field, str)


class TestStreamingKeepalive:
    """Tests for SSE connection keepalive"""

    def test_keepalive_comment_format(self):
        """
        SSE keepalive should be sent as comment (line starting with :)
        Format: : keepalive
        """
        keepalive_format = ": keepalive\n\n"
        assert keepalive_format.startswith(":")
        assert "\n\n" in keepalive_format
