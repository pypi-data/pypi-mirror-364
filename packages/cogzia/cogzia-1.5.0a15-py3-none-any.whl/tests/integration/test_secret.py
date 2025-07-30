#!/usr/bin/env python3
"""Test script to verify Google Secret Manager access."""

import os
import sys

# Unset API key to test Secret Manager
os.environ.pop('ANTHROPIC_API_KEY', None)

# Set GCP project
os.environ['GCP_PROJECT_ID'] = 'cogzia-dev-main'

# Import and test
try:
    from semantic_matcher import SemanticToolMatcher
    
    print("Creating SemanticToolMatcher...")
    matcher = SemanticToolMatcher()
    print("✅ Success! API key was retrieved from Secret Manager")
    
except SystemExit as e:
    print("❌ Failed - the app exited")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()