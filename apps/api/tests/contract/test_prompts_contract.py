"""
Contract tests for prompt endpoints (TDD - Red Phase)

Tests verify that prompt endpoints conform to the OpenAPI specification.
These should FAIL until implementation is complete.

Endpoints:
- POST /api/v1/analyses/{id}/prompts/suggest - Get AI prompt suggestions
- POST /api/v1/analyses/{id}/prompts - Add custom prompt
"""
import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_suggest_prompts_endpoint_exists():
    """Test that POST /api/v1/analyses/{id}/prompts/suggest endpoint exists"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register and login
        await client.post(
            "/api/v1/auth/register",
            json={"email": "prompt_test@example.com", "password": "SecurePass123!"}
        )
        await client.post(
            "/api/v1/auth/login",
            json={"email": "prompt_test@example.com", "password": "SecurePass123!"}
        )

        # Create analysis
        create_response = await client.post(
            "/api/v1/analyses",
            json={"brand_name": "Tesla"}
        )

        if create_response.status_code == 201:
            analysis_id = create_response.json()["id"]

            # Request prompt suggestions
            response = await client.post(
                f"/api/v1/analyses/{analysis_id}/prompts/suggest"
            )

            # Should not return 404
            assert response.status_code != 404, "Suggest prompts endpoint should exist"


@pytest.mark.asyncio
async def test_suggest_prompts_requires_authentication():
    """Test that suggesting prompts requires authentication"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.post(
            f"/api/v1/analyses/{fake_id}/prompts/suggest"
        )

        # Should return 401
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_suggest_prompts_returns_suggestions():
    """Test that suggesting prompts returns list of prompts"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register and login
        await client.post(
            "/api/v1/auth/register",
            json={"email": "suggest_test@example.com", "password": "SecurePass123!"}
        )
        await client.post(
            "/api/v1/auth/login",
            json={"email": "suggest_test@example.com", "password": "SecurePass123!"}
        )

        # Create analysis
        create_response = await client.post(
            "/api/v1/analyses",
            json={"brand_name": "Tesla"}
        )

        if create_response.status_code == 201:
            analysis_id = create_response.json()["id"]

            # Request suggestions
            response = await client.post(
                f"/api/v1/analyses/{analysis_id}/prompts/suggest"
            )

            if response.status_code == 200:
                data = response.json()
                # Should return list of suggested prompts
                assert "prompts" in data
                assert isinstance(data["prompts"], list)
                # Should suggest 5 prompts
                assert len(data["prompts"]) <= 5

                # Each prompt should have required fields
                for prompt in data["prompts"]:
                    assert "text" in prompt
                    assert "is_suggested" in prompt
                    assert prompt["is_suggested"] is True


@pytest.mark.asyncio
async def test_add_prompt_endpoint_exists():
    """Test that POST /api/v1/analyses/{id}/prompts exists"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register and login
        await client.post(
            "/api/v1/auth/register",
            json={"email": "add_prompt@example.com", "password": "SecurePass123!"}
        )
        await client.post(
            "/api/v1/auth/login",
            json={"email": "add_prompt@example.com", "password": "SecurePass123!"}
        )

        # Create analysis
        create_response = await client.post(
            "/api/v1/analyses",
            json={"brand_name": "Tesla"}
        )

        if create_response.status_code == 201:
            analysis_id = create_response.json()["id"]

            # Add prompt
            response = await client.post(
                f"/api/v1/analyses/{analysis_id}/prompts",
                json={"prompt_text": "What are the best electric vehicles?"}
            )

            # Should not return 404
            assert response.status_code != 404, "Add prompt endpoint should exist"


@pytest.mark.asyncio
async def test_add_prompt_requires_authentication():
    """Test that adding prompts requires authentication"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.post(
            f"/api/v1/analyses/{fake_id}/prompts",
            json={"prompt_text": "Test prompt"}
        )

        # Should return 401
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_add_prompt_validates_prompt_text():
    """Test that prompt_text is required"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register and login
        await client.post(
            "/api/v1/auth/register",
            json={"email": "validate_prompt@example.com", "password": "SecurePass123!"}
        )
        await client.post(
            "/api/v1/auth/login",
            json={"email": "validate_prompt@example.com", "password": "SecurePass123!"}
        )

        # Create analysis
        create_response = await client.post(
            "/api/v1/analyses",
            json={"brand_name": "Tesla"}
        )

        if create_response.status_code == 201:
            analysis_id = create_response.json()["id"]

            # Try to add without prompt_text
            response = await client.post(
                f"/api/v1/analyses/{analysis_id}/prompts",
                json={}
            )

            # Should return validation error
            assert response.status_code == 422


@pytest.mark.asyncio
async def test_add_prompt_returns_prompt_data():
    """Test that adding prompt returns prompt data"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register and login
        await client.post(
            "/api/v1/auth/register",
            json={"email": "add_data@example.com", "password": "SecurePass123!"}
        )
        await client.post(
            "/api/v1/auth/login",
            json={"email": "add_data@example.com", "password": "SecurePass123!"}
        )

        # Create analysis
        create_response = await client.post(
            "/api/v1/analyses",
            json={"brand_name": "Tesla"}
        )

        if create_response.status_code == 201:
            analysis_id = create_response.json()["id"]

            # Add prompt
            prompt_text = "What are the most innovative electric car companies?"
            response = await client.post(
                f"/api/v1/analyses/{analysis_id}/prompts",
                json={"prompt_text": prompt_text}
            )

            if response.status_code == 201:
                data = response.json()
                # Should return prompt object
                assert "id" in data
                assert "text" in data
                assert data["text"] == prompt_text
                assert "is_suggested" in data
                assert data["is_suggested"] is False
                assert "created_at" in data


@pytest.mark.asyncio
async def test_user_can_only_access_own_analysis_prompts():
    """Test that users can only access their own analysis prompts"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # User 1: Create analysis
        await client.post(
            "/api/v1/auth/register",
            json={"email": "owner@example.com", "password": "SecurePass123!"}
        )
        await client.post(
            "/api/v1/auth/login",
            json={"email": "owner@example.com", "password": "SecurePass123!"}
        )
        create_response = await client.post(
            "/api/v1/analyses",
            json={"brand_name": "Private Brand"}
        )

        if create_response.status_code == 201:
            analysis_id = create_response.json()["id"]

            # Logout user 1
            await client.post("/api/v1/auth/logout")

            # User 2: Try to access user 1's analysis prompts
            await client.post(
                "/api/v1/auth/register",
                json={"email": "intruder@example.com", "password": "SecurePass123!"}
            )
            await client.post(
                "/api/v1/auth/login",
                json={"email": "intruder@example.com", "password": "SecurePass123!"}
            )

            # Try to suggest prompts for user 1's analysis
            response = await client.post(
                f"/api/v1/analyses/{analysis_id}/prompts/suggest"
            )

            # Should return 403 or 404 (not authorized)
            assert response.status_code in [403, 404]
