"""Tests for cache functionality."""

import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from llm_cache.core.cache import LLMCache
from llm_cache.core.hashing import hash_request
from llm_cache.core.schema import CacheEntry


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as f:
        db_path = f.name
    
    yield db_path
    
    # Cleanup
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def cache(temp_db):
    """Create a cache instance with temporary database."""
    return LLMCache(database_path=temp_db)


def test_cache_initialization(cache):
    """Test cache initialization."""
    assert cache.backend == "sqlite"
    assert cache.enable_compression is True
    assert cache.default_ttl_days == 30


def test_hash_request():
    """Test request hashing."""
    request_data = {"messages": [{"role": "user", "content": "Hello"}]}
    
    key1 = hash_request("openai", "gpt-4", "/v1/chat/completions", request_data)
    key2 = hash_request("openai", "gpt-4", "/v1/chat/completions", request_data)
    
    # Same request should produce same hash
    assert key1 == key2
    
    # Different request should produce different hash
    key3 = hash_request("openai", "gpt-3.5-turbo", "/v1/chat/completions", request_data)
    assert key1 != key3


def test_get_or_set(cache):
    """Test get_or_set functionality."""
    request_data = {"messages": [{"role": "user", "content": "Hello"}]}
    
    def fetch_func():
        return {"choices": [{"message": {"content": "Hello there!"}}]}
    
    # First call should fetch and cache
    response1 = cache.get_or_set(
        key="test_key",
        fetch_func=fetch_func,
        provider="openai",
        model="gpt-4",
        endpoint="/v1/chat/completions",
        request_data=request_data,
    )
    
    assert response1 == {"choices": [{"message": {"content": "Hello there!"}}]}
    
    # Second call should return cached response
    response2 = cache.get_or_set(
        key="test_key",
        fetch_func=lambda: {"choices": [{"message": {"content": "Different response"}}]},
        provider="openai",
        model="gpt-4",
        endpoint="/v1/chat/completions",
        request_data=request_data,
    )
    
    # Should return cached response, not the new one
    assert response2 == {"choices": [{"message": {"content": "Hello there!"}}]}


def test_cache_entry_creation(cache):
    """Test cache entry creation and retrieval."""
    request_data = {"messages": [{"role": "user", "content": "Test"}]}
    response_data = {"choices": [{"message": {"content": "Test response"}}]}
    
    cache.set(
        key="test_entry",
        provider="openai",
        model="gpt-4",
        endpoint="/v1/chat/completions",
        request_data=request_data,
        response_data=response_data,
    )
    
    entry = cache.get("test_entry")
    assert entry is not None
    assert entry.provider == "openai"
    assert entry.model == "gpt-4"
    assert entry.request_data == request_data
    assert entry.response_data == response_data
    assert entry.response_text == "Test response"


def test_cache_deletion(cache):
    """Test cache entry deletion."""
    request_data = {"messages": [{"role": "user", "content": "Test"}]}
    response_data = {"choices": [{"message": {"content": "Test response"}}]}
    
    cache.set(
        key="test_delete",
        provider="openai",
        model="gpt-4",
        endpoint="/v1/chat/completions",
        request_data=request_data,
        response_data=response_data,
    )
    
    # Verify entry exists
    assert cache.get("test_delete") is not None
    
    # Delete entry
    assert cache.delete("test_delete") is True
    
    # Verify entry is gone
    assert cache.get("test_delete") is None


def test_list_entries(cache):
    """Test listing cache entries."""
    # Add multiple entries
    for i in range(3):
        cache.set(
            key=f"test_{i}",
            provider="openai",
            model="gpt-4",
            endpoint="/v1/chat/completions",
            request_data={"messages": [{"role": "user", "content": f"Test {i}"}]},
            response_data={"choices": [{"message": {"content": f"Response {i}"}}]},
        )
    
    # List all entries
    entries = cache.list_entries()
    assert len(entries) == 3
    
    # List with limit
    entries = cache.list_entries(limit=2)
    assert len(entries) == 2
    
    # Filter by provider
    entries = cache.list_entries(provider="openai")
    assert len(entries) == 3
    
    entries = cache.list_entries(provider="anthropic")
    assert len(entries) == 0


def test_purge_expired(cache):
    """Test purging expired entries."""
    # Add entry with short TTL
    cache.set(
        key="test_expired",
        provider="openai",
        model="gpt-4",
        endpoint="/v1/chat/completions",
        request_data={"messages": [{"role": "user", "content": "Test"}]},
        response_data={"choices": [{"message": {"content": "Response"}}]},
        ttl_days=-1,  # Expires immediately
    )
    
    # Add entry with normal TTL
    cache.set(
        key="test_valid",
        provider="openai",
        model="gpt-4",
        endpoint="/v1/chat/completions",
        request_data={"messages": [{"role": "user", "content": "Test"}]},
        response_data={"choices": [{"message": {"content": "Response"}}]},
        ttl_days=30,
    )
    
    # Purge expired
    deleted_count = cache.purge_expired()
    assert deleted_count == 1
    
    # Verify expired entry is gone
    assert cache.get("test_expired") is None
    
    # Verify valid entry remains
    assert cache.get("test_valid") is not None


def test_purge_older_than(cache):
    """Test purging entries older than specified days."""
    # Add entry
    cache.set(
        key="test_old",
        provider="openai",
        model="gpt-4",
        endpoint="/v1/chat/completions",
        request_data={"messages": [{"role": "user", "content": "Test"}]},
        response_data={"choices": [{"message": {"content": "Response"}}]},
    )
    
    # Purge entries older than 1 day (should not delete our entry since it's not older than 1 day)
    deleted_count = cache.purge_older_than(1)
    assert deleted_count == 0
    
    # Verify entry is still there
    assert cache.get("test_old") is not None


def test_get_stats(cache):
    """Test getting cache statistics."""
    # Add some entries
    for i in range(2):
        cache.set(
            key=f"test_stats_{i}",
            provider="openai",
            model="gpt-4",
            endpoint="/v1/chat/completions",
            request_data={"messages": [{"role": "user", "content": f"Test {i}"}]},
            response_data={"choices": [{"message": {"content": f"Response {i}"}}]},
        )
    
    cache.set(
        key="test_stats_anthropic",
        provider="anthropic",
        model="claude-3",
        endpoint="/v1/messages",
        request_data={"messages": [{"role": "user", "content": "Test"}]},
        response_data={"content": [{"text": "Response"}]},
    )
    
    stats = cache.get_stats()
    assert stats.total_entries == 3
    assert "openai" in stats.provider_stats
    assert "anthropic" in stats.provider_stats
    assert stats.provider_stats["openai"]["count"] == 2
    assert stats.provider_stats["anthropic"]["count"] == 1


def test_cache_close(cache):
    """Test cache cleanup."""
    # Add an entry
    cache.set(
        key="test_close",
        provider="openai",
        model="gpt-4",
        endpoint="/v1/chat/completions",
        request_data={"messages": [{"role": "user", "content": "Test"}]},
        response_data={"choices": [{"message": {"content": "Response"}}]},
    )
    
    # Close cache
    cache.close()
    
    # Should not raise an error
    assert True


def test_compression_disabled(temp_db):
    """Test cache with compression disabled."""
    cache = LLMCache(database_path=temp_db, enable_compression=False)
    
    request_data = {"messages": [{"role": "user", "content": "Hello"}]}
    response_data = {"choices": [{"message": {"content": "Hello there!"}}]}
    
    cache.set(
        key="test_no_compression",
        provider="openai",
        model="gpt-4",
        endpoint="/v1/chat/completions",
        request_data=request_data,
        response_data=response_data,
    )
    
    entry = cache.get("test_no_compression")
    assert entry is not None
    assert entry.response_data == response_data
    
    cache.close()


def test_custom_ttl(cache):
    """Test custom TTL setting."""
    request_data = {"messages": [{"role": "user", "content": "Test"}]}
    response_data = {"choices": [{"message": {"content": "Response"}}]}
    
    cache.set(
        key="test_custom_ttl",
        provider="openai",
        model="gpt-4",
        endpoint="/v1/chat/completions",
        request_data=request_data,
        response_data=response_data,
        ttl_days=7,
    )
    
    entry = cache.get("test_custom_ttl")
    assert entry is not None
    assert entry.ttl_days == 7
    
    # Check expiration date
    expected_expires = datetime.now(timezone.utc) + timedelta(days=7)
    assert abs((entry.expires_at - expected_expires).total_seconds()) < 60  # Within 1 minute 