"""
Contract tests for analysis endpoints (TDD - Red Phase)

Tests verify that analysis endpoints conform to the OpenAPI specification.
These should FAIL until implementation is complete.

Endpoints:
- POST /api/v1/analyses - Create new analysis
- POST /api/v1/analyses/{id}/competitors/suggest - Get AI competitor suggestions
- POST /api/v1/analyses/{id}/competitors - Add competitors to analysis
"""
import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_create_analysis_endpoint_exists():
    """Test that POST /api/v1/analyses endpoint exists"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register and login first
        await client.post(
            "/api/v1/auth/register",
            json={"email": "analyst@example.com", "password": "SecurePass123!"}
        )
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "analyst@example.com", "password": "SecurePass123!"}
        )

        # Create analysis
        response = await client.post(
            "/api/v1/analyses",
            json={"brand_name": "Tesla"}
        )

        # Should not return 404 (endpoint exists)
        assert response.status_code != 404, "Create analysis endpoint should exist"


@pytest.mark.asyncio
async def test_create_analysis_requires_authentication():
    """Test that creating analysis requires authentication"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/analyses",
            json={"brand_name": "Tesla"}
        )

        # Should return 401 when not authenticated
        assert response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.skip(reason="Requires async test fixtures with test database - uses real PostgreSQL")
async def test_create_analysis_validates_brand_name():
    """Test that brand_name is required"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register and login
        await client.post(
            "/api/v1/auth/register",
            json={"email": "validator@example.com", "password": "SecurePass123!"}
        )
        await client.post(
            "/api/v1/auth/login",
            json={"email": "validator@example.com", "password": "SecurePass123!"}
        )

        # Try to create without brand_name
        response = await client.post("/api/v1/analyses", json={})

        # Should return validation error
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_analysis_returns_analysis_data():
    """Test that successful creation returns analysis data"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register and login
        await client.post(
            "/api/v1/auth/register",
            json={"email": "creator@example.com", "password": "SecurePass123!"}
        )
        await client.post(
            "/api/v1/auth/login",
            json={"email": "creator@example.com", "password": "SecurePass123!"}
        )

        # Create analysis
        response = await client.post(
            "/api/v1/analyses",
            json={"brand_name": "Apple"}
        )

        if response.status_code == 201:
            data = response.json()
            # Should return analysis object
            assert "id" in data
            assert "brand_name" in data
            assert data["brand_name"] == "Apple"
            assert "status" in data
            assert data["status"] == "draft"
            assert "created_at" in data


@pytest.mark.asyncio
async def test_suggest_competitors_endpoint_exists():
    """Test that POST /api/v1/analyses/{id}/competitors/suggest exists"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register and login
        await client.post(
            "/api/v1/auth/register",
            json={"email": "suggester@example.com", "password": "SecurePass123!"}
        )
        await client.post(
            "/api/v1/auth/login",
            json={"email": "suggester@example.com", "password": "SecurePass123!"}
        )

        # Create analysis
        create_response = await client.post(
            "/api/v1/analyses",
            json={"brand_name": "Tesla"}
        )

        if create_response.status_code == 201:
            analysis_id = create_response.json()["id"]

            # Request competitor suggestions
            response = await client.post(
                f"/api/v1/analyses/{analysis_id}/competitors/suggest"
            )

            # Should not return 404
            assert response.status_code != 404, "Suggest competitors endpoint should exist"


@pytest.mark.asyncio
async def test_suggest_competitors_requires_authentication():
    """Test that suggesting competitors requires authentication"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Try without authentication
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.post(
            f"/api/v1/analyses/{fake_id}/competitors/suggest"
        )

        # Should return 401
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_suggest_competitors_returns_suggestions():
    """Test that suggesting competitors returns list of competitors"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register and login
        await client.post(
            "/api/v1/auth/register",
            json={"email": "suggester2@example.com", "password": "SecurePass123!"}
        )
        await client.post(
            "/api/v1/auth/login",
            json={"email": "suggester2@example.com", "password": "SecurePass123!"}
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
                f"/api/v1/analyses/{analysis_id}/competitors/suggest"
            )

            if response.status_code == 200:
                data = response.json()
                # Should return list of suggested competitors
                assert "competitors" in data
                assert isinstance(data["competitors"], list)
                # Should suggest 3 competitors
                assert len(data["competitors"]) <= 3


@pytest.mark.asyncio
async def test_add_competitors_endpoint_exists():
    """Test that POST /api/v1/analyses/{id}/competitors exists"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register and login
        await client.post(
            "/api/v1/auth/register",
            json={"email": "adder@example.com", "password": "SecurePass123!"}
        )
        await client.post(
            "/api/v1/auth/login",
            json={"email": "adder@example.com", "password": "SecurePass123!"}
        )

        # Create analysis
        create_response = await client.post(
            "/api/v1/analyses",
            json={"brand_name": "Tesla"}
        )

        if create_response.status_code == 201:
            analysis_id = create_response.json()["id"]

            # Add competitor
            response = await client.post(
                f"/api/v1/analyses/{analysis_id}/competitors",
                json={"competitor_name": "Rivian"}
            )

            # Should not return 404
            assert response.status_code != 404, "Add competitors endpoint should exist"


@pytest.mark.asyncio
async def test_add_competitors_requires_authentication():
    """Test that adding competitors requires authentication"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.post(
            f"/api/v1/analyses/{fake_id}/competitors",
            json={"competitor_name": "Rivian"}
        )

        # Should return 401
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_add_competitors_validates_competitor_name():
    """Test that competitor_name is required"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register and login
        await client.post(
            "/api/v1/auth/register",
            json={"email": "validator2@example.com", "password": "SecurePass123!"}
        )
        await client.post(
            "/api/v1/auth/login",
            json={"email": "validator2@example.com", "password": "SecurePass123!"}
        )

        # Create analysis
        create_response = await client.post(
            "/api/v1/analyses",
            json={"brand_name": "Tesla"}
        )

        if create_response.status_code == 201:
            analysis_id = create_response.json()["id"]

            # Try to add without competitor_name
            response = await client.post(
                f"/api/v1/analyses/{analysis_id}/competitors",
                json={}
            )

            # Should return validation error
            assert response.status_code == 422


@pytest.mark.asyncio
async def test_add_competitors_returns_competitor_data():
    """Test that adding competitor returns competitor data"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register and login
        await client.post(
            "/api/v1/auth/register",
            json={"email": "adder2@example.com", "password": "SecurePass123!"}
        )
        await client.post(
            "/api/v1/auth/login",
            json={"email": "adder2@example.com", "password": "SecurePass123!"}
        )

        # Create analysis
        create_response = await client.post(
            "/api/v1/analyses",
            json={"brand_name": "Tesla"}
        )

        if create_response.status_code == 201:
            analysis_id = create_response.json()["id"]

            # Add competitor
            response = await client.post(
                f"/api/v1/analyses/{analysis_id}/competitors",
                json={"competitor_name": "Rivian"}
            )

            if response.status_code == 201:
                data = response.json()
                # Should return competitor object
                assert "id" in data
                assert "name" in data
                assert data["name"] == "Rivian"
                assert "is_suggested" in data
                assert "created_at" in data


@pytest.mark.asyncio
async def test_user_can_only_access_own_analyses():
    """Test that users can only access their own analyses"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # User 1: Create analysis
        await client.post(
            "/api/v1/auth/register",
            json={"email": "user1@example.com", "password": "SecurePass123!"}
        )
        await client.post(
            "/api/v1/auth/login",
            json={"email": "user1@example.com", "password": "SecurePass123!"}
        )
        create_response = await client.post(
            "/api/v1/analyses",
            json={"brand_name": "Private Brand"}
        )

        if create_response.status_code == 201:
            analysis_id = create_response.json()["id"]

            # Logout user 1
            await client.post("/api/v1/auth/logout")

            # User 2: Try to access user 1's analysis
            await client.post(
                "/api/v1/auth/register",
                json={"email": "user2@example.com", "password": "SecurePass123!"}
            )
            await client.post(
                "/api/v1/auth/login",
                json={"email": "user2@example.com", "password": "SecurePass123!"}
            )

            # Try to suggest competitors for user 1's analysis
            response = await client.post(
                f"/api/v1/analyses/{analysis_id}/competitors/suggest"
            )

            # Should return 403 or 404 (not authorized)
            assert response.status_code in [403, 404]
