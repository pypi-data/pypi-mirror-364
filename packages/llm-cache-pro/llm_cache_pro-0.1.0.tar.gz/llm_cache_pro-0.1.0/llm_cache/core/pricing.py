"""Pricing utilities for cost calculation."""

from typing import Dict, Optional


# Default pricing table (cost per 1K tokens)
DEFAULT_PRICING = {
    "openai": {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-4o": {"input": 0.005, "output": 0.015},
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
        "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
        "gpt-3.5-turbo-16k": {"input": 0.003, "output": 0.004},
    },
    "anthropic": {
        "claude-3-opus": {"input": 0.015, "output": 0.075},
        "claude-3-sonnet": {"input": 0.003, "output": 0.015},
        "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
        "claude-2.1": {"input": 0.008, "output": 0.024},
        "claude-2.0": {"input": 0.008, "output": 0.024},
        "claude-instant-1": {"input": 0.00163, "output": 0.00551},
    },
    "cohere": {
        "command": {"input": 0.0015, "output": 0.002},
        "command-light": {"input": 0.0003, "output": 0.0006},
        "command-nightly": {"input": 0.0015, "output": 0.002},
    },
    "google": {
        "gemini-pro": {"input": 0.0005, "output": 0.0015},
        "gemini-pro-vision": {"input": 0.0005, "output": 0.0015},
    },
}


class PricingCalculator:
    """Calculate costs for LLM API calls."""
    
    def __init__(self, pricing_table: Optional[Dict] = None):
        """
        Initialize pricing calculator.
        
        Args:
            pricing_table: Custom pricing table, uses default if None
        """
        self.pricing_table = pricing_table or DEFAULT_PRICING
    
    def calculate_cost(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        """
        Calculate cost for a request.
        
        Args:
            provider: LLM provider (openai, anthropic, etc.)
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Cost in USD
        """
        if provider not in self.pricing_table:
            return 0.0
        
        if model not in self.pricing_table[provider]:
            return 0.0
        
        model_pricing = self.pricing_table[provider][model]
        
        input_cost = (input_tokens / 1000) * model_pricing.get("input", 0.0)
        output_cost = (output_tokens / 1000) * model_pricing.get("output", 0.0)
        
        return input_cost + output_cost
    
    def get_model_pricing(self, provider: str, model: str) -> Optional[Dict[str, float]]:
        """
        Get pricing for a specific model.
        
        Args:
            provider: LLM provider
            model: Model name
            
        Returns:
            Pricing dict with input/output costs per 1K tokens
        """
        return self.pricing_table.get(provider, {}).get(model)
    
    def add_model_pricing(
        self,
        provider: str,
        model: str,
        input_cost: float,
        output_cost: float,
    ) -> None:
        """
        Add or update pricing for a model.
        
        Args:
            provider: LLM provider
            model: Model name
            input_cost: Cost per 1K input tokens
            output_cost: Cost per 1K output tokens
        """
        if provider not in self.pricing_table:
            self.pricing_table[provider] = {}
        
        self.pricing_table[provider][model] = {
            "input": input_cost,
            "output": output_cost,
        }
    
    def estimate_tokens(self, text: str) -> int:
        """
        Rough token estimation (4 chars per token).
        
        Args:
            text: Text to estimate tokens for
            
        Returns:
            Estimated token count
        """
        return len(text) // 4 