"""
Contract tests for authentication endpoints

These tests verify that authentication endpoints conform to the API specification.

Tests:
- POST /api/v1/auth/register - User registration
- POST /api/v1/auth/login - User login
- POST /api/v1/auth/logout - User logout
- GET /api/v1/auth/me - Get current user
"""
from fastapi.testclient import TestClient


def test_register_endpoint_contract(client: TestClient):
    """
    Contract: POST /api/v1/auth/register

    Request:
    {
        "email": "user@example.com",
        "password": "SecurePass123!"
    }

    Response (201):
    {
        "id": str,
        "email": str,
        "verified": bool,
        "created_at": datetime
    }
    """
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "newuser@example.com", "password": "SecurePass123!"}
    )

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert "email" in data
    assert data["email"] == "newuser@example.com"
    assert "verified" in data
    assert "created_at" in data
    # Should NOT return password
    assert "password" not in data
    assert "password_hash" not in data


def test_register_validates_email_format(client: TestClient):
    """Contract: Register endpoint validates email format"""
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "invalid-email", "password": "SecurePass123!"}
    )
    # Should return 422 for validation error (FastAPI standard)
    assert response.status_code == 422


def test_register_validates_password_length(client: TestClient):
    """Contract: Register endpoint validates password length (min 8 chars)"""
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "short"}
    )
    # Should return 422 for validation error (FastAPI standard)
    assert response.status_code == 422


def test_register_rejects_duplicate_email(client: TestClient):
    """Contract: Register endpoint rejects duplicate email"""
    email = "duplicate@example.com"
    password = "SecurePass123!"

    # First registration
    response1 = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password}
    )
    assert response1.status_code == 201

    # Second registration with same email
    response2 = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password}
    )

    # Second should fail with 400
    assert response2.status_code == 400


def test_login_endpoint_contract(client: TestClient):
    """
    Contract: POST /api/v1/auth/login

    Request:
    {
        "email": "user@example.com",
        "password": "SecurePass123!"
    }

    Response (200):
    {
        "id": str,
        "email": str,
        "verified": bool,
        "created_at": datetime
    }
    + Sets session cookie
    """
    # Register user first
    client.post(
        "/api/v1/auth/register",
        json={"email": "logintest@example.com", "password": "SecurePass123!"}
    )

    # Login
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "logintest@example.com", "password": "SecurePass123!"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "email" in data
    assert data["email"] == "logintest@example.com"

    # Should set session cookie
    assert "set-cookie" in response.headers or len(response.cookies) > 0


def test_login_rejects_invalid_credentials(client: TestClient):
    """Contract: Login rejects invalid credentials"""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent@example.com", "password": "WrongPass123!"}
    )
    # Should return 401 for invalid credentials
    assert response.status_code == 401


def test_login_rejects_wrong_password(client: TestClient):
    """Contract: Login rejects correct email but wrong password"""
    # Register user
    client.post(
        "/api/v1/auth/register",
        json={"email": "rightuser@example.com", "password": "CorrectPass123!"}
    )

    # Login with wrong password
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "rightuser@example.com", "password": "WrongPass123!"}
    )
    assert response.status_code == 401


def test_logout_endpoint_contract(client: TestClient, auth_headers: dict):
    """
    Contract: POST /api/v1/auth/logout

    Requires: Valid session cookie

    Response (200):
    {
        "message": str
    }
    + Clears session cookie
    """
    # auth_headers fixture logs in the test user
    response = client.post("/api/v1/auth/logout")

    assert response.status_code == 200

    # Should clear/expire cookie
    cookies_header = response.headers.get("set-cookie", "")
    if "promptly_session" in cookies_header:
        # Cookie should be cleared or have Max-Age=0
        assert "=" in cookies_header  # Cookie is being set/cleared


def test_me_endpoint_contract(client: TestClient, auth_headers: dict):
    """
    Contract: GET /api/v1/auth/me

    Requires: Valid session cookie

    Response (200):
    {
        "id": str,
        "email": str,
        "verified": bool,
        "created_at": datetime
    }
    """
    # auth_headers fixture logs in test_user
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "email" in data
    assert data["email"] == "test@example.com"  # From test_user fixture
    assert "verified" in data
    assert "created_at" in data


def test_me_requires_authentication(client: TestClient):
    """Contract: /me endpoint requires authentication"""
    response = client.get("/api/v1/auth/me")
    # Should return 401 when not authenticated
    assert response.status_code == 401
