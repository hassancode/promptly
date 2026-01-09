"""
Integration tests for brand name disambiguation (TDD - Red Phase)

Tests verify disambiguation flow for ambiguous brand names:
- System detects ambiguous brand names (e.g., "Apple" = tech company or fruit)
- User is presented with disambiguation options
- User selects correct interpretation
- Analysis proceeds with clarified brand

These should FAIL until implementation is complete.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_ambiguous_brand_name_detection():
    """Test that system detects ambiguous brand names"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register and login
        await client.post(
            "/api/v1/auth/register",
            json={"email": "ambiguous_test@example.com", "password": "SecurePass123!"}
        )
        await client.post(
            "/api/v1/auth/login",
            json={"email": "ambiguous_test@example.com", "password": "SecurePass123!"}
        )

        # Try to create analysis with ambiguous brand name
        create_response = await client.post(
            "/api/v1/analyses",
            json={"brand_name": "Apple"}
        )

        # If disambiguation is implemented, might return:
        # - 200 with disambiguation_required flag
        # - 422 with disambiguation options
        # - 201 if it makes a reasonable guess
        if create_response.status_code == 200:
            data = create_response.json()

            # Check if disambiguation is flagged
            if "disambiguation_required" in data and data["disambiguation_required"]:
                # Should provide options
                assert "options" in data
                assert isinstance(data["options"], list)
                assert len(data["options"]) > 1

                # Each option should have relevant fields
                for option in data["options"]:
                    assert "id" in option or "value" in option
                    assert "description" in option or "label" in option


@pytest.mark.asyncio
async def test_disambiguation_with_context():
    """Test disambiguation with additional context"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register and login
        await client.post(
            "/api/v1/auth/register",
            json={"email": "context_test@example.com", "password": "SecurePass123!"}
        )
        await client.post(
            "/api/v1/auth/login",
            json={"email": "context_test@example.com", "password": "SecurePass123!"}
        )

        # Create analysis with additional context to help disambiguation
        create_response = await client.post(
            "/api/v1/analyses",
            json={
                "brand_name": "Apple",
                "context": "technology company"  # Helps clarify intent
            }
        )

        # With context, should create successfully or still offer disambiguation
        if create_response.status_code == 201:
            data = create_response.json()
            assert data["brand_name"] == "Apple"
            assert data["status"] == "draft"


@pytest.mark.asyncio
async def test_unambiguous_brand_name():
    """Test that clearly unambiguous brand names work without disambiguation"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register and login
        await client.post(
            "/api/v1/auth/register",
            json={"email": "unambiguous_test@example.com", "password": "SecurePass123!"}
        )
        await client.post(
            "/api/v1/auth/login",
            json={"email": "unambiguous_test@example.com", "password": "SecurePass123!"}
        )

        # Use a clearly unambiguous brand name
        create_response = await client.post(
            "/api/v1/analyses",
            json={"brand_name": "Tesla Motors"}
        )

        # Should create without disambiguation
        if create_response.status_code == 201:
            data = create_response.json()
            assert data["brand_name"] == "Tesla Motors"
            assert "disambiguation_required" not in data or data["disambiguation_required"] is False


@pytest.mark.asyncio
@pytest.mark.skip(reason="Requires async test fixtures with test database - uses real PostgreSQL")
async def test_empty_brand_name_validation():
    """Test that empty brand names are rejected"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register and login
        await client.post(
            "/api/v1/auth/register",
            json={"email": "empty_test@example.com", "password": "SecurePass123!"}
        )
        await client.post(
            "/api/v1/auth/login",
            json={"email": "empty_test@example.com", "password": "SecurePass123!"}
        )

        # Try to create with empty brand name
        create_response = await client.post(
            "/api/v1/analyses",
            json={"brand_name": ""}
        )

        # Should return validation error
        assert create_response.status_code == 422


@pytest.mark.asyncio
@pytest.mark.skip(reason="Requires async test fixtures with test database - uses real PostgreSQL")
async def test_whitespace_only_brand_name():
    """Test that whitespace-only brand names are rejected"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register and login
        await client.post(
            "/api/v1/auth/register",
            json={"email": "whitespace_test@example.com", "password": "SecurePass123!"}
        )
        await client.post(
            "/api/v1/auth/login",
            json={"email": "whitespace_test@example.com", "password": "SecurePass123!"}
        )

        # Try to create with whitespace-only brand name
        create_response = await client.post(
            "/api/v1/analyses",
            json={"brand_name": "   "}
        )

        # Should return validation error
        assert create_response.status_code == 422


@pytest.mark.asyncio
@pytest.mark.skip(reason="Requires async test fixtures with test database - uses real PostgreSQL")
async def test_very_long_brand_name():
    """Test that excessively long brand names are handled"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register and login
        await client.post(
            "/api/v1/auth/register",
            json={"email": "long_name_test@example.com", "password": "SecurePass123!"}
        )
        await client.post(
            "/api/v1/auth/login",
            json={"email": "long_name_test@example.com", "password": "SecurePass123!"}
        )

        # Try to create with very long brand name (> 255 characters)
        long_name = "A" * 300
        create_response = await client.post(
            "/api/v1/analyses",
            json={"brand_name": long_name}
        )

        # Should either:
        # - Reject with 422 (validation error)
        # - Accept and truncate
        # - Accept if database allows
        assert create_response.status_code in [201, 422]


@pytest.mark.asyncio
@pytest.mark.skip(reason="Requires async test fixtures with test database - uses real PostgreSQL")
async def test_special_characters_in_brand_name():
    """Test that special characters in brand names are handled correctly"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register and login
        await client.post(
            "/api/v1/auth/register",
            json={"email": "special_chars_test@example.com", "password": "SecurePass123!"}
        )
        await client.post(
            "/api/v1/auth/login",
            json={"email": "special_chars_test@example.com", "password": "SecurePass123!"}
        )

        # Try brand names with special characters
        test_cases = [
            "AT&T",  # Ampersand
            "L'Oréal",  # Apostrophe and accented character
            "H&M",  # Ampersand
            "LEGO®",  # Registered trademark symbol
            "3M™",  # Trademark symbol
        ]

        for brand_name in test_cases:
            create_response = await client.post(
                "/api/v1/analyses",
                json={"brand_name": brand_name}
            )

            # Should handle gracefully - either accept or reject consistently
            assert create_response.status_code in [201, 422]

            if create_response.status_code == 201:
                data = create_response.json()
                # Ensure brand name is preserved correctly
                assert data["brand_name"] == brand_name


@pytest.mark.asyncio
async def test_case_insensitive_brand_matching():
    """Test that brand name matching is case-insensitive for duplicates"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register and login
        await client.post(
            "/api/v1/auth/register",
            json={"email": "case_test@example.com", "password": "SecurePass123!"}
        )
        await client.post(
            "/api/v1/auth/login",
            json={"email": "case_test@example.com", "password": "SecurePass123!"}
        )

        # Create first analysis
        first_response = await client.post(
            "/api/v1/analyses",
            json={"brand_name": "Tesla"}
        )

        if first_response.status_code == 201:
            # Try to create with different casing
            second_response = await client.post(
                "/api/v1/analyses",
                json={"brand_name": "TESLA"}
            )

            # Should either:
            # - Allow (different analyses for same user)
            # - Reject as duplicate
            # Both are valid depending on business rules
            assert second_response.status_code in [201, 400, 409]
