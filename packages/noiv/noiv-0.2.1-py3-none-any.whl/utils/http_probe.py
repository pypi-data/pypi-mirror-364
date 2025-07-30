"""
HTTP Probe Utility - The Trust-Building Foundation

This is the NON-AI component that builds developer trust by showing
pure technical analysis before any AI magic happens.
"""

import time
import httpx
from typing import Dict, Any, Optional
from dataclasses import dataclass
from rich.console import Console

console = Console()


@dataclass
class ProbeResult:
    """Results from endpoint probing - pure technical analysis"""
    url: str
    status_code: int
    response_time: float  # milliseconds
    content_type: str
    auth_required: bool
    has_pagination: bool
    response_sample: Dict[str, Any]
    headers: Dict[str, str]
    response_size: int
    server_info: Optional[str] = None
    api_version: Optional[str] = None


async def probe_endpoint(url: str, timeout: int = 10) -> ProbeResult:
    """
    Probe an API endpoint to gather technical information
    
    This is PURE HTTP analysis - no AI involved
    Builds trust by showing real technical data first
    """
    
    start_time = time.time()
    
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            # Make the request
            response = await client.get(url, follow_redirects=True)
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            # Analyze response
            try:
                response_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
            except:
                response_data = {}
            
            # Detect authentication requirements
            auth_required = (
                response.status_code == 401 or
                'authorization' in response.headers.get('www-authenticate', '').lower() or
                'login' in str(response_data).lower()
            )
            
            # Detect pagination
            has_pagination = _detect_pagination(response, response_data)
            
            # Extract server info
            server_info = response.headers.get('server')
            
            # Extract API version
            api_version = _extract_api_version(url, response.headers)
            
            return ProbeResult(
                url=url,
                status_code=response.status_code,
                response_time=response_time,
                content_type=response.headers.get('content-type', 'unknown'),
                auth_required=auth_required,
                has_pagination=has_pagination,
                response_sample=response_data,
                headers=dict(response.headers),
                response_size=len(response.content),
                server_info=server_info,
                api_version=api_version
            )
            
        except httpx.TimeoutException:
            return ProbeResult(
                url=url,
                status_code=408,  # Request Timeout
                response_time=timeout * 1000,
                content_type="timeout",
                auth_required=False,
                has_pagination=False,
                response_sample={},
                headers={},
                response_size=0,
                server_info=None,
                api_version=None
            )
        except Exception as e:
            return ProbeResult(
                url=url,
                status_code=0,  # Connection failed
                response_time=0,
                content_type="error",
                auth_required=False,
                has_pagination=False,
                response_sample={"error": str(e)},
                headers={},
                response_size=0,
                server_info=None,
                api_version=None
            )


def _detect_pagination(response: httpx.Response, data: Dict[str, Any]) -> bool:
    """Detect if the API uses pagination"""
    
    # Check headers for pagination
    pagination_headers = ['link', 'x-total-count', 'x-page', 'x-per-page']
    if any(header in response.headers for header in pagination_headers):
        return True
    
    # Check response data for pagination indicators
    if isinstance(data, dict):
        pagination_fields = ['page', 'pages', 'total', 'limit', 'offset', 'next', 'previous', 'has_more']
        if any(field in data for field in pagination_fields):
            return True
        
        # Check for array responses (often paginated)
        if isinstance(data.get('data'), list) and len(data.get('data', [])) >= 10:
            return True
    
    # Check if response is a large array (likely paginated)
    if isinstance(data, list) and len(data) >= 20:
        return True
    
    return False


def _extract_api_version(url: str, headers: Dict[str, str]) -> Optional[str]:
    """Extract API version from URL or headers"""
    
    # Check URL for version
    import re
    version_match = re.search(r'/v(\d+(?:\.\d+)?)', url)
    if version_match:
        return version_match.group(1)
    
    # Check headers
    version_headers = ['api-version', 'version', 'x-api-version']
    for header in version_headers:
        if header in headers:
            return headers[header]
    
    return None


def probe_endpoint_sync(url: str, timeout: int = 10) -> ProbeResult:
    """Synchronous version of probe_endpoint"""
    import asyncio
    return asyncio.run(probe_endpoint(url, timeout))
