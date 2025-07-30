#!/usr/bin/env python3
"""
Test script for quick access commands in Cogzia Alpha v1.5

Tests the new --last, --quick, and --continue commands functionality.
"""
import asyncio
import sys
from pathlib import Path
import json
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from auth_manager import TUIAuthManager, UserContext
from ui import EnhancedConsole


async def create_test_data():
    """Create test app data for testing quick access."""
    console = EnhancedConsole()
    
    # Create test user context
    test_user = UserContext(
        user_id="test_user_123",
        email="test@cogzia.com",
        token="test_token",
        roles=["user"]
    )
    
    # Initialize auth manager
    auth_manager = TUIAuthManager()
    auth_manager.current_user = test_user
    
    # Create test apps
    test_apps = [
        {
            "app_id": "app_time_teller",
            "name": "Time Teller Assistant",
            "created_at": "2025-07-17T08:00:00",
            "requirements": "I want an agent to tell the time",
            "servers": ["time-mcp-server"],
            "last_used": "2025-07-17T09:30:00",
            "launch_count": 5
        },
        {
            "app_id": "app_weather_bot",
            "name": "Weather Information Bot",
            "created_at": "2025-07-17T07:00:00",
            "requirements": "I need weather information",
            "servers": ["weather-mcp-server"],
            "last_used": "2025-07-17T08:00:00",
            "launch_count": 3
        },
        {
            "app_id": "app_search_helper",
            "name": "Web Search Assistant",
            "created_at": "2025-07-17T06:00:00",
            "requirements": "I want to search the web",
            "servers": ["brave-search-mcp-server"],
            "last_used": "2025-07-17T07:00:00",
            "launch_count": 2
        }
    ]
    
    # Clear any existing test data first
    apps_path = auth_manager.get_user_apps_path()
    if apps_path.exists():
        import shutil
        shutil.rmtree(apps_path)
    apps_path.mkdir(parents=True, exist_ok=True)
    
    # Save test apps
    for app in test_apps:
        auth_manager.save_user_app_reference(app["app_id"], {
            "app_name": app["name"],
            "requirements": app["requirements"],
            "servers": app["servers"]
        })
        
        # Manually update metadata for testing
        apps_path = auth_manager.get_user_apps_path()
        ref_file = apps_path / f"{app['app_id']}.json"
        if ref_file.exists():
            with open(ref_file, 'r') as f:
                data = json.load(f)
            data.update({
                "created_at": app["created_at"],
                "last_used": app["last_used"],
                "launch_count": app["launch_count"]
            })
            with open(ref_file, 'w') as f:
                json.dump(data, f, indent=2)
    
    # Create test conversation for the time teller app
    test_messages = [
        {"role": "user", "content": "What time is it?"},
        {"role": "assistant", "content": "The current time is 9:30 AM."},
        {"role": "user", "content": "What time is it in Tokyo?"},
        {"role": "assistant", "content": "The current time in Tokyo is 11:30 PM."}
    ]
    auth_manager.save_conversation_state("app_time_teller", test_messages)
    
    console.print("[green]✓ Test data created successfully![/green]")
    return auth_manager


async def test_list_apps(auth_manager: TUIAuthManager):
    """Test listing user apps."""
    console = EnhancedConsole()
    console.print("\n[bold cyan]Testing --list-my-apps[/bold cyan]")
    
    apps = auth_manager.list_user_apps()
    console.print(f"Found {len(apps)} apps:")
    
    for app in apps:
        name = app.get('name', 'Unknown')
        app_id = app.get('app_id', 'Unknown')
        launch_count = app.get('launch_count', 0)
        console.print(f"  - {app_id}: {name} (used {launch_count} times)")


async def test_last_app(auth_manager: TUIAuthManager):
    """Test getting last used app."""
    console = EnhancedConsole()
    console.print("\n[bold cyan]Testing --last[/bold cyan]")
    
    last_app = auth_manager.get_last_app()
    if last_app:
        console.print(f"Last used app: {last_app['name']} ({last_app['app_id']})")
        console.print(f"Last used at: {last_app['last_used']}")
    else:
        console.print("[yellow]No apps found[/yellow]")


async def test_quick_search(auth_manager: TUIAuthManager):
    """Test quick search functionality."""
    console = EnhancedConsole()
    console.print("\n[bold cyan]Testing --quick[/bold cyan]")
    
    # Test various search queries
    test_queries = ["time", "weather", "search", "bot", "nonexistent"]
    
    for query in test_queries:
        app = auth_manager.get_app_by_name_fuzzy(query)
        if app:
            console.print(f"Query '{query}' -> Found: {app['name']} ({app['app_id']})")
        else:
            console.print(f"Query '{query}' -> [yellow]No match found[/yellow]")


async def test_conversation_persistence(auth_manager: TUIAuthManager):
    """Test conversation save/load functionality."""
    console = EnhancedConsole()
    console.print("\n[bold cyan]Testing --continue[/bold cyan]")
    
    # Load conversation for time teller app
    conversation = auth_manager.load_conversation_state("app_time_teller")
    if conversation:
        console.print(f"Found saved conversation from {conversation['saved_at']}")
        console.print(f"Messages: {len(conversation['messages'])}")
        
        console.print("\nLast 3 messages:")
        for msg in conversation['messages'][-3:]:
            role = "You" if msg['role'] == 'user' else "Assistant"
            console.print(f"  [dim]{role}: {msg['content']}[/dim]")
    else:
        console.print("[yellow]No saved conversation found[/yellow]")


async def main():
    """Run all tests."""
    console = EnhancedConsole()
    console.print("[bold green]Quick Access Commands Test Suite[/bold green]")
    console.print("=" * 50)
    
    # Create test data
    auth_manager = await create_test_data()
    
    # Run tests
    await test_list_apps(auth_manager)
    await test_last_app(auth_manager)
    await test_quick_search(auth_manager)
    await test_conversation_persistence(auth_manager)
    
    console.print("\n[green]✓ All tests completed![/green]")
    console.print("\n[dim]Note: This test creates data in ~/.cogzia/my_apps/test_user_123/[/dim]")
    console.print("[dim]You may want to clean up this directory after testing.[/dim]")


if __name__ == "__main__":
    asyncio.run(main())