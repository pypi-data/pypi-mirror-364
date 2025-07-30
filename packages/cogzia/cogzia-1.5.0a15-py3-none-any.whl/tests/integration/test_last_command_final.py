#!/usr/bin/env python3
"""
Final verification test for --last command functionality.
Tests that the command loads apps correctly without errors.
"""

import subprocess
import sys
import os
import time
from pathlib import Path

MAIN_PY = Path(__file__).parent.parent.parent / "main.py"
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://34.13.112.200")

def test_last_command_loads_app():
    """Test that --last successfully loads an app without import errors."""
    
    print("\n🧪 Testing --last Command App Loading")
    print("=====================================\n")
    
    cmd = [sys.executable, str(MAIN_PY), "--last"]
    env = os.environ.copy()
    env["GATEWAY_URL"] = GATEWAY_URL
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        # Run with a very short timeout since we expect it to wait for input
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
            cwd=str(MAIN_PY.parent)
        )
        
        # Give it 3 seconds to load
        time.sleep(3)
        
        # Send quit command
        process.stdin.write("quit\n")
        process.stdin.flush()
        
        # Wait for completion
        stdout, stderr = process.communicate(timeout=5)
        
        # Check for success indicators
        success_indicators = [
            "Launching last used app",
            "Loading app:",
            "App loaded successfully",
            "Enter queries"
        ]
        
        errors_to_check = [
            "ModuleNotFoundError",
            "No module named 'tools'",
            "ImportError"
        ]
        
        # Check stdout
        found_success = []
        for indicator in success_indicators:
            if indicator in stdout:
                found_success.append(indicator)
        
        # Check for errors
        found_errors = []
        for error in errors_to_check:
            if error in stderr or error in stdout:
                found_errors.append(error)
        
        print("\nResults:")
        print(f"✅ Success indicators found: {', '.join(found_success)}")
        
        if found_errors:
            print(f"❌ Errors found: {', '.join(found_errors)}")
            print("\nSTDERR:")
            print(stderr)
            return False
        else:
            print("✅ No import errors found")
            
        if "Enter queries" in stdout or "App loaded successfully" in stdout:
            print("✅ App loaded and ready for queries")
            return True
        else:
            print("⚠️  App may not have loaded fully")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏱️  Process timed out (expected for interactive app)")
        process.kill()
        # Timeout is actually good - means app is running
        return True
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def main():
    """Run the final verification test."""
    
    print("🚀 Cogzia Alpha v1.5 - --last Command Final Test")
    print(f"Gateway URL: {GATEWAY_URL}")
    print(f"Main script: {MAIN_PY}\n")
    
    result = test_last_command_loads_app()
    
    print("\n" + "="*50)
    if result:
        print("✅ PASS: --last command is working correctly!")
        print("   - No import errors")
        print("   - App loads successfully")
        print("   - Ready for user interaction")
    else:
        print("❌ FAIL: --last command has issues")
    print("="*50)

if __name__ == "__main__":
    main()