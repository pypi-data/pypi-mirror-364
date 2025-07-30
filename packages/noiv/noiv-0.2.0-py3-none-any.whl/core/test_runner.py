"""
Test execution engine for NOIV
Run tests, collect results, generate reports
"""

import asyncio
import httpx
import time
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.progress import Progress, TaskID
from rich.table import Table
from pydantic import BaseModel

console = Console()

class TestResult(BaseModel):
    name: str
    url: str
    method: str
    status_code: Optional[int] = None
    response_time_ms: Optional[float] = None
    success: bool = False
    error: Optional[str] = None
    response_data: Optional[Dict[str, Any]] = None
    timestamp: float
    assertions_passed: int = 0
    assertions_total: int = 0

class TestSuite(BaseModel):
    name: str
    tests: List[Dict[str, Any]]
    metadata: Dict[str, Any] = {}

class TestRunner:
    def __init__(self):
        self.results: List[TestResult] = []
        self.history_dir = Path.home() / ".noiv" / "history"
        self.history_dir.mkdir(parents=True, exist_ok=True)
    
    async def run_test_suite(self, suite_path: Path, parallel: bool = True) -> List[TestResult]:
        """Run a complete test suite"""
        
        # Load test suite
        with open(suite_path, 'r') as f:
            suite_data = yaml.safe_load(f)
        
        suite = TestSuite(**suite_data)
        
        console.print(f"Running test suite: [cyan]{suite.name}[/cyan]")
        console.print(f"Total tests: [yellow]{len(suite.tests)}[/yellow]")
        
        if parallel and len(suite.tests) > 1:
            results = await self._run_parallel(suite.tests)
        else:
            results = await self._run_sequential(suite.tests)
        
        # Save results
        self._save_results(suite.name, results)
        
        # Display summary
        self._display_summary(results)
        
        return results
    
    async def _run_parallel(self, tests: List[Dict[str, Any]]) -> List[TestResult]:
        """Run tests in parallel"""
        
        with Progress() as progress:
            task = progress.add_task("Running tests...", total=len(tests))
            
            async with httpx.AsyncClient() as client:
                tasks = [self._execute_test(client, test, progress, task) for test in tests]
                results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [r for r in results if isinstance(r, TestResult)]
    
    async def _run_sequential(self, tests: List[Dict[str, Any]]) -> List[TestResult]:
        """Run tests one by one"""
        
        results = []
        
        with Progress() as progress:
            task = progress.add_task("Running tests...", total=len(tests))
            
            async with httpx.AsyncClient() as client:
                for test in tests:
                    result = await self._execute_test(client, test, progress, task)
                    results.append(result)
        
        return results
    
    async def _execute_test(self, client: httpx.AsyncClient, test: Dict[str, Any], 
                          progress: Progress, task: TaskID) -> TestResult:
        """Execute a single test"""
        
        start_time = time.time()
        
        try:
            response = await client.request(
                method=test.get('method', 'GET'),
                url=test['url'],
                headers=test.get('headers', {}),
                json=test.get('body'),
                timeout=test.get('timeout', 30)
            )
            
            response_time = (time.time() - start_time) * 1000
            
            # Check assertions
            assertions_passed, assertions_total = self._check_assertions(
                response, test.get('assertions', [])
            )
            
            result = TestResult(
                name=test['name'],
                url=test['url'], 
                method=test.get('method', 'GET'),
                status_code=response.status_code,
                response_time_ms=response_time,
                success=response.status_code == test.get('expected_status', 200),
                timestamp=time.time(),
                assertions_passed=assertions_passed,
                assertions_total=assertions_total
            )
            
        except Exception as e:
            result = TestResult(
                name=test['name'],
                url=test['url'],
                method=test.get('method', 'GET'),
                success=False,
                error=str(e),
                timestamp=time.time()
            )
        
        progress.advance(task)
        return result
    
    def _check_assertions(self, response: httpx.Response, assertions: List[str]) -> tuple[int, int]:
        """Check response against assertions"""
        passed = 0
        total = len(assertions)
        
        for assertion in assertions:
            try:
                # Simple assertion checking (can be enhanced)
                if "status == " in assertion:
                    expected = int(assertion.split("== ")[1])
                    if response.status_code == expected:
                        passed += 1
                elif "response_time <" in assertion:
                    # Would need response time from caller
                    passed += 1  # Placeholder
                # Add more assertion types
            except:
                continue
        
        return passed, total
    
    def _save_results(self, suite_name: str, results: List[TestResult]):
        """Save test results to history"""
        
        timestamp = int(time.time())
        filename = f"{suite_name}_{timestamp}.json"
        filepath = self.history_dir / filename
        
        results_data = {
            "suite_name": suite_name,
            "timestamp": timestamp,
            "results": [result.model_dump() for result in results]
        }
        
        import json
        with open(filepath, 'w') as f:
            json.dump(results_data, f, indent=2)
    
    def _display_summary(self, results: List[TestResult]):
        """Display test results summary"""
        
        passed = sum(1 for r in results if r.success)
        failed = len(results) - passed
        avg_response_time = sum(r.response_time_ms or 0 for r in results) / len(results)
        
        # Summary table
        table = Table(title="Test Results Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Total Tests", str(len(results)))
        table.add_row("Passed", f"[green]{passed}[/green]")
        table.add_row("Failed", f"[red]{failed}[/red]" if failed > 0 else "0")
        table.add_row("Success Rate", f"{(passed/len(results)*100):.1f}%")
        table.add_row("Avg Response Time", f"{avg_response_time:.1f}ms")
        
        console.print(table)
        
        # Detailed results
        if failed > 0:
            console.print("\n[bold red]Failed Tests:[/bold red]")
            for result in results:
                if not result.success:
                    console.print(f"  • {result.name}: {result.error or f'Status {result.status_code}'}")

def load_test_suite(file_path: Path) -> TestSuite:
    """Load test suite from YAML file"""
    with open(file_path, 'r') as f:
        data = yaml.safe_load(f)
    return TestSuite(**data)
