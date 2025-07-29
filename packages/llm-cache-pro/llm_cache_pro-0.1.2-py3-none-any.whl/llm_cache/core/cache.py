"""Main cache interface for LLM API calls."""

import time
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Dict, Generator, List, Optional, Union

import orjson
import zstandard as zstd

from .backends import SQLiteBackend
from .encryption import CacheEncryption
from .hashing import (
    extract_text_from_response,
    extract_usage_from_response,
    hash_request,
)
from .pricing import PricingCalculator
from .schema import CacheEntry, CacheStats
from .streaming import StreamCollector, collect_stream, create_stream_from_chunks


class LLMCache:
    """Main cache interface for LLM API calls."""
    
    def __init__(
        self,
        backend: Optional[str] = None,
        database_path: Optional[str] = None,
        enable_compression: bool = True,
        enable_encryption: bool = False,
        encryption_key: Optional[str] = None,
        default_ttl_days: int = 30,
        pricing_table: Optional[Dict] = None,
    ):
        """
        Initialize LLM cache.
        
        Args:
            backend: Storage backend (sqlite, redis)
            database_path: Path to database file
            enable_compression: Enable response compression
            enable_encryption: Enable response encryption
            encryption_key: Encryption passphrase
            default_ttl_days: Default TTL in days
            pricing_table: Custom pricing table
        """
        self.backend = backend or "sqlite"
        self.enable_compression = enable_compression
        self.enable_encryption = enable_encryption
        self.default_ttl_days = default_ttl_days
        
        # Initialize components
        if self.backend == "sqlite":
            self.storage = SQLiteBackend(database_path)
        else:
            raise ValueError(f"Unsupported backend: {self.backend}")
        
        self.encryption = CacheEncryption(encryption_key) if enable_encryption else None
        self.pricing = PricingCalculator(pricing_table)
        
        # Compression
        if enable_compression:
            self.compressor = zstd.ZstdCompressor()
            self.decompressor = zstd.ZstdDecompressor()
        else:
            self.compressor = None
            self.decompressor = None
    
    def _compress(self, data: str) -> str:
        """Compress data if compression is enabled."""
        if not self.compressor:
            return data
        
        compressed = self.compressor.compress(data.encode())
        return orjson.dumps(compressed).decode()
    
    def _decompress(self, compressed_data: str) -> str:
        """Decompress data if compression is enabled."""
        if not self.decompressor:
            return compressed_data
        
        compressed = orjson.loads(compressed_data)
        return self.decompressor.decompress(compressed).decode()
    
    def _encrypt(self, data: str) -> str:
        """Encrypt data if encryption is enabled."""
        if not self.encryption:
            return data
        
        return self.encryption.encrypt(data)
    
    def _decrypt(self, encrypted_data: str) -> str:
        """Decrypt data if encryption is enabled."""
        if not self.encryption:
            return encrypted_data
        
        return self.encryption.decrypt(encrypted_data)
    
    def get_or_set(
        self,
        key: str,
        fetch_func: Callable[[], Any],
        provider: str,
        model: str,
        endpoint: str,
        request_data: Dict[str, Any],
        ttl_days: Optional[int] = None,
        stream: bool = False,
    ) -> Any:
        """
        Get from cache or fetch and store.
        
        Args:
            key: Cache key
            fetch_func: Function to fetch data if not in cache
            provider: LLM provider
            model: Model name
            endpoint: API endpoint
            request_data: Request payload
            ttl_days: TTL in days (uses default if None)
            stream: Whether response is streamed
            
        Returns:
            Cached or fetched response
        """
        # Try to get from cache
        cached_entry = self.storage.get(key)
        if cached_entry:
            # Return cached response
            if stream and cached_entry.stream_chunks:
                # Replay stream
                return create_stream_from_chunks(cached_entry.stream_chunks)
            else:
                # Return final response
                return cached_entry.response_data
        
        # Fetch from API
        start_time = time.time()
        response = fetch_func()
        latency_ms = (time.time() - start_time) * 1000
        
        # Handle streaming responses
        if stream:
            collector = collect_stream(response, provider)
            response_data = collector.get_chunks()
            response_text = collector.get_final_text()
            stream_chunks = collector.get_chunks()
        else:
            response_data = response
            response_text = extract_text_from_response(response, provider)
            stream_chunks = None
        
        # Extract usage information
        usage = extract_usage_from_response(response_data, provider)
        input_tokens = usage.get("input_tokens")
        output_tokens = usage.get("output_tokens")
        
        # Calculate cost
        cost_usd = None
        if input_tokens and output_tokens:
            cost_usd = self.pricing.calculate_cost(
                provider, model, input_tokens, output_tokens
            )
        
        # Create cache entry
        ttl = ttl_days or self.default_ttl_days
        expires_at = datetime.now(timezone.utc) + timedelta(days=ttl) if ttl else None
        
        entry = CacheEntry(
            key=key,
            provider=provider,
            model=model,
            endpoint=endpoint,
            request_data=request_data,
            request_hash=hash_request(provider, model, endpoint, request_data),
            response_data=response_data,
            response_text=response_text,
            response_tokens=output_tokens,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost_usd,
            latency_ms=latency_ms,
            ttl_days=ttl,
            expires_at=expires_at,
            is_streaming=stream,
            stream_chunks=stream_chunks,
        )
        
        # Store in cache
        self.storage.set(entry)
        
        # Return response
        if stream:
            return create_stream_from_chunks(stream_chunks)
        else:
            return response_data
    
    async def get_or_set_async(
        self,
        key: str,
        fetch_func: Callable[[], Any],
        provider: str,
        model: str,
        endpoint: str,
        request_data: Dict[str, Any],
        ttl_days: Optional[int] = None,
        stream: bool = False,
    ) -> Any:
        """
        Async version of get_or_set.
        
        Args:
            key: Cache key
            fetch_func: Async function to fetch data
            provider: LLM provider
            model: Model name
            endpoint: API endpoint
            request_data: Request payload
            ttl_days: TTL in days
            stream: Whether response is streamed
            
        Returns:
            Cached or fetched response
        """
        # Try to get from cache
        cached_entry = self.storage.get(key)
        if cached_entry:
            if stream and cached_entry.stream_chunks:
                return create_async_stream_from_chunks(cached_entry.stream_chunks)
            else:
                return cached_entry.response_data
        
        # Fetch from API
        start_time = time.time()
        response = await fetch_func()
        latency_ms = (time.time() - start_time) * 1000
        
        # Handle streaming responses
        if stream:
            collector = await collect_stream_async(response, provider)
            response_data = collector.get_chunks()
            response_text = collector.get_final_text()
            stream_chunks = collector.get_chunks()
        else:
            response_data = response
            response_text = extract_text_from_response(response, provider)
            stream_chunks = None
        
        # Extract usage and calculate cost
        usage = extract_usage_from_response(response_data, provider)
        input_tokens = usage.get("input_tokens")
        output_tokens = usage.get("output_tokens")
        
        cost_usd = None
        if input_tokens and output_tokens:
            cost_usd = self.pricing.calculate_cost(
                provider, model, input_tokens, output_tokens
            )
        
        # Create and store entry
        ttl = ttl_days or self.default_ttl_days
        expires_at = datetime.now(timezone.utc) + timedelta(days=ttl) if ttl else None
        
        entry = CacheEntry(
            key=key,
            provider=provider,
            model=model,
            endpoint=endpoint,
            request_data=request_data,
            request_hash=hash_request(provider, model, endpoint, request_data),
            response_data=response_data,
            response_text=response_text,
            response_tokens=output_tokens,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost_usd,
            latency_ms=latency_ms,
            ttl_days=ttl,
            expires_at=expires_at,
            is_streaming=stream,
            stream_chunks=stream_chunks,
        )
        
        self.storage.set(entry)
        
        # Return response
        if stream:
            return create_async_stream_from_chunks(stream_chunks)
        else:
            return response_data
    
    def get(self, key: str) -> Optional[CacheEntry]:
        """Get cache entry by key."""
        return self.storage.get(key)
    
    def set(
        self,
        key: str,
        provider: str,
        model: str,
        endpoint: str,
        request_data: Dict[str, Any],
        response_data: Any,
        ttl_days: Optional[int] = None,
        stream: bool = False,
    ) -> None:
        """Manually store a cache entry."""
        response_text = extract_text_from_response(response_data, provider)
        usage = extract_usage_from_response(response_data, provider)
        
        input_tokens = usage.get("input_tokens")
        output_tokens = usage.get("output_tokens")
        
        cost_usd = None
        if input_tokens and output_tokens:
            cost_usd = self.pricing.calculate_cost(
                provider, model, input_tokens, output_tokens
            )
        
        ttl = ttl_days or self.default_ttl_days
        expires_at = datetime.now(timezone.utc) + timedelta(days=ttl) if ttl else None
        
        entry = CacheEntry(
            key=key,
            provider=provider,
            model=model,
            endpoint=endpoint,
            request_data=request_data,
            request_hash=hash_request(provider, model, endpoint, request_data),
            response_data=response_data,
            response_text=response_text,
            response_tokens=output_tokens,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost_usd,
            ttl_days=ttl,
            expires_at=expires_at,
            is_streaming=stream,
        )
        
        self.storage.set(entry)
    
    def delete(self, key: str) -> bool:
        """Delete cache entry by key."""
        return self.storage.delete(key)
    
    def list_entries(
        self,
        limit: Optional[int] = None,
        offset: int = 0,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        query: Optional[str] = None,
    ) -> List[CacheEntry]:
        """List cache entries with optional filtering."""
        return self.storage.list_entries(limit, offset, provider, model, query)
    
    def purge_expired(self) -> int:
        """Delete expired entries and return count."""
        return self.storage.purge_expired()
    
    def purge_older_than(self, days: int) -> int:
        """Delete entries older than specified days."""
        return self.storage.purge_older_than(days)
    
    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        return self.storage.get_stats()
    
    def close(self):
        """Close cache and cleanup resources."""
        self.storage.close() 