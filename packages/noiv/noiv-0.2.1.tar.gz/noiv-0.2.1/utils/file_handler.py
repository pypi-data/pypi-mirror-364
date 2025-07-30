"""
File Handler Utilities - Configuration and Test Suite Management
"""

import yaml
import json
from pathlib import Path
from typing import Dict, Any, Union
from rich.console import Console

from ..models import TestSuite, TestCase, HTTPMethod
from ..config import Config

console = Console()


def load_config(config_path: Optional[Path] = None) -> Config:
    """Load NOIV configuration from file or defaults"""
    
    if config_path is None:
        # Look for config in standard locations
        possible_paths = [
            Path.cwd() / "noiv.yaml",
            Path.cwd() / "noiv.yml", 
            Path.cwd() / ".noiv.yaml",
            Path.home() / ".config" / "noiv" / "config.yaml"
        ]
        
        config_path = next((p for p in possible_paths if p.exists()), None)
    
    if config_path and config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            return Config(**config_data)
        except Exception as e:
            console.print(f"⚠️ [yellow]Error loading config from {config_path}: {e}[/yellow]")
    
    # Return default config
    return Config()


def save_config(config: Config, config_path: Path):
    """Save configuration to file"""
    
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, 'w') as f:
        yaml.dump(config.dict(), f, default_flow_style=False, indent=2)
    
    console.print(f"[green]Configuration saved to {config_path}[/green]")


def save_test_suite(test_suite: TestSuite, output_path: Path):
    """Save test suite to file (YAML or JSON)"""
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert to serializable format
    suite_data = {
        "name": test_suite.name,
        "metadata": test_suite.metadata,
        "created_by": test_suite.created_by,
        "tests": [
            {
                "name": test.name,
                "method": test.method.value,
                "url": test.url,
                "expected_status": test.expected_status,
                "headers": test.headers,
                "body": test.body,
                "ai_reasoning": test.ai_reasoning
            }
            for test in test_suite.tests
        ]
    }
    
    if output_path.suffix.lower() in ['.yaml', '.yml']:
        with open(output_path, 'w') as f:
            yaml.dump(suite_data, f, default_flow_style=False, indent=2)
    else:
        with open(output_path, 'w') as f:
            json.dump(suite_data, f, indent=2)
    
    console.print(f"[green]Test suite saved to {output_path}[/green]")


def load_test_suite(file_path: Path) -> TestSuite:
    """Load test suite from file (supports YAML, JSON, Postman)"""
    
    if not file_path.exists():
        raise FileNotFoundError(f"Test file not found: {file_path}")
    
    with open(file_path, 'r') as f:
        if file_path.suffix.lower() in ['.yaml', '.yml']:
            data = yaml.safe_load(f)
        else:
            data = json.load(f)
    
    # Handle different formats
    if 'info' in data and 'item' in data:
        # Postman collection format
        return _convert_postman_collection(data)
    elif 'tests' in data:
        # NOIV format
        return _convert_noiv_format(data)
    else:
        raise ValueError(f"Unsupported test file format: {file_path}")


def _convert_noiv_format(data: Dict[str, Any]) -> TestSuite:
    """Convert NOIV format to TestSuite object"""
    
    tests = []
    for test_data in data.get('tests', []):
        test = TestCase(
            name=test_data['name'],
            method=HTTPMethod(test_data['method']),
            url=test_data['url'],
            expected_status=test_data.get('expected_status', 200),
            headers=test_data.get('headers', {}),
            body=test_data.get('body'),
            ai_reasoning=test_data.get('ai_reasoning')
        )
        tests.append(test)
    
    return TestSuite(
        name=data.get('name', 'Loaded Test Suite'),
        tests=tests,
        metadata=data.get('metadata', {}),
        created_by=data.get('created_by', 'unknown')
    )


def _convert_postman_collection(data: Dict[str, Any]) -> TestSuite:
    """Convert Postman collection to TestSuite object"""
    
    tests = []
    
    def extract_requests(items):
        for item in items:
            if 'request' in item:
                # Individual request
                request = item['request']
                test = TestCase(
                    name=item.get('name', 'Postman Test'),
                    method=HTTPMethod(request.get('method', 'GET')),
                    url=_build_postman_url(request.get('url', {})),
                    expected_status=200,  # Default, Postman doesn't always specify
                    headers=_extract_postman_headers(request.get('header', [])),
                    body=_extract_postman_body(request.get('body', {}))
                )
                tests.append(test)
            elif 'item' in item:
                # Folder with nested items
                extract_requests(item['item'])
    
    extract_requests(data.get('item', []))
    
    return TestSuite(
        name=data.get('info', {}).get('name', 'Postman Collection'),
        tests=tests,
        metadata={
            "imported_from": "postman",
            "original_id": data.get('info', {}).get('_postman_id'),
            "schema": data.get('info', {}).get('schema')
        },
        created_by="postman_import"
    )


def _build_postman_url(url_data: Union[str, Dict[str, Any]]) -> str:
    """Build URL from Postman URL object"""
    
    if isinstance(url_data, str):
        return url_data
    
    if isinstance(url_data, dict):
        protocol = url_data.get('protocol', 'https')
        host = '.'.join(url_data.get('host', []))
        path = '/'.join(url_data.get('path', []))
        return f"{protocol}://{host}/{path}"
    
    return "https://example.com"


def _extract_postman_headers(headers_data: list) -> Dict[str, str]:
    """Extract headers from Postman format"""
    
    headers = {}
    for header in headers_data:
        if not header.get('disabled', False):
            headers[header.get('key', '')] = header.get('value', '')
    
    return headers


def _extract_postman_body(body_data: Dict[str, Any]) -> Any:
    """Extract body from Postman format"""
    
    mode = body_data.get('mode')
    
    if mode == 'raw':
        return body_data.get('raw')
    elif mode == 'formdata':
        form_data = {}
        for item in body_data.get('formdata', []):
            if not item.get('disabled', False):
                form_data[item.get('key', '')] = item.get('value', '')
        return form_data
    elif mode == 'urlencoded':
        url_data = {}
        for item in body_data.get('urlencoded', []):
            if not item.get('disabled', False):
                url_data[item.get('key', '')] = item.get('value', '')
        return url_data
    
    return None


def export_to_postman(test_suite: TestSuite) -> Dict[str, Any]:
    """Export TestSuite to Postman collection format"""
    
    items = []
    for test in test_suite.tests:
        item = {
            "name": test.name,
            "request": {
                "method": test.method.value,
                "header": [
                    {"key": k, "value": v}
                    for k, v in test.headers.items()
                ],
                "url": {
                    "raw": test.url,
                    "protocol": "https",
                    "host": test.url.split('://')[1].split('/')[0].split('.'),
                    "path": test.url.split('://')[1].split('/')[1:] if '/' in test.url.split('://')[1] else []
                }
            }
        }
        
        if test.body:
            item["request"]["body"] = {
                "mode": "raw",
                "raw": json.dumps(test.body) if isinstance(test.body, dict) else str(test.body)
            }
        
        items.append(item)
    
    return {
        "info": {
            "name": test_suite.name,
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": items
    }


def export_to_curl(test_suite: TestSuite) -> str:
    """Export TestSuite to curl commands"""
    
    curl_commands = []
    
    for test in test_suite.tests:
        cmd = f"curl -X {test.method.value}"
        
        # Add headers
        for key, value in test.headers.items():
            cmd += f" -H '{key}: {value}'"
        
        # Add body
        if test.body:
            if isinstance(test.body, dict):
                cmd += f" -d '{json.dumps(test.body)}'"
            else:
                cmd += f" -d '{test.body}'"
        
        cmd += f" '{test.url}'"
        
        curl_commands.append(f"# {test.name}")
        if test.ai_reasoning:
            curl_commands.append(f"# AI Reasoning: {test.ai_reasoning}")
        curl_commands.append(cmd)
        curl_commands.append("")
    
    return "\n".join(curl_commands)
