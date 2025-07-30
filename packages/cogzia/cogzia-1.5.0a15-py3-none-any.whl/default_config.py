"""
Default configuration for Cogzia Alpha v1.5.

This module provides default configuration values for alpha users,
including rate-limited API keys for demo purposes.
"""
import os
import base64

def get_default_anthropic_key():
    """
    Get the default Anthropic API key for alpha users.
    
    This is a rate-limited key specifically for Cogzia Alpha users
    to avoid requiring individual API keys during the alpha phase.
    """
    # Check if explicitly disabled
    if os.getenv('COGZIA_NO_DEFAULT_KEY') == 'true':
        return None
    
    # For security, we'll need to set this via environment on the server
    # This is just a placeholder that won't work without server-side config
    return None  # Server will provide this via environment