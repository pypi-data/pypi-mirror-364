"""
Configuration management for NOIV
Handle API keys, settings, and user preferences
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from rich.console import Console
from rich.prompt import Prompt, Confirm

console = Console()

class NOIVConfig:
    def __init__(self):
        self.config_dir = Path.home() / ".noiv"
        self.config_file = self.config_dir / "config.yaml"
        self.config_dir.mkdir(exist_ok=True)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f) or {}
        return {}
    
    def _save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)
    
    def set_api_key(self, api_key: str, validate: bool = True) -> bool:
        """Set and optionally validate Gemini API key"""
        if validate:
            from ai.gemini_client import validate_api_key
            if not validate_api_key(api_key):
                console.print("Invalid API key!")
                return False
        
        self.config['gemini_api_key'] = api_key
        self._save_config()
        
        # Also set environment variable for current session
        os.environ['GEMINI_API_KEY'] = api_key
        
        console.print("API key saved successfully!")
        return True
    
    def get_api_key(self) -> Optional[str]:
        """Get Gemini API key from config or environment"""
        # Return user's custom key if set, otherwise None (will use default in AI client)
        return self.config.get('gemini_api_key') or os.getenv('GEMINI_API_KEY')
    
    def show_config(self):
        """Display current configuration"""
        from rich.table import Table
        
        table = Table(title="NOIV Configuration")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")
        
        api_key = self.get_api_key()
        if api_key:
            masked_key = f"{api_key[:8]}...{api_key[-4:]}"
            table.add_row("Gemini API Key", f"Custom: {masked_key}")
        else:
            table.add_row("Gemini API Key", "[yellow]Using default (free tier)[/yellow]")
        
        table.add_row("Config Location", str(self.config_file))
        
        for key, value in self.config.items():
            if key != 'gemini_api_key':
                table.add_row(key, str(value))
        
        console.print(table)
    
    def interactive_setup(self):
        """Interactive setup for first-time users"""
        console.print("[bold cyan]Welcome to NOIV Setup![/bold cyan]")
        console.print("Let's configure your API testing environment.\n")
        
        # API Key setup (now optional)
        console.print("[dim]NOIV includes a free tier with built-in AI access.[/dim]")
        console.print("[dim]You can optionally set your own Gemini API key for higher usage limits.[/dim]\n")
        
        if Confirm.ask("Do you want to set your own Gemini API key? (optional)", default=False):
            console.print("Get one free at: https://makersuite.google.com/app/apikey")
            api_key = Prompt.ask("Enter your Gemini API key", password=True)
            self.set_api_key(api_key)
        else:
            console.print("Using built-in AI access for free tier usage.")
        
        # Default settings
        self.config.setdefault('default_timeout', 30)
        self.config.setdefault('parallel_requests', 5)
        self.config.setdefault('save_history', True)
        
        self._save_config()
        console.print("\nSetup complete! Try: [cyan]noiv quick https://api.github.com/users[/cyan]")

# Global config instance
config = NOIVConfig()
