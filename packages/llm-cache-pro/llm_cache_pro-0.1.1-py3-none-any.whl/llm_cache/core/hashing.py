"""Deterministic hashing for LLM requests."""

import hashlib
import json
from typing import Any, Dict, List, Optional, Union


def canonicalize_json(obj: Any) -> str:
    """Canonicalize JSON for stable hashing."""
    if isinstance(obj, dict):
        # Sort dictionary keys
        return json.dumps(obj, sort_keys=True, separators=(",", ":"))
    elif isinstance(obj, list):
        # Lists are already ordered
        return json.dumps(obj, separators=(",", ":"))
    else:
        return json.dumps(obj, separators=(",", ":"))


def hash_request(
    provider: str,
    model: str,
    endpoint: str,
    request_data: Dict[str, Any],
    params: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Create a deterministic hash for an LLM request.
    
    Args:
        provider: LLM provider (openai, anthropic, etc.)
        model: Model name (gpt-4, claude-3, etc.)
        endpoint: API endpoint path
        request_data: Full request payload
        params: Additional parameters to include in hash
        
    Returns:
        SHA256 hash as hex string
    """
    # Create a stable request signature
    signature = {
        "provider": provider,
        "model": model,
        "endpoint": endpoint,
        "request_data": request_data,
    }
    
    # Add additional parameters if provided
    if params:
        signature["params"] = params
    
    # Canonicalize and hash
    canonical = canonicalize_json(signature)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def hash_messages(messages: List[Dict[str, str]]) -> str:
    """Hash a list of messages for caching."""
    return hashlib.sha256(canonicalize_json(messages).encode("utf-8")).hexdigest()


def hash_prompt(prompt: str) -> str:
    """Hash a single prompt string."""
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()


def extract_text_from_response(response_data: Dict[str, Any], provider: str) -> str:
    """
    Extract text content from various LLM provider responses.
    
    Args:
        response_data: Response payload from provider
        provider: Provider name (openai, anthropic, etc.)
        
    Returns:
        Extracted text content
    """
    if provider == "openai":
        # OpenAI format
        if "choices" in response_data and response_data["choices"]:
            choice = response_data["choices"][0]
            if "message" in choice and "content" in choice["message"]:
                return choice["message"]["content"]
            elif "delta" in choice and "content" in choice["delta"]:
                return choice["delta"]["content"]
    elif provider == "anthropic":
        # Anthropic format
        if "content" in response_data and response_data["content"]:
            content = response_data["content"][0]
            if "text" in content:
                return content["text"]
    elif provider == "cohere":
        # Cohere format
        if "generations" in response_data and response_data["generations"]:
            return response_data["generations"][0]["text"]
    
    # Fallback: try to extract any text field
    if isinstance(response_data, dict):
        for key in ["text", "content", "message", "response"]:
            if key in response_data:
                value = response_data[key]
                if isinstance(value, str):
                    return value
                elif isinstance(value, dict) and "content" in value:
                    return value["content"]
    
    # Last resort: return stringified response
    return str(response_data)


def extract_usage_from_response(response_data: Dict[str, Any], provider: str) -> Dict[str, int]:
    """
    Extract token usage information from provider response.
    
    Args:
        response_data: Response payload from provider
        provider: Provider name
        
    Returns:
        Dict with input_tokens, output_tokens, total_tokens
    """
    usage = {"input_tokens": None, "output_tokens": None, "total_tokens": None}
    
    if provider == "openai":
        if "usage" in response_data:
            openai_usage = response_data["usage"]
            usage.update({
                "input_tokens": openai_usage.get("prompt_tokens"),
                "output_tokens": openai_usage.get("completion_tokens"),
                "total_tokens": openai_usage.get("total_tokens"),
            })
    elif provider == "anthropic":
        if "usage" in response_data:
            anthropic_usage = response_data["usage"]
            usage.update({
                "input_tokens": anthropic_usage.get("input_tokens"),
                "output_tokens": anthropic_usage.get("output_tokens"),
                "total_tokens": anthropic_usage.get("input_tokens", 0) + anthropic_usage.get("output_tokens", 0),
            })
    
    return usage 