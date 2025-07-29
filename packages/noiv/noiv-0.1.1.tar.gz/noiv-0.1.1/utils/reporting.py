"""
Enhanced reporting system for NOIV
Generate beautiful HTML reports and comparisons
"""

import json
import time
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from rich.console import Console

console = Console()

class ReportGenerator:
    """Generate detailed test reports"""
    
    def __init__(self):
        self.reports_dir = Path.home() / ".noiv" / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_html_report(self, results: List[Dict[str, Any]], suite_name: str) -> Path:
        """Generate beautiful HTML report"""
        
        # Calculate statistics
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.get('success', False))
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        avg_response_time = sum(r.get('response_time_ms', 0) for r in results) / total_tests if total_tests > 0 else 0
        
        # Generate HTML
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NOIV Test Report - {suite_name}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .success {{ color: #28a745; }}
        .failure {{ color: #dc3545; }}
        .info {{ color: #17a2b8; }}
        .results-table {{
            margin: 0 30px 30px;
            border-collapse: collapse;
            width: calc(100% - 60px);
        }}
        .results-table th,
        .results-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        .results-table th {{
            background-color: #f8f9fa;
            font-weight: 600;
        }}
        .status-badge {{
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: bold;
            text-transform: uppercase;
        }}
        .status-success {{
            background-color: #d4edda;
            color: #155724;
        }}
        .status-failure {{
            background-color: #f8d7da;
            color: #721c24;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>NOIV Test Report</h1>
            <h2>{suite_name}</h2>
            <p>Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number info">{total_tests}</div>
                <div>Total Tests</div>
            </div>
            <div class="stat-card">
                <div class="stat-number success">{passed_tests}</div>
                <div>Passed</div>
            </div>
            <div class="stat-card">
                <div class="stat-number failure">{failed_tests}</div>
                <div>Failed</div>
            </div>
            <div class="stat-card">
                <div class="stat-number info">{success_rate:.1f}%</div>
                <div>Success Rate</div>
            </div>
            <div class="stat-card">
                <div class="stat-number info">{avg_response_time:.1f}ms</div>
                <div>Avg Response Time</div>
            </div>
        </div>
        
        <table class="results-table">
            <thead>
                <tr>
                    <th>Test Name</th>
                    <th>Method</th>
                    <th>URL</th>
                    <th>Status</th>
                    <th>Response Time</th>
                    <th>Result</th>
                </tr>
            </thead>
            <tbody>
"""
        
        # Add test results
        for result in results:
            status_class = "status-success" if result.get('success', False) else "status-failure"
            status_text = "PASS" if result.get('success', False) else "FAIL"
            
            html_content += f"""
                <tr>
                    <td>{result.get('name', 'Unknown')}</td>
                    <td>{result.get('method', 'GET')}</td>
                    <td>{result.get('url', '')}</td>
                    <td>{result.get('status_code', 'N/A')}</td>
                    <td>{result.get('response_time_ms', 0):.1f}ms</td>
                    <td><span class="status-badge {status_class}">{status_text}</span></td>
                </tr>
"""
        
        html_content += """
            </tbody>
        </table>
    </div>
</body>
</html>
"""
        
        # Save report
        timestamp = int(time.time())
        report_file = self.reports_dir / f"{suite_name}_{timestamp}.html"
        
        with open(report_file, 'w') as f:
            f.write(html_content)
        
        return report_file
    
    def compare_test_runs(self, run1_file: Path, run2_file: Path) -> Dict[str, Any]:
        """Compare two test runs for regressions"""
        
        with open(run1_file, 'r') as f:
            run1_data = json.load(f)
        
        with open(run2_file, 'r') as f:
            run2_data = json.load(f)
        
        run1_results = {r['name']: r for r in run1_data['results']}
        run2_results = {r['name']: r for r in run2_data['results']}
        
        comparison = {
            "run1": {
                "timestamp": run1_data['timestamp'],
                "total": len(run1_data['results']),
                "passed": sum(1 for r in run1_data['results'] if r['success'])
            },
            "run2": {
                "timestamp": run2_data['timestamp'],
                "total": len(run2_data['results']),
                "passed": sum(1 for r in run2_data['results'] if r['success'])
            },
            "new_failures": [],
            "fixed_tests": [],
            "performance_regressions": [],
            "performance_improvements": []
        }
        
        # Find new failures and fixes
        for test_name in set(run1_results.keys()) | set(run2_results.keys()):
            r1 = run1_results.get(test_name)
            r2 = run2_results.get(test_name)
            
            if r1 and r2:
                # Test exists in both runs
                if r1['success'] and not r2['success']:
                    comparison['new_failures'].append(test_name)
                elif not r1['success'] and r2['success']:
                    comparison['fixed_tests'].append(test_name)
                
                # Performance comparison
                if r1.get('response_time_ms') and r2.get('response_time_ms'):
                    r1_time = r1['response_time_ms']
                    r2_time = r2['response_time_ms']
                    
                    if r2_time > r1_time * 1.5:  # 50% slower
                        comparison['performance_regressions'].append({
                            'test': test_name,
                            'old_time': r1_time,
                            'new_time': r2_time,
                            'change_percent': ((r2_time - r1_time) / r1_time) * 100
                        })
                    elif r2_time < r1_time * 0.8:  # 20% faster
                        comparison['performance_improvements'].append({
                            'test': test_name,
                            'old_time': r1_time,
                            'new_time': r2_time,
                            'change_percent': ((r1_time - r2_time) / r1_time) * 100
                        })
        
        return comparison
    
    def generate_trend_report(self, suite_name: str, days: int = 7) -> Dict[str, Any]:
        """Generate trend analysis for recent test runs"""
        
        history_dir = Path.home() / ".noiv" / "history"
        history_files = list(history_dir.glob(f"{suite_name}_*.json"))
        
        # Sort by timestamp (newest first)
        history_files.sort(key=lambda x: int(x.stem.split('_')[-1]), reverse=True)
        
        # Take last N days
        recent_runs = []
        current_time = time.time()
        
        for file in history_files[:days]:
            try:
                timestamp = int(file.stem.split('_')[-1])
                if current_time - timestamp <= days * 24 * 3600:  # Within N days
                    with open(file, 'r') as f:
                        data = json.load(f)
                        recent_runs.append({
                            'timestamp': timestamp,
                            'results': data['results']
                        })
            except:
                continue
        
        if not recent_runs:
            return {"error": "No recent test runs found"}
        
        # Calculate trends
        trend_data = {
            "runs": len(recent_runs),
            "success_rates": [],
            "avg_response_times": [],
            "test_counts": []
        }
        
        for run in recent_runs:
            results = run['results']
            total = len(results)
            passed = sum(1 for r in results if r['success'])
            avg_time = sum(r.get('response_time_ms', 0) for r in results) / total if total > 0 else 0
            
            trend_data["success_rates"].append({
                'timestamp': run['timestamp'],
                'rate': (passed / total * 100) if total > 0 else 0
            })
            trend_data["avg_response_times"].append({
                'timestamp': run['timestamp'],
                'time': avg_time
            })
            trend_data["test_counts"].append({
                'timestamp': run['timestamp'],
                'count': total
            })
        
        return trend_data
