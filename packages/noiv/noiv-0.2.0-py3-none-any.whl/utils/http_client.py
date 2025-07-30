"""
Simple HTTP utilities for NOIV V1
Clean and fast endpoint testing
"""

import httpx
import time
from typing import Dict, Any, Optional
from rich.console import Console

console = Console()

class HTTPClient:
    """Async HTTP client for API testing"""
    
    def __init__(self):
        self.client = httpx.AsyncClient()
    
    async def get(self, url: str, timeout: int = 30, **kwargs):
        """Async GET request"""
        return await self.client.get(url, timeout=timeout, **kwargs)
    
    async def post(self, url: str, timeout: int = 30, **kwargs):
        """Async POST request"""
        return await self.client.post(url, timeout=timeout, **kwargs)
    
    async def put(self, url: str, timeout: int = 30, **kwargs):
        """Async PUT request"""
        return await self.client.put(url, timeout=timeout, **kwargs)
    
    async def delete(self, url: str, timeout: int = 30, **kwargs):
        """Async DELETE request"""
        return await self.client.delete(url, timeout=timeout, **kwargs)
    
    async def patch(self, url: str, timeout: int = 30, **kwargs):
        """Async PATCH request"""
        return await self.client.patch(url, timeout=timeout, **kwargs)
    
    async def request(self, method: str, url: str, **kwargs):
        """Generic async request"""
        return await self.client.request(method, url, **kwargs)
    
    async def close(self):
        """Close the client"""
        await self.client.aclose()

def quick_test(url: str, timeout: int = 30) -> Dict[str, Any]:
    """
    Quick test of an API endpoint
    Returns basic information about the endpoint
    """
    
    start_time = time.time()
    
    try:
        with httpx.Client(timeout=timeout) as client:
            response = client.get(url)
            
        response_time = round((time.time() - start_time) * 1000, 2)
        
        return {
            "url": url,
            "status_code": response.status_code,
            "response_time_ms": response_time,
            "content_type": response.headers.get("content-type", "unknown"),
            "content_length": len(response.content),
            "success": 200 <= response.status_code < 300,
            "headers": dict(response.headers),
        }
        
    except httpx.TimeoutException:
        return {
            "url": url,
            "error": "Timeout",
            "response_time_ms": timeout * 1000,
            "success": False
        }
    except Exception as e:
        return {
            "url": url,
            "error": str(e),
            "success": False
        }
