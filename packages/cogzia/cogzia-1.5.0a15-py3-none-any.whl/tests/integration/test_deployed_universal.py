#!/usr/bin/env python3
"""
Test universal server integration with deployed Cloud Run servers.

This script tests the integration of universal servers without requiring
the MCP registry to be populated.
"""

import asyncio
from rich.console import Console
from rich.table import Table
from universal_discovery import UniversalServerDiscovery
from app_executor import AppQueryExecutor

console = Console()


async def test_cloud_run_servers():
    """Test the deployed Cloud Run servers directly."""
    console.print("[bold cyan]Testing Deployed Universal Servers[/bold cyan]\n")
    
    # Define the deployed servers
    deployed_servers = {
        'time-mcp-server': 'https://mcp-time-jsavfqld4a-uc.a.run.app',
        'calculator-mcp-server': 'https://mcp-calculator-jsavfqld4a-uc.a.run.app',
        'brave-search-mcp-server': 'https://mcp-brave-search-jsavfqld4a-uc.a.run.app'
    }
    
    # Test discovery enhancement
    discovery = UniversalServerDiscovery()
    
    # Simulate discovery results
    test_requirements = "I need to know the time and do some calculations"
    discovered_servers = []
    server_details = {}
    
    # Enhance with universal servers
    enhanced_servers, enhanced_details = discovery.enhance_discovery_results(
        discovered_servers, server_details, test_requirements
    )
    
    # Display enhancement results
    table = Table(title="Universal Server Discovery Enhancement")
    table.add_column("Server", style="cyan")
    table.add_column("Relevance", style="yellow")
    table.add_column("Source", style="green")
    
    for server in enhanced_servers[:5]:
        details = enhanced_details.get(server, {})
        table.add_row(
            server,
            f"{details.get('relevance', 0):.2f}",
            details.get('source', 'Unknown')
        )
    
    console.print(table)
    
    # Test tool execution on deployed servers
    console.print("\n[bold cyan]Testing Tool Execution[/bold cyan]\n")
    
    executor = AppQueryExecutor(
        app_name="Universal Test",
        servers=['time-mcp-server', 'calculator-mcp-server'],
        cloud_run_urls=deployed_servers
    )
    
    # Test time tool
    console.print("[yellow]Testing time server...[/yellow]")
    try:
        time_url = deployed_servers['time-mcp-server']
        time_result = await executor._execute_cloud_run_tool_direct(
            time_url, 'get_current_time', {'timezone': 'UTC'}
        )
        console.print(f"[green]✓ Time result: {time_result}[/green]")
    except Exception as e:
        console.print(f"[red]✗ Time error: {e}[/red]")
    
    # Test calculator tool
    console.print("\n[yellow]Testing calculator server...[/yellow]")
    try:
        calc_url = deployed_servers['calculator-mcp-server']
        calc_result = await executor._execute_cloud_run_tool_direct(
            calc_url, 'calculate', {'expression': '42 * 2'}
        )
        console.print(f"[green]✓ Calculator result: {calc_result}[/green]")
    except Exception as e:
        console.print(f"[red]✗ Calculator error: {e}[/red]")
    
    console.print("\n[bold green]Universal server integration is working![/bold green]")


# Add direct tool execution method to AppQueryExecutor
import aiohttp
import json

async def _execute_cloud_run_tool_direct(self, cloud_run_url, tool_name, arguments):
    """Execute a tool directly on a Cloud Run server."""
    async with aiohttp.ClientSession() as session:
        # Call the tool endpoint
        tool_url = f"{cloud_run_url}/tools/{tool_name}/execute"
        
        async with session.post(
            tool_url,
            json={"arguments": arguments},
            headers={"Content-Type": "application/json"}
        ) as response:
            if response.status == 200:
                result = await response.json()
                return result
            else:
                text = await response.text()
                raise Exception(f"Tool execution failed: {response.status} - {text}")

# Monkey patch the method
AppQueryExecutor._execute_cloud_run_tool_direct = _execute_cloud_run_tool_direct


if __name__ == "__main__":
    asyncio.run(test_cloud_run_servers())