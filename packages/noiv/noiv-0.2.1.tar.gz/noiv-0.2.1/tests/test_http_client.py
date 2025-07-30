"""
Tests for HTTP client functionality
"""

import pytest
import sys
from pathlib import Path

# Add the parent directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.http_client import quick_test


def test_quick_test_success():
    """Test successful HTTP request"""
    result = quick_test("https://httpbin.org/get")
    
    assert result["success"] is True
    assert result["status_code"] == 200
    assert "response_time_ms" in result
    assert result["content_type"] == "application/json"


def test_quick_test_invalid_url():
    """Test handling of invalid URL"""
    result = quick_test("https://invalid-url-that-does-not-exist.com")
    
    assert result["success"] is False
    assert "error" in result
