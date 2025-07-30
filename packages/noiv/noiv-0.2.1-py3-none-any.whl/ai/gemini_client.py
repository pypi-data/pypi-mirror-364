"""
Gemini AI Integration for NOIV
Handles API key management and AI test generation

Free Tier: Uses built-in API key for immediate AI access
Advanced: Users can set custom API key for higher usage limits
"""

import os
import google.generativeai as genai
from typing import List, Dict, Any, Optional
from rich.console import Console
from pydantic import BaseModel

console = Console()

# Default API key for free tier users - enables AI features out of the box
DEFAULT_GEMINI_API_KEY = "AIzaSyCNTuRk9Oy05MzaqoeTIKujVWIhJ5oPHpo"

class AITestCase(BaseModel):
    name: str
    method: str
    url: str
    description: str
    expected_status: int = 200
    headers: Dict[str, str] = {}
    body: Optional[Dict[str, Any]] = None
    assertions: List[str] = []

class GeminiGenerator:
    def __init__(self, api_key: Optional[str] = None):
        # Priority order: provided key -> user config -> environment -> default
        from core.config_manager import config
        
        self.api_key = (
            api_key or 
            config.get_api_key() or 
            os.getenv("GEMINI_API_KEY") or 
            DEFAULT_GEMINI_API_KEY
        )
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def analyze_endpoint(self, url: str, sample_response: Dict[str, Any]) -> List[AITestCase]:
        """Generate intelligent test cases for an API endpoint"""
        
        prompt = f"""
        Analyze this API endpoint and generate comprehensive test cases:
        
        URL: {url}
        Sample Response: {sample_response}
        
        Generate test cases that cover:
        1. Happy path scenarios
        2. Edge cases (invalid IDs, missing params)
        3. Error scenarios (404, 400, 500)
        4. Security tests (SQL injection, XSS if applicable)
        5. Performance boundaries
        
        Return a JSON array of test cases with this structure:
        {{
            "name": "descriptive test name",
            "method": "GET/POST/PUT/DELETE",
            "url": "full URL with test data",
            "description": "what this test validates",
            "expected_status": 200,
            "headers": {{}},
            "body": null,
            "assertions": ["response.status == 200", "response.data.id exists"]
        }}
        
        Make tests realistic and practical for developers.
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Parse AI response and convert to test cases
            # TODO: Add proper JSON parsing and validation
            return self._parse_ai_response(response.text)
        except Exception as e:
            console.print(f"AI generation failed: {e}")
            return []
    
    def generate_from_description(self, description: str, base_url: str = "") -> List[AITestCase]:
        """Generate tests from natural language description"""
        
        prompt = f"""
        Generate API test cases based on this description:
        "{description}"
        
        Base URL: {base_url}
        
        Create realistic test scenarios that match the description.
        Return JSON array of test cases with proper HTTP methods, URLs, and assertions.
        Focus on practical, executable tests.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return self._parse_ai_response(response.text)
        except Exception as e:
            console.print(f"AI generation failed: {e}")
            return []
    
    def _parse_ai_response(self, response_text: str) -> List[AITestCase]:
        """Parse AI response into test cases"""
        # For demo purposes, return a sample test case
        # TODO: Implement proper AI response parsing
        
        sample_test = AITestCase(
            name="GET User Profile",
            method="GET", 
            url="https://api.github.com/users/octocat",
            description="Test basic user profile retrieval",
            expected_status=200,
            headers={"Accept": "application/json"},
            assertions=["Status code is 200", "Response contains login field"]
        )
        
        return [sample_test]

def validate_api_key(api_key: str) -> bool:
    """Validate if Gemini API key works"""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Say 'API key works' if you can read this.")
        return "API key works" in response.text
    except:
        return False
