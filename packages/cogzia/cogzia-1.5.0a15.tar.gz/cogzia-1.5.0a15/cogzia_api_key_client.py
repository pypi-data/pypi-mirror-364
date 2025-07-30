"""
Cogzia API Key Client - Fetches API keys from Cogzia's backend services.

This module eliminates the need for users to have GCP credentials by fetching
the API key through Cogzia's deployed services which have the proper GCP access.

Created: 2025-07-23
Author: Claude Code
"""
import os
import httpx
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class CogziaApiKeyClient:
    """
    Client for fetching API keys from Cogzia's backend services.
    
    This approach allows users to get the centralized API key without
    needing their own GCP credentials or authentication.
    """
    
    def __init__(self, base_url: str = "https://app.cogzia.com"):
        """
        Initialize the API key client.
        
        Args:
            base_url: Base URL for Cogzia services
        """
        self.base_url = base_url
        self.api_key_endpoint = f"{base_url}/api/v1/system/api-key"
        self._cached_key = None
        
    def get_api_key(self) -> Optional[str]:
        """
        Fetch the ANTHROPIC_API_KEY from Cogzia's backend service.
        
        Requires user authentication - users must run 'cogzia --login' first.
        
        Returns:
            The API key if successful, None otherwise
        """
        # Check if already cached
        if self._cached_key:
            return self._cached_key
        
        # First check environment variable (user's own key takes precedence)
        env_key = os.getenv("ANTHROPIC_API_KEY")
        if env_key and env_key.strip().startswith('sk-'):
            logger.info("Using user-provided ANTHROPIC_API_KEY from environment")
            self._cached_key = env_key.strip()
            return env_key.strip()
        
        # Get authentication token
        auth_token = self._get_auth_token()
        if not auth_token:
            logger.error("❌ No authentication token found. Please run 'cogzia --login' first.")
            return None
        
        # Fetch from Cogzia's backend service
        try:
            with httpx.Client(timeout=10.0, verify=False) as client:
                # Make authenticated request to get the API key
                response = client.get(
                    self.api_key_endpoint,
                    headers={
                        "User-Agent": "Cogzia-Alpha-v1.5-Client",
                        "Accept": "application/json",
                        "Authorization": f"Bearer {auth_token}"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    api_key = data.get("anthropic_api_key")
                    
                    if api_key and api_key.startswith('sk-'):
                        logger.info("✅ Successfully retrieved API key from Cogzia backend")
                        self._cached_key = api_key
                        # Set it in the environment for the current process
                        os.environ["ANTHROPIC_API_KEY"] = api_key
                        return api_key
                    else:
                        logger.error("❌ Invalid API key format received from backend")
                        
                elif response.status_code == 401:
                    logger.error("❌ Authentication failed. Please run 'cogzia --login' to authenticate.")
                    
                elif response.status_code == 503:
                    logger.warning("⚠️  Cogzia backend services are starting up, please wait...")
                    
                else:
                    logger.error(f"❌ Failed to fetch API key: HTTP {response.status_code}")
                    
        except httpx.ConnectError:
            logger.error("❌ Cannot connect to Cogzia backend services")
        except httpx.TimeoutException:
            logger.error("❌ Timeout connecting to Cogzia backend services")
        except Exception as e:
            logger.error(f"❌ Unexpected error fetching API key: {e}")
        
        return None
    
    def _get_auth_token(self) -> Optional[str]:
        """
        Get the authentication token for API requests.
        
        Looks for token in various locations where Cogzia might store it.
        
        Returns:
            The auth token if found, None otherwise
        """
        # Check environment variable first
        token = os.getenv("COGZIA_AUTH_TOKEN")
        if token and token != "demo_token_123":
            return token
        
        # Check for token file in user's home directory
        try:
            from pathlib import Path
            token_file = Path.home() / ".cogzia" / "auth_token"
            if token_file.exists():
                token = token_file.read_text().strip()
                if token and token != "demo_token_123":
                    return token
        except Exception:
            pass
        
        # Check for token in config file
        try:
            import json
            config_file = Path.home() / ".cogzia" / "config.json"
            if config_file.exists():
                config = json.loads(config_file.read_text())
                token = config.get("auth_token")
                if token and token != "demo_token_123":
                    return token
        except Exception:
            pass
        
        return None
    
    def ensure_api_key(self) -> bool:
        """
        Ensure the ANTHROPIC_API_KEY is available.
        
        Returns:
            True if API key is available, False otherwise
        """
        key = self.get_api_key()
        return key is not None


# Global instance for easy access
_api_key_client = None


def get_api_key_client() -> CogziaApiKeyClient:
    """
    Get the global API key client instance.
    
    Returns:
        The global CogziaApiKeyClient instance
    """
    global _api_key_client
    if _api_key_client is None:
        _api_key_client = CogziaApiKeyClient()
    return _api_key_client


def ensure_anthropic_api_key() -> bool:
    """
    Ensure the ANTHROPIC_API_KEY is available via Cogzia's backend.
    
    This is a convenience function that uses the global client.
    
    Returns:
        True if API key is available, False otherwise
    """
    client = get_api_key_client()
    return client.ensure_api_key()