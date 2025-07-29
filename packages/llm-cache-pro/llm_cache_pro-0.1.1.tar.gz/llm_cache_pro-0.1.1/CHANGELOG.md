# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2024-07-23

### Changed
- Updated package name to `llm-cache-pro` for PyPI compatibility
- Improved error handling and validation
- Enhanced CLI output formatting

## [0.1.0] - 2024-07-23

### Added

### Added
- Initial release of LLM Cache
- Core caching functionality with SQLite backend
- Deterministic request hashing
- Cost tracking and statistics
- Streaming response support
- HTTP proxy mode
- CLI interface with rich output
- OpenAI integration with decorators and context managers
- Compression and encryption support
- Prometheus metrics endpoint
- Configuration management
- Comprehensive test suite

### Features
- `@cached_call` decorator for easy function caching
- `wrap_openai()` context manager for client wrapping
- `LLMCache` class for low-level cache operations
- HTTP proxy server for transparent caching
- CLI commands: stats, list, show, purge, export, serve, doctor
- Support for multiple LLM providers (OpenAI, Anthropic, Cohere, Google)
- TTL support with automatic expiration
- Cost calculation based on token usage
- Rich CLI output with tables and colors

### Technical
- SQLite backend with SQLModel ORM
- Zstandard compression for response data
- AES-256 encryption for sensitive data
- SHA256 hashing for request signatures
- FastAPI-based HTTP proxy
- Typer-based CLI with rich output
- Comprehensive error handling
- Async support for streaming responses 