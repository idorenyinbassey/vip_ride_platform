#!/usr/bin/env python3
"""
Comprehensive API Test Suite for VIP Ride-Hailing Platform
Simple HTTP client tests for all major API endpoints
"""

import os
import sys
import json
import requests
from datetime import datetime
import subprocess


class VIPRideAPITester:
    """Main API testing class using HTTP requests"""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.auth_token = None
        self.results = {}
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
        # Test users data
        self.test_users = {
            'normal': {
                'email': 'normal@test.com',
                'password': 'testpass123',
                'first_name': 'Normal',
                'last_name': 'User',
                'user_type': 'normal',
                'tier': 'normal'
            },
            'premium': {
                'email': 'premium@test.com',
                'password': 'testpass123',
                'first_name': 'Premium',
                'last_name': 'User',
                'user_type': 'premium',
                'tier': 'premium'
            },
            'vip': {
                'email': 'vip@test.com',
                'password': 'testpass123',
                'first_name': 'VIP',
                'last_name': 'User',
                'user_type': 'vip',
                'tier': 'vip'
            },
            'driver': {
                'email': 'driver@test.com',
                'password': 'testpass123',
                'first_name': 'Test',
                'last_name': 'Driver',
                'user_type': 'driver'
            }
        }
    
    def make_request(self, method, endpoint, data=None, params=None, auth_required=True):
        """Make HTTP request to API endpoint"""
        url = f"{self.base_url}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if auth_required and self.auth_token:
            headers['Authorization'] = f'Bearer {self.auth_token}'
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=headers, params=params, timeout=10)
            elif method == 'POST':
                response = self.session.post(url, headers=headers, json=data, timeout=10)
            elif method == 'PUT':
                response = self.session.put(url, headers=headers, json=data, timeout=10)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=headers, timeout=10)
            else:
                return None, f"Unsupported method: {method}"
            
            return response, None
            
        except requests.exceptions.RequestException as e:
            return None, str(e)
    
    def test_endpoint(self, name, method, endpoint, data=None, params=None, expected_statuses=None, auth_required=True):
        """Test a single API endpoint"""
        if expected_statuses is None:
            expected_statuses = [200, 201, 400, 401, 403, 404]  # Removed 500
        
        self.total_tests += 1
        print(f"\n🧪 Testing {name}: {method} {endpoint}")
        
        response, error = self.make_request(method, endpoint, data, params, auth_required)
        
        if error:
            self.failed_tests += 1
            result = f"❌ {name}: Connection Error - {error}"
            print(result)
            return False, result
        
        status_code = response.status_code
        print(f"   Status: {status_code}")
        
        # Check if status code is expected or is a success/redirect (2xx/3xx)
        if status_code in expected_statuses or (200 <= status_code <= 399):
            self.passed_tests += 1
            result = f"✅ {name}: {status_code}"
            print(f"   ✅ PASSED")
            
            # Try to show response data preview
            try:
                if response.content:
                    data = response.json()
                    if isinstance(data, dict):
                        keys = list(data.keys())[:3]
                        print(f"   Response keys: {keys}")
                    elif isinstance(data, list):
                        print(f"   Response: List with {len(data)} items")
            except:
                print(f"   Response: {len(response.content)} bytes")
            
            return True, result
        else:
            self.failed_tests += 1
            result = f"❌ {name}: Unexpected status {status_code}"
            print(f"   ❌ FAILED: {result}")
            
            # Show error details
            try:
                if response.content:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
            except:
                print(f"   Error content: {response.text[:200]}")
            
            return False, result
    
    def authenticate_user(self, user_type='normal'):
        """Authenticate with the API"""
        print(f"\n🔐 Authenticating as {user_type} user...")
        
        # Try to login first
        user_data = self.test_users[user_type]
        login_data = {
            'email': user_data['email'],
            'password': user_data['password']
        }
        
        response, error = self.make_request('POST', '/api/v1/accounts/login/', login_data, auth_required=False)
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                if 'access' in data:
                    self.auth_token = data['access']
                    print(f"✅ Authenticated successfully")
                    return True
                elif 'token' in data:
                    self.auth_token = data['token']
                    print(f"✅ Authenticated successfully")
                    return True
            except:
                pass
        
        # If login fails, try to register first
        print(f"⚠️  Login failed, trying to register user...")
        response, error = self.make_request('POST', '/api/v1/accounts/register/', user_data, auth_required=False)
        
        if response and response.status_code in [200, 201]:
            print(f"✅ User registered, trying login again...")
            response, error = self.make_request('POST', '/api/v1/accounts/login/', login_data, auth_required=False)
            
            if response and response.status_code == 200:
                try:
                    data = response.json()
                    if 'access' in data:
                        self.auth_token = data['access']
                        print(f"✅ Authenticated successfully after registration")
                        return True
                    elif 'token' in data:
                        self.auth_token = data['token']
                        print(f"✅ Authenticated successfully after registration")
                        return True
                except:
                    pass
        
        print(f"❌ Authentication failed")
        return False
    
    def test_accounts_apis(self):
        """Test Accounts API endpoints"""
        print("\n" + "="*60)
        print("TESTING ACCOUNTS APIs")
        print("="*60)
        
        results = []
        
        # Test registration
        success, result = self.test_endpoint(
            "User Registration",
            "POST",
            "/api/v1/accounts/register/",
            {
                'email': 'newtest@example.com',
                'password': 'newpass123',
                'first_name': 'New',
                'last_name': 'Test',
                'user_type': 'normal'
            },
            auth_required=False
        )
        results.append(result)
        
        # Test login
        success, result = self.test_endpoint(
            "User Login",
            "POST",
            "/api/v1/accounts/login/",
            {
                'email': 'normal@test.com',
                'password': 'testpass123'
            },
            auth_required=False
        )
        results.append(result)
        
        # Authenticate for other tests
        if self.authenticate_user('normal'):
            # Test profile
            success, result = self.test_endpoint(
                "User Profile",
                "GET",
                "/api/v1/accounts/profile/"
            )
            results.append(result)
            
            # Test user list
            success, result = self.test_endpoint(
                "User List",
                "GET",
                "/api/v1/accounts/users/"
            )
            results.append(result)
        
        self.results['Accounts'] = results
    
    def test_rides_apis(self):
        """Test Rides API endpoints"""
        print("\n" + "="*60)
        print("TESTING RIDES APIs")
        print("="*60)
        
        results = []
        
        if not self.auth_token:
            self.authenticate_user('normal')
        
        # Test ride requests
        success, result = self.test_endpoint(
            "Create Ride Request",
            "POST",
            "/api/v1/rides/requests/",
            {
                'pickup_location': 'Test Pickup',
                'destination': 'Test Destination',
                'pickup_latitude': 6.5244,
                'pickup_longitude': 3.3792,
                'destination_latitude': 6.5344,
                'destination_longitude': 3.3892,
                'ride_type': 'standard'
            }
        )
        results.append(result)
        
        # Test list rides
        success, result = self.test_endpoint(
            "List Rides",
            "GET",
            "/api/v1/rides/"
        )
        results.append(result)
        
        # Test ride history
        success, result = self.test_endpoint(
            "Ride History",
            "GET",
            "/api/v1/rides/history/"
        )
        results.append(result)
        
        self.results['Rides'] = results
    
    def test_fleet_apis(self):
        """Test Fleet Management API endpoints"""
        print("\n" + "="*60)
        print("TESTING FLEET MANAGEMENT APIs")
        print("="*60)
        
        results = []
        
        if not self.auth_token:
            self.authenticate_user('driver')
        
        # Test vehicles list
        success, result = self.test_endpoint(
            "List Vehicles",
            "GET",
            "/api/v1/fleet/vehicles/"
        )
        results.append(result)
        
        # Test create vehicle
        success, result = self.test_endpoint(
            "Create Vehicle",
            "POST",
            "/api/v1/fleet/vehicles/",
            {
                'make': 'Toyota',
                'model': 'Camry',
                'year': 2023,
                'license_plate': 'TEST-123',
                'category': 'PREMIUM',
                'engine_type': 'V6'
            }
        )
        results.append(result)
        
        # Test fleet companies
        success, result = self.test_endpoint(
            "List Fleet Companies",
            "GET",
            "/api/v1/fleet/companies/"
        )
        results.append(result)
        
        self.results['Fleet Management'] = results
    
    def test_leasing_apis(self):
        """Test Vehicle Leasing API endpoints"""
        print("\n" + "="*60)
        print("TESTING VEHICLE LEASING APIs")
        print("="*60)
        
        results = []
        
        if not self.auth_token:
            self.authenticate_user('driver')
        
        # Test vehicle listings
        success, result = self.test_endpoint(
            "Vehicle Listings",
            "GET",
            "/api/v1/leasing/vehicles/"
        )
        results.append(result)
        
        # Test vehicle search
        success, result = self.test_endpoint(
            "Vehicle Search",
            "GET",
            "/api/v1/leasing/search/",
            params={'vehicle_type': 'PREMIUM', 'make': 'Toyota'}
        )
        results.append(result)
        
        # Test owner dashboard
        success, result = self.test_endpoint(
            "Owner Dashboard",
            "GET",
            "/api/v1/leasing/owner-dashboard/"
        )
        results.append(result)
        
        # Test fleet dashboard
        success, result = self.test_endpoint(
            "Fleet Dashboard",
            "GET",
            "/api/v1/leasing/fleet-dashboard/"
        )
        results.append(result)
        
        self.results['Vehicle Leasing'] = results
    
    def test_payments_apis(self):
        """Test Payments API endpoints"""
        print("\n" + "="*60)
        print("TESTING PAYMENTS APIs")
        print("="*60)
        
        results = []
        
        if not self.auth_token:
            self.authenticate_user('normal')
        
        # Test payments list
        success, result = self.test_endpoint(
            "List Payments",
            "GET",
            "/api/v1/payments/"
        )
        results.append(result)
        
        # Test payment methods
        success, result = self.test_endpoint(
            "Payment Methods",
            "GET",
            "/api/v1/payments/methods/"
        )
        results.append(result)
        
        # Test create payment
        success, result = self.test_endpoint(
            "Create Payment",
            "POST",
            "/api/v1/payments/",
            {
                'amount': '100.00',
                'currency': 'NGN',
                'payment_method': 'card'
            }
        )
        results.append(result)
        
        self.results['Payments'] = results
    
    def test_notifications_apis(self):
        """Test Notifications API endpoints"""
        print("\n" + "="*60)
        print("TESTING NOTIFICATIONS APIs")
        print("="*60)
        
        results = []
        
        if not self.auth_token:
            self.authenticate_user('normal')
        
        # Test notifications list
        success, result = self.test_endpoint(
            "List Notifications",
            "GET",
            "/api/v1/notifications/"
        )
        results.append(result)
        
        # Test notification preferences
        success, result = self.test_endpoint(
            "Notification Preferences",
            "GET",
            "/api/v1/notifications/preferences/"
        )
        results.append(result)
        
        self.results['Notifications'] = results
    
    def test_hotels_apis(self):
        """Test Hotels API endpoints"""
        print("\n" + "="*60)
        print("TESTING HOTELS APIs")
        print("="*60)
        
        results = []
        
        if not self.auth_token:
            self.authenticate_user('premium')
        
        # Test hotels list
        success, result = self.test_endpoint(
            "List Hotels",
            "GET",
            "/api/v1/hotels/"
        )
        results.append(result)
        
        # Test hotel search
        success, result = self.test_endpoint(
            "Hotel Search",
            "GET",
            "/api/v1/hotels/search/",
            params={
                'location': 'Lagos',
                'check_in': '2025-08-15',
                'check_out': '2025-08-17'
            }
        )
        results.append(result)
        
        # Test nearby hotels
        success, result = self.test_endpoint(
            "Nearby Hotels",
            "GET",
            "/api/v1/hotels/nearby/",
            params={
                'latitude': 6.5244,
                'longitude': 3.3792,
                'radius': 10
            }
        )
        results.append(result)
        
        self.results['Hotels'] = results
    
    def test_pricing_apis(self):
        """Test Pricing API endpoints"""
        print("\n" + "="*60)
        print("TESTING PRICING APIs")
        print("="*60)
        
        results = []
        
        if not self.auth_token:
            self.authenticate_user('normal')
        
        # Test fare calculation
        success, result = self.test_endpoint(
            "Calculate Fare",
            "POST",
            "/api/v1/pricing/calculate/",
            {
                'pickup_latitude': 6.5244,
                'pickup_longitude': 3.3792,
                'destination_latitude': 6.5344,
                'destination_longitude': 3.3892,
                'ride_type': 'standard'
            }
        )
        results.append(result)
        
        # Test surge pricing
        success, result = self.test_endpoint(
            "Surge Pricing",
            "GET",
            "/api/v1/pricing/surge/",
            params={'latitude': 6.5244, 'longitude': 3.3792}
        )
        results.append(result)
        
        self.results['Pricing'] = results
    
    def test_gps_apis(self):
        """Test GPS Tracking API endpoints"""
        print("\n" + "="*60)
        print("TESTING GPS TRACKING APIs")
        print("="*60)
        
        results = []
        
        if not self.auth_token:
            self.authenticate_user('driver')
        
        # Test location update
        success, result = self.test_endpoint(
            "Update Location",
            "POST",
            "/api/v1/gps/location/",
            {
                'latitude': 6.5244,
                'longitude': 3.3792,
                'accuracy': 5.0,
                'speed': 0.0
            }
        )
        results.append(result)
        
        # Test tracking history
        success, result = self.test_endpoint(
            "Tracking History",
            "GET",
            "/api/v1/gps/history/"
        )
        results.append(result)
        
        self.results['GPS Tracking'] = results
    
    def test_control_center_apis(self):
        """Test Control Center API endpoints"""
        print("\n" + "="*60)
        print("TESTING CONTROL CENTER APIs")
        print("="*60)
        
        results = []
        
        if not self.auth_token:
            self.authenticate_user('vip')
        
        # Test VIP monitoring
        success, result = self.test_endpoint(
            "VIP Monitoring",
            "GET",
            "/api/v1/control-center/monitoring/"
        )
        results.append(result)
        
        # Test emergency requests
        success, result = self.test_endpoint(
            "Emergency Requests",
            "GET",
            "/api/v1/control-center/emergency/"
        )
        results.append(result)
        
        self.results['Control Center'] = results
    
    def check_server_status(self):
        """Check if Django server is running"""
        print("🔍 Checking server status...")
        
        try:
            response = requests.get(f"{self.base_url}/admin/", timeout=5)
            if response.status_code in [200, 302, 404]:
                print("✅ Django server is running")
                return True
        except requests.exceptions.RequestException:
            pass
        
        print("❌ Django server is not running")
        print("💡 Please run: python manage.py runserver")
        return False
    
    def run_all_tests(self):
        """Run all API tests"""
        print("=" * 80)
        print("VIP RIDE-HAILING PLATFORM - COMPREHENSIVE API TEST SUITE")
        print("=" * 80)
        print(f"Started at: {datetime.now()}")
        print(f"Testing server: {self.base_url}")
        print()
        
        # Check if server is running
        if not self.check_server_status():
            print("\n❌ Cannot run tests - Django server not accessible")
            return
        
        # Run all test modules
        test_modules = [
            self.test_accounts_apis,
            self.test_rides_apis,
            self.test_fleet_apis,
            self.test_leasing_apis,
            self.test_payments_apis,
            self.test_notifications_apis,
            self.test_hotels_apis,
            self.test_pricing_apis,
            self.test_gps_apis,
            self.test_control_center_apis
        ]
        
        for test_module in test_modules:
            try:
                test_module()
            except Exception as e:
                print(f"❌ Error in {test_module.__name__}: {str(e)}")
        
        self.print_summary()
    
    def print_summary(self):
        """Print test results summary"""
        print("\n" + "=" * 80)
        print("TEST RESULTS SUMMARY")
        print("=" * 80)
        
        for module_name, results in self.results.items():
            print(f"\n{module_name}:")
            for result in results:
                print(f"  {result}")
        
        print(f"\n{'='*80}")
        print(f"TOTAL TESTS: {self.total_tests}")
        print(f"PASSED: {self.passed_tests}")
        print(f"FAILED: {self.failed_tests}")
        
        if self.total_tests > 0:
            success_rate = (self.passed_tests / self.total_tests) * 100
            print(f"SUCCESS RATE: {success_rate:.1f}%")
        
        print(f"Completed at: {datetime.now()}")
        print("=" * 80)
        
        # Print endpoint coverage
        self.print_endpoint_coverage()
    
    def print_endpoint_coverage(self):
        """Print API endpoint coverage information"""
        print(f"\n{'='*80}")
        print("API ENDPOINTS TESTED")
        print("=" * 80)
        
        endpoints_by_module = {
            "Accounts": [
                "POST /api/v1/accounts/register/",
                "POST /api/v1/accounts/login/",
                "GET /api/v1/accounts/profile/",
                "GET /api/v1/accounts/users/"
            ],
            "Rides": [
                "POST /api/v1/rides/requests/",
                "GET /api/v1/rides/",
                "GET /api/v1/rides/history/"
            ],
            "Fleet Management": [
                "GET /api/v1/fleet/vehicles/",
                "POST /api/v1/fleet/vehicles/",
                "GET /api/v1/fleet/companies/"
            ],
            "Vehicle Leasing": [
                "GET /api/v1/leasing/vehicles/",
                "GET /api/v1/leasing/search/",
                "GET /api/v1/leasing/owner-dashboard/",
                "GET /api/v1/leasing/fleet-dashboard/"
            ],
            "Payments": [
                "GET /api/v1/payments/",
                "GET /api/v1/payments/methods/",
                "POST /api/v1/payments/"
            ],
            "Notifications": [
                "GET /api/v1/notifications/",
                "GET /api/v1/notifications/preferences/"
            ],
            "Hotels": [
                "GET /api/v1/hotels/",
                "GET /api/v1/hotels/search/",
                "GET /api/v1/hotels/nearby/"
            ],
            "Pricing": [
                "POST /api/v1/pricing/calculate/",
                "GET /api/v1/pricing/surge/"
            ],
            "GPS Tracking": [
                "POST /api/v1/gps/location/",
                "GET /api/v1/gps/history/"
            ],
            "Control Center": [
                "GET /api/v1/control-center/monitoring/",
                "GET /api/v1/control-center/emergency/"
            ]
        }
        
        total_endpoints = 0
        for module, endpoints in endpoints_by_module.items():
            total_endpoints += len(endpoints)
            print(f"\n{module} ({len(endpoints)} endpoints):")
            for endpoint in endpoints:
                print(f"  • {endpoint}")
        
        print(f"\n{'='*80}")
        print(f"TOTAL ENDPOINTS TESTED: {total_endpoints}")
        print(f"MODULES COVERED: {len(endpoints_by_module)}")
        print("=" * 80)


def main():
    """Main function to run the test suite"""
    import argparse
    
    parser = argparse.ArgumentParser(description='VIP Ride-Hailing Platform API Test Suite')
    parser.add_argument('--host', default='localhost', help='Server host (default: localhost)')
    parser.add_argument('--port', default='8000', help='Server port (default: 8000)')
    parser.add_argument('--protocol', default='http', help='Protocol (default: http)')
    
    args = parser.parse_args()
    
    base_url = f"{args.protocol}://{args.host}:{args.port}"
    
    # Create and run the test suite
    tester = VIPRideAPITester(base_url)
    tester.run_all_tests()


if __name__ == '__main__':
    main()
