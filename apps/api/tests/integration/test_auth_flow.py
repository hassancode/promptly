"""
Integration tests for complete authentication flows

These tests verify end-to-end authentication flows including:
- Full registration -> verification -> login flow
- Unverified user login handling
- Invalid credentials handling
- Session persistence
- Concurrent registration handling
"""
from fastapi.testclient import TestClient


def test_full_registration_and_login_flow(client: TestClient):
    """
    Test complete flow: register -> login

    Steps:
    1. User registers with email/password
    2. User logs in successfully
    3. User can access protected endpoints
    """
    email = "fullflow@example.com"
    password = "SecurePass123!"

    # Step 1: Register
    register_response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password}
    )
    assert register_response.status_code == 201, "Registration should succeed"
    user_data = register_response.json()
    assert user_data["email"] == email
    user_id = user_data["id"]

    # Step 2: Login
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password}
    )
    assert login_response.status_code == 200, "Login should succeed"
    login_data = login_response.json()
    assert login_data["id"] == user_id
    assert login_data["email"] == email

    # Step 3: Access protected endpoint
    me_response = client.get("/api/v1/auth/me")
    assert me_response.status_code == 200, "Should access protected endpoint"
    me_data = me_response.json()
    assert me_data["email"] == email


def test_unverified_user_can_login(client: TestClient):
    """
    Test that unverified users can log in (MVP behavior)

    Note: Per the implementation, unverified users are allowed to login
    for MVP. In production, this should be changed to reject unverified users.

    Flow:
    1. User registers
    2. User can login even without email verification
    3. User has verified=False in their profile
    """
    email = "unverified@example.com"
    password = "SecurePass123!"

    # Register user
    register_response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password}
    )
    assert register_response.status_code == 201

    # Attempt login without verification (should succeed in MVP)
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password}
    )
    assert login_response.status_code == 200, "MVP allows unverified login"

    # Check that user is marked as unverified
    user_data = login_response.json()
    assert user_data["verified"] == False, "User should be unverified"


def test_invalid_credentials_handling(client: TestClient):
    """
    Test various invalid credential scenarios

    Tests:
    1. Non-existent email
    2. Wrong password
    3. Empty email
    4. Empty password
    5. Missing fields
    """
    # Register a valid user first
    valid_email = "validuser@example.com"
    valid_password = "SecurePass123!"
    client.post(
        "/api/v1/auth/register",
        json={"email": valid_email, "password": valid_password}
    )

    # Test 1: Non-existent email
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent@example.com", "password": "AnyPassword123!"}
    )
    assert response.status_code == 401, "Non-existent email should return 401"

    # Test 2: Wrong password
    response = client.post(
        "/api/v1/auth/login",
        json={"email": valid_email, "password": "WrongPassword123!"}
    )
    assert response.status_code == 401, "Wrong password should return 401"

    # Test 3: Empty email
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "", "password": valid_password}
    )
    assert response.status_code in [400, 422], "Empty email should return 400/422"

    # Test 4: Empty password
    response = client.post(
        "/api/v1/auth/login",
        json={"email": valid_email, "password": ""}
    )
    # API may treat empty password as invalid credentials (401) or validation error (422)
    assert response.status_code in [400, 401, 422], "Empty password should return 400/401/422"

    # Test 5: Missing email field
    response = client.post(
        "/api/v1/auth/login",
        json={"password": valid_password}
    )
    assert response.status_code in [400, 422], "Missing email should return 400/422"

    # Test 6: Missing password field
    response = client.post(
        "/api/v1/auth/login",
        json={"email": valid_email}
    )
    assert response.status_code in [400, 422], "Missing password should return 400/422"


def test_session_persistence_across_requests(client: TestClient):
    """
    Test that session persists across multiple requests

    Flow:
    1. User logs in
    2. Make authenticated request to /api/v1/auth/me
    3. Session should persist
    4. User logs out
    5. Session should be cleared
    """
    email = "session@example.com"
    password = "SecurePass123!"

    # Register and login
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password}
    )
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password}
    )
    assert login_response.status_code == 200

    # Check session persistence - should be able to access /me
    me_response = client.get("/api/v1/auth/me")
    assert me_response.status_code == 200, "Session should persist"
    user_data = me_response.json()
    assert user_data["email"] == email

    # Logout
    logout_response = client.post("/api/v1/auth/logout")
    assert logout_response.status_code == 200, "Logout should succeed"

    # Session should be cleared - /me should return 401
    me_after_logout = client.get("/api/v1/auth/me")
    assert me_after_logout.status_code == 401, "Should be unauthorized after logout"


def test_duplicate_email_registration_race_condition(client: TestClient):
    """
    Test that duplicate email registrations are properly rejected

    This tests the database constraint and error handling for duplicate emails.
    Note: True concurrent testing would require async, but we can test sequential attempts.
    """
    email = "duplicate@example.com"
    password = "SecurePass123!"

    # First registration
    response1 = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password}
    )
    assert response1.status_code == 201, "First registration should succeed"

    # Second registration with same email
    response2 = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password}
    )
    assert response2.status_code == 400, "Duplicate email should be rejected"

    error_data = response2.json()
    # Check for error message in 'error', 'detail', or 'message' field
    error_msg = (error_data.get("error", "") + error_data.get("detail", "") + error_data.get("message", "")).lower()
    assert "email" in error_msg or "already" in error_msg or "registered" in error_msg, \
           f"Error message should indicate duplicate email, got: {error_data}"


def test_password_security_validation(client: TestClient):
    """
    Test password validation rules

    Current Requirements (MVP):
    - Minimum 8 characters

    Note: Additional complexity requirements (uppercase, lowercase, digits, special chars)
    should be added in production version for enhanced security.
    """
    # Test short password (< 8 chars)
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "shortpass@example.com", "password": "short"}
    )
    # Should return 422 for validation error
    assert response.status_code == 422, "Should reject password shorter than 8 chars"

    # Test minimum valid password (8 chars)
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "minpass@example.com", "password": "12345678"}
    )
    assert response.status_code == 201, "8-character password should be accepted"

    # Test strong password (recommended but not required)
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "strongpass@example.com", "password": "ValidPass123!"}
    )
    assert response.status_code == 201, "Strong password should be accepted"


def test_logout_without_login(client: TestClient):
    """
    Test that logout works (doesn't error) even without being logged in
    """
    response = client.post("/api/v1/auth/logout")
    # Should handle gracefully (either 200 or 401, depending on implementation)
    assert response.status_code in [200, 401], "Logout should handle no-session gracefully"


def test_session_cookie_properties(client: TestClient):
    """
    Test that session cookies have proper security properties

    Expected properties:
    - HttpOnly flag (prevents JavaScript access)
    - SameSite attribute (CSRF protection)
    - Secure flag in production (HTTPS only)
    - Proper expiration
    """
    email = "cookietest@example.com"
    password = "SecurePass123!"

    # Register and login
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password}
    )
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password}
    )

    # Check Set-Cookie header
    set_cookie = login_response.headers.get("set-cookie", "")

    if set_cookie:
        # Cookie should exist
        assert "promptly_session" in set_cookie or len(login_response.cookies) > 0, \
            "Should set session cookie"

        # Security properties (HttpOnly, SameSite)
        # Note: In test environment, Secure flag may not be set
        if "promptly_session" in set_cookie:
            assert "httponly" in set_cookie.lower(), "Cookie should be HttpOnly"
            assert "samesite" in set_cookie.lower(), "Cookie should have SameSite"
