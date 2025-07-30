#!/usr/bin/env python3
"""
Manual test script for universal MCP server integration.

This script provides a quick way to test universal server discovery
and execution without running the full demo workflow.
"""

import asyncio
import os
import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services import ServiceDiscovery
from universal_discovery import UniversalServerDiscovery
from app_executor import AppQueryExecutor

console = Console()


async def test_discovery():
    """Test universal server discovery enhancement."""
    console.print(Panel("[bold cyan]Testing Universal Server Discovery[/bold cyan]", expand=False))
    
    service_discovery = ServiceDiscovery()
    universal_discovery = UniversalServerDiscovery()
    
    # Test different requirements
    test_cases = [
        "I need a calculator",
        "Show me the current time",
        "Generate some test data",
        "I want to calculate math and tell fortunes",
        "Help me with workflow automation"
    ]
    
    for requirements in test_cases:
        console.print(f"\n[yellow]Requirements:[/yellow] {requirements}")
        
        # Standard discovery
        discovered, details = await service_discovery.discover_servers(requirements)
        console.print(f"[dim]Standard discovery found {len(discovered)} servers[/dim]")
        
        # Enhanced discovery
        enhanced_servers, enhanced_details = universal_discovery.enhance_discovery_results(
            discovered, details, requirements
        )
        
        # Show results
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Server", style="cyan")
        table.add_column("Universal", style="green")
        table.add_column("Relevance", style="yellow")
        
        for server in enhanced_servers[:5]:
            is_universal = enhanced_details.get(server, {}).get('is_universal', False)
            relevance = enhanced_details.get(server, {}).get('relevance', 0)
            universal_mark = "✓" if is_universal else ""
            table.add_row(server, universal_mark, f"{relevance:.2f}")
        
        console.print(table)


async def test_execution():
    """Test executing tools from universal servers."""
    console.print(Panel("[bold cyan]Testing Universal Server Execution[/bold cyan]", expand=False))
    
    # Test with actual servers
    test_tools = [
        ("time-mcp-server", "get_current_time", {"timezone": "UTC"}),
        ("calculator-mcp-server", "calculate", {"expression": "42 * 2"}),
        ("fortune-mcp-server", "get_fortune", {}),
    ]
    
    executor = AppQueryExecutor(
        app_name="Universal Test",
        servers=[t[0] for t in test_tools],
        system_prompt="Test universal server tools"
    )
    
    for server, tool, args in test_tools:
        console.print(f"\n[yellow]Testing {server} - {tool}[/yellow]")
        try:
            result = await executor._execute_cloud_run_tool(tool, args)
            if hasattr(result, 'success') and result.success:
                console.print(f"[green]✓ Success[/green]")
                if hasattr(result, 'result'):
                    console.print(f"[dim]Result: {result.result}[/dim]")
            else:
                console.print(f"[red]✗ Failed[/red]")
                if hasattr(result, 'error'):
                    console.print(f"[dim]Error: {result.error}[/dim]")
        except Exception as e:
            console.print(f"[red]✗ Exception: {e}[/red]")


async def main():
    """Run manual tests."""
    try:
        # Test discovery
        await test_discovery()
        
        console.print("\n" + "="*60 + "\n")
        
        # Test execution (only if servers are deployed)
        console.print("[dim]Note: Execution tests require deployed Cloud Run servers[/dim]")
        
        # Uncomment to test execution
        # await test_execution()
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Test interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Test failed with error: {e}[/red]")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())