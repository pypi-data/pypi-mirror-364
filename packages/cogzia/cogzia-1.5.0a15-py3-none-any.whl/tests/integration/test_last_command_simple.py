#!/usr/bin/env python3
"""
Simple test for --last command that simulates real user interaction.

This test:
1. Logs in as a test user
2. Creates an app
3. Uses --last to launch it
4. Captures and verifies all output
"""

import subprocess
import sys
import os
import time
from pathlib import Path

# Test configuration
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://34.13.112.200")
MAIN_PY = Path(__file__).parent.parent.parent / "main.py"

def run_command(args, input_text=None, timeout=60):
    """Run the TUI with given arguments."""
    cmd = [sys.executable, str(MAIN_PY)] + args
    env = os.environ.copy()
    env["GATEWAY_URL"] = GATEWAY_URL
    
    print(f"\n{'='*60}")
    print(f"Running: {' '.join(cmd)}")
    print(f"{'='*60}\n")
    
    try:
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
            cwd=str(MAIN_PY.parent)
        )
        
        stdout, stderr = process.communicate(input=input_text, timeout=timeout)
        
        print("STDOUT:")
        print(stdout)
        print("\nSTDERR:")
        print(stderr)
        print(f"\nReturn code: {process.returncode}")
        print(f"{'='*60}\n")
        
        return process.returncode, stdout, stderr
        
    except subprocess.TimeoutExpired:
        process.kill()
        print(f"TIMEOUT after {timeout} seconds")
        return -1, "", "TIMEOUT"

def test_last_command_flow():
    """Test the complete --last command flow."""
    
    print("\n🧪 Testing --last Command Flow")
    print("================================\n")
    
    # Generate unique test user
    timestamp = int(time.time())
    test_email = f"test_last_{timestamp}@example.com"
    test_username = f"test_last_{timestamp}"
    test_password = "TestPassword123!"
    
    # Step 1: Login/Register
    print("Step 1: Login/Register Test User")
    login_input = f"{test_email}\n{test_username}\n{test_password}\n"
    rc, stdout, stderr = run_command(["--login"], input_text=login_input)
    
    if rc != 0 and "already registered" not in stdout:
        print("❌ Login/Register failed")
        return False
    
    print("✅ User authenticated")
    
    # Step 2: Create an app
    print("\nStep 2: Create a Test App")
    rc, stdout, stderr = run_command(
        ["--auto", "3", "--requirements", "Simple calculator app"],
        timeout=90
    )
    
    if rc != 0:
        print("❌ App creation failed")
        return False
    
    # Extract app_id
    app_id = None
    for line in stdout.split('\n'):
        if "app_" in line and ("created" in line.lower() or "saved" in line.lower()):
            # Find app_id pattern
            import re
            match = re.search(r'app_[a-z0-9]{8}', line)
            if match:
                app_id = match.group(0)
                break
    
    if app_id:
        print(f"✅ Created app: {app_id}")
    else:
        print("⚠️  Could not extract app_id, but app may have been created")
    
    # Step 3: List apps (to verify)
    print("\nStep 3: List User Apps")
    rc, stdout, stderr = run_command(["--list-my-apps"])
    
    if rc == 0:
        app_count = stdout.count("app_")
        print(f"✅ Found {app_count} apps")
    else:
        print("⚠️  List apps returned non-zero but may still work")
    
    # Step 4: Test --last command
    print("\nStep 4: Test --last Command")
    rc, stdout, stderr = run_command(["--last"], timeout=30)
    
    # Check for success indicators
    success_indicators = [
        "launching",
        "loading", 
        "last used app",
        "calculator",  # Should match our app
        "app_"
    ]
    
    found_indicators = []
    for indicator in success_indicators:
        if indicator in stdout.lower():
            found_indicators.append(indicator)
    
    if found_indicators:
        print(f"✅ --last command worked! Found: {', '.join(found_indicators)}")
        return True
    else:
        print("❌ --last command did not show expected output")
        return False

def test_last_without_apps():
    """Test --last when user has no apps."""
    
    print("\n🧪 Testing --last Without Apps")
    print("================================\n")
    
    # Generate unique test user
    timestamp = int(time.time())
    test_email = f"test_empty_{timestamp}@example.com"
    test_username = f"test_empty_{timestamp}"
    test_password = "TestPassword123!"
    
    # Login as new user
    print("Step 1: Login as New User")
    login_input = f"{test_email}\n{test_username}\n{test_password}\n"
    rc, stdout, stderr = run_command(["--login"], input_text=login_input)
    
    # Test --last with no apps
    print("\nStep 2: Test --last with No Apps")
    rc, stdout, stderr = run_command(["--last"])
    
    # Should show "no apps" message
    if "no apps" in stdout.lower() or "library" in stdout.lower():
        print("✅ Correctly shows 'no apps' message")
        return True
    else:
        print("❌ Did not show expected 'no apps' message")
        return False

def main():
    """Run all tests."""
    
    print("🚀 Cogzia Alpha v1.5 - --last Command Test Suite")
    print(f"Gateway URL: {GATEWAY_URL}")
    print(f"Main script: {MAIN_PY}")
    
    tests = [
        ("--last with no apps", test_last_without_apps),
        ("--last complete flow", test_last_command_flow),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'#'*60}")
        print(f"Running: {test_name}")
        print(f"{'#'*60}")
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = 0
    for test_name, result in results:
        status = "PASS ✅" if result else "FAIL ❌"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(results)} passed")
    print("="*60)

if __name__ == "__main__":
    main()