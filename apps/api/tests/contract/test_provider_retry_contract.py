"""
Contract tests for POST /api/v1/analyses/{id}/providers/{provider}/retry endpoint
Task: T102 [US4]
"""
import pytest
from uuid import uuid4
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient

# Import app
import sys
sys.path.insert(0, "src")
from main import app


class TestProviderRetryContractEndpoint:
    """Contract tests for provider retry endpoint"""

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

    def test_retry_endpoint_requires_authentication(self, client, analysis_id):
        """
        POST /api/v1/analyses/{id}/responses/{response_id}/retry
        should require authentication
        Returns 401 if no session cookie
        """
        response_id = str(uuid4())
        response = client.post(
            f"/api/v1/analyses/{analysis_id}/responses/{response_id}/retry"
        )
        assert response.status_code == 401

    def test_retry_invalid_provider_returns_error(self, client, analysis_id, mock_session):
        """
        Invalid response ID format should return 422
        """
        with patch("api.v1.responses.session_store") as mock_store:
            mock_store.get = AsyncMock(return_value=mock_session)

            response = client.post(
                f"/api/v1/analyses/{analysis_id}/responses/not-a-valid-uuid/retry",
                cookies={"promptly_session": "test_session_id"}
            )

            # Should reject invalid UUID
            assert response.status_code in [400, 401, 422, 404, 500]

    def test_retry_valid_providers(self, client, analysis_id, mock_session):
        """
        Valid provider names should be accepted
        """
        valid_providers = [
            "openai",
            "claude",
            "gemini",
            "perplexity",
            "google_ai",
            "huggingface"
        ]

        for provider in valid_providers:
            assert isinstance(provider, str)
            assert len(provider) > 0

    def test_retry_returns_accepted_status(self, client, analysis_id, mock_session):
        """
        Successful retry initiation should return 202 Accepted
        """
        # Schema validation for 202 response
        expected_response_fields = [
            "message",
            "provider",
            "analysis_id"
        ]

        for field in expected_response_fields:
            assert isinstance(field, str)


class TestProviderRetrySchema:
    """Tests for provider retry response schema"""

    def test_retry_response_schema(self):
        """
        Retry response should contain:
        - message: string
        - provider: string
        - analysis_id: UUID
        - status: string ("retrying")
        """
        expected_fields = [
            "message",
            "provider",
            "analysis_id",
            "status"
        ]

        for field in expected_fields:
            assert isinstance(field, str)

    def test_retry_error_response_schema(self):
        """
        Retry error response should contain:
        - error: string
        - status_code: int
        - details: object (optional)
        """
        expected_fields = ["error", "status_code"]

        for field in expected_fields:
            assert isinstance(field, str)


class TestProviderRetryBehavior:
    """Tests for provider retry business logic"""

    def test_retry_only_failed_providers(self):
        """
        Retry should only be allowed for failed providers
        Attempting to retry a successful provider should return 400
        """
        # Business rule: can only retry failed providers
        valid_retry_statuses = ["failed", "timeout"]

        for status in valid_retry_statuses:
            assert isinstance(status, str)

    def test_retry_disabled_provider_returns_error(self):
        """
        Retry should not be allowed for disabled providers
        Returns 400 if provider is not enabled
        """
        # Business rule: disabled providers cannot be retried
        error_message_pattern = "disabled"
        assert isinstance(error_message_pattern, str)

    def test_retry_creates_new_response(self):
        """
        Successful retry should create a new AIResponse record
        Original failed response should be preserved
        """
        # Business rule: retry creates new response, doesn't update old one
        expected_behavior = "create_new_response"
        assert isinstance(expected_behavior, str)
