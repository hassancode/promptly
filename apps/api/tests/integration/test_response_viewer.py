"""
Integration Tests for Response Viewer

Tests response retrieval with citation linking and filtering.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid import uuid4, UUID

from models.analysis import Analysis
from models.prompt import Prompt
from models.ai_response import AIResponse, ResponseStatus, CitationCoverage, ProviderType
from models.citation import Citation, SourceType, ValidityStatus


def test_response_viewer_full_workflow(client: TestClient, auth_headers: dict, db: Session, test_user):
    """
    Test full response viewer workflow:
    1. Create analysis
    2. Add prompts
    3. Add responses with citations
    4. Retrieve and verify all data
    """
    # 1. Create analysis (brand only)
    analysis_data = {
        "brand_name": "TestBrand",
    }

    create_response = client.post(
        "/api/v1/analyses",
        json=analysis_data,
        headers=auth_headers
    )
    assert create_response.status_code == 201
    analysis = create_response.json()
    analysis_id = analysis["id"]

    # 2. Add a prompt to the analysis
    prompt_response = client.post(
        f"/api/v1/analyses/{analysis_id}/prompts",
        json={"prompt_text": "What is TestBrand?"},
        headers=auth_headers
    )
    assert prompt_response.status_code == 201
    prompt_id = UUID(prompt_response.json()["id"])

    # 3. Manually add AI responses with citations (simulating provider queries)
    # Response 1: OpenAI with 3 citations (HIGH confidence)
    response_1 = AIResponse(
        id=uuid4(),
        prompt_id=prompt_id,
        provider=ProviderType.OPENAI,
        model_name="gpt-4-turbo",
        answer_text={"text": "TestBrand is a leading company in the industry with strong market presence."},
        citation_coverage=CitationCoverage.COMPLETE,
        status=ResponseStatus.SUCCESS,
    )
    db.add(response_1)
    db.flush()

    # Add citations for response 1
    for i in range(3):
        citation = Citation(
            id=uuid4(),
            ai_response_id=response_1.id,
            url=f"https://example{i}.com/testbrand",
            title=f"TestBrand Review {i+1}",
            snippet=f"TestBrand is mentioned positively in context {i+1}.",
            source_type=SourceType.NEWS,
            validity_status=ValidityStatus.VALID,
            position=i + 1,
        )
        db.add(citation)

    # Response 2: Claude with 1 citation (MEDIUM confidence)
    response_2 = AIResponse(
        id=uuid4(),
        prompt_id=prompt_id,
        provider=ProviderType.CLAUDE,
        model_name="claude-3-sonnet",
        answer_text={"text": "TestBrand offers competitive products."},
        citation_coverage=CitationCoverage.PARTIAL,
        status=ResponseStatus.SUCCESS,
    )
    db.add(response_2)
    db.flush()

    citation_2 = Citation(
        id=uuid4(),
        ai_response_id=response_2.id,
        url="https://techsite.com/testbrand-review",
        title="TestBrand Product Review",
        snippet="TestBrand products are competitive.",
        source_type=SourceType.WEB,
        validity_status=ValidityStatus.VALID,
        position=1,
    )
    db.add(citation_2)

    # Response 3: Gemini with no citations (LOW confidence)
    response_3 = AIResponse(
        id=uuid4(),
        prompt_id=prompt_id,
        provider=ProviderType.GEMINI,
        model_name="gemini-pro",
        answer_text={"text": "TestBrand is known in the market."},
        citation_coverage=CitationCoverage.NONE,
        status=ResponseStatus.SUCCESS,
    )
    db.add(response_3)

    db.commit()

    # 3. Retrieve responses via API
    responses_response = client.get(
        f"/api/v1/analyses/{analysis_id}/responses",
        headers=auth_headers
    )

    assert responses_response.status_code == 200
    responses = responses_response.json()

    # Verify we got all 3 responses
    assert len(responses) == 3

    # Verify OpenAI response with 3 citations
    openai_response = next(r for r in responses if r["provider"] == "openai")
    assert openai_response["model_name"] == "gpt-4-turbo"
    assert openai_response["citation_coverage"] == "complete"
    assert len(openai_response["citations"]) == 3

    # Verify citations are properly linked
    for i, citation in enumerate(openai_response["citations"]):
        assert "url" in citation
        assert "title" in citation
        assert "snippet" in citation
        assert citation["position"] == i + 1
        assert citation["source_type"] == "news"
        assert citation["validity_status"] == "valid"

    # Verify Claude response with 1 citation
    claude_response = next(r for r in responses if r["provider"] == "claude")
    assert claude_response["model_name"] == "claude-3-sonnet"
    assert claude_response["citation_coverage"] == "partial"
    assert len(claude_response["citations"]) == 1

    # Verify Gemini response with no citations
    gemini_response = next(r for r in responses if r["provider"] == "gemini")
    assert gemini_response["citation_coverage"] == "none"
    assert len(gemini_response["citations"]) == 0


def test_response_viewer_filtering_by_provider(client: TestClient, auth_headers: dict, db: Session, test_user):
    """
    Test filtering responses by provider
    """
    # Create analysis with multiple provider responses
    analysis_data = {
        "brand_name": "FilterTest",
    }

    create_response = client.post(
        "/api/v1/analyses",
        json=analysis_data,
        headers=auth_headers
    )
    analysis_id = create_response.json()["id"]

    # Add a prompt
    prompt_response = client.post(
        f"/api/v1/analyses/{analysis_id}/prompts",
        json={"prompt_text": "Test prompt"},
        headers=auth_headers
    )
    prompt_id = UUID(prompt_response.json()["id"])

    # Add responses from different providers
    for provider in [ProviderType.OPENAI, ProviderType.CLAUDE, ProviderType.GEMINI]:
        response = AIResponse(
            id=uuid4(),
            prompt_id=prompt_id,
            provider=provider,
            model_name=f"{provider.value}-model",
            answer_text={"text": f"Response from {provider.value}"},
            citation_coverage=CitationCoverage.NONE,
            status=ResponseStatus.SUCCESS,
        )
        db.add(response)

    db.commit()

    # Test filtering by OpenAI
    openai_responses = client.get(
        f"/api/v1/analyses/{analysis_id}/responses?provider=openai",
        headers=auth_headers
    )
    assert openai_responses.status_code == 200
    openai_data = openai_responses.json()
    assert len(openai_data) == 1
    assert openai_data[0]["provider"] == "openai"

    # Test filtering by Claude
    claude_responses = client.get(
        f"/api/v1/analyses/{analysis_id}/responses?provider=claude",
        headers=auth_headers
    )
    assert claude_responses.status_code == 200
    claude_data = claude_responses.json()
    assert len(claude_data) == 1
    assert claude_data[0]["provider"] == "claude"


def test_response_viewer_filtering_by_status(client: TestClient, auth_headers: dict, db: Session, test_user):
    """
    Test filtering responses by status
    """
    analysis_data = {
        "brand_name": "StatusTest",
    }

    create_response = client.post(
        "/api/v1/analyses",
        json=analysis_data,
        headers=auth_headers
    )
    analysis_id = create_response.json()["id"]

    # Add a prompt
    prompt_response = client.post(
        f"/api/v1/analyses/{analysis_id}/prompts",
        json={"prompt_text": "Test prompt"},
        headers=auth_headers
    )
    prompt_id = UUID(prompt_response.json()["id"])

    # Add responses with different statuses
    statuses = [
        ResponseStatus.SUCCESS,
        ResponseStatus.FAILED,
        ResponseStatus.TIMEOUT,
    ]

    for i, status in enumerate(statuses):
        response = AIResponse(
            id=uuid4(),
            prompt_id=prompt_id,
            provider=ProviderType.OPENAI,
            model_name="gpt-4",
            answer_text={"text": f"Response {i}"},
            citation_coverage=CitationCoverage.NONE,
            status=status,
        )
        db.add(response)

    db.commit()

    # Filter by success
    success_responses = client.get(
        f"/api/v1/analyses/{analysis_id}/responses?status=success",
        headers=auth_headers
    )
    assert success_responses.status_code == 200
    success_data = success_responses.json()
    assert len(success_data) == 1
    assert success_data[0]["status"] == "success"

    # Filter by failed
    failed_responses = client.get(
        f"/api/v1/analyses/{analysis_id}/responses?status=failed",
        headers=auth_headers
    )
    assert failed_responses.status_code == 200
    failed_data = failed_responses.json()
    assert len(failed_data) == 1
    assert failed_data[0]["status"] == "failed"


def test_citation_linking_preserves_order(client: TestClient, auth_headers: dict, db: Session, test_user):
    """
    Test that citations are returned in correct position order
    """
    analysis_data = {
        "brand_name": "OrderTest",
    }

    create_response = client.post(
        "/api/v1/analyses",
        json=analysis_data,
        headers=auth_headers
    )
    analysis_id = create_response.json()["id"]

    # Add a prompt
    prompt_response = client.post(
        f"/api/v1/analyses/{analysis_id}/prompts",
        json={"prompt_text": "Test prompt"},
        headers=auth_headers
    )
    prompt_id = UUID(prompt_response.json()["id"])

    # Add response with citations in specific order
    response = AIResponse(
        id=uuid4(),
        prompt_id=prompt_id,
        provider=ProviderType.OPENAI,
        model_name="gpt-4",
        answer_text={"text": "Response with ordered citations"},
        citation_coverage=CitationCoverage.COMPLETE,
        status=ResponseStatus.SUCCESS,
    )
    db.add(response)
    db.flush()

    # Add citations in reverse order to test sorting
    positions = [3, 1, 2]
    for pos in positions:
        citation = Citation(
            id=uuid4(),
            ai_response_id=response.id,
            url=f"https://example.com/citation-{pos}",
            title=f"Citation {pos}",
            position=pos,
            source_type=SourceType.OTHER,
            validity_status=ValidityStatus.UNKNOWN,
        )
        db.add(citation)

    db.commit()

    # Retrieve and verify order
    responses_response = client.get(
        f"/api/v1/analyses/{analysis_id}/responses",
        headers=auth_headers
    )

    responses_data = responses_response.json()
    citations = responses_data[0]["citations"]

    # Verify citations are in position order
    assert len(citations) == 3
    for i, citation in enumerate(citations):
        expected_position = i + 1
        assert citation["position"] == expected_position
        assert f"Citation {expected_position}" in citation["title"]


def test_response_viewer_empty_results(client: TestClient, auth_headers: dict):
    """
    Test response viewer with no responses
    """
    analysis_data = {
        "brand_name": "EmptyTest",
    }

    create_response = client.post(
        "/api/v1/analyses",
        json=analysis_data,
        headers=auth_headers
    )
    analysis_id = create_response.json()["id"]

    # Get responses (should be empty)
    responses_response = client.get(
        f"/api/v1/analyses/{analysis_id}/responses",
        headers=auth_headers
    )

    assert responses_response.status_code == 200
    assert responses_response.json() == []


def test_response_viewer_invalid_provider_filter(client: TestClient, auth_headers: dict):
    """
    Test response viewer with invalid provider filter
    """
    analysis_data = {
        "brand_name": "InvalidTest",
    }

    create_response = client.post(
        "/api/v1/analyses",
        json=analysis_data,
        headers=auth_headers
    )
    analysis_id = create_response.json()["id"]

    # Try invalid provider
    invalid_response = client.get(
        f"/api/v1/analyses/{analysis_id}/responses?provider=invalid_provider",
        headers=auth_headers
    )

    assert invalid_response.status_code == 400
    assert "Invalid provider" in invalid_response.json()["detail"]


@pytest.mark.skip(reason="Requires separate clients for multi-user tests - fixture limitation")
def test_response_viewer_access_control(client: TestClient, auth_headers: dict, second_user_headers: dict, db: Session, test_user):
    """
    Test that users can only view their own responses

    Note: This test is skipped because the current fixture setup shares a single
    client between users. The `second_user_headers` fixture logs in user 2,
    overwriting user 1's session cookie. For proper multi-user access control
    tests, we would need separate TestClient instances.
    """
    # User 1 creates analysis
    analysis_data = {
        "brand_name": "PrivateAnalysis",
    }

    create_response = client.post(
        "/api/v1/analyses",
        json=analysis_data,
        headers=auth_headers
    )
    analysis_id = create_response.json()["id"]

    # User 2 tries to access User 1's responses
    responses_response = client.get(
        f"/api/v1/analyses/{analysis_id}/responses",
        headers=second_user_headers
    )

    # Should return 404 (not 403 for security)
    assert responses_response.status_code == 404
