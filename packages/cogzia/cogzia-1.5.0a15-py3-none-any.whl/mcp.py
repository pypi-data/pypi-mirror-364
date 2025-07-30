#!/usr/bin/env python3
"""
Cloud-only MCP CLI for Cogzia Alpha v1.5.

This CLI connects exclusively to GCP-hosted MCP services. No local service fallbacks.
All operations go through the GCP gateway with proper authentication.

Created: 2025-07-22
Author: Claude Code
"""
import asyncio
import sys
import os
import argparse
import json
from typing import Optional, Dict, Any, List
from pathlib import Path

import httpx
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

# Import our config which has all the GCP endpoints
from config import (
    MCP_REGISTRY_URL, 
    MCP_SERVER_MANAGER_URL,
    DEFAULT_HEADERS,
    DEFAULT_TIMEOUT,
    GCP_ENABLED,
    GATEWAY_URL
)
from auth_manager import TUIAuthManager, UserContext

console = Console()


class CloudMCPClient:
    """Client for cloud-hosted MCP services."""
    
    def __init__(self, auth_token: Optional[str] = None):
        """
        Initialize the cloud MCP client.
        
        Args:
            auth_token: JWT token for authenticated requests
        """
        self.auth_token = auth_token
        self.headers = DEFAULT_HEADERS.copy()
        
        if auth_token:
            self.headers["Authorization"] = f"Bearer {auth_token}"
        
        self.client = httpx.AsyncClient(
            headers=self.headers,
            timeout=DEFAULT_TIMEOUT
        )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def check_registry_health(self) -> bool:
        """Check if the MCP Registry service is healthy."""
        try:
            response = await self.client.get(f"{MCP_REGISTRY_URL}/health")
            return response.status_code == 200
        except Exception as e:
            console.print(f"[red]❌ MCP Registry connection failed: {e}[/red]")
            return False
    
    async def list_servers(self, verified_only: bool = False) -> List[Dict[str, Any]]:
        """
        List available MCP servers from the cloud registry.
        
        Args:
            verified_only: If True, only return verified servers
            
        Returns:
            List of server configurations
        """
        try:
            params = {"verified_only": verified_only}
            response = await self.client.get(
                f"{MCP_REGISTRY_URL}/servers",
                params=params
            )
            response.raise_for_status()
            data = response.json()
            # Handle both list and dict responses
            if isinstance(data, dict) and "servers" in data:
                return data["servers"]
            elif isinstance(data, dict) and "results" in data:
                return data["results"]
            elif isinstance(data, list):
                return data
            else:
                console.print(f"[yellow]Unexpected response format: {type(data)}[/yellow]")
                if isinstance(data, dict):
                    console.print(f"[yellow]Response keys: {list(data.keys())}[/yellow]")
                return []
        except httpx.HTTPStatusError as e:
            console.print(f"[red]❌ Failed to fetch servers: HTTP {e.response.status_code}[/red]")
            return []
        except Exception as e:
            console.print(f"[red]❌ Error fetching servers: {e}[/red]")
            return []
    
    async def search_servers(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for MCP servers by query.
        
        Args:
            query: Search query
            
        Returns:
            List of matching servers
        """
        try:
            # Use the main servers endpoint with search parameter
            params = {"search": query}
            response = await self.client.get(
                f"{MCP_REGISTRY_URL}/servers",
                params=params
            )
            response.raise_for_status()
            data = response.json()
            # Handle both list and dict responses
            if isinstance(data, dict) and "servers" in data:
                return data["servers"]
            elif isinstance(data, dict) and "results" in data:
                return data["results"]
            elif isinstance(data, list):
                return data
            else:
                return []
        except Exception as e:
            console.print(f"[red]❌ Search failed: {e}[/red]")
            return []
    
    async def get_server_details(self, server_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific server.
        
        Args:
            server_id: The server ID
            
        Returns:
            Server details or None
        """
        try:
            response = await self.client.get(f"{MCP_REGISTRY_URL}/servers/{server_id}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            console.print(f"[red]❌ Failed to get server details: {e}[/red]")
            return None
    
    async def check_server_health(self, server_id: str) -> Dict[str, Any]:
        """Check health of a specific server."""
        try:
            response = await self.client.get(
                f"{MCP_REGISTRY_URL}/servers/{server_id}/health"
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the MCP CLI."""
    parser = argparse.ArgumentParser(
        description="Cloud-only MCP CLI for Cogzia Alpha v1.5",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  mcp --list                    List all available MCP servers
  mcp --search "weather"        Search for weather-related servers
  mcp --info server-id          Get details about a specific server
  mcp --health                  Check MCP Registry health
  mcp --verified                List only verified servers
        """
    )
    
    # Commands
    parser.add_argument("--list", "-l", action="store_true",
                        help="List all available MCP servers")
    parser.add_argument("--search", "-s", metavar="QUERY",
                        help="Search for MCP servers")
    parser.add_argument("--info", "-i", metavar="SERVER_ID",
                        help="Get details about a specific server")
    parser.add_argument("--health", action="store_true",
                        help="Check MCP Registry health status")
    parser.add_argument("--verified", "-v", action="store_true",
                        help="Show only verified servers")
    
    # Output options
    parser.add_argument("--json", action="store_true",
                        help="Output in JSON format")
    parser.add_argument("--quiet", "-q", action="store_true",
                        help="Minimal output")
    
    return parser


async def list_servers_command(client: CloudMCPClient, verified_only: bool, json_output: bool):
    """Execute the list servers command."""
    servers = await client.list_servers(verified_only=verified_only)
    
    if json_output:
        print(json.dumps(servers, indent=2))
        return
    
    if not servers:
        console.print("[yellow]No servers found in the registry[/yellow]")
        return
    
    # Create a rich table
    table = Table(title="Available MCP Servers", box=box.ROUNDED)
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name", style="green")
    table.add_column("Description", style="white")
    table.add_column("Verified", style="yellow", justify="center")
    
    for server in servers:
        verified = "✅" if server.get("verified", False) else "❌"
        table.add_row(
            server.get("id", "N/A"),
            server.get("name", "N/A"),
            server.get("description", "N/A")[:60] + "...",
            verified
        )
    
    console.print(table)
    console.print(f"\n[dim]Total servers: {len(servers)}[/dim]")


async def search_servers_command(client: CloudMCPClient, query: str, json_output: bool):
    """Execute the search servers command."""
    console.print(f"[cyan]Searching for '{query}'...[/cyan]")
    servers = await client.search_servers(query)
    
    if json_output:
        print(json.dumps(servers, indent=2))
        return
    
    if not servers:
        console.print(f"[yellow]No servers found matching '{query}'[/yellow]")
        return
    
    # Display results
    for server in servers:
        panel = Panel(
            f"[bold]{server.get('name', 'N/A')}[/bold]\n"
            f"ID: [cyan]{server.get('id', 'N/A')}[/cyan]\n"
            f"Description: {server.get('description', 'N/A')}\n"
            f"Verified: {'✅' if server.get('verified', False) else '❌'}",
            box=box.ROUNDED,
            expand=False
        )
        console.print(panel)
    
    console.print(f"\n[dim]Found {len(servers)} server(s)[/dim]")


async def get_server_info_command(client: CloudMCPClient, server_id: str, json_output: bool):
    """Execute the get server info command."""
    info = await client.get_server_details(server_id)
    
    if json_output:
        print(json.dumps(info or {}, indent=2))
        return
    
    if not info:
        console.print(f"[red]Server '{server_id}' not found[/red]")
        return
    
    # Display detailed info
    tools_section = ""
    tools = info.get('tools', [])
    if tools:
        tools_list = []
        for tool in tools:
            if isinstance(tool, dict):
                tool_name = tool.get('name', 'Unknown')
                tool_desc = tool.get('description', 'No description')
                tools_list.append(f"  • [cyan]{tool_name}[/cyan]: {tool_desc}")
            else:
                tools_list.append(f"  • {tool}")
        tools_section = "\n".join(tools_list)
    else:
        tools_section = "  [dim]No tools available[/dim]"
    
    console.print(Panel(
        f"[bold cyan]{info.get('name', 'N/A')}[/bold cyan]\n\n"
        f"[bold]ID:[/bold] {info.get('id', 'N/A')}\n"
        f"[bold]Description:[/bold] {info.get('description', 'N/A')}\n"
        f"[bold]Version:[/bold] {info.get('version', 'N/A')}\n"
        f"[bold]Verified:[/bold] {'✅ Yes' if info.get('verified', False) else '❌ No'}\n"
        f"[bold]Category:[/bold] {info.get('category', 'N/A')}\n"
        f"[bold]Author:[/bold] {info.get('author', 'N/A')}\n"
        f"[bold]License:[/bold] {info.get('license', 'N/A')}\n\n"
        f"[bold]Tools:[/bold]\n{tools_section}",
        title="Server Information",
        box=box.ROUNDED
    ))
    
    # Check server health
    health = await client.check_server_health(server_id)
    health_status = "✅ Healthy" if health.get("status") == "healthy" else "❌ Unhealthy"
    console.print(f"\n[bold]Health Status:[/bold] {health_status}")


async def check_health_command(client: CloudMCPClient, json_output: bool):
    """Execute the health check command."""
    console.print("[cyan]Checking MCP Registry health...[/cyan]")
    
    healthy = await client.check_registry_health()
    
    if json_output:
        print(json.dumps({"healthy": healthy, "url": MCP_REGISTRY_URL}))
        return
    
    if healthy:
        console.print(f"[green]✅ MCP Registry is healthy[/green]")
        console.print(f"[dim]URL: {MCP_REGISTRY_URL}[/dim]")
    else:
        console.print(f"[red]❌ MCP Registry is not responding[/red]")
        console.print(f"[dim]URL: {MCP_REGISTRY_URL}[/dim]")
        console.print("\n[yellow]Troubleshooting:[/yellow]")
        console.print("• Check your internet connection")
        console.print("• Verify GCP services are running")
        console.print("• Ensure you have proper authentication")


async def main():
    """Main entry point for the MCP CLI."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Check if any command was specified
    if not any([args.list, args.search, args.info, args.health]):
        parser.print_help()
        return 1
    
    # Check GCP availability
    if not GCP_ENABLED:
        console.print("[red]❌ GCP services are not available[/red]")
        console.print("[yellow]This tool requires connection to cloud services[/yellow]")
        return 1
    
    # Get authentication token if available
    auth_manager = TUIAuthManager()
    auth_token = None
    
    # Try to load saved authentication
    saved_token = await auth_manager.load_token()
    if saved_token:
        # The token is stored as "token" not "access_token"
        auth_manager.current_token = saved_token.get("token")
        auth_manager.refresh_token_value = saved_token.get("refresh_token")
        # Extract user info from the token data
        if "user" in saved_token:
            user_data = saved_token["user"]
            auth_manager.current_user = UserContext(
                user_id=user_data.get("id", ""),
                email=user_data.get("email", ""),
                token=saved_token.get("token", ""),
                roles=user_data.get("roles", [])
            )
        else:
            # Fallback if user data not in expected format
            auth_manager.current_user = UserContext(
                user_id=saved_token.get("user_id", ""),
                email=saved_token.get("email", ""),
                token=saved_token.get("token", ""),
                roles=saved_token.get("roles", [])
            )
    
    if auth_manager.is_authenticated():
        user_context = auth_manager.current_user
        auth_token = user_context.token if user_context else None
        if not args.quiet:
            console.print(f"[green]🔐 Authenticated as: {user_context.email}[/green]")
    elif not args.quiet:
        console.print("[yellow]🔓 Running in anonymous mode (some features limited)[/yellow]")
    
    # Create client and execute commands
    async with CloudMCPClient(auth_token=auth_token) as client:
        try:
            if args.health:
                await check_health_command(client, args.json)
            elif args.list:
                await list_servers_command(client, args.verified, args.json)
            elif args.search:
                await search_servers_command(client, args.search, args.json)
            elif args.info:
                await get_server_info_command(client, args.info, args.json)
            
            return 0
            
        except KeyboardInterrupt:
            if not args.quiet:
                console.print("\n[yellow]Interrupted by user[/yellow]")
            return 130
        except Exception as e:
            console.print(f"[red]❌ Unexpected error: {e}[/red]")
            return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))