"""
NOIV Core Test Engine - The Fast & Reliable Execution Engine

This is the performance-focused test execution engine that makes NOIV 
blazingly fast compared to GUI tools like Postman.
"""

import asyncio
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import httpx
from rich.console import Console
from rich.progress import Progress, TaskID
from rich.table import Table
from rich.panel import Panel

from ..models import TestSuite, TestCase, TestResult, TestStatus, HTTPMethod
from ..config import Config

console = Console()


@dataclass
class TestSuiteResult:
    """Results from running a complete test suite"""
    suite_name: str
    total: int
    passed: int
    failed: int
    errors: int
    skipped: int
    total_time: float
    results: List[TestResult]
    
    @property
    def success_rate(self) -> float:
        if self.total == 0:
            return 0.0
        return (self.passed / self.total) * 100


class TestEngine:
    """
    The revolutionary test execution engine
    
    KEY FEATURES:
    - Async execution (10x faster than sequential)
    - Real-time progress tracking
    - Detailed result analysis
    - Resource management
    - Error resilience
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.client: Optional[httpx.AsyncClient] = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.client = httpx.AsyncClient(
            timeout=self.config.http.timeout,
            follow_redirects=self.config.http.follow_redirects,
            verify=self.config.http.verify_ssl,
            headers={"User-Agent": self.config.http.user_agent}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.client:
            await self.client.aclose()
    
    async def run_test_suite(
        self, 
        suite: TestSuite, 
        show_progress: bool = True,
        parallel: bool = True,
        max_concurrent: Optional[int] = None
    ) -> TestSuiteResult:
        """
        Run a complete test suite with real-time feedback
        
        PERFORMANCE FEATURES:
        - Parallel execution (configurable concurrency)
        - Real-time progress tracking
        - Early failure detection
        - Resource optimization
        """
        
        start_time = time.time()
        max_concurrent = max_concurrent or self.config.http.parallel_requests
        
        console.print(Panel.fit(
            f"🚀 [bold cyan]Running Test Suite: {suite.name}[/bold cyan]\n"
            f"Tests: [yellow]{len(suite.tests)}[/yellow] | "
            f"Parallel: [green]{parallel}[/green] | "
            f"Max Concurrent: [blue]{max_concurrent}[/blue]",
            title="Test Execution"
        ))
        
        if show_progress:
            progress = Progress()
            task = progress.add_task(f"Running {suite.name}", total=len(suite.tests))
            progress.start()
        
        try:
            if parallel:
                # Parallel execution with semaphore
                semaphore = asyncio.Semaphore(max_concurrent)
                tasks = [
                    self._run_test_with_semaphore(test, semaphore, progress, task if show_progress else None)
                    for test in suite.tests
                ]
                results = await asyncio.gather(*tasks, return_exceptions=True)
            else:
                # Sequential execution
                results = []
                for test in suite.tests:
                    result = await self.execute_test(test)
                    results.append(result)
                    if show_progress:
                        progress.update(task, advance=1)
        
        finally:
            if show_progress:
                progress.stop()
        
        # Process results
        test_results = [r for r in results if isinstance(r, TestResult)]
        exceptions = [r for r in results if isinstance(r, Exception)]
        
        # Handle exceptions as error results
        for i, exc in enumerate(exceptions):
            error_result = TestResult(
                test_case=suite.tests[i],
                status=TestStatus.ERROR,
                response_time=0,
                actual_status=0,
                error_message=str(exc)
            )
            test_results.append(error_result)
        
        total_time = time.time() - start_time
        
        # Calculate statistics
        passed = sum(1 for r in test_results if r.status == TestStatus.PASSED)
        failed = sum(1 for r in test_results if r.status == TestStatus.FAILED)
        errors = sum(1 for r in test_results if r.status == TestStatus.ERROR)
        skipped = sum(1 for r in test_results if r.status == TestStatus.SKIPPED)
        
        suite_result = TestSuiteResult(
            suite_name=suite.name,
            total=len(suite.tests),
            passed=passed,
            failed=failed,
            errors=errors,
            skipped=skipped,
            total_time=total_time,
            results=test_results
        )
        
        # Display results
        self._display_results(suite_result)
        
        return suite_result
    
    async def _run_test_with_semaphore(
        self, 
        test: TestCase, 
        semaphore: asyncio.Semaphore,
        progress: Optional[Progress] = None,
        task: Optional[TaskID] = None
    ) -> TestResult:
        """Run a single test with concurrency control"""
        
        async with semaphore:
            result = await self.execute_test(test)
            if progress and task:
                progress.update(task, advance=1)
            return result
    
    async def execute_test(self, test: TestCase) -> TestResult:
        """
        Execute a single test case
        
        COMPREHENSIVE TESTING:
        - HTTP request execution
        - Status code validation
        - Response time measurement
        - Error handling
        - Response analysis
        """
        
        start_time = time.time()
        
        try:
            # Prepare request
            request_kwargs = {
                'method': test.method.value,
                'url': test.url,
                'headers': test.headers or {}
            }
            
            # Add body if present
            if test.body:
                if isinstance(test.body, dict):
                    request_kwargs['json'] = test.body
                    request_kwargs['headers']['Content-Type'] = 'application/json'
                else:
                    request_kwargs['content'] = str(test.body)
            
            # Execute request
            response = await self.client.request(**request_kwargs)
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            # Analyze response
            try:
                response_data = response.json() if 'application/json' in response.headers.get('content-type', '') else None
            except:
                response_data = None
            
            # Determine test status
            status = TestStatus.PASSED if response.status_code == test.expected_status else TestStatus.FAILED
            
            return TestResult(
                test_case=test,
                status=status,
                response_time=response_time,
                actual_status=response.status_code,
                response_data=response_data,
                response_headers=dict(response.headers),
                response_size=len(response.content)
            )
            
        except asyncio.TimeoutError:
            response_time = (time.time() - start_time) * 1000
            return TestResult(
                test_case=test,
                status=TestStatus.ERROR,
                response_time=response_time,
                actual_status=408,  # Request Timeout
                error_message="Request timeout"
            )
        
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return TestResult(
                test_case=test,
                status=TestStatus.ERROR,
                response_time=response_time,
                actual_status=0,
                error_message=str(e)
            )
    
    def _display_results(self, suite_result: TestSuiteResult):
        """Display comprehensive test results"""
        
        # Summary
        console.print(f"\n🏁 [bold]Test Suite Complete: {suite_result.suite_name}[/bold]")
        console.print(f"⏱️  Total Time: [yellow]{suite_result.total_time:.2f}s[/yellow]")
        console.print(f"📊 Success Rate: [{'green' if suite_result.success_rate >= 80 else 'red'}]{suite_result.success_rate:.1f}%[/]")
        
        # Results table
        table = Table(title="📋 Test Results")
        table.add_column("Test", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Expected", style="blue")
        table.add_column("Actual", style="blue")
        table.add_column("Time (ms)", style="yellow")
        table.add_column("Details", style="dim")
        
        for result in suite_result.results:
            status_color = {
                TestStatus.PASSED: "green",
                TestStatus.FAILED: "red", 
                TestStatus.ERROR: "red",
                TestStatus.SKIPPED: "yellow"
            }.get(result.status, "white")
            
            status_symbol = {
                TestStatus.PASSED: "✅ PASS",
                TestStatus.FAILED: "❌ FAIL",
                TestStatus.ERROR: "💥 ERROR", 
                TestStatus.SKIPPED: "⏭️ SKIP"
            }.get(result.status, "❓ UNKNOWN")
            
            details = ""
            if result.status == TestStatus.FAILED:
                details = f"Expected {result.test_case.expected_status}, got {result.actual_status}"
            elif result.status == TestStatus.ERROR:
                details = result.error_message or "Unknown error"
            
            table.add_row(
                result.test_case.name,
                f"[{status_color}]{status_symbol}[/]",
                str(result.test_case.expected_status),
                str(result.actual_status),
                f"{result.response_time:.1f}",
                details
            )
        
        console.print(table)
        
        # Performance insights
        if suite_result.results:
            avg_time = sum(r.response_time for r in suite_result.results) / len(suite_result.results)
            slowest = max(suite_result.results, key=lambda r: r.response_time)
            fastest = min(suite_result.results, key=lambda r: r.response_time)
            
            console.print(f"\n⚡ [bold]Performance Insights:[/bold]")
            console.print(f"   Average Response Time: [yellow]{avg_time:.1f}ms[/yellow]")
            console.print(f"   Fastest: [green]{fastest.test_case.name} ({fastest.response_time:.1f}ms)[/green]")
            console.print(f"   Slowest: [red]{slowest.test_case.name} ({slowest.response_time:.1f}ms)[/red]")
        
        # Failure analysis
        failed_tests = [r for r in suite_result.results if r.status in [TestStatus.FAILED, TestStatus.ERROR]]
        if failed_tests:
            console.print(f"\n🔍 [bold red]Failure Analysis:[/bold red]")
            for result in failed_tests:
                console.print(f"   • {result.test_case.name}: {result.error_message or 'Status code mismatch'}")
    
    async def run_single_test(self, test: TestCase, verbose: bool = True) -> TestResult:
        """Run a single test with detailed output"""
        
        if verbose:
            console.print(f"🧪 [bold cyan]Running: {test.name}[/bold cyan]")
            console.print(f"   Method: [yellow]{test.method.value}[/yellow]")
            console.print(f"   URL: [blue]{test.url}[/blue]")
            if test.ai_reasoning:
                console.print(f"   💭 AI Reasoning: [dim]{test.ai_reasoning}[/dim]")
        
        result = await self.execute_test(test)
        
        if verbose:
            status_color = "green" if result.status == TestStatus.PASSED else "red"
            console.print(f"   Result: [{status_color}]{result.status.value.upper()}[/]")
            console.print(f"   Response Time: [yellow]{result.response_time:.1f}ms[/yellow]")
            
            if result.status != TestStatus.PASSED:
                console.print(f"   Error: [red]{result.error_message or 'Status code mismatch'}[/red]")
        
        return result


# Utility function for simple usage
async def run_tests(suite: TestSuite, config: Optional[Config] = None) -> TestSuiteResult:
    """Simple function to run tests with default config"""
    
    if config is None:
        from ..utils.file_handler import load_config
        config = load_config()
    
    async with TestEngine(config) as engine:
        return await engine.run_test_suite(suite)
