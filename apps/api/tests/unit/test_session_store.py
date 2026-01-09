"""
Unit tests for Redis-backed session store

Tests cover:
- Session creation with TTL
- Session retrieval
- Session deletion
- TTL expiration
- Non-existent session handling
"""
import pytest
import json
from unittest.mock import AsyncMock, patch
from core.session_store import SessionStore
from core.config import settings


@pytest.mark.asyncio
async def test_create_session_with_ttl():
    """Test session creation stores data with correct TTL"""
    mock_redis = AsyncMock()
    session_id = "test_session_123"
    session_data = {"user_id": "user_456", "email": "test@example.com"}

    with patch("core.session_store.get_redis", return_value=mock_redis):
        store = SessionStore()
        await store.create(session_id, session_data)

    # Verify Redis setex was called with correct parameters
    mock_redis.setex.assert_called_once()
    call_args = mock_redis.setex.call_args[0]

    assert call_args[0] == f"session:{session_id}"
    assert call_args[1] == settings.SESSION_TTL_SECONDS
    assert json.loads(call_args[2]) == session_data


@pytest.mark.asyncio
async def test_read_existing_session():
    """Test reading an existing session returns correct data"""
    mock_redis = AsyncMock()
    session_id = "test_session_123"
    session_data = {"user_id": "user_456", "email": "test@example.com"}

    # Mock Redis returning session data
    mock_redis.get.return_value = json.dumps(session_data)

    with patch("core.session_store.get_redis", return_value=mock_redis):
        store = SessionStore()
        result = await store.read(session_id)

    mock_redis.get.assert_called_once_with(f"session:{session_id}")
    assert result == session_data


@pytest.mark.asyncio
async def test_read_nonexistent_session():
    """Test reading a non-existent session returns None"""
    mock_redis = AsyncMock()
    session_id = "nonexistent_session"

    # Mock Redis returning None (session doesn't exist)
    mock_redis.get.return_value = None

    with patch("core.session_store.get_redis", return_value=mock_redis):
        store = SessionStore()
        result = await store.read(session_id)

    mock_redis.get.assert_called_once_with(f"session:{session_id}")
    assert result is None


@pytest.mark.asyncio
async def test_delete_session():
    """Test session deletion removes key from Redis"""
    mock_redis = AsyncMock()
    session_id = "test_session_123"

    with patch("core.session_store.get_redis", return_value=mock_redis):
        store = SessionStore()
        await store.delete(session_id)

    mock_redis.delete.assert_called_once_with(f"session:{session_id}")


@pytest.mark.asyncio
async def test_update_session_ttl():
    """Test updating session refreshes TTL"""
    mock_redis = AsyncMock()
    session_id = "test_session_123"
    new_data = {"user_id": "user_456", "last_activity": "2024-01-01T00:00:00Z"}

    with patch("core.session_store.get_redis", return_value=mock_redis):
        store = SessionStore()
        await store.create(session_id, new_data)

    # Verify TTL is set on update
    mock_redis.setex.assert_called_once()
    call_args = mock_redis.setex.call_args[0]
    assert call_args[1] == settings.SESSION_TTL_SECONDS


@pytest.mark.asyncio
async def test_session_key_format():
    """Test session keys are prefixed correctly"""
    mock_redis = AsyncMock()
    session_id = "my_session"
    session_data = {"data": "value"}

    with patch("core.session_store.get_redis", return_value=mock_redis):
        store = SessionStore()
        await store.create(session_id, session_data)

    # Check key format includes prefix
    call_args = mock_redis.setex.call_args[0]
    assert call_args[0] == "session:my_session"


@pytest.mark.asyncio
async def test_concurrent_session_operations():
    """Test multiple session operations can be performed concurrently"""
    import asyncio
    mock_redis = AsyncMock()

    sessions = [
        ("session_1", {"user": "user_1"}),
        ("session_2", {"user": "user_2"}),
        ("session_3", {"user": "user_3"}),
    ]

    with patch("core.session_store.get_redis", return_value=mock_redis):
        store = SessionStore()

        # Create all sessions concurrently
        await asyncio.gather(*[
            store.create(sid, data) for sid, data in sessions
        ])

    # Verify all were created
    assert mock_redis.setex.call_count == 3


@pytest.mark.asyncio
async def test_session_data_serialization():
    """Test complex data structures are serialized correctly"""
    mock_redis = AsyncMock()
    session_id = "test_session"
    complex_data = {
        "user_id": "user_123",
        "preferences": {
            "theme": "dark",
            "notifications": True,
        },
        "permissions": ["read", "write"],
    }

    with patch("core.session_store.get_redis", return_value=mock_redis):
        store = SessionStore()
        await store.create(session_id, complex_data)

    # Verify data was serialized to JSON
    call_args = mock_redis.setex.call_args[0]
    serialized_data = call_args[2]
    assert json.loads(serialized_data) == complex_data
