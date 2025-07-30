"""
GCP deployment configuration for Cogzia Alpha v1.5.

This configuration connects to Cogzia services deployed on Google Kubernetes Engine (GKE)
via the external load balancer ingress. All traffic goes through the single static IP
address with path-based routing.

NO FALLBACKS - This configuration requires GCP services to be available.
The application will exit if GCP services cannot be reached.

Created: 2025-07-15
Author: Claude Code
"""
import os
import sys
import httpx
import logging
from enum import Enum
from dataclasses import dataclass
from pathlib import Path

# Project root for file paths
PROJECT_ROOT = Path(__file__).parent.parent

# Suppress K8S localhost messages
os.environ["USE_K8S"] = "false"


# GCP Configuration
GCP_STATIC_IP = os.getenv("COGZIA_GCP_IP", "34.13.112.200")
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "696792272068")
GCP_REGION = os.getenv("GCP_REGION", "us-central1")
GCP_BASE_URL = "https://app.cogzia.com"
USE_GCP = os.getenv("USE_GCP", "true").lower() == "true"

# Enable SSL verification for production HTTPS endpoints
VERIFY_SSL = os.getenv("VERIFY_SSL", "true").lower() == "true"


def is_gcp_available() -> bool:
    """Check if GCP services are available."""
    if not USE_GCP:
        return False
        
    try:
        # Test connection to gateway health endpoint
        with httpx.Client(verify=VERIFY_SSL, timeout=5.0) as client:
            response = client.get(f"{GCP_BASE_URL}/health")
            return response.status_code == 200
    except Exception as e:
        print(f"⚠️  GCP services not reachable: {e}")
        return False


def get_gcp_service_url(service_path: str) -> str:
    """
    Get the URL for a GCP service through the ingress.
    
    All services are accessed through the single static IP with path routing:
    - /api/* routes to the API gateway
    - /ws/* routes to the WebSocket gateway
    
    Service name mapping for correct routes:
    - mcp-registry -> /api/v1/mcp/* (not /api/v1/mcp-registry/*)
    """
    # Remove leading slash if present
    service_path = service_path.lstrip("/")
    
    # Map service names to their actual route patterns
    # Map service names to their correct routes
    # Fixed: Use legacy routing for MCP Registry due to domain routing issues
    service_mappings = {
        "mcp-registry": "mcp-registry",  # Use legacy routing pattern
        "messages": "messages",  # chat service uses /messages endpoint
    }
    
    # Check if we need to map the service name
    if not service_path.startswith(("api/", "ws/")):
        # Extract service name from path
        parts = service_path.split("/", 1)
        service_name = parts[0]
        remaining_path = parts[1] if len(parts) > 1 else ""
        
        # Map service name if needed
        mapped_service = service_mappings.get(service_name, service_name)
        
        # Use direct routing for services in the mapping, api/v1 for others
        if service_name in service_mappings:
            service_path = f"{mapped_service}"
            if remaining_path:
                service_path += f"/{remaining_path}"
        else:
            service_path = f"api/v1/{mapped_service}"
            if remaining_path:
                service_path += f"/{remaining_path}"
    
    return f"{GCP_BASE_URL}/{service_path}"


# NO FALLBACKS - HARD EXIT IF GCP NOT AVAILABLE
if not USE_GCP:
    print("❌ GCP mode is disabled. This demo requires GCP services.")
    print("   Set USE_GCP=true to enable GCP mode.")
    sys.exit(1)

GCP_ENABLED = is_gcp_available()

if not GCP_ENABLED:
    print(f"❌ FATAL: GCP services at {GCP_STATIC_IP} are not available!")
    print("   This demo requires active GCP deployment.")
    print("   Please ensure:")
    print("   1. GCP services are deployed and running")
    print("   2. The ingress is properly configured") 
    print("   3. The IP address is correct")
    sys.exit(1)

# print(f"☁️  Using GCP-deployed services at {GCP_STATIC_IP}")  # Moved to main.py to avoid duplication

# All services go through the ingress gateway
# The gateway handles internal routing to the appropriate services
GATEWAY_URL = GCP_BASE_URL
AUTH_URL = get_gcp_service_url("auth")
ORCHESTRATOR_URL = get_gcp_service_url("orchestrator")
MCP_REGISTRY_URL = get_gcp_service_url("mcp-registry")
MCP_SERVER_MANAGER_URL = get_gcp_service_url("mcp-server-manager")
MCP_HOST_MANAGER_URL = get_gcp_service_url("mcp-host-manager")

# WebSocket URL - currently using HTTP ingress
# Will be upgraded to WSS when SSL is configured
WEBSOCKET_URL = f"ws://{GCP_STATIC_IP}/ws/gateway"

# Health check endpoints
HEALTH_CHECK_URL = get_gcp_service_url("health")


# Additional GCP-specific configuration
# Headers for GCP requests
DEFAULT_HEADERS = {
    "X-Forwarded-For": "cogzia-alpha-v1.5",
    "X-Forwarded-Proto": "http",  # Will be https after SSL setup
    "User-Agent": "Cogzia-Alpha-v1.5-GCP"
}

# Timeout configuration for GCP (may need higher values due to cold starts)
DEFAULT_TIMEOUT = httpx.Timeout(
    connect=10.0,      # Connection timeout
    read=30.0,         # Read timeout
    write=10.0,        # Write timeout
    pool=5.0           # Pool timeout
)


# Default app configuration template
DEFAULT_APP_CONFIG = {
    "requirements": "",
    "servers": [],
    "system_prompt": "",
    "app_name": "Custom AI App"
}

# Export configuration
__all__ = [
    "GCP_ENABLED",
    "GCP_STATIC_IP",
    "GATEWAY_URL",
    "AUTH_URL",
    "ORCHESTRATOR_URL",
    "MCP_REGISTRY_URL",
    "MCP_SERVER_MANAGER_URL",
    "MCP_HOST_MANAGER_URL",
    "WEBSOCKET_URL",
    "HEALTH_CHECK_URL",
    "DEFAULT_HEADERS",
    "DEFAULT_TIMEOUT",
    "VERIFY_SSL",
    "DEFAULT_APP_CONFIG",
]


def print_config():
    """Print the current configuration for debugging."""
    print("\n🔧 GCP Service Configuration:")
    print(f"  GCP Mode: {'☁️  Enabled' if GCP_ENABLED else '❌ Disabled'}")
    if GCP_ENABLED:
        print(f"  Static IP: {GCP_STATIC_IP}")
        print(f"  Base URL: {GCP_BASE_URL}")
    print(f"  Gateway URL: {GATEWAY_URL}")
    print(f"  Auth URL: {AUTH_URL}")
    print(f"  Orchestrator URL: {ORCHESTRATOR_URL}")
    print(f"  MCP Registry URL: {MCP_REGISTRY_URL}")
    print(f"  WebSocket URL: {WEBSOCKET_URL}")
    print(f"  SSL Verification: {'✅ Enabled' if VERIFY_SSL else '⚠️  Disabled'}")
    print()


def test_gcp_connection():
    """Test connection to GCP services."""
    print("\n🧪 Testing GCP Connection...")
    
    tests = [
        ("Gateway Health", f"{GCP_BASE_URL}/health"),
        ("Auth Service", f"{AUTH_URL}/health"),
        ("MCP Registry", f"{MCP_REGISTRY_URL}/health"),
    ]
    
    with httpx.Client(verify=VERIFY_SSL, timeout=DEFAULT_TIMEOUT) as client:
        for name, url in tests:
            try:
                response = client.get(url, headers=DEFAULT_HEADERS)
                if response.status_code == 200:
                    print(f"  ✅ {name}: OK")
                else:
                    print(f"  ❌ {name}: HTTP {response.status_code}")
            except Exception as e:
                print(f"  ❌ {name}: {type(e).__name__}: {e}")
    
    print()


# Service Descriptions for v1.5 (GCP-based)
SERVICE_DESCRIPTIONS = {
    "MCP Registry": {
        "port": 10008,
        "purpose": "Discovers MCP servers",
        "check_url": f"{MCP_REGISTRY_URL}/health",
        "required": True,
        "new_structure_path": "microservices/mcp_registry"
    },
    "Host Registry": {
        "port": None,
        "purpose": "Manages AI app hosts",
        "check_func": "check_host_registry",
        "required": True,
        "new_structure_path": "microservices/mcp_host_manager"
    },
    "Live Server Registry": {
        "port": None,
        "purpose": "Tracks running servers",
        "check_func": "check_live_server_registry",
        "required": True,
        "new_structure_path": "microservices/mcp_server_manager"
    },
    "MCP Factory": {
        "port": None,
        "purpose": "Creates MCP instances",
        "check_func": "check_mcp_factory",
        "required": True,
        "new_structure_path": "microservices/ai_app_creator"
    }
}

# Demo steps configuration
DEMO_STEPS = [
    "Service Health Check",
    "MCP Server Discovery",
    "App Requirements Analysis",
    "MCP Server Selection",
    "App Configuration",
    "App Execution",
    "Results Display"
]

class DebugLevel(Enum):
    """Debug levels for progressive testing and debugging."""
    CRAWL = "crawl"  # Maximum verbosity, step-by-step
    WALK = "walk"    # Key checkpoints only
    RUN = "run"      # Minimal output
    NONE = "none"    # Default user-friendly mode


@dataclass
class DemoStep:
    """Represents a single step in the demo."""
    name: str
    description: str
    func: callable


def configure_logging(verbose_mode: bool = False, show_mcp_logs: bool = False) -> None:
    """
    Configure logging for the application.
    
    Args:
        verbose_mode: Enable verbose logging
        show_mcp_logs: Show MCP-related logs
    """
    log_level = logging.DEBUG if verbose_mode else logging.WARNING
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Configure specific loggers
    if not show_mcp_logs:
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("mcp").setLevel(logging.ERROR)
        logging.getLogger("mcp.factory").setLevel(logging.ERROR)
        logging.getLogger("mcp.factory.MCPHostFactory").setLevel(logging.ERROR)
        logging.getLogger("MCPHostFactory").setLevel(logging.ERROR)
        logging.getLogger("shared.mcp").setLevel(logging.ERROR)


def validate_environment_variables(verbose: bool = False) -> dict:
    """
    Validate that required environment variables are available.
    
    Args:
        verbose: Whether to print detailed validation info
        
    Returns:
        Dict containing validation results with details about available/missing vars
    """
    # Import here to avoid circular dependencies
    from cogzia_api_key_client import ensure_anthropic_api_key
    
    # Try to fetch API key from Cogzia backend services
    api_key_available = ensure_anthropic_api_key()
    
    results = {
        'anthropic_api_key': api_key_available,
        'mongodb_uri': bool(os.getenv('MONGODB_URI')),
        'jwt_secret': bool(os.getenv('JWT_SECRET')),
        'ready_for_production': False
    }
    
    # Check if we have the minimum for real tool usage
    results['ready_for_production'] = results['anthropic_api_key']
    
    if verbose:
        print("\n🔍 Environment Variable Status:")
        api_key_source = ""
        if api_key_available:
            env_key = os.getenv('ANTHROPIC_API_KEY', '')
            if env_key.startswith('sk-'):
                # Check if this came from Secret Manager by looking for our marker
                if hasattr(os.environ.get('_COGZIA_API_KEY_SOURCE'), 'secret_manager'):
                    api_key_source = " (from GCP Secret Manager)"
                else:
                    api_key_source = " (from environment)"
            print(f"  ANTHROPIC_API_KEY: ✅ Present{api_key_source}")
        else:
            print(f"  ANTHROPIC_API_KEY: ❌ Missing - Cannot start in production mode")
        
        print(f"  MONGODB_URI: {'✅ Present' if results['mongodb_uri'] else '❌ Missing'}")
        print(f"  JWT_SECRET: {'✅ Present' if results['jwt_secret'] else '❌ Missing'}")
        
        if results['ready_for_production']:
            print(f"  Production Ready: ✅ Yes - Using live Anthropic API")
        else:
            print(f"  Production Ready: ❌ No - BLOCKED: Missing ANTHROPIC_API_KEY")
        print()
    
    return results


if __name__ == "__main__":
    print_config()
    if GCP_ENABLED:
        test_gcp_connection()