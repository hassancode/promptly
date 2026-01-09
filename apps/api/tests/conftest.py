"""
Pytest configuration and fixtures for all tests
"""
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Add src directory to Python path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from main import app
from core.database import get_db, Base
from models.user import User


# Test database setup
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db() -> Session:
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db: Session):
    """Create a test client with database override"""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(db: Session):
    """Create a test user"""
    from core.security import hash_password

    password = "TestPass123!"[:72]  # Ensure password is within bcrypt limit
    user = User(
        email="test@example.com",
        password_hash=hash_password(password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def second_test_user(db: Session):
    """Create a second test user for access control tests"""
    from core.security import hash_password

    password = "TestPass123!"[:72]  # Ensure password is within bcrypt limit
    user = User(
        email="test2@example.com",
        password_hash=hash_password(password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def auth_headers(client: TestClient, test_user: User):
    """
    Authenticate test user and return headers.

    NOTE: The API uses cookie-based authentication (not Bearer tokens).
    This fixture logs in the user, which sets a session cookie in the client.
    The returned dict is empty since auth is via cookies, not headers.
    """
    # Login to set session cookie in the client
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "TestPass123!"}
    )
    assert response.status_code == 200

    # Return empty dict (auth is via cookies in the client, not headers)
    return {}


@pytest.fixture(scope="function")
def second_user_headers(client: TestClient, second_test_user: User):
    """
    Authenticate second test user and return headers.

    NOTE: This will overwrite the first user's session cookie since both users
    use the same client. Tests requiring multiple concurrent users will not work.
    """
    # Login to set session cookie in the client (overwrites previous user's cookie!)
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test2@example.com", "password": "TestPass123!"}
    )
    assert response.status_code == 200

    # Return empty dict (auth is via cookies in the client, not headers)
    return {}
