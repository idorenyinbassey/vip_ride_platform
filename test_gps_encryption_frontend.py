#!/usr/bin/env python3
"""
Frontend GPS Encryption Testing Suite
Simulates mobile/web client interactions with GPS encryption APIs
"""

import requests
import json
import base64
import os
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List
import uuid

# Simulated ECDH implementation for client-side testing
try:
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives import serialization, hashes
    from cryptography.hazmat.primitives.kdf.hkdf import HKDF
    from cryptography.hazmat.backends import default_backend
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("⚠️  Cryptography library not available for full ECDH testing")


class ClientECDHSimulator:
    """Simulates client-side ECDH key exchange"""
    
    def __init__(self):
        if CRYPTO_AVAILABLE:
            self.private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
            self.public_key = self.private_key.public_key()
        else:
            # Mock implementation
            self.private_key = "mock_private_key"
            self.public_key = "mock_public_key"
    
    def get_public_key_base64(self) -> str:
        """Get public key as base64 string for transmission"""
        if CRYPTO_AVAILABLE:
            public_bytes = self.public_key.public_bytes(
                encoding=serialization.Encoding.X962,
                format=serialization.PublicFormat.UncompressedPoint
            )
            return base64.b64encode(public_bytes).decode('utf-8')
        else:
            # Mock base64 encoded public key (65 bytes for ECDH P-256 uncompressed point)
            return base64.b64encode(b'A' * 65).decode('utf-8')
    
    def derive_shared_key(self, server_public_key_b64: str) -> Optional[bytes]:
        """Derive shared key from server's public key"""
        if not CRYPTO_AVAILABLE:
            return os.urandom(32)  # Mock shared key
            
        try:
            server_public_bytes = base64.b64decode(server_public_key_b64)
            server_public_key = ec.EllipticCurvePublicKey.from_encoded_point(
                ec.SECP256R1(), server_public_bytes
            )
            
            shared_key = self.private_key.exchange(ec.ECDH(), server_public_key)
            
            # Derive AES-256 key using HKDF
            derived_key = HKDF(
                algorithm=hashes.SHA256(),
                length=32,
                salt=None,
                info=b'VIP_GPS_ENCRYPTION',
                backend=default_backend()
            ).derive(shared_key)
            
            return derived_key
        except Exception as e:
            print(f"❌ ECDH key derivation failed: {e}")
            return None


class GPSEncryptionFrontendTester:
    """Frontend testing class for GPS encryption APIs"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8001"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.jwt_token = None
        self.user_tier = None
        
        # Test ride IDs (should match created test rides)
        self.test_ride_ids = {
            'vip@test.com': 'f8d8af0a-045a-4057-8375-5819c914bcc1',
            'vip_premium@test.com': '17ad0c40-c478-49f2-b7b0-09ee18a0453b',
            'normal@test.com': 'f25a9c53-aa8c-4481-99da-6ceb14e7883e'
        }
        
        # Test coordinates (Lagos, Nigeria area)
        self.test_route = [
            {"lat": 6.5244, "lng": 3.3792, "name": "Victoria Island"},
            {"lat": 6.5270, "lng": 3.3820, "name": "Ikoyi"},
            {"lat": 6.5180, "lng": 3.3890, "name": "Lagos Island"},
            {"lat": 6.5320, "lng": 3.3650, "name": "Yaba"},
            {"lat": 6.5420, "lng": 3.3580, "name": "Surulere"}
        ]
    
    def authenticate(self, email: str, password: str) -> bool:
        """Authenticate user and get JWT token"""
        print(f"🔐 Authenticating user: {email}")
        
        auth_data = {
            "email": email,
            "password": password
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/auth/login/",
                json=auth_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.jwt_token = data.get('access')
                self.user_tier = data.get('user', {}).get('tier')
                
                # Set authorization header for future requests
                self.session.headers.update({
                    'Authorization': f'Bearer {self.jwt_token}'
                })
                
                print(f"✅ Authentication successful - User tier: {self.user_tier}")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def test_key_exchange(self, ride_id: str) -> Optional[Dict[str, Any]]:
        """Test GPS encryption key exchange"""
        print(f"🔑 Testing GPS key exchange for ride: {ride_id}")
        
        # Create client ECDH
        client_ecdh = ClientECDHSimulator()
        
        key_exchange_data = {
            "ride_id": ride_id,
            "client_public_key": client_ecdh.get_public_key_base64(),
            "encryption_level": "VIP" if self.user_tier in ["vip", "vip_premium"] else "STANDARD"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/gps/key-exchange/",
                json=key_exchange_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                session_id = data.get('session_id')
                server_public_key = data.get('server_public_key')
                expires_at = data.get('expires_at')
                
                print(f"✅ Key exchange successful:")
                print(f"   Session ID: {session_id}")
                print(f"   Expires at: {expires_at}")
                
                # Derive shared key (in real app, this would be used for client-side encryption)
                shared_key = client_ecdh.derive_shared_key(server_public_key)
                if shared_key:
                    print(f"   Shared key derived: {len(shared_key)} bytes")
                
                return {
                    'session_id': session_id,
                    'server_public_key': server_public_key,
                    'shared_key': shared_key,
                    'expires_at': expires_at
                }
            else:
                print(f"❌ Key exchange failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Key exchange error: {e}")
            return None
    
    def test_gps_encryption(self, session_data: Dict[str, Any], coordinates: Dict[str, float]) -> Optional[Dict[str, Any]]:
        """Test GPS coordinate encryption"""
        print(f"📍 Testing GPS encryption for coordinates: ({coordinates['lat']}, {coordinates['lng']})")
        
        encryption_data = {
            "session_id": session_data['session_id'],
            "coordinates": {
                "latitude": coordinates['lat'],
                "longitude": coordinates['lng'],
                "altitude": coordinates.get('altitude', 10.0),
                "accuracy": coordinates.get('accuracy', 5.0),
                "speed": coordinates.get('speed', 0.0),
                "bearing": coordinates.get('bearing', 0.0),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/gps/encrypt/",
                json=encryption_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ GPS encryption successful:")
                print(f"   Encrypted data length: {len(data.get('encrypted_data', ''))}")
                print(f"   Nonce length: {len(data.get('nonce', ''))}")
                
                return data
            else:
                print(f"❌ GPS encryption failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ GPS encryption error: {e}")
            return None
    
    def test_gps_decryption(self, encrypted_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Test GPS coordinate decryption"""
        print("🔓 Testing GPS decryption...")
        
        decryption_data = {
            "session_id": encrypted_data['session_id'],
            "encrypted_data": encrypted_data['encrypted_data'],
            "nonce": encrypted_data['nonce'],
            "timestamp": encrypted_data['timestamp']
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/gps/decrypt/",
                json=decryption_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                coordinates = data.get('coordinates', {})
                print(f"✅ GPS decryption successful:")
                print(f"   Latitude: {coordinates.get('latitude')}")
                print(f"   Longitude: {coordinates.get('longitude')}")
                
                return data
            else:
                print(f"❌ GPS decryption failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ GPS decryption error: {e}")
            return None
    
    def test_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Test session status endpoint"""
        print(f"📊 Testing session status for: {session_id}")
        
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/gps/session/{session_id}/status/"
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Session status retrieved:")
                print(f"   Status: {data.get('status')}")
                print(f"   Encryption count: {data.get('encryption_count')}")
                print(f"   Age (minutes): {data.get('age_minutes')}")
                
                return data
            else:
                print(f"❌ Session status failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Session status error: {e}")
            return None
    
    def test_complete_ride_simulation(self, user_credentials: Dict[str, str]) -> bool:
        """Test complete ride simulation with GPS encryption"""
        print("🚗 Starting Complete Ride Simulation with GPS Encryption")
        print("=" * 60)
        
        # Step 1: Authenticate
        if not self.authenticate(user_credentials['email'], user_credentials['password']):
            return False
        
        # Check if user has VIP access
        if self.user_tier not in ['vip', 'vip_premium']:
            print(f"⚠️  User tier '{self.user_tier}' does not have VIP GPS encryption access")
            print("   Testing with standard encryption level...")
        
        # Step 2: Start ride and establish encryption session
        user_email = user_credentials['email']
        ride_id = self.test_ride_ids.get(user_email)
        if not ride_id:
            print(f"❌ No test ride found for user {user_email}")
            return False
            
        print(f"\n🚗 Starting ride: {ride_id}")
        
        session_data = self.test_key_exchange(ride_id)
        if not session_data:
            print("❌ Ride simulation failed - could not establish encryption session")
            return False
        
        # Step 3: Simulate GPS tracking during ride
        print(f"\n📱 Simulating GPS tracking with {len(self.test_route)} points...")
        
        encrypted_points = []
        tracking_successful = True
        
        for i, point in enumerate(self.test_route):
            print(f"\n📍 Point {i+1}/{len(self.test_route)}: {point['name']}")
            
            # Add some variation to simulate real movement
            coordinates = {
                'lat': point['lat'] + (i * 0.001),  # Slight movement
                'lng': point['lng'] + (i * 0.001),
                'speed': 25.0 + (i * 5.0),  # Varying speed
                'bearing': 90.0 + (i * 15.0) % 360,  # Changing direction
                'altitude': 10.0 + i,
                'accuracy': 5.0
            }
            
            # Encrypt GPS point
            encrypted_data = self.test_gps_encryption(session_data, coordinates)
            if encrypted_data:
                encrypted_points.append({
                    'original': coordinates,
                    'encrypted': encrypted_data
                })
            else:
                tracking_successful = False
                break
            
            # Simulate time between GPS updates
            time.sleep(0.5)
        
        if not tracking_successful:
            print("❌ Ride simulation failed during GPS tracking")
            return False
        
        # Step 4: Verify encryption by decrypting some points
        print(f"\n🔓 Verifying encryption by decrypting {min(3, len(encrypted_points))} points...")
        
        verification_successful = True
        for i, point_data in enumerate(encrypted_points[:3]):
            print(f"\n   Verifying point {i+1}...")
            
            decrypted_data = self.test_gps_decryption(point_data['encrypted'])
            if decrypted_data:
                # Compare original vs decrypted
                original = point_data['original']
                decrypted = decrypted_data['coordinates']
                
                lat_diff = abs(original['lat'] - decrypted['latitude'])
                lng_diff = abs(original['lng'] - decrypted['longitude'])
                
                if lat_diff < 0.000001 and lng_diff < 0.000001:
                    print(f"   ✅ Point {i+1} verification successful")
                else:
                    print(f"   ❌ Point {i+1} verification failed - coordinate mismatch")
                    verification_successful = False
            else:
                verification_successful = False
        
        # Step 5: Check session status
        print(f"\n📊 Checking final session status...")
        session_status = self.test_session_status(session_data['session_id'])
        
        # Step 6: Summary
        print(f"\n🏁 Ride Simulation Complete")
        print("=" * 40)
        print(f"User Tier: {self.user_tier}")
        print(f"GPS Points Encrypted: {len(encrypted_points)}")
        print(f"Encryption Successful: {'Yes' if tracking_successful else 'No'}")
        print(f"Verification Successful: {'Yes' if verification_successful else 'No'}")
        
        overall_success = tracking_successful and verification_successful
        print(f"Overall Success: {'Yes' if overall_success else 'No'}")
        
        return overall_success
    
    def test_unauthorized_access(self) -> bool:
        """Test that unauthorized users cannot access VIP encryption"""
        print("🚫 Testing Unauthorized Access Protection")
        print("-" * 40)
        
        # Clear any existing authentication
        self.session.headers.pop('Authorization', None)
        self.jwt_token = None
        
        ride_id = str(uuid.uuid4())
        client_ecdh = ClientECDHSimulator()
        
        # Try key exchange without authentication
        key_exchange_data = {
            "ride_id": ride_id,
            "client_public_key": client_ecdh.get_public_key_base64(),
            "encryption_level": "VIP"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/gps/key-exchange/",
                json=key_exchange_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code in [401, 403]:
                print("✅ Unauthorized access correctly blocked")
                return True
            else:
                print(f"❌ Security vulnerability - unauthorized access allowed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Test error: {e}")
            return False


def run_frontend_tests():
    """Run all frontend GPS encryption tests"""
    print("🧪 GPS Encryption Frontend Testing Suite")
    print("=" * 60)
    
    # Test configuration
    tester = GPSEncryptionFrontendTester()
    
    # Test scenarios
    test_users = [
        {
            'name': 'VIP User',
            'credentials': {'email': 'vip@test.com', 'password': 'testpass123'},
            'expected_tier': 'vip'
        },
        {
            'name': 'VIP Premium User',
            'credentials': {'email': 'vip_premium@test.com', 'password': 'testpass123'},
            'expected_tier': 'vip_premium'
        },
        {
            'name': 'Normal User',
            'credentials': {'email': 'normal@test.com', 'password': 'testpass123'},
            'expected_tier': 'normal'
        }
    ]
    
    results = []
    
    # Test unauthorized access first
    print("\n🔒 SECURITY TESTS")
    print("-" * 30)
    unauthorized_test = tester.test_unauthorized_access()
    results.append(('Unauthorized Access Protection', unauthorized_test))
    
    # Test each user type
    for user_info in test_users:
        print(f"\n👤 TESTING {user_info['name'].upper()}")
        print("-" * 40)
        
        try:
            success = tester.test_complete_ride_simulation(user_info['credentials'])
            results.append((f"{user_info['name']} Complete Simulation", success))
        except Exception as e:
            print(f"❌ {user_info['name']} test failed: {e}")
            results.append((f"{user_info['name']} Complete Simulation", False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 FRONTEND TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("🎉 All frontend tests passed!")
    else:
        print("⚠️  Some tests failed - check implementation")
    
    return passed == total


if __name__ == "__main__":
    try:
        run_frontend_tests()
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
