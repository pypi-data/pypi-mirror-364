#!/usr/bin/env python3
"""
Test interactive session with Cogzia Alpha v1.3.

This script simulates an interactive session by programmatically sending
multiple messages to test conversation continuity and tool usage.
"""
import asyncio
import os
import sys
import subprocess
import time
from typing import List, Tuple
import pexpect

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))


def run_interactive_test(test_name: str, requirements: str, messages: List[str]) -> Tuple[bool, str]:
    """
    Run an interactive test session with v1.3.
    
    Args:
        test_name: Name of the test
        requirements: App requirements
        messages: List of messages to send
        
    Returns:
        Tuple of (success, output)
    """
    print(f"\n{'='*60}")
    print(f"Running: {test_name}")
    print(f"Requirements: {requirements}")
    print(f"Messages: {len(messages)}")
    print('='*60)
    
    try:
        # Start the v1.3 main.py in interactive mode
        cmd = f'uv run python tools/demos/cogzia_alpha_v1_3/main.py --no-save --requirements "{requirements}"'
        
        # Use pexpect for interactive control
        child = pexpect.spawn(cmd, timeout=30, encoding='utf-8')
        child.setecho(False)
        
        output_lines = []
        
        # Wait for the app to be ready
        print("Waiting for app to start...")
        child.expect(['Your AI app is ready!', 'Test query completed'], timeout=20)
        
        # Clear any initial output
        child.expect(['You:', 'Enter your message'], timeout=5)
        
        # Send each message
        for i, message in enumerate(messages, 1):
            print(f"\n[Turn {i}] Sending: {message}")
            
            # Send the message
            child.sendline(message)
            
            # Wait for response
            time.sleep(0.5)  # Small delay to let response start
            
            # Capture response until next prompt
            try:
                index = child.expect(['You:', 'Enter your message', pexpect.EOF, pexpect.TIMEOUT], timeout=10)
                response = child.before
                output_lines.append(f"Turn {i} - User: {message}")
                output_lines.append(f"Turn {i} - Assistant: {response.strip()}")
                print(f"Response received (length: {len(response)} chars)")
                
                # Check if we see tool usage
                if '🔧' in response:
                    print("  ✓ Tool usage detected")
                
            except pexpect.TIMEOUT:
                print("  ⚠️ Timeout waiting for response")
                output_lines.append(f"Turn {i} - TIMEOUT")
        
        # Send exit command
        print("\nSending exit command...")
        child.sendline("exit")
        child.expect(pexpect.EOF, timeout=5)
        
        # Get full output
        full_output = '\n'.join(output_lines)
        
        print("\n✅ Test completed successfully")
        return True, full_output
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False, str(e)


def run_scripted_test(test_name: str, requirements: str, messages: List[str]) -> Tuple[bool, str]:
    """
    Run a scripted test using echo to pipe messages.
    
    Args:
        test_name: Name of the test
        requirements: App requirements
        messages: List of messages to send
        
    Returns:
        Tuple of (success, output)
    """
    print(f"\n{'='*60}")
    print(f"Running Scripted: {test_name}")
    print(f"Requirements: {requirements}")
    print(f"Messages: {len(messages)}")
    print('='*60)
    
    try:
        # Create input script
        input_script = '\n'.join(messages + ['exit'])
        
        # Run v1.3 with piped input
        cmd = f'echo "{input_script}" | uv run python tools/demos/cogzia_alpha_v1_3/main.py --no-save --requirements "{requirements}"'
        
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print("✅ Test completed successfully")
            
            # Check for tool usage
            if '🔧' in result.stdout:
                print("  ✓ Tool usage detected")
            
            # Check for all messages processed
            for i, msg in enumerate(messages, 1):
                if msg in result.stdout:
                    print(f"  ✓ Message {i} processed")
            
            return True, result.stdout
        else:
            print(f"❌ Test failed with return code: {result.returncode}")
            return False, result.stderr
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False, str(e)


async def main():
    """Run all interactive tests."""
    
    # Check for API key
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("❌ ANTHROPIC_API_KEY not set. Please set it to run tests.")
        return
    
    # Test scenarios
    test_scenarios = [
        {
            'name': 'Basic Multi-Turn Time Test',
            'requirements': 'I need an assistant that tells time',
            'messages': [
                "What time is it?",
                "What about in London?",
                "Thank you!"
            ]
        },
        {
            'name': 'Tool Switching Test',
            'requirements': 'I want an assistant with time and calculation abilities',
            'messages': [
                "What's the current time?",
                "Calculate 42 * 17",
                "What time will it be in 2 hours?"
            ]
        },
        {
            'name': 'Context Retention Test',
            'requirements': 'I need a helpful assistant',
            'messages': [
                "My name is Bob and I'm planning a trip",
                "What time is it in Paris?",
                "What about Sydney?",
                "Which city has the later time?"
            ]
        }
    ]
    
    print("\n🧪 Testing Cogzia Alpha v1.3 Interactive Sessions")
    print("=" * 60)
    
    # Try different test methods
    print("\n1️⃣ Testing with pexpect (interactive control)...")
    for scenario in test_scenarios[:1]:  # Run first test with pexpect
        success, output = run_interactive_test(
            scenario['name'],
            scenario['requirements'],
            scenario['messages']
        )
        
        if success:
            print(f"\n📝 Output preview:")
            print(output[:500] + "..." if len(output) > 500 else output)
    
    print("\n2️⃣ Testing with scripted input...")
    for scenario in test_scenarios:
        success, output = run_scripted_test(
            scenario['name'],
            scenario['requirements'],
            scenario['messages']
        )
        
        if success and '🔧' in output:
            # Count tool uses
            tool_count = output.count('🔧')
            print(f"  📊 Tool calls detected: {tool_count}")
    
    print("\n✅ All tests completed!")


if __name__ == "__main__":
    # Check if pexpect is available
    try:
        import pexpect
        print("✓ pexpect available for interactive testing")
    except ImportError:
        print("⚠️ pexpect not available - install with: pip install pexpect")
        print("  Falling back to scripted tests only")
    
    asyncio.run(main())