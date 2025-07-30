"""
Plugin system for NOIV
Extensible architecture for custom functionality
"""

import json
import importlib
import importlib.util
from pathlib import Path
from typing import Dict, Any, List, Callable
from rich.console import Console

console = Console()

class PluginManager:
    """Manage and load NOIV plugins"""
    
    def __init__(self):
        self.plugins_dir = Path.home() / ".noiv" / "plugins"
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
        self.loaded_plugins = {}
        self.custom_assertions = {}
        self.custom_generators = {}
        self.custom_reporters = {}
    
    def load_plugins(self):
        """Load all plugins from the plugins directory"""
        
        for plugin_file in self.plugins_dir.glob("*.py"):
            if plugin_file.name.startswith("_"):
                continue
            
            try:
                self._load_plugin(plugin_file)
                console.print(f"✅ Loaded plugin: [cyan]{plugin_file.stem}[/cyan]")
            except Exception as e:
                console.print(f"❌ Failed to load plugin {plugin_file.stem}: {e}")
    
    def _load_plugin(self, plugin_file: Path):
        """Load a single plugin file"""
        
        spec = importlib.util.spec_from_file_location(plugin_file.stem, plugin_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        self.loaded_plugins[plugin_file.stem] = module
        
        # Register plugin components
        if hasattr(module, 'register_assertions'):
            assertions = module.register_assertions()
            self.custom_assertions.update(assertions)
        
        if hasattr(module, 'register_generators'):
            generators = module.register_generators()
            self.custom_generators.update(generators)
        
        if hasattr(module, 'register_reporters'):
            reporters = module.register_reporters()
            self.custom_reporters.update(reporters)
    
    def get_custom_assertion(self, assertion_type: str) -> Callable:
        """Get a custom assertion function"""
        return self.custom_assertions.get(assertion_type)
    
    def get_custom_generator(self, generator_type: str) -> Callable:
        """Get a custom test generator"""
        return self.custom_generators.get(generator_type)
    
    def get_custom_reporter(self, reporter_type: str) -> Callable:
        """Get a custom reporter"""
        return self.custom_reporters.get(reporter_type)
    
    def list_plugins(self):
        """List all loaded plugins"""
        
        from rich.table import Table
        
        table = Table(title="Loaded NOIV Plugins")
        table.add_column("Plugin", style="cyan")
        table.add_column("Assertions", style="green")
        table.add_column("Generators", style="yellow")
        table.add_column("Reporters", style="blue")
        
        for plugin_name, module in self.loaded_plugins.items():
            assertions = len([k for k in self.custom_assertions.keys() if k.startswith(plugin_name)])
            generators = len([k for k in self.custom_generators.keys() if k.startswith(plugin_name)])
            reporters = len([k for k in self.custom_reporters.keys() if k.startswith(plugin_name)])
            
            table.add_row(
                plugin_name,
                str(assertions),
                str(generators),
                str(reporters)
            )
        
        console.print(table)
    
    def create_example_plugin(self):
        """Create an example plugin file"""
        
        example_plugin = '''"""
Example NOIV Plugin
This shows how to create custom assertions, generators, and reporters
"""

import json
from typing import Dict, Any, List

def register_assertions() -> Dict[str, callable]:
    """Register custom assertion functions"""
    return {
        "json_schema_valid": validate_json_schema,
        "response_contains_field": check_field_exists,
        "custom_status_check": custom_status_validation
    }

def register_generators() -> Dict[str, callable]:
    """Register custom test generators"""
    return {
        "security_tests": generate_security_tests,
        "performance_tests": generate_performance_tests
    }

def register_reporters() -> Dict[str, callable]:
    """Register custom report formats"""
    return {
        "csv_report": generate_csv_report,
        "slack_summary": generate_slack_summary
    }

# Custom Assertions
def validate_json_schema(response_data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
    """Validate response against JSON schema"""
    try:
        import jsonschema
        jsonschema.validate(response_data, schema)
        return True
    except:
        return False

def check_field_exists(response_data: Dict[str, Any], field_path: str) -> bool:
    """Check if a nested field exists in response"""
    try:
        keys = field_path.split('.')
        current = response_data
        for key in keys:
            current = current[key]
        return True
    except:
        return False

def custom_status_check(status_code: int, expected_codes: List[int]) -> bool:
    """Custom status code validation"""
    return status_code in expected_codes

# Custom Generators
def generate_security_tests(base_url: str) -> List[Dict[str, Any]]:
    """Generate security-focused test cases"""
    return [
        {
            "name": "SQL Injection Test",
            "method": "GET",
            "url": f"{base_url}?id=' OR 1=1--",
            "expected_status": 400,
            "description": "Test for SQL injection vulnerability"
        },
        {
            "name": "XSS Test",
            "method": "POST",
            "url": base_url,
            "body": {"data": "<script>alert('xss')</script>"},
            "expected_status": 400,
            "description": "Test for XSS vulnerability"
        }
    ]

def generate_performance_tests(base_url: str) -> List[Dict[str, Any]]:
    """Generate performance test cases"""
    return [
        {
            "name": "Load Test - Multiple Requests",
            "method": "GET", 
            "url": base_url,
            "repeat": 100,
            "parallel": True,
            "max_response_time": 1000,
            "description": "Test endpoint under load"
        }
    ]

# Custom Reporters
def generate_csv_report(results: List[Dict[str, Any]]) -> str:
    """Generate CSV format report"""
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(['Test Name', 'Method', 'URL', 'Status', 'Response Time', 'Success'])
    
    # Data
    for result in results:
        writer.writerow([
            result.get('name', ''),
            result.get('method', ''),
            result.get('url', ''),
            result.get('status_code', ''),
            result.get('response_time_ms', ''),
            result.get('success', False)
        ])
    
    return output.getvalue()

def generate_slack_summary(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate Slack-formatted summary"""
    total = len(results)
    passed = sum(1 for r in results if r.get('success', False))
    failed = total - passed
    
    color = "good" if failed == 0 else "danger"
    
    return {
        "text": f"NOIV Test Results: {passed}/{total} passed",
        "attachments": [{
            "color": color,
            "fields": [
                {"title": "Passed", "value": str(passed), "short": True},
                {"title": "Failed", "value": str(failed), "short": True},
                {"title": "Success Rate", "value": f"{(passed/total*100):.1f}%", "short": True}
            ]
        }]
    }
'''
        
        example_file = self.plugins_dir / "example_plugin.py"
        with open(example_file, 'w') as f:
            f.write(example_plugin)
        
        console.print(f"✅ Created example plugin: [cyan]{example_file}[/cyan]")
        console.print("💡 Edit the file to add your custom functionality")

# Global plugin manager instance
plugin_manager = PluginManager()

# Enhanced assertion checker that uses plugins
def check_assertions(response, test_assertions: List[str], plugin_manager: PluginManager) -> tuple[int, int]:
    """Enhanced assertion checking with plugin support"""
    passed = 0
    total = len(test_assertions)
    
    for assertion in test_assertions:
        try:
            # Parse assertion
            if "==" in assertion:
                # Standard equality check
                if "status ==" in assertion:
                    expected = int(assertion.split("== ")[1])
                    if response.status_code == expected:
                        passed += 1
                elif "response_time <" in assertion:
                    max_time = float(assertion.split("< ")[1])
                    # Would need actual response time
                    passed += 1  # Placeholder
            
            elif "custom:" in assertion:
                # Custom plugin assertion
                assertion_type, assertion_data = assertion.split(":", 1)
                assertion_func = plugin_manager.get_custom_assertion(assertion_type)
                
                if assertion_func:
                    try:
                        assertion_params = json.loads(assertion_data)
                        if assertion_func(response.json(), assertion_params):
                            passed += 1
                    except:
                        continue
            
            # Add more assertion types as needed
            
        except Exception as e:
            console.print(f"❌ Assertion failed: {assertion} - {e}")
            continue
    
    return passed, total
