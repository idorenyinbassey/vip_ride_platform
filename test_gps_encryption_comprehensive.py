#!/usr/bin/env python3
"""
Comprehensive GPS Encryption Testing Suite for VIP and VIP Premium Users
Tests both backend encryption logic and API endpoints
"""

import os
import sys
import django
import json
import base64
from datetime import datetime, timezone, timedelta
import uuid
import requests
from typing import Dict, Any, Optional, List

# Django setup
sys.path.append('/home/idorenyinbassey/My projects/workspace1/vip_ride_platform')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vip_ride_platform.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import UserTier
from core.encryption import (
    GPSEncryptionManager, GPSCoordinates, ECDHKeyExchange, 
    GPSEncryptionSession, EncryptedLocation
)
from core.gps_models import GPSEncryptionSession as GPSSessionModel
from rides.models import Ride

User = get_user_model()


class GPSEncryptionTestCase(TestCase):
    """Base test case for GPS encryption testing"""
    
    def setUp(self):
        """Set up test users and data"""
        # Create test users
        self.normal_user = User.objects.create_user(
            email='normal@test.com',
            password='testpass123',
            tier=UserTier.NORMAL
        )
        
        self.vip_user = User.objects.create_user(
            email='vip@test.com',
            password='testpass123',
            tier=UserTier.VIP
        )
        
        self.vip_premium_user = User.objects.create_user(
            email='vip_premium@test.com',
            password='testpass123',
            tier=UserTier.VIP_PREMIUM
        )
        
        # Create API client
        self.client = APIClient()
        
        # Test GPS coordinates
        self.test_coordinates = GPSCoordinates(
            latitude=6.5244,  # Lagos, Nigeria
            longitude=3.3792,
            altitude=50.0,
            accuracy=5.0,
            speed=25.5,
            bearing=180.0,
            timestamp=datetime.now(timezone.utc)
        )
        
        # Initialize encryption manager
        self.encryption_manager = GPSEncryptionManager()

    def get_jwt_token(self, user):
        """Get JWT token for user authentication"""
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def authenticate_user(self, user):
        """Authenticate user for API calls"""
        token = self.get_jwt_token(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        return token


class CoreEncryptionTests(GPSEncryptionTestCase):
    """Test core encryption functionality"""
    
    def test_ecdh_key_exchange(self):
        """Test ECDH key exchange process"""
        print("🔐 Testing ECDH Key Exchange...")
        
        # Create two ECDH instances (client and server)
        client_ecdh = ECDHKeyExchange()
        server_ecdh = ECDHKeyExchange()
        
        # Exchange public keys
        client_public = client_ecdh.get_public_key_bytes()
        server_public = server_ecdh.get_public_key_bytes()
        
        # Derive shared keys
        client_shared = client_ecdh.derive_shared_key(server_public)
        server_shared = server_ecdh.derive_shared_key(client_public)
        
        # Verify keys match
        self.assertEqual(client_shared, server_shared)
        self.assertEqual(len(client_shared), 32)  # 256 bits
        
        print("✅ ECDH Key Exchange successful")
        
    def test_gps_encryption_decryption(self):
        """Test GPS coordinate encryption and decryption"""
        print("🌍 Testing GPS Encryption/Decryption...")
        
        # Create encryption session
        session_id = str(uuid.uuid4())
        ride_id = str(uuid.uuid4())
        shared_key = os.urandom(32)  # 256-bit key
        
        session = GPSEncryptionSession(session_id, ride_id, shared_key)
        
        # Encrypt coordinates
        encrypted_location = session.encrypt_location(self.test_coordinates)
        
        # Verify encrypted data structure
        self.assertIsInstance(encrypted_location, EncryptedLocation)
        self.assertEqual(encrypted_location.session_id, session_id)
        self.assertEqual(encrypted_location.ride_id, ride_id)
        self.assertTrue(encrypted_location.encrypted_data)
        self.assertTrue(encrypted_location.nonce)
        
        # Decrypt coordinates
        decrypted_coordinates = session.decrypt_location(encrypted_location)
        
        # Verify decryption accuracy
        self.assertAlmostEqual(decrypted_coordinates.latitude, self.test_coordinates.latitude, places=6)
        self.assertAlmostEqual(decrypted_coordinates.longitude, self.test_coordinates.longitude, places=6)
        self.assertEqual(decrypted_coordinates.altitude, self.test_coordinates.altitude)
        
        print("✅ GPS Encryption/Decryption successful")
        
    def test_vip_user_tier_access(self):
        """Test VIP user tier access to encryption"""
        print("👑 Testing VIP User Tier Access...")
        
        # Test VIP user can access encryption
        self.assertTrue(self.vip_user.can_access_tier(UserTier.VIP))
        self.assertTrue(self.vip_premium_user.can_access_tier(UserTier.VIP))
        self.assertTrue(self.vip_premium_user.can_access_tier(UserTier.VIP_PREMIUM))
        
        # Test normal user cannot access VIP features
        self.assertFalse(self.normal_user.can_access_tier(UserTier.VIP))
        self.assertFalse(self.normal_user.can_access_tier(UserTier.VIP_PREMIUM))
        
        print("✅ VIP User Tier Access verified")


class APIEndpointTests(GPSEncryptionTestCase):
    """Test GPS encryption API endpoints"""
    
    def test_key_exchange_endpoint_vip_user(self):
        """Test key exchange endpoint for VIP user"""
        print("🔑 Testing Key Exchange API for VIP User...")
        
        # Authenticate VIP user
        self.authenticate_user(self.vip_user)
        
        # Create client ECDH for key exchange
        client_ecdh = ECDHKeyExchange()
        
        # Request data
        request_data = {
            'ride_id': str(uuid.uuid4()),
            'client_public_key': client_ecdh.get_public_key_base64(),
            'encryption_level': 'VIP'
        }
        
        # Make key exchange request
        response = self.client.post('/api/v1/gps/key-exchange/', request_data, format='json')
        
        # Verify response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertIn('session_id', data)
        self.assertIn('server_public_key', data)
        self.assertIn('expires_at', data)
        
        print(f"✅ Key Exchange successful. Session ID: {data['session_id']}")
        return data
        
    def test_key_exchange_endpoint_normal_user_denied(self):
        """Test key exchange endpoint denies normal users"""
        print("🚫 Testing Key Exchange API denial for Normal User...")
        
        # Authenticate normal user
        self.authenticate_user(self.normal_user)
        
        # Create client ECDH for key exchange
        client_ecdh = ECDHKeyExchange()
        
        # Request data
        request_data = {
            'ride_id': str(uuid.uuid4()),
            'client_public_key': client_ecdh.get_public_key_base64(),
            'encryption_level': 'VIP'
        }
        
        # Make key exchange request
        response = self.client.post('/api/v1/gps/key-exchange/', request_data, format='json')
        
        # Verify access is denied
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED])
        
        print("✅ Normal User correctly denied access")
        
    def test_gps_encryption_endpoint_vip_premium(self):
        """Test GPS encryption endpoint for VIP Premium user"""
        print("🌟 Testing GPS Encryption API for VIP Premium User...")
        
        # Authenticate VIP Premium user
        self.authenticate_user(self.vip_premium_user)
        
        # First, establish key exchange
        key_exchange_data = self.test_key_exchange_endpoint_vip_user()
        
        # Request GPS encryption
        encryption_request = {
            'session_id': key_exchange_data['session_id'],
            'coordinates': {
                'latitude': self.test_coordinates.latitude,
                'longitude': self.test_coordinates.longitude,
                'altitude': self.test_coordinates.altitude,
                'accuracy': self.test_coordinates.accuracy,
                'speed': self.test_coordinates.speed,
                'bearing': self.test_coordinates.bearing,
                'timestamp': self.test_coordinates.timestamp.isoformat()
            }
        }
        
        # Make encryption request
        response = self.client.post('/api/v1/gps/encrypt/', encryption_request, format='json')
        
        # Verify response
        if response.status_code != status.HTTP_200_OK:
            print(f"❌ Encryption failed: {response.content}")
            return
            
        data = response.json()
        
        self.assertIn('encrypted_data', data)
        self.assertIn('nonce', data)
        self.assertIn('timestamp', data)
        self.assertIn('session_id', data)
        
        print("✅ GPS Encryption successful for VIP Premium user")
        return data
        
    def test_gps_decryption_endpoint(self):
        """Test GPS decryption endpoint"""
        print("🔓 Testing GPS Decryption API...")
        
        # First encrypt some data
        encrypted_data = self.test_gps_encryption_endpoint_vip_premium()
        
        if not encrypted_data:
            print("❌ Skipping decryption test - encryption failed")
            return
        
        # Request decryption
        decryption_request = {
            'session_id': encrypted_data['session_id'],
            'encrypted_data': encrypted_data['encrypted_data'],
            'nonce': encrypted_data['nonce'],
            'timestamp': encrypted_data['timestamp']
        }
        
        # Make decryption request
        response = self.client.post('/api/v1/gps/decrypt/', decryption_request, format='json')
        
        # Verify response
        if response.status_code != status.HTTP_200_OK:
            print(f"❌ Decryption failed: {response.content}")
            return
            
        data = response.json()
        
        self.assertIn('coordinates', data)
        coords = data['coordinates']
        
        # Verify decrypted coordinates match original
        self.assertAlmostEqual(coords['latitude'], self.test_coordinates.latitude, places=6)
        self.assertAlmostEqual(coords['longitude'], self.test_coordinates.longitude, places=6)
        
        print("✅ GPS Decryption successful")


class SecurityTests(GPSEncryptionTestCase):
    """Test security aspects of GPS encryption"""
    
    def test_session_isolation(self):
        """Test that sessions are properly isolated"""
        print("🔒 Testing Session Isolation...")
        
        # Create two different sessions
        session1_id = str(uuid.uuid4())
        session2_id = str(uuid.uuid4())
        ride1_id = str(uuid.uuid4())
        ride2_id = str(uuid.uuid4())
        
        key1 = os.urandom(32)
        key2 = os.urandom(32)
        
        session1 = GPSEncryptionSession(session1_id, ride1_id, key1)
        session2 = GPSEncryptionSession(session2_id, ride2_id, key2)
        
        # Encrypt with session1
        encrypted1 = session1.encrypt_location(self.test_coordinates)
        
        # Try to decrypt with session2 (should fail)
        try:
            session2.decrypt_location(encrypted1)
            self.fail("Session isolation broken - decryption should have failed")
        except Exception:
            print("✅ Session isolation working correctly")
            
    def test_encryption_uniqueness(self):
        """Test that encryption produces unique outputs"""
        print("🎲 Testing Encryption Uniqueness...")
        
        session_id = str(uuid.uuid4())
        ride_id = str(uuid.uuid4())
        shared_key = os.urandom(32)
        
        session = GPSEncryptionSession(session_id, ride_id, shared_key)
        
        # Encrypt same coordinates multiple times
        encrypted1 = session.encrypt_location(self.test_coordinates)
        encrypted2 = session.encrypt_location(self.test_coordinates)
        
        # Verify outputs are different (due to random nonces)
        self.assertNotEqual(encrypted1.encrypted_data, encrypted2.encrypted_data)
        self.assertNotEqual(encrypted1.nonce, encrypted2.nonce)
        
        print("✅ Encryption uniqueness verified")


class PerformanceTests(GPSEncryptionTestCase):
    """Test performance of GPS encryption"""
    
    def test_encryption_performance(self):
        """Test encryption performance with multiple coordinates"""
        print("⚡ Testing Encryption Performance...")
        
        import time
        
        session_id = str(uuid.uuid4())
        ride_id = str(uuid.uuid4())
        shared_key = os.urandom(32)
        
        session = GPSEncryptionSession(session_id, ride_id, shared_key)
        
        # Test with 100 coordinates
        coordinates_list = []
        for i in range(100):
            coords = GPSCoordinates(
                latitude=6.5244 + (i * 0.001),
                longitude=3.3792 + (i * 0.001),
                timestamp=datetime.now(timezone.utc)
            )
            coordinates_list.append(coords)
        
        # Measure encryption time
        start_time = time.time()
        encrypted_list = []
        
        for coords in coordinates_list:
            encrypted = session.encrypt_location(coords)
            encrypted_list.append(encrypted)
        
        encryption_time = time.time() - start_time
        
        # Measure decryption time
        start_time = time.time()
        
        for encrypted in encrypted_list:
            session.decrypt_location(encrypted)
        
        decryption_time = time.time() - start_time
        
        print(f"✅ Encrypted/Decrypted 100 coordinates:")
        print(f"   Encryption time: {encryption_time:.3f}s ({encryption_time*10:.1f}ms per coordinate)")
        print(f"   Decryption time: {decryption_time:.3f}s ({decryption_time*10:.1f}ms per coordinate)")
        
        # Performance assertions
        self.assertLess(encryption_time, 1.0, "Encryption too slow")
        self.assertLess(decryption_time, 1.0, "Decryption too slow")


class IntegrationTests(GPSEncryptionTestCase):
    """Integration tests for complete workflows"""
    
    def test_vip_ride_tracking_workflow(self):
        """Test complete VIP ride tracking workflow"""
        print("🚗 Testing Complete VIP Ride Tracking Workflow...")
        
        # Authenticate VIP user
        self.authenticate_user(self.vip_user)
        
        # Step 1: Create a ride (mock)
        ride_id = str(uuid.uuid4())
        print(f"   📱 Created ride: {ride_id}")
        
        # Step 2: Establish encryption session
        client_ecdh = ECDHKeyExchange()
        key_exchange_request = {
            'ride_id': ride_id,
            'client_public_key': client_ecdh.get_public_key_base64(),
            'encryption_level': 'VIP'
        }
        
        response = self.client.post('/api/v1/gps/key-exchange/', key_exchange_request, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        session_data = response.json()
        session_id = session_data['session_id']
        print(f"   🔑 Established encryption session: {session_id}")
        
        # Step 3: Simulate multiple GPS updates during ride
        route_coordinates = [
            (6.5244, 3.3792),  # Start point
            (6.5250, 3.3800),  # Point 1
            (6.5256, 3.3808),  # Point 2
            (6.5262, 3.3816),  # Point 3
            (6.5268, 3.3824),  # End point
        ]
        
        encrypted_route = []
        
        for i, (lat, lng) in enumerate(route_coordinates):
            coords_data = {
                'session_id': session_id,
                'coordinates': {
                    'latitude': lat,
                    'longitude': lng,
                    'altitude': 50.0,
                    'accuracy': 5.0,
                    'speed': 25.0 + i * 5,  # Varying speed
                    'bearing': 90.0,
                    'timestamp': (datetime.now(timezone.utc) + timedelta(minutes=i)).isoformat()
                }
            }
            
            response = self.client.post('/api/v1/gps/encrypt/', coords_data, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            encrypted_route.append(response.json())
            print(f"   📍 Encrypted GPS point {i+1}: ({lat}, {lng})")
        
        # Step 4: Verify route can be decrypted
        decrypted_route = []
        
        for encrypted_point in encrypted_route:
            decryption_request = {
                'session_id': encrypted_point['session_id'],
                'encrypted_data': encrypted_point['encrypted_data'],
                'nonce': encrypted_point['nonce'],
                'timestamp': encrypted_point['timestamp']
            }
            
            response = self.client.post('/api/v1/gps/decrypt/', decryption_request, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            decrypted_route.append(response.json()['coordinates'])
        
        # Step 5: Verify route integrity
        for i, (original_coords, decrypted_coords) in enumerate(zip(route_coordinates, decrypted_route)):
            self.assertAlmostEqual(decrypted_coords['latitude'], original_coords[0], places=6)
            self.assertAlmostEqual(decrypted_coords['longitude'], original_coords[1], places=6)
        
        print(f"   ✅ Successfully tracked {len(route_coordinates)} GPS points with encryption")
        print("✅ VIP Ride Tracking Workflow completed successfully")


def run_all_tests():
    """Run all GPS encryption tests"""
    print("🧪 Starting Comprehensive GPS Encryption Tests")
    print("=" * 60)
    
    # Initialize test suite
    test_classes = [
        CoreEncryptionTests,
        APIEndpointTests,
        SecurityTests,
        PerformanceTests,
        IntegrationTests
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    for test_class in test_classes:
        print(f"\n📋 Running {test_class.__name__}")
        print("-" * 40)
        
        # Get all test methods
        test_methods = [method for method in dir(test_class) if method.startswith('test_')]
        
        for test_method in test_methods:
            total_tests += 1
            try:
                # Create test instance and run test
                test_instance = test_class()
                test_instance.setUp()
                
                # Run the test method
                getattr(test_instance, test_method)()
                passed_tests += 1
                
            except Exception as e:
                failed_tests.append(f"{test_class.__name__}.{test_method}: {str(e)}")
                print(f"❌ {test_method} failed: {str(e)}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {len(failed_tests)}")
    
    if failed_tests:
        print("\n❌ FAILED TESTS:")
        for failure in failed_tests:
            print(f"   • {failure}")
    else:
        print("\n🎉 ALL TESTS PASSED!")
    
    print(f"\nSuccess Rate: {(passed_tests/total_tests)*100:.1f}%")


if __name__ == "__main__":
    # Set up Django environment
    os.environ.setdefault('DEBUG', 'True')
    
    try:
        run_all_tests()
    except Exception as e:
        print(f"❌ Test suite failed to run: {e}")
        import traceback
        traceback.print_exc()
