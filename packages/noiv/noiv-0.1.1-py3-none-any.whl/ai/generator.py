"""
AI Test Generator - The Revolutionary Test Creation Engine

This is the CORE AI that makes NOIV magical while maintaining developer trust.
Key principles:
1. Full transparency - explain every decision
2. Conservative defaults - build trust first
3. Interactive refinement - developers stay in control
4. Multi-modal generation - endpoints, natural language, enhancements
"""

import json
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import httpx
import google.generativeai as genai
from rich.console import Console

from ..models import TestSuite, TestCase, HTTPMethod, TestStatus
from ..config import Config

console = Console()


@dataclass
class ProbeResult:
    """Results from endpoint probing"""
    url: str
    status_code: int
    response_time: float
    content_type: str
    auth_required: bool
    has_pagination: bool
    response_sample: Dict[str, Any]
    headers: Dict[str, str]
    response_size: int


class AITestGenerator:
    """
    The revolutionary AI test generator that developers actually trust
    """
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        
        # Initialize Gemini (with proper error handling)
        if self.config.ai.api_key:
            genai.configure(api_key=self.config.ai.api_key)
            self.model = genai.GenerativeModel(self.config.ai.model)
        else:
            console.print("⚠️ [yellow]No AI API key configured. AI features disabled.[/yellow]")
            self.model = None
    
    async def generate_from_endpoint(
        self, 
        url: str, 
        probe_result: ProbeResult,
        conservative: bool = False,
        show_reasoning: bool = True
    ) -> TestSuite:
        """
        Generate tests from a single endpoint analysis
        
        REVOLUTIONARY APPROACH:
        1. Analyze real API response (technical analysis)
        2. Generate context-aware test scenarios (AI analysis)  
        3. Provide full reasoning for each test (transparency)
        4. Conservative mode for trust-building
        """
        
        console.print("🧠 [bold blue]AI analyzing endpoint patterns...[/bold blue]")
        
        # Build context for AI
        context = self._build_endpoint_context(url, probe_result)
        
        # Generate tests with AI
        if self.model:
            test_scenarios = await self._generate_ai_scenarios(
                context, 
                conservative=conservative,
                show_reasoning=show_reasoning
            )
        else:
            # Fallback to rule-based generation
            test_scenarios = self._generate_rule_based_scenarios(context, conservative)
        
        # Convert to TestSuite
        test_suite = TestSuite(
            name=f"Generated tests for {url}",
            tests=test_scenarios,
            metadata={
                "generated_from": "endpoint",
                "source_url": url,
                "probe_results": probe_result.__dict__,
                "ai_generated": self.model is not None,
                "conservative_mode": conservative
            },
            created_by="ai" if self.model else "rules"
        )
        
        return test_suite
    
    async def generate_from_natural_language(
        self,
        description: str,
        base_url: Optional[str] = None,
        show_reasoning: bool = True
    ) -> TestSuite:
        """
        Generate tests from natural language descriptions
        
        EXAMPLES:
        "Test user authentication and profile management"
        "Check if pagination works correctly" 
        "Verify all POST endpoints handle rate limiting"
        """
        
        console.print("🗣️ [bold blue]AI interpreting natural language...[/bold blue]")
        
        if not self.model:
            raise ValueError("AI model required for natural language generation. Please configure API key.")
        
        # Build natural language prompt
        prompt = self._build_natural_language_prompt(description, base_url)
        
        # Generate with AI
        response = await self._call_ai_model(prompt)
        test_scenarios = self._parse_ai_response(response, show_reasoning=show_reasoning)
        
        test_suite = TestSuite(
            name=f"Tests from: {description[:50]}...",
            tests=test_scenarios,
            metadata={
                "generated_from": "natural_language",
                "description": description,
                "base_url": base_url,
                "ai_generated": True
            },
            created_by="ai"
        )
        
        return test_suite
    
    def enhance_test_suite(
        self,
        original_suite: TestSuite,
        focus: Optional[str] = None,
        conservative: bool = True
    ) -> TestSuite:
        """
        Enhance existing test suites with AI suggestions
        
        PERFECT for stubborn developers:
        - Respects existing work
        - Only adds improvements
        - Shows what's being changed
        - Conservative by default
        """
        
        console.print("🔧 [bold blue]AI analyzing existing tests for improvements...[/bold blue]")
        
        if not self.model:
            # Rule-based enhancements
            return self._enhance_rule_based(original_suite, focus, conservative)
        
        # AI-powered enhancements
        enhancement_prompt = self._build_enhancement_prompt(original_suite, focus, conservative)
        
        # Get AI suggestions
        import asyncio
        response = asyncio.run(self._call_ai_model(enhancement_prompt))
        new_tests = self._parse_enhancement_response(response, original_suite)
        
        # Create enhanced suite
        enhanced_suite = TestSuite(
            name=f"{original_suite.name} (Enhanced)",
            tests=original_suite.tests + new_tests,
            metadata={
                **original_suite.metadata,
                "enhanced_by": "ai",
                "enhancement_focus": focus,
                "conservative_enhancement": conservative,
                "original_test_count": len(original_suite.tests),
                "added_test_count": len(new_tests)
            },
            created_by="hybrid"  # Human + AI
        )
        
        return enhanced_suite
    
    def _build_endpoint_context(self, url: str, probe_result: ProbeResult) -> Dict[str, Any]:
        """Build rich context from endpoint analysis"""
        
        context = {
            "url": url,
            "method": "GET",  # Starting with GET
            "status_code": probe_result.status_code,
            "response_time": probe_result.response_time,
            "content_type": probe_result.content_type,
            "auth_required": probe_result.auth_required,
            "has_pagination": probe_result.has_pagination,
            "response_sample": probe_result.response_sample,
            "response_size": probe_result.response_size
        }
        
        # Analyze URL patterns for intelligence
        context["url_patterns"] = self._analyze_url_patterns(url)
        
        # Analyze response structure
        context["response_analysis"] = self._analyze_response_structure(probe_result.response_sample)
        
        return context
    
    def _analyze_url_patterns(self, url: str) -> Dict[str, Any]:
        """Analyze URL for patterns that suggest test scenarios"""
        
        patterns = {
            "has_id_parameter": bool(re.search(r'/\d+/?$', url)),
            "suggests_crud": any(word in url.lower() for word in ['users', 'posts', 'items', 'products']),
            "api_version": bool(re.search(r'/v\d+/', url)),
            "suggests_pagination": any(word in url.lower() for word in ['list', 'search', 'users', 'posts']),
            "known_service": self._detect_known_service(url)
        }
        
        return patterns
    
    def _detect_known_service(self, url: str) -> Optional[str]:
        """Detect known API services for specialized testing"""
        
        known_services = {
            "github.com": "github",
            "api.stripe.com": "stripe", 
            "jsonplaceholder": "test_api",
            "httpbin.org": "test_api",
            "reqres.in": "test_api"
        }
        
        for domain, service in known_services.items():
            if domain in url:
                return service
        
        return None
    
    def _analyze_response_structure(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze response structure for test insights"""
        
        if not isinstance(response, dict):
            return {"type": "non_object", "testable": False}
        
        analysis = {
            "type": "object",
            "fields": list(response.keys()) if response else [],
            "field_types": {k: type(v).__name__ for k, v in response.items()} if response else {},
            "has_id": "id" in response or "userId" in response,
            "has_timestamps": any("time" in k.lower() or "date" in k.lower() for k in response.keys()),
            "has_nested_objects": any(isinstance(v, dict) for v in response.values()),
            "has_arrays": any(isinstance(v, list) for v in response.values()),
            "estimated_size": len(str(response))
        }
        
        return analysis
    
    async def _generate_ai_scenarios(
        self, 
        context: Dict[str, Any], 
        conservative: bool = False,
        show_reasoning: bool = True
    ) -> List[TestCase]:
        """Generate test scenarios using AI"""
        
        prompt = f"""
        You are an expert API testing specialist. Generate test cases for this endpoint:
        
        ENDPOINT ANALYSIS:
        URL: {context['url']}
        Status: {context['status_code']}
        Response Time: {context['response_time']}ms
        Content Type: {context['content_type']}
        Auth Required: {context['auth_required']}
        Has Pagination: {context['has_pagination']}
        
        URL PATTERNS: {json.dumps(context['url_patterns'], indent=2)}
        RESPONSE ANALYSIS: {json.dumps(context['response_analysis'], indent=2)}
        
        GENERATE {"3-5" if conservative else "8-12"} TEST CASES following these rules:
        
        1. ALWAYS include reasoning for each test case
        2. Cover happy path, edge cases, error scenarios
        3. {"Be conservative - focus on standard scenarios" if conservative else "Be comprehensive - include advanced scenarios"}
        4. Consider the detected patterns and response structure
        5. Generate realistic test scenarios based on the actual API
        
        OUTPUT FORMAT (JSON):
        {{
            "tests": [
                {{
                    "name": "Test name",
                    "method": "GET|POST|PUT|DELETE",
                    "url": "full URL with any modifications",
                    "expected_status": 200,
                    "reasoning": "Why this test is important and what it validates",
                    "headers": {{}},
                    "body": null
                }}
            ]
        }}
        
        Make tests realistic and valuable for the developer.
        """
        
        response = await self._call_ai_model(prompt)
        return self._parse_ai_response(response, show_reasoning=show_reasoning)
    
    def _generate_rule_based_scenarios(self, context: Dict[str, Any], conservative: bool) -> List[TestCase]:
        """Fallback rule-based test generation"""
        
        tests = []
        base_url = context['url']
        
        # Happy path test
        tests.append(TestCase(
            name="Happy Path - Valid Request",
            method=HTTPMethod.GET,
            url=base_url,
            expected_status=200,
            ai_reasoning="Basic functionality test - ensures endpoint responds correctly"
        ))
        
        # Error scenarios based on URL patterns
        if context['url_patterns']['has_id_parameter']:
            tests.append(TestCase(
                name="Invalid ID - Should Return 404",
                method=HTTPMethod.GET,
                url=re.sub(r'/\d+/?$', '/99999', base_url),
                expected_status=404,
                ai_reasoning="Testing error handling with non-existent resource ID"
            ))
        
        if not conservative:
            # Add more comprehensive tests
            tests.append(TestCase(
                name="Malformed Request - Invalid Characters",
                method=HTTPMethod.GET,
                url=base_url.replace('/', '/%') if '/' in base_url else base_url + '/%',
                expected_status=400,
                ai_reasoning="Testing input validation and error handling"
            ))
        
        return tests
    
    async def _call_ai_model(self, prompt: str) -> str:
        """Call the AI model with proper error handling"""
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.config.ai.temperature,
                    max_output_tokens=self.config.ai.max_tokens,
                )
            )
            return response.text
        except Exception as e:
            console.print(f"⚠️ [yellow]AI generation failed: {str(e)}. Using fallback.[/yellow]")
            raise
    
    def _parse_ai_response(self, response: str, show_reasoning: bool = True) -> List[TestCase]:
        """Parse AI response into TestCase objects"""
        
        try:
            # Extract JSON from response
            json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find JSON directly
                json_str = response
            
            data = json.loads(json_str)
            tests = []
            
            for test_data in data.get('tests', []):
                test = TestCase(
                    name=test_data['name'],
                    method=HTTPMethod(test_data['method']),
                    url=test_data['url'],
                    expected_status=test_data.get('expected_status', 200),
                    headers=test_data.get('headers', {}),
                    body=test_data.get('body'),
                    ai_reasoning=test_data.get('reasoning') if show_reasoning else None
                )
                tests.append(test)
            
            return tests
            
        except Exception as e:
            console.print(f"⚠️ [yellow]Failed to parse AI response: {str(e)}[/yellow]")
            return []
    
    def _build_natural_language_prompt(self, description: str, base_url: Optional[str]) -> str:
        """Build prompt for natural language test generation"""
        
        prompt = f"""
        You are an expert API testing specialist. A developer wants to test:
        
        DESCRIPTION: "{description}"
        {"BASE URL: " + base_url if base_url else "NO SPECIFIC URL PROVIDED"}
        
        Generate a comprehensive test suite based on this natural language description.
        
        INSTRUCTIONS:
        1. Interpret the description and create realistic API test scenarios
        2. If no base URL provided, create example URLs that match the description
        3. Include proper HTTP methods (GET, POST, PUT, DELETE) as appropriate
        4. Provide clear reasoning for each test case
        5. Cover positive and negative test scenarios
        6. Make tests realistic and executable
        
        OUTPUT FORMAT (JSON):
        {{
            "tests": [
                {{
                    "name": "Test name",
                    "method": "GET|POST|PUT|DELETE",
                    "url": "complete URL",
                    "expected_status": 200,
                    "reasoning": "Why this test validates the user's requirement",
                    "headers": {{}},
                    "body": null
                }}
            ]
        }}
        """
        
        return prompt
    
    def _build_enhancement_prompt(self, suite: TestSuite, focus: Optional[str], conservative: bool) -> str:
        """Build prompt for enhancing existing tests"""
        
        existing_tests = "\n".join([
            f"- {test.name}: {test.method.value} {test.url}"
            for test in suite.tests
        ])
        
        prompt = f"""
        You are an expert API testing specialist. Enhance this existing test suite:
        
        EXISTING TESTS:
        {existing_tests}
        
        ENHANCEMENT FOCUS: {focus or "General improvements"}
        MODE: {"Conservative - only add essential tests" if conservative else "Comprehensive - add thorough coverage"}
        
        SUGGEST ADDITIONAL TESTS that:
        1. Fill gaps in the existing test coverage
        2. Focus on: {focus or "security, edge cases, error handling"}
        3. {"Add only 2-3 essential tests" if conservative else "Add comprehensive test scenarios"}
        4. Don't duplicate existing tests
        5. Provide clear reasoning for each suggestion
        
        OUTPUT FORMAT (JSON):
        {{
            "additional_tests": [
                {{
                    "name": "New test name",
                    "method": "GET|POST|PUT|DELETE", 
                    "url": "complete URL",
                    "expected_status": 200,
                    "reasoning": "Why this test improves the existing suite",
                    "headers": {{}},
                    "body": null
                }}
            ]
        }}
        """
        
        return prompt
    
    def _parse_enhancement_response(self, response: str, original_suite: TestSuite) -> List[TestCase]:
        """Parse enhancement suggestions"""
        
        try:
            json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = response
            
            data = json.loads(json_str)
            new_tests = []
            
            for test_data in data.get('additional_tests', []):
                test = TestCase(
                    name=test_data['name'],
                    method=HTTPMethod(test_data['method']),
                    url=test_data['url'],
                    expected_status=test_data.get('expected_status', 200),
                    headers=test_data.get('headers', {}),
                    body=test_data.get('body'),
                    ai_reasoning=test_data.get('reasoning')
                )
                new_tests.append(test)
            
            return new_tests
            
        except Exception as e:
            console.print(f"⚠️ [yellow]Failed to parse enhancement response: {str(e)}[/yellow]")
            return []
    
    def _enhance_rule_based(self, suite: TestSuite, focus: Optional[str], conservative: bool) -> TestSuite:
        """Rule-based enhancement fallback"""
        
        new_tests = []
        
        # Add basic security tests if not present
        if focus == "security" or not focus:
            security_test = TestCase(
                name="Security - SQL Injection Test",
                method=HTTPMethod.GET,
                url=suite.tests[0].url + "?id=1' OR '1'='1",
                expected_status=400,
                ai_reasoning="Testing for SQL injection vulnerabilities"
            )
            new_tests.append(security_test)
        
        # Enhanced suite
        return TestSuite(
            name=f"{suite.name} (Rule-Enhanced)",
            tests=suite.tests + new_tests,
            metadata={
                **suite.metadata,
                "enhanced_by": "rules",
                "enhancement_focus": focus
            },
            created_by="hybrid"
        )
