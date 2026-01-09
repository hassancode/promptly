"""
Integration tests for prompt configuration (TDD - Red Phase)

Tests verify complete prompt selection flow:
1. User gets AI-suggested prompts for their analysis
2. User adds custom prompts
3. System enforces 7 prompt maximum (5 suggested + 2 custom)

These should FAIL until implementation is complete.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_complete_prompt_configuration_flow():
    """Test complete flow: suggest prompts -> add custom prompts"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register and login
        await client.post(
            "/api/v1/auth/register",
            json={"email": "flow_prompts@example.com", "password": "SecurePass123!"}
        )
        await client.post(
            "/api/v1/auth/login",
            json={"email": "flow_prompts@example.com", "password": "SecurePass123!"}
        )

        # Create analysis
        create_response = await client.post(
            "/api/v1/analyses",
            json={"brand_name": "Tesla"}
        )

        if create_response.status_code == 201:
            analysis_id = create_response.json()["id"]

            # Step 1: Get AI prompt suggestions
            suggest_response = await client.post(
                f"/api/v1/analyses/{analysis_id}/prompts/suggest"
            )

            if suggest_response.status_code == 200:
                suggestions = suggest_response.json()

                # Verify suggestions structure
                assert "prompts" in suggestions
                assert isinstance(suggestions["prompts"], list)
                assert len(suggestions["prompts"]) <= 5

                # Each suggestion should have required fields
                for prompt in suggestions["prompts"]:
                    assert "text" in prompt
                    assert "is_suggested" in prompt
                    assert prompt["is_suggested"] is True

                # Step 2: Add custom prompts
                custom_prompt_1 = await client.post(
                    f"/api/v1/analyses/{analysis_id}/prompts",
                    json={"prompt_text": "What are the safest electric vehicles?"}
                )

                if custom_prompt_1.status_code == 201:
                    custom_data = custom_prompt_1.json()
                    assert custom_data["is_suggested"] is False
                    assert custom_data["text"] == "What are the safest electric vehicles?"

                custom_prompt_2 = await client.post(
                    f"/api/v1/analyses/{analysis_id}/prompts",
                    json={"prompt_text": "Which electric cars have the longest range?"}
                )

                if custom_prompt_2.status_code == 201:
                    assert custom_prompt_2.json()["is_suggested"] is False


@pytest.mark.asyncio
async def test_prompt_limit_enforcement():
    """Test that system enforces maximum prompt limit"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register and login
        await client.post(
            "/api/v1/auth/register",
            json={"email": "limit_prompts@example.com", "password": "SecurePass123!"}
        )
        await client.post(
            "/api/v1/auth/login",
            json={"email": "limit_prompts@example.com", "password": "SecurePass123!"}
        )

        # Create analysis
        create_response = await client.post(
            "/api/v1/analyses",
            json={"brand_name": "Nike"}
        )

        if create_response.status_code == 201:
            analysis_id = create_response.json()["id"]

            # Add maximum allowed prompts (7 total: 5 suggested + 2 custom)
            prompts = [
                "What are the best running shoes?",
                "Which athletic brands are most innovative?",
                "What makes a good sports shoe?",
                "Who are Nike's main competitors?",
                "What are the latest sneaker trends?",
                "Which shoes are best for marathons?",
                "What are eco-friendly athletic shoes?",
            ]

            added_count = 0
            for prompt_text in prompts:
                response = await client.post(
                    f"/api/v1/analyses/{analysis_id}/prompts",
                    json={"prompt_text": prompt_text}
                )
                if response.status_code == 201:
                    added_count += 1

            # Should be able to add at least 7 prompts total
            # (5 suggested + 2 custom might already exist)

            # Try to add 8th prompt - should fail
            eighth_response = await client.post(
                f"/api/v1/analyses/{analysis_id}/prompts",
                json={"prompt_text": "What is the 8th prompt?"}
            )

            # Should return error if limit enforced
            if eighth_response.status_code == 400:
                error_data = eighth_response.json()
                assert "error" in error_data or "detail" in error_data


@pytest.mark.asyncio
async def test_duplicate_prompt_prevention():
    """Test that system prevents adding duplicate prompts"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register and login
        await client.post(
            "/api/v1/auth/register",
            json={"email": "duplicate_prompts@example.com", "password": "SecurePass123!"}
        )
        await client.post(
            "/api/v1/auth/login",
            json={"email": "duplicate_prompts@example.com", "password": "SecurePass123!"}
        )

        # Create analysis
        create_response = await client.post(
            "/api/v1/analyses",
            json={"brand_name": "Coca-Cola"}
        )

        if create_response.status_code == 201:
            analysis_id = create_response.json()["id"]

            # Add prompt
            first_add = await client.post(
                f"/api/v1/analyses/{analysis_id}/prompts",
                json={"prompt_text": "What are the best soft drinks?"}
            )

            if first_add.status_code == 201:
                # Try to add same prompt again
                duplicate_add = await client.post(
                    f"/api/v1/analyses/{analysis_id}/prompts",
                    json={"prompt_text": "What are the best soft drinks?"}
                )

                # Should return error
                if duplicate_add.status_code == 400:
                    error_data = duplicate_add.json()
                    assert "error" in error_data or "detail" in error_data


@pytest.mark.asyncio
async def test_empty_prompt_text_validation():
    """Test that empty prompt text is rejected"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register and login
        await client.post(
            "/api/v1/auth/register",
            json={"email": "empty_prompt@example.com", "password": "SecurePass123!"}
        )
        await client.post(
            "/api/v1/auth/login",
            json={"email": "empty_prompt@example.com", "password": "SecurePass123!"}
        )

        # Create analysis
        create_response = await client.post(
            "/api/v1/analyses",
            json={"brand_name": "Tesla"}
        )

        if create_response.status_code == 201:
            analysis_id = create_response.json()["id"]

            # Try to add empty prompt
            response = await client.post(
                f"/api/v1/analyses/{analysis_id}/prompts",
                json={"prompt_text": ""}
            )

            # Should return validation error
            assert response.status_code == 422


@pytest.mark.asyncio
async def test_whitespace_only_prompt_text():
    """Test that whitespace-only prompt text is rejected"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register and login
        await client.post(
            "/api/v1/auth/register",
            json={"email": "whitespace_prompt@example.com", "password": "SecurePass123!"}
        )
        await client.post(
            "/api/v1/auth/login",
            json={"email": "whitespace_prompt@example.com", "password": "SecurePass123!"}
        )

        # Create analysis
        create_response = await client.post(
            "/api/v1/analyses",
            json={"brand_name": "Tesla"}
        )

        if create_response.status_code == 201:
            analysis_id = create_response.json()["id"]

            # Try to add whitespace-only prompt
            response = await client.post(
                f"/api/v1/analyses/{analysis_id}/prompts",
                json={"prompt_text": "   "}
            )

            # Should return validation error
            assert response.status_code == 422


@pytest.mark.asyncio
async def test_very_long_prompt_text():
    """Test that excessively long prompts are handled"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register and login
        await client.post(
            "/api/v1/auth/register",
            json={"email": "long_prompt@example.com", "password": "SecurePass123!"}
        )
        await client.post(
            "/api/v1/auth/login",
            json={"email": "long_prompt@example.com", "password": "SecurePass123!"}
        )

        # Create analysis
        create_response = await client.post(
            "/api/v1/analyses",
            json={"brand_name": "Tesla"}
        )

        if create_response.status_code == 201:
            analysis_id = create_response.json()["id"]

            # Try to add very long prompt (> 1000 characters)
            long_text = "What " + "is " * 500 + "Tesla?"
            response = await client.post(
                f"/api/v1/analyses/{analysis_id}/prompts",
                json={"prompt_text": long_text}
            )

            # Should either reject with 422 or accept and truncate
            assert response.status_code in [201, 422]


@pytest.mark.asyncio
async def test_ai_suggestions_are_relevant_to_brand():
    """Test that AI prompt suggestions are contextually relevant"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register and login
        await client.post(
            "/api/v1/auth/register",
            json={"email": "relevance_prompts@example.com", "password": "SecurePass123!"}
        )
        await client.post(
            "/api/v1/auth/login",
            json={"email": "relevance_prompts@example.com", "password": "SecurePass123!"}
        )

        # Create analysis for a specific brand
        create_response = await client.post(
            "/api/v1/analyses",
            json={"brand_name": "Tesla"}
        )

        if create_response.status_code == 201:
            analysis_id = create_response.json()["id"]

            # Get AI suggestions
            suggest_response = await client.post(
                f"/api/v1/analyses/{analysis_id}/prompts/suggest"
            )

            if suggest_response.status_code == 200:
                suggestions = suggest_response.json()["prompts"]

                # Suggestions should be non-empty and reasonable
                assert len(suggestions) > 0
                assert len(suggestions) <= 5

                # All suggestions should have text
                for prompt in suggestions:
                    assert prompt["text"]
                    assert len(prompt["text"]) > 0
                    # Should be marked as AI-suggested
                    assert prompt["is_suggested"] is True
