#!/usr/bin/env python3
"""
Basic usage example for LLM Cache.

This example demonstrates the three main ways to use LLM Cache:
1. Decorator pattern
2. Context manager
3. Low-level API
"""

import time
from llm_cache import LLMCache, cached_call, wrap_openai


def example_decorator():
    """Example using the @cached_call decorator."""
    print("=== Decorator Pattern ===")
    
    @cached_call(provider="openai", model="gpt-4")
    def ask_llm(prompt: str):
        # Simulate API call
        time.sleep(1)  # Simulate network delay
        return {
            "choices": [{
                "message": {
                    "content": f"Response to: {prompt}"
                }
            }]
        }
    
    # First call - hits the API
    start = time.time()
    response1 = ask_llm("What is Python?")
    duration1 = time.time() - start
    print(f"First call: {duration1:.2f}s")
    
    # Second call - returns cached response
    start = time.time()
    response2 = ask_llm("What is Python?")
    duration2 = time.time() - start
    print(f"Second call: {duration2:.2f}s")
    
    print(f"Speedup: {duration1/duration2:.1f}x faster")
    print()


def example_context_manager():
    """Example using the context manager."""
    print("=== Context Manager Pattern ===")
    
    # Mock OpenAI client
    class MockOpenAIClient:
        class Chat:
            class Completions:
                def create(self, **kwargs):
                    time.sleep(1)  # Simulate API call
                    return {
                        "choices": [{
                            "message": {
                                "content": f"Response to: {kwargs.get('messages', [])}"
                            }
                        }]
                    }
            
            completions = Completions()
        
        chat = Chat()
    
    client = MockOpenAIClient()
    
    with wrap_openai(client, ttl_days=7):
        # First call - hits the API
        start = time.time()
        response1 = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": "Hello"}]
        )
        duration1 = time.time() - start
        print(f"First call: {duration1:.2f}s")
        
        # Second call - returns cached response
        start = time.time()
        response2 = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": "Hello"}]
        )
        duration2 = time.time() - start
        print(f"Second call: {duration2:.2f}s")
        
        print(f"Speedup: {duration1/duration2:.1f}x faster")
    print()


def example_low_level():
    """Example using the low-level API."""
    print("=== Low-level API Pattern ===")
    
    cache = LLMCache()
    
    def fetch_from_api(prompt: str):
        """Simulate API call."""
        time.sleep(1)  # Simulate network delay
        return {
            "choices": [{
                "message": {
                    "content": f"Response to: {prompt}"
                }
            }]
        }
    
    # First call - hits the API
    start = time.time()
    response1 = cache.get_or_set(
        key="prompt_what_is_python",
        fetch_func=lambda: fetch_from_api("What is Python?"),
        provider="openai",
        model="gpt-4",
        endpoint="/v1/chat/completions",
        request_data={"messages": [{"role": "user", "content": "What is Python?"}]}
    )
    duration1 = time.time() - start
    print(f"First call: {duration1:.2f}s")
    
    # Second call - returns cached response
    start = time.time()
    response2 = cache.get_or_set(
        key="prompt_what_is_python",
        fetch_func=lambda: fetch_from_api("What is Python?"),
        provider="openai",
        model="gpt-4",
        endpoint="/v1/chat/completions",
        request_data={"messages": [{"role": "user", "content": "What is Python?"}]}
    )
    duration2 = time.time() - start
    print(f"Second call: {duration2:.2f}s")
    
    print(f"Speedup: {duration1/duration2:.1f}x faster")
    
    # Show cache stats
    stats = cache.get_stats()
    print(f"Cache entries: {stats.total_entries}")
    
    cache.close()
    print()


def example_streaming():
    """Example with streaming responses."""
    print("=== Streaming Support ===")
    
    @cached_call(provider="openai", model="gpt-4")
    def streaming_call(messages, stream=False):
        if stream:
            # Simulate streaming response
            return [
                {"choices": [{"delta": {"content": "Hello"}}]},
                {"choices": [{"delta": {"content": " world"}}]},
                {"choices": [{"delta": {"content": "!"}}]},
            ]
        else:
            return {"choices": [{"message": {"content": "Hello world!"}}]}
    
    # First call - collects stream
    print("First call (streaming):")
    response1 = streaming_call([{"role": "user", "content": "Hello"}], stream=True)
    for chunk in response1:
        print(f"  Chunk: {chunk}")
    
    # Second call - replays cached stream
    print("\nSecond call (cached stream):")
    response2 = streaming_call([{"role": "user", "content": "Hello"}], stream=True)
    for chunk in response2:
        print(f"  Chunk: {chunk}")
    
    print()


def main():
    """Run all examples."""
    print("LLM Cache Examples")
    print("=" * 50)
    
    example_decorator()
    example_context_manager()
    example_low_level()
    example_streaming()
    
    print("Examples completed!")


if __name__ == "__main__":
    main() 