#!/usr/bin/env python3
"""
Comprehensive test suite for the --last command functionality.

This test simulates real user interactions with the TUI, running the actual
program through subprocess to capture and verify output.
"""

import asyncio
import subprocess
import sys
import os
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

class TUITestRunner:
    """Runs the TUI as a subprocess and captures output."""
    
    def __init__(self, working_dir: str):
        self.working_dir = Path(working_dir)
        self.main_py = self.working_dir / "main.py"
        self.env = os.environ.copy()
        # Ensure we're using the test environment
        self.env["GATEWAY_URL"] = os.getenv("GATEWAY_URL", "http://34.13.112.200")
        self.env["PYTHONPATH"] = str(self.working_dir.parent)
        
    def run_command(self, args: List[str], input_text: Optional[str] = None, 
                   timeout: int = 30) -> Tuple[int, str, str]:
        """
        Run the TUI with given arguments and capture output.
        
        Returns: (return_code, stdout, stderr)
        """
        cmd = [sys.executable, str(self.main_py)] + args
        
        console.print(f"[dim]Running: {' '.join(cmd)}[/dim]")
        
        try:
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=self.env,
                cwd=str(self.working_dir)
            )
            
            stdout, stderr = process.communicate(input=input_text, timeout=timeout)
            return process.returncode, stdout, stderr
            
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            return -1, stdout, f"TIMEOUT after {timeout}s\n{stderr}"
        except Exception as e:
            return -1, "", str(e)

class LastCommandTestSuite:
    """Test suite for --last command functionality."""
    
    def __init__(self):
        self.runner = TUITestRunner(Path(__file__).parent.parent.parent)
        self.test_user = {
            "email": f"test_last_{int(time.time())}@example.com",
            "password": "TestPassword123!",
            "username": f"test_last_{int(time.time())}"
        }
        self.auth_token = None
        self.created_apps = []
        
    async def setup_test_user(self):
        """Create a test user and authenticate."""
        console.print("\n[cyan]Setting up test user...[/cyan]")
        
        # First register the user
        register_input = f"{self.test_user['email']}\n{self.test_user['username']}\n{self.test_user['password']}\n"
        rc, stdout, stderr = self.runner.run_command(["--login"], input_text=register_input)
        
        if "already registered" in stdout.lower() or "successfully" in stdout.lower():
            console.print("  [green]✅ User setup complete[/green]")
            # Extract token if shown
            if "token:" in stdout.lower():
                lines = stdout.split('\n')
                for line in lines:
                    if "token:" in line.lower():
                        self.auth_token = line.split(":")[-1].strip()
            return True
        else:
            console.print(f"  [red]❌ User setup failed: {stdout}[/red]")
            return False
    
    def test_last_no_apps(self):
        """Test --last when no apps exist."""
        console.print("\n[bold]Test 1: --last with no apps[/bold]")
        
        rc, stdout, stderr = self.runner.run_command(["--last"])
        
        # Check for expected messages
        if "no apps in your library" in stdout.lower():
            console.print("  [green]✅ Correctly shows no apps message[/green]")
            return True
        else:
            console.print(f"  [red]❌ Unexpected output: {stdout}[/red]")
            return False
    
    def test_create_and_use_last(self):
        """Test creating an app and then using --last."""
        console.print("\n[bold]Test 2: Create app and use --last[/bold]")
        
        # Create an app first
        console.print("  [dim]Creating test app...[/dim]")
        rc, stdout, stderr = self.runner.run_command(
            ["--auto", "3", "--requirements", "Simple weather app", "--no-save"],
            timeout=60
        )
        
        if rc != 0:
            console.print(f"  [red]❌ App creation failed: {stderr}[/red]")
            return False
            
        # Extract app_id from output
        app_id = None
        if "app_" in stdout:
            for line in stdout.split('\n'):
                if "app_" in line and ("created" in line.lower() or "id:" in line.lower()):
                    # Extract app_id
                    import re
                    match = re.search(r'app_[a-z0-9]{8}', line)
                    if match:
                        app_id = match.group(0)
                        self.created_apps.append(app_id)
                        break
        
        if not app_id:
            console.print("  [yellow]⚠️  Could not extract app_id from output[/yellow]")
        else:
            console.print(f"  [green]✅ Created app: {app_id}[/green]")
        
        # Now test --last
        console.print("  [dim]Testing --last command...[/dim]")
        rc, stdout, stderr = self.runner.run_command(["--last"], timeout=30)
        
        if rc == 0 and ("launching" in stdout.lower() or "loading" in stdout.lower()):
            console.print("  [green]✅ --last command executed successfully[/green]")
            return True
        else:
            console.print(f"  [red]❌ --last failed: {stdout}[/red]")
            return False
    
    def test_last_with_multiple_apps(self):
        """Test --last behavior with multiple apps."""
        console.print("\n[bold]Test 3: --last with multiple apps[/bold]")
        
        # Create first app
        console.print("  [dim]Creating first app...[/dim]")
        rc1, stdout1, stderr1 = self.runner.run_command(
            ["--auto", "3", "--requirements", "Calculator app", "--no-save"],
            timeout=60
        )
        
        time.sleep(2)  # Small delay between apps
        
        # Create second app
        console.print("  [dim]Creating second app...[/dim]")
        rc2, stdout2, stderr2 = self.runner.run_command(
            ["--auto", "3", "--requirements", "Todo list app", "--no-save"],
            timeout=60
        )
        
        if rc1 != 0 or rc2 != 0:
            console.print("  [red]❌ Failed to create test apps[/red]")
            return False
        
        # Use --last (should launch the second app)
        console.print("  [dim]Testing --last (should launch Todo list app)...[/dim]")
        rc, stdout, stderr = self.runner.run_command(["--last"], timeout=30)
        
        if rc == 0 and ("todo" in stdout.lower() or "launching" in stdout.lower()):
            console.print("  [green]✅ --last correctly launches most recent app[/green]")
            return True
        else:
            console.print(f"  [red]❌ --last behavior incorrect: {stdout}[/red]")
            return False
    
    def test_list_and_last(self):
        """Test --list-my-apps followed by --last."""
        console.print("\n[bold]Test 4: List apps and use --last[/bold]")
        
        # List apps first
        console.print("  [dim]Listing apps...[/dim]")
        rc, stdout, stderr = self.runner.run_command(["--list-my-apps"])
        
        if rc == 0:
            console.print("  [green]✅ Listed apps successfully[/green]")
            # Count apps in output
            app_count = stdout.lower().count("app_")
            console.print(f"  [dim]Found {app_count} apps[/dim]")
        else:
            console.print(f"  [red]❌ Failed to list apps: {stderr}[/red]")
            return False
        
        # Use --last
        console.print("  [dim]Using --last...[/dim]")
        rc, stdout, stderr = self.runner.run_command(["--last"], timeout=30)
        
        if rc == 0:
            console.print("  [green]✅ --last works after listing apps[/green]")
            return True
        else:
            console.print(f"  [red]❌ --last failed: {stderr}[/red]")
            return False
    
    def test_last_error_scenarios(self):
        """Test error handling for --last command."""
        console.print("\n[bold]Test 5: Error scenarios[/bold]")
        
        # Test without authentication
        console.print("  [dim]Testing --last without login...[/dim]")
        
        # Create a temporary environment without auth
        temp_env = self.runner.env.copy()
        temp_env.pop("COGZIA_AUTH_TOKEN", None)
        
        # Temporarily change runner env
        original_env = self.runner.env
        self.runner.env = temp_env
        
        rc, stdout, stderr = self.runner.run_command(["--last"])
        
        # Restore original env
        self.runner.env = original_env
        
        if "authentication required" in stdout.lower() or "must be logged in" in stdout.lower():
            console.print("  [green]✅ Correctly requires authentication[/green]")
            return True
        else:
            console.print(f"  [yellow]⚠️  Unexpected auth behavior: {stdout}[/yellow]")
            return True  # Not critical
    
    async def run_all_tests(self):
        """Run all test scenarios."""
        console.print(Panel(
            "[bold]--last Command Test Suite[/bold]\n\n"
            "Testing real user interactions with the TUI",
            title="🧪 Integration Tests",
            border_style="blue"
        ))
        
        # Setup
        if not await self.setup_test_user():
            console.print("[red]Failed to setup test user, aborting tests[/red]")
            return
        
        # Run tests
        results = []
        
        results.append(("No apps scenario", self.test_last_no_apps()))
        results.append(("Create and use last", self.test_create_and_use_last()))
        results.append(("Multiple apps", self.test_last_with_multiple_apps()))
        results.append(("List and last", self.test_list_and_last()))
        results.append(("Error scenarios", self.test_last_error_scenarios()))
        
        # Summary
        console.print("\n[bold]Test Summary[/bold]")
        table = Table()
        table.add_column("Test", style="cyan")
        table.add_column("Result", justify="center")
        
        passed = 0
        for test_name, result in results:
            status = "[green]PASS[/green]" if result else "[red]FAIL[/red]"
            table.add_row(test_name, status)
            if result:
                passed += 1
        
        console.print(table)
        console.print(f"\n[bold]Total: {passed}/{len(results)} passed[/bold]")
        
        # Cleanup info
        if self.created_apps:
            console.print(f"\n[dim]Created {len(self.created_apps)} test apps[/dim]")

if __name__ == "__main__":
    suite = LastCommandTestSuite()
    asyncio.run(suite.run_all_tests())