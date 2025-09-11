#!/usr/bin/env python3
"""
Simple GPS encryption endpoint test with detailed error reporting
"""

import os
import sys
import django
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vip_ride_platform.settings')
django.setup()

import requests
import json
import base64

def test_gps_endpoint_directly():
    """Test GPS encryption endpoint with detailed error reporting"""
    base_url = "http://127.0.0.1:8001"
    
    print("🔬 Direct GPS Endpoint Test")
    print("=" * 40)
    
    # Step 1: Authenticate VIP user
    print("1. Authenticating VIP user...")
    login_data = {
        "email": "vip@test.com",
        "password": "testpass123"
    }
    
    response = requests.post(f"{base_url}/api/v1/accounts/login/", json=login_data)
    print(f"   Login status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"   Login failed: {response.text}")
        return False
    
    # Get JWT token
    login_result = response.json()
    token = login_result.get('access')
    user_tier = login_result.get('user', {}).get('tier')
    print(f"   ✅ Authentication successful - Tier: {user_tier}")
    
    # Step 2: Test GPS key exchange endpoint
    print("2. Testing GPS key exchange...")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    key_exchange_data = {
        'ride_id': 'f8d8af0a-045a-4057-8375-5819c914bcc1',
        'client_public_key': base64.b64encode(b'A' * 65).decode('utf-8'),  # 65-byte mock key (typical ECDH P-256 uncompressed point)
        'encryption_level': 'VIP'
    }
    
    print(f"   Request data: {json.dumps(key_exchange_data, indent=2)}")
    
    response = requests.post(
        f"{base_url}/api/v1/gps/key-exchange/", 
        json=key_exchange_data,
        headers=headers
    )
    
    print(f"   Response status: {response.status_code}")
    print(f"   Response headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Success: {json.dumps(result, indent=2)}")
        return True
    else:
        print(f"   ❌ Error response: {response.text}")
        
        # Try to get more detailed error information
        if response.headers.get('content-type', '').startswith('application/json'):
            try:
                error_data = response.json()
                print(f"   Error details: {json.dumps(error_data, indent=2)}")
            except:
                pass
        
        return False

if __name__ == "__main__":
    test_gps_endpoint_directly()
