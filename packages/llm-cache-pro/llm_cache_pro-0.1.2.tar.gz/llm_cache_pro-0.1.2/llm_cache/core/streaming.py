"""Streaming utilities for LLM responses."""

import asyncio
from typing import Any, AsyncGenerator, Dict, Generator, List, Optional


class StreamCollector:
    """Collect and replay streamed LLM responses."""
    
    def __init__(self):
        """Initialize stream collector."""
        self.chunks: List[Dict[str, Any]] = []
        self.final_text: str = ""
        self.is_complete: bool = False
    
    def add_chunk(self, chunk: Dict[str, Any]) -> None:
        """
        Add a chunk to the stream.
        
        Args:
            chunk: Stream chunk data
        """
        self.chunks.append(chunk)
    
    def set_final_text(self, text: str) -> None:
        """
        Set the final aggregated text.
        
        Args:
            text: Final response text
        """
        self.final_text = text
        self.is_complete = True
    
    def replay_stream(self) -> Generator[Dict[str, Any], None, None]:
        """
        Replay the collected stream.
        
        Yields:
            Stream chunks in original order
        """
        for chunk in self.chunks:
            yield chunk
    
    async def replay_stream_async(self) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Replay the collected stream asynchronously.
        
        Yields:
            Stream chunks in original order
        """
        for chunk in self.chunks:
            yield chunk
            await asyncio.sleep(0)  # Allow other coroutines to run
    
    def get_chunks(self) -> List[Dict[str, Any]]:
        """
        Get all collected chunks.
        
        Returns:
            List of stream chunks
        """
        return self.chunks.copy()
    
    def get_final_text(self) -> str:
        """
        Get the final aggregated text.
        
        Returns:
            Final response text
        """
        return self.final_text


def extract_text_from_stream_chunk(chunk: Dict[str, Any], provider: str) -> str:
    """
    Extract text content from a stream chunk.
    
    Args:
        chunk: Stream chunk data
        provider: Provider name (openai, anthropic, etc.)
        
    Returns:
        Extracted text content
    """
    if provider == "openai":
        if "choices" in chunk and chunk["choices"]:
            choice = chunk["choices"][0]
            if "delta" in choice and "content" in choice["delta"]:
                return choice["delta"]["content"]
            elif "message" in choice and "content" in choice["message"]:
                return choice["message"]["content"]
    elif provider == "anthropic":
        if "type" in chunk and chunk["type"] == "content_block_delta":
            if "delta" in chunk and "text" in chunk["delta"]:
                return chunk["delta"]["text"]
        elif "type" in chunk and chunk["type"] == "message_delta":
            if "delta" in chunk and "content" in chunk["delta"]:
                content = chunk["delta"]["content"][0]
                if "text" in content:
                    return content["text"]
    
    return ""


def collect_stream(
    stream: Generator[Dict[str, Any], None, None],
    provider: str,
) -> StreamCollector:
    """
    Collect a stream into a StreamCollector.
    
    Args:
        stream: Stream generator
        provider: Provider name
        
    Returns:
        StreamCollector with collected data
    """
    collector = StreamCollector()
    final_text = ""
    
    for chunk in stream:
        collector.add_chunk(chunk)
        final_text += extract_text_from_stream_chunk(chunk, provider)
    
    collector.set_final_text(final_text)
    return collector


async def collect_stream_async(
    stream: AsyncGenerator[Dict[str, Any], None],
    provider: str,
) -> StreamCollector:
    """
    Collect an async stream into a StreamCollector.
    
    Args:
        stream: Async stream generator
        provider: Provider name
        
    Returns:
        StreamCollector with collected data
    """
    collector = StreamCollector()
    final_text = ""
    
    async for chunk in stream:
        collector.add_chunk(chunk)
        final_text += extract_text_from_stream_chunk(chunk, provider)
    
    collector.set_final_text(final_text)
    return collector


def create_stream_from_chunks(chunks: List[Dict[str, Any]]) -> Generator[Dict[str, Any], None, None]:
    """
    Create a stream generator from collected chunks.
    
    Args:
        chunks: List of stream chunks
        
    Yields:
        Stream chunks
    """
    for chunk in chunks:
        yield chunk


async def create_async_stream_from_chunks(
    chunks: List[Dict[str, Any]]
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Create an async stream generator from collected chunks.
    
    Args:
        chunks: List of stream chunks
        
    Yields:
        Stream chunks
    """
    for chunk in chunks:
        yield chunk
        await asyncio.sleep(0)  # Allow other coroutines to run 