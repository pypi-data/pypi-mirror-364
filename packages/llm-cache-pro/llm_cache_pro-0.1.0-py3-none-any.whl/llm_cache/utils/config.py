"""Configuration utilities for LLM cache."""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import toml

from ..core.schema import CacheConfig


def get_config_path() -> Path:
    """Get the path to the configuration file."""
    config_dir = Path.home() / ".config" / "llm-cache"
    return config_dir / "config.toml"


def get_default_config() -> Dict[str, Any]:
    """Get default configuration."""
    return {
        "backend": "sqlite",
        "database_url": None,
        "default_ttl_days": 30,
        "enable_compression": True,
        "enable_encryption": False,
        "max_cache_size_mb": None,
        "cleanup_interval_hours": 24,
        "log_level": "INFO",
        "log_file": None,
        "proxy_host": "127.0.0.1",
        "proxy_port": 8100,
        "pricing_table": {},
    }


def get_config() -> CacheConfig:
    """Load configuration from file and environment variables."""
    config_path = get_config_path()
    
    # Start with defaults
    config_data = get_default_config()
    
    # Load from file if it exists
    if config_path.exists():
        try:
            file_config = toml.load(config_path)
            config_data.update(file_config)
        except Exception as e:
            print(f"Warning: Failed to load config file {config_path}: {e}")
    
    # Override with environment variables
    env_mapping = {
        "LLMCACHE_BACKEND": "backend",
        "LLMCACHE_DATABASE_URL": "database_url",
        "LLMCACHE_TTL": "default_ttl_days",
        "LLMCACHE_COMPRESSION": "enable_compression",
        "LLMCACHE_ENCRYPTION": "enable_encryption",
        "LLMCACHE_MAX_SIZE": "max_cache_size_mb",
        "LLMCACHE_CLEANUP_INTERVAL": "cleanup_interval_hours",
        "LLMCACHE_LOG_LEVEL": "log_level",
        "LLMCACHE_LOG_FILE": "log_file",
        "LLMCACHE_PROXY_HOST": "proxy_host",
        "LLMCACHE_PROXY_PORT": "proxy_port",
    }
    
    for env_var, config_key in env_mapping.items():
        env_value = os.getenv(env_var)
        if env_value is not None:
            # Convert string values to appropriate types
            if config_key in ["default_ttl_days", "max_cache_size_mb", "cleanup_interval_hours", "proxy_port"]:
                try:
                    config_data[config_key] = int(env_value)
                except ValueError:
                    print(f"Warning: Invalid integer value for {env_var}: {env_value}")
            elif config_key in ["enable_compression", "enable_encryption"]:
                config_data[config_key] = env_value.lower() in ["true", "1", "yes", "on"]
            else:
                config_data[config_key] = env_value
    
    return CacheConfig(**config_data)


def save_config(config: CacheConfig) -> None:
    """Save configuration to file."""
    config_path = get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert to dict and remove None values
    config_dict = config.dict(exclude_none=True)
    
    with open(config_path, "w") as f:
        toml.dump(config_dict, f)


def create_default_config() -> None:
    """Create default configuration file."""
    config = CacheConfig()
    save_config(config)
    print(f"Created default configuration at {get_config_path()}")


def get_cache_dir() -> Path:
    """Get the cache directory path."""
    cache_dir = Path.home() / ".cache" / "llm-cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def get_log_dir() -> Path:
    """Get the log directory path."""
    log_dir = get_cache_dir() / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir 