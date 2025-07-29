# LLM Cache

A drop-in, model-agnostic cache for Large Language Model API calls. Cache your OpenAI, Anthropic, and other LLM API responses to save costs and improve performance.

**Author:** [Sherin Joseph Roy](https://sherin-sef-ai.github.io/)  
**Email:** sherin.joseph2217@gmail.com  
**GitHub:** [@Sherin-SEF-AI](https://github.com/Sherin-SEF-AI)

[![PyPI version](https://badge.fury.io/py/llm-cache.svg)](https://badge.fury.io/py/llm-cache)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- **🔐 Deterministic Hashing**: SHA256-based request signature hashing
- **💾 Multiple Backends**: SQLite (default) and Redis support
- **📊 Cost Tracking**: Monitor API costs and savings
- **⚡ Streaming Support**: Cache and replay streamed responses
- **🔧 Provider Agnostic**: Works with OpenAI, Anthropic, Cohere, and more
- **🛡️ Encryption**: Optional AES-256 encryption for sensitive data
- **🗜️ Compression**: Zstandard compression to reduce storage
- **🌐 HTTP Proxy**: Transparent proxy mode for existing applications
- **📈 Metrics**: Prometheus-compatible metrics endpoint
- **⚙️ TTL Support**: Configurable time-to-live for cache entries

## Quick Start

### Installation

```bash
pip install llm-cache
```

### Basic Usage

#### Decorator Pattern

```python
from llm_cache import cached_call

@cached_call(provider="openai", model="gpt-4")
def ask_llm(prompt: str):
    # Your existing OpenAI call here
    return openai_client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

# First call hits the API
response1 = ask_llm("What is Python?")
# Second call returns cached response
response2 = ask_llm("What is Python?")  # Instant!
```

#### Context Manager

```python
from llm_cache import wrap_openai
import openai

client = openai.OpenAI()

# Wrap your client with caching
with wrap_openai(client, ttl_days=7):
    # All calls are automatically cached
    response1 = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Hello"}]
    )
    
    # Same request returns cached response
    response2 = client.chat.completions.create(
        model="gpt-4", 
        messages=[{"role": "user", "content": "Hello"}]
    )
```

#### Low-level API

```python
from llm_cache import LLMCache

cache = LLMCache()

def fetch_from_openai(prompt):
    # Your actual API call
    return openai_client.chat.completions.create(...)

# Get or set from cache
response = cache.get_or_set(
    key="unique_request_hash",
    fetch_func=lambda: fetch_from_openai("What is AI?"),
    provider="openai",
    model="gpt-4",
    endpoint="/v1/chat/completions",
    request_data={"messages": [{"role": "user", "content": "What is AI?"}]}
)
```

### HTTP Proxy Mode

Start a proxy server that intercepts and caches LLM API calls:

```bash
llm-cache serve --host 127.0.0.1 --port 8100
```

Then point your applications to the proxy instead of the original API:

```python
import openai

# Use proxy instead of direct API
client = openai.OpenAI(
    base_url="http://127.0.0.1:8100",
    api_key="your-api-key"
)

# All calls are automatically cached
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}]
)
```

## CLI Commands

### View Statistics

```bash
# Basic stats
llm-cache stats

# Detailed stats with provider breakdown
llm-cache stats --verbose
```

### List Cache Entries

```bash
# List recent entries
llm-cache list

# Filter by provider
llm-cache list --provider openai

# Filter by model
llm-cache list --model gpt-4

# Limit results
llm-cache list --limit 10
```

### Inspect Entries

```bash
# Show entry details
llm-cache show <cache_key>

# Export entry to file
llm-cache show <cache_key> --output entry.json
```

### Purge Cache

```bash
# Delete specific entry
llm-cache purge --key <cache_key>

# Delete expired entries
llm-cache purge --expired

# Delete entries older than 30 days
llm-cache purge --older 30

# Delete all entries for a model
llm-cache purge --model gpt-3.5-turbo

# Delete all entries (with confirmation)
llm-cache purge --all
```

### Export Data

```bash
# Export to JSONL format
llm-cache export cache_dump.jsonl

# Export to JSON format
llm-cache export cache_dump.json --format json

# Export only OpenAI entries
llm-cache export openai_entries.jsonl --provider openai
```

### Health Check

```bash
# Check system health
llm-cache doctor
```

## Configuration

### Environment Variables

```bash
# Cache settings
export LLMCACHE_TTL=30                    # Default TTL in days
export LLMCACHE_COMPRESSION=true          # Enable compression
export LLMCACHE_ENCRYPTION=false          # Enable encryption
export LLMCACHE_ENCRYPTION_KEY="secret"   # Encryption key

# Storage
export LLMCACHE_BACKEND=sqlite            # Backend (sqlite, redis)
export LLMCACHE_DATABASE_URL="..."        # Database URL

# Proxy settings
export LLMCACHE_PROXY_HOST=127.0.0.1
export LLMCACHE_PROXY_PORT=8100

# Logging
export LLMCACHE_LOG_LEVEL=INFO
export LLMCACHE_LOG_FILE=/path/to/logs
```

### Configuration File

Create `~/.config/llm-cache/config.toml`:

```toml
# Cache settings
backend = "sqlite"
default_ttl_days = 30
enable_compression = true
enable_encryption = false

# Proxy settings
proxy_host = "127.0.0.1"
proxy_port = 8100

# Pricing table (cost per 1K tokens)
[pricing_table]
openai.gpt-4 = { input = 0.03, output = 0.06 }
openai.gpt-3.5-turbo = { input = 0.0015, output = 0.002 }
anthropic.claude-3 = { input = 0.015, output = 0.075 }
```

## Advanced Usage

### Streaming Support

```python
@cached_call(provider="openai", model="gpt-4")
def streaming_call(messages, stream=True):
    return openai_client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        stream=stream
    )

# First call collects the stream
response = streaming_call([{"role": "user", "content": "Hello"}], stream=True)

# Subsequent calls replay the cached stream
for chunk in response:
    print(chunk)
```

### Custom TTL

```python
@cached_call(provider="openai", model="gpt-4", ttl_days=7)
def short_lived_cache(prompt):
    return openai_client.chat.completions.create(...)
```

### Encryption

```python
import os
os.environ["LLMCACHE_ENCRYPTION_KEY"] = "your-secret-key"

cache = LLMCache(enable_encryption=True)
# All cached data will be encrypted
```

### Redis Backend

```python
cache = LLMCache(
    backend="redis",
    database_url="redis://localhost:6379/0"
)
```

## Metrics

When running in proxy mode, access metrics at `/metrics`:

```bash
curl http://localhost:8100/metrics
```

Example output:
```
# HELP llm_cache_entries_total Total number of cache entries
# TYPE llm_cache_entries_total counter
llm_cache_entries_total 42

# HELP llm_cache_hits_total Total number of cache hits
# TYPE llm_cache_hits_total counter
llm_cache_hits_total 156

# HELP llm_cache_cost_saved_usd Total cost saved in USD
# TYPE llm_cache_cost_saved_usd counter
llm_cache_cost_saved_usd 12.34
```

## Examples

### OpenAI Integration

```python
import openai
from llm_cache import wrap_openai

client = openai.OpenAI()

with wrap_openai(client):
    # All calls are cached
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Explain quantum computing"}],
        temperature=0.7
    )
```

### Anthropic Integration

```python
import anthropic
from llm_cache import cached_call

@cached_call(provider="anthropic", model="claude-3-sonnet")
def ask_claude(prompt):
    client = anthropic.Anthropic()
    return client.messages.create(
        model="claude-3-sonnet",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )
```

### HTTP Client Integration

```python
import httpx
from llm_cache import LLMCache

cache = LLMCache()

def cached_api_call(prompt):
    def fetch():
        with httpx.Client() as client:
            response = client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "gpt-4",
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            return response.json()
    
    return cache.get_or_set(
        key=f"prompt_{hash(prompt)}",
        fetch_func=fetch,
        provider="openai",
        model="gpt-4",
        endpoint="/v1/chat/completions",
        request_data={"messages": [{"role": "user", "content": prompt}]}
    )
```

## Performance

- **Cache Hit Rate**: Typically 60-80% for repeated queries
- **Cost Savings**: 40-60% reduction in API costs
- **Latency**: Cache hits return in <1ms
- **Storage**: ~1KB per cached response (compressed)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run `pytest`
6. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- 📖 [Documentation](https://llm-cache.readthedocs.io)
- 🐛 [Issue Tracker](https://github.com/llm-cache/llm-cache/issues)
- 💬 [Discussions](https://github.com/llm-cache/llm-cache/discussions) 