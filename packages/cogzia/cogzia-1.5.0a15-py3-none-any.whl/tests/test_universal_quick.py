#!/usr/bin/env python3
"""
Quick test for universal server discovery enhancement.

This test verifies the UniversalServerDiscovery logic without 
requiring full service infrastructure.
"""

import sys
import os
from rich.console import Console
from rich.table import Table

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from universal_discovery import UniversalServerDiscovery

console = Console()


def test_universal_enhancement():
    """Test universal server enhancement logic."""
    discovery = UniversalServerDiscovery()
    
    # Simulate discovery results
    test_cases = [
        {
            "requirements": "I need a calculator app",
            "discovered": ["openai-mcp-server", "calculator-mcp-server"],
            "details": {
                "openai-mcp-server": {"relevance": 0.8, "capabilities": ["llm"]},
                "calculator-mcp-server": {"relevance": 0.6, "capabilities": ["math"]}
            }
        },
        {
            "requirements": "Show me the time and do some math",
            "discovered": ["weather-mcp-server"],
            "details": {
                "weather-mcp-server": {"relevance": 0.4, "capabilities": ["weather"]}
            }
        },
        {
            "requirements": "Generate test data for my app",
            "discovered": [],
            "details": {}
        }
    ]
    
    for test in test_cases:
        console.print(f"\n[bold cyan]Test: {test['requirements']}[/bold cyan]")
        
        # Apply enhancement
        enhanced_servers, enhanced_details = discovery.enhance_discovery_results(
            test["discovered"].copy(),
            test["details"].copy(),
            test["requirements"]
        )
        
        # Display results
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Server", style="cyan", width=30)
        table.add_column("Universal", style="green", width=10)
        table.add_column("Relevance", style="yellow", width=10)
        table.add_column("Source", style="magenta", width=25)
        
        for server in enhanced_servers[:5]:
            details = enhanced_details.get(server, {})
            is_universal = "✓" if details.get('is_universal', False) else ""
            relevance = f"{details.get('relevance', 0):.2f}"
            source = details.get('source', 'Unknown')
            
            table.add_row(server, is_universal, relevance, source)
        
        console.print(table)
        
        # Summary
        universal_count = sum(1 for s in enhanced_servers 
                            if enhanced_details.get(s, {}).get('is_universal', False))
        console.print(f"[dim]Found {len(enhanced_servers)} servers, "
                     f"{universal_count} universal[/dim]")


def test_universal_info():
    """Test universal server information."""
    discovery = UniversalServerDiscovery()
    info = discovery.get_universal_servers_info()
    
    console.print("\n[bold cyan]Available Universal Servers:[/bold cyan]")
    
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Server", style="cyan", width=25)
    table.add_column("Description", style="white", width=45)
    table.add_column("Capabilities", style="green", width=30)
    
    for server_name, server_info in info.items():
        caps = ", ".join(server_info['capabilities'][:3])
        table.add_row(
            server_name,
            server_info['description'],
            caps
        )
    
    console.print(table)


if __name__ == "__main__":
    console.print("[bold]Universal Server Discovery Test[/bold]")
    console.print("=" * 60)
    
    # Test enhancement logic
    test_universal_enhancement()
    
    # Show available servers
    test_universal_info()
    
    console.print("\n[green]✓ Test completed successfully[/green]")