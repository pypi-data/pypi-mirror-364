#!/usr/bin/env python3
"""
Cogzia Alpha v1.5 - Main Entry Point

This is the main entry point for the Cogzia Alpha v1.5 AI App Creator with GCP deployment.
It handles command-line arguments and launches the demo workflow.

Usage:
    # Interactive mode (default)
    cogzia
    
    # Auto mode - run complete demo
    cogzia --auto
    
    # Auto mode - run up to specific step
    cogzia --auto 3
    
    # Auto mode with custom requirements
    cogzia --auto --requirements "I need an app that can search news"
    
    # Demo mode (simulated services)
    cogzia --demo
    
    # Verbose mode (detailed logging)
    cogzia --verbose
    
    # Save app configuration
    cogzia --save
    
    # Run with first query
    cogzia --auto --first-query "What's the weather today?"
"""
import asyncio
import argparse
import logging
import sys
import os
from pathlib import Path
from typing import Optional

# Load environment variables FIRST
from dotenv import load_dotenv
from pathlib import Path

# Try to load from multiple locations
load_dotenv()  # Current directory .env
load_dotenv(Path.home() / ".cogzia" / ".env")  # User home directory

# Set GCP deployment flags
os.environ["REQUIRE_REAL_SERVICES"] = "true"
os.environ["SKIP_MCP_INITIALIZATION"] = "true"

# Set default GCP project ID if not already set
if not os.environ.get("GCP_PROJECT_ID"):
    os.environ["GCP_PROJECT_ID"] = "696792272068"  # Use project number for Cloud Run URLs

# Disable logfire messages
os.environ["LOGFIRE_DISABLE_STARTUP_MESSAGE"] = "true"
os.environ["LOGFIRE_SEND_TO_CLOUD"] = "false"
os.environ["LOGFIRE_IGNORE_NO_CONFIG"] = "true"

# Also filter warnings
import warnings
warnings.filterwarnings("ignore", message="Logfire project URL:")

# Configure logging BEFORE any imports to suppress warnings
import logging
logging.getLogger("mcp").setLevel(logging.ERROR)
logging.getLogger("mcp.factory").setLevel(logging.ERROR)
logging.getLogger("mcp.factory.MCPHostFactory").setLevel(logging.ERROR)
logging.getLogger("MCPHostFactory").setLevel(logging.ERROR)
logging.getLogger("shared.mcp").setLevel(logging.ERROR)
logging.getLogger("logfire").setLevel(logging.ERROR)
logging.getLogger("logfire._internal").setLevel(logging.ERROR)

# Add parent directory to path for imports (only when running from source)
if __name__ == "__main__" and "site-packages" not in str(Path(__file__)):
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# Import configure_logging first and set up logging immediately
from config import configure_logging
# Configure logging early to suppress import warnings
configure_logging(verbose_mode=False, show_mcp_logs=False)

# Import our modules  
from config import DebugLevel
from demo_workflow import AIAppCreateDemo
from ui_components import (
    AuthenticationStatusBox, StandardMessages, WelcomeScreen,
    ProgressIndicators
)


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Cogzia Alpha v1.5 - Enhanced AI App Creator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # First-time setup
    cogzia --signup                 # Create new account
    cogzia --login                  # Sign in to existing account
    
    # Interactive mode (requires authentication)
    cogzia
    
    # Auto mode - complete demo
    cogzia --auto
    
    # Auto mode - run up to step 3
    cogzia --auto 3
    
    # Demo mode with custom requirements (no auth required)
    cogzia --demo --requirements "I need an app that can analyze data"
    
    # Quick access commands
    cogzia --last                    # Launch your most recent app
    cogzia --quick "time"           # Search and launch app by name
    cogzia --continue app_123xyz    # Resume previous conversation
    
    # Verbose mode with debugging
    cogzia --verbose --debug-level walk
        """
    )
    
    # Mode arguments
    parser.add_argument(
        '--auto', 
        nargs='?', 
        const=True, 
        metavar='STEP',
        help='Run in auto mode. Optionally specify step number to stop at.'
    )
    
    parser.add_argument(
        '--demo', 
        action='store_true',
        help='Run in demo mode with simulated services'
    )
    
    # Configuration arguments
    parser.add_argument(
        '--requirements', 
        type=str,
        help='App requirements (for auto mode)'
    )
    
    parser.add_argument(
        '--first-query',
        type=str,
        help='First query to run after app creation (auto mode only)'
    )
    
    parser.add_argument(
        '--save', 
        action='store_true',
        default=False,
        help='Save the created app to disk'
    )
    
    parser.add_argument(
        '--no-save',
        action='store_true',
        help='Do not save the app (overrides --save)'
    )
    
    # Debug/display arguments
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--debug-level',
        type=str,
        choices=['none', 'run', 'walk', 'crawl'],
        default='none',
        help='Set debug output level'
    )
    
    # Structure arguments
    parser.add_argument(
        '--use-new-structure',
        action='store_true',
        help='Force use of new repository structure'
    )
    
    parser.add_argument(
        '--use-old-structure',
        action='store_true',
        help='Force use of old repository structure'
    )
    
    # Authentication arguments
    parser.add_argument(
        '--login',
        action='store_true',
        help='Login with your Cogzia account'
    )
    
    parser.add_argument(
        '--logout',
        action='store_true',
        help='Logout from your Cogzia account'
    )
    
    parser.add_argument(
        '--signup',
        action='store_true',
        help='Create a new Cogzia account'
    )
    
    parser.add_argument(
        '--enable-auth',
        action='store_true',
        help='Enable authentication features (feature flag)'
    )
    
    parser.add_argument(
        '--token',
        type=str,
        help='Use existing auth token instead of interactive login'
    )
    
    # Load existing app
    parser.add_argument(
        '--load',
        type=str,
        metavar='MANIFEST_PATH',
        help='Load a previously saved app from manifest'
    )
    
    # User app library commands
    parser.add_argument(
        '--list-my-apps',
        action='store_true',
        help='List all apps in your library'
    )
    
    parser.add_argument(
        '--launch',
        type=str,
        metavar='APP_ID',
        help='Launch app by ID from your library'
    )
    
    # Quick access commands
    parser.add_argument(
        '--last',
        action='store_true',
        help='Launch your most recently used app'
    )
    
    parser.add_argument(
        '--quick',
        type=str,
        metavar='QUERY',
        help='Quick launch app by name search'
    )
    
    parser.add_argument(
        '--continue',
        type=str,
        metavar='APP_ID',
        dest='continue_app',
        help='Continue previous conversation with an app'
    )
    
    # Model selection for discovery
    parser.add_argument(
        '--discovery-model',
        type=str,
        choices=[
            'claude-opus-4-20250514',
            'claude-sonnet-4-20250514',
            'claude-3-5-haiku-20241022',
            'claude-3-7-sonnet-20250219'
        ],
        help='Model to use for tool discovery (defaults to ANTHROPIC_MODEL env var)'
    )
    
    # Prompt caching
    parser.add_argument(
        '--cache-prompt',
        action='store_true',
        help='Cache generated system prompts to avoid re-generation for similar requirements'
    )
    
    # Update functionality
    parser.add_argument(
        '--update',
        action='store_true',
        help='Check for and install updates'
    )
    
    parser.add_argument(
        '--check-update',
        action='store_true',
        help='Check for updates without installing'
    )
    
    parser.add_argument(
        '--update-channel',
        type=str,
        choices=['stable', 'alpha'],
        default='stable',
        help='Update channel to use (default: stable)'
    )
    
    parser.add_argument(
        '--version', 
        action='store_true',
        help='Show version information'
    )
    
    parser.add_argument(
        '--uninstall',
        action='store_true',
        help='Completely uninstall cogzia and clean up all artifacts'
    )
    
    parser.add_argument(
        '--cleanup',
        action='store_true',
        help='Clean up legacy aliases and configuration without uninstalling'
    )
    
    return parser.parse_args()


async def load_existing_app(manifest_path: Optional[str] = None, resume_messages: Optional[list] = None, 
                          app_config: Optional[dict] = None, app_id: Optional[str] = None, 
                          user_context: Optional['UserContext'] = None):
    """Load and run an existing app from cloud storage or local manifest."""
    import yaml
    from app_executor import MinimalAIApp
    from ui import EnhancedConsole
    from cloud_storage_adapter import CloudStorageAdapter
    from auth_manager import TUIAuthManager
    
    console = EnhancedConsole()
    manifest = None
    
    try:
        # Use provided app_config if available
        if app_config:
            manifest = app_config
            if not app_id and manifest_path:
                app_id = manifest_path
        # Check if this is an app ID (for cloud loading)
        elif manifest_path and not manifest_path.endswith('.yaml') and not '/' in manifest_path:
            # This looks like an app ID, try cloud storage
            console.print(f"[cyan]Loading app from cloud: {manifest_path}[/cyan]")
            
            auth_manager = TUIAuthManager()
            if auth_manager.is_authenticated():
                storage = CloudStorageAdapter(auth_manager.user_context.token)
                app_config = await storage.load_app(manifest_path)
                
                if app_config:
                    console.print(f"[green]✅ Loaded from cloud: {app_config['app_name']}[/green]")
                    # Convert cloud format to manifest format
                    manifest = {
                        'app_id': manifest_path,
                        'app_name': app_config['app_name'],
                        'created_at': app_config.get('created_at', 'Unknown'),
                        'system_prompt': app_config.get('system_prompt', ''),
                        'servers': app_config.get('servers', []),
                        'requirements': app_config.get('requirements', '')
                    }
                else:
                    console.print("[red]❌ App not found in cloud storage[/red]")
                    return
            else:
                console.print("[red]❌ Not authenticated[/red]")
                console.print("[yellow]Please login to access your apps[/yellow]")
                return
        
        # If not loaded from cloud, app not found
        if manifest is None:
            console.print(f"[red]❌ App not found: {manifest_path}[/red]")
            console.print("[yellow]Please ensure you're logged in and the app exists[/yellow]")
            return
        
        console.print(f"[green]Loading app: {manifest['app_name']}[/green]")
        console.print(f"[dim]Created: {manifest['created_at']}[/dim]")
        
        # Create app instance
        app = MinimalAIApp(
            app_id=manifest['app_id'],
            system_prompt=manifest['system_prompt'],
            mcp_servers=manifest.get('servers', []),
            verbose=True
        )
        
        # Start the app
        await app.start()
        console.print("[green]✓ App loaded successfully![/green]")
        
        # Restore conversation if resuming
        if resume_messages:
            console.print(f"\n[cyan]Previous conversation ({len(resume_messages)} messages):[/cyan]")
            for msg in resume_messages[-3:]:  # Show last 3 messages
                role = "You" if msg.get('role') == 'user' else "Assistant"
                console.print(f"[dim]{role}: {msg.get('content', '')[:80]}...[/dim]")
            console.print()
            
            # Restore conversation history to app
            if hasattr(app, 'conversation_history'):
                app.conversation_history = resume_messages
        
        # Track messages for saving
        conversation_messages = resume_messages or []
        
        # Run the app in proper interactive mode
        from demo_workflow import AIAppCreateDemo
        from app_executor import AppQueryExecutor
        
        # Create demo instance for interactive mode
        demo = AIAppCreateDemo(
            auto_mode=False,
            demo_mode=False,
            save_app=True,
            verbose=False,
            user_context=user_context
        )
        
        # Set up the demo with the loaded app
        demo.app = app
        demo.app_config = manifest
        demo.app_id = app_id
        demo.app_executor = AppQueryExecutor(console, verbose=False)  # Use proper executor for streaming
        
        # Show that we're continuing the conversation
        if resume_messages and len(resume_messages) > 0:
            console.print(f"\n[dim]Continuing conversation with {len(resume_messages)} previous messages[/dim]\n")
        
        # Run interactive chat loop
        console.print("[bold cyan]💬 Continuing your conversation![/bold cyan]")
        console.print("[dim]Type '/help' for commands or 'quit' to exit.[/dim]\n")
        
        while True:
            try:
                # Get user input
                user_input = await asyncio.get_event_loop().run_in_executor(
                    None, input, "\nUser: "
                )
                
                if not user_input.strip():
                    continue
                
                # Handle exit commands
                if user_input.lower() in ['quit', 'exit', 'q']:
                    console.print("\n[yellow]Chat ended. Goodbye![/yellow]")
                    break
                
                # Handle commands
                if user_input.startswith('/'):
                    await demo._handle_chat_command(user_input)
                else:
                    # Add to conversation history
                    conversation_messages.append({"role": "user", "content": user_input})
                    
                    # Execute query with full streaming
                    result = await demo.app_executor.execute_query(app, user_input, show_user_message=False)
                    
                    # Add response to history if available
                    if result and isinstance(result, dict) and result.get('content'):
                        conversation_messages.append({"role": "assistant", "content": result['content']})
                    
            except KeyboardInterrupt:
                console.print("\n[yellow]Chat ended. Goodbye![/yellow]")
                break
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                if demo.verbose:
                    import traceback
                    traceback.print_exc()
        
        # Note: Conversation state is now managed by cloud storage
        # No local saving needed
        
        # Cleanup
        await app.stop()
        
    except Exception as e:
        console.print(f"[red]Error loading app: {e}[/red]")
        raise


async def uninstall_cogzia():
    """Completely uninstall cogzia and clean up all artifacts."""
    from ui import EnhancedConsole
    from cleanup import comprehensive_cleanup
    import subprocess
    import sys
    from rich.prompt import Confirm
    
    console = EnhancedConsole()
    
    console.print("[bold red]🗑️  Cogzia Uninstaller[/bold red]")
    console.print("[dim]This will completely remove Cogzia and clean up all configuration[/dim]\n")
    
    # Confirm uninstall
    if not Confirm.ask("Are you sure you want to completely uninstall Cogzia?"):
        console.print("[yellow]Uninstall cancelled.[/yellow]")
        return
    
    try:
        console.print("[cyan]Step 1: Cleaning up aliases and configuration...[/cyan]")
        
        # Run comprehensive cleanup
        cleanup_results = comprehensive_cleanup(dry_run=False)
        
        console.print("\n[cyan]Step 2: Uninstalling package...[/cyan]")
        console.print("[dim]Running: pip uninstall cogzia[/dim]")
        
        # Uninstall the package
        result = subprocess.run([
            sys.executable, "-m", "pip", "uninstall", "cogzia", "-y"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            console.print("[green]✅ Package uninstalled successfully[/green]")
        else:
            console.print(f"[yellow]⚠️  Package uninstall output:[/yellow]")
            console.print(result.stdout)
            if result.stderr:
                console.print(result.stderr)
        
        # Final summary
        console.print("\n[bold green]🎉 Uninstall Complete![/bold green]")
        console.print("[dim]Summary of actions taken:[/dim]")
        
        alias_results = cleanup_results.get('alias_cleanup', {})
        if alias_results.get('aliases_removed', 0) > 0:
            console.print(f"• Removed {alias_results['aliases_removed']} legacy aliases")
        
        if cleanup_results.get('config_removed', False):
            console.print("• Removed ~/.cogzia configuration directory")
        
        console.print("• Uninstalled cogzia package via pip")
        console.print("\n[yellow]Please restart your terminal to ensure all changes take effect.[/yellow]")
        
    except Exception as e:
        console.print(f"[red]❌ Error during uninstall: {e}[/red]")
        console.print("[yellow]You may need to manually remove some components[/yellow]")
        raise

async def cleanup_only():
    """Run cleanup without uninstalling."""
    from ui import EnhancedConsole
    from cleanup import comprehensive_cleanup
    
    console = EnhancedConsole()
    
    console.print("[bold cyan]🧹 Cogzia Cleanup Tool[/bold cyan]")
    console.print("[dim]This will clean up legacy aliases without uninstalling[/dim]\n")
    
    try:
        cleanup_results = comprehensive_cleanup(dry_run=False)
        
        alias_results = cleanup_results.get('alias_cleanup', {})
        if alias_results.get('aliases_removed', 0) > 0:
            console.print(f"\n[green]✅ Successfully cleaned up {alias_results['aliases_removed']} legacy aliases[/green]")
            console.print("[yellow]Please restart your terminal for changes to take effect.[/yellow]")
        else:
            console.print("\n[green]✅ No cleanup needed - your installation is already clean![/green]")
            
    except Exception as e:
        console.print(f"[red]❌ Error during cleanup: {e}[/red]")
        raise

async def main():
    """Main entry point."""
    args = parse_arguments()
    
    # Handle version command first
    if args.version:
        print("Cogzia Alpha v1.5.0a6")
        return
    
    # Handle uninstall command
    if args.uninstall:
        await uninstall_cogzia()
        return
    
    # Handle cleanup command
    if args.cleanup:
        await cleanup_only()
        return
    
    # Handle update commands
    if args.update or args.check_update:
        from update_manager import UpdateManager
        from version import get_version_string
        
        manager = UpdateManager(channel=args.update_channel)
        
        if args.check_update:
            # Just check for updates
            print(f"Current version: {get_version_string()}")
            update_info = await manager.check_for_updates()
            if update_info:
                new_version = update_info.get("version", "Unknown")
                print(f"\n📦 Update available: Cogzia Alpha v{new_version}")
                print("Run 'cogzia --update' to install")
            else:
                print("✅ You're on the latest version!")
            return
        
        if args.update:
            # Perform update
            success = await manager.perform_update()
            sys.exit(0 if success else 1)
    
    # Load user context early to show auth status
    user_context = None
    if not args.demo:
        from auth_manager import TUIAuthManager
        auth_manager = TUIAuthManager()
        await auth_manager.load_token()
        user_context = auth_manager.current_user
    
    # Determine the mode for welcome screen
    mode = "demo" if args.demo else "auto" if args.auto else "chat"
    if args.login:
        mode = "login"
    elif args.list_my_apps or args.launch or args.last or args.quick or args.continue_app:
        mode = "list"
    
    # Show welcome screen with authentication status for all commands
    # (except utility commands that have their own display)
    if not args.logout and not args.launch:
        WelcomeScreen.create(mode, user_context)
        
        # Check for updates in background (non-blocking)
        if not args.demo:
            import asyncio
            from update_manager import check_and_notify_update
            asyncio.create_task(check_and_notify_update())
    
    # Skip MCP server startup and validation for GCP deployment
    from ui import EnhancedConsole
    console = EnhancedConsole()
    console.print("[cyan]Using GCP-deployed services - skipping local startup[/cyan]")
    
    # Get GCP auth token for Cloud Run access (optional)
    try:
        import subprocess
        result = subprocess.run(
            ["gcloud", "auth", "print-identity-token"],
            capture_output=True,
            text=True,
            check=True
        )
        os.environ["GCP_AUTH_TOKEN"] = result.stdout.strip()
        console.print("[green]✓ GCP authentication token obtained[/green]")
    except FileNotFoundError:
        # gcloud not installed - this is OK for public endpoints
        console.print("[dim]! gcloud CLI not found - using public endpoints[/dim]")
    except Exception as e:
        console.print(f"[dim]! Could not get GCP auth token: {e}[/dim]")
        console.print("[dim]   Using public Cloud Run endpoints[/dim]")
    
    # Simple validation that GCP services are available
    import httpx
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            from config import GCP_BASE_URL
            response = await client.get(f"{GCP_BASE_URL}/health")
            if response.status_code == 200:
                console.print("[green]✓ GCP services are available[/green]")
            else:
                console.print(f"[dim]! GCP services returned: {response.status_code}[/dim]")
    except Exception as e:
        console.print(f"[red][X] GCP services not available: {e}[/red]")
        return
    
    # Handle user app library commands
    if args.list_my_apps or args.launch or args.last or args.quick or args.continue_app:
        from ui import EnhancedConsole
        from rich.table import Table
        
        console = EnhancedConsole()
        
        # Check authentication
        if not user_context:
            error_panel = StandardMessages.error(
                "Authentication Required",
                "You must be logged in to access your app library",
                recovery="Use 'cogzia_alpha_v1_5 --login' to authenticate",
                details=[
                    "Your app library stores all apps you've created",
                    "Login provides persistent access to your apps",
                    "Apps are automatically saved when authenticated"
                ]
            )
            console.print(error_panel)
            return
        
        # Initialize auth manager
        from auth_manager import TUIAuthManager
        auth_manager = TUIAuthManager()
        auth_manager.current_user = user_context
        
        if args.list_my_apps:
            # List user's apps
            apps = auth_manager.list_user_apps()
            if not apps:
                console.print("[yellow]No apps in your library yet![/yellow]")
                console.print("[dim]Create an app with: cogzia_alpha_v1_5 --auto[/dim]")
                return
            
            # Display apps table
            table = Table(title="Your Apps")
            table.add_column("App ID", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("Created", style="dim")
            table.add_column("Uses", style="yellow")
            
            for app in apps:
                table.add_row(
                    app.get('app_id', 'Unknown'),
                    app.get('name', app.get('app_name', 'Unnamed App')),  # Try both 'name' and 'app_name'
                    app.get('created_at', '')[:10] if app.get('created_at') else 'Unknown',
                    str(app.get('launch_count', 1))
                )
            
            console.print(table)
            console.print(f"\n[dim]Launch with: cogzia_alpha_v1_5 --launch <app_id>[/dim]")
            console.print(f"[dim]Quick launch: cogzia_alpha_v1_5 --last[/dim]")
            return
        
        if args.last:
            # Launch last used app
            last_app = auth_manager.get_last_app()
            if not last_app:
                console.print("[yellow]No apps in your library yet![/yellow]")
                console.print("[dim]Create an app with: cogzia_alpha_v1_5 --auto[/dim]")
                return
            
            app_name = last_app.get('name', last_app.get('app_name', 'Unnamed App'))
            console.print(f"[green]Launching last used app: {app_name}[/green]")
            args.launch = last_app.get('app_id', 'Unknown')
        
        if args.quick:
            # Quick search and launch
            app = auth_manager.get_app_by_name_fuzzy(args.quick)
            if not app:
                console.print(f"[red]No app found matching '{args.quick}'[/red]")
                console.print("[dim]Use --list-my-apps to see available apps[/dim]")
                return
            
            app_name = app.get('name', app.get('app_name', 'Unnamed App'))
            console.print(f"[green]Found app: {app_name}[/green]")
            args.launch = app.get('app_id', 'Unknown')
        
        if args.continue_app:
            # Resume conversation with specific app
            app_id = args.continue_app
            
            # Cloud-only: need to check cloud storage
            console.print(f"[cyan]Looking for app {app_id} in cloud storage...[/cyan]")
            
            # Try to load from cloud storage
            from cloud_storage_adapter import CloudStorageAdapter
            storage = CloudStorageAdapter(user_context.token if user_context else None)
            app_config = await storage.load_app(app_id)
            
            if not app_config:
                console.print(f"[red]App {app_id} not found![/red]")
                console.print("[dim]Use --list-my-apps to see available apps[/dim]")
                return
            
            # Load conversation state
            conversation = auth_manager.load_conversation_state(app_id)
            if conversation:
                console.print(f"[green]Resuming conversation from {conversation['saved_at']}[/green]")
                console.print(f"[dim]Previous messages: {len(conversation['messages'])}[/dim]")
                
                # Pass conversation to load function
                await load_existing_app(None, app_config=app_config, app_id=app_id, resume_messages=conversation['messages'], user_context=user_context)
            else:
                console.print("[yellow]No saved conversation found[/yellow]")
                console.print("[dim]Starting fresh conversation...[/dim]")
                await load_existing_app(None, app_config=app_config, app_id=app_id, user_context=user_context)
            return
        
        if args.launch:
            # Launch specific app from cloud storage
            console.print(f"[dim]Loading app: {args.launch}[/dim]")
            
            # Try to load from cloud storage first
            from cloud_storage_adapter import CloudStorageAdapter
            storage = CloudStorageAdapter(auth_token=user_context.token if user_context else None)
            
            app_config = await storage.load_app(args.launch)
            if not app_config:
                console.print(f"[red]App {args.launch} not found![/red]")
                console.print("[dim]Use --list-my-apps to see available apps[/dim]")
                return
            
            # Update usage stats
            auth_manager.update_app_usage(args.launch)
            
            # Load from cloud config
            await load_existing_app(None, app_config=app_config, app_id=args.launch, user_context=user_context)
            return
    
    # Handle --login option separately
    if args.login:
        from ui import EnhancedConsole
        import getpass
        
        console = EnhancedConsole()
        
        # Check if already authenticated
        if user_context and not user_context.is_demo:
            info_panel = StandardMessages.info(
                "Already Authenticated",
                [
                    f"Signed in as: {user_context.email}",
                    "Full app library access enabled",
                    "Auto-save enabled for all created apps"
                ],
                footer="Use --logout to sign out"
            )
            console.print(info_panel)
            return
        
        console.print("[cyan]🔐 Cogzia Login[/cyan]")
        console.print("[dim]Enter your credentials to access your app library[/dim]\n")
        
        # Get credentials
        email = input("Email: ")
        password = getpass.getpass("Password: ")
        
        try:
            # Re-initialize auth_manager for login
            from auth_manager import TUIAuthManager
            auth_manager = TUIAuthManager()
            
            # Attempt login
            loading_panel = ProgressIndicators.loading("Authenticating")
            console.print(loading_panel)
            
            result = await auth_manager.login(email, password)
            
            if result.get("success", False):
                success_panel = StandardMessages.success(
                    "Login Successful",
                    f"Welcome back, {auth_manager.current_user.email}!",
                    details=[
                        "Your apps are now accessible",
                        "New apps will be auto-saved to your library",
                        "Use --list-my-apps to see your saved apps"
                    ]
                )
                console.print(success_panel)
                console.print("\n[cyan]Quick commands:[/cyan]")
                console.print("• Create app: [bold]cogzia_alpha_v1_5 --auto --requirements 'your request'[/bold]")
                console.print("• List apps: [bold]cogzia_alpha_v1_5 --list-my-apps[/bold]")
                console.print("• Launch app: [bold]cogzia_alpha_v1_5 --launch <app_id>[/bold]")
            else:
                error_panel = StandardMessages.error(
                    "Login Failed",
                    result.get('error', 'Invalid credentials'),
                    recovery="Please check your email and password and try again"
                )
                console.print(error_panel)
        except Exception as e:
            error_panel = StandardMessages.error(
                "Connection Error",
                str(e),
                recovery="Check your internet connection and try again"
            )
            console.print(error_panel)
        
        return
    
    # Handle --signup option separately
    if args.signup:
        from ui import EnhancedConsole
        
        console = EnhancedConsole()
        
        # Check if already authenticated
        if user_context and not user_context.is_demo:
            info_panel = StandardMessages.info(
                "Already Authenticated",
                [
                    f"Signed in as: {user_context.email}",
                    "Account already exists and is active",
                    "You can create apps and access your library"
                ],
                footer="Use --logout to sign out and create a different account"
            )
            console.print(info_panel)
            return
        
        try:
            # Initialize auth_manager for signup
            from auth_manager import TUIAuthManager
            auth_manager = TUIAuthManager()
            
            # Attempt interactive signup
            result = await auth_manager.interactive_signup()
            
            if result.get("success", False):
                success_panel = StandardMessages.success(
                    "Account Created Successfully",
                    f"Welcome to Cogzia, {auth_manager.current_user.email}!",
                    details=[
                        "Your account is now active",
                        "You can create and save AI agents",
                        "Your apps will be auto-saved to your library"
                    ]
                )
                console.print(success_panel)
                console.print("\n[cyan]Get started:[/cyan]")
                console.print("• Create your first app: [bold]cogzia --auto[/bold]")
                console.print("• Create custom app: [bold]cogzia --auto --requirements 'your request'[/bold]")
                console.print("• Interactive mode: [bold]cogzia[/bold]")
            else:
                error_panel = StandardMessages.error(
                    "Signup Failed",
                    result.get('error', 'Account creation failed'),
                    recovery="Please try again or use --login if you already have an account"
                )
                console.print(error_panel)
        except Exception as e:
            error_panel = StandardMessages.error(
                "Connection Error",
                str(e),
                recovery="Check your internet connection and try again"
            )
            console.print(error_panel)
        
        return
    
    # Handle --logout option separately
    if args.logout:
        from ui import EnhancedConsole
        
        console = EnhancedConsole()
        
        # Show compact auth status first
        auth_box = AuthenticationStatusBox.create(user_context, compact=True)
        console.print(auth_box)
        console.print()
        
        if not user_context or user_context.is_demo:
            warning_panel = StandardMessages.warning(
                "Not Logged In",
                "You are not currently logged in",
                action="Use --login to authenticate"
            )
            console.print(warning_panel)
            return
        
        # Clear token
        from auth_manager import TUIAuthManager
        auth_manager = TUIAuthManager()
        auth_manager.current_user = user_context
        
        email = user_context.email
        auth_manager.clear_token()
        auth_manager.current_user = None
        
        success_panel = StandardMessages.success(
            "Logout Successful",
            f"Successfully logged out from {email}",
            details=[
                "Your app library is no longer accessible",
                "Apps created will not be saved",
                "Use --login to sign in again"
            ]
        )
        console.print(success_panel)
        return
    
    # Handle --load option separately
    if args.load:
        await load_existing_app(args.load, user_context=user_context)
        return
    
    # Reconfigure logging based on verbose flag if needed
    if args.verbose:
        configure_logging(verbose_mode=args.verbose)
        # Enable MCP logs in verbose mode
        os.environ["SHOW_MCP_LOGS"] = "true"
    
    # Parse auto mode step
    auto_step = None
    if args.auto and args.auto is not True:
        try:
            auto_step = int(args.auto)
        except ValueError:
            print(f"Error: Invalid step number '{args.auto}'")
            sys.exit(1)
    
    # Determine save behavior - save by default in auto mode like v1.2
    if args.auto:
        save_app = not args.no_save  # Save by default unless --no-save
    else:
        save_app = args.save and not args.no_save
    
    # Determine structure preference
    use_new_structure = None
    if args.use_new_structure:
        use_new_structure = True
    elif args.use_old_structure:
        use_new_structure = False
    
    # Parse debug level
    debug_level_map = {
        'none': DebugLevel.NONE,
        'run': DebugLevel.RUN,
        'walk': DebugLevel.WALK,
        'crawl': DebugLevel.CRAWL
    }
    debug_level = debug_level_map.get(args.debug_level, DebugLevel.NONE)
    
    # Load user context if available
    user_context = None
    enable_auth = args.enable_auth
    if not args.demo:  # Only load user context if not in demo mode
        from auth_manager import TUIAuthManager
        auth_manager = TUIAuthManager()
        await auth_manager.load_token()
        user_context = auth_manager.current_user
        
        # Auto-enable auth if we have a valid user context
        if user_context and not user_context.is_demo:
            enable_auth = True
    
    # Require authentication for all non-demo usage
    if not args.demo and (not user_context or user_context.is_demo):
        from ui import EnhancedConsole
        
        console = EnhancedConsole()
        
        # Show welcome screen with authentication requirement
        welcome_panel = StandardMessages.info(
            "Welcome to Cogzia Alpha v1.5!",
            [
                "🤖 Create AI agents from natural language",
                "☁️  Save and manage your app library in the cloud",
                "🔧 Integrate with 7+ MCP servers for extended functionality"
            ],
            footer="Authentication required to continue"
        )
        console.print(welcome_panel)
        console.print()
        
        # Show authentication options
        auth_panel = StandardMessages.warning(
            "Authentication Required",
            "Please create an account or sign in to continue:",
            action="Choose an option below"
        )
        console.print(auth_panel)
        console.print()
        
        console.print("[cyan]Authentication Options:[/cyan]")
        console.print("• [bold]New user?[/bold] Create account: [green]cogzia --signup[/green]")
        console.print("• [bold]Existing user?[/bold] Sign in: [green]cogzia --login[/green]")
        console.print("• [bold]Just testing?[/bold] Demo mode: [green]cogzia --demo[/green]")
        console.print()
        
        console.print("[dim]Note: Demo mode creates temporary apps that are not saved.[/dim]")
        return
    
    # Create and run demo
    demo = AIAppCreateDemo(
        auto_mode=bool(args.auto),
        demo_mode=args.demo,
        auto_step=auto_step,
        auto_requirements=args.requirements,
        save_app=save_app,
        verbose=args.verbose,
        debug_level=debug_level,
        first_query=args.first_query,
        use_new_structure=use_new_structure,
        enable_auth=enable_auth,
        login=args.login,
        auth_token=args.token,
        user_context=user_context,
        discovery_model=args.discovery_model,
        cache_prompt=args.cache_prompt,
        auth_manager=auth_manager if not args.demo else None
    )
    
    try:
        await demo.run()
    except KeyboardInterrupt:
        print("\n\n[yellow]Demo interrupted by user[/yellow]")
    except Exception as e:
        if args.verbose:
            import traceback
            traceback.print_exc()
        else:
            print(f"\n[red]Error: {e}[/red]")
        sys.exit(1)


def cli_main():
    """Entry point for the cogzia command installed via pip."""
    # Check Python version
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        sys.exit(1)
    
    # Run the main function
    asyncio.run(main())


if __name__ == "__main__":
    cli_main()