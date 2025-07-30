#!/usr/bin/env python3
"""Debug Google Secret Manager access."""

import os
import httpx
import google.auth
from google.auth.transport.requests import Request

# Get default credentials
try:
    credentials, project = google.auth.default()
    print(f"✅ Got credentials, project: {project}")
    
    # Refresh if needed
    if hasattr(credentials, 'expired') and credentials.expired and hasattr(credentials, 'refresh_token'):
        credentials.refresh(Request())
        print("✅ Refreshed credentials")
    
    # Get token
    if hasattr(credentials, 'token'):
        print(f"✅ Got token: {credentials.token[:20]}...")
    else:
        print("❌ No token attribute")
        # Try to get token another way
        auth_req = Request()
        credentials.refresh(auth_req)
        print(f"✅ After refresh, token: {getattr(credentials, 'token', 'NO TOKEN')[:20]}...")
    
    # Test Secret Manager API
    project_id = os.getenv('GCP_PROJECT_ID', 'cogzia-dev-main')
    secret_name = f"projects/{project_id}/secrets/anthropic-api-key/versions/latest"
    
    headers = {
        'Authorization': f'Bearer {credentials.token}',
        'Accept': 'application/json'
    }
    
    print(f"\n📍 Accessing secret: {secret_name}")
    response = httpx.get(
        f"https://secretmanager.googleapis.com/v1/{secret_name}:access",
        headers=headers,
        timeout=5.0
    )
    
    print(f"📍 Response status: {response.status_code}")
    if response.status_code == 200:
        import base64
        data = response.json()
        secret_data = data.get('payload', {}).get('data', '')
        if secret_data:
            api_key = base64.b64decode(secret_data).decode('utf-8')
            print(f"✅ Retrieved API key: {api_key[:10]}...")
        else:
            print("❌ No secret data in response")
    else:
        print(f"❌ Error response: {response.text}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()