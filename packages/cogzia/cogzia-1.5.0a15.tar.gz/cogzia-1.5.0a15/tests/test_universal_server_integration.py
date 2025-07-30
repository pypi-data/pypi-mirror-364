#!/usr/bin/env python3
"""
Integration test for universal MCP server discovery and execution.

This test follows Cogzia's real-data testing philosophy:
- Uses actual MCP Registry
- Tests with real server connections
- No mocking allowed
- Must be non-interactive
"""

import asyncio
import os
import sys
from datetime import datetime
from typing import Dict, List, Tuple

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from dotenv import load_dotenv

# Import modules to test
from services import ServiceDiscovery
from universal_discovery import UniversalServerDiscovery
from demo_workflow import AIAppCreateDemo
from app_executor import AppExecutor

load_dotenv()

console = Console()


class UniversalServerIntegrationTest:
    """Test universal server integration with real services."""
    
    def __init__(self):
        self.service_discovery = ServiceDiscovery()
        self.universal_discovery = UniversalServerDiscovery()
        self.results = []
        self.test_count = 0
        self.pass_count = 0
        
    async def run_all_tests(self):
        """Run all integration tests."""
        console.print(Panel(
            "[bold cyan]Universal MCP Server Integration Test[/bold cyan]\n" +
            "Testing with real services - no mocking",
            expand=False
        ))
        
        # Test 1: Universal server discovery enhancement
        await self.test_universal_discovery_enhancement()
        
        # Test 2: Priority ordering of universal servers
        await self.test_universal_server_priority()
        
        # Test 3: Universal server metadata
        await self.test_universal_server_metadata()
        
        # Test 4: App creation with universal servers
        await self.test_app_creation_with_universal_servers()
        
        # Test 5: Tool execution with universal servers
        await self.test_universal_tool_execution()
        
        # Print results
        self.print_results()
        
        return self.pass_count == self.test_count
    
    async def test_universal_discovery_enhancement(self):
        """Test that universal discovery properly enhances results."""
        self.test_count += 1
        test_name = "Universal Discovery Enhancement"
        
        try:
            # Discover servers for a calculator requirement
            requirements = "I need a calculator app"
            discovered, details = await self.service_discovery.discover_servers(requirements)
            
            # Enhance with universal discovery
            enhanced_servers, enhanced_details = self.universal_discovery.enhance_discovery_results(
                discovered, details, requirements
            )
            
            # Check if calculator servers are marked as universal
            calculator_found = False
            universal_marked = False
            
            for server in enhanced_servers:
                if 'calculator' in server.lower():
                    calculator_found = True
                    if enhanced_details.get(server, {}).get('is_universal', False):
                        universal_marked = True
                        break
            
            if calculator_found and universal_marked:
                self.pass_count += 1
                self.results.append((test_name, "PASS", "Calculator marked as universal"))
            else:
                self.results.append((test_name, "FAIL", 
                    f"Calculator found: {calculator_found}, Universal marked: {universal_marked}"))
                
        except Exception as e:
            self.results.append((test_name, "ERROR", str(e)))
    
    async def test_universal_server_priority(self):
        """Test that universal servers get priority boost."""
        self.test_count += 1
        test_name = "Universal Server Priority"
        
        try:
            # Test with mixed requirements
            requirements = "I need web search and calculations"
            discovered, details = await self.service_discovery.discover_servers(requirements)
            
            # Enhance results
            enhanced_servers, enhanced_details = self.universal_discovery.enhance_discovery_results(
                discovered, details, requirements
            )
            
            # Check relevance scores
            universal_relevance = []
            non_universal_relevance = []
            
            for server, info in enhanced_details.items():
                relevance = info.get('relevance', 0)
                if info.get('is_universal', False):
                    universal_relevance.append(relevance)
                else:
                    non_universal_relevance.append(relevance)
            
            # Universal servers should have higher average relevance
            avg_universal = sum(universal_relevance) / len(universal_relevance) if universal_relevance else 0
            avg_non_universal = sum(non_universal_relevance) / len(non_universal_relevance) if non_universal_relevance else 0
            
            if avg_universal >= avg_non_universal:
                self.pass_count += 1
                self.results.append((test_name, "PASS", 
                    f"Universal avg: {avg_universal:.2f}, Non-universal avg: {avg_non_universal:.2f}"))
            else:
                self.results.append((test_name, "FAIL", 
                    f"Universal avg: {avg_universal:.2f} < Non-universal avg: {avg_non_universal:.2f}"))
                
        except Exception as e:
            self.results.append((test_name, "ERROR", str(e)))
    
    async def test_universal_server_metadata(self):
        """Test universal server metadata is correct."""
        self.test_count += 1
        test_name = "Universal Server Metadata"
        
        try:
            # Get universal server info
            universal_info = self.universal_discovery.get_universal_servers_info()
            
            # Check required fields
            required_fields = ['description', 'capabilities', 'examples']
            missing_fields = []
            
            for server_name, info in universal_info.items():
                for field in required_fields:
                    if field not in info:
                        missing_fields.append(f"{server_name}.{field}")
            
            if not missing_fields:
                self.pass_count += 1
                self.results.append((test_name, "PASS", 
                    f"All {len(universal_info)} servers have complete metadata"))
            else:
                self.results.append((test_name, "FAIL", 
                    f"Missing fields: {', '.join(missing_fields[:3])}..."))
                
        except Exception as e:
            self.results.append((test_name, "ERROR", str(e)))
    
    async def test_app_creation_with_universal_servers(self):
        """Test creating an app that uses universal servers."""
        self.test_count += 1
        test_name = "App Creation with Universal Servers"
        
        try:
            # Create demo instance with non-interactive config
            demo = AIAppCreateDemo(verbose=False)
            
            # Set up app config
            demo.app_config = {
                'name': 'Test Universal App',
                'requirements': 'Calculate time differences between timezones',
                'servers': []  # Will be populated by discovery
            }
            
            # Discover servers
            discovered, details = await demo.service_discovery.discover_servers(
                demo.app_config['requirements']
            )
            
            # Enhance with universal discovery
            enhanced_servers, enhanced_details = self.universal_discovery.enhance_discovery_results(
                discovered, details, demo.app_config['requirements']
            )
            
            # Select universal servers
            universal_servers = [
                server for server in enhanced_servers
                if enhanced_details.get(server, {}).get('is_universal', False)
            ]
            
            if len(universal_servers) >= 2:  # Should find time and calculator
                self.pass_count += 1
                self.results.append((test_name, "PASS", 
                    f"Found {len(universal_servers)} universal servers: {', '.join(universal_servers[:2])}"))
            else:
                self.results.append((test_name, "FAIL", 
                    f"Only found {len(universal_servers)} universal servers"))
                
        except Exception as e:
            self.results.append((test_name, "ERROR", str(e)))
    
    async def test_universal_tool_execution(self):
        """Test executing tools from universal servers."""
        self.test_count += 1
        test_name = "Universal Tool Execution"
        
        try:
            # Create app executor
            executor = AppExecutor(
                app_name="Test Universal Executor",
                servers=['time-mcp-server', 'calculator-mcp-server']
            )
            
            # Test time tool
            time_result = await executor._execute_cloud_run_tool(
                'get_current_time',
                {'timezone': 'UTC'}
            )
            
            # Test calculator tool
            calc_result = await executor._execute_cloud_run_tool(
                'calculate',
                {'expression': '2 + 2'}
            )
            
            # Check results
            time_success = hasattr(time_result, 'success') and time_result.success
            calc_success = hasattr(calc_result, 'success') and calc_result.success
            
            if time_success and calc_success:
                self.pass_count += 1
                self.results.append((test_name, "PASS", 
                    "Both time and calculator tools executed successfully"))
            else:
                self.results.append((test_name, "FAIL", 
                    f"Time: {time_success}, Calculator: {calc_success}"))
                
        except Exception as e:
            self.results.append((test_name, "ERROR", str(e)))
    
    def print_results(self):
        """Print test results in a table."""
        table = Table(title="Test Results", show_header=True, header_style="bold cyan")
        table.add_column("Test", style="cyan", width=40)
        table.add_column("Result", style="bold", width=10)
        table.add_column("Details", style="dim", width=50)
        
        for test_name, result, details in self.results:
            if result == "PASS":
                result_style = "[green]PASS[/green]"
            elif result == "FAIL":
                result_style = "[red]FAIL[/red]"
            else:
                result_style = "[yellow]ERROR[/yellow]"
            
            table.add_row(test_name, result_style, details)
        
        console.print(table)
        
        # Summary
        console.print(f"\n[bold]Summary:[/bold] {self.pass_count}/{self.test_count} tests passed")
        
        if self.pass_count == self.test_count:
            console.print("[bold green]✅ All tests passed![/bold green]")
        else:
            console.print(f"[bold red]❌ {self.test_count - self.pass_count} tests failed[/bold red]")


async def main():
    """Run the integration test."""
    test_runner = UniversalServerIntegrationTest()
    success = await test_runner.run_all_tests()
    
    # Exit with proper code for CI/CD
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())