"""
Import/Export functionality for NOIV
Convert between different API testing formats
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Any
from rich.console import Console

console = Console()

class PostmanImporter:
    """Import Postman collections to NOIV format"""
    
    def import_collection(self, postman_file: Path) -> Dict[str, Any]:
        """Convert Postman collection to NOIV test suite"""
        
        with open(postman_file, 'r') as f:
            postman_data = json.load(f)
        
        # Extract collection info
        collection = postman_data.get('collection', postman_data)
        name = collection.get('info', {}).get('name', 'Imported from Postman')
        
        # Convert requests to NOIV tests
        tests = []
        for item in collection.get('item', []):
            test = self._convert_postman_request(item)
            if test:
                tests.append(test)
        
        return {
            "name": name,
            "tests": tests,
            "metadata": {
                "imported_from": "postman",
                "original_file": str(postman_file)
            }
        }
    
    def _convert_postman_request(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Convert single Postman request to NOIV test"""
        
        if 'request' not in item:
            return None
        
        request = item['request']
        
        # Handle different URL formats
        url = request.get('url', '')
        if isinstance(url, dict):
            url = url.get('raw', '')
        
        # Extract method
        method = request.get('method', 'GET')
        
        # Extract headers
        headers = {}
        for header in request.get('header', []):
            if not header.get('disabled', False):
                headers[header['key']] = header['value']
        
        # Extract body
        body = None
        if 'body' in request and request['body'].get('mode') == 'raw':
            try:
                body = json.loads(request['body']['raw'])
            except:
                body = request['body']['raw']
        
        return {
            "name": item.get('name', f"{method} {url}"),
            "method": method,
            "url": url,
            "headers": headers,
            "body": body,
            "expected_status": 200,
            "description": f"Imported from Postman: {item.get('name', '')}"
        }

class PostmanExporter:
    """Export NOIV tests to Postman format"""
    
    def export_collection(self, suite_data: Dict[str, Any], output_file: Path):
        """Convert NOIV test suite to Postman collection"""
        
        collection = {
            "info": {
                "name": suite_data.get('name', 'NOIV Exported Tests'),
                "description": "Exported from NOIV CLI",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "item": []
        }
        
        # Convert each test
        for test in suite_data.get('tests', []):
            item = self._convert_noiv_test(test)
            collection['item'].append(item)
        
        # Save to file
        with open(output_file, 'w') as f:
            json.dump(collection, f, indent=2)
        
        return output_file
    
    def _convert_noiv_test(self, test: Dict[str, Any]) -> Dict[str, Any]:
        """Convert single NOIV test to Postman request"""
        
        item = {
            "name": test.get('name', 'Unnamed Test'),
            "request": {
                "method": test.get('method', 'GET'),
                "header": [],
                "url": {
                    "raw": test.get('url', ''),
                    "protocol": "https",
                    "host": test.get('url', '').split('//')[1].split('/')[0].split('.') if '//' in test.get('url', '') else [],
                    "path": test.get('url', '').split('//')[1].split('/')[1:] if '//' in test.get('url', '') else []
                }
            }
        }
        
        # Add headers
        for key, value in test.get('headers', {}).items():
            item['request']['header'].append({
                "key": key,
                "value": value,
                "type": "text"
            })
        
        # Add body if present
        if test.get('body'):
            item['request']['body'] = {
                "mode": "raw",
                "raw": json.dumps(test['body']) if isinstance(test['body'], dict) else str(test['body']),
                "options": {
                    "raw": {
                        "language": "json"
                    }
                }
            }
        
        return item

class CurlImporter:
    """Import cURL commands to NOIV format"""
    
    def import_curl(self, curl_command: str) -> Dict[str, Any]:
        """Convert cURL command to NOIV test"""
        
        # Basic cURL parsing (can be enhanced)
        import shlex
        
        try:
            parts = shlex.split(curl_command)
        except:
            parts = curl_command.split()
        
        url = ""
        method = "GET"
        headers = {}
        body = None
        
        i = 0
        while i < len(parts):
            part = parts[i]
            
            if part == 'curl':
                i += 1
                continue
            elif part in ['-X', '--request']:
                method = parts[i + 1]
                i += 2
            elif part in ['-H', '--header']:
                header_line = parts[i + 1]
                if ':' in header_line:
                    key, value = header_line.split(':', 1)
                    headers[key.strip()] = value.strip()
                i += 2
            elif part in ['-d', '--data']:
                body_data = parts[i + 1]
                try:
                    body = json.loads(body_data)
                except:
                    body = body_data
                i += 2
            elif not part.startswith('-'):
                url = part.strip('\'"')
                i += 1
            else:
                i += 1
        
        return {
            "name": f"cURL {method} {url}",
            "method": method,
            "url": url,
            "headers": headers,
            "body": body,
            "expected_status": 200,
            "description": f"Imported from cURL command"
        }
