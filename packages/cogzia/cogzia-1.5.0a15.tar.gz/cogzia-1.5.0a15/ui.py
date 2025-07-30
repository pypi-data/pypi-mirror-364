"""
UI components for Cogzia Alpha v1.5.

This module contains all UI-related components including console handling,
output formatting, and display utilities.
"""
import os
import sys
from pathlib import Path
from typing import Optional, Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.live import Live
from rich.text import Text
from rich.markdown import Markdown
from rich.status import Status
from rich.columns import Columns
from rich.align import Align
from rich import box


class DevNull:
    """Null device for suppressing output."""
    def write(self, msg): 
        pass
    
    def flush(self): 
        pass


class SuppressOutput:
    """Context manager to suppress stdout/stderr temporarily."""
    def __init__(self, suppress: bool = True):
        self.suppress = suppress
        self._stdout = None
        self._stderr = None
        
    def __enter__(self):
        if self.suppress:
            self._stdout = sys.stdout
            self._stderr = sys.stderr
            sys.stdout = DevNull()
            sys.stderr = DevNull()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.suppress and self._stdout and self._stderr:
            sys.stdout = self._stdout
            sys.stderr = self._stderr


class EnhancedConsole:
    """Enhanced console wrapper with better error handling and structure awareness."""
    
    def __init__(self, structure_detector=None):
        self.console = Console()
        self.structure_detector = structure_detector
        
    def print(self, *args, **kwargs):
        """Enhanced print with error handling."""
        try:
            self.console.print(*args, **kwargs)
        except Exception:
            # Fallback to basic print if Rich fails
            print(*args)
    
    def status(self, *args, **kwargs):
        """Enhanced status with fallback."""
        try:
            return self.console.status(*args, **kwargs)
        except Exception:
            # Return a dummy context manager
            class DummyStatus:
                def __enter__(self): 
                    return self
                def __exit__(self, *args): 
                    pass
            return DummyStatus()
    
    def print_structure_info(self):
        """Print information about detected repository structure."""
        if not self.structure_detector:
            self.print("[dim]! Structure detector not initialized[/dim]")
            return
            
        # Check for root-level optimized directories
        root_tools_exists = (self.structure_detector.project_root / "tools").exists()
        root_mcp_ecosystem_exists = (self.structure_detector.project_root / "mcp_ecosystem").exists()
        
        if root_tools_exists or root_mcp_ecosystem_exists:
            self.print("[green]✓[/green] Optimized repository structure detected")
            self.print("[dim]Using root-level promoted directories[/dim]")
        elif self.structure_detector.has_new_structure:
            self.print("[green]✓[/green] Repository structure ready")
            self.print(f"[dim]Using: {self.structure_detector.new_structure_path}[/dim]")
        else:
            self.print("[dim]! Using base repository structure[/dim]")
            self.print("[dim]Consider upgrading to optimized structure for better organization[/dim]")


def create_service_table(services: dict, title: str = "System Prerequisites", 
                        show_structure: bool = True) -> Table:
    """
    Create a service status table.
    
    Args:
        services: Dictionary of service information
        title: Table title
        show_structure: Whether to show structure column
        
    Returns:
        Rich Table object
    """
    table = Table(title=title, box=box.ROUNDED)
    table.add_column("Service", style="cyan")
    table.add_column("Port", style="magenta")
    table.add_column("Status", style="green")
    table.add_column("Purpose", style="white")
    if show_structure:
        table.add_column("Structure", style="dim")
    
    return table


def create_component_table(components: list, title: str = "Component Initialization") -> Table:
    """
    Create a component initialization table.
    
    Args:
        components: List of (component_name, status) tuples
        title: Table title
        
    Returns:
        Rich Table object
    """
    table = Table(title=title, show_header=True)
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    
    for component, status in components:
        table.add_row(component, status)
    
    return table


def create_progress_panel(title: str, content: str, border_style: str = "blue") -> Panel:
    """
    Create a progress panel.
    
    Args:
        title: Panel title
        content: Panel content
        border_style: Border style color
        
    Returns:
        Rich Panel object
    """
    return Panel(
        content,
        title=title,
        border_style=border_style,
        expand=True
    )


def create_chat_message(sender: str, message: str, style: str = "") -> str:
    """
    Format a chat message.
    
    Args:
        sender: Message sender
        message: Message content
        style: Optional style
        
    Returns:
        Formatted message string
    """
    if sender == "Assistant":
        panel = Panel(
            message,
            title="[bold]Assistant[/bold]",
            border_style="green",
            box=box.ROUNDED
        )
        return panel
    else:
        return f"[bright_blue]{sender}:[/bright_blue] {message}"


def create_step_header(step_name: str, step_description: str, 
                      structure_info: str = None, verbose: bool = False) -> Panel:
    """
    Create a step header panel.
    
    Args:
        step_name: Name of the step
        step_description: Description of the step
        structure_info: Optional structure information
        verbose: Whether to show verbose header
        
    Returns:
        Rich Panel object
    """
    if verbose:
        content = f"[bold yellow]{step_name}[/bold yellow]\n"
        content += f"[dim]{step_description}[/dim]"
        if structure_info:
            content += f"\n[dim italic]{structure_info}[/dim italic]"
        
        return Panel(
            content,
            style="yellow",
            expand=True,
            border_style="double"
        )
    else:
        # Simple progress message for non-verbose mode - keep it minimal
        return ""


def create_summary_panel(app_name: str, server_count: int, status: str = "Ready") -> Panel:
    """
    Create a summary panel for app creation.
    
    Args:
        app_name: Name of the created app
        server_count: Number of integrated servers
        status: App status
        
    Returns:
        Rich Panel object
    """
    content = f"[bold green]App Creation Complete![/bold green]\n\n"
    content += f"[cyan]App Name:[/cyan] {app_name}\n"
    content += f"[cyan]Tools Integrated:[/cyan] {server_count}\n"
    content += f"[cyan]Structure:[/cyan] Optimized Repository Structure\n"
    content += f"[cyan]Status:[/cyan] {status}\n\n"
    content += f"[dim]Your AI app has been successfully created and tested![/dim]"
    
    return Panel(
        content,
        title="[bold]Mission Accomplished[/bold]",
        border_style="green",
        expand=True
    )