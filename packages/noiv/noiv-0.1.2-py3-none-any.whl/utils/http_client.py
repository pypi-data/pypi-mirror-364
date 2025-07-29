"""
Simple HTTP utilities for NOIV V1
Clean and fast endpoint testing
"""

import httpx
import time
from typing import Dict, Any, Optional
from rich.console import Console

console = Console()

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
