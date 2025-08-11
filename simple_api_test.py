#!/usr/bin/env python3
"""
VIP Ride-Hailing Platform API Test Suite
Uses Django's built-in test framework - no external dependencies required
"""

import os
import sys
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vip_ride_platform.settings')

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    import django
    django.setup()
    
    from django.test import TestCase, Client
    from django.contrib.auth import get_user_model
    from django.urls import reverse, NoReverseMatch
    from django.core.management import execute_from_command_line
    import json
    
    User = get_user_model()
    print("✅ Django environment loaded successfully")
    
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    print("Make sure you're in the correct directory with manage.py")
    sys.exit(1)


class APITestRunner:
    """Simple API test runner using Django test client"""
    
    def __init__(self):
        self.client = Client()
        self.results = {}
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
        # Setup test users
        self.setup_test_data()
    
    def setup_test_data(self):
        """Create test users and data"""
        print("🔧 Setting up test data...")
        
        # Clean up existing test users
        User.objects.filter(email__contains='@test.com').delete()
        
        # Create test users
        try:
            self.normal_user = User.objects.create_user(
                username='normal_test',
                email='normal@test.com',
                password='testpass123',
                first_name='Normal',
                last_name='User'
            )
            print("   ✅ Created normal user")
            
            self.premium_user = User.objects.create_user(
                username='premium_test',
                email='premium@test.com',
                password='testpass123',
                first_name='Premium',
                last_name='User'
            )
            print("   ✅ Created premium user")
            
            self.driver_user = User.objects.create_user(
                username='driver_test',
                email='driver@test.com',
                password='testpass123',
                first_name='Driver',
                last_name='User'
            )
            print("   ✅ Created driver user")
            
        except Exception as e:
            print(f"   ⚠️  Error creating users: {e}")
    
    def test_endpoint(self, name, url, method='GET', data=None, user=None, expected_codes=None):
        """Test a single API endpoint"""
        if expected_codes is None:
            expected_codes = [200, 201]  # Only success codes by default
        
        self.total_tests += 1
        print(f"\n🧪 Testing {name}")
        print(f"   📍 {method} {url}")
        
        # Login user if provided
        if user:
            login_success = self.client.force_login(user)
            if login_success:
                print(f"   👤 Logged in as {user.username}")
            else:
                print(f"   ❌ Failed to login user {user.username}")
        
        try:
            # Make the request
            if method == 'GET':
                response = self.client.get(url, data or {})
            elif method == 'POST':
                if data:
                    response = self.client.post(url, 
                                             data=json.dumps(data), 
                                             content_type='application/json')
                else:
                    response = self.client.post(url)
            elif method == 'PUT':
                response = self.client.put(url, 
                                         data=json.dumps(data or {}), 
                                         content_type='application/json')
            elif method == 'DELETE':
                response = self.client.delete(url)
            else:
                print(f"   ❌ Unsupported method: {method}")
                self.failed_tests += 1
                return False
            
            status_code = response.status_code
            print(f"   📊 Status Code: {status_code}")
            
            # Check response
            if status_code in expected_codes:
                self.passed_tests += 1
                
                if 200 <= status_code <= 299:
                    print(f"   ✅ SUCCESS")
                else:
                    print(f"   ⚠️  Expected error (endpoint accessible)")
                
                # Show response preview for successful requests
                if 200 <= status_code <= 299:
                    try:
                        if response.content:
                            content = response.content.decode('utf-8')
                            if content.startswith('{') or content.startswith('['):
                                data = json.loads(content)
                                if isinstance(data, dict):
                                    keys = list(data.keys())[:3]
                                    print(f"   📝 Response keys: {keys}")
                                elif isinstance(data, list):
                                    print(f"   📝 Response: Array with {len(data)} items")
                            else:
                                print(f"   📝 Response: {len(content)} characters")
                    except Exception as e:
                        print(f"   📝 Response: {len(response.content)} bytes")
                
                return True
            else:
                self.failed_tests += 1
                print(f"   ❌ FAILED: Unexpected status {status_code}")
                
                # Show error content
                try:
                    if response.content:
                        content = response.content.decode('utf-8')[:200]
                        print(f"   🔍 Error: {content}")
                except:
                    pass
                
                return False
                
        except Exception as e:
            self.failed_tests += 1
            print(f"   ❌ FAILED: Exception - {str(e)}")
            return False
        
        finally:
            # Logout after each test
            self.client.logout()
    
    def test_core_urls(self):
        """Test core Django URLs"""
        print("\n" + "="*60)
        print("TESTING CORE DJANGO URLs")
        print("="*60)
        
        results = []
        
        # Test admin
        success = self.test_endpoint("Django Admin", "/admin/")
        results.append(f"{'✅' if success else '❌'} Django Admin")
        
        # Test static/media (if configured)
        success = self.test_endpoint("Static Files", "/static/", expected_codes=[200, 404])
        results.append(f"{'✅' if success else '❌'} Static Files")
        
        self.results['Core URLs'] = results
    
    def test_api_endpoints(self):
        """Test API endpoints"""
        print("\n" + "="*60)
        print("TESTING API ENDPOINTS")
        print("="*60)
        
        results = []
        
        # Test API root
        success = self.test_endpoint("API Root", "/api/")
        results.append(f"{'✅' if success else '❌'} API Root")
        
        success = self.test_endpoint("API v1", "/api/v1/")
        results.append(f"{'✅' if success else '❌'} API v1")
        
        self.results['API Endpoints'] = results
    
    def test_accounts_endpoints(self):
        """Test accounts endpoints"""
        print("\n" + "="*60)
        print("TESTING ACCOUNTS ENDPOINTS")
        print("="*60)
        
        results = []
        
        # Test accounts endpoints
        endpoints = [
            ("/api/v1/accounts/", "GET", None, None),
            ("/api/v1/accounts/users/", "GET", None, self.normal_user),
            ("/api/v1/accounts/profile/", "GET", None, self.normal_user),
            ("/api/v1/accounts/register/", "POST", {
                'username': 'newtest',
                'email': 'newtest@example.com',
                'password': 'newpass123',
                'first_name': 'New',
                'last_name': 'Test'
            }, None),
            ("/api/v1/accounts/login/", "POST", {
                'username': 'normal@test.com',
                'password': 'testpass123'
            }, None)
        ]
        
        for url, method, data, user in endpoints:
            endpoint_name = f"Accounts {url.split('/')[-2].title()}"
            success = self.test_endpoint(endpoint_name, url, method, data, user)
            results.append(f"{'✅' if success else '❌'} {endpoint_name}")
        
        self.results['Accounts'] = results
    
    def test_rides_endpoints(self):
        """Test rides endpoints"""
        print("\n" + "="*60)
        print("TESTING RIDES ENDPOINTS")
        print("="*60)
        
        results = []
        
        endpoints = [
            ("/api/v1/rides/", "GET", None, self.normal_user),
            ("/api/v1/rides/requests/", "GET", None, self.normal_user),
            ("/api/v1/rides/requests/", "POST", {
                'pickup_location': 'Test Pickup',
                'destination': 'Test Destination',
                'pickup_latitude': 6.5244,
                'pickup_longitude': 3.3792,
                'destination_latitude': 6.5344,
                'destination_longitude': 3.3892
            }, self.normal_user),
            ("/api/v1/rides/history/", "GET", None, self.normal_user)
        ]
        
        for url, method, data, user in endpoints:
            endpoint_name = f"Rides {url.split('/')[-2].title()}"
            success = self.test_endpoint(endpoint_name, url, method, data, user)
            results.append(f"{'✅' if success else '❌'} {endpoint_name}")
        
        self.results['Rides'] = results
    
    def test_fleet_endpoints(self):
        """Test fleet management endpoints"""
        print("\n" + "="*60)
        print("TESTING FLEET MANAGEMENT ENDPOINTS")
        print("="*60)
        
        results = []
        
        endpoints = [
            ("/api/v1/fleet/", "GET", None, self.driver_user),
            ("/api/v1/fleet/vehicles/", "GET", None, self.driver_user),
            ("/api/v1/fleet/companies/", "GET", None, self.driver_user),
            ("/api/v1/fleet/drivers/", "GET", None, self.driver_user)
        ]
        
        for url, method, data, user in endpoints:
            endpoint_name = f"Fleet {url.split('/')[-2].title()}"
            success = self.test_endpoint(endpoint_name, url, method, data, user)
            results.append(f"{'✅' if success else '❌'} {endpoint_name}")
        
        self.results['Fleet Management'] = results
    
    def test_leasing_endpoints(self):
        """Test vehicle leasing endpoints"""
        print("\n" + "="*60)
        print("TESTING VEHICLE LEASING ENDPOINTS")
        print("="*60)
        
        results = []
        
        endpoints = [
            ("/api/v1/leasing/", "GET", None, self.driver_user),
            ("/api/v1/leasing/vehicles/", "GET", None, self.driver_user),
            ("/api/v1/leasing/search/", "GET", None, self.driver_user),
            ("/api/v1/leasing/owner-dashboard/", "GET", None, self.driver_user),
            ("/api/v1/leasing/fleet-dashboard/", "GET", None, self.driver_user)
        ]
        
        for url, method, data, user in endpoints:
            endpoint_name = f"Leasing {url.split('/')[-2].title()}"
            success = self.test_endpoint(endpoint_name, url, method, data, user)
            results.append(f"{'✅' if success else '❌'} {endpoint_name}")
        
        self.results['Vehicle Leasing'] = results
    
    def test_payments_endpoints(self):
        """Test payments endpoints"""
        print("\n" + "="*60)
        print("TESTING PAYMENTS ENDPOINTS")
        print("="*60)
        
        results = []
        
        endpoints = [
            ("/api/v1/payments/", "GET", None, self.normal_user),
            ("/api/v1/payments/methods/", "GET", None, self.normal_user),
            ("/api/v1/payments/disputes/", "GET", None, self.normal_user)
        ]
        
        for url, method, data, user in endpoints:
            endpoint_name = f"Payments {url.split('/')[-2].title()}"
            success = self.test_endpoint(endpoint_name, url, method, data, user)
            results.append(f"{'✅' if success else '❌'} {endpoint_name}")
        
        self.results['Payments'] = results
    
    def test_hotels_endpoints(self):
        """Test hotels endpoints"""
        print("\n" + "="*60)
        print("TESTING HOTELS ENDPOINTS")
        print("="*60)
        
        results = []
        
        endpoints = [
            ("/api/v1/hotels/", "GET", None, self.premium_user),
            ("/api/v1/hotels/search/", "GET", None, self.premium_user),
            ("/api/v1/hotels/nearby/", "GET", None, self.premium_user)
        ]
        
        for url, method, data, user in endpoints:
            endpoint_name = f"Hotels {url.split('/')[-2].title()}"
            success = self.test_endpoint(endpoint_name, url, method, data, user)
            results.append(f"{'✅' if success else '❌'} {endpoint_name}")
        
        self.results['Hotels'] = results
    
    def test_notifications_endpoints(self):
        """Test notifications endpoints"""
        print("\n" + "="*60)
        print("TESTING NOTIFICATIONS ENDPOINTS")
        print("="*60)
        
        results = []
        
        endpoints = [
            ("/api/v1/notifications/", "GET", None, self.normal_user),
            ("/api/v1/notifications/preferences/", "GET", None, self.normal_user)
        ]
        
        for url, method, data, user in endpoints:
            endpoint_name = f"Notifications {url.split('/')[-2].title()}"
            success = self.test_endpoint(endpoint_name, url, method, data, user)
            results.append(f"{'✅' if success else '❌'} {endpoint_name}")
        
        self.results['Notifications'] = results
    
    def test_pricing_endpoints(self):
        """Test pricing endpoints"""
        print("\n" + "="*60)
        print("TESTING PRICING ENDPOINTS")
        print("="*60)
        
        results = []
        
        endpoints = [
            ("/api/v1/pricing/calculate/", "POST", {
                'pickup_latitude': 6.5244,
                'pickup_longitude': 3.3792,
                'destination_latitude': 6.5344,
                'destination_longitude': 3.3892,
                'ride_type': 'standard'
            }, self.normal_user),
            ("/api/v1/pricing/surge/", "GET", None, self.normal_user)
        ]
        
        for url, method, data, user in endpoints:
            endpoint_name = f"Pricing {url.split('/')[-2].title()}"
            success = self.test_endpoint(endpoint_name, url, method, data, user)
            results.append(f"{'✅' if success else '❌'} {endpoint_name}")
        
        self.results['Pricing'] = results
    
    def test_gps_endpoints(self):
        """Test GPS tracking endpoints"""
        print("\n" + "="*60)
        print("TESTING GPS TRACKING ENDPOINTS")
        print("="*60)
        
        results = []
        
        endpoints = [
            ("/api/v1/gps/location/", "POST", {
                'latitude': 6.5244,
                'longitude': 3.3792,
                'accuracy': 5.0
            }, self.driver_user),
            ("/api/v1/gps/history/", "GET", None, self.driver_user)
        ]
        
        for url, method, data, user in endpoints:
            endpoint_name = f"GPS {url.split('/')[-2].title()}"
            success = self.test_endpoint(endpoint_name, url, method, data, user)
            results.append(f"{'✅' if success else '❌'} {endpoint_name}")
        
        self.results['GPS Tracking'] = results
    
    def test_control_center_endpoints(self):
        """Test control center endpoints"""
        print("\n" + "="*60)
        print("TESTING CONTROL CENTER ENDPOINTS")
        print("="*60)
        
        results = []
        
        endpoints = [
            ("/api/v1/control-center/monitoring/", "GET", None, self.premium_user),
            ("/api/v1/control-center/emergency/", "GET", None, self.premium_user)
        ]
        
        for url, method, data, user in endpoints:
            endpoint_name = f"Control Center {url.split('/')[-2].title()}"
            success = self.test_endpoint(endpoint_name, url, method, data, user)
            results.append(f"{'✅' if success else '❌'} {endpoint_name}")
        
        self.results['Control Center'] = results
    
    def run_all_tests(self):
        """Run all API tests"""
        print("=" * 80)
        print("VIP RIDE-HAILING PLATFORM - COMPREHENSIVE API TEST SUITE")
        print("=" * 80)
        print(f"Started at: {datetime.now()}")
        print(f"Django Version: {django.get_version()}")
        print()
        
        # Run all test modules
        test_modules = [
            self.test_core_urls,
            self.test_api_endpoints,
            self.test_accounts_endpoints,
            self.test_rides_endpoints,
            self.test_fleet_endpoints,
            self.test_leasing_endpoints,
            self.test_payments_endpoints,
            self.test_hotels_endpoints,
            self.test_notifications_endpoints,
            self.test_pricing_endpoints,
            self.test_gps_endpoints,
            self.test_control_center_endpoints
        ]
        
        for test_module in test_modules:
            try:
                test_module()
            except Exception as e:
                print(f"❌ Error in {test_module.__name__}: {str(e)}")
        
        self.print_summary()
    
    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("COMPREHENSIVE TEST RESULTS SUMMARY")
        print("=" * 80)
        
        # Print results by module
        for module_name, results in self.results.items():
            print(f"\n{module_name}:")
            for result in results:
                print(f"  {result}")
        
        # Print overall statistics
        print(f"\n{'='*80}")
        print("OVERALL STATISTICS")
        print("="*80)
        print(f"Total Tests Run: {self.total_tests}")
        print(f"Tests Passed: {self.passed_tests}")
        print(f"Tests Failed: {self.failed_tests}")
        
        if self.total_tests > 0:
            success_rate = (self.passed_tests / self.total_tests) * 100
            print(f"Success Rate: {success_rate:.1f}%")
        
        print(f"\nCompleted at: {datetime.now()}")
        print("=" * 80)
        
        # Print endpoint coverage
        self.print_endpoint_coverage()
    
    def print_endpoint_coverage(self):
        """Print endpoint coverage information"""
        print(f"\n{'='*80}")
        print("API ENDPOINT COVERAGE REPORT")
        print("=" * 80)
        
        total_modules = len(self.results)
        total_endpoints_tested = self.total_tests
        
        print(f"Modules Tested: {total_modules}")
        print(f"Endpoints Tested: {total_endpoints_tested}")
        print(f"Framework: Django {django.get_version()}")
        
        print("\nEndpoint Categories:")
        for module_name, results in self.results.items():
            tested_count = len([r for r in results if '✅' in r])
            total_count = len(results)
            print(f"  • {module_name}: {tested_count}/{total_count} successful")
        
        print("=" * 80)


def main():
    """Main function to run the test suite"""
    print("🚀 Starting VIP Ride-Hailing Platform API Tests")
    print("Using Django's built-in test client (no external dependencies)")
    print()
    
    # Check if we can import Django properly
    try:
        from django.conf import settings
        print(f"✅ Django settings module: {settings.SETTINGS_MODULE}")
    except Exception as e:
        print(f"❌ Django configuration error: {e}")
        return
    
    # Create and run the test suite
    runner = APITestRunner()
    runner.run_all_tests()
    
    # Final recommendations
    print("\n" + "🔧 RECOMMENDATIONS:")
    if runner.failed_tests > 0:
        print("• Check failed endpoints - they might need URL pattern fixes")
        print("• Verify authentication requirements for protected endpoints")
        print("• Review API documentation for proper request formats")
    
    if runner.passed_tests > 0:
        print("• Working endpoints are ready for frontend integration")
        print("• Consider adding more detailed API tests for business logic")
    
    print("• Run 'python manage.py runserver' to test with live server")


if __name__ == '__main__':
    main()
