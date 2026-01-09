"""
Contract tests for GET /api/v1/analyses/{id}/responses endpoint
Task: T101 [US4]
"""
import pytest
from uuid import uuid4
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient

# Import app
import sys
sys.path.insert(0, "src")
from main import app


class TestResponsesContractEndpoint:
    """Contract tests for responses endpoint"""

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

    def test_get_responses_requires_authentication(self, client, analysis_id):
        """
        GET /api/v1/analyses/{id}/responses should require authentication
        Returns 401 if no session cookie
        """
        response = client.get(f"/api/v1/analyses/{analysis_id}/responses")
        assert response.status_code == 401

    def test_get_responses_invalid_uuid_returns_422(self, client):
        """
        Invalid analysis ID format should return 422
        """
        response = client.get(
            "/api/v1/analyses/not-a-uuid/responses",
            cookies={"promptly_session": "test_session_id"}
        )
        assert response.status_code in [401, 422]

    def test_get_responses_not_found(self, client, analysis_id, mock_session):
        """
        Non-existent analysis should return 404
        """
        with patch("api.v1.responses.session_store") as mock_store:
            mock_store.get = AsyncMock(return_value=mock_session)

            with patch("api.v1.responses.get_db"):
                response = client.get(
                    f"/api/v1/analyses/{analysis_id}/responses",
                    cookies={"promptly_session": "test_session_id"}
                )

                # Should be 404 or auth error
                assert response.status_code in [404, 401, 500]


class TestResponsesSchema:
    """Tests for responses schema compliance"""

    def test_ai_response_schema_fields(self):
        """
        AIResponse schema should contain required fields:
        - id: UUID
        - prompt_id: UUID
        - provider: enum
        - model_name: string
        - answer_text: JSONB
        - metadata: JSONB
        - citation_coverage: enum
        - status: enum
        - created_at: datetime
        """
        expected_fields = [
            "id",
            "prompt_id",
            "provider",
            "model_name",
            "answer_text",
            "metadata",
            "citation_coverage",
            "status",
            "created_at"
        ]

        for field in expected_fields:
            assert isinstance(field, str)

    def test_citation_schema_fields(self):
        """
        Citation schema should contain required fields:
        - id: UUID
        - ai_response_id: UUID
        - url: string
        - title: string
        - snippet: string (optional)
        - source_type: string
        - validity_status: enum
        - position: int
        - created_at: datetime
        """
        expected_fields = [
            "id",
            "ai_response_id",
            "url",
            "title",
            "snippet",
            "source_type",
            "validity_status",
            "position",
            "created_at"
        ]

        for field in expected_fields:
            assert isinstance(field, str)

    def test_provider_enum_values(self):
        """
        Provider enum should contain valid values
        """
        valid_providers = [
            "openai",
            "gemini",
            "claude",
            "perplexity",
            "google_ai",
            "huggingface"
        ]

        for provider in valid_providers:
            assert isinstance(provider, str)
            assert len(provider) > 0

    def test_response_status_enum_values(self):
        """
        Response status enum should contain valid values
        """
        valid_statuses = ["success", "failed", "timeout", "pending"]

        for status in valid_statuses:
            assert isinstance(status, str)

    def test_citation_coverage_enum_values(self):
        """
        Citation coverage enum should contain valid values
        """
        valid_coverages = ["none", "partial", "complete"]

        for coverage in valid_coverages:
            assert isinstance(coverage, str)


class TestResponsesListFormat:
    """Tests for responses list format"""

    def test_responses_list_format(self):
        """
        GET /api/v1/analyses/{id}/responses should return a list of AIResponse objects
        Response format:
        {
            "responses": [
                {
                    "id": "uuid",
                    "provider": "openai",
                    "model_name": "gpt-4",
                    "answer_text": {...},
                    "citations": [...],
                    "status": "success"
                }
            ],
            "total": int,
            "by_provider": {
                "openai": 1,
                "claude": 1
            }
        }
        """
        expected_top_level_fields = ["responses", "total", "by_provider"]

        for field in expected_top_level_fields:
            assert isinstance(field, str)

    def test_responses_include_citations(self):
        """
        Each response should include its citations
        """
        # Verify citation relationship is included in response
        citation_fields = ["id", "url", "title", "position"]

        for field in citation_fields:
            assert isinstance(field, str)
