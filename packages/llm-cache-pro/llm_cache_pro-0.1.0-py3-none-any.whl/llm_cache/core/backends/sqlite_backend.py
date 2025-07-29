"""SQLite backend for cache storage."""

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import orjson
from sqlmodel import Field, Session, SQLModel, create_engine, select

from ..schema import CacheEntry, CacheStats


class CacheEntryModel(SQLModel, table=True):
    """SQLModel for cache entries."""
    
    __tablename__ = "cache_entries"
    
    id: str = Field(primary_key=True)
    key: str = Field(index=True)
    provider: str = Field(index=True)
    model: str = Field(index=True)
    endpoint: str = Field()
    
    # Request data
    request_data: str = Field()  # JSON string
    request_hash: str = Field()
    
    # Response data
    response_data: str = Field()  # JSON string
    response_text: str = Field()
    response_tokens: Optional[int] = Field(default=None)
    
    # Metadata
    created_at: str = Field()  # ISO format
    accessed_at: str = Field()  # ISO format
    access_count: int = Field(default=0)
    
    # Cost tracking
    cost_usd: Optional[float] = Field(default=None)
    input_tokens: Optional[int] = Field(default=None)
    output_tokens: Optional[int] = Field(default=None)
    
    # Performance
    latency_ms: Optional[float] = Field(default=None)
    
    # Cache settings
    ttl_days: Optional[int] = Field(default=None)
    expires_at: Optional[str] = Field(default=None)  # ISO format
    
    # Versioning
    cache_version: str = Field(default="0.1.0")
    library_version: str = Field(default="0.1.0")
    
    # Streaming support
    is_streaming: bool = Field(default=False)
    stream_chunks: Optional[str] = Field(default=None)  # JSON string


class SQLiteBackend:
    """SQLite backend for cache storage."""
    
    def __init__(self, database_path: Optional[str] = None):
        """
        Initialize SQLite backend.
        
        Args:
            database_path: Path to SQLite database file
        """
        if database_path is None:
            cache_dir = Path.home() / ".cache" / "llm-cache"
            cache_dir.mkdir(parents=True, exist_ok=True)
            database_path = str(cache_dir / "db.sqlite")
        
        self.database_path = database_path
        self.engine = create_engine(f"sqlite:///{database_path}")
        self._create_tables()
    
    def _create_tables(self):
        """Create database tables."""
        SQLModel.metadata.create_all(self.engine)
    
    def _entry_to_model(self, entry: CacheEntry) -> CacheEntryModel:
        """Convert CacheEntry to SQLModel."""
        return CacheEntryModel(
            id=str(entry.id),
            key=entry.key,
            provider=entry.provider,
            model=entry.model,
            endpoint=entry.endpoint,
            request_data=orjson.dumps(entry.request_data).decode(),
            request_hash=entry.request_hash,
            response_data=orjson.dumps(entry.response_data).decode(),
            response_text=entry.response_text,
            response_tokens=entry.response_tokens,
            created_at=entry.created_at.isoformat(),
            accessed_at=entry.accessed_at.isoformat(),
            access_count=entry.access_count,
            cost_usd=entry.cost_usd,
            input_tokens=entry.input_tokens,
            output_tokens=entry.output_tokens,
            latency_ms=entry.latency_ms,
            ttl_days=entry.ttl_days,
            expires_at=entry.expires_at.isoformat() if entry.expires_at else None,
            cache_version=entry.cache_version,
            library_version=entry.library_version,
            is_streaming=entry.is_streaming,
            stream_chunks=orjson.dumps(entry.stream_chunks).decode() if entry.stream_chunks else None,
        )
    
    def _model_to_entry(self, model: CacheEntryModel) -> CacheEntry:
        """Convert SQLModel to CacheEntry."""
        return CacheEntry(
            id=model.id,
            key=model.key,
            provider=model.provider,
            model=model.model,
            endpoint=model.endpoint,
            request_data=orjson.loads(model.request_data),
            request_hash=model.request_hash,
            response_data=orjson.loads(model.response_data),
            response_text=model.response_text,
            response_tokens=model.response_tokens,
            created_at=datetime.fromisoformat(model.created_at),
            accessed_at=datetime.fromisoformat(model.accessed_at),
            access_count=model.access_count,
            cost_usd=model.cost_usd,
            input_tokens=model.input_tokens,
            output_tokens=model.output_tokens,
            latency_ms=model.latency_ms,
            ttl_days=model.ttl_days,
            expires_at=datetime.fromisoformat(model.expires_at) if model.expires_at else None,
            cache_version=model.cache_version,
            library_version=model.library_version,
            is_streaming=model.is_streaming,
            stream_chunks=orjson.loads(model.stream_chunks) if model.stream_chunks else None,
        )
    
    def get(self, key: str) -> Optional[CacheEntry]:
        """Get cache entry by key."""
        with Session(self.engine) as session:
            statement = select(CacheEntryModel).where(CacheEntryModel.key == key)
            result = session.exec(statement).first()
            
            if result is None:
                return None
            
            # Check if expired
            if result.expires_at:
                expires_at = datetime.fromisoformat(result.expires_at)
                # Ensure timezone-aware comparison
                if expires_at.tzinfo is None:
                    expires_at = expires_at.replace(tzinfo=timezone.utc)
                if datetime.now(timezone.utc) > expires_at:
                    # Delete expired entry
                    session.delete(result)
                    session.commit()
                    return None
            
            # Update access count and timestamp
            result.access_count += 1
            result.accessed_at = datetime.now(timezone.utc).isoformat()
            session.commit()
            
            return self._model_to_entry(result)
    
    def set(self, entry: CacheEntry) -> None:
        """Store cache entry."""
        with Session(self.engine) as session:
            # Check if entry already exists
            existing = session.exec(
                select(CacheEntryModel).where(CacheEntryModel.key == entry.key)
            ).first()
            
            if existing:
                # Update existing entry
                model = self._entry_to_model(entry)
                for field, value in model.dict(exclude={"id"}).items():
                    setattr(existing, field, value)
            else:
                # Create new entry
                model = self._entry_to_model(entry)
                session.add(model)
            
            session.commit()
    
    def delete(self, key: str) -> bool:
        """Delete cache entry by key."""
        with Session(self.engine) as session:
            statement = select(CacheEntryModel).where(CacheEntryModel.key == key)
            result = session.exec(statement).first()
            
            if result:
                session.delete(result)
                session.commit()
                return True
            
            return False
    
    def list_entries(
        self,
        limit: Optional[int] = None,
        offset: int = 0,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        query: Optional[str] = None,
    ) -> List[CacheEntry]:
        """List cache entries with optional filtering."""
        with Session(self.engine) as session:
            statement = select(CacheEntryModel)
            
            # Apply filters
            if provider:
                statement = statement.where(CacheEntryModel.provider == provider)
            if model:
                statement = statement.where(CacheEntryModel.model == model)
            
            # Apply limit and offset
            if limit:
                statement = statement.limit(limit)
            statement = statement.offset(offset)
            
            results = session.exec(statement).all()
            return [self._model_to_entry(model) for model in results]
    
    def purge_expired(self) -> int:
        """Delete expired entries and return count."""
        with Session(self.engine) as session:
            now = datetime.now(timezone.utc).isoformat()
            statement = select(CacheEntryModel).where(
                CacheEntryModel.expires_at < now
            )
            expired = session.exec(statement).all()
            
            for entry in expired:
                session.delete(entry)
            
            session.commit()
            return len(expired)
    
    def purge_older_than(self, days: int) -> int:
        """Delete entries older than specified days."""
        with Session(self.engine) as session:
            cutoff = datetime.now(timezone.utc) - timedelta(days=days)
            cutoff_iso = cutoff.isoformat()
            
            statement = select(CacheEntryModel).where(
                CacheEntryModel.created_at < cutoff_iso
            )
            old_entries = session.exec(statement).all()
            
            for entry in old_entries:
                session.delete(entry)
            
            session.commit()
            return len(old_entries)
    
    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        with Session(self.engine) as session:
            # Total entries
            total_entries = session.exec(
                select(CacheEntryModel)
            ).all()
            
            # Provider breakdown
            provider_stats = {}
            for entry in total_entries:
                if entry.provider not in provider_stats:
                    provider_stats[entry.provider] = {
                        "count": 0,
                        "total_cost": 0.0,
                        "total_tokens": 0,
                    }
                provider_stats[entry.provider]["count"] += 1
                if entry.cost_usd:
                    provider_stats[entry.provider]["total_cost"] += entry.cost_usd
                if entry.input_tokens:
                    provider_stats[entry.provider]["total_tokens"] += entry.input_tokens
                if entry.output_tokens:
                    provider_stats[entry.provider]["total_tokens"] += entry.output_tokens
            
            # Model breakdown
            model_stats = {}
            for entry in total_entries:
                if entry.model not in model_stats:
                    model_stats[entry.model] = {
                        "count": 0,
                        "total_cost": 0.0,
                        "total_tokens": 0,
                    }
                model_stats[entry.model]["count"] += 1
                if entry.cost_usd:
                    model_stats[entry.model]["total_cost"] += entry.cost_usd
                if entry.input_tokens:
                    model_stats[entry.model]["total_tokens"] += entry.input_tokens
                if entry.output_tokens:
                    model_stats[entry.model]["total_tokens"] += entry.output_tokens
            
            # Oldest and newest entries
            oldest = session.exec(
                select(CacheEntryModel).order_by(CacheEntryModel.created_at)
            ).first()
            newest = session.exec(
                select(CacheEntryModel).order_by(CacheEntryModel.created_at.desc())
            ).first()
            
            return CacheStats(
                total_entries=len(total_entries),
                provider_stats=provider_stats,
                model_stats=model_stats,
                oldest_entry=datetime.fromisoformat(oldest.created_at) if oldest else None,
                newest_entry=datetime.fromisoformat(newest.created_at) if newest else None,
            )
    
    def close(self):
        """Close database connection."""
        self.engine.dispose() 