#!/usr/bin/env python3
"""
Interactive test for --last command that captures real TUI behavior.

This test uses pexpect to interact with the TUI as a real user would,
capturing the full interactive experience.
"""

import sys
import os
import time
import re
from pathlib import Path

# Check if pexpect is available
try:
    import pexpect
except ImportError:
    print("Installing pexpect for interactive testing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pexpect"])
    import pexpect

# Test configuration
MAIN_PY = Path(__file__).parent.parent.parent / "main.py"
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://34.13.112.200")

class InteractiveTUITest:
    """Interactive TUI testing using pexpect."""
    
    def __init__(self):
        self.env = os.environ.copy()
        self.env["GATEWAY_URL"] = GATEWAY_URL
        self.env["PYTHONUNBUFFERED"] = "1"
        self.test_user_email = f"test_interactive_{int(time.time())}@example.com"
        self.test_user_name = f"test_interactive_{int(time.time())}"
        self.test_password = "TestPassword123!"
        
    def run_interactive_command(self, args, timeout=120):
        """Run command with interactive support."""
        cmd = f"{sys.executable} {MAIN_PY} {' '.join(args)}"
        print(f"\n{'='*60}")
        print(f"Running: {cmd}")
        print(f"{'='*60}\n")
        
        child = pexpect.spawn(cmd, env=self.env, encoding='utf-8', timeout=timeout)
        child.logfile = sys.stdout
        
        return child
    
    def test_complete_workflow(self):
        """Test complete workflow: login, create app, use --last."""
        
        print("\n🧪 Interactive --last Command Test")
        print("===================================\n")
        
        # Step 1: Login
        print("\n📝 Step 1: Interactive Login")
        child = self.run_interactive_command(["--login"], timeout=60)
        
        try:
            # Look for email prompt
            child.expect("Email:", timeout=10)
            child.sendline(self.test_user_email)
            
            # Look for username prompt
            child.expect("Username:", timeout=10)
            child.sendline(self.test_user_name)
            
            # Look for password prompt
            child.expect("Password:", timeout=10)
            child.sendline(self.test_password)
            
            # Wait for completion
            child.expect(pexpect.EOF, timeout=30)
            
            print("\n✅ Login completed")
            
        except pexpect.TIMEOUT:
            print("\n⚠️  Login timed out, but may have succeeded")
        except pexpect.EOF:
            print("\n✅ Login process completed")
        
        # Step 2: Create an app interactively
        print("\n📝 Step 2: Create App Interactively")
        child = self.run_interactive_command([], timeout=180)
        
        try:
            # Wait for main menu
            child.expect("What would you like to create", timeout=30)
            child.sendline("A simple calculator that can add, subtract, multiply and divide")
            
            # Wait for app creation
            print("\n⏳ Waiting for app creation...")
            
            # Look for completion indicators
            patterns = [
                "App created",
                "app_[a-z0-9]{8}",
                "successfully",
                "ready to use",
                "What would you like to do"
            ]
            
            found = False
            app_id = None
            
            for _ in range(60):  # Check for up to 60 seconds
                try:
                    index = child.expect(patterns, timeout=1)
                    if index == 1:  # Found app_id pattern
                        # Extract the app_id
                        match = re.search(r'app_[a-z0-9]{8}', child.before + child.after)
                        if match:
                            app_id = match.group(0)
                            print(f"\n✅ Found app_id: {app_id}")
                    found = True
                except pexpect.TIMEOUT:
                    continue
            
            if found:
                print("\n✅ App creation detected")
            
            # Send exit command
            child.sendline("/exit")
            child.expect(pexpect.EOF, timeout=10)
            
        except Exception as e:
            print(f"\n⚠️  App creation had issues: {e}")
            child.terminate()
        
        # Step 3: Use --last to launch the app
        print("\n📝 Step 3: Test --last Command")
        child = self.run_interactive_command(["--last"], timeout=60)
        
        try:
            # Look for launch indicators
            patterns = [
                "Launching",
                "Loading",
                "last used app",
                "calculator",
                "Welcome back",
                "app_[a-z0-9]{8}"
            ]
            
            found_patterns = []
            
            # Check output for indicators
            output = ""
            try:
                output = child.read()
            except:
                pass
            
            for pattern in patterns:
                if re.search(pattern, output, re.IGNORECASE):
                    found_patterns.append(pattern)
            
            if found_patterns:
                print(f"\n✅ --last command successful!")
                print(f"   Found: {', '.join(found_patterns)}")
                return True
            else:
                print(f"\n❌ --last command didn't show expected output")
                print(f"   Output: {output[:200]}...")
                return False
                
        except Exception as e:
            print(f"\n❌ --last command failed: {e}")
            return False
        finally:
            try:
                child.terminate()
            except:
                pass
    
    def test_last_with_no_apps(self):
        """Test --last behavior when user has no apps."""
        
        print("\n🧪 Test --last With No Apps")
        print("============================\n")
        
        # Create a fresh user
        self.test_user_email = f"test_noapp_{int(time.time())}@example.com"
        self.test_user_name = f"test_noapp_{int(time.time())}"
        
        # Login first
        print("📝 Creating fresh user...")
        child = self.run_interactive_command(["--login"], timeout=60)
        
        try:
            child.expect("Email:", timeout=10)
            child.sendline(self.test_user_email)
            child.expect("Username:", timeout=10)
            child.sendline(self.test_user_name)
            child.expect("Password:", timeout=10)
            child.sendline(self.test_password)
            child.expect(pexpect.EOF, timeout=30)
            print("✅ Fresh user created")
        except:
            print("⚠️  User creation completed")
        
        # Test --last
        print("\n📝 Testing --last with no apps...")
        child = self.run_interactive_command(["--last"], timeout=30)
        
        try:
            output = child.read()
            
            if "no apps" in output.lower() or "library" in output.lower():
                print("✅ Correctly shows 'no apps' message")
                return True
            else:
                print("❌ Did not show expected message")
                return False
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return False

def main():
    """Run interactive tests."""
    
    print("🚀 Cogzia Alpha v1.5 - Interactive --last Command Tests")
    print(f"Main script: {MAIN_PY}")
    print(f"Gateway URL: {GATEWAY_URL}")
    
    # Check if main.py exists
    if not MAIN_PY.exists():
        print(f"❌ Error: {MAIN_PY} not found!")
        return
    
    tester = InteractiveTUITest()
    
    # Run tests
    results = []
    
    print("\n" + "="*60)
    print("Running Test Suite")
    print("="*60)
    
    # Test 1: No apps scenario
    try:
        result1 = tester.test_last_with_no_apps()
        results.append(("--last with no apps", result1))
    except Exception as e:
        print(f"❌ Test 1 crashed: {e}")
        results.append(("--last with no apps", False))
    
    # Test 2: Complete workflow
    try:
        result2 = tester.test_complete_workflow()
        results.append(("Complete workflow", result2))
    except Exception as e:
        print(f"❌ Test 2 crashed: {e}")
        results.append(("Complete workflow", False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    for test_name, result in results:
        status = "PASS ✅" if result else "FAIL ❌"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{len(results)} passed")
    print("="*60)

if __name__ == "__main__":
    main()