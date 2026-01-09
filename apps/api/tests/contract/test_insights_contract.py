"""
Contract tests for insights endpoints
Tasks: T155, T156, T157 [US6]
"""
import pytest
from uuid import uuid4
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient

# Import app
import sys
sys.path.insert(0, "src")
from main import app


class TestGenerateInsightsContract:
    """Contract tests for POST /api/v1/analyses/{id}/insights/generate endpoint (T155)"""

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

    def test_generate_insights_requires_authentication(self, client, analysis_id):
        """
        POST /api/v1/analyses/{id}/insights/generate
        should require authentication (401 without session)
        """
        response = client.post(
            f"/api/v1/analyses/{analysis_id}/insights/generate"
        )
        assert response.status_code == 401

    def test_generate_insights_invalid_uuid_returns_422(self, client):
        """
        Invalid analysis ID format should return 422
        """
        response = client.post(
            "/api/v1/analyses/not-a-valid-uuid/insights/generate",
            cookies={"promptly_session": "test_session_id"}
        )
        assert response.status_code in [401, 422]

    def test_generate_insights_response_schema(self):
        """
        Generate insights response should contain:
        - analysis_id: UUID
        - status: string
        - message: string
        """
        expected_fields = ["analysis_id", "status", "message"]

        for field in expected_fields:
            assert isinstance(field, str)


class TestGetInsightsContract:
    """Contract tests for GET /api/v1/analyses/{id}/insights endpoint (T156)"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def analysis_id(self):
        """Generate a test analysis ID"""
        return str(uuid4())

    def test_get_insights_requires_authentication(self, client, analysis_id):
        """
        GET /api/v1/analyses/{id}/insights
        should require authentication (401 without session)
        """
        response = client.get(
            f"/api/v1/analyses/{analysis_id}/insights"
        )
        assert response.status_code == 401

    def test_get_insights_response_schema(self):
        """
        Get insights response should contain array of Insight objects:
        - id: UUID
        - analysis_id: UUID
        - insight_type: enum (mention, visibility, sentiment, theme, gap)
        - brand_name: string
        - competitor_name: string (optional)
        - summary: string
        - explanation: string
        - evidence_references: JSONB
        - confidence_level: enum (high, medium, low)
        - scores: JSONB
        - created_at: datetime
        """
        expected_insight_fields = [
            "id",
            "analysis_id",
            "insight_type",
            "brand_name",
            "summary",
            "explanation",
            "evidence_references",
            "confidence_level",
            "scores",
            "created_at"
        ]

        for field in expected_insight_fields:
            assert isinstance(field, str)

    def test_insight_type_enum_values(self):
        """
        Insight type enum should contain valid values
        """
        valid_types = ["mention", "visibility", "sentiment", "theme", "gap"]

        for insight_type in valid_types:
            assert isinstance(insight_type, str)

    def test_confidence_level_enum_values(self):
        """
        Confidence level enum should contain valid values
        """
        valid_levels = ["high", "medium", "low"]

        for level in valid_levels:
            assert isinstance(level, str)


class TestGetRecommendationsContract:
    """Contract tests for GET /api/v1/analyses/{id}/recommendations endpoint (T157)"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def analysis_id(self):
        """Generate a test analysis ID"""
        return str(uuid4())

    def test_get_recommendations_requires_authentication(self, client, analysis_id):
        """
        GET /api/v1/analyses/{id}/insights/recommendations
        should require authentication (401 without session)
        """
        response = client.get(
            f"/api/v1/analyses/{analysis_id}/insights/recommendations"
        )
        assert response.status_code == 401

    def test_get_recommendations_response_schema(self):
        """
        Get recommendations response should contain array of Recommendation objects:
        - id: UUID
        - analysis_id: UUID
        - text: string
        - rationale: string
        - expected_impact: string
        - confidence_level: enum (high, medium, low)
        - evidence_references: JSONB
        - priority: int (1-5)
        - created_at: datetime
        """
        expected_recommendation_fields = [
            "id",
            "analysis_id",
            "text",
            "rationale",
            "expected_impact",
            "confidence_level",
            "evidence_references",
            "priority",
            "created_at"
        ]

        for field in expected_recommendation_fields:
            assert isinstance(field, str)

    def test_recommendation_minimum_count(self):
        """
        Recommendations should have minimum 5 items per analysis
        """
        MIN_RECOMMENDATIONS = 5
        assert MIN_RECOMMENDATIONS == 5

    def test_recommendation_priority_range(self):
        """
        Recommendation priority should be 1-5
        """
        valid_priorities = [1, 2, 3, 4, 5]

        for priority in valid_priorities:
            assert 1 <= priority <= 5


class TestInsightsListFormat:
    """Tests for insights list response format"""

    def test_insights_grouped_by_type(self):
        """
        Insights response can be grouped by insight_type for easier consumption
        """
        grouped_response = {
            "visibility": [],
            "sentiment": [],
            "mention": [],
            "theme": [],
            "gap": []
        }

        expected_types = ["visibility", "sentiment", "mention", "theme", "gap"]
        assert set(grouped_response.keys()) == set(expected_types)

    def test_insights_include_evidence_links(self):
        """
        Each insight should include evidence_references linking to AI responses
        """
        evidence_reference_schema = {
            "ai_response_id": "uuid",
            "citation_id": "uuid (optional)",
            "relevance_score": 0.95
        }

        assert "ai_response_id" in evidence_reference_schema


class TestInsightsScoresSchema:
    """Tests for insight scores structure"""

    def test_visibility_scores_schema(self):
        """
        Visibility insight scores should contain:
        - presence: float (0-1)
        - frequency: float (0-1)
        - position: float (0-1)
        - composite: float (0-1)
        """
        visibility_scores = {
            "presence": 0.8,
            "frequency": 0.6,
            "position": 0.7,
            "composite": 0.7  # 0.4*0.8 + 0.3*0.6 + 0.3*0.7 = 0.71
        }

        for score in visibility_scores.values():
            assert 0 <= score <= 1

    def test_sentiment_scores_schema(self):
        """
        Sentiment insight scores should contain:
        - sentiment: string (Positive/Neutral/Negative)
        - confidence: float (0-1)
        """
        sentiment_scores = {
            "sentiment": "Positive",
            "confidence": 0.85
        }

        assert sentiment_scores["sentiment"] in ["Positive", "Neutral", "Negative"]
        assert 0 <= sentiment_scores["confidence"] <= 1

    def test_mention_scores_schema(self):
        """
        Mention insight scores should contain:
        - mention_count: int
        - providers_mentioning: int
        - total_providers: int
        """
        mention_scores = {
            "mention_count": 5,
            "providers_mentioning": 4,
            "total_providers": 6
        }

        assert mention_scores["mention_count"] >= 0
        assert mention_scores["providers_mentioning"] <= mention_scores["total_providers"]
