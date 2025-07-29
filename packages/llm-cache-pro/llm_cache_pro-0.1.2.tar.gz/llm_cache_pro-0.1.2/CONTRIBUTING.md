# Contributing to LLM Cache

Thank you for your interest in contributing to LLM Cache! This document provides guidelines and information for contributors.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Git
- pip

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/your-username/llm-cache.git
   cd llm-cache
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

## Development Workflow

### Code Style

We use the following tools to maintain code quality:

- **Black**: Code formatting
- **Ruff**: Linting and import sorting
- **Pre-commit**: Git hooks for automatic formatting

Run the formatters:
```bash
black llm_cache tests
ruff check --fix llm_cache tests
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=llm_cache --cov-report=html

# Run specific test file
pytest tests/test_cache.py

# Run with verbose output
pytest -v
```

### Type Checking

```bash
# Run mypy (if installed)
mypy llm_cache
```

## Making Changes

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes

- Follow the existing code style
- Add tests for new functionality
- Update documentation if needed
- Add type hints to new functions

### 3. Test Your Changes

```bash
# Run the full test suite
pytest

# Run linting
ruff check llm_cache tests

# Check formatting
black --check llm_cache tests
```

### 4. Commit Your Changes

```bash
git add .
git commit -m "feat: add new feature description"
```

Follow conventional commit format:
- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `style:` Code style changes
- `refactor:` Code refactoring
- `test:` Test changes
- `chore:` Maintenance tasks

### 5. Push and Create a Pull Request

```bash
git push origin feature/your-feature-name
```

## Project Structure

```
llm-cache/
├── llm_cache/              # Main package
│   ├── __init__.py         # Package exports
│   ├── cli.py              # CLI interface
│   ├── core/               # Core functionality
│   │   ├── cache.py        # Main cache interface
│   │   ├── schema.py       # Pydantic models
│   │   ├── hashing.py      # Request hashing
│   │   ├── pricing.py      # Cost calculation
│   │   ├── encryption.py   # Encryption utilities
│   │   ├── streaming.py    # Streaming support
│   │   └── backends/       # Storage backends
│   ├── integrations/       # Provider integrations
│   │   ├── openai_wrap.py  # OpenAI integration
│   │   └── http_proxy.py   # HTTP proxy
│   └── utils/              # Utilities
│       └── config.py       # Configuration
├── tests/                  # Test suite
├── examples/               # Example scripts
├── docs/                   # Documentation
└── pyproject.toml          # Project configuration
```

## Adding New Features

### Adding a New Backend

1. Create a new backend class in `llm_cache/core/backends/`
2. Implement the required interface methods
3. Add tests in `tests/test_backends.py`
4. Update the cache factory in `llm_cache/core/cache.py`

### Adding a New Provider Integration

1. Create integration module in `llm_cache/integrations/`
2. Add provider-specific response parsing
3. Update pricing table in `llm_cache/core/pricing.py`
4. Add tests for the integration

### Adding CLI Commands

1. Add command function to `llm_cache/cli.py`
2. Use Typer decorators for argument parsing
3. Add help text and examples
4. Add tests for the command

## Testing Guidelines

### Writing Tests

- Use descriptive test names
- Test both success and error cases
- Use fixtures for common setup
- Mock external dependencies
- Test edge cases and boundary conditions

### Test Structure

```python
def test_feature_name():
    """Test description."""
    # Arrange
    cache = LLMCache()
    
    # Act
    result = cache.some_method()
    
    # Assert
    assert result == expected_value
```

### Running Specific Tests

```bash
# Run tests matching a pattern
pytest -k "test_cache"

# Run tests in a specific file
pytest tests/test_cache.py::test_get_or_set

# Run tests with specific markers
pytest -m "slow"
```

## Documentation

### Updating Documentation

- Update README.md for user-facing changes
- Update docstrings for API changes
- Add examples for new features
- Update CHANGELOG.md for releases

### Building Documentation

```bash
# Install docs dependencies
pip install sphinx sphinx-rtd-theme

# Build docs
cd docs
make html
```

## Release Process

### Preparing a Release

1. **Update version**
   - Update version in `pyproject.toml`
   - Update version in `llm_cache/__init__.py`

2. **Update changelog**
   - Move items from [Unreleased] to new version
   - Add release date

3. **Create release branch**
   ```bash
   git checkout -b release/v1.0.0
   git commit -m "chore: release v1.0.0"
   git tag v1.0.0
   git push origin release/v1.0.0 --tags
   ```

4. **Build and publish**
   ```bash
   python -m build
   twine upload dist/*
   ```

## Getting Help

- **Issues**: Use GitHub issues for bug reports and feature requests
- **Discussions**: Use GitHub discussions for questions and ideas
- **Code Review**: All changes require review before merging

## Code of Conduct

Please be respectful and inclusive in all interactions. We follow the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/0/code_of_conduct/).

## License

By contributing to LLM Cache, you agree that your contributions will be licensed under the MIT License. 