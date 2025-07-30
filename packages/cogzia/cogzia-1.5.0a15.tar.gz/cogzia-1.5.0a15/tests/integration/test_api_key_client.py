#!/usr/bin/env python3
"""
Test script for Cogzia API key client.
Tests fetching API key from Cogzia's backend without requiring GCP credentials.

Usage:
    python test_api_key_client.py
"""
import os
import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_api_key_client():
    """Test the Cogzia API key client functionality."""
    print("🧪 Testing Cogzia API Key Client")
    print("=" * 50)
    
    try:
        from cogzia_api_key_client import CogziaApiKeyClient, ensure_anthropic_api_key
        
        # Test 1: Initialize client
        print("\n1. Initializing API key client...")
        client = CogziaApiKeyClient()
        print(f"   ✅ Client initialized with endpoint: {client.api_key_endpoint}")
        
        # Test 2: Clear any existing environment variable to test fetching
        print("\n2. Testing API key retrieval...")
        original_key = os.environ.get("ANTHROPIC_API_KEY")
        
        # Clear environment variable to test backend retrieval
        if "ANTHROPIC_API_KEY" in os.environ:
            del os.environ["ANTHROPIC_API_KEY"]
        
        success = ensure_anthropic_api_key()
        new_key = os.environ.get("ANTHROPIC_API_KEY")
        
        if success and new_key:
            print(f"   ✅ API key retrieved successfully")
            print(f"   Key starts with: {new_key[:8]}..." if len(new_key) > 8 else "   Short key")
            print(f"   Key length: {len(new_key)} characters")
        else:
            print("   ❌ Could not retrieve API key from backend")
        
        # Test 3: Test caching
        print("\n3. Testing API key caching...")
        cached_success = ensure_anthropic_api_key()
        if cached_success:
            print("   ✅ Cached API key access working")
        else:
            print("   ❌ Caching failed")
        
        # Restore original key if it existed
        if original_key:
            os.environ["ANTHROPIC_API_KEY"] = original_key
        elif "ANTHROPIC_API_KEY" in os.environ:
            del os.environ["ANTHROPIC_API_KEY"]
        
        # Test 4: Test config validation
        print("\n4. Testing config validation integration...")
        from config import validate_environment_variables
        
        results = validate_environment_variables(verbose=False)
        print(f"   API key available: {'✅ Yes' if results['anthropic_api_key'] else '❌ No'}")
        print(f"   Ready for production: {'✅ Yes' if results['ready_for_production'] else '❌ No'}")
        
        return success
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_local_gateway():
    """Test if local gateway is running with API key endpoint."""
    print("\n🌐 Testing Local Gateway API Key Endpoint")
    print("=" * 50)
    
    try:
        import httpx
        
        # Test different possible URLs
        test_urls = [
            "http://localhost:10000/api/v1/system/api-key",  # Standard gateway port
            "https://app.cogzia.com/api/v1/system/api-key",  # Production URL
        ]
        
        for url in test_urls:
            try:
                print(f"\n   Testing: {url}")
                with httpx.Client(timeout=5.0, verify=False) as client:
                    response = client.get(url)
                    
                    if response.status_code == 200:
                        data = response.json()
                        api_key = data.get("anthropic_api_key", "")
                        
                        print(f"   ✅ Success! Status: {response.status_code}")
                        print(f"   Key starts with: {api_key[:8]}...")
                        print(f"   Source: {data.get('source', 'unknown')}")
                        return True
                        
                    elif response.status_code == 503:
                        print(f"   ⚠️  Service unavailable: {response.status_code}")
                        
                    else:
                        print(f"   ❌ Failed: HTTP {response.status_code}")
                        
            except httpx.ConnectError:
                print(f"   ❌ Connection failed to {url}")
            except httpx.TimeoutException:
                print(f"   ❌ Timeout connecting to {url}")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        return False
        
    except ImportError:
        print("   ❌ httpx not available for testing gateway endpoint")
        return False


def main():
    """Run all tests."""
    print("🚀 Cogzia API Key Client Integration Test")
    print("=" * 60)
    
    test1_passed = test_api_key_client()
    test2_passed = test_local_gateway()
    
    print("\n📊 Test Summary")
    print("=" * 50)
    print(f"API Key Client Test:  {'✅ PASS' if test1_passed else '❌ FAIL'}")
    print(f"Gateway Endpoint Test: {'✅ PASS' if test2_passed else '❌ FAIL'}")
    
    if test1_passed or test2_passed:
        print("\n🎉 API key integration is working!")
        print("Users will not need to set up their own API keys.")
        return 0
    else:
        print("\n⚠️  API key integration needs setup.")
        print("Either the backend service needs to be deployed or GCP access configured.")
        return 1


if __name__ == "__main__":
    sys.exit(main())