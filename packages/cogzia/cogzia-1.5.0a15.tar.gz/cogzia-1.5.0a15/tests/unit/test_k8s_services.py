#!/usr/bin/env python3
"""
Test script to verify Kubernetes services are accessible.
"""
import asyncio
import httpx
from config_k8s import (
    K8S_ENABLED,
    GATEWAY_URL,
    AUTH_URL,
    ORCHESTRATOR_URL,
    MCP_REGISTRY_URL,
    WEBSOCKET_URL,
    print_config
)


async def test_service(name: str, url: str, path: str = "/") -> bool:
    """Test if a service is accessible."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{url}{path}")
            status = "✅" if response.status_code < 500 else "⚠️"
            print(f"  {status} {name}: {url} -> {response.status_code}")
            return response.status_code < 500
    except Exception as e:
        print(f"  ❌ {name}: {url} -> {type(e).__name__}: {str(e)}")
        return False


async def main():
    """Test all configured services."""
    print("🔍 Testing Kubernetes Service Connectivity")
    print("=" * 50)
    
    # Show configuration
    print_config()
    
    # Test each service
    print("🧪 Service Tests:")
    print("-" * 50)
    
    services_to_test = [
        ("Gateway", GATEWAY_URL, "/health"),
        ("Auth", AUTH_URL, "/"),
        ("Orchestrator", ORCHESTRATOR_URL, "/health"),
        ("MCP Registry", MCP_REGISTRY_URL, "/health"),
    ]
    
    results = []
    for name, url, path in services_to_test:
        result = await test_service(name, url, path)
        results.append((name, result))
    
    # WebSocket test (different protocol)
    print(f"  ℹ️  WebSocket: {WEBSOCKET_URL} (not tested via HTTP)")
    
    print()
    print("📊 Summary:")
    print("-" * 50)
    
    working = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"Services working: {working}/{total}")
    
    if working == total:
        print("✅ All services are accessible!")
    elif working > 0:
        print("⚠️  Some services are not accessible")
    else:
        print("❌ No services are accessible")
    
    # Show missing services
    missing = [name for name, result in results if not result]
    if missing:
        print(f"\nMissing services: {', '.join(missing)}")
        print("\nTroubleshooting:")
        print("1. Check if services are running: kubectl get pods -n cogzia-dev")
        print("2. Set up port forwarding: ./setup_k8s_port_forward.sh")
        print("3. Check service logs: kubectl logs -n cogzia-dev -l app=<service>")


if __name__ == "__main__":
    asyncio.run(main())