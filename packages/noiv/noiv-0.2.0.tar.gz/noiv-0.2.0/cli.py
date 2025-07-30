"""
NOIV CLI v0.2.0 - API Testing Tool
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import typer
import asyncio
import time
import json
from typing import Optional, List
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

app = typer.Typer(
    help="NOIV - API Testing Tool",
    rich_markup_mode="rich"
)

console = Console()

# Create all sub-applications
test_app = typer.Typer(help="Test execution")
generate_app = typer.Typer(help="AI test generation")
import_app = typer.Typer(help="Import from other tools")
report_app = typer.Typer(help="Generate reports")

# Add sub-applications to main app
app.add_typer(test_app, name="test")
app.add_typer(generate_app, name="generate")
app.add_typer(import_app, name="import")
app.add_typer(report_app, name="report")

@app.command()
def init(
    name: str = typer.Option("my-api-tests", help="Project name"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing config")
):
    """Initialize a new NOIV project"""
    
    console.print(Panel.fit(
        f"[bold cyan]Initializing NOIV Project[/bold cyan]\n"
        f"Name: [yellow]{name}[/yellow]",
        title="Setup"
    ))
    
    # Create basic config
    config_path = Path("noiv.yaml")
    if config_path.exists() and not force:
        console.print("Config already exists! Use --force to overwrite")
        return
    
    basic_config = f"""# NOIV Configuration
project_name: {name}
version: "1.0.0"

# AI Settings (optional)
ai:
  provider: gemini
  temperature: 0.7

# HTTP Settings  
http:
  timeout: 30
  retries: 3

# Test Settings
tests:
  parallel: true
  show_progress: true
"""
    
    config_path.write_text(basic_config)
    console.print(f"[bold green]Created {config_path}[/bold green]")
    
    console.print("\n[dim]Next steps:[/dim]")
    console.print("   [cyan]noiv quick https://api.example.com[/cyan]")
    console.print("   [cyan]noiv generate endpoint https://api.example.com[/cyan]")
    console.print("   [cyan]noiv test run http://api.example.com[/cyan]")

@app.command()
def quick(url: str = typer.Argument(..., help="API endpoint to test")):
    """Quick test any API endpoint"""
    
    console.print(Panel.fit(
        f"[bold cyan]Quick Testing[/bold cyan]\n"
        f"URL: [yellow]{url}[/yellow]",
        title="NOIV Test"
    ))
    
    try:
        from utils.http_client import quick_test
        
        with console.status("[bold green]Testing endpoint..."):
            result = quick_test(url)
        
        if result["success"]:
            console.print(f"[bold green]Success![/bold green]")
            console.print(f"Status: [green]{result['status_code']}[/green]")
            console.print(f"Time: [blue]{result['response_time_ms']}ms[/blue]")
            console.print(f"Type: [yellow]{result['content_type']}[/yellow]")
            
            # Offer to generate tests
            if Confirm.ask("\nGenerate AI test suite for this endpoint?", default=False):
                console.print("Use: [cyan]noiv generate endpoint " + url + "[/cyan]")
        else:
            console.print(f"[bold red]Failed![/bold red]")
            if "error" in result:
                console.print(f"Error: [red]{result['error']}[/red]")
    except ImportError as e:
        console.print(f"Import error: {e}")
        console.print("Make sure all dependencies are installed")

@app.command()
def version():
    """Show NOIV version"""
    console.print(Panel.fit(
        "[bold cyan]NOIV v0.2.0[/bold cyan]\n"
        "[dim]API Testing Tool[/dim]",
        title="Version Info"
    ))

# GENERATE COMMANDS
@generate_app.command("natural")
def generate_natural(
    description: str = typer.Argument(..., help="Natural language test description"),
    base_url: Optional[str] = typer.Option(None, help="Base API URL"),
    output: Optional[Path] = typer.Option(None, "-o", "--output", help="Output file")
):
    """Generate tests from natural language"""
    
    console.print(Panel.fit(
        f"[bold cyan]Natural Language Generation[/bold cyan]\n"
        f"Description: [yellow]{description}[/yellow]",
        title="AI Understanding"
    ))
    
    try:
        from ai.gemini_client import GeminiGenerator
        
        generator = GeminiGenerator()
        
        with console.status("AI interpreting your request..."):
            test_cases = generator.generate_from_description(description, base_url or "")
        
        if not test_cases:
            console.print("Failed to generate tests")
            return
        
        # Create and save suite
        suite_data = {
            "name": f"Tests: {description}",
            "tests": [case.model_dump() for case in test_cases]
        }
        
        output_path = output or Path("natural_tests.yaml")
        
        import yaml
        with open(output_path, 'w') as f:
            yaml.dump(suite_data, f, default_flow_style=False)
        
        console.print(f"Generated {len(test_cases)} test cases → [green]{output_path}[/green]")
        
    except ValueError as e:
        console.print(f"{e}")
        console.print("For higher usage limits, set your own API key: [cyan]noiv config set-api-key[/cyan]")
    except ImportError:
        console.print("AI modules not available")

# TEST COMMANDS
@test_app.command("run")
def run_tests(
    suite_file: Path = typer.Argument(..., help="Test suite YAML file"),
    parallel: bool = typer.Option(True, "--parallel/--sequential", help="Run tests in parallel")
):
    """Run test suite"""
    
    if not suite_file.exists():
        console.print(f"Test suite not found: {suite_file}")
        return
    
    try:
        asyncio.run(run_test_suite_async(suite_file, parallel))
    except ImportError:
        console.print("Test runner not available")

@test_app.command("history")
def test_history():
    """Show test execution history"""
    
    try:
        history_dir = Path.home() / ".noiv" / "history"
        
        if not history_dir.exists():
            console.print("No test history found")
            return
        
        history_files = list(history_dir.glob("*.json"))
        
        if not history_files:
            console.print("No test history found")
            return
        
        from rich.table import Table
        
        table = Table(title="Test History")
        table.add_column("Suite", style="cyan")
        table.add_column("Date", style="green") 
        table.add_column("Results", style="yellow")
        
        import json
        from datetime import datetime
        
        for file in sorted(history_files, reverse=True)[:10]:  # Last 10 runs
            with open(file, 'r') as f:
                data = json.load(f)
            
            timestamp = datetime.fromtimestamp(data['timestamp'])
            results = data['results']
            passed = sum(1 for r in results if r['success'])
            total = len(results)
            
            table.add_row(
                data['suite_name'],
                timestamp.strftime("%Y-%m-%d %H:%M"),
                f"{passed}/{total}"
            )
        
        console.print(table)
    except ImportError:
        console.print("History module not available")

# IMPORT COMMANDS
@import_app.command("postman")
def import_postman(
    file: Path = typer.Argument(..., help="Postman collection JSON file"),
    output: Optional[Path] = typer.Option(None, "-o", "--output", help="Output YAML file")
):
    """Import Postman collection to NOIV format"""
    
    if not file.exists():
        console.print(f"File not found: {file}")
        return
    
    try:
        from utils.importers import PostmanImporter
        
        importer = PostmanImporter()
        
        with console.status("Converting Postman collection..."):
            test_suite = importer.import_collection(file)
        
        # Save converted tests
        output_file = output or Path(f"imported_{file.stem}.yaml")
        
        import yaml
        with open(output_file, 'w') as f:
            yaml.dump(test_suite, f, default_flow_style=False)
        
        console.print(f"Imported {len(test_suite['tests'])} tests from Postman → [green]{output_file}[/green]")
        
        # Ask if user wants to run tests immediately
        if Confirm.ask("Run imported tests now?"):
            asyncio.run(run_test_suite_async(output_file))
            
    except ImportError:
        console.print("Import module not available")
    except Exception as e:
        console.print(f"Import failed: {e}")

@import_app.command("swagger")  
def import_swagger(
    url: str = typer.Argument(..., help="Swagger/OpenAPI URL or file"),
    output: Optional[Path] = typer.Option(None, "-o", "--output", help="Output YAML file")
):
    """Import Swagger/OpenAPI spec to NOIV format"""
    
    try:
        from utils.importers import SwaggerImporter
        
        importer = SwaggerImporter()
        
        with console.status("Converting OpenAPI spec..."):
            test_suite = importer.import_spec(url)
        
        output_file = output or Path("swagger_tests.yaml")
        
        import yaml
        with open(output_file, 'w') as f:
            yaml.dump(test_suite, f, default_flow_style=False)
        
        console.print(f"Generated {len(test_suite['tests'])} tests from OpenAPI → [green]{output_file}[/green]")
        
    except ImportError:
        console.print("Swagger import not available")
    except Exception as e:
        console.print(f"Import failed: {e}")

# REPORT COMMANDS  
@report_app.command("html")
def generate_html_report(
    results_file: Optional[Path] = typer.Argument(None, help="Test results JSON file"),
    output: Optional[Path] = typer.Option(None, "-o", "--output", help="Output HTML file")
):
    """Generate beautiful HTML report"""
    
    try:
        from utils.reporting import ReportGenerator
        
        # If no file specified, use latest results
        if not results_file:
            history_dir = Path.home() / ".noiv" / "history"
            if history_dir.exists():
                latest_file = max(history_dir.glob("*.json"), key=lambda f: f.stat().st_mtime)
                results_file = latest_file
            else:
                console.print("No test results found. Run some tests first!")
                return
        
        if not results_file.exists():
            console.print(f"Results file not found: {results_file}")
            return
        
        # Load results
        import json
        with open(results_file, 'r') as f:
            data = json.load(f)
        
        # Generate report
        generator = ReportGenerator()
        
        with console.status("Generating HTML report..."):
            report_path = generator.generate_html_report(
                data['results'], 
                data['suite_name']
            )
        
        console.print(f"HTML report generated → [green]{report_path}[/green]")
        
        # Ask to open report
        if Confirm.ask("Open report in browser?"):
            import webbrowser
            webbrowser.open(f"file://{report_path.absolute()}")
            
    except ImportError:
        console.print("Reporting module not available")
    except Exception as e:
        console.print(f"Report generation failed: {e}")

@report_app.command("compare")
def compare_reports(
    file1: Path = typer.Argument(..., help="First test results file"),
    file2: Path = typer.Argument(..., help="Second test results file"),
    output: Optional[Path] = typer.Option(None, "-o", "--output", help="Output comparison file")
):
    """Compare two test runs"""
    
    try:
        from utils.reporting import ReportGenerator
        
        generator = ReportGenerator()
        
        with console.status("Comparing test results..."):
            comparison_path = generator.compare_results(file1, file2, output)
        
        console.print(f"Comparison report → [green]{comparison_path}[/green]")
        
    except Exception as e:
        console.print(f"Comparison failed: {e}")

# INTERACTIVE TEST BUILDER
@app.command("build")
def build_test_interactive():
    """Interactive test builder - create tests step by step"""
    
    console.print(Panel("[bold blue]Interactive Test Builder[/bold blue]", expand=False))
    
    # Collect test details
    test_name = Prompt.ask("Test name")
    base_url = Prompt.ask("Base URL", default="https://api.example.com")
    
    tests = []
    
    while True:
        console.print(f"\n[bold]Creating test #{len(tests) + 1}[/bold]")
        
        # HTTP method
        method = Prompt.ask(
            "HTTP method", 
            choices=["GET", "POST", "PUT", "DELETE", "PATCH"],
            default="GET"
        )
        
        # Endpoint
        endpoint = Prompt.ask("Endpoint path", default="/")
        
        # Headers
        headers = {}
        if Confirm.ask("Add custom headers?", default=False):
            while True:
                header_name = Prompt.ask("Header name (or press Enter to finish)", default="")
                if not header_name:
                    break
                header_value = Prompt.ask(f"Value for {header_name}")
                headers[header_name] = header_value
        
        # Request body
        body = None
        if method in ["POST", "PUT", "PATCH"]:
            if Confirm.ask("Add request body?", default=False):
                body_type = Prompt.ask(
                    "Body type",
                    choices=["json", "form", "text"],
                    default="json"
                )
                
                if body_type == "json":
                    console.print("Enter JSON body (press Ctrl+D when done):")
                    body_lines = []
                    try:
                        while True:
                            line = input()
                            body_lines.append(line)
                    except EOFError:
                        body = "\n".join(body_lines)
                else:
                    body = Prompt.ask("Request body")
        
        # Expected response
        expected_status = IntPrompt.ask("Expected status code", default=200)
        
        # Response validations
        validations = []
        if Confirm.ask("Add response validations?", default=False):
            while True:
                validation_type = Prompt.ask(
                    "Validation type",
                    choices=["contains", "json_path", "header", "done"],
                    default="done"
                )
                
                if validation_type == "done":
                    break
                elif validation_type == "contains":
                    text = Prompt.ask("Text that response should contain")
                    validations.append({"type": "contains", "value": text})
                elif validation_type == "json_path":
                    path = Prompt.ask("JSON path (e.g., $.data.id)")
                    expected = Prompt.ask("Expected value")
                    validations.append({"type": "json_path", "path": path, "expected": expected})
                elif validation_type == "header":
                    header = Prompt.ask("Header name")
                    expected = Prompt.ask("Expected header value")
                    validations.append({"type": "header", "name": header, "expected": expected})
        
        # Build test
        test = {
            "name": f"{method} {endpoint}",
            "url": f"{base_url.rstrip('/')}{endpoint}",
            "method": method,
            "expected_status": expected_status
        }
        
        if headers:
            test["headers"] = headers
        if body:
            test["body"] = body
        if validations:
            test["validations"] = validations
        
        tests.append(test)
        
        if not Confirm.ask("Add another test?", default=True):
            break
    
    # Save test suite
    suite = {
        "name": test_name,
        "base_url": base_url,
        "tests": tests
    }
    
    filename = f"{test_name.lower().replace(' ', '_')}.yaml"
    
    import yaml
    with open(filename, 'w') as f:
        yaml.dump(suite, f, default_flow_style=False)
    
    console.print(f"\nTest suite saved as [green]{filename}[/green]")
    console.print(f"Created {len(tests)} tests")
    
    # Run tests immediately?
    if Confirm.ask("Run tests now?", default=True):
        asyncio.run(run_test_suite_async(Path(filename)))

# BENCHMARK COMMANDS
@app.command("benchmark")
def benchmark_endpoint(
    url: str = typer.Argument(..., help="URL to benchmark"),
    requests: int = typer.Option(100, "-n", "--requests", help="Number of requests"),
    concurrency: int = typer.Option(10, "-c", "--concurrency", help="Concurrent requests"),
    duration: Optional[int] = typer.Option(None, "-d", "--duration", help="Test duration in seconds")
):
    """Benchmark API endpoint performance"""
    
    console.print(Panel(f"[bold blue]Benchmarking {url}[/bold blue]", expand=False))
    
    asyncio.run(run_benchmark(url, requests, concurrency, duration))

async def run_benchmark(url: str, requests: int, concurrency: int, duration: Optional[int]):
    """Run performance benchmark"""
    
    from utils.http_client import HTTPClient
    
    client = HTTPClient()
    
    results = []
    start_time = time.time()
    
    # Progress tracking
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        expand=False
    ) as progress:
        
        task = progress.add_task("Running benchmark...", total=requests)
        
        # Semaphore for concurrency control
        semaphore = asyncio.Semaphore(concurrency)
        
        async def make_request():
            async with semaphore:
                req_start = time.time()
                try:
                    response = await client.get(url)
                    req_time = time.time() - req_start
                    results.append({
                        "status": response.status_code,
                        "time": req_time,
                        "success": 200 <= response.status_code < 300
                    })
                except Exception as e:
                    req_time = time.time() - req_start
                    results.append({
                        "status": 0,
                        "time": req_time,
                        "success": False,
                        "error": str(e)
                    })
                
                progress.advance(task)
        
        # Create tasks
        if duration:
            # Time-based benchmark
            tasks = []
            end_time = start_time + duration
            
            while time.time() < end_time:
                if len(tasks) < concurrency:
                    tasks.append(asyncio.create_task(make_request()))
                
                # Clean completed tasks
                tasks = [t for t in tasks if not t.done()]
                
                await asyncio.sleep(0.01)
            
            # Wait for remaining tasks
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
        else:
            # Request count-based benchmark
            tasks = [make_request() for _ in range(requests)]
            await asyncio.gather(*tasks, return_exceptions=True)
    
    # Calculate statistics
    total_time = time.time() - start_time
    successful_requests = [r for r in results if r["success"]]
    failed_requests = [r for r in results if not r["success"]]
    
    if successful_requests:
        response_times = [r["time"] * 1000 for r in successful_requests]  # Convert to ms
        avg_time = sum(response_times) / len(response_times)
        min_time = min(response_times)
        max_time = max(response_times)
        
        # Calculate percentiles
        sorted_times = sorted(response_times)
        p50 = sorted_times[len(sorted_times) // 2]
        p95 = sorted_times[int(len(sorted_times) * 0.95)]
        p99 = sorted_times[int(len(sorted_times) * 0.99)]
    else:
        avg_time = min_time = max_time = p50 = p95 = p99 = 0
    
    # Display results
    table = Table(title="Benchmark Results")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Total Requests", str(len(results)))
    table.add_row("Successful", str(len(successful_requests)))
    table.add_row("Failed", str(len(failed_requests)))
    table.add_row("Total Time", f"{total_time:.2f}s")
    table.add_row("Requests/sec", f"{len(results) / total_time:.2f}")
    
    if successful_requests:
        table.add_row("Avg Response", f"{avg_time:.2f}ms")
        table.add_row("Min Response", f"{min_time:.2f}ms")
        table.add_row("Max Response", f"{max_time:.2f}ms")
        table.add_row("50th Percentile", f"{p50:.2f}ms")
        table.add_row("95th Percentile", f"{p95:.2f}ms")
        table.add_row("99th Percentile", f"{p99:.2f}ms")
    
    console.print(table)
    
    # Save detailed results
    if Confirm.ask("Save detailed results?", default=False):
        timestamp = int(time.time())
        results_file = f"benchmark_{timestamp}.json"
        
        benchmark_data = {
            "url": url,
            "timestamp": timestamp,
            "config": {
                "requests": requests,
                "concurrency": concurrency,
                "duration": duration
            },
            "summary": {
                "total_requests": len(results),
                "successful": len(successful_requests),
                "failed": len(failed_requests),
                "total_time": total_time,
                "rps": len(results) / total_time,
                "avg_response_time": avg_time,
                "min_response_time": min_time,
                "max_response_time": max_time,
                "percentiles": {
                    "p50": p50,
                    "p95": p95, 
                    "p99": p99
                }
            },
            "detailed_results": results
        }
        
        with open(results_file, 'w') as f:
            json.dump(benchmark_data, f, indent=2)
        
        console.print(f"Results saved to [green]{results_file}[/green]")

# INTERACTIVE EXPLORER
@app.command("explore")  
def explore_apis():
    """Interactive API explorer - discover and test endpoints"""
    
    console.print(Panel("[bold blue]API Explorer[/bold blue]", expand=False))
    
    base_url = Prompt.ask("Base URL to explore", default="https://jsonplaceholder.typicode.com")
    
    # Common API patterns to try
    common_endpoints = [
        "/",
        "/health",
        "/status", 
        "/api",
        "/v1",
        "/docs",
        "/swagger",
        "/openapi.json",
        "/users",
        "/posts",
        "/products",
        "/items"
    ]
    
    console.print("\n[bold]Discovering endpoints...[/bold]")
    
    asyncio.run(explore_endpoints(base_url, common_endpoints))

async def explore_endpoints(base_url: str, endpoints: List[str]):
    """Explore and test common endpoints"""
    
    from utils.http_client import HTTPClient
    
    client = HTTPClient()
    results = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        expand=False
    ) as progress:
        
        task = progress.add_task("Exploring endpoints...", total=len(endpoints))
        
        for endpoint in endpoints:
            url = f"{base_url.rstrip('/')}{endpoint}"
            
            try:
                response = await client.get(url, timeout=5)
                results.append({
                    "endpoint": endpoint,
                    "status": response.status_code,
                    "success": 200 <= response.status_code < 300,
                    "content_type": response.headers.get("content-type", ""),
                    "size": len(response.text) if hasattr(response, 'text') else 0
                })
            except Exception as e:
                results.append({
                    "endpoint": endpoint,
                    "status": 0,
                    "success": False,
                    "error": str(e)
                })
            
            progress.advance(task)
    
    # Display discovered endpoints
    table = Table(title="Discovered Endpoints")
    table.add_column("Endpoint", style="cyan")
    table.add_column("Status", style="yellow")
    table.add_column("Type", style="green")
    table.add_column("Size", style="blue")
    
    successful_endpoints = []
    
    for result in results:
        if result["success"]:
            status_color = "green" if result["status"] == 200 else "yellow"
            table.add_row(
                result["endpoint"],
                f"[{status_color}]{result['status']}[/{status_color}]",
                result.get("content_type", "").split(";")[0],
                f"{result.get('size', 0)} bytes"
            )
            successful_endpoints.append(result)
        elif result.get("status", 0) != 0:
            table.add_row(
                result["endpoint"],
                f"[red]{result['status']}[/red]",
                "Error",
                "-"
            )
    
    console.print(table)
    
    if successful_endpoints:
        console.print(f"\n[green]Found {len(successful_endpoints)} accessible endpoints![/green]")
        
        if Confirm.ask("Generate test suite from discovered endpoints?", default=True):
            # Create test suite
            tests = []
            for result in successful_endpoints:
                tests.append({
                    "name": f"Test {result['endpoint']}",
                    "url": f"{base_url.rstrip('/')}{result['endpoint']}",
                    "method": "GET",
                    "expected_status": result["status"]
                })
            
            suite = {
                "name": f"Explored API Tests - {base_url}",
                "base_url": base_url,
                "tests": tests
            }
            
            filename = "explored_api_tests.yaml"
            import yaml
            with open(filename, 'w') as f:
                yaml.dump(suite, f, default_flow_style=False)
            
            console.print(f"Test suite saved as [green]{filename}[/green]")
            
            if Confirm.ask("Run the generated tests?", default=True):
                asyncio.run(run_test_suite_async(Path(filename)))
    else:
        console.print("[yellow]No accessible endpoints found. Try a different base URL.[/yellow]")

async def run_test_suite_async(suite_file: Path, parallel: bool = True):
    """Async wrapper for test suite execution"""
    try:
        from core.test_runner import TestRunner
        
        runner = TestRunner()
        await runner.run_test_suite(suite_file, parallel)
    except ImportError:
        console.print("Test runner module not available")

@app.callback()
def main():
    """
    NOIV - API Testing Tool with Built-in AI
    
    Essential commands:
    
    Setup & Quick Test:
    • noiv init - Setup new project
    • noiv quick URL - Quick test endpoint
    
    AI Test Generation (FREE - No API key needed):
    • noiv generate natural "description" - Natural language tests
    
    Test Execution:
    • noiv test run suite.yaml - Run test suite
    • noiv test history - View test history
    
    Get started: noiv init then noiv generate natural "Test user login"
    """
    pass

if __name__ == "__main__":
    app()
