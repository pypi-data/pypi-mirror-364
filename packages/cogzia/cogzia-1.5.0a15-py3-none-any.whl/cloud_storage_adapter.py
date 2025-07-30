#!/usr/bin/env python3
"""
Cloud Storage Adapter for Cogzia Alpha v1.5.

This module provides a cloud-based storage solution for user apps,
replacing local file storage with MongoDB persistence via the Projects API.

Features:
- Store app configurations in MongoDB (not local files)
- Retrieve apps from cloud storage
- Update app metadata and usage statistics
- Maintain backward compatibility with existing code
"""
import os
import json
import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
from rich.console import Console

from config import get_gcp_service_url, DEFAULT_HEADERS, DEFAULT_TIMEOUT


class CloudStorageAdapter:
    """
    Adapter for storing v1.5 apps in cloud via Projects API.
    
    This replaces local file storage with cloud-based MongoDB storage,
    ensuring apps persist across sessions and machines.
    """
    
    def __init__(self, auth_token: Optional[str] = None, auth_manager=None):
        """
        Initialize cloud storage adapter.
        
        Args:
            auth_token: JWT token for API authentication
            auth_manager: Optional TUIAuthManager for automatic token refresh
        """
        self.auth_token = auth_token
        self.auth_manager = auth_manager
        self.projects_url = get_gcp_service_url("projects")
        self.headers = {**DEFAULT_HEADERS}
        if auth_token:
            self.headers["Authorization"] = f"Bearer {auth_token}"
        self.console = Console()
    
    async def _ensure_valid_token(self) -> bool:
        """
        Ensure we have a valid token, refreshing if necessary.
        
        Returns:
            True if we have a valid token, False otherwise
        """
        if not self.auth_manager:
            return bool(self.auth_token)
        
        try:
            # Check if token is already expired
            if self.auth_manager.is_token_expired():
                self.console.print(f"[yellow]Token has expired[/yellow]")
                # Try to refresh anyway in case there's a refresh token
                refresh_result = await self.auth_manager.refresh_token()
                if refresh_result.get('success'):
                    self.auth_token = refresh_result['token']
                    self.headers["Authorization"] = f"Bearer {self.auth_token}"
                    self.console.print(f"[green]✅ Token refreshed successfully[/green]")
                    return True
                else:
                    error_msg = refresh_result.get('error', 'Unknown error')
                    if "No current token available" in error_msg:
                        self.console.print(f"[dim]No token available for refresh. Please login: `uv run python main.py --login`[/dim]")
                    else:
                        self.console.print(f"[yellow]Token refresh failed: {error_msg}[/yellow]")
                        self.console.print(f"[dim]You may need to re-login: `uv run python main.py --logout && uv run python main.py --login`[/dim]")
                    return False
            
            # Check if token needs refresh (within 5 minutes of expiry)
            elif await self.auth_manager.token_needs_refresh():
                refresh_result = await self.auth_manager.refresh_token()
                if refresh_result.get('success'):
                    self.auth_token = refresh_result['token']
                    self.headers["Authorization"] = f"Bearer {self.auth_token}"
                    return True
                else:
                    error_msg = refresh_result.get('error', 'Unknown error')
                    if "No current token available" in error_msg:
                        self.console.print(f"[yellow]⚠️ Token expiring soon but no token available for refresh[/yellow]")
                        self.console.print(f"[dim]Please re-login soon to avoid authentication issues[/dim]")
                    else:
                        self.console.print(f"[yellow]Warning: Token refresh failed: {error_msg}[/yellow]")
                        self.console.print(f"[dim]You may need to re-login if this persists[/dim]")
                    return False
            
            return bool(self.auth_token)
            
        except Exception as e:
            self.console.print(f"[yellow]Warning: Token validation error: {e}[/yellow]")
            return bool(self.auth_token)
    
    async def _handle_auth_error_and_retry(self, request_func, *args, **kwargs):
        """
        Handle authentication errors with token refresh and retry.
        
        Args:
            request_func: The async function to call (client.post, client.put, etc.)
            *args, **kwargs: Arguments to pass to the request function
            
        Returns:
            Response object from the API call
        """
        # First attempt
        response = await request_func(*args, **kwargs)
        
        # If we get 401 and have an auth manager, try to refresh token and retry
        if response.status_code == 401 and self.auth_manager:
            try:
                refresh_result = await self.auth_manager.refresh_token()
                if refresh_result.get('success'):
                    # Update token and headers
                    self.auth_token = refresh_result['token']
                    if 'headers' in kwargs:
                        kwargs['headers']['Authorization'] = f"Bearer {self.auth_token}"
                    else:
                        kwargs['headers'] = {**self.headers}
                        kwargs['headers']['Authorization'] = f"Bearer {self.auth_token}"
                    
                    # Retry the request with fresh token
                    response = await request_func(*args, **kwargs)
                    
                    if response.status_code in (200, 201):
                        # Silently succeed - retry worked
                        pass
                else:
                    error_msg = refresh_result.get('error', 'Unknown error')
                    self.console.print(f"[red]Token refresh failed: {error_msg}[/red]")
                    self.console.print(f"[dim]Please logout and login again: `uv run python main.py --logout` then `uv run python main.py --login`[/dim]")
            except Exception as e:
                self.console.print(f"[red]Error during token refresh: {e}[/red]")
        
        return response
    
    async def save_app(self, app_id: str, app_config: Dict[str, Any]) -> bool:
        """
        Save app configuration to cloud storage.
        
        Args:
            app_id: Unique app identifier
            app_config: Complete app configuration including:
                - app_name: Display name
                - requirements: Natural language requirements
                - servers: List of MCP servers
                - system_prompt: AI system prompt
                
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            # Ensure we have a valid token before making requests
            if not await self._ensure_valid_token():
                self.console.print("[red]❌ No valid authentication token available[/red]")
                return False
                
            # Prepare project data for API
            project_data = {
                "name": app_config.get("app_name", f"App {app_id}"),
                "description": app_config.get("requirements", "")[:500],  # Truncate to fit
                "type": "custom",  # v1.5 apps are custom type
                "initial_prompt": app_config.get("requirements", ""),
                "tags": ["v1.5", "mcp-enabled"] + app_config.get("servers", []),
                "visibility": "private",
                # Store v1.5 specific data in a custom field
                # We'll use description + tags for now, but ideally Projects API
                # should be extended with a metadata field
            }
            
            # Check if project already exists
            existing = await self._get_project_by_app_id(app_id)
            
            async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT, follow_redirects=True) as client:
                if existing:
                    # Update existing project with retry logic
                    response = await self._handle_auth_error_and_retry(
                        client.put,
                        f"{self.projects_url}/projects/{existing['id']}",
                        json=project_data,
                        headers=self.headers
                    )
                    if response.status_code not in (200, 201):
                        self.console.print(f"[red]Update failed with status {response.status_code}: {response.text}[/red]")
                else:
                    # Create new project with v1.5 app data
                    # Store full config in initial_prompt as JSON for now
                    full_config = {
                        "v1_5_app": True,
                        "app_id": app_id,
                        "config": app_config
                    }
                    project_data["initial_prompt"] = json.dumps(full_config)
                    
                    response = await self._handle_auth_error_and_retry(
                        client.post,
                        f"{self.projects_url}/projects",
                        json=project_data,
                        headers=self.headers
                    )
                
                if response.status_code not in (200, 201):
                    self.console.print(f"[red]Save failed with status {response.status_code}: {response.text}[/red]")
                return response.status_code in (200, 201)
                
        except Exception as e:
            self.console.print(f"[red]Error saving app to cloud: {e}[/red]")
            return False
    
    async def load_app(self, app_id: str) -> Optional[Dict[str, Any]]:
        """
        Load app configuration from cloud storage.
        
        Args:
            app_id: App identifier to load
            
        Returns:
            App configuration dict or None if not found
        """
        try:
            # Ensure we have a valid token before making requests
            if not await self._ensure_valid_token():
                self.console.print("[red]❌ No valid authentication token available[/red]")
                return None
                
            project = await self._get_project_by_app_id(app_id)
            if not project:
                return None
            
            # Extract v1.5 config from project data
            if project.get("initial_prompt"):
                try:
                    # Try to parse as JSON first (new format)
                    data = json.loads(project["initial_prompt"])
                    if isinstance(data, dict) and data.get("v1_5_app"):
                        return data["config"]
                except:
                    pass
            
            # Fallback: reconstruct from basic fields
            return {
                "app_name": project.get("name", "Unnamed App"),
                "requirements": project.get("description", ""),
                "servers": [tag for tag in project.get("tags", []) 
                           if tag not in ["v1.5", "mcp-enabled"]],
                "system_prompt": project.get("initial_prompt", ""),
                "created_at": project.get("created_at"),
                "updated_at": project.get("updated_at")
            }
            
        except Exception as e:
            self.console.print(f"[red]Error loading app from cloud: {e}[/red]")
            return None
    
    async def list_apps(self) -> List[Dict[str, Any]]:
        """
        List all user's apps from cloud storage.
        
        Returns:
            List of app summaries sorted by last update
        """
        try:
            # Ensure we have a valid token before making requests
            if not await self._ensure_valid_token():
                self.console.print("[red]❌ No valid authentication token available[/red]")
                return []
                
            async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT, follow_redirects=True) as client:
                response = await self._handle_auth_error_and_retry(
                    client.get,
                    f"{self.projects_url}/projects",
                    headers=self.headers,
                    params={"tags": "v1.5"}  # Filter for v1.5 apps
                )
                
                if response.status_code != 200:
                    return []
                
                projects = response.json()
                apps = []
                
                for project in projects:
                    # Extract app_id from tags or initial_prompt
                    app_id = None
                    if project.get("initial_prompt"):
                        try:
                            data = json.loads(project["initial_prompt"])
                            if isinstance(data, dict) and data.get("v1_5_app"):
                                app_id = data.get("app_id")
                        except:
                            pass
                    
                    if not app_id:
                        # Generate from project ID
                        app_id = f"app_{project['guid'].replace('proj_', '')}"
                    
                    apps.append({
                        "app_id": app_id,
                        "name": project.get("name", "Unnamed App"),
                        "requirements": project.get("description", ""),
                        "created_at": project.get("created_at"),
                        "updated_at": project.get("updated_at"),
                        "project_guid": project.get("guid")
                    })
                
                # Sort by updated_at (newest first)
                return sorted(apps, 
                            key=lambda x: x.get("updated_at", ""), 
                            reverse=True)
                
        except Exception as e:
            self.console.print(f"[red]Error listing apps from cloud: {e}[/red]")
            return []
    
    async def delete_app(self, app_id: str) -> bool:
        """
        Delete app from cloud storage.
        
        Args:
            app_id: App identifier to delete
            
        Returns:
            bool: True if deleted successfully
        """
        try:
            # Ensure we have a valid token before making requests
            if not await self._ensure_valid_token():
                self.console.print("[red]❌ No valid authentication token available[/red]")
                return False
                
            project = await self._get_project_by_app_id(app_id)
            if not project:
                return False
            
            async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT, follow_redirects=True) as client:
                response = await self._handle_auth_error_and_retry(
                    client.delete,
                    f"{self.projects_url}/projects/{project['id']}",
                    headers=self.headers
                )
                return response.status_code == 204
                
        except Exception as e:
            self.console.print(f"[red]Error deleting app from cloud: {e}[/red]")
            return False
    
    async def _get_project_by_app_id(self, app_id: str) -> Optional[Dict[str, Any]]:
        """
        Find project by v1.5 app ID.
        
        Args:
            app_id: App identifier to search for
            
        Returns:
            Project data or None if not found
        """
        apps = await self.list_apps()
        for app in apps:
            if app["app_id"] == app_id:
                # Get full project details
                try:
                    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT, follow_redirects=True) as client:
                        response = await self._handle_auth_error_and_retry(
                            client.get,
                            f"{self.projects_url}/projects/by-guid/{app['project_guid']}",
                            headers=self.headers
                        )
                        if response.status_code == 200:
                            return response.json()
                except:
                    pass
        return None
    
    def migrate_local_apps(self) -> int:
        """
        Migrate existing local apps to cloud storage.
        
        This is a one-time migration helper for existing users.
        
        Returns:
            Number of apps migrated
        """
        migrated = 0
        apps_dir = Path("apps")
        
        if not apps_dir.exists():
            return 0
        
        for app_dir in apps_dir.iterdir():
            if not app_dir.is_dir():
                continue
                
            manifest_path = app_dir / "manifest.yaml"
            if not manifest_path.exists():
                continue
            
            try:
                # Load manifest
                import yaml
                with open(manifest_path) as f:
                    manifest = yaml.safe_load(f)
                
                app_config = manifest.get("config", {})
                app_id = manifest.get("id", app_dir.name)
                
                # Save to cloud (sync call for migration)
                import asyncio
                success = asyncio.run(self.save_app(app_id, app_config))
                
                if success:
                    migrated += 1
                    self.console.print(f"[green]Migrated {app_id} to cloud storage[/green]")
                    
            except Exception as e:
                self.console.print(f"[yellow]Failed to migrate {app_dir.name}: {e}[/yellow]")
        
        return migrated


# Backward compatibility functions
async def save_app_to_cloud(app_id: str, app_config: Dict[str, Any], 
                           auth_token: Optional[str] = None, 
                           auth_manager=None) -> bool:
    """
    Save app to cloud storage (backward compatibility wrapper).
    
    Args:
        app_id: App identifier
        app_config: App configuration
        auth_token: JWT authentication token
        auth_manager: Optional TUIAuthManager for token refresh
        
    Returns:
        bool: Success status
    """
    adapter = CloudStorageAdapter(auth_token, auth_manager=auth_manager)
    return await adapter.save_app(app_id, app_config)


async def load_app_from_cloud(app_id: str, 
                             auth_token: Optional[str] = None,
                             auth_manager=None) -> Optional[Dict[str, Any]]:
    """
    Load app from cloud storage (backward compatibility wrapper).
    
    Args:
        app_id: App identifier
        auth_token: JWT authentication token
        auth_manager: Optional TUIAuthManager for token refresh
        
    Returns:
        App configuration or None
    """
    adapter = CloudStorageAdapter(auth_token, auth_manager=auth_manager)
    return await adapter.load_app(app_id)


async def list_cloud_apps(auth_token: Optional[str] = None,
                         auth_manager=None) -> List[Dict[str, Any]]:
    """
    List all apps from cloud storage (backward compatibility wrapper).
    
    Args:
        auth_token: JWT authentication token
        auth_manager: Optional TUIAuthManager for token refresh
        
    Returns:
        List of app summaries
    """
    adapter = CloudStorageAdapter(auth_token, auth_manager=auth_manager)
    return await adapter.list_apps()