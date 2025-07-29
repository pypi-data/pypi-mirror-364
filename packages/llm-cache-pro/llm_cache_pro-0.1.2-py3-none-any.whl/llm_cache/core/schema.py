"""Pydantic models for cache entries and metadata."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class CacheEntry(BaseModel):
    """A cache entry storing LLM request/response data."""
    
    id: UUID = Field(default_factory=uuid4)
    key: str = Field(..., description="SHA256 hash of the request signature")
    provider: str = Field(..., description="LLM provider (openai, anthropic, etc.)")
    model: str = Field(..., description="Model name (gpt-4, claude-3, etc.)")
    endpoint: str = Field(..., description="API endpoint path")
    
    # Request data
    request_data: Dict[str, Any] = Field(..., description="Full request payload")
    request_hash: str = Field(..., description="Hash of request data")
    
    # Response data
    response_data: Union[Dict[str, Any], List[Dict[str, Any]]] = Field(..., description="Full response payload")
    response_text: str = Field(..., description="Extracted response text")
    response_tokens: Optional[int] = Field(None, description="Number of tokens in response")
    
    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    accessed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    access_count: int = Field(default=0, description="Number of cache hits")
    
    # Cost tracking
    cost_usd: Optional[float] = Field(None, description="Cost in USD")
    input_tokens: Optional[int] = Field(None, description="Input tokens")
    output_tokens: Optional[int] = Field(None, description="Output tokens")
    
    # Performance
    latency_ms: Optional[float] = Field(None, description="Request latency in milliseconds")
    
    # Cache settings
    ttl_days: Optional[int] = Field(None, description="Time to live in days")
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp")
    
    # Versioning
    cache_version: str = Field(default="0.1.0", description="Cache schema version")
    library_version: str = Field(default="0.1.0", description="LLM Cache library version")
    
    # Streaming support
    is_streaming: bool = Field(default=False, description="Whether response was streamed")
    stream_chunks: Optional[List[Dict[str, Any]]] = Field(None, description="Streamed chunks")
    
    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }
    }


class CacheStats(BaseModel):
    """Statistics about cache usage."""
    
    total_entries: int = 0
    total_hits: int = 0
    total_misses: int = 0
    hit_rate: float = 0.0
    total_cost_saved_usd: float = 0.0
    total_tokens_saved: int = 0
    oldest_entry: Optional[datetime] = None
    newest_entry: Optional[datetime] = None
    
    # Provider breakdown
    provider_stats: Dict[str, Dict[str, Union[int, float]]] = Field(default_factory=dict)
    
    # Model breakdown
    model_stats: Dict[str, Dict[str, Union[int, float]]] = Field(default_factory=dict)


class CacheConfig(BaseModel):
    """Configuration for the cache."""
    
    # Storage
    backend: str = Field(default="sqlite", description="Storage backend (sqlite, redis)")
    database_url: Optional[str] = Field(None, description="Database connection URL")
    
    # Default settings
    default_ttl_days: int = Field(default=30, description="Default TTL in days")
    enable_compression: bool = Field(default=True, description="Enable response compression")
    enable_encryption: bool = Field(default=False, description="Enable response encryption")
    
    # Performance
    max_cache_size_mb: Optional[int] = Field(None, description="Maximum cache size in MB")
    cleanup_interval_hours: int = Field(default=24, description="Cleanup interval in hours")
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: Optional[str] = Field(None, description="Log file path")
    
    # HTTP proxy
    proxy_host: str = Field(default="127.0.0.1", description="Proxy server host")
    proxy_port: int = Field(default=8100, description="Proxy server port")
    
    # Pricing
    pricing_table: Dict[str, Dict[str, float]] = Field(
        default_factory=dict,
        description="Cost per 1K tokens by model"
    ) 