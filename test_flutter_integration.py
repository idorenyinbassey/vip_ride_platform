#!/usr/bin/env python3
"""
Test Flutter Integration with Backend

This script tests that the Flutter frontend is properly integrated with the 
updated backend endpoints and can handle tier status changes and session management.
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
FLUTTER_ENDPOINTS = {
    'tier_status': '/api/v1/accounts/flutter/tier-status/',
    'activate_card': '/api/v1/accounts/flutter/activate-card/',
    'profile': '/api/v1/accounts/profile/',
    'login': '/api/v1/accounts/login/',
    'register': '/api/v1/accounts/register/',
}

class FlutterIntegrationTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        
    def login(self, email, password):
        """Login and get access token"""
        url = f"{BASE_URL}{FLUTTER_ENDPOINTS['login']}"
        data = {
            'email': email,
            'password': password,
            'device_name': 'Flutter Integration Test',
            'device_type': 'mobile',
            'device_os': 'ios'
        }
        
        response = self.session.post(url, json=data)
        if response.status_code == 200:
            result = response.json()
            self.access_token = result.get('access_token')
            self.user_id = result.get('user', {}).get('id')
            
            # Set authorization header
            self.session.headers.update({
                'Authorization': f'Bearer {self.access_token}'
            })
            
            print(f"✓ Login successful for user {self.user_id}")
            return True
        else:
            print(f"✗ Login failed: {response.status_code} - {response.text}")
            return False
    
    def test_tier_status_endpoint(self):
        """Test the Flutter tier status endpoint"""
        print("\n--- Testing Flutter Tier Status Endpoint ---")
        
        url = f"{BASE_URL}{FLUTTER_ENDPOINTS['tier_status']}"
        response = self.session.get(url)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Tier status endpoint working")
            print(f"  Current tier: {data.get('tier')}")
            print(f"  Tier display: {data.get('tier_display')}")
            print(f"  Premium cards: {len(data.get('premium_cards', []))}")
            print(f"  Device registered: {data.get('device_status', {}).get('is_registered')}")
            print(f"  Session active: {data.get('session_status', {}).get('is_active')}")
            return data
        else:
            print(f"✗ Tier status endpoint failed: {response.status_code} - {response.text}")
            return None
    
    def test_card_activation_endpoint(self):
        """Test the Flutter card activation endpoint with dummy data"""
        print("\n--- Testing Flutter Card Activation Endpoint ---")
        
        url = f"{BASE_URL}{FLUTTER_ENDPOINTS['activate_card']}"
        
        # Test with dummy card data (should fail validation but test endpoint structure)
        test_data = {
            'card_number': 'TEST1234567890123456',
            'verification_code': 'TEST123',
            'device_name': 'Flutter Integration Test'
        }
        
        response = self.session.post(url, json=test_data)
        
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.json()}")
        
        # We expect this to fail with validation error, but endpoint should be accessible
        if response.status_code in [400, 404]:  # Validation error or card not found
            print("✓ Card activation endpoint accessible (expected validation error)")
            return True
        elif response.status_code == 200:
            print("✓ Card activation endpoint working (unexpected success with test data)")
            return True
        else:
            print(f"✗ Card activation endpoint failed: {response.status_code}")
            return False
    
    def test_session_and_device_tracking(self):
        """Test if session and device info is being tracked"""
        print("\n--- Testing Session and Device Tracking ---")
        
        # Get tier status to check device/session info
        tier_data = self.test_tier_status_endpoint()
        
        if tier_data:
            device_status = tier_data.get('device_status', {})
            session_status = tier_data.get('session_status', {})
            
            print(f"Device ID: {device_status.get('device_id')}")
            print(f"Device registered: {device_status.get('is_registered')}")
            print(f"Session ID: {session_status.get('session_id')}")
            print(f"Session active: {session_status.get('is_active')}")
            
            if device_status.get('is_registered') and session_status.get('is_active'):
                print("✓ Session and device tracking working correctly")
                return True
            else:
                print("⚠ Session or device tracking may not be fully working")
                return False
        
        return False
    
    def test_profile_comparison(self):
        """Compare old profile endpoint vs new tier status endpoint"""
        print("\n--- Comparing Profile vs Tier Status Endpoints ---")
        
        # Test old profile endpoint
        profile_url = f"{BASE_URL}{FLUTTER_ENDPOINTS['profile']}"
        profile_response = self.session.get(profile_url)
        
        # Test new tier status endpoint
        tier_url = f"{BASE_URL}{FLUTTER_ENDPOINTS['tier_status']}"
        tier_response = self.session.get(tier_url)
        
        if profile_response.status_code == 200 and tier_response.status_code == 200:
            profile_data = profile_response.json()
            tier_data = tier_response.json()
            
            print("Old Profile Endpoint:")
            print(f"  Tier: {profile_data.get('tier')}")
            print(f"  Keys: {list(profile_data.keys())}")
            
            print("New Tier Status Endpoint:")
            print(f"  Tier: {tier_data.get('tier')}")
            print(f"  Keys: {list(tier_data.keys())}")
            
            # Check if new endpoint has more comprehensive data
            new_keys = set(tier_data.keys()) - set(profile_data.keys())
            if new_keys:
                print(f"✓ New endpoint provides additional data: {new_keys}")
            
            return True
        else:
            print("✗ Could not compare endpoints")
            return False
    
    def run_all_tests(self):
        """Run all integration tests"""
        print("=== Flutter Integration Test Suite ===")
        print(f"Testing against: {BASE_URL}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        
        results = {
            'tier_status': False,
            'card_activation': False,
            'session_tracking': False,
            'profile_comparison': False
        }
        
        # Run individual tests
        results['tier_status'] = self.test_tier_status_endpoint() is not None
        results['card_activation'] = self.test_card_activation_endpoint()
        results['session_tracking'] = self.test_session_and_device_tracking()
        results['profile_comparison'] = self.test_profile_comparison()
        
        # Summary
        print("\n=== Test Results Summary ===")
        passed = sum(results.values())
        total = len(results)
        
        for test_name, passed_test in results.items():
            status = "✓ PASS" if passed_test else "✗ FAIL"
            print(f"{test_name}: {status}")
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All Flutter integration tests passed!")
        else:
            print("⚠ Some tests failed - check Flutter frontend configuration")
        
        return results

def main():
    """Main test runner"""
    tester = FlutterIntegrationTester()
    
    # You'll need to provide valid login credentials
    print("Note: This test requires a valid user account")
    print("Make sure your Django server is running on localhost:8000")
    
    # Test with a demo user (update credentials as needed)
    email = input("Enter test user email (or press Enter for guest mode): ").strip()
    
    if email:
        password = input("Enter password: ").strip()
        
        if tester.login(email, password):
            tester.run_all_tests()
        else:
            print("Login failed - cannot run authenticated tests")
    else:
        print("Running unauthenticated endpoint tests...")
        # You could add tests for public endpoints here
        print("Note: Most tests require authentication")

if __name__ == "__main__":
    main()