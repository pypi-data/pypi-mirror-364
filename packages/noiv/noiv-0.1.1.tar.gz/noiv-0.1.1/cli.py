"""
NOIV CLI v0.1.0 - API Testing Tool
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import typer
import asyncio
import time
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

app = typer.Typer(
    help="NOIV - API Testing Tool",
    rich_markup_mode="rich"
)

console = Console()

# Create all sub-applications
test_app = typer.Typer(help="Test execution")
generate_app = typer.Typer(help="AI test generation")

# Add sub-applications to main app
app.add_typer(test_app, name="test")
app.add_typer(generate_app, name="generate")

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
        "[bold cyan]NOIV v0.1.0[/bold cyan]\n"
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
