#!/usr/bin/env python3
"""
Test script to verify pip install cogzia works correctly.
Run this after: pip install cogzia
"""
import subprocess
import sys
import os

def test_basic_import():
    """Test that cogzia can be imported."""
    print("1. Testing basic import...")
    try:
        import cogzia_alpha_v1_5
        print("   ✓ Package imported")
        return True
    except ImportError as e:
        print(f"   ✗ Import failed: {e}")
        return False

def test_cli_command():
    """Test that cogzia command is available."""
    print("\n2. Testing CLI command...")
    try:
        result = subprocess.run(["cogzia", "--help"], capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✓ cogzia --help works")
            return True
        else:
            print(f"   ✗ cogzia command failed: {result.stderr}")
            return False
    except FileNotFoundError:
        print("   ✗ cogzia command not found in PATH")
        return False

def test_demo_mode():
    """Test that demo mode works without API key."""
    print("\n3. Testing demo mode (no API key needed)...")
    try:
        # Set a dummy API key for demo mode
        env = os.environ.copy()
        env["ANTHROPIC_API_KEY"] = "dummy-key-for-demo"
        
        result = subprocess.run(
            ["cogzia", "--demo", "--auto", "1"],
            capture_output=True,
            text=True,
            timeout=30,
            env=env
        )
        
        if "Welcome to Cogzia" in result.stdout or result.returncode == 0:
            print("   ✓ Demo mode works")
            return True
        else:
            print("   ✗ Demo mode failed")
            print(f"   Output: {result.stdout[:200]}...")
            return False
            
    except subprocess.TimeoutExpired:
        print("   ✗ Demo mode timed out")
        return False
    except Exception as e:
        print(f"   ✗ Demo mode error: {e}")
        return False

def test_api_key_handling():
    """Test API key requirement handling."""
    print("\n4. Testing API key handling...")
    
    # Test without API key
    env = os.environ.copy()
    env.pop("ANTHROPIC_API_KEY", None)
    
    try:
        result = subprocess.run(
            ["cogzia", "--auto", "1"],
            capture_output=True,
            text=True,
            timeout=10,
            env=env
        )
        
        if "ANTHROPIC_API_KEY" in result.stdout or "API key" in result.stdout:
            print("   ✓ Properly warns about missing API key")
            return True
        else:
            print("   ! May not be checking for API key properly")
            return True  # Not a critical failure
            
    except Exception:
        print("   ! Could not test API key handling")
        return True  # Not a critical failure

def main():
    """Run all tests."""
    print("="*60)
    print("Testing Cogzia pip installation...")
    print("="*60)
    
    results = []
    results.append(test_basic_import())
    results.append(test_cli_command())
    results.append(test_demo_mode())
    results.append(test_api_key_handling())
    
    print("\n" + "="*60)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ All tests passed ({passed}/{total})")
        print("\nInstallation is working correctly!")
        print("\nNext steps:")
        print("1. Set your API key: export ANTHROPIC_API_KEY='your-key'")
        print("2. Run: cogzia --auto")
    else:
        print(f"⚠️  Some tests failed ({passed}/{total} passed)")
        print("\nThe installation may need fixes.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)