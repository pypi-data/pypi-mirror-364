"""
Main demo workflow for Cogzia Alpha v1.5.

This module contains the AIAppCreateDemo class which orchestrates the entire
AI app creation workflow including all steps and modes.
"""
import os
import sys
import asyncio
import logging
from typing import List, Optional
from datetime import datetime
from pathlib import Path
import httpx

# Import from our modules
from config import (
    DemoStep, DebugLevel, SERVICE_DESCRIPTIONS, DEFAULT_APP_CONFIG,
    validate_environment_variables, MCP_REGISTRY_URL
)

# Import K8s config if available
try:
    from .config_k8s import K8S_ENABLED, MCP_SERVER_MANAGER_URL
    from .k8s_mcp_helper import get_k8s_mcp_servers
except ImportError:
    K8S_ENABLED = False
    MCP_SERVER_MANAGER_URL = "http://localhost:10010"
    get_k8s_mcp_servers = None
from ui import (
    EnhancedConsole, create_service_table, create_component_table,
    create_chat_message, create_step_header
)
from services import (
    ServiceHealthChecker, AuthService,
    ServiceDiscovery
)
# Simplified GCP-only implementations
# MCPRegistryClient and get_live_server_registry will be implemented inline
from app_executor import MinimalAIApp, AppQueryExecutor
from utils import (
    StructureDetector, PromptGenerator, generate_app_id,
    generate_test_query, AppManifest
)

from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.table import Table


class AIAppCreateDemo:
    """Enhanced AI App creation demo with new structure support."""
    
    def __init__(self, auto_mode: bool = False, demo_mode: bool = False, 
                 auto_step: Optional[int] = None, auto_requirements: Optional[str] = None, 
                 save_app: bool = False, verbose: bool = False, 
                 debug_level: Optional[DebugLevel] = None,
                 first_query: Optional[str] = None, use_new_structure: bool = None,
                 enable_auth: bool = False, login: bool = False, 
                 auth_token: Optional[str] = None, user_context: Optional['UserContext'] = None,
                 discovery_model: Optional[str] = None, cache_prompt: bool = False,
                 auth_manager=None):
        self.auto_mode = auto_mode
        self.demo_mode = demo_mode
        self.auto_step = auto_step
        self.auto_requirements = auto_requirements or "I need an app that can search the web for information"
        self.first_query = first_query
        self.save_app = save_app
        self.verbose = verbose
        self.debug_level = debug_level or DebugLevel.NONE
        self.chat_mode = not verbose and (debug_level is None or debug_level == DebugLevel.NONE)
        
        # Authentication attributes
        self.enable_auth = enable_auth
        self.login = login
        self.auth_token = auth_token  # Don't default to demo token here
        self.user_context = user_context
        self.auth_manager = auth_manager  # TUIAuthManager for token refresh
        self.auth_mode = "demo"  # Will be set to "authenticated" after login
        self.auth_service_url = None  # Will be set in _initialize_services
        self.discovery_model = discovery_model  # Model to use for tool discovery
        self.cache_prompt = cache_prompt  # Whether to cache generated prompts
        
        self.current_step = 0
        self.app: Optional[MinimalAIApp] = None
        self.skeleton = None
        self.structure_detector = StructureDetector()
        self.console = EnhancedConsole(self.structure_detector)
        
        # Auto-detect or use specified structure
        if use_new_structure is None:
            self.use_new_structure = self.structure_detector.has_new_structure
        else:
            self.use_new_structure = use_new_structure
        
        self.stats = {
            "searches": 0,
            "total_time": 0,
            "chunks_streamed": 0,
            "start_time": None
        }
        
        # Initialize services
        self._initialize_services()
        
        self.logger = logging.getLogger(__name__)
        self.mcp_registry_client = None
        self.steps: List[DemoStep] = []
        self._register_steps()
        
        self.app_config = DEFAULT_APP_CONFIG.copy()
        
        self.in_chat_loop = False
    
    def _initialize_services(self):
        """Initialize services with structure awareness."""
        try:
            # Initialize service helpers
            self.health_checker = ServiceHealthChecker()
            self.auth_service = AuthService()
            from config import get_gcp_service_url
            self.auth_service_url = get_gcp_service_url("auth")
            # Simple implementations for GCP deployment
            class MCPRegistryClient:
                def __init__(self):
                    pass
            
            self.registry_client = MCPRegistryClient()
            self.live_registry = []  # Empty for GCP deployment
            self.service_discovery = ServiceDiscovery(self.registry_client, self.live_registry)
            # Pass discovery model to service discovery for semantic matching
            if self.discovery_model:
                self.service_discovery.discovery_model = self.discovery_model
            self.prompt_generator = PromptGenerator(enable_cache=self.cache_prompt)
            self.app_executor = AppQueryExecutor(self.console, self.verbose)
            
        except Exception as e:
            self.console.print(f"[red][X] CRITICAL: Service initialization failed: {e}[/red]")
            self.console.print("[red]Hard exit - no fallbacks allowed[/red]")
            import sys
            sys.exit(1)
    
    def _print_technical(self, message, **kwargs):
        """Print technical details only in verbose mode."""
        if self.verbose:
            self.console.print(message, **kwargs)
    
    def _print_user_friendly(self, message, **kwargs):
        """Print user-friendly messages in both modes."""
        self.console.print(message, **kwargs)
    
    def _print_step_header(self, step_name: str, step_description: str):
        """Print enhanced step header with structure awareness."""
        if self.verbose:
            # Enhanced technical step header
            structure_info = "Optimized Structure"
            header = create_step_header(step_name, step_description, structure_info, verbose=True)
            self.console.print("\n", header)
        else:
            # In non-verbose mode, create_step_header returns empty string, so don't print anything
            pass
    
    def _print_chat_message(self, sender: str, message: str, style: str = ""):
        """Print enhanced chat-style message."""
        if not self.verbose:
            msg = create_chat_message(sender, message, style)
            self.console.print(msg)
        else:
            self.console.print(f"[{style}]{sender}: {message}[/{style}]" if style else f"{sender}: {message}")
    
    def _register_steps(self):
        """Register all demo steps in order."""
        self.add_step("System Prerequisites", "Check all required services", self.check_system_prerequisites)
        self.add_step("Structure Detection", "Detect repository structure", self.detect_structure)
        self.add_step("Current MCP Servers", "Show available MCP servers", self.show_mcp_server_status)
        self.add_step("Gather Requirements", "Get app requirements from user", self.gather_requirements)
        self.add_step("Discover MCP Servers", "Find servers matching requirements", self.discover_mcp_servers)
        self.add_step("Generate System Prompt", "Create AI assistant prompt", self.generate_system_prompt)
        self.add_step("Configure App", "Set app name and parameters", self.configure_app)
        self.add_step("Create App Instance", "Build the AI app", self.create_app_instance)
        self.add_step("Initialize Components", "Start all app components", self.initialize_app_components)
        self.add_step("Test App", "Run a test query", self.test_app)
        
        if self.save_app:
            self.add_step("Save App", "Save app configuration to disk", self.save_app_to_disk)
        
        if self.first_query and self.auto_mode:
            self.add_step("Run First Query", "Execute the provided first query", self.run_first_query)
    
    def add_step(self, name: str, description: str, func: callable):
        """Add a step to the demo."""
        self.steps.append(DemoStep(name, description, func))
    
    async def run(self):
        """Run the enhanced demo."""
        try:
            self.stats["start_time"] = datetime.now()
            
            # Enhanced welcome with structure info
            if not self.chat_mode:
                await self.show_welcome()
            
            # Auto-login for both modes
            await self._auto_login()
            
            # In default mode (not verbose, not auto), start chat loop directly
            if self.chat_mode and not self.auto_mode:
                await self.chat_loop()
                if self.app:
                    await self.app.stop()
                    self.console.print("\n[green]✓ AI assistant stopped successfully[/green]")
            else:
                # Check for real MCP implementations first
                try:
                    # Simplified GCP-only implementations
                    def create_mcp_client(server_config):
                        return server_config  # Return config for now
                    
                    def get_live_server_registry():
                        return []  # Return empty registry for now
                    
                    class MCPRegistryClient:
                        def __init__(self, registry_url):
                            self.registry_url = registry_url
                    if not self.auto_mode:
                        self.console.print("[green]✓ Real MCP implementations loaded successfully[/green]\n")
                except ImportError as e:
                    self.console.print(f"[dim]! MCP implementations not available: {e}[/dim]\n")
                
                # Check environment (silently in auto mode)
                env_validation = validate_environment_variables(verbose=False)
                if not self.auto_mode:
                    if env_validation['ready_for_production']:
                        self.console.print("[green]✓ Real environment detected - using live API services[/green]\n")
                    else:
                        if os.getenv("NO_DEMO_MODE") != "true":
                            self.console.print("[dim]! Demo environment - some features may use fallbacks[/dim]\n")
                
                # Run each registered step
                for i, step in enumerate(self.steps, 1):
                    if not await self.run_step(i, step):
                        return
                
                # Interactive loop (only in interactive mode)
                if not self.auto_mode:
                    await self.interactive_loop()
                
                # Cleanup
                await self.cleanup_and_summary()
            
        except Exception as e:
            self.console.print(f"\n[red]Error: {e}[/red]")
            if self.app:
                await self.app.stop()
            raise
    
    async def show_welcome(self):
        """Show enhanced welcome screen with structure information."""
        
        # Show title with rocket emoji like v1.2
        self.console.print("[bold]Cogzia Alpha v1.5[/bold]")
        
        if self.auto_mode:
            self.console.print("[yellow]Running in Auto Mode - Using real API services[/yellow]")
            
        # Show authentication status prominently
        if hasattr(self, 'user_context') and self.user_context:
            if not getattr(self.user_context, 'is_demo', True):
                self.console.print(f"[bold green]Signed in as: {self.user_context.email}[/bold green]")
                self.console.print("[dim]Apps will be auto-saved to your library[/dim]")
            else:
                self.console.print("[bold]Running as demo user[/bold]")
                self.console.print("[dim]Use --login to access your personal library[/dim]")
        else:
            self.console.print("[bold yellow]:) Running as demo user[/bold yellow]")
            self.console.print("[dim]Use --login to access your personal library[/dim]")
        
        # Spacing handled by sections
    
    async def _authenticate(self) -> bool:
        """Handle authentication based on flags."""
        # Import here to avoid circular import at module level
        from auth_manager import TUIAuthManager, UserContext, DemoUserContext
        
        # If demo mode explicitly set, use demo credentials
        if self.demo_mode:
            self.user_context = DemoUserContext()
            self.auth_token = "demo_token_123"
            self.auth_mode = "demo"
            return True
        
        # If auth not enabled, use demo by default
        if not self.enable_auth:
            self.user_context = DemoUserContext()
            self.auth_token = "demo_token_123"
            self.auth_mode = "demo"
            return True
        
        # Auth is enabled - try to authenticate
        try:
            auth_manager = TUIAuthManager(auth_url=self.auth_service_url)
            
            # If we have a user context already, use it
            if self.user_context and not isinstance(self.user_context, DemoUserContext):
                self.auth_token = self.user_context.token
                self.auth_mode = "authenticated"
                return True
            
            # If we have a token provided via CLI, verify it
            if self.auth_token:
                user_info = await auth_manager.verify_token(self.auth_token)
                if user_info:
                    self.user_context = UserContext(
                        user_id=user_info.get("id", "unknown"),
                        email=user_info.get("email", "unknown@cogzia.com"),
                        token=self.auth_token,
                        roles=user_info.get("roles", ["user"])
                    )
                    self.auth_mode = "authenticated"
                    return True
            
            # If login flag set, do interactive login
            if self.login:
                result = await auth_manager.interactive_login()
                if result["success"]:
                    self.auth_token = result["token"]
                    self.user_context = auth_manager.current_user
                    self.auth_mode = "authenticated"
                    return True
                else:
                    self.console.print("[dim]! Login failed, falling back to demo mode[/dim]")
            
            # Check for saved token
            saved_token = await auth_manager.load_token()
            if saved_token:
                self.auth_token = saved_token["token"]
                self.user_context = auth_manager.current_user
                self.auth_mode = "authenticated"
                self.console.print(f"[green]✓ Using saved authentication for {self.user_context.email}[/green]")
                return True
        
        except Exception as e:
            if self.verbose:
                self.console.print(f"[red]Authentication error: {e}[/red]")
        
        # Fall back to demo mode
        self.console.print("[yellow]ℹ️ Using demo mode (no authentication)[/yellow]")
        self.user_context = DemoUserContext()
        self.auth_token = "demo_token_123"
        self.auth_mode = "demo"
        return True
    
    async def _auto_login(self) -> bool:
        """Legacy method - now calls _authenticate."""
        result = await self._authenticate()
        # Show authentication status after authentication is complete
        if not self.chat_mode:  # Don't show in chat mode to avoid clutter
            await self._show_auth_status()
        return result
    
    async def _show_auth_status(self):
        """Display current authentication status prominently."""
        from ui_components import AuthenticationStatusBox
        
        auth_box = AuthenticationStatusBox.create(self.user_context)
        self.console.print(auth_box)
    
    async def run_step(self, step_num: int, step: DemoStep) -> bool:
        """Run a single step with enhanced feedback."""
        self.current_step = step_num
        
        # Enhanced step header
        self._print_step_header(step.name, step.description)
        
        # Check if we should stop at this step
        if self.auto_mode and self.auto_step is not None and step_num > self.auto_step:
            self._print_user_friendly(f"\n[yellow]Stopping at step {self.auto_step} as requested[/yellow]")
            return False
        
        # Run the step
        try:
            await step.func()
            return True
        except Exception as e:
            self._print_user_friendly(f"\n[red]Step failed: {e}[/red]")
            if self.verbose:
                import traceback
                self.console.print(traceback.format_exc())
            return False
    
    async def check_system_prerequisites(self):
        """Check system prerequisites."""
        # Check environment variables first
        env_validation = validate_environment_variables(verbose=False)
        
        # Check all services
        service_health = await self.health_checker.check_all_services(SERVICE_DESCRIPTIONS)
        all_ok = all(service_health.values())
        
        # CRITICAL: For auto mode, ALWAYS validate MCP servers can be started
        # This must happen regardless of env vars to prevent "No MCP servers connected" later
        if self.auto_mode and not self.demo_mode:
            mcp_servers_ok = await self._validate_mcp_servers_can_start()
            if not mcp_servers_ok:
                # HARD EXIT: Auto mode requires working MCP servers
                from ui_components import StandardMessages
                
                error_panel = StandardMessages.error(
                    "System Requirements Not Met",
                    "Auto mode requires MCP servers to be operational",
                    recovery="Try running with --demo flag for demo mode",
                    details=[
                        "Pre-flight checks FAILED - cannot proceed",
                        "Check if MCP servers are deployed",
                        "Verify port forwarding is active",
                        "Use --verbose for detailed logs"
                    ]
                )
                self.console.print(error_panel)
                if K8S_ENABLED:
                    self._print_user_friendly("[yellow]   1. Ensure MCP servers are deployed in Kubernetes[/yellow]")
                    self._print_user_friendly("[yellow]   2. Check if MCP Server Manager is running: kubectl get pods -n cogzia-dev | grep mcp[/yellow]")
                    self._print_user_friendly("[yellow]   3. Verify port forwarding: kubectl port-forward -n cogzia-dev svc/mcp-server-manager 30010:10010[/yellow]")
                    self._print_user_friendly("[yellow]   4. Try running with --demo flag for demo mode[/yellow]")
                else:
                    self._print_user_friendly("[yellow]   1. Check if MCP server scripts exist in mcp_ecosystem/examples/[/yellow]")
                    self._print_user_friendly("[yellow]   2. Verify 'uv' is installed and working[/yellow]")
                    self._print_user_friendly("[yellow]   3. Try running with --demo flag for demo mode[/yellow]")
                    self._print_user_friendly("[yellow]   4. Check logs with --verbose flag[/yellow]")
                
                # HARD EXIT
                self.console.print("\n[red bold]EXITING: System requirements not met for auto mode[/red bold]")
                sys.exit(1)
        
        # Now show status based on what we found
        if self.verbose or self.debug_level != DebugLevel.NONE:
            # Show detailed table
            table = create_service_table(SERVICE_DESCRIPTIONS)
            
            for service_name, config in SERVICE_DESCRIPTIONS.items():
                status = "✓ Live" if service_health.get(service_name, False) else "✗ Down"
                port_str = str(config["port"]) if config["port"] else "N/A"
                
                table.add_row(
                    service_name,
                    port_str,
                    status,
                    config["purpose"],
                    "Optimized"
                )
            
            self.console.print(table)
        
        # Show appropriate status message (only in verbose mode)
        if self.auto_mode and env_validation['ready_for_production']:
            if self.verbose:
                self._print_user_friendly("[green]✓ Environment ready - using real API services[/green]")
                validate_environment_variables(verbose=True)
        elif all_ok:
            if not self.auto_mode:
                self._print_user_friendly(f"[green]✓ Services are ready[/green]")
        else:
            # Different behavior for demo mode vs other modes
            if self.demo_mode:
                self._print_user_friendly(f"[blue]ℹ️ Running in demo mode with simulated services.[/blue]")
            else:
                self._print_user_friendly(f"[dim]! Some required services aren't running. Consider --demo flag for simulation.[/dim]")
    
    async def _validate_mcp_servers_can_start(self) -> bool:
        """
        CRITICAL PRE-FLIGHT CHECK: Validate that MCP servers can actually be started.
        
        This is a HARD EXIT check for auto mode. If MCP servers can't be started,
        the script should exit immediately rather than failing later with "No MCP servers connected".
        
        Returns:
            bool: True if at least one MCP server can be started, False otherwise
        """
        try:
            if self.verbose:
                self._print_technical("[cyan]Pre-flight: Testing MCP server availability...[/cyan]")
            
            # Check for GCP deployment first
            if os.getenv("REQUIRE_REAL_SERVICES") == "true":
                if self.verbose:
                    self._print_technical("[dim]  Running in GCP mode - checking MCP registry...[/dim]")
                
                # Check GCP MCP Registry
                try:
                    async with httpx.AsyncClient(timeout=10.0) as client:
                        response = await client.get(f"{MCP_REGISTRY_URL}/servers")
                        if response.status_code == 200:
                            data = response.json()
                            servers = data.get('results', [])
                            if servers:
                                if self.verbose:
                                    self._print_technical(f"[green]✓ Found {len(servers)} MCP servers in GCP registry[/green]")
                                    for server in servers:
                                        self._print_technical(f"[dim]    - {server.get('name', 'Unknown')} server[/dim]")
                                return True
                            else:
                                if self.verbose:
                                    self._print_technical("[dim]! No MCP servers found in GCP registry[/dim]")
                                return False
                        else:
                            if self.verbose:
                                self._print_technical(f"[red]MCP Registry returned status {response.status_code}[/red]")
                            return False
                except Exception as e:
                    if self.verbose:
                        self._print_technical(f"[red]Cannot check GCP MCP registry: {e}[/red]")
                    return False
            
            # In K8s mode, check if MCP servers are deployed as services
            elif K8S_ENABLED:
                if self.verbose:
                    self._print_technical("[dim]  Running in Kubernetes mode - checking MCP server pods...[/dim]")
                
                # Check K8s pods directly
                try:
                    if get_k8s_mcp_servers:
                        k8s_servers = get_k8s_mcp_servers()
                        if k8s_servers:
                            if self.verbose:
                                self._print_technical(f"[green]✓ Found {len(k8s_servers)} running MCP servers in K8s[/green]")
                                for server in k8s_servers:
                                    self._print_technical(f"[dim]    - {server['name']} server (pod: {server['pod_name']})[/dim]")
                            return True
                        else:
                            if self.verbose:
                                self._print_technical("[dim]! No running MCP servers found in K8s[/dim]")
                                self._print_technical("[yellow]   MCP servers need to be deployed as K8s pods[/yellow]")
                            return False
                    else:
                        # Fallback to MCP Server Manager check
                        async with httpx.AsyncClient() as client:
                            response = await client.get(f"{MCP_SERVER_MANAGER_URL}/servers", timeout=3.0)
                            if response.status_code == 200:
                                servers_data = response.json()
                                # For K8s, just check if we have any servers registered
                                if servers_data:
                                    if self.verbose:
                                        self._print_technical(f"[green]✓ Found {len(servers_data)} MCP servers registered[/green]")
                                    return True
                                else:
                                    if self.verbose:
                                        self._print_technical("[dim]! No MCP servers registered[/dim]")
                                    return False
                            else:
                                if self.verbose:
                                    self._print_technical(f"[red]MCP Server Manager returned status {response.status_code}[/red]")
                                return False
                except Exception as e:
                    if self.verbose:
                        self._print_technical(f"[red]Cannot check MCP servers: {e}[/red]")
                    return False
            else:
                # Local mode - try to start servers as processes
                if self.verbose:
                    self._print_technical("[dim]  Running in local mode - testing server startup...[/dim]")
                
                # Test if we can start at least one essential MCP server
                essential_servers = ["time", "calculator", "fortune"]
                servers_started = 0
                
                for server_type in essential_servers:
                    try:
                        if self.verbose:
                            self._print_technical(f"[dim]  Testing {server_type} server startup...[/dim]")
                        
                        # Try to ensure server is running
                        server_info = await self.live_registry.ensure_server_running(server_type)
                        if server_info and server_info.port:
                            servers_started += 1
                            if self.verbose:
                                self._print_technical(f"[green]  ✓ {server_type} server: port {server_info.port}[/green]")
                            
                            # Stop it immediately after testing (cleanup)
                            try:
                                await self.live_registry.stop_server(server_info.instance_id)
                            except:
                                pass  # Ignore cleanup errors
                            
                            break  # One successful startup is enough for pre-flight
                        
                    except Exception as e:
                        if self.verbose:
                            self._print_technical(f"[red]  ✗ {server_type} server failed: {e}[/red]")
                        continue
                
                if servers_started == 0:
                    if self.verbose:
                        self._print_technical("[red][X] PRE-FLIGHT FAILED: No MCP servers can be started[/red]")
                        self._print_technical("[red]   This is a HARD EXIT condition for auto mode[/red]")
                    else:
                        self._print_user_friendly("[red][X] CRITICAL: No MCP servers available[/red]")
                        self._print_user_friendly("[red]   Cannot proceed with auto mode - MCP servers required[/red]")
                    return False
                else:
                    if self.verbose:
                        self._print_technical(f"[green]✓ Pre-flight: MCP servers can be started ({servers_started} tested)[/green]")
                    return True
                
        except Exception as e:
            if self.verbose:
                self._print_technical(f"[red][X] PRE-FLIGHT FAILED: MCP server validation error: {e}[/red]")
            else:
                self._print_user_friendly(f"[red][X] CRITICAL: MCP server system error: {e}[/red]")
            return False
    
    async def detect_structure(self):
        """Detect and display repository structure information."""
        # Skip structure detection output in auto mode
    
    async def show_mcp_server_status(self):
        """Show current MCP server status with enhanced display."""
        # Skip MCP server status in auto mode to reduce clutter
        if self.auto_mode:
            return
        
        self._print_user_friendly("\n[bold]Available Development Tools[/bold]")
        
        # Skip localhost MCP servers for GCP mode with real services
        if os.getenv("SKIP_MCP_INITIALIZATION") == "true" and os.getenv("REQUIRE_REAL_SERVICES") == "true":
            self._print_user_friendly("[green]✓ Using Cloud Run MCP servers (authenticated)[/green]")
            self._print_user_friendly("[dim]   • time: https://mcp-time-*.run.app[/dim]")
            self._print_user_friendly("[dim]   • calculator: https://mcp-calculator-*.run.app[/dim]") 
            self._print_user_friendly("[dim]   • brave-search: https://mcp-brave-search-*.run.app[/dim]")
            return
        
        # Create status table
        status_table = Table(title="MCP Server Status", show_header=True, header_style="bold cyan")
        status_table.add_column("Server", style="cyan")
        status_table.add_column("Port", style="magenta")
        status_table.add_column("Status", style="green")
        status_table.add_column("Capabilities", style="blue")
        
        # Map server names to display names and capabilities
        server_info_map = {
            "time": ("time-mcp-server", "Time, Timezone, Date Operations"),
            "calculator": ("calculator-mcp-server", "Math, Calculations, Formulas"),
            "filesystem": ("filesystem-mcp-server", "File Operations"),
            "fortune": ("fortune-mcp-server", "Fortune Messages"),
            "weather": ("weather-mcp-server", "Weather Information"),
            "brave_search": ("brave-search-mcp-server", "Web Search via Brave API"),
            "workflow_system": ("workflow-system-mcp-server", "AI Workflow Patterns")
        }
        
        # Get K8s server status if available
        k8s_running_servers = set()
        if K8S_ENABLED and get_k8s_mcp_servers:
            k8s_servers = get_k8s_mcp_servers()
            k8s_running_servers = {s['name'] for s in k8s_servers}
        
        try:
            # Query MCP Server Manager for all servers
            async with httpx.AsyncClient() as client:
                # Use K8s URL if in K8s mode
                mcp_url = MCP_SERVER_MANAGER_URL if K8S_ENABLED else "http://localhost:10010"
                response = await client.get(f"{mcp_url}/servers", timeout=3.0)
                if response.status_code == 200:
                    servers_data = response.json()
                    
                    # Process each server from the manager
                    for server in servers_data:
                        server_name = server['name']
                        
                        # Skip duplicate brave-search entry
                        if server_name == 'brave-search-mcp-server':
                            continue
                        
                        # Get display info
                        if server_name in server_info_map:
                            display_name, capabilities = server_info_map[server_name]
                        else:
                            # Fallback for unknown servers
                            display_name = f"{server_name}-mcp-server"
                            capabilities = server_name.replace('_', ' ').title()
                        
                        # Determine status
                        port = server.get('port', 'N/A')
                        manager_status = server.get('status', '').lower()
                        health_status = server.get('health_status', '').lower()
                        
                        # In K8s mode, check if server is running as a pod
                        if K8S_ENABLED and server_name in k8s_running_servers:
                            status = "[•] Active"
                            # Show K8s service port instead of local port
                            port = ":8080"  # Standard MCP server port in K8s
                        elif manager_status == 'running' and health_status == 'healthy':
                            status = "[•] Active"
                        elif manager_status == 'running':
                            status = "[o] Running"
                        elif manager_status == 'stopped' or health_status == 'not_running':
                            status = "[x] Offline"
                        else:
                            status = "[?] Unknown"
                        
                        status_table.add_row(display_name, f":{port}", status, capabilities)
                else:
                    # MCP Server Manager returned error - FAIL HARD
                    self.console.print(f"\n[red][X] ERROR: MCP Server Manager returned status {response.status_code}[/red]")
                    self.console.print("   MCP Server Manager must be running to show server status.")
                    self.console.print("   Start it with: ./start-services.sh --services mcp-server-manager")
                    self.console.print("\n[red]Hard exit - no fallbacks allowed[/red]")
                    import sys
                    sys.exit(1)
                        
        except Exception as e:
            # Cannot reach MCP Server Manager - FAIL HARD
            mcp_url = MCP_SERVER_MANAGER_URL if K8S_ENABLED else "http://localhost:10010"
            self.console.print(f"\n[red][X] ERROR: Cannot connect to MCP Server Manager at {mcp_url}[/red]")
            self.console.print(f"   Error: {str(e)}")
            self.console.print("   MCP Server Manager must be running to show server status.")
            self.console.print("   Start it with: ./start-services.sh --services mcp-server-manager")
            self.console.print("\n[red]Hard exit - no fallbacks allowed[/red]")
            import sys
            sys.exit(1)
        
        self.console.print(status_table)
        
        # Show structure-specific info
        self._print_user_friendly("[dim]Using optimized repository structure for enhanced tool discovery[/dim]")
    
    async def gather_requirements(self):
        """Gather app requirements from user."""
        if self.auto_mode:
            # Enhanced auto mode output
            self._print_user_friendly("\n[bold cyan]Requirements Gathering[/bold cyan]")
            self._print_user_friendly(f"[green]✓ Auto mode requirements:[/green] {self.auto_requirements}")
            
            # Show requirements breakdown
            requirements_panel = Panel(
                f"[bold]Target Application:[/bold]\n{self.auto_requirements}\n\n"
                f"[dim]This will help us find the right tools and capabilities for your app.[/dim]",
                title="[bold]App Requirements[/bold]",
                border_style="cyan",
                expand=True
            )
            self.console.print(requirements_panel)
            
            self.app_config["requirements"] = self.auto_requirements
        else:
            # Interactive mode
            self._print_user_friendly("\n[bold cyan]Tell us what you want to build[/bold cyan]")
            requirements = await asyncio.get_event_loop().run_in_executor(
                None,
                input,
                "\nDescribe your app requirements: "
            )
            self.app_config['requirements'] = requirements.strip() if requirements.strip() else self.auto_requirements
            
            # Show requirements panel
            req_panel = Panel(
                f"[bold]Your AI Assistant will:[/bold]\n\n"
                f"• {self.app_config['requirements']}\n\n"
                f"[dim]Now I'll find the right tools to make this happen...[/dim]",
                title="[bold]Requirements Captured[/bold]",
                border_style="green",
                expand=True
            )
            self.console.print(req_panel)
    
    async def discover_mcp_servers(self):
        """Discover MCP servers matching requirements."""
        import time
        
        self._print_user_friendly("\n[bold cyan]Discovering Available Tools[/bold cyan]")
        
        # Get the current model being used
        current_model = os.getenv('ANTHROPIC_MODEL', 'claude-sonnet-4-20250514')
        self._print_user_friendly(f"[dim]Using model: {current_model}[/dim]")
        
        # Show search panel
        search_panel = Panel(
            f"[bold]Searching for tools that can:[/bold]\n"
            f"• {self.app_config['requirements']}\n\n"
            f"[dim]Analyzing {len(self.app_config['requirements'].split())} requirement keywords...[/dim]",
            title="Tool Discovery",
            border_style="yellow",
            expand=True
        )
        self.console.print(search_panel)
        
        # Discover servers with progress
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
            task = progress.add_task("Connecting to MCP Registry...", total=100)
            
            try:
                progress.update(task, description="Discovering servers...", advance=50)
                
                # Start timing the discovery call
                start_time = time.time()
                
                discovered_servers, server_details = await self.service_discovery.discover_servers(
                    self.app_config['requirements'],
                    auto_start=True
                )
                
                # Enhance discovery with universal server priority
                try:
                    from universal_discovery import UniversalServerDiscovery
                    universal_discovery = UniversalServerDiscovery()
                    discovered_servers, server_details = universal_discovery.enhance_discovery_results(
                        discovered_servers, server_details, self.app_config['requirements']
                    )
                    if self.verbose:
                        self.console.print("[dim]Universal server discovery enhancement applied[/dim]")
                except ImportError:
                    if self.verbose:
                        self.console.print("[dim]Universal discovery module not available, continuing with standard discovery[/dim]")
                except Exception as e:
                    if self.verbose:
                        self.console.print(f"[dim]Universal discovery enhancement failed: {e}, continuing with standard discovery[/dim]")
                
                # Calculate elapsed time
                elapsed_time = time.time() - start_time
                
                progress.update(task, description="Complete!", advance=50)
                
                # Print timing information
                if elapsed_time < 0.5:
                    self._print_user_friendly(f"[cyan]✓ Discovery completed in {elapsed_time:.3f} seconds (cached)[/cyan]")
                else:
                    self._print_user_friendly(f"[green]✓ Discovery completed in {elapsed_time:.2f} seconds[/green]")
                
            except Exception as e:
                self.console.print(f"[red][X] CRITICAL: Tool discovery failed: {e}[/red]")
                self.console.print("[red]Hard exit - no fallbacks allowed[/red]")
                import sys
                sys.exit(1)
        
        # Store server details for later use
        self.server_details = server_details
        
        # Filter servers by relevance (medium or high only)
        relevant_servers = []
        for server in discovered_servers:
            relevance_score = server_details.get(server, {}).get('relevance', 0.0)
            if relevance_score >= 0.5:  # Medium (0.5) or High (0.8+)
                relevant_servers.append(server)
        
        # Update app config with filtered servers
        if relevant_servers:
            self.app_config['servers'] = relevant_servers[:3]  # Limit to 3 servers
        else:
            # No servers with medium/high relevance
            if not self.auto_mode:
                # Interactive mode - ask user
                self._print_user_friendly("\n[yellow][!] No tools found with medium or high relevance[/yellow]")
                self._print_user_friendly("[yellow]The following tools have low relevance:[/yellow]")
                for server in discovered_servers[:3]:
                    relevance_score = server_details.get(server, {}).get('relevance', 0.0)
                    self._print_user_friendly(f"  • {server} (relevance: {relevance_score:.2f})")
                
                use_low = await asyncio.get_event_loop().run_in_executor(
                    None,
                    input,
                    "\nWould you like to use these low-relevance tools anyway? (y/N): "
                )
                if use_low.lower() == 'y':
                    self.app_config['servers'] = discovered_servers[:3]
                else:
                    self.app_config['servers'] = []
            else:
                # Auto mode - skip low relevance servers
                self._print_user_friendly("\n[yellow][!] No tools found with medium or high relevance - proceeding without tools[/yellow]")
                self.app_config['servers'] = []
        
        # Display results
        if discovered_servers:
            # Enhanced table display like v1.2
            results_table = Table(title="Found Tools", show_header=True, header_style="bold cyan")
            results_table.add_column("Tool", style="cyan")
            results_table.add_column("Capability", style="green", width=30)
            results_table.add_column("Relevance", style="yellow")
            results_table.add_column("Status", style="magenta")
            
            for server in discovered_servers[:5]:
                details = server_details.get(server, {})
                capabilities = ', '.join(details.get('capabilities', [])[:2])
                
                # Check if universal server
                is_universal = details.get('is_universal', False)
                if is_universal:
                    status = "[green]✓ No API key[/green]"
                else:
                    status = "[dim]API key needed[/dim]"
                
                # Use actual relevance from discovery
                relevance_score = details.get('relevance', 0.5)
                if relevance_score >= 0.8:
                    relevance = "[green]High[/green]"
                elif relevance_score >= 0.5:
                    relevance = "[cyan]Medium[/cyan]"
                else:
                    relevance = "[dim]Low[/dim]"
                results_table.add_row(server, capabilities, relevance, status)
            
            self.console.print(results_table)
            
            # Show selection summary
            selected_count = len(self.app_config.get('servers', []))
            if selected_count > 0:
                self._print_user_friendly(f"\n[green]✓ Selected {selected_count} tools for your app[/green]")
                selected_names = []
                universal_count = 0
                for server in self.app_config['servers']:
                    details = server_details.get(server, {})
                    relevance_score = details.get('relevance', 0.0)
                    is_universal = details.get('is_universal', False)
                    
                    if is_universal:
                        universal_count += 1
                        selected_names.append(f"{server} [green]✓[/green]")
                    elif relevance_score >= 0.8:
                        selected_names.append(f"{server} (High)")
                    else:
                        selected_names.append(f"{server} (Medium)")
                
                self._print_user_friendly(f"[dim]Selected: {', '.join(selected_names)}[/dim]")
                
                if universal_count > 0:
                    self._print_user_friendly(f"[green]{universal_count} universal server(s) selected - no API keys needed![/green]")
                
                if server_details:
                    self._print_user_friendly("[dim]Using real MCP servers with live connections[/dim]")
            else:
                self._print_user_friendly("\n[yellow][!] No tools selected - app will use general capabilities only[/yellow]")
        else:
            self._print_user_friendly("[yellow]No specific tools found, using general assistant capabilities[/yellow]")
    
    async def generate_system_prompt(self):
        """Generate system prompt for the AI app."""
        self._print_user_friendly("\n[bold cyan]Creating AI Assistant Personality[/bold cyan]")
        
        # Show generation panel
        cache_status = "[green]💾 Caching enabled[/green]" if self.cache_prompt else ""
        gen_panel = Panel(
            f"[bold]Crafting instructions for:[/bold]\n"
            f"• App: {self.app_config.get('app_name', 'Custom AI App')}\n"
            f"• Purpose: {self.app_config['requirements']}\n"
            f"• Tools: {', '.join(self.app_config['servers'])}\n"
            f"{cache_status}\n"
            f"[dim]This creates the AI's personality and capabilities...[/dim]",
            title="[bold]System Prompt Generation[/bold]",
            border_style="cyan",
            expand=True
        )
        self.console.print(gen_panel)
        
        # Generate prompt with streaming (fallback to local generation if needed)
        prompt_parts = []
        
        # Use Rich Live display for smooth streaming (v1.4 style)
        from rich.live import Live
        from rich.text import Text
        
        # Create initial display text
        current_display = Text()
        
        # Create live display outside the if block
        live_display = Live(current_display, console=self.console.console, refresh_per_second=10, transient=False)
        
        def on_chunk(chunk):
            prompt_parts.append(chunk)
            if not self.verbose:
                # Update live display with accumulated text
                current_display.append(chunk)
                live_display.update(current_display)
        
        try:
            # Get server capabilities if available
            server_capabilities = {}
            if hasattr(self, 'server_details'):
                for server in self.app_config['servers']:
                    if server in self.server_details:
                        caps = self.server_details[server].get('capabilities', [])
                        if caps:
                            # Pass capabilities as a list of strings
                            server_capabilities[server] = caps
            
            # Debug: print what we're passing
            if self.verbose:
                self.console.print(f"[dim]DEBUG: Requirements: {self.app_config['requirements']}[/dim]")
                self.console.print(f"[dim]DEBUG: Servers: {self.app_config['servers']}[/dim]")
                self.console.print(f"[dim]DEBUG: Server capabilities: {server_capabilities}[/dim]")
            
            # Start the live display (only in non-verbose mode)
            if not self.verbose:
                live_display.start()
                
            async for chunk in self.prompt_generator.generate_system_prompt_stream(
                self.app_config['requirements'],
                self.app_config['servers'],
                server_capabilities=server_capabilities,
                on_chunk=on_chunk
            ):
                # In verbose mode, print chunks directly
                if self.verbose:
                    self.console.print(chunk, end="")
                    prompt_parts.append(chunk)
            
            # Stop the live display (clear it after streaming)
            if not self.verbose:
                live_display.stop()
            
            self.app_config['system_prompt'] = ''.join(prompt_parts)
        except Exception as e:
            # Stop the live display if it's running
            if not self.verbose and hasattr(locals(), 'live_display'):
                try:
                    live_display.stop()
                except:
                    pass
            
            import traceback
            self.console.print(f"[red][X] CRITICAL: System prompt generation failed: {e}[/red]")
            if self.verbose:
                traceback.print_exc()
            self.console.print("[red]Hard exit - no fallbacks allowed[/red]")
            import sys
            sys.exit(1)
        
        # Only show full prompt panel in verbose mode to avoid duplication
        if self.verbose:
            prompt_panel = Panel(
                self.app_config['system_prompt'],
                title="Generated System Prompt",
                border_style="cyan",
                expand=True
            )
            self.console.print(prompt_panel)
        else:
            # In non-verbose mode, just show a brief completion message
            self._print_user_friendly("[green]✓ System prompt generated successfully[/green]")
    
    async def configure_app(self):
        """Configure app settings."""
        self._print_user_friendly("\n[bold]Configuring Your App[/bold]")
        
        # Generate app name based on requirements
        req_words = self.app_config['requirements'].split()[:3]
        app_name = ' '.join(word.capitalize() for word in req_words) + " Assistant"
        self.app_config['app_name'] = app_name
        
        # Show configuration tree like v1.2
        self.console.print(f"\n[bold]{app_name}[/bold]")
        self.console.print(f"├── Purpose: {self.app_config['requirements']}")
        self.console.print(f"├── Tools: {', '.join(self.app_config['servers'])}")
        self.console.print(f"└── Structure: Optimized Repository Structure")
        
        self._print_user_friendly(f"\n[green]✓ App configured as '{app_name}'[/green]")
    
    async def create_app_instance(self):
        """Create the actual AI app instance."""
        self._print_user_friendly("\n[bold]Building Your AI App[/bold]")
        
        # Generate app ID
        app_id = generate_app_id()
        
        # Create app instance with user context
        self.app = MinimalAIApp(
            app_id=app_id,
            system_prompt=self.app_config['system_prompt'],
            mcp_servers=self.app_config['servers'],
            verbose=self.verbose,
            auto_mode=self.auto_mode,
            user_context=self.user_context
        )
        
        # Show creation success
        self._print_user_friendly(f"[green]✓ Created app: {self.app_config['app_name']}[/green]")
        self._print_user_friendly(f"[green]✓ App ID: {app_id}[/green]")
        self._print_user_friendly(f"[green]✓ Configured with {len(self.app_config['servers'])} MCP server(s)[/green]")
        self._print_user_friendly("[green]✓ System prompt applied[/green]")
        
        # Show tree structure like v1.2
        tree_display = f"""[cyan]{self.app_config['app_name']}[/cyan]
├── ID: {app_id}
├── Host: {self.app_config['app_name']} v1.0.0
│   └── Capabilities: ['search', 'streaming', 'multi-tool']
├── Client: Anthropic (claude-opus-4-20250514)
└── Servers:"""
        
        for i, server in enumerate(self.app_config['servers']):
            if i < len(self.app_config['servers']) - 1:
                tree_display += f"\n    ├── {server}"
            else:
                tree_display += f"\n    └── {server}"
            tree_display += f"\n        └── Status: Ready to connect"
        
        self.console.print(tree_display)
        
        # Auto-save to cloud for authenticated users (even without --save flag)
        if self.verbose:
            self._print_user_friendly(f"[dim]DEBUG: user_context={self.user_context}[/dim]")
            if self.user_context:
                self._print_user_friendly(f"[dim]DEBUG: is_demo={self.user_context.is_demo}[/dim]")
        
        if self.user_context and not self.user_context.is_demo:
            try:
                # Save to cloud storage automatically for authenticated users
                from cloud_storage_adapter import CloudStorageAdapter
                storage = CloudStorageAdapter(self.user_context.token, auth_manager=self.auth_manager)
                
                self._print_user_friendly("[dim]Auto-saving to cloud...[/dim]")
                success = await storage.save_app(self.app.app_id, self.app_config)
                
                if success:
                    self._print_user_friendly(f"[green]✓ Auto-saved to cloud! ({self.user_context.email})[/green]")
                else:
                    self._print_user_friendly(f"[red][X] Cloud save failed - app not saved[/red]")
            except Exception as e:
                # Don't fail app creation if save fails
                self._print_user_friendly(f"[yellow]Warning: Could not auto-save to cloud: {e}[/yellow]")
    
    async def initialize_app_components(self):
        """Initialize all app components."""
        self._print_user_friendly("\n[bold]Starting App Components[/bold]")
        
        # Actually start the app
        try:
            await self.app.start()
            
            # Show component status table
            components = [
                ("AI Model", "✓ Ready"),
                ("Tool Registry", "✓ Ready"),
                ("Memory System", "✓ Ready"),
                ("Safety Filters", "✓ Ready"),
                ("API Gateway", "✓ Ready" if os.getenv('ANTHROPIC_API_KEY') else "! Demo Mode")
            ]
            
            component_table = create_component_table(components)
            self.console.print(component_table)
            
            self.console.print("\n[green]✓ App started successfully![/green]")
            self.console.print(f"[dim]App ID: {self.app.app_id}[/dim]")
            
        except Exception as e:
            self.console.print(f"[yellow]App initialization issue: {e}[/yellow]")
            self.console.print("[dim]Continuing with fallback mode...[/dim]")
    
    async def test_app(self):
        """Test the created app with a relevant query."""
        self._print_user_friendly("\n[bold]Testing Your App[/bold]")
        
        # Generate or use test query
        if self.auto_mode:
            test_query = generate_test_query(self.app_config['requirements'])
        else:
            test_query = "Tell me something interesting about the topic I'm interested in"
        
        # Show test setup
        test_panel = Panel(
            f"[bold]Running Test Query:[/bold]\n\n"
            f"[cyan]Query:[/cyan] {test_query}\n\n"
            f"[dim]This will verify that your app can process requests correctly.[/dim]",
            title="[bold]App Test[/bold]",
            border_style="purple",
            expand=True
        )
        self.console.print(test_panel)
        
        # Execute the test
        await self.app_executor.execute_query(self.app, test_query, show_chat_ui=not self.verbose)
    
    async def save_app_to_disk(self):
        """Save app configuration to cloud storage."""
        self._print_user_friendly("\n[bold cyan]Saving Your App to Cloud[/bold cyan]")
        
        # Import cloud storage
        from cloud_storage_adapter import CloudStorageAdapter
        
        # Get auth token
        auth_token = None
        if self.user_context and not self.user_context.is_demo:
            auth_token = self.user_context.token
        
        # Show save panel
        save_panel = Panel(
            f"[bold]Saving to Cloud Storage:[/bold]\n\n"
            f"[cyan]App ID:[/cyan] {self.app.app_id}\n"
            f"[cyan]Storage:[/cyan] MongoDB (Cloud)\n"
            f"[cyan]Status:[/cyan] Secure & Backed Up\n\n"
            f"[dim]Your app is saved in the cloud and accessible from any device![/dim]",
            title="[bold]Cloud Save[/bold]",
            border_style="cyan",
            expand=True
        )
        self.console.print(save_panel)
        
        # Save to cloud
        storage = CloudStorageAdapter(auth_token, auth_manager=self.auth_manager)
        
        try:
            success = await storage.save_app(self.app.app_id, self.app_config)
            
            if success:
                if self.verbose:
                    self.console.print("[green]✓ App saved to cloud storage successfully![/green]")
                
                # Show cloud save complete panel
                complete_panel = Panel(
                    f"[bold]App Saved to Cloud![/bold]\n\n"
                    f"[cyan]Storage:[/cyan] Cloud (MongoDB)\n"
                    f"[cyan]App ID:[/cyan] {self.app.app_id}\n\n"
                    f"Your app is securely stored in the cloud and\n"
                    f"accessible from any device with your account!\n\n"
                    f"[bold]Quick Access Commands:[/bold]\n"
                    f"• [cyan]--last[/cyan] - Use your most recent app\n"
                    f"• [cyan]--quick '{self.app_config['app_name']}'[/cyan] - Search by name\n"
                    f"• [cyan]--continue {self.app.app_id}[/cyan] - Resume this app",
                    title="[bold]Cloud Save Complete[/bold]",
                    border_style="green",
                    expand=True
                )
                self.console.print(complete_panel)
            else:
                self._print_user_friendly("[yellow][!] Cloud save failed[/yellow]")
                self._print_user_friendly("[dim]Login to enable cloud saves[/dim]")
                
        except Exception as e:
            if self.verbose:
                self.console.print(f"[red]Error saving to cloud: {e}[/red]")
            self._print_user_friendly(f"[red][X] Cloud save failed: {e}[/red]")
            self._print_user_friendly("[yellow]Please check your connection and try again[/yellow]")
        
        self.console.print()
    
    
    async def run_first_query(self):
        """Run the first query provided via command line."""
        if self.first_query:
            self._print_user_friendly("\n[bold cyan]Running your query...[/bold cyan]")
            await self.app_executor.execute_query(self.app, self.first_query)
    
    async def interactive_loop(self):
        """Allow multiple queries in interactive mode."""
        while True:
            self.console.print(f"\n[yellow]Would you like to try another query?[/yellow]")
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                input,
                "Enter 'y' for yes or 'n' for no: "
            )
            
            if response.lower() != 'y':
                break
            
            # Get another query
            query = await asyncio.get_event_loop().run_in_executor(
                None,
                input,
                "\nEnter your query: "
            )
            
            # Execute the query
            await self.app_executor.execute_query(self.app, query)
    
    async def chat_loop(self):
        """Run an interactive chat loop."""
        from ui_components import AuthenticationStatusBox
        
        # Show authentication status at chat start
        auth_box = AuthenticationStatusBox.create(self.user_context, compact=True)
        self.console.print(auth_box)
        
        self._print_user_friendly("\n[bold cyan]Welcome to Chat Mode![/bold cyan]")
        self._print_user_friendly("[dim]I'll help you create an AI assistant based on your needs.[/dim]")
        self._print_user_friendly("[dim]Just tell me what kind of assistant you want to build![/dim]")
        self._print_user_friendly("[dim]Type '/help' for commands or 'quit' to exit.[/dim]\n")
        
        while not self.in_chat_loop:
            try:
                # Get user input with "User: " prompt
                user_input = await asyncio.get_event_loop().run_in_executor(
                    None, input, "\nUser: "
                )
                
                if not user_input.strip():
                    continue
                
                # Handle exit commands
                if user_input.lower() in ['quit', 'exit', 'q']:
                    self._print_user_friendly("\n[yellow]Chat ended. Goodbye![/yellow]")
                    break
                
                # Handle help command
                if user_input.strip() == '/help':
                    help_text = """
[bold cyan]Available Commands:[/bold cyan]
  /help     - Show this help message
  /save     - Save the current app configuration
  /status   - Show app status
  /agency   - Show agent configuration and MCP connections
  /restart  - Create a new app
  quit      - Exit chat mode

[dim]Or just type naturally to interact with your assistant![/dim]
"""
                    self.console.print(help_text)
                    continue
                
                # Handle other commands
                if user_input.startswith('/'):
                    await self._handle_chat_command(user_input)
                else:
                    # Natural language input
                    await self._handle_natural_input(user_input)
                    
            except KeyboardInterrupt:
                self._print_user_friendly("\n[yellow]Chat ended. Goodbye![/yellow]")
                break
            except Exception as e:
                self._print_user_friendly(f"[red]Error: {e}[/red]")
    
    async def _handle_chat_command(self, command: str):
        """Handle chat commands."""
        cmd = command.lower().strip()
        
        if cmd == '/save':
            if self.app:
                await self.save_app_to_disk()
            else:
                self._print_user_friendly("[yellow]No app to save yet. Create one first![/yellow]")
        elif cmd == '/status':
            if self.app:
                self._print_user_friendly(f"[green]✓ App '{self.app_config['app_name']}' is running[/green]")
                self._print_user_friendly(f"[dim]App ID: {self.app.app_id}[/dim]")
                self._print_user_friendly(f"[dim]Tools: {', '.join(self.app_config['servers'])}[/dim]")
            else:
                self._print_user_friendly("[yellow]No app created yet.[/yellow]")
        elif cmd == '/restart':
            if self.app:
                await self.app.stop()
            self.app = None
            self._print_user_friendly("[green]Ready to create a new app! Tell me what you need.[/green]")
        elif cmd == '/agency':
            await self._show_agency_info()
        else:
            self._print_user_friendly(f"[yellow]Unknown command: {command}[/yellow]")
    
    async def _show_agency_info(self):
        """Display current agent configuration and MCP connections."""
        if not self.app:
            self._print_user_friendly("[yellow]No app created yet.[/yellow]")
            return
        
        # Header
        self._print_user_friendly("\n[bold cyan]🤖 Agent Configuration[/bold cyan]")
        
        # App info
        self._print_user_friendly(f"├── App: {self.app_config.get('app_name', 'Unknown')} ({self.app.app_id})")
        
        # LLM Client info
        self._print_user_friendly("├── LLM Client:")
        if self.app.llm_client:
            # Get model from environment
            model = os.getenv('ANTHROPIC_MODEL', 'claude-sonnet-4-20250514')
            self._print_user_friendly(f"│   ├── Status: ✓ Connected")
            self._print_user_friendly(f"│   └── Model: {model} (from ANTHROPIC_MODEL env)")
        else:
            self._print_user_friendly(f"│   └── Status: ❌ Not connected")
        
        # System prompt (truncated)
        prompt_preview = self.app.system_prompt[:500] + "..." if len(self.app.system_prompt) > 500 else self.app.system_prompt
        self._print_user_friendly(f"├── System Prompt: {prompt_preview.split(chr(10))[0]}... [truncated]")
        
        # MCP Servers
        server_count = len(self.app.mcp_servers)
        self._print_user_friendly(f"└── MCP Servers ({server_count} configured):")
        
        # For each configured server
        for i, server_name in enumerate(self.app.mcp_servers):
            is_last = i == server_count - 1
            prefix = "    └──" if is_last else "    ├──"
            
            # Check if server is connected
            if self.app.mcp_client and hasattr(self.app.mcp_client, 'connections'):
                # Try different name variations to find the connection
                connection = None
                canonical_name = server_name.replace("-mcp-server", "").replace("_mcp_server", "")
                
                # Try exact name first, then canonical name
                for name_variant in [server_name, canonical_name]:
                    connection = self.app.mcp_client.connections.get(name_variant)
                    if connection:
                        break
                
                if connection and connection.connected:
                    status = "✓ Connected"
                    # Try to get tools for this server
                    try:
                        # Use the name that worked for the connection
                        tools = await self.app.mcp_client.list_tools(connection.server_id)
                        tool_names = [t.name for t in tools] if tools else []
                    except:
                        tool_names = []
                else:
                    status = "❌ Failed to connect"
                    tool_names = []
            else:
                status = "❓ Unknown"
                tool_names = []
            
            self._print_user_friendly(f"{prefix} {server_name}")
            
            # Status line
            if is_last:
                self._print_user_friendly(f"        ├── Status: {status}")
            else:
                self._print_user_friendly(f"    │   ├── Status: {status}")
            
            # Tools line
            if tool_names:
                tools_str = ", ".join(tool_names)
                if is_last:
                    self._print_user_friendly(f"        └── Tools: {tools_str}")
                else:
                    self._print_user_friendly(f"    │   └── Tools: {tools_str}")
            else:
                if is_last:
                    self._print_user_friendly(f"        └── Tools: [none found]")
                else:
                    self._print_user_friendly(f"    │   └── Tools: [none found]")
    
    async def _handle_natural_input(self, user_input: str):
        """Handle natural language input from user."""
        
        # If no app exists, treat as requirements for new app
        if not self.app:
            # Don't print user message - already shown via input prompt
            self.app_config['requirements'] = user_input
            self._print_chat_message("Assistant", "Perfect! Let me create your assistant...")
            
            # Run through the creation process quietly
            await self._run_creation_steps_quietly()
        else:
            # App exists, execute query (don't show user message since it's already shown via input prompt)
            await self.app_executor.execute_query(self.app, user_input, show_user_message=False)
    
    async def _run_creation_steps_quietly(self):
        """Run app creation steps without verbose output."""
        try:
            # Run creation steps without step headers
            creation_steps = [
                self.discover_mcp_servers,
                self.generate_system_prompt,
                self.configure_app,
                self.create_app_instance,
                self.initialize_app_components
            ]
            
            for step_func in creation_steps:
                await step_func()
            
            # Show completion message
            self._print_chat_message("Assistant", 
                f"Your assistant '{self.app_config['app_name']}' is ready! What would you like to ask it?")
                
        except Exception as e:
            self._print_chat_message("Assistant", 
                f"Sorry, I encountered an error creating your assistant: {e}\n\nWould you like to try again with different requirements?")
    
    async def cleanup_and_summary(self):
        """Cleanup and show summary."""
        if self.auto_mode:
            from ui_components import AppCreationSummary
            
            # Determine if app was saved
            saved = self.save_app and hasattr(self, 'app') and self.app is not None
            
            # Show standardized app creation summary
            summary_panel = AppCreationSummary.create(
                self.app_config,
                self.app.app_id if self.app else "unknown",
                saved=saved
            )
            self.console.print(summary_panel)
            
            # Show next steps
            next_steps = Panel(
                "[bold]What's Next?[/bold]\n\n"
                "• Your app is ready to use\n"
                "• Test it with different queries\n"
                "• Add more tools as needed\n"
                "• Deploy to production when ready\n\n"
                "[dim]Thank you for using Cogzia Alpha v1.5![/dim]",
                title="[bold]Next Steps[/bold]",
                border_style="blue",
                expand=True
            )
            self.console.print(next_steps)