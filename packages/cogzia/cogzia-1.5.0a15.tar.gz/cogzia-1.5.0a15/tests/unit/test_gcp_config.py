#!/usr/bin/env python3
"""
Test script for Cogzia Alpha v1.5 GCP configuration.

This script tests the GCP service connectivity and configuration.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from config import (
        GCP_ENABLED,
        GCP_STATIC_IP,
        GATEWAY_URL,
        AUTH_URL,
        ORCHESTRATOR_URL,
        MCP_REGISTRY_URL,
        WEBSOCKET_URL,
        print_config,
        test_gcp_connection
    )
    
    print("🚀 Cogzia Alpha v1.5 - GCP Configuration Test")
    print("=" * 50)
    
    # Print configuration
    print_config()
    
    # Test GCP connection
    if GCP_ENABLED:
        test_gcp_connection()
    else:
        print("❌ GCP is not enabled")
        
    print("✅ Configuration test completed")
    
except Exception as e:
    print(f"❌ Configuration test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)