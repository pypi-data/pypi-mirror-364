"""
Startup validation and pre-flight checks for Cogzia Alpha v1.5.

This module ensures all required services are available before starting.
Hard exits if any critical component is missing.
"""
import os
import sys
import httpx
import asyncio
from typing import List, Dict, Tuple, Optional


class StartupValidator:
    """Validates that all required services are available at startup."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.required_env_vars = [
            "ANTHROPIC_API_KEY",
            "ANTHROPIC_MODEL"
        ]
        self.critical_imports = [
            "anthropic",
            "shared.mcp.unified_mcp_client",
            "shared.mcp.client_factory",
            "shared.utils.prompt_generator"
        ]
        
    async def validate_all(self) -> None:
        """
        Run all validation checks. Hard exit on any failure.
        """
        print("🔍 Running pre-flight validation checks...")
        
        # Check environment variables
        self._validate_env_vars()
        
        # Check critical imports
        self._validate_imports()
        
        # Check MCP Registry
        await self._validate_mcp_registry()
        
        # Check at least one MCP server is available
        await self._validate_mcp_servers()
        
        print("✅ All validation checks passed!")
    
    def _validate_env_vars(self) -> None:
        """Validate required environment variables are set."""
        missing = []
        
        for var in self.required_env_vars:
            if not os.getenv(var):
                missing.append(var)
        
        if missing:
            print(f"❌ CRITICAL: Missing required environment variables: {', '.join(missing)}")
            print("💥 Hard exit - environment not properly configured")
            sys.exit(1)
        
        # Validate API key format
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key.startswith("sk-ant-api"):
            print(f"❌ CRITICAL: Invalid ANTHROPIC_API_KEY format")
            print("💥 Hard exit - API key must start with 'sk-ant-api'")
            sys.exit(1)
        
        if self.verbose:
            print("✓ Environment variables validated")
    
    def _validate_imports(self) -> None:
        """Validate critical imports are available."""
        for module in self.critical_imports:
            try:
                __import__(module)
            except ImportError as e:
                print(f"❌ CRITICAL: Cannot import required module '{module}': {e}")
                print("💥 Hard exit - missing critical dependencies")
                sys.exit(1)
        
        if self.verbose:
            print("✓ Critical imports validated")
    
    async def _validate_mcp_registry(self) -> None:
        """Validate MCP Registry is accessible."""
        registry_url = "http://localhost:10008"
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{registry_url}/health")
                if response.status_code != 200:
                    raise Exception(f"Health check returned {response.status_code}")
        except Exception as e:
            print(f"❌ CRITICAL: MCP Registry not accessible at {registry_url}: {e}")
            print("💥 Hard exit - MCP Registry is required")
            sys.exit(1)
        
        if self.verbose:
            print("✓ MCP Registry is accessible")
    
    async def _validate_mcp_servers(self) -> None:
        """Validate at least one MCP server is available."""
        # Check known MCP server ports
        server_ports = {
            "time": 9100,
            "weather": 9101,
            "calculator": 9102,
            "filesystem": 9103,
            "brave_search": 9104,
            "fortune": 9105
        }
        
        available_servers = []
        
        async with httpx.AsyncClient(timeout=2.0) as client:
            for server_name, port in server_ports.items():
                try:
                    response = await client.get(f"http://localhost:{port}/health")
                    if response.status_code == 200:
                        available_servers.append(server_name)
                except:
                    pass  # Server not available
        
        if not available_servers:
            print("❌ CRITICAL: No MCP servers are running")
            print("💥 Hard exit - at least one MCP server must be available")
            print("💡 Hint: Run ./start-services.sh to start MCP servers")
            sys.exit(1)
        
        if self.verbose:
            print(f"✓ Found {len(available_servers)} MCP servers: {', '.join(available_servers)}")


async def run_validation(verbose: bool = False) -> None:
    """
    Run startup validation.
    
    Args:
        verbose: Whether to show detailed output
    """
    validator = StartupValidator(verbose=verbose)
    await validator.validate_all()


if __name__ == "__main__":
    # Allow running this module directly for testing
    import argparse
    parser = argparse.ArgumentParser(description="Validate v1.5 startup requirements")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")
    args = parser.parse_args()
    
    asyncio.run(run_validation(args.verbose))