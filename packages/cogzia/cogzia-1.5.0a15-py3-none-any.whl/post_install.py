#!/usr/bin/env python3
"""
Post-installation setup for Cogzia.
This script runs after pip install to help users get started.
"""
import os
import sys
from pathlib import Path

def setup_api_key():
    """Help user set up their API key."""
    print("\n🔑 API Key Setup")
    print("-" * 40)
    
    # Check if API key is already set locally
    if os.environ.get("ANTHROPIC_API_KEY"):
        print("✓ ANTHROPIC_API_KEY is already set in environment")
        return True
    
    # Check for .env file
    env_path = Path.home() / ".cogzia" / ".env"
    if env_path.exists():
        print(f"✓ Found local configuration at {env_path}")
        return True
    
    print("✅ Cogzia uses a centralized API key - no manual setup required!")
    print("   Just authenticate once with 'cogzia --login' to get started.")
    print("\n📝 Getting Started:")
    print("1. Run: cogzia --login")
    print("2. Then run: cogzia")
    print("\nAlternatively, you can set your own API key (optional):")
    print("1. Get your key at: https://console.anthropic.com")
    print("2. Set it using:")
    print('   export ANTHROPIC_API_KEY="your-key-here"')
    print()
    
    return False

def test_installation():
    """Quick test to verify installation."""
    print("\n🧪 Testing Installation")
    print("-" * 40)
    
    try:
        import cogzia_alpha_v1_5
        print("✓ Package imported successfully")
        
        # Test that main entry point exists
        from cogzia_alpha_v1_5 import cli_main
        print("✓ CLI entry point found")
        
        return True
    except Exception as e:
        print(f"✗ Import test failed: {e}")
        return False

def print_next_steps():
    """Print getting started instructions."""
    print("\n🚀 Getting Started")
    print("-" * 40)
    print("\nQuick commands:")
    print("  cogzia --help          # Show all options")
    print("  cogzia --demo          # Run in demo mode (no API key needed)")
    print("  cogzia --auto          # Create an AI app automatically")
    print("  cogzia --login         # Login to save apps to cloud")
    print()
    print("Documentation: https://app.cogzia.com/docs")
    print("Support: https://github.com/cogzia/agent_builder/issues")

def main():
    """Main post-install setup."""
    print("\n" + "="*60)
    print("🎉 Cogzia Alpha v1.5 Installed Successfully!")
    print("="*60)
    
    # Test installation
    if not test_installation():
        print("\n⚠️  Installation may be incomplete")
        print("Try reinstalling: pip install --force-reinstall cogzia")
        return
    
    # Check API key
    api_key_ok = setup_api_key()
    
    # Print next steps
    print_next_steps()
    
    if not api_key_ok:
        print("\n⚠️  Remember to set your ANTHROPIC_API_KEY before using Cogzia!")
    else:
        print("\n✅ You're all set! Run 'cogzia' to get started.")

if __name__ == "__main__":
    main()