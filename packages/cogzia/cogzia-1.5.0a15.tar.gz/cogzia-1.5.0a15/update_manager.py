#!/usr/bin/env python3
"""
Update Manager for Cogzia Alpha v1.5

Handles checking for updates and performing in-place updates of the Cogzia installation.
"""
import os
import sys
import json
import shutil
import tempfile
import subprocess
from pathlib import Path
from typing import Optional, Dict, Tuple
import httpx
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm

from version import __version__, is_newer_version, get_version_string
from ui import EnhancedConsole
from cleanup import cleanup_legacy_aliases

class UpdateManager:
    """Manages updates for Cogzia Alpha."""
    
    def __init__(self, channel: str = "stable"):
        """Initialize the update manager.
        
        Args:
            channel: Update channel ('stable' or 'alpha')
        """
        self.channel = channel
        self.console = EnhancedConsole()
        self.update_base_url = "https://storage.googleapis.com/cogzia-releases"
        self.backup_dir = Path.home() / ".cogzia" / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    async def check_for_updates(self) -> Optional[Dict]:
        """Check if updates are available.
        
        Returns:
            Update info dict if available, None otherwise
        """
        try:
            manifest_url = f"{self.update_base_url}/{self.channel}/latest.json"
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(manifest_url)
                
                if response.status_code != 200:
                    return None
                
                manifest = response.json()
                remote_version = manifest.get("version", "0.0.0")
                
                if is_newer_version(remote_version, __version__):
                    return manifest
                
                return None
                
        except Exception as e:
            self.console.print(f"[yellow]⚠️  Could not check for updates: {e}[/yellow]")
            return None
    
    async def download_update(self, update_info: Dict, progress: Progress) -> Optional[Path]:
        """Download the update package.
        
        Args:
            update_info: Update manifest information
            progress: Rich progress bar
            
        Returns:
            Path to downloaded file or None if failed
        """
        try:
            download_url = update_info.get("download_url")
            if not download_url:
                # Construct URL from version
                version = update_info.get("version", __version__)
                filename = f"cogzia_alpha_v1_5-{version}-py3-none-any.whl"
                download_url = f"{self.update_base_url}/{self.channel}/{filename}"
            
            # Create temp file
            temp_dir = tempfile.mkdtemp()
            download_path = Path(temp_dir) / "update.whl"
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(download_url, follow_redirects=True)
                
                if response.status_code != 200:
                    self.console.print(f"[red]❌ Download failed: HTTP {response.status_code}[/red]")
                    return None
                
                # Save to file
                download_path.write_bytes(response.content)
                return download_path
                
        except Exception as e:
            self.console.print(f"[red]❌ Download error: {e}[/red]")
            return None
    
    def backup_current_installation(self) -> Optional[Path]:
        """Backup the current installation.
        
        Returns:
            Path to backup or None if failed
        """
        try:
            # Find site-packages location
            import main
            module_path = Path(main.__file__).parent
            
            # Create backup with timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_dir / f"cogzia_backup_{__version__}_{timestamp}"
            
            # Copy current installation
            shutil.copytree(module_path, backup_path, dirs_exist_ok=True)
            
            return backup_path
            
        except Exception as e:
            self.console.print(f"[yellow]⚠️  Could not backup installation: {e}[/yellow]")
            return None
    
    def install_update(self, wheel_path: Path) -> bool:
        """Install the update package.
        
        Args:
            wheel_path: Path to the wheel file
            
        Returns:
            True if successful
        """
        try:
            # Use pip to install/upgrade with force-reinstall to ensure clean update
            result = subprocess.run([
                sys.executable, "-m", "pip", "install",
                "--upgrade", "--force-reinstall",
                str(wheel_path)
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                self.console.print(f"[red]❌ Installation failed:[/red]")
                self.console.print(result.stderr)
                return False
            
            return True
            
        except Exception as e:
            self.console.print(f"[red]❌ Installation error: {e}[/red]")
            return False
    
    def cleanup_legacy_installation_artifacts(self) -> bool:
        """Clean up legacy aliases and configuration that might prevent proper updates.
        
        Returns:
            True if cleanup was successful or not needed
        """
        try:
            self.console.print("[cyan]🧹 Cleaning up legacy installation artifacts...[/cyan]")
            
            # Run the cleanup function
            cleanup_results = cleanup_legacy_aliases(dry_run=False)
            
            if cleanup_results['aliases_removed'] > 0:
                self.console.print(f"[green]✅ Cleaned up {cleanup_results['aliases_removed']} legacy aliases[/green]")
                self.console.print("[yellow]⚠️  Please restart your terminal after the update[/yellow]")
            else:
                self.console.print("[dim]No legacy aliases found to clean up[/dim]")
            
            return True
            
        except Exception as e:
            self.console.print(f"[yellow]⚠️  Could not complete cleanup: {e}[/yellow]")
            self.console.print("[dim]This won't prevent the update from working[/dim]")
            return False
    
    def preserve_user_data(self) -> Dict:
        """Preserve user data before update.
        
        Returns:
            Dict of preserved data
        """
        preserved = {}
        
        try:
            # Preserve auth tokens
            auth_dir = Path.home() / ".cogzia"
            if auth_dir.exists():
                token_file = auth_dir / "auth_token.json"
                if token_file.exists():
                    preserved["auth_token"] = token_file.read_text()
            
            # Preserve user preferences
            config_file = auth_dir / "config.json"
            if config_file.exists():
                preserved["config"] = config_file.read_text()
                
        except Exception as e:
            self.console.print(f"[yellow]⚠️  Could not preserve all user data: {e}[/yellow]")
        
        return preserved
    
    def restore_user_data(self, preserved: Dict):
        """Restore user data after update.
        
        Args:
            preserved: Dict of preserved data
        """
        try:
            auth_dir = Path.home() / ".cogzia"
            auth_dir.mkdir(exist_ok=True)
            
            # Restore auth token
            if "auth_token" in preserved:
                token_file = auth_dir / "auth_token.json"
                token_file.write_text(preserved["auth_token"])
            
            # Restore config
            if "config" in preserved:
                config_file = auth_dir / "config.json"
                config_file.write_text(preserved["config"])
                
        except Exception as e:
            self.console.print(f"[yellow]⚠️  Could not restore all user data: {e}[/yellow]")
    
    async def perform_update(self, force: bool = False) -> bool:
        """Perform the full update process.
        
        Args:
            force: Force update even if on latest version
            
        Returns:
            True if successful
        """
        self.console.print(f"[cyan]🔍 Checking for updates...[/cyan]")
        self.console.print(f"[dim]Current version: {get_version_string()}[/dim]")
        
        # Check for updates
        update_info = await self.check_for_updates()
        
        if not update_info and not force:
            self.console.print("[green]✅ You're already on the latest version![/green]")
            return True
        
        if update_info:
            new_version = update_info.get("version", "Unknown")
            self.console.print(f"\n[yellow]📦 Update available: v{new_version}[/yellow]")
            
            # Show release notes if available
            if "release_notes" in update_info:
                self.console.print("\n[bold]Release Notes:[/bold]")
                self.console.print(update_info["release_notes"])
            
            # Confirm update
            if not force and not Confirm.ask("\nDo you want to update?"):
                self.console.print("[yellow]Update cancelled.[/yellow]")
                return False
        
        # Preserve user data
        self.console.print("\n[cyan]💾 Preserving user data...[/cyan]")
        preserved_data = self.preserve_user_data()
        
        # Backup current installation
        self.console.print("[cyan]📦 Backing up current installation...[/cyan]")
        backup_path = self.backup_current_installation()
        if backup_path:
            self.console.print(f"[dim]Backup saved to: {backup_path}[/dim]")
        
        # Download update
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            download_task = progress.add_task("[cyan]Downloading update...", total=None)
            
            if update_info:
                wheel_path = await self.download_update(update_info, progress)
            else:
                # Force reinstall current version
                self.console.print("[yellow]Force reinstalling current version...[/yellow]")
                # This would need to download current version
                return False
            
            progress.update(download_task, completed=True)
        
        if not wheel_path:
            self.console.print("[red]❌ Update download failed[/red]")
            return False
        
        # Install update
        self.console.print("[cyan]🔧 Installing update...[/cyan]")
        if not self.install_update(wheel_path):
            self.console.print("[red]❌ Update installation failed[/red]")
            if backup_path:
                self.console.print(f"[yellow]Backup available at: {backup_path}[/yellow]")
            return False
        
        # Clean up legacy installation artifacts (aliases, etc.)
        self.cleanup_legacy_installation_artifacts()
        
        # Restore user data
        self.console.print("[cyan]♻️  Restoring user data...[/cyan]")
        self.restore_user_data(preserved_data)
        
        # Clean up
        try:
            shutil.rmtree(wheel_path.parent)
        except:
            pass
        
        self.console.print("\n[green]✅ Update completed successfully![/green]")
        self.console.print("[yellow]Please restart Cogzia to use the new version.[/yellow]")
        
        return True


async def check_and_notify_update():
    """Check for updates and notify user (non-blocking)."""
    try:
        manager = UpdateManager()
        update_info = await manager.check_for_updates()
        
        if update_info:
            console = EnhancedConsole()
            new_version = update_info.get("version", "Unknown")
            console.print(f"\n[yellow]📦 Update available: Cogzia Alpha v{new_version}[/yellow]")
            console.print("[dim]Run 'cogzia --update' to update[/dim]\n")
    except:
        # Silently fail - don't interrupt user workflow
        pass