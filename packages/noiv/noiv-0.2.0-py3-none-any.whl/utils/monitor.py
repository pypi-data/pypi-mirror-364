"""
Monitoring and scheduled testing for NOIV
Run tests automatically and send alerts
"""

import asyncio
import json
import time
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import signal
import sys
from rich.console import Console

console = Console()

class TestMonitor:
    """Monitor API endpoints and run scheduled tests"""
    
    def __init__(self):
        self.monitors_dir = Path.home() / ".noiv" / "monitors"
        self.monitors_dir.mkdir(parents=True, exist_ok=True)
        self.pid_file = self.monitors_dir / "monitor.pid"
        self.config_file = self.monitors_dir / "monitor_config.json"
        self.running = False
    
    def schedule_tests(self, suite_file: Path, schedule: str, alerts: Optional[Dict[str, str]] = None):
        """Schedule tests to run automatically"""
        
        config = self._load_monitor_config()
        
        monitor_id = f"monitor_{int(time.time())}"
        config[monitor_id] = {
            "suite_file": str(suite_file),
            "schedule": schedule,  # "5m", "1h", "daily", etc.
            "alerts": alerts or {},
            "created": time.time(),
            "last_run": None,
            "enabled": True
        }
        
        self._save_monitor_config(config)
        
        console.print(f"Scheduled monitoring for [cyan]{suite_file}[/cyan]")
        console.print(f"📅 Schedule: [yellow]{schedule}[/yellow]")
        
        if not self.is_running():
            console.print("Start monitoring with: [cyan]noiv monitor start[/cyan]")
    
    def start_monitoring(self, background: bool = True):
        """Start the monitoring daemon"""
        
        if self.is_running():
            console.print("Monitor is already running")
            return
        
        if background:
            # Start as background process
            process = subprocess.Popen([
                sys.executable, "-c",
                f"from monitor import TestMonitor; TestMonitor()._run_daemon()"
            ])
            
            # Save PID
            with open(self.pid_file, 'w') as f:
                f.write(str(process.pid))
            
            console.print(f"Monitor started in background (PID: {process.pid})")
        else:
            # Run in foreground
            self._run_daemon()
    
    def stop_monitoring(self):
        """Stop the monitoring daemon"""
        
        if not self.is_running():
            console.print("Monitor is not running")
            return
        
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            import os
            os.kill(pid, signal.SIGTERM)
            self.pid_file.unlink()
            
            console.print("Monitor stopped")
        except Exception as e:
            console.print(f"Failed to stop monitor: {e}")
    
    def is_running(self) -> bool:
        """Check if monitor daemon is running"""
        
        if not self.pid_file.exists():
            return False
        
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            import os
            os.kill(pid, 0)  # Check if process exists
            return True
        except:
            # PID file exists but process is dead
            if self.pid_file.exists():
                self.pid_file.unlink()
            return False
    
    def show_status(self):
        """Show monitoring status"""
        
        from rich.table import Table
        
        table = Table(title="NOIV Monitoring Status")
        table.add_column("Monitor", style="cyan")
        table.add_column("Suite", style="green")
        table.add_column("Schedule", style="yellow")
        table.add_column("Last Run", style="blue")
        table.add_column("Status", style="magenta")
        
        config = self._load_monitor_config()
        
        if not config:
            console.print("No monitors configured")
            return
        
        for monitor_id, monitor_config in config.items():
            last_run = "Never"
            if monitor_config.get('last_run'):
                last_run = datetime.fromtimestamp(monitor_config['last_run']).strftime("%Y-%m-%d %H:%M")
            
            status = "🟢 Running" if self.is_running() and monitor_config.get('enabled') else "🔴 Stopped"
            
            table.add_row(
                monitor_id,
                Path(monitor_config['suite_file']).name,
                monitor_config['schedule'],
                last_run,
                status
            )
        
        console.print(table)
        
        if self.is_running():
            console.print("\nMonitor daemon is running")
        else:
            console.print("\nMonitor daemon is stopped")
            console.print("Start with: [cyan]noiv monitor start[/cyan]")
    
    def _run_daemon(self):
        """Main daemon loop"""
        
        console.print("NOIV Monitor daemon starting...")
        
        # Set up signal handlers
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        signal.signal(signal.SIGINT, self._handle_shutdown)
        
        self.running = True
        
        try:
            while self.running:
                self._check_and_run_monitors()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            pass
        finally:
            console.print("🛑 Monitor daemon stopping...")
            if self.pid_file.exists():
                self.pid_file.unlink()
    
    def _check_and_run_monitors(self):
        """Check if any monitors need to run"""
        
        config = self._load_monitor_config()
        current_time = time.time()
        
        for monitor_id, monitor_config in config.items():
            if not monitor_config.get('enabled', True):
                continue
            
            if self._should_run_monitor(monitor_config, current_time):
                self._run_monitor(monitor_id, monitor_config)
    
    def _should_run_monitor(self, monitor_config: Dict[str, Any], current_time: float) -> bool:
        """Check if a monitor should run now"""
        
        last_run = monitor_config.get('last_run', 0)
        schedule = monitor_config.get('schedule', '5m')
        
        # Parse schedule string
        interval_seconds = self._parse_schedule(schedule)
        
        return (current_time - last_run) >= interval_seconds
    
    def _parse_schedule(self, schedule: str) -> int:
        """Parse schedule string to seconds"""
        
        schedule = schedule.lower().strip()
        
        if schedule.endswith('s'):
            return int(schedule[:-1])
        elif schedule.endswith('m'):
            return int(schedule[:-1]) * 60
        elif schedule.endswith('h'):
            return int(schedule[:-1]) * 3600
        elif schedule == 'daily':
            return 24 * 3600
        elif schedule == 'hourly':
            return 3600
        else:
            # Default to 5 minutes
            return 300
    
    def _run_monitor(self, monitor_id: str, monitor_config: Dict[str, Any]):
        """Run a single monitor"""
        
        suite_file = Path(monitor_config['suite_file'])
        
        if not suite_file.exists():
            console.print(f"Suite file not found: {suite_file}")
            return
        
        console.print(f"🔄 Running monitor: {monitor_id}")
        
        try:
            # Run the test suite
            from core.test_runner import TestRunner
            runner = TestRunner()
            
            # Use asyncio.run in a way that works with the daemon
            import asyncio
            results = asyncio.run(runner.run_test_suite(suite_file, parallel=True))
            
            # Update last run time
            config = self._load_monitor_config()
            config[monitor_id]['last_run'] = time.time()
            self._save_monitor_config(config)
            
            # Check for failures and send alerts
            failed_tests = [r for r in results if not r.success]
            if failed_tests:
                self._send_alerts(monitor_config['alerts'], failed_tests, suite_file.name)
            
            console.print(f"Monitor {monitor_id} completed: {len(results) - len(failed_tests)}/{len(results)} passed")
            
        except Exception as e:
            console.print(f"Monitor {monitor_id} failed: {e}")
    
    def _send_alerts(self, alerts: Dict[str, str], failed_tests: List[Any], suite_name: str):
        """Send alerts for failed tests"""
        
        if not alerts:
            return
        
        failure_summary = f"{len(failed_tests)} test(s) failed in {suite_name}"
        
        for alert_type, alert_config in alerts.items():
            try:
                if alert_type == 'slack':
                    self._send_slack_alert(alert_config, failure_summary, failed_tests)
                elif alert_type == 'discord':
                    self._send_discord_alert(alert_config, failure_summary, failed_tests)
                elif alert_type == 'webhook':
                    self._send_webhook_alert(alert_config, failure_summary, failed_tests)
            except Exception as e:
                console.print(f"Failed to send {alert_type} alert: {e}")
    
    def _send_slack_alert(self, webhook_url: str, summary: str, failed_tests: List[Any]):
        """Send Slack notification"""
        import httpx
        
        payload = {
            "text": f"🚨 NOIV Alert: {summary}",
            "attachments": [{
                "color": "danger",
                "fields": [
                    {
                        "title": "Failed Tests",
                        "value": "\\n".join(f"• {test.name}" for test in failed_tests[:5])
                    }
                ]
            }]
        }
        
        with httpx.Client() as client:
            client.post(webhook_url, json=payload)
    
    def _send_webhook_alert(self, webhook_url: str, summary: str, failed_tests: List[Any]):
        """Send generic webhook notification"""
        import httpx
        
        payload = {
            "alert_type": "test_failure",
            "summary": summary,
            "failed_tests": [{"name": test.name, "error": test.error} for test in failed_tests],
            "timestamp": time.time()
        }
        
        with httpx.Client() as client:
            client.post(webhook_url, json=payload)
    
    def _handle_shutdown(self, signum, frame):
        """Handle shutdown signals"""
        self.running = False
    
    def _load_monitor_config(self) -> Dict[str, Any]:
        """Load monitor configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_monitor_config(self, config: Dict[str, Any]):
        """Save monitor configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
