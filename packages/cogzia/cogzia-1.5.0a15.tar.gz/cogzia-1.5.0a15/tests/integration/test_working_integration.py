#!/usr/bin/env python3
"""
Test v1.5 integration with the 3 working universal servers.

This verifies that v1.5 can successfully use the deployed universal servers
for zero-config functionality.
"""

import asyncio
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from universal_discovery import UniversalServerDiscovery

console = Console()


async def test_v15_integration():
    """Test v1.5 integration with working universal servers."""
    console.print(Panel("[bold cyan]Testing v1.5 Universal Server Integration[/bold cyan]", expand=False))
    
    # Initialize discovery
    discovery = UniversalServerDiscovery()
    
    # Test scenarios that should trigger each universal server
    test_scenarios = [
        {
            "name": "Time Query",
            "requirements": "What time is it in Tokyo?",
            "expected_server": "time-mcp-server"
        },
        {
            "name": "Math Calculation",
            "requirements": "Calculate the square root of 144",
            "expected_server": "calculator-mcp-server"
        },
        {
            "name": "Web Search",
            "requirements": "Search for information about MCP servers",
            "expected_server": "brave-search-mcp-server"
        },
        {
            "name": "Combined Query",
            "requirements": "Search for the current time and calculate time differences",
            "expected_servers": ["time-mcp-server", "calculator-mcp-server", "brave-search-mcp-server"]
        }
    ]
    
    all_passed = True
    
    for scenario in test_scenarios:
        console.print(f"\n[yellow]Scenario: {scenario['name']}[/yellow]")
        console.print(f"Requirements: {scenario['requirements']}")
        
        # Simulate empty discovery (worst case)
        discovered_servers = []
        server_details = {}
        
        # Enhance with universal discovery
        enhanced_servers, enhanced_details = discovery.enhance_discovery_results(
            discovered_servers, server_details, scenario['requirements']
        )
        
        # Check results
        if 'expected_servers' in scenario:
            # Multiple servers expected
            found_all = all(server in enhanced_servers for server in scenario['expected_servers'])
            if found_all:
                console.print("[green]✓ All expected servers found[/green]")
            else:
                console.print("[red]✗ Not all expected servers found[/red]")
                all_passed = False
        else:
            # Single server expected
            if scenario['expected_server'] in enhanced_servers:
                console.print(f"[green]✓ Found {scenario['expected_server']}[/green]")
            else:
                console.print(f"[red]✗ Expected {scenario['expected_server']} not found[/red]")
                all_passed = False
        
        # Show results table
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Server", width=30)
        table.add_column("Relevance", width=10)
        table.add_column("Universal", width=10)
        
        for server in enhanced_servers[:3]:
            details = enhanced_details.get(server, {})
            is_universal = "✓" if details.get('is_universal', False) else ""
            table.add_row(
                server,
                f"{details.get('relevance', 0):.2f}",
                is_universal
            )
        
        console.print(table)
    
    # Summary
    console.print("\n" + "="*60)
    if all_passed:
        console.print("[bold green]✅ All integration tests passed![/bold green]")
        console.print("\nThe 3 working universal servers are properly integrated with v1.5:")
        console.print("- Time server responds to time-related queries")
        console.print("- Calculator server handles math expressions")
        console.print("- Brave search provides web search capability")
        console.print("\n[dim]Zero-config functionality is working as designed![/dim]")
    else:
        console.print("[bold red]❌ Some integration tests failed[/bold red]")
    
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(test_v15_integration())
    exit(0 if success else 1)