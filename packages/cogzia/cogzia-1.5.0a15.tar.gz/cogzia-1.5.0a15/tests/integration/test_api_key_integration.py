#!/usr/bin/env python3
"""
Test script for GCP API key integration.
This script tests the API key manager functionality in isolation.

Usage:
    python test_api_key_integration.py
"""
import os
import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_api_key_manager():
    """Test the GCP API key manager functionality."""
    print("🧪 Testing GCP API Key Manager")
    print("=" * 50)
    
    try:
        from gcp_api_key_manager import GCPApiKeyManager, ensure_anthropic_api_key
        
        # Test 1: Check if GCP libraries are available
        print("\n1. Checking GCP library availability...")
        manager = GCPApiKeyManager()
        if manager.secret_client:
            print("   ✅ GCP Secret Manager client initialized")
        else:
            print("   ⚠️  GCP Secret Manager client not available")
        
        # Test 2: Check if running on GCP
        print("\n2. Checking GCP environment...")
        is_gcp = GCPApiKeyManager.is_running_on_gcp()
        print(f"   Running on GCP: {'✅ Yes' if is_gcp else '❌ No'}")
        
        # Test 3: Try to get API key
        print("\n3. Testing API key retrieval...")
        original_key = os.environ.get("ANTHROPIC_API_KEY")
        
        # Clear environment variable to test GCP retrieval
        if "ANTHROPIC_API_KEY" in os.environ:
            del os.environ["ANTHROPIC_API_KEY"]
        
        success = ensure_anthropic_api_key()
        new_key = os.environ.get("ANTHROPIC_API_KEY")
        
        if success and new_key:
            print(f"   ✅ API key retrieved successfully")
            print(f"   Key starts with: {new_key[:8]}..." if len(new_key) > 8 else "   Short key")
        else:
            print("   ❌ Could not retrieve API key")
        
        # Restore original key if it existed
        if original_key:
            os.environ["ANTHROPIC_API_KEY"] = original_key
        elif "ANTHROPIC_API_KEY" in os.environ:
            del os.environ["ANTHROPIC_API_KEY"]
        
        # Test 4: Test config validation
        print("\n4. Testing config validation...")
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


def test_demo_mode_fallback():
    """Test that demo mode still works when API key is not available."""
    print("\n🎭 Testing Demo Mode Fallback")
    print("=" * 50)
    
    try:
        from config import validate_environment_variables
        
        # Temporarily remove API key
        original_key = os.environ.get("ANTHROPIC_API_KEY")
        if "ANTHROPIC_API_KEY" in os.environ:
            del os.environ["ANTHROPIC_API_KEY"]
        
        # Force the manager to not find any key
        from gcp_api_key_manager import get_api_key_manager
        manager = get_api_key_manager()
        manager._cached_key = None
        manager.secret_client = None
        
        results = validate_environment_variables(verbose=False)
        
        # Restore original key
        if original_key:
            os.environ["ANTHROPIC_API_KEY"] = original_key
        
        if not results['ready_for_production']:
            print("   ✅ Demo mode fallback working correctly")
            return True
        else:
            print("   ❌ Demo mode fallback not triggered")
            return False
            
    except Exception as e:
        print(f"   ❌ Demo mode test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 Cogzia API Key Integration Test")
    print("=" * 60)
    
    test1_passed = test_api_key_manager()
    test2_passed = test_demo_mode_fallback()
    
    print("\n📊 Test Summary")
    print("=" * 50)
    print(f"API Key Manager Test: {'✅ PASS' if test1_passed else '❌ FAIL'}")
    print(f"Demo Mode Fallback:   {'✅ PASS' if test2_passed else '❌ FAIL'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())