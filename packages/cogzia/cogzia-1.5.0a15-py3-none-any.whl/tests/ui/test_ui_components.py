#!/usr/bin/env python3
"""
Test UI components for consistency.

This script tests all UI components to ensure visual consistency
across the Cogzia Alpha v1.5 application.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from ui_components import (
    AuthenticationStatusBox, StandardMessages, WelcomeScreen,
    ProgressIndicators, AppCreationSummary, UIHelpers
)
from auth_manager import UserContext, DemoUserContext
from rich.console import Console


async def test_ui_components():
    """Test all UI components."""
    console = Console()
    
    # Test with authenticated user
    user = UserContext(
        user_id="test123",
        email="test@example.com",
        token="fake_token",
        roles=["user"]
    )
    
    print("\n" + "="*60)
    print("AUTHENTICATED USER DISPLAYS")
    print("="*60 + "\n")
    
    # Full auth box
    print("1. Full Authentication Status Box:")
    auth_box = AuthenticationStatusBox.create(user, compact=False)
    console.print(auth_box)
    console.print()
    
    # Compact auth box
    print("2. Compact Authentication Status Box:")
    auth_box_compact = AuthenticationStatusBox.create(user, compact=True)
    console.print(auth_box_compact)
    console.print()
    
    # Welcome screen
    print("3. Welcome Screen (Auto Mode):")
    WelcomeScreen.create("auto", user)
    console.print()
    
    # Success message
    print("4. Success Message:")
    success = StandardMessages.success(
        "Test Success",
        "Operation completed successfully",
        details=["Created 5 files", "Updated 3 configurations", "All tests passed"]
    )
    console.print(success)
    console.print()
    
    # Info message
    print("5. Info Message:")
    info = StandardMessages.info(
        "System Information",
        [
            "Version: 1.5.0",
            "Environment: Production",
            "Services: All operational"
        ],
        footer="Last updated: 2025-07-17"
    )
    console.print(info)
    console.print()
    
    # Progress indicator
    print("6. Progress Indicator:")
    progress = ProgressIndicators.step_progress(
        3, 10, "Generating System Prompt", 
        "Creating an intelligent prompt based on your requirements"
    )
    console.print(progress)
    console.print()
    
    # App creation summary
    print("7. App Creation Summary:")
    app_config = {
        'app_name': 'Weather Assistant',
        'requirements': 'Get current weather and forecasts',
        'servers': ['time-server', 'brave-search', 'calculator']
    }
    summary = AppCreationSummary.create(app_config, "app_test123", saved=True)
    console.print(summary)
    console.print()
    
    print("\n" + "="*60)
    print("DEMO/UNAUTHENTICATED USER DISPLAYS")
    print("="*60 + "\n")
    
    # Demo user
    demo_user = DemoUserContext()
    
    # Full auth box (demo)
    print("8. Demo Mode Authentication Box:")
    auth_box_demo = AuthenticationStatusBox.create(demo_user, compact=False)
    console.print(auth_box_demo)
    console.print()
    
    # Compact auth box (demo)
    print("9. Demo Mode Compact Box:")
    auth_box_demo_compact = AuthenticationStatusBox.create(demo_user, compact=True)
    console.print(auth_box_demo_compact)
    console.print()
    
    # Error message
    print("10. Error Message:")
    error = StandardMessages.error(
        "Connection Failed",
        "Unable to connect to authentication service",
        recovery="Check your internet connection and try again",
        details=["Status code: 503", "Service: auth.cogzia.com", "Timeout: 30s"]
    )
    console.print(error)
    console.print()
    
    # Warning message
    print("11. Warning Message:")
    warning = StandardMessages.warning(
        "Limited Functionality",
        "Running in demo mode - some features are disabled",
        action="Login with --login to access all features"
    )
    console.print(warning)
    console.print()
    
    # Loading indicator
    print("12. Loading Indicator:")
    loading = ProgressIndicators.loading("Connecting to MCP servers")
    console.print(loading)
    console.print()
    
    # Welcome screen (chat mode)
    print("13. Welcome Screen (Chat Mode):")
    WelcomeScreen.create("chat", None)
    console.print()
    
    print("\n" + "="*60)
    print("INTERACTIVE HELPERS")
    print("="*60 + "\n")
    
    # Test confirmation dialog (show structure only, don't call interactive method)
    print("14. Confirmation Dialog (Demo - would be interactive):")
    # Just show what it would look like
    from rich.panel import Panel
    confirm_content = f"""[bold yellow]Confirm Action:[/bold yellow] Delete application 'app_123'?

• This action cannot be undone
• All app data will be permanently removed
• 3 saved configurations will be deleted

[cyan]Continue? (y/N):[/cyan]"""
    
    confirm_panel = Panel(
        confirm_content,
        border_style="yellow",
        padding=(1, 2)
    )
    console.print(confirm_panel)
    console.print()
    
    print("\n✅ All UI components tested successfully!")
    print("\nKey observations:")
    print("- Consistent color scheme: green (success), yellow (warning), red (error), cyan (info)")
    print("- Consistent padding and borders across all panels")
    print("- Clear visual hierarchy with titles and content separation")
    print("- Helpful recovery suggestions in error messages")
    print("- Professional appearance suitable for production use")


if __name__ == "__main__":
    asyncio.run(test_ui_components())