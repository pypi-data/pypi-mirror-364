"""LLM Cache - A drop-in, model-agnostic cache for Large Language Model API calls."""

__version__ = "0.1.0"

from .core.cache import LLMCache
from .core.hashing import hash_request
from .integrations.openai_wrap import cached_call, wrap_openai
from .utils.config import get_config

__all__ = [
    "LLMCache",
    "hash_request",
    "cached_call",
    "wrap_openai",
    "get_config",
] 