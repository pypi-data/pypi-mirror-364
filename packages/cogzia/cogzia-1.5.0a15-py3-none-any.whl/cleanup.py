#!/usr/bin/env python3
"""
Cleanup utility for Cogzia Alpha v1.5

Handles removal of legacy aliases and configuration files that may cause
version conflicts or prevent proper updates.
"""
import os
import re
import shutil
from pathlib import Path
from typing import List, Dict, Optional
from rich.console import Console

console = Console()

def get_shell_config_files() -> List[str]:
    """Identifies potential shell configuration files."""
    home = Path.home()
    potential_files = [
        home / ".bashrc",
        home / ".zshrc", 
        home / ".profile",
        home / ".bash_profile",
        home / ".config" / "fish" / "config.fish",
    ]
    
    # Only return files that actually exist
    return [str(f) for f in potential_files if f.exists()]

def find_cogzia_aliases(file_path: str) -> List[Dict[str, any]]:
    """Find cogzia aliases in a shell config file.
    
    Args:
        file_path: Path to shell config file
        
    Returns:
        List of dicts with alias info: {'line_num': int, 'line': str, 'alias_target': str}
    """
    aliases_found = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Pattern to match alias cogzia=... 
        alias_pattern = re.compile(r'^\s*alias\s+cogzia\s*=\s*["\']?([^"\']+)["\']?\s*$')
        
        for line_num, line in enumerate(lines, 1):
            match = alias_pattern.match(line.strip())
            if match:
                aliases_found.append({
                    'line_num': line_num,
                    'line': line.strip(),
                    'alias_target': match.group(1).strip()
                })
                
    except Exception as e:
        console.print(f"[yellow]Warning: Could not read {file_path}: {e}[/yellow]")
    
    return aliases_found

def remove_cogzia_aliases(file_path: str, dry_run: bool = False) -> bool:
    """Remove cogzia aliases from a shell config file.
    
    Args:
        file_path: Path to shell config file
        dry_run: If True, don't actually modify files
        
    Returns:
        True if aliases were found and removed (or would be removed in dry_run)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Pattern to match alias cogzia=...
        alias_pattern = re.compile(r'^\s*alias\s+cogzia\s*=.*$')
        
        original_count = len(lines)
        filtered_lines = []
        removed_count = 0
        
        for line in lines:
            if alias_pattern.match(line):
                removed_count += 1
                console.print(f"[yellow]Found alias: {line.strip()}[/yellow]")
            else:
                filtered_lines.append(line)
        
        if removed_count > 0:
            if not dry_run:
                # Create backup before modifying
                backup_path = f"{file_path}.cogzia-backup"
                shutil.copy2(file_path, backup_path)
                console.print(f"[dim]Created backup: {backup_path}[/dim]")
                
                # Write cleaned content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(filtered_lines)
                
                console.print(f"[green]✅ Removed {removed_count} cogzia alias(es) from {file_path}[/green]")
            else:
                console.print(f"[cyan]Would remove {removed_count} cogzia alias(es) from {file_path}[/cyan]")
            
            return True
        
        return False
        
    except Exception as e:
        console.print(f"[red]❌ Error processing {file_path}: {e}[/red]")
        return False

def find_cogzia_in_path_exports(file_path: str) -> List[Dict[str, any]]:
    """Find PATH exports that might contain old cogzia installations.
    
    Args:
        file_path: Path to shell config file
        
    Returns:
        List of dicts with PATH export info
    """
    path_exports = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Pattern to match export PATH=... lines that might contain cogzia paths
        path_pattern = re.compile(r'^\s*export\s+PATH\s*=.*cogzia.*$', re.IGNORECASE)
        
        for line_num, line in enumerate(lines, 1):
            if path_pattern.match(line.strip()):
                path_exports.append({
                    'line_num': line_num,
                    'line': line.strip()
                })
                
    except Exception as e:
        console.print(f"[yellow]Warning: Could not read {file_path}: {e}[/yellow]")
    
    return path_exports

def cleanup_legacy_aliases(dry_run: bool = False) -> Dict[str, any]:
    """Main cleanup function to remove legacy cogzia aliases.
    
    Args:
        dry_run: If True, show what would be done without actually doing it
        
    Returns:
        Dict with cleanup results
    """
    console.print(f"[cyan]🧹 {'Scanning for' if dry_run else 'Cleaning up'} legacy cogzia aliases...[/cyan]")
    
    results = {
        'files_scanned': 0,
        'files_with_aliases': 0,
        'aliases_removed': 0,
        'config_files': [],
        'warnings': []
    }
    
    config_files = get_shell_config_files()
    results['files_scanned'] = len(config_files)
    
    if not config_files:
        console.print("[yellow]No shell configuration files found to check[/yellow]")
        return results
    
    console.print(f"[dim]Checking {len(config_files)} shell configuration files...[/dim]")
    
    for config_file in config_files:
        console.print(f"\n[dim]Checking: {config_file}[/dim]")
        
        # Find aliases
        aliases = find_cogzia_aliases(config_file)
        if aliases:
            console.print(f"[yellow]Found {len(aliases)} cogzia alias(es):[/yellow]")
            for alias_info in aliases:
                console.print(f"  Line {alias_info['line_num']}: {alias_info['line']}")
                console.print(f"    → Points to: {alias_info['alias_target']}")
        
        # Check for PATH exports (informational only)
        path_exports = find_cogzia_in_path_exports(config_file)
        if path_exports:
            console.print(f"[blue]ℹ️  Found {len(path_exports)} PATH export(s) mentioning cogzia (keeping these):[/blue]")
            for export_info in path_exports:
                console.print(f"  Line {export_info['line_num']}: {export_info['line']}")
        
        # Remove aliases
        if aliases:
            if remove_cogzia_aliases(config_file, dry_run):
                results['files_with_aliases'] += 1
                results['aliases_removed'] += len(aliases)
                results['config_files'].append(config_file)
    
    # Summary
    console.print(f"\n[bold cyan]Cleanup Summary:[/bold cyan]")
    console.print(f"Files scanned: {results['files_scanned']}")
    console.print(f"Files with aliases: {results['files_with_aliases']}")
    console.print(f"Aliases {'would be ' if dry_run else ''}removed: {results['aliases_removed']}")
    
    if results['aliases_removed'] > 0:
        if not dry_run:
            console.print(f"\n[green]✅ Cleanup complete! Restart your terminal to ensure changes take effect.[/green]")
        else:
            console.print(f"\n[cyan]Run without --dry-run to actually remove these aliases.[/cyan]")
        
        console.print(f"\n[yellow]💡 Make sure ~/.local/bin is in your PATH for pip user installs:[/yellow]")
        console.print(f"   echo 'export PATH=\"$HOME/.local/bin:$PATH\"' >> ~/.bashrc")
        console.print(f"   source ~/.bashrc")
    elif results['files_scanned'] > 0:
        console.print(f"\n[green]✅ No legacy aliases found - your shell configuration is clean![/green]")
    
    return results

def remove_cogzia_config_directory(dry_run: bool = False) -> bool:
    """Remove the cogzia configuration directory.
    
    Args:
        dry_run: If True, show what would be done without actually doing it
        
    Returns:
        True if directory was found and removed (or would be removed)
    """
    config_dir = Path.home() / ".cogzia"
    
    if not config_dir.exists():
        console.print("[dim]No ~/.cogzia directory found[/dim]")
        return False
    
    if dry_run:
        console.print(f"[cyan]Would remove configuration directory: {config_dir}[/cyan]")
        
        # Show what's inside
        try:
            items = list(config_dir.iterdir())
            if items:
                console.print(f"[dim]Contains {len(items)} items:[/dim]")
                for item in items[:5]:  # Show first 5 items
                    console.print(f"  - {item.name}")
                if len(items) > 5:
                    console.print(f"  ... and {len(items) - 5} more")
        except Exception:
            pass
        
        return True
    else:
        try:
            shutil.rmtree(config_dir)
            console.print(f"[green]✅ Removed configuration directory: {config_dir}[/green]")
            return True
        except Exception as e:
            console.print(f"[red]❌ Could not remove {config_dir}: {e}[/red]")
            console.print("[yellow]You may need to remove it manually[/yellow]")
            return False

def comprehensive_cleanup(dry_run: bool = False) -> Dict[str, any]:
    """Perform comprehensive cleanup of cogzia installation artifacts.
    
    Args:
        dry_run: If True, show what would be done without actually doing it
        
    Returns:
        Dict with comprehensive cleanup results
    """
    console.print(f"[bold cyan]🧹 {'Dry run: ' if dry_run else ''}Comprehensive Cogzia Cleanup[/bold cyan]")
    console.print(f"[dim]This will clean up legacy aliases and configuration files[/dim]\n")
    
    results = {
        'alias_cleanup': {},
        'config_removed': False,
        'dry_run': dry_run
    }
    
    # Clean up aliases
    results['alias_cleanup'] = cleanup_legacy_aliases(dry_run)
    
    # Clean up config directory (optional - ask user)
    if results['alias_cleanup']['aliases_removed'] > 0 or dry_run:
        console.print(f"\n[cyan]Configuration directory cleanup:[/cyan]")
        results['config_removed'] = remove_cogzia_config_directory(dry_run)
    
    return results

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Cleanup legacy Cogzia installation artifacts")
    parser.add_argument('--dry-run', action='store_true', 
                        help='Show what would be cleaned up without actually doing it')
    
    args = parser.parse_args()
    
    comprehensive_cleanup(dry_run=args.dry_run)