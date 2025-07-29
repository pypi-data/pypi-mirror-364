"""HTTP proxy for intercepting and caching LLM API calls."""

import json
import time
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import httpx
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse, StreamingResponse
from starlette.middleware.base import BaseHTTPMiddleware

from ..core.cache import LLMCache
from ..core.hashing import hash_request
from ..core.schema import CacheStats


class LLMCacheProxy:
    """HTTP proxy that intercepts and caches LLM API calls."""
    
    def __init__(
        self,
        cache: Optional[LLMCache] = None,
        upstream_urls: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize proxy.
        
        Args:
            cache: Cache instance
            upstream_urls: Mapping of provider names to upstream URLs
        """
        self.cache = cache or LLMCache()
        self.upstream_urls = upstream_urls or {
            "openai": "https://api.openai.com",
            "anthropic": "https://api.anthropic.com",
            "cohere": "https://api.cohere.ai",
        }
        
        self.app = FastAPI(title="LLM Cache Proxy", version="0.1.0")
        self.app.add_middleware(ProxyMiddleware, cache=self.cache, upstream_urls=self.upstream_urls)
        
        # Add metrics endpoint
        self.app.get("/metrics")(self.metrics_endpoint)
        self.app.get("/health")(self.health_endpoint)
    
    def metrics_endpoint(self):
        """Return cache metrics in Prometheus format."""
        stats = self.cache.get_stats()
        
        metrics = []
        metrics.append(f"# HELP llm_cache_entries_total Total number of cache entries")
        metrics.append(f"# TYPE llm_cache_entries_total counter")
        metrics.append(f"llm_cache_entries_total {stats.total_entries}")
        
        metrics.append(f"# HELP llm_cache_hits_total Total number of cache hits")
        metrics.append(f"# TYPE llm_cache_hits_total counter")
        metrics.append(f"llm_cache_hits_total {stats.total_hits}")
        
        metrics.append(f"# HELP llm_cache_misses_total Total number of cache misses")
        metrics.append(f"# TYPE llm_cache_misses_total counter")
        metrics.append(f"llm_cache_misses_total {stats.total_misses}")
        
        metrics.append(f"# HELP llm_cache_cost_saved_usd Total cost saved in USD")
        metrics.append(f"# TYPE llm_cache_cost_saved_usd counter")
        metrics.append(f"llm_cache_cost_saved_usd {stats.total_cost_saved_usd}")
        
        # Provider breakdown
        for provider, provider_stats in stats.provider_stats.items():
            metrics.append(f"# HELP llm_cache_provider_entries_total Cache entries by provider")
            metrics.append(f"# TYPE llm_cache_provider_entries_total counter")
            metrics.append(f'llm_cache_provider_entries_total{{provider="{provider}"}} {provider_stats["count"]}')
            
            metrics.append(f"# HELP llm_cache_provider_cost_total Cost by provider")
            metrics.append(f"# TYPE llm_cache_provider_cost_total counter")
            metrics.append(f'llm_cache_provider_cost_total{{provider="{provider}"}} {provider_stats["total_cost"]}')
        
        return Response(content="\n".join(metrics), media_type="text/plain")
    
    def health_endpoint(self):
        """Health check endpoint."""
        return {"status": "healthy", "cache_backend": self.cache.backend}


class ProxyMiddleware(BaseHTTPMiddleware):
    """Middleware to intercept and cache LLM API calls."""
    
    def __init__(self, app, cache: LLMCache, upstream_urls: Dict[str, str]):
        super().__init__(app)
        self.cache = cache
        self.upstream_urls = upstream_urls
    
    async def dispatch(self, request: Request, call_next):
        """Process request and potentially cache response."""
        # Only intercept LLM API calls
        if not self._is_llm_request(request):
            return await call_next(request)
        
        # Extract provider and model
        provider = self._extract_provider(request)
        model = self._extract_model(request)
        
        if not provider or not model:
            return await call_next(request)
        
        # Create cache key
        request_data = await self._extract_request_data(request)
        key = hash_request(
            provider=provider,
            model=model,
            endpoint=request.url.path,
            request_data=request_data,
        )
        
        # Try to get from cache
        cached_entry = self.cache.get(key)
        if cached_entry:
            # Return cached response
            if cached_entry.is_streaming and cached_entry.stream_chunks:
                return self._create_streaming_response(cached_entry.stream_chunks)
            else:
                return JSONResponse(content=cached_entry.response_data)
        
        # Forward to upstream
        upstream_url = self.upstream_urls.get(provider)
        if not upstream_url:
            raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}")
        
        # Make upstream request
        start_time = time.time()
        response = await self._forward_request(request, upstream_url)
        latency_ms = (time.time() - start_time) * 1000
        
        # Cache response
        await self._cache_response(
            key=key,
            provider=provider,
            model=model,
            endpoint=request.url.path,
            request_data=request_data,
            response=response,
            latency_ms=latency_ms,
        )
        
        return response
    
    def _is_llm_request(self, request: Request) -> bool:
        """Check if request is for an LLM API."""
        path = request.url.path
        return any(
            path.startswith("/v1/chat/completions") or
            path.startswith("/v1/completions") or
            path.startswith("/v1/messages")
            for provider in self.upstream_urls.keys()
        )
    
    def _extract_provider(self, request: Request) -> Optional[str]:
        """Extract provider from request."""
        host = request.headers.get("host", "")
        
        if "openai" in host or "api.openai.com" in host:
            return "openai"
        elif "anthropic" in host or "api.anthropic.com" in host:
            return "anthropic"
        elif "cohere" in host or "api.cohere.ai" in host:
            return "cohere"
        
        return None
    
    def _extract_model(self, request: Request) -> Optional[str]:
        """Extract model from request body."""
        try:
            body = request.body()
            if body:
                data = json.loads(body)
                return data.get("model")
        except (json.JSONDecodeError, AttributeError):
            pass
        
        return None
    
    async def _extract_request_data(self, request: Request) -> Dict[str, Any]:
        """Extract request data for caching."""
        try:
            body = await request.body()
            if body:
                return json.loads(body)
        except json.JSONDecodeError:
            pass
        
        return {}
    
    async def _forward_request(self, request: Request, upstream_url: str) -> Response:
        """Forward request to upstream server."""
        # Build upstream URL
        upstream_path = request.url.path
        upstream_full_url = f"{upstream_url}{upstream_path}"
        
        # Prepare headers
        headers = dict(request.headers)
        headers.pop("host", None)  # Remove host header
        
        # Make request
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=request.method,
                url=upstream_full_url,
                headers=headers,
                content=await request.body(),
                params=request.query_params,
            )
        
        # Convert to FastAPI response
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
        )
    
    async def _cache_response(
        self,
        key: str,
        provider: str,
        model: str,
        endpoint: str,
        request_data: Dict[str, Any],
        response: Response,
        latency_ms: float,
    ):
        """Cache the response."""
        try:
            # Parse response
            if response.headers.get("content-type", "").startswith("application/json"):
                response_data = json.loads(response.body)
            else:
                response_data = {"content": response.body.decode()}
            
            # Store in cache
            self.cache.set(
                key=key,
                provider=provider,
                model=model,
                endpoint=endpoint,
                request_data=request_data,
                response_data=response_data,
            )
        except Exception as e:
            # Log error but don't fail the request
            print(f"Failed to cache response: {e}")
    
    def _create_streaming_response(self, chunks: List[Dict[str, Any]]) -> StreamingResponse:
        """Create streaming response from cached chunks."""
        def generate():
            for chunk in chunks:
                yield f"data: {json.dumps(chunk)}\n\n"
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/plain",
            headers={"content-type": "text/event-stream"},
        ) 