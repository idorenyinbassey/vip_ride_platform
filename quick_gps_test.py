#!/usr/bin/env python3
"""
Quick GPS Encryption Test
"""

import requests
import json
import base64

# Test configuration
BASE_URL = "http://127.0.0.1:8001"

def test_authentication():
    """Test user authentication"""
    print("🔐 Testing authentication...")
    
    response = requests.post(f"{BASE_URL}/api/v1/accounts/login/", {
        "email": "vip@test.com",
        "password": "testpass123"
    })
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        token = response.json().get("access")
        print(f"✅ Authentication successful! Token: {token[:20]}...")
        return token
    else:
        print(f"❌ Authentication failed: {response.text}")
        return None

def test_gps_key_exchange(token):
    """Test GPS key exchange"""
    print("\n🔑 Testing GPS key exchange...")
    
    # Use a real SECP256R1 public key for testing
    mock_public_key = "BI/4nMckfi0ptgLHd+oFKJi8/NVh/JBtz49XCXLxhxBPHnrUiqHyV2azS0c5FJfxiTNLmx69Yz4suFkk3nxBN2M="
    
    response = requests.post(
        f"{BASE_URL}/api/v1/gps/key-exchange/",
        json={
            "ride_id": "f8d8af0a-045a-4057-8375-5819c914bcc1",
            "client_public_key": mock_public_key
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Key exchange successful!")
        print(f"   Session ID: {data.get('session_id')}")
        return data.get('session_id')
    else:
        print(f"❌ Key exchange failed: {response.text}")
        return None

def test_gps_encryption(token, session_id):
    """Test GPS data encryption"""
    print("\n🔐 Testing GPS encryption...")
    
    test_location = {
        "latitude": 6.5244,
        "longitude": 3.3792,
        "accuracy": 5.0,
        "timestamp": "2025-09-11T16:00:00Z",
        "speed": 45.5,
        "heading": 180.0
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/gps/encrypt/",
        json={
            "ride_id": "f8d8af0a-045a-4057-8375-5819c914bcc1",
            "session_id": session_id,
            "latitude": test_location["latitude"],
            "longitude": test_location["longitude"],
            "accuracy": test_location["accuracy"],
            "timestamp": test_location["timestamp"],
            "speed": test_location["speed"],
            "heading": test_location["heading"]
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ GPS encryption successful!")
        print(f"   Encrypted data length: {len(data.get('encrypted_data', ''))}")
        return True
    else:
        print(f"❌ GPS encryption failed: {response.text}")
        return False

def main():
    print("🧪 Quick GPS Encryption Test")
    print("=" * 40)
    
    # Test authentication
    token = test_authentication()
    if not token:
        return
    
    # Test key exchange
    session_id = test_gps_key_exchange(token)
    if not session_id:
        return
    
    # Test encryption
    success = test_gps_encryption(token, session_id)
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 All tests passed! GPS encryption is working!")
    else:
        print("❌ Tests failed. Check implementation.")

if __name__ == "__main__":
    main()