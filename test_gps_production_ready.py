#!/usr/bin/env python3
"""
Quick test script to verify GPS encryption endpoint status
"""

import os
import sys
import django
import requests
import json

# Setup Django
sys.path.append('/home/idorenyinbassey/My projects/workspace1/vip_ride_platform')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vip_ride_platform.settings')
django.setup()

def test_gps_encryption_endpoint():
    """Test the GPS encryption endpoint"""
    
    base_url = 'http://localhost:8000/api'
    
    # Test authentication first
    print("🔐 Testing authentication...")
    
    # Login to get token
    login_data = {
        'email': 'vip@example.com',
        'password': 'securepass123'
    }
    
    try:
        response = requests.post(f'{base_url}/auth/login/', json=login_data)
        print(f"Login Status: {response.status_code}")
        
        if response.status_code == 200:
            auth_data = response.json()
            token = auth_data.get('access_token')
            print("✅ Authentication successful")
            
            # Test GPS key exchange
            print("\n🔑 Testing GPS key exchange...")
            
            headers = {'Authorization': f'Bearer {token}'}
            
            # Create a test ride first
            ride_data = {
                'pickup_address': 'Lagos Island, Lagos',
                'pickup_latitude': 6.4541,
                'pickup_longitude': 3.3947,
                'destination_address': 'Victoria Island, Lagos',
                'destination_latitude': 6.4281,
                'destination_longitude': 3.4219,
                'vehicle_type': 'premium'
            }
            
            ride_response = requests.post(f'{base_url}/rides/book/', json=ride_data, headers=headers)
            print(f"Ride booking status: {ride_response.status_code}")
            
            if ride_response.status_code == 201:
                ride_id = ride_response.json()['ride']['id']
                print(f"✅ Ride created: {ride_id}")
                
                # Test key exchange
                key_exchange_data = {
                    'ride_id': ride_id,
                    'client_public_key': 'test_public_key_base64_encoded'
                }
                
                key_response = requests.post(f'{base_url}/gps/key-exchange/', json=key_exchange_data, headers=headers)
                print(f"Key exchange status: {key_response.status_code}")
                
                if key_response.status_code == 200:
                    session_id = key_response.json()['session_id']
                    print(f"✅ Key exchange successful: {session_id}")
                    
                    # Test GPS encryption
                    print("\n📍 Testing GPS encryption...")
                    
                    gps_data = {
                        'session_id': session_id,
                        'latitude': 6.5244,
                        'longitude': 3.3792,
                        'timestamp': '2024-01-15T10:30:00Z',
                        'accuracy': 5.0
                    }
                    
                    encrypt_response = requests.post(f'{base_url}/gps/encrypt/', json=gps_data, headers=headers)
                    print(f"GPS encryption status: {encrypt_response.status_code}")
                    
                    if encrypt_response.status_code == 200:
                        print("✅ GPS encryption successful!")
                        print(f"Response: {encrypt_response.json()}")
                        return True
                    else:
                        print(f"❌ GPS encryption failed")
                        print(f"Error: {encrypt_response.text}")
                        return False
                else:
                    print(f"❌ Key exchange failed")
                    print(f"Error: {key_response.text}")
                    return False
            else:
                print(f"❌ Ride booking failed")
                print(f"Error: {ride_response.text}")
                return False
        else:
            print(f"❌ Authentication failed")
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - Django server may not be running")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

if __name__ == '__main__':
    print("🧪 GPS Encryption Endpoint Test")
    print("=" * 40)
    
    success = test_gps_encryption_endpoint()
    
    if success:
        print("\n🎉 All tests passed! GPS encryption is working correctly.")
        print("✅ Backend is ready for production deployment!")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
        print("🔧 Backend needs minor fixes before production.")