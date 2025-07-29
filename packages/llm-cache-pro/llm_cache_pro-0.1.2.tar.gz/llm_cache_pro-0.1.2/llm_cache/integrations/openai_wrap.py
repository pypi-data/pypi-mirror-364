"""OpenAI integration for LLM cache."""

import functools
import inspect
from typing import Any, Callable, Dict, Optional, TypeVar, Union

from ..core.cache import LLMCache
from ..core.hashing import hash_request

T = TypeVar("T")


def cached_call(
    provider: str = "openai",
    model: Optional[str] = None,
    params: Optional[Dict[str, Any]] = None,
    ttl_days: Optional[int] = None,
    cache: Optional[LLMCache] = None,
):
    """
    Decorator to cache LLM API calls.
    
    Args:
        provider: LLM provider (openai, anthropic, etc.)
        model: Model name (if not in function args)
        params: Additional parameters to include in hash
        ttl_days: TTL in days
        cache: Cache instance (creates default if None)
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get cache instance
            cache_instance = cache or LLMCache()
            
            # Extract model from kwargs if not provided
            model_name = model or kwargs.get("model")
            if not model_name:
                raise ValueError("Model must be specified in decorator or function call")
            
            # Extract request data from function call
            request_data = _extract_request_data(func, args, kwargs)
            
            # Create cache key
            key = hash_request(
                provider=provider,
                model=model_name,
                endpoint=_get_endpoint_from_func(func),
                request_data=request_data,
                params=params,
            )
            
            # Define fetch function
            def fetch():
                return func(*args, **kwargs)
            
            # Get or set from cache
            return cache_instance.get_or_set(
                key=key,
                fetch_func=fetch,
                provider=provider,
                model=model_name,
                endpoint=_get_endpoint_from_func(func),
                request_data=request_data,
                ttl_days=ttl_days,
                stream=kwargs.get("stream", False),
            )
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Get cache instance
            cache_instance = cache or LLMCache()
            
            # Extract model from kwargs if not provided
            model_name = model or kwargs.get("model")
            if not model_name:
                raise ValueError("Model must be specified in decorator or function call")
            
            # Extract request data from function call
            request_data = _extract_request_data(func, args, kwargs)
            
            # Create cache key
            key = hash_request(
                provider=provider,
                model=model_name,
                endpoint=_get_endpoint_from_func(func),
                request_data=request_data,
                params=params,
            )
            
            # Define async fetch function
            async def fetch():
                return await func(*args, **kwargs)
            
            # Get or set from cache
            return await cache_instance.get_or_set_async(
                key=key,
                fetch_func=fetch,
                provider=provider,
                model=model_name,
                endpoint=_get_endpoint_from_func(func),
                request_data=request_data,
                ttl_days=ttl_days,
                stream=kwargs.get("stream", False),
            )
        
        # Return appropriate wrapper based on function type
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return wrapper
    
    return decorator


class OpenAICacheWrapper:
    """Context manager to wrap OpenAI client with caching."""
    
    def __init__(
        self,
        client,
        cache: Optional[LLMCache] = None,
        ttl_days: Optional[int] = None,
    ):
        """
        Initialize wrapper.
        
        Args:
            client: OpenAI client instance
            cache: Cache instance
            ttl_days: TTL in days
        """
        self.client = client
        self.cache = cache or LLMCache()
        self.ttl_days = ttl_days
        self._original_methods = {}
    
    def __enter__(self):
        """Enter context and patch client methods."""
        self._patch_client()
        return self.client
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context and restore original methods."""
        self._unpatch_client()
    
    def _patch_client(self):
        """Patch OpenAI client methods with caching."""
        # Patch chat.completions.create
        if hasattr(self.client, "chat") and hasattr(self.client.chat, "completions"):
            original_create = self.client.chat.completions.create
            self._original_methods["chat_create"] = original_create
            
            def cached_create(*args, **kwargs):
                return self._cached_chat_create(original_create, *args, **kwargs)
            
            self.client.chat.completions.create = cached_create
        
        # Patch completions.create
        if hasattr(self.client, "completions"):
            original_create = self.client.completions.create
            self._original_methods["completions_create"] = original_create
            
            def cached_create(*args, **kwargs):
                return self._cached_completions_create(original_create, *args, **kwargs)
            
            self.client.completions.create = cached_create
    
    def _unpatch_client(self):
        """Restore original client methods."""
        if "chat_create" in self._original_methods:
            self.client.chat.completions.create = self._original_methods["chat_create"]
        if "completions_create" in self._original_methods:
            self.client.completions.create = self._original_methods["completions_create"]
    
    def _cached_chat_create(self, original_func, *args, **kwargs):
        """Cached version of chat.completions.create."""
        model = kwargs.get("model")
        if not model:
            raise ValueError("Model must be specified")
        
        # Create cache key
        key = hash_request(
            provider="openai",
            model=model,
            endpoint="/v1/chat/completions",
            request_data=kwargs,
        )
        
        # Define fetch function
        def fetch():
            return original_func(*args, **kwargs)
        
        # Get or set from cache
        return self.cache.get_or_set(
            key=key,
            fetch_func=fetch,
            provider="openai",
            model=model,
            endpoint="/v1/chat/completions",
            request_data=kwargs,
            ttl_days=self.ttl_days,
            stream=kwargs.get("stream", False),
        )
    
    def _cached_completions_create(self, original_func, *args, **kwargs):
        """Cached version of completions.create."""
        model = kwargs.get("model")
        if not model:
            raise ValueError("Model must be specified")
        
        # Create cache key
        key = hash_request(
            provider="openai",
            model=model,
            endpoint="/v1/completions",
            request_data=kwargs,
        )
        
        # Define fetch function
        def fetch():
            return original_func(*args, **kwargs)
        
        # Get or set from cache
        return self.cache.get_or_set(
            key=key,
            fetch_func=fetch,
            provider="openai",
            model=model,
            endpoint="/v1/completions",
            request_data=kwargs,
            ttl_days=self.ttl_days,
            stream=kwargs.get("stream", False),
        )


def wrap_openai(client, cache: Optional[LLMCache] = None, ttl_days: Optional[int] = None):
    """
    Create a context manager to wrap OpenAI client with caching.
    
    Args:
        client: OpenAI client instance
        cache: Cache instance
        ttl_days: TTL in days
        
    Returns:
        Context manager for wrapped client
    """
    return OpenAICacheWrapper(client, cache, ttl_days)


def _extract_request_data(func: Callable, args: tuple, kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """Extract request data from function call."""
    # For OpenAI client methods, the request data is typically in kwargs
    # Remove internal parameters that shouldn't affect caching
    request_data = kwargs.copy()
    
    # Remove parameters that shouldn't affect cache key
    cache_ignored = {"api_key", "api_base", "organization", "timeout", "max_retries"}
    for key in cache_ignored:
        request_data.pop(key, None)
    
    return request_data


def _get_endpoint_from_func(func: Callable) -> str:
    """Get endpoint from function name/attributes."""
    func_name = func.__name__
    
    if "chat" in func_name:
        return "/v1/chat/completions"
    elif "completion" in func_name:
        return "/v1/completions"
    else:
        return "/v1/unknown" 