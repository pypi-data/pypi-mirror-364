"""
Standardized UI components for Cogzia Alpha v1.5.

This module provides consistent UI elements for authentication status,
progress indicators, and user feedback.
"""
from typing import Optional, List, Dict, Any
from rich.panel import Panel
from rich.table import Table
from rich.console import Console
from rich.layout import Layout
from rich.align import Align
from rich.columns import Columns
from rich import box

from auth_manager import UserContext


class AuthenticationStatusBox:
    """Standardized authentication status display component."""
    
    @staticmethod
    def create(user_context: Optional[UserContext], compact: bool = False) -> Panel:
        """
        Create authentication status box.
        
        Args:
            user_context: Current user context or None
            compact: Whether to use compact display (for limited space)
            
        Returns:
            Rich Panel with authentication status
        """
        if user_context and not getattr(user_context, 'is_demo', True):
            # Authenticated user
            if compact:
                content = f"[*] [bold green]Signed in as: {user_context.email}[/bold green]"
                return Panel(
                    content,
                    box=box.ROUNDED,
                    padding=(0, 1),
                    style="green"
                )
            else:
                # Full display
                lines = [
                    "[bold green]AUTHENTICATED[/bold green]",
                    "",
                    f"User: [cyan]{user_context.email}[/cyan]",
                    "Library: [green]✓ Full Access[/green]",
                    "Auto-save: [green]✓ Enabled[/green]",
                    "Status: [green]Ready to create and save apps[/green]"
                ]
                content = Align.center("\n".join(lines))
                
                return Panel(
                    content,
                    title="[bold]Authentication Status[/bold]",
                    title_align="center",
                    border_style="green",
                    padding=(1, 2),
                    expand=False
                )
        else:
            # Demo mode
            if compact:
                content = "[*] [bold]Demo Mode[/bold] - [dim]Login for full features[/dim]"
                return Panel(
                    content,
                    box=box.ROUNDED,
                    padding=(0, 1),
                    style="dim"
                )
            else:
                lines = [
                    "[bold]DEMO MODE[/bold]",
                    "",
                    "User: [dim]demo@cogzia.com (temporary)[/dim]",
                    "Library: [dim]! Limited (session only)[/dim]",
                    "Auto-save: [red]✗ Disabled[/red]",
                    "",
                    "[cyan]Login with --login for full features[/cyan]"
                ]
                content = Align.center("\n".join(lines))
                
                return Panel(
                    content,
                    title="[bold]Authentication Status[/bold]",
                    title_align="center",
                    border_style="dim",
                    padding=(1, 2),
                    expand=False
                )


class StandardMessages:
    """Consistent message formatting across the application."""
    
    @staticmethod
    def success(title: str, message: str, details: List[str] = None) -> Panel:
        """Create a success message panel."""
        content = f"[green]✓ {message}[/green]"
        
        if details:
            content += "\n\n" + "\n".join(f"[dim]- {detail}[/dim]" for detail in details)
        
        return Panel(
            content,
            title=f"[bold]{title}[/bold]",
            title_align="center",
            border_style="green",
            padding=(1, 2),
            expand=False
        )
    
    @staticmethod
    def error(title: str, message: str, recovery: str = None, details: List[str] = None) -> Panel:
        """Create an error message panel."""
        content = f"[red]✗ {message}[/red]"
        
        if details:
            content += "\n\n" + "\n".join(f"[dim]- {detail}[/dim]" for detail in details)
        
        if recovery:
            content += f"\n\n[cyan][i] {recovery}[/cyan]"
        
        return Panel(
            content,
            title=f"[bold]{title}[/bold]",
            title_align="center",
            border_style="red",
            padding=(1, 2),
            expand=False
        )
    
    @staticmethod
    def warning(title: str, message: str, action: str = None) -> Panel:
        """Create a warning message panel."""
        content = f"[dim]! {message}[/dim]"
        
        if action:
            content += f"\n\n[cyan]-> {action}[/cyan]"
        
        return Panel(
            content,
            title=f"[bold]{title}[/bold]",
            title_align="center",
            border_style="dim",
            padding=(1, 2),
            expand=False
        )
    
    @staticmethod
    def info(title: str, items: List[str], footer: str = None) -> Panel:
        """Create an information panel."""
        content = "\n".join(f"- {item}" for item in items)
        
        if footer:
            content += f"\n\n[dim]{footer}[/dim]"
        
        return Panel(
            content,
            title=f"[bold]{title}[/bold]",
            title_align="center",
            border_style="cyan",
            padding=(1, 2),
            expand=False
        )


class ProgressIndicators:
    """Consistent progress indication components."""
    
    @staticmethod
    def step_progress(current: int, total: int, step_name: str, description: str) -> Panel:
        """Create a step progress indicator."""
        # Calculate progress
        percentage = (current / total) * 100 if total > 0 else 0
        filled = int((current / total) * 20) if total > 0 else 0
        
        # Create progress bar
        progress_bar = "#" * filled + "-" * (20 - filled)
        
        content = f"""[{progress_bar}] {percentage:.0f}%

[bold]Step {current} of {total}:[/bold] {step_name}
[dim]{description}[/dim]"""
        
        return Panel(
            content,
            title="[bold]Progress[/bold]",
            title_align="center",
            border_style="cyan",
            padding=(1, 2),
            expand=False
        )
    
    @staticmethod
    def loading(message: str) -> Panel:
        """Create a loading indicator panel."""
        return Panel(
            f"[cyan][..] {message}...[/cyan]",
            border_style="cyan",
            padding=(0, 1),
            expand=False
        )


class WelcomeScreen:
    """Professional welcome screen component."""
    
    @staticmethod
    def create(mode: str, user_context: Optional[UserContext], version: str = "1.5") -> None:
        """
        Display professional welcome screen.
        
        Args:
            mode: Current mode (auto, chat, list, demo, etc.)
            user_context: Current user context
            version: App version
        """
        console = Console()
        
        # Header with full terminal width
        terminal_width = console.width
        console.print("\n" + "=" * terminal_width)
        console.print(f"[bold]COGZIA ALPHA v{version}[/bold]")
        console.print("[dim]AI-Powered App Creator with MCP Tools[/dim]")
        console.print("=" * terminal_width + "\n")
        
        # Authentication status
        auth_box = AuthenticationStatusBox.create(user_context)
        console.print(auth_box)
        console.print()
        
        # Mode information
        mode_info = {
            "auto": ("[>>] Auto Mode", "Creating app from requirements automatically"),
            "chat": ("[>] Chat Mode", "Interactive app creation through conversation"),
            "list": ("[:] Library Mode", "Managing your saved applications"),
            "demo": ("[*] Demo Mode", "Testing with simulated services"),
            "login": ("[*] Login Mode", "Authenticating to access full features")
        }
        
        if mode in mode_info:
            title, description = mode_info[mode]
            mode_panel = Panel(
                f"[bold]{title}[/bold]\n[dim]{description}[/dim]",
                border_style="cyan",
                padding=(0, 1),
                expand=True
            )
            console.print(mode_panel)


class AppCreationSummary:
    """Summary display for created applications."""
    
    @staticmethod
    def create(app_config: Dict[str, Any], app_id: str, saved: bool = False) -> Panel:
        """Create app creation summary panel."""
        lines = [
            "[bold green]App Successfully Created![/bold green]",
            "",
            "[bold]App Details:[/bold]",
            f"- Name: [cyan]{app_config.get('app_name', 'Unnamed App')}[/cyan]",
            f"- ID: [dim]{app_id}[/dim]",
            f"- Purpose: {app_config.get('requirements', 'Not specified')}",
            "",
            "[bold]Integrated Tools:[/bold]"
        ]
        
        # Add tools
        tools = app_config.get('servers', [])
        if tools:
            for tool in tools:
                lines.append(f"- {tool}")
        else:
            lines.append("[dim]- No specific tools (using general capabilities)[/dim]")
        
        # Add save status
        lines.append("")
        if saved:
            lines.append("[green]✓ Saved to your app library[/green]")
        else:
            lines.append("[dim]! Not saved (use --save to persist)[/dim]")
        
        content = Align.center("\n".join(lines))
        
        return Panel(
            content,
            title="[bold]App Creation Complete[/bold]",
            title_align="center",
            border_style="green",
            padding=(1, 2),
            expand=False
        )


class UIHelpers:
    """Helper utilities for consistent UI behavior."""
    
    @staticmethod
    def clear_and_show_header(console: Console, title: str):
        """Clear screen and show consistent header."""
        console.clear()
        console.print(f"\n[bold cyan]{title}[/bold cyan]\n")
    
    @staticmethod
    def prompt_with_default(prompt: str, default: str = None) -> str:
        """Show prompt with optional default value."""
        if default:
            display_prompt = f"{prompt} [dim](default: {default})[/dim]: "
        else:
            display_prompt = f"{prompt}: "
        
        response = input(display_prompt).strip()
        return response if response else default
    
    @staticmethod
    def confirm_action(console: Console, action: str, details: List[str] = None) -> bool:
        """Show confirmation prompt for an action."""
        content = f"[bold yellow]Confirm Action:[/bold yellow] {action}"
        
        if details:
            content += "\n\n" + "\n".join(f"• {detail}" for detail in details)
        
        panel = Panel(
            content + "\n\n[cyan]Continue? (y/N):[/cyan]",
            border_style="yellow",
            padding=(1, 2)
        )
        
        console.print(panel)
        response = input().strip().lower()
        return response == 'y'