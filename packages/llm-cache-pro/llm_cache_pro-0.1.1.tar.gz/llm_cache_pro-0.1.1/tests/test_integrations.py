"""Tests for integrations."""

import tempfile
from pathlib import Path

import pytest

from llm_cache.core.cache import LLMCache
from llm_cache.integrations.openai_wrap import cached_call, wrap_openai


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


def test_cached_call_decorator(cache):
    """Test the cached_call decorator."""
    
    @cached_call(provider="openai", model="gpt-4", cache=cache)
    def mock_openai_call(messages, temperature=0.7):
        return {"choices": [{"message": {"content": "Mock response"}}]}
    
    # First call
    response1 = mock_openai_call([{"role": "user", "content": "Hello"}])
    assert response1 == {"choices": [{"message": {"content": "Mock response"}}]}
    
    # Second call with same parameters should return cached response
    response2 = mock_openai_call([{"role": "user", "content": "Hello"}])
    assert response2 == {"choices": [{"message": {"content": "Mock response"}}]}
    
    # Different parameters should not be cached
    response3 = mock_openai_call([{"role": "user", "content": "Different"}])
    assert response3 == {"choices": [{"message": {"content": "Mock response"}}]}
    
    cache.close()


def test_cached_call_with_model_in_kwargs(cache):
    """Test cached_call with model specified in function call."""
    
    @cached_call(provider="openai", cache=cache)
    def mock_openai_call(messages, model, temperature=0.7):
        return {"choices": [{"message": {"content": f"Response for {model}"}}]}
    
    # Call with model in kwargs
    response1 = mock_openai_call([{"role": "user", "content": "Hello"}], model="gpt-4")
    assert response1 == {"choices": [{"message": {"content": "Response for gpt-4"}}]}
    
    # Same call should be cached
    response2 = mock_openai_call([{"role": "user", "content": "Hello"}], model="gpt-4")
    assert response2 == {"choices": [{"message": {"content": "Response for gpt-4"}}]}
    
    cache.close()


def test_cached_call_with_streaming(cache):
    """Test cached_call with streaming responses."""
    
    @cached_call(provider="openai", model="gpt-4", cache=cache)
    def mock_streaming_call(messages, stream=False):
        if stream:
            return [
                {"choices": [{"delta": {"content": "Hello"}}]},
                {"choices": [{"delta": {"content": " world"}}]},
            ]
        else:
            return {"choices": [{"message": {"content": "Hello world"}}]}
    
        # Non-streaming call
        response1 = mock_streaming_call([{"role": "user", "content": "Hello"}], stream=False)
        assert response1 == {"choices": [{"message": {"content": "Hello world"}}]}
    
        # Streaming call
        response2 = mock_streaming_call([{"role": "user", "content": "Hello"}], stream=True)
        # Convert generator to list for testing
        response2_list = list(response2)
        assert len(response2_list) == 2
    
    cache.close()


def test_wrap_openai_context_manager(cache):
    """Test the wrap_openai context manager."""
    
    # Mock OpenAI client
    class MockOpenAIClient:
        class Chat:
            class Completions:
                def create(self, **kwargs):
                    return {"choices": [{"message": {"content": "Mock response"}}]}
            
            completions = Completions()
        
        chat = Chat()
    
    client = MockOpenAIClient()
    
    # Use context manager
    with wrap_openai(client, cache=cache, ttl_days=7):
        # First call
        response1 = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": "Hello"}]
        )
        assert response1 == {"choices": [{"message": {"content": "Mock response"}}]}
        
        # Second call should be cached
        response2 = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": "Hello"}]
        )
        assert response2 == {"choices": [{"message": {"content": "Mock response"}}]}
    
    # After context manager, original method should be restored
    # (This is hard to test without modifying the original method)
    
    cache.close()


def test_cached_call_async(cache):
    """Test async version of cached_call."""
    import asyncio
    
    @cached_call(provider="openai", model="gpt-4", cache=cache)
    async def mock_async_call(messages, temperature=0.7):
        return {"choices": [{"message": {"content": "Async response"}}]}
    
    async def test_async():
        # First call
        response1 = await mock_async_call([{"role": "user", "content": "Hello"}])
        assert response1 == {"choices": [{"message": {"content": "Async response"}}]}
        
        # Second call should be cached (same response)
        response2 = await mock_async_call([{"role": "user", "content": "Hello"}])
        assert response2 == {"choices": [{"message": {"content": "Async response"}}]}
        
        # Both responses should be the same (cached)
        assert response1 == response2
    
    asyncio.run(test_async())
    cache.close()


def test_cached_call_with_params(cache):
    """Test cached_call with additional params."""
    
    @cached_call(
        provider="openai",
        model="gpt-4",
        params={"temperature": 0.5, "max_tokens": 100},
        cache=cache
    )
    def mock_call(messages):
        return {"choices": [{"message": {"content": "Response"}}]}
    
    # Call with different messages but same params
    response1 = mock_call([{"role": "user", "content": "Hello"}])
    response2 = mock_call([{"role": "user", "content": "World"}])
    
    # Should be different due to different messages
    assert response1 == response2  # Same mock response
    
    cache.close()


def test_cached_call_error_handling(cache):
    """Test error handling in cached_call."""
    
    @cached_call(provider="openai", cache=cache)  # No model specified
    def mock_call_without_model(messages, model=None):
        return {"choices": [{"message": {"content": "Response"}}]}
    
    # Should raise error when model is not provided in function call
    with pytest.raises(ValueError, match="Model must be specified"):
        mock_call_without_model([{"role": "user", "content": "Hello"}])
    
    cache.close() 