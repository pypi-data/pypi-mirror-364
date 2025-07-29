#!/usr/bin/env python3
"""
HTTP Proxy Example for LLM Cache.

This example demonstrates how to use the HTTP proxy mode to cache
LLM API calls transparently.
"""

import asyncio
import json
import subprocess
import time
from pathlib import Path

import httpx


def start_proxy():
    """Start the LLM Cache proxy server."""
    print("Starting LLM Cache proxy server...")
    
    # Start proxy in background
    process = subprocess.Popen([
        "python", "-m", "llm_cache.cli", "serve",
        "--host", "127.0.0.1",
        "--port", "8100"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for server to start
    time.sleep(2)
    
    return process


def stop_proxy(process):
    """Stop the proxy server."""
    print("Stopping proxy server...")
    process.terminate()
    process.wait()


def test_direct_api():
    """Test direct API calls (no caching)."""
    print("=== Direct API Calls (No Caching) ===")
    
    # Simulate API calls
    for i in range(3):
        start = time.time()
        
        # Simulate API call
        time.sleep(1)  # Simulate network delay
        
        duration = time.time() - start
        print(f"Call {i+1}: {duration:.2f}s")
    
    print()


def test_proxy_api():
    """Test API calls through the proxy (with caching)."""
    print("=== Proxy API Calls (With Caching) ===")
    
    # Test data
    test_request = {
        "model": "gpt-4",
        "messages": [{"role": "user", "content": "What is Python?"}],
        "temperature": 0.7
    }
    
    for i in range(3):
        start = time.time()
        
        try:
            # Make request to proxy
            with httpx.Client() as client:
                response = client.post(
                    "http://127.0.0.1:8100/v1/chat/completions",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": "Bearer fake-api-key"
                    },
                    json=test_request,
                    timeout=30
                )
                
                if response.status_code == 200:
                    print(f"Call {i+1}: Success")
                else:
                    print(f"Call {i+1}: Error {response.status_code}")
                    
        except Exception as e:
            print(f"Call {i+1}: Error - {e}")
        
        duration = time.time() - start
        print(f"  Duration: {duration:.2f}s")
    
    print()


def test_metrics():
    """Test the metrics endpoint."""
    print("=== Metrics Endpoint ===")
    
    try:
        with httpx.Client() as client:
            response = client.get("http://127.0.0.1:8100/metrics")
            
            if response.status_code == 200:
                print("Metrics endpoint is working:")
                print(response.text[:500] + "..." if len(response.text) > 500 else response.text)
            else:
                print(f"Metrics endpoint error: {response.status_code}")
                
    except Exception as e:
        print(f"Metrics endpoint error: {e}")
    
    print()


def test_health():
    """Test the health endpoint."""
    print("=== Health Endpoint ===")
    
    try:
        with httpx.Client() as client:
            response = client.get("http://127.0.0.1:8100/health")
            
            if response.status_code == 200:
                health_data = response.json()
                print(f"Health status: {health_data}")
            else:
                print(f"Health endpoint error: {response.status_code}")
                
    except Exception as e:
        print(f"Health endpoint error: {e}")
    
    print()


def main():
    """Run the proxy example."""
    print("LLM Cache HTTP Proxy Example")
    print("=" * 50)
    
    # Test direct API calls
    test_direct_api()
    
    # Start proxy server
    proxy_process = start_proxy()
    
    try:
        # Test proxy API calls
        test_proxy_api()
        
        # Test endpoints
        test_health()
        test_metrics()
        
    finally:
        # Stop proxy server
        stop_proxy(proxy_process)
    
    print("Proxy example completed!")


if __name__ == "__main__":
    main() 