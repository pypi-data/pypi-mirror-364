"""
Tests for configuration management
"""

import pytest
import sys
from pathlib import Path

# Add the parent directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config_manager import NOIVConfig


def test_config_initialization():
    """Test config class initialization"""
    config = NOIVConfig()
    
    assert config.config_dir.exists()
    assert config.config_file.name == "config.yaml"


def test_config_get_api_key():
    """Test API key retrieval"""
    config = NOIVConfig()
    
    # Should return None or string
    api_key = config.get_api_key()
    assert api_key is None or isinstance(api_key, str)
