#!/usr/bin/env python3
"""
Authentication manager for Cogzia Alpha v1.5 TUI.

This module handles user authentication, token management, and secure
credential storage for the TUI interface. It integrates with the existing
auth service and provides seamless authentication flow.
"""
import os
import json
import getpass
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import httpx
import jwt

from config import get_gcp_service_url
from ui import EnhancedConsole


class UserContext:
    """
    Represents an authenticated user's context.
    
    This class stores user information and authentication tokens,
    providing a consistent interface for user data throughout the application.
    
    Attributes:
        user_id (str): Unique identifier for the user
        email (str): User's email address
        token (str): JWT access token for API calls
        roles (List[str]): User's assigned roles
        refresh_token (Optional[str]): Token for refreshing access token
        is_demo (bool): Whether this is a demo user (always False)
    """
    
    def __init__(
        self,
        user_id: str,
        email: str,
        token: str,
        roles: Optional[list] = None,
        refresh_token: Optional[str] = None,
        is_demo: bool = False
    ):
        """
        Initialize user context with authentication data.
        
        Args:
            user_id: Unique user identifier
            email: User's email address
            token: JWT access token
            roles: List of user roles (defaults to ["user"])
            refresh_token: Optional refresh token
            is_demo: Whether this is a demo user
        """
        if not isinstance(user_id, str):
            raise TypeError("user_id must be a string")
        if not isinstance(roles, (list, type(None))):
            raise TypeError("roles must be a list or None")
            
        self.user_id = user_id
        self.email = email
        self.token = token
        self.roles = roles or ["user"]
        self.refresh_token = refresh_token
        self.is_demo = is_demo
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert user context to dictionary for serialization.
        
        Returns:
            Dict containing all user context fields
        """
        return {
            "user_id": self.user_id,
            "email": self.email,
            "token": self.token,
            "roles": self.roles,
            "refresh_token": self.refresh_token,
            "is_demo": self.is_demo
        }
    
    def has_role(self, role: str) -> bool:
        """
        Check if user has a specific role.
        
        Args:
            role: Role name to check
            
        Returns:
            True if user has the role, False otherwise
        """
        return role in self.roles


class DemoUserContext(UserContext):
    """
    Demo user context for unauthenticated usage.
    
    This class provides a consistent demo user context when authentication
    is not enabled or available.
    """
    
    def __init__(self):
        """Initialize demo user with fixed values."""
        super().__init__(
            user_id="demo_user",
            email="demo@cogzia.com",
            token="demo_token_123",
            roles=["demo"],
            is_demo=True
        )


class TUIAuthManager:
    """
    Manages authentication for the TUI application.
    
    This class handles login, logout, token management, and secure storage
    of authentication credentials. It integrates with the auth service to
    provide a seamless authentication experience.
    
    Attributes:
        auth_url (str): URL of the authentication service
        current_token (Optional[str]): Current JWT access token
        current_user (Optional[UserContext]): Current user context
        refresh_token_value (Optional[str]): Current refresh token
        token_storage_path (Path): Path to secure token storage
        timeout (float): HTTP request timeout in seconds
    """
    
    def __init__(self, auth_url: Optional[str] = None):
        """
        Initialize the authentication manager.
        
        Args:
            auth_url: Optional custom auth service URL
        """
        self.auth_url = auth_url or get_gcp_service_url("auth")
        self.current_token: Optional[str] = None
        self.current_user: Optional[UserContext] = None
        self.refresh_token_value: Optional[str] = None
        self.token_storage_path = Path.home() / ".cogzia" / "auth_token.json"
        self.timeout = 30.0  # 30 second timeout
        self._token_expiry: Optional[datetime] = None
        self.console = EnhancedConsole()
        
        # Ensure storage directory exists
        self.token_storage_path.parent.mkdir(parents=True, exist_ok=True)
    
    async def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user with email and password.
        
        Makes a request to the auth service to validate credentials and
        obtain access tokens.
        
        Args:
            email: User's email address
            password: User's password
            
        Returns:
            Dict with success status, token, and user info on success,
            or error message on failure
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.auth_url}/login",
                    json={"email": email, "password": password}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Store tokens
                    self.current_token = data.get("access_token", data.get("token"))
                    self.refresh_token_value = data.get("refresh_token")
                    
                    # Create user context
                    self.current_user = self.create_user_context({
                        "token": self.current_token,
                        "user": data.get("user", {"email": email}),
                        "refresh_token": self.refresh_token_value
                    })
                    
                    # Extract token expiry
                    self._extract_token_expiry(self.current_token)
                    
                    # Save token for persistence
                    await self.save_token({
                        "token": self.current_token,
                        "refresh_token": self.refresh_token_value,
                        "user": self.current_user.to_dict()
                    })
                    
                    return {
                        "success": True,
                        "token": self.current_token,
                        "user": data.get("user", {"email": email})
                    }
                else:
                    return {
                        "success": False,
                        "error": "Invalid credentials"
                    }
                    
        except httpx.ConnectError:
            return {
                "success": False,
                "error": "Cannot connect to authentication service"
            }
        except httpx.TimeoutException:
            return {
                "success": False,
                "error": "Authentication service timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Authentication failed: {str(e)}"
            }
    
    async def interactive_login(self) -> Dict[str, Any]:
        """
        Perform interactive login with user prompts.
        
        Prompts the user for email and password through the TUI interface
        and attempts authentication.
        
        Returns:
            Dict with login result (same format as login method)
        """
        self.console.print("\n[bold cyan]🔐 Cogzia Login[/bold cyan]")
        self.console.print("Please enter your credentials:\n")
        
        # Get email
        email = input("Email: ")
        
        # Get password (hidden input)
        password = getpass.getpass("Password: ")
        
        # Show progress
        self.console.print("\n[dim]Authenticating...[/dim]")
        
        # Attempt login
        result = await self.login(email, password)
        
        if result["success"]:
            self.console.print(f"\n[green]✅ Welcome, {email}![/green]")
        else:
            self.console.print(f"\n[red]❌ Login failed: {result['error']}[/red]")
        
        return result
    
    async def logout(self) -> None:
        """
        Log out the current user.
        
        Clears all authentication data from memory and removes stored tokens.
        """
        self.current_token = None
        self.current_user = None
        self.refresh_token_value = None
        self._token_expiry = None
        
        # Clear stored token
        self.clear_token()
        
        self.console.print("[yellow]👋 Logged out successfully[/yellow]")
    
    async def refresh_token(self) -> Dict[str, Any]:
        """
        Refresh the access token using the current JWT token.
        
        The auth service uses JWT-based refresh where you send the current
        token via Authorization header to get a new one.
        
        Returns:
            Dict with success status and new token, or error on failure
        """
        if not self.current_token:
            return {
                "success": False,
                "error": "No current token available for refresh"
            }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.auth_url}/refresh",
                    headers={"Authorization": f"Bearer {self.current_token}"},
                    json={}  # Empty body - token sent in header
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Update the current token with the new JWT
                    old_token = self.current_token
                    self.current_token = data.get("access_token", data.get("token"))
                    
                    if not self.current_token:
                        return {
                            "success": False,
                            "error": "Refresh response did not contain a new token"
                        }
                    
                    # Update expiry time from new token
                    self._extract_token_expiry(self.current_token)
                    
                    # Update user context with new token
                    if self.current_user:
                        self.current_user.token = self.current_token
                    
                    # Save updated token (refresh_token stays None for JWT-based auth)
                    await self.save_token({
                        "token": self.current_token,
                        "refresh_token": None,  # JWT-based auth doesn't use refresh tokens
                        "user": self.current_user.to_dict() if self.current_user else {}
                    })
                    
                    return {
                        "success": True,
                        "token": self.current_token,
                        "old_token": old_token
                    }
                else:
                    error_detail = "Unknown error"
                    try:
                        error_data = response.json()
                        error_detail = error_data.get("detail", error_detail)
                    except:
                        pass
                    
                    return {
                        "success": False,
                        "error": f"Token refresh failed: {error_detail} (status: {response.status_code})"
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": f"Token refresh error: {str(e)}"
            }
    
    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify a token with the auth service.
        
        Args:
            token: JWT token to verify
            
        Returns:
            User info dict if token is valid, None otherwise
        """
        if not token:
            return None
            
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.auth_url}/profile",
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return None
                    
        except Exception:
            return None
    
    async def token_needs_refresh(self) -> bool:
        """
        Check if the current token needs refreshing.
        
        Tokens should be refreshed 5 minutes before expiry to ensure
        uninterrupted service.
        
        Returns:
            True if token needs refresh, False otherwise
        """
        if not self._token_expiry:
            # If we can't determine expiry, assume token is still valid
            return False
        
        # Refresh if less than 5 minutes until expiry
        time_until_expiry = self._token_expiry - datetime.utcnow()
        return time_until_expiry < timedelta(minutes=5)
    
    def is_token_expired(self) -> bool:
        """
        Check if the current token has expired.
        
        Returns:
            True if token is expired, False otherwise
        """
        if not self._token_expiry:
            return False
        
        return datetime.utcnow() > self._token_expiry
    
    def get_auth_headers(self) -> Dict[str, str]:
        """
        Get authorization headers for API requests.
        
        Returns:
            Dict with Authorization header if token exists,
            plus standard headers
        """
        headers = {"Content-Type": "application/json"}
        
        if self.current_token:
            headers["Authorization"] = f"Bearer {self.current_token}"
        
        return headers
    
    def create_user_context(self, login_result: Dict[str, Any]) -> UserContext:
        """
        Create a UserContext from login response.
        
        Args:
            login_result: Response from login endpoint
            
        Returns:
            UserContext instance with user data
        """
        user_data = login_result.get("user", {})
        
        return UserContext(
            user_id=user_data.get("id", user_data.get("_id", "unknown")),
            email=user_data.get("email", "unknown@cogzia.com"),
            token=login_result.get("token", ""),
            roles=user_data.get("roles", ["user"]),
            refresh_token=login_result.get("refresh_token")
        )
    
    async def save_token(self, token_data: Dict[str, Any]) -> None:
        """
        Save token data to secure storage.
        
        Args:
            token_data: Dict containing token and user information
        """
        try:
            # Write with restricted permissions
            with open(self.token_storage_path, 'w') as f:
                json.dump(token_data, f, indent=2)
            
            # Set file permissions to owner-only (Unix)
            if os.name != 'nt':  # Not Windows
                os.chmod(self.token_storage_path, 0o600)
                
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not save token: {e}[/yellow]")
    
    async def load_token(self) -> Optional[Dict[str, Any]]:
        """
        Load saved token from storage.
        
        Returns:
            Saved token data if exists and valid, None otherwise
        """
        if not self.token_storage_path.exists():
            return None
        
        try:
            with open(self.token_storage_path, 'r') as f:
                data = json.load(f)
                
            # Restore tokens and user context
            self.current_token = data.get("token")
            self.refresh_token_value = data.get("refresh_token")
            
            if data.get("user"):
                user_data = data["user"]
                self.current_user = UserContext(
                    user_id=user_data.get("user_id"),
                    email=user_data.get("email"),
                    token=self.current_token,
                    roles=user_data.get("roles", ["user"]),
                    refresh_token=self.refresh_token_value
                )
            
            return data
            
        except Exception:
            return None
    
    def clear_token(self) -> None:
        """Remove stored token file."""
        try:
            if self.token_storage_path.exists():
                self.token_storage_path.unlink()
        except Exception:
            pass
    
    def _extract_token_expiry(self, token: str) -> None:
        """
        Extract expiry time from JWT token.
        
        Args:
            token: JWT token to decode
        """
        try:
            # Decode without verification to get expiry
            payload = jwt.decode(token, options={"verify_signature": False})
            if "exp" in payload:
                self._token_expiry = datetime.fromtimestamp(payload["exp"])
        except Exception:
            self._token_expiry = None
    
    def is_authenticated(self) -> bool:
        """
        Check if user is currently authenticated.
        
        Returns:
            True if user has a valid token and user context, False otherwise
        """
        return (self.current_token is not None and 
                self.current_user is not None and
                not self.current_user.is_demo)
    
    
    def list_user_apps(self) -> list[Dict[str, Any]]:
        """
        List all apps in user's library from cloud storage.
        
        Returns apps sorted by last used date (newest first).
        
        Returns:
            List of app references with metadata
        """
        # Cloud storage only - no local fallback
        if self.is_authenticated() and hasattr(self, 'user_context'):
            try:
                from cloud_storage_adapter import CloudStorageAdapter
                storage = CloudStorageAdapter(self.user_context.token)
                # Run async operation in sync context
                import asyncio
                loop = asyncio.new_event_loop()
                cloud_apps = loop.run_until_complete(storage.list_apps())
                loop.close()
                
                return cloud_apps if cloud_apps else []
            except Exception:
                # Return empty list on error
                return []
        
        # Not authenticated - no apps available
        return []
    
    def update_app_usage(self, app_id: str) -> None:
        """
        Update usage statistics for an app in cloud storage.
        
        Increments launch count and updates last used timestamp.
        
        Args:
            app_id: App identifier to update
        """
        # Cloud-only: Update usage stats via cloud storage API
        # Note: This would ideally be implemented in the cloud storage adapter
        # For now, this is a no-op as usage tracking happens server-side
        pass
    
    def get_last_app(self) -> Optional[Dict[str, Any]]:
        """
        Get the most recently used app.
        
        Returns:
            App reference dict if any apps exist, None otherwise
        """
        apps = self.list_user_apps()
        return apps[0] if apps else None
    
    def get_app_by_name_fuzzy(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Find an app by fuzzy matching the name or requirements.
        
        Args:
            query: Search query to match against app names and requirements
            
        Returns:
            Best matching app reference dict if found, None otherwise
        """
        apps = self.list_user_apps()
        if not apps:
            return None
        
        query_lower = query.lower()
        
        # Try exact app_id match first
        for app in apps:
            if app.get('app_id', '').lower() == query_lower:
                return app
        
        # Then try partial name match
        for app in apps:
            if query_lower in app.get('name', '').lower():
                return app
        
        # Finally try requirements match
        for app in apps:
            if query_lower in app.get('requirements', '').lower():
                return app
        
        return None
    
    def save_conversation_state(self, app_id: str, messages: list[Dict[str, str]]) -> None:
        """
        Save conversation state for resuming later.
        
        Note: This is now a no-op as conversation state should be handled
        by cloud storage. Kept for compatibility.
        
        Args:
            app_id: App identifier
            messages: List of conversation messages
        """
        # Cloud-only: Conversation state is managed by cloud storage
        pass
    
    def load_conversation_state(self, app_id: str) -> Optional[Dict[str, Any]]:
        """
        Load saved conversation state.
        
        Note: This now returns None as conversation state should be loaded
        from cloud storage. Kept for compatibility.
        
        Args:
            app_id: App identifier
            
        Returns:
            None (cloud storage should be used directly)
        """
        # Cloud-only: Conversation state is managed by cloud storage
        return None
    
    async def _create_test_user(self, email: str, password: str) -> None:
        """
        Create a test user (for testing only).
        
        Args:
            email: Test user email
            password: Test user password
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                await client.post(
                    f"{self.auth_url}/register",
                    json={"email": email, "password": password}
                )
        except Exception:
            pass  # User might already exist