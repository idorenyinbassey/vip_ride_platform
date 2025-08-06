# Tests fofrom django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch, MagicMock

from accounts.models import Driver, UserTier
from fleet_management.models import Vehicle, VehicleCategory, VehicleStatus
from rides.models import Ride, RideOffer, SurgeZone, RideMatchingLog, RideStatus
from rides.matching import RideMatchingService

User = get_user_model()


class RideMatchingSystemTestCase(TestCase):
"""
Comprehensive tests for the ride matching algorithm and API endpoints
"""

import json
from decimal import Decimal
from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch, MagicMock

from accounts.models import Driver, UserTier
from fleet_management.models import Vehicle, VehicleCategory
from rides.models import Ride, RideStatus, RideType
from rides.models import Ride, RideOffer, SurgeZone, RideMatchingLog
from rides.matching import RideMatchingService, RideMatchingController


class RideMatchingServiceTest(TestCase):
    """Test the core ride matching service"""
    
    def setUp(self):
        """Set up test data"""
        # Create test users
        self.customer = User.objects.create_user(
            username='customer1',
            email='customer@test.com',
            first_name='Test',
            last_name='Customer'
        )
        
        self.driver_user = User.objects.create_user(
            username='driver1',
            email='driver@test.com',
            first_name='Test',
            last_name='Driver'
        )
        
        # Create driver profile
        self.driver = Driver.objects.create(
            user=self.driver_user,
            license_number='DL123456',
            phone_number='+2348012345678',
            status=Driver.DriverStatus.ACTIVE,
            subscription_tier=Driver.SubscriptionTier.PREMIUM,
            is_online=True,
            is_available=True,
            current_location_lat=Decimal('6.5244'),
            current_location_lng=Decimal('3.3792'),
            average_rating=Decimal('4.5'),
            completion_rate=95.0
        )
        
        # Create vehicle
        self.vehicle = Vehicle.objects.create(
            owner=self.driver_user,
            make='Toyota',
            model='Camry',
            year=2020,
            color='Black',
            license_plate='ABC123',
            category=VehicleCategory.PREMIUM,
            status=Vehicle.VehicleStatus.ACTIVE,
            capacity=4
        )
        
        # Create test ride
        self.ride = Ride.objects.create(
            customer=self.customer,
            customer_tier=UserTier.PREMIUM,
            ride_type=RideType.NORMAL,
            pickup_address='Test Pickup',
            pickup_latitude=Decimal('6.5200'),
            pickup_longitude=Decimal('3.3800'),
            destination_address='Test Destination',
            destination_latitude=Decimal('6.5300'),
            destination_longitude=Decimal('3.3900'),
            status=RideStatus.PENDING
        )
        
        self.matching_service = RideMatchingService()
    
    def test_distance_calculation(self):
        """Test haversine distance calculation"""
        # Distance between two close points
        lat1, lng1 = 6.5244, 3.3792
        lat2, lng2 = 6.5200, 3.3800
        
        distance = self.matching_service.calculate_distance(lat1, lng1, lat2, lng2)
        
        # Should be approximately 0.8 km
        self.assertAlmostEqual(distance, 0.8, delta=0.2)
    
    def test_search_radius_by_tier(self):
        """Test search radius varies by customer tier"""
        # VIP should have larger radius
        vip_radius = self.matching_service.get_search_radius(
            UserTier.VIP, RideType.NORMAL
        )
        
        # Normal should have standard radius
        normal_radius = self.matching_service.get_search_radius(
            UserTier.NORMAL, RideType.NORMAL
        )
        
        self.assertGreater(vip_radius, normal_radius)
        self.assertEqual(vip_radius, 50.0)
        self.assertEqual(normal_radius, 20.0)
    
    def test_tier_match_scoring(self):
        """Test tier matching scores"""
        # VIP driver serving VIP customer should score highest
        vip_score = self.matching_service.calculate_tier_match_score(
            self.driver, UserTier.VIP
        )
        
        # Premium driver can serve VIP but with lower score
        self.driver.subscription_tier = Driver.SubscriptionTier.PREMIUM
        premium_score = self.matching_service.calculate_tier_match_score(
            self.driver, UserTier.VIP
        )
        
        # Basic driver cannot serve VIP
        self.driver.subscription_tier = Driver.SubscriptionTier.BASIC
        basic_score = self.matching_service.calculate_tier_match_score(
            self.driver, UserTier.VIP
        )
        
        self.assertGreater(premium_score, basic_score)
        self.assertEqual(basic_score, 0.0)
    
    def test_vehicle_match_scoring(self):
        """Test vehicle matching scores"""
        # Premium vehicle for VIP ride should score high
        self.vehicle.category = VehicleCategory.PREMIUM
        premium_score = self.matching_service.calculate_vehicle_match_score(
            self.vehicle, self.ride
        )
        
        # Standard vehicle for VIP ride should score lower
        self.vehicle.category = VehicleCategory.STANDARD
        standard_score = self.matching_service.calculate_vehicle_match_score(
            self.vehicle, self.ride
        )
        
        self.assertGreater(premium_score, standard_score)
    
    def test_availability_scoring(self):
        """Test driver availability scoring"""
        # Recent location update should score higher
        self.driver.last_location_update = timezone.now()
        recent_score = self.matching_service.calculate_availability_score(
            self.driver
        )
        
        # Old location update should score lower
        self.driver.last_location_update = timezone.now() - timedelta(hours=1)
        old_score = self.matching_service.calculate_availability_score(
            self.driver
        )
        
        self.assertGreater(recent_score, old_score)
    
    def test_surge_calculation(self):
        """Test surge pricing calculation"""
        # Test with no surge conditions
        surge = self.matching_service.calculate_surge_multiplier(
            float(self.ride.pickup_latitude),
            float(self.ride.pickup_longitude),
            self.ride.customer_tier
        )
        
        self.assertGreaterEqual(surge, Decimal('1.0'))
        
        # Test VIP surge limit
        with patch.object(
            self.matching_service, 'calculate_dynamic_surge',
            return_value=Decimal('3.0')
        ):
            vip_surge = self.matching_service.calculate_surge_multiplier(
                float(self.ride.pickup_latitude),
                float(self.ride.pickup_longitude),
                UserTier.VIP
            )
            
            # VIP surge should be capped at 2.0
            self.assertLessEqual(vip_surge, Decimal('2.0'))
    
    def test_driver_eligibility(self):
        """Test driver eligibility checks"""
        # Active, available driver should be eligible
        eligible = self.matching_service.can_driver_accept_ride(
            self.driver, UserTier.PREMIUM, RideType.NORMAL
        )
        
        self.assertTrue(eligible)
        
        # Offline driver should not be eligible
        self.driver.is_online = False
        not_eligible = self.matching_service.can_driver_accept_ride(
            self.driver, UserTier.PREMIUM, RideType.NORMAL
        )
        
        self.assertFalse(not_eligible)
    
    @patch('rides.matching.RideMatchingService.get_available_drivers')
    def test_find_best_drivers(self, mock_get_drivers):
        """Test finding best drivers"""
        # Mock available drivers
        mock_get_drivers.return_value = [{
            'driver': self.driver,
            'vehicle': self.vehicle,
            'distance_km': 2.5
        }]
        
        driver_scores = self.matching_service.find_best_drivers(self.ride)
        
        self.assertEqual(len(driver_scores), 1)
        self.assertEqual(driver_scores[0].driver, self.driver)
        self.assertGreater(driver_scores[0].score, 0)
    
    def test_estimated_arrival_calculation(self):
        """Test estimated arrival time calculation"""
        distance_km = 5.0
        surge_multiplier = Decimal('1.5')
        
        arrival_time = self.matching_service.calculate_estimated_arrival(
            distance_km, surge_multiplier
        )
        
        # Should be reasonable time (between 1-60 minutes)
        self.assertGreaterEqual(arrival_time, 1)
        self.assertLessEqual(arrival_time, 60)


class RideMatchingControllerTest(TestCase):
    """Test the ride matching controller"""
    
    def setUp(self):
        """Set up test data"""
        self.customer = User.objects.create_user(
            username='customer1',
            email='customer@test.com'
        )
        
        self.driver_user = User.objects.create_user(
            username='driver1',
            email='driver@test.com'
        )
        
        self.driver = Driver.objects.create(
            user=self.driver_user,
            license_number='DL123456',
            phone_number='+2348012345678',
            status=Driver.DriverStatus.ACTIVE,
            subscription_tier=Driver.SubscriptionTier.PREMIUM,
            is_online=True,
            is_available=True,
            current_location_lat=Decimal('6.5244'),
            current_location_lng=Decimal('3.3792')
        )
        
        self.ride = Ride.objects.create(
            customer=self.customer,
            customer_tier=UserTier.PREMIUM,
            ride_type=RideType.NORMAL,
            pickup_address='Test Pickup',
            pickup_latitude=Decimal('6.5200'),
            pickup_longitude=Decimal('3.3800'),
            destination_address='Test Destination',
            destination_latitude=Decimal('6.5300'),
            destination_longitude=Decimal('3.3900'),
            status=RideStatus.PENDING
        )
        
        self.controller = RideMatchingController()
    
    @patch('rides.matching.RideMatchingService.find_best_drivers')
    def test_process_ride_request_success(self, mock_find_drivers):
        """Test successful ride request processing"""
        from rides.matching import DriverScore
        
        # Mock successful driver finding
        mock_driver_score = DriverScore(
            driver=self.driver,
            vehicle=None,
            distance_km=2.5,
            estimated_arrival_minutes=8,
            surge_multiplier=Decimal('1.0'),
            score=0.85,
            match_reasons=['Distance: 2.5km', 'Tier match: 1.00']
        )
        mock_find_drivers.return_value = [mock_driver_score]
        
        result = self.controller.process_ride_request(self.ride)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['drivers_found'], 1)
        self.assertEqual(result['offers_created'], 1)
    
    @patch('rides.matching.RideMatchingService.find_best_drivers')
    def test_process_ride_request_no_drivers(self, mock_find_drivers):
        """Test ride request with no available drivers"""
        # Mock no drivers found
        mock_find_drivers.return_value = []
        
        result = self.controller.process_ride_request(self.ride)
        
        self.assertFalse(result['success'])
        self.assertEqual(result['drivers_found'], 0)
        self.assertEqual(result['offers_created'], 0)
        
        # Ride status should be updated
        self.ride.refresh_from_db()
        self.assertEqual(self.ride.status, RideStatus.NO_DRIVER_FOUND)
    
    def test_accept_ride_offer(self):
        """Test driver accepting ride offer"""
        # Create ride offer
        offer = RideOffer.objects.create(
            ride=self.ride,
            driver=self.driver_user,
            estimated_arrival_time=10,
            driver_latitude=self.driver.current_location_lat,
            driver_longitude=self.driver.current_location_lng,
            expires_at=timezone.now() + timedelta(minutes=2)
        )
        
        # Set ride status to requested
        self.ride.status = RideStatus.REQUESTED
        self.ride.save()
        
        result = self.controller.accept_ride_offer(offer)
        
        self.assertTrue(result['success'])
        
        # Check updates
        offer.refresh_from_db()
        self.ride.refresh_from_db()
        self.driver.refresh_from_db()
        
        self.assertEqual(offer.status, RideOffer.OfferStatus.ACCEPTED)
        self.assertEqual(self.ride.status, RideStatus.ACCEPTED)
        self.assertEqual(self.ride.driver, self.driver_user)
        self.assertFalse(self.driver.is_available)
    
    def test_reject_ride_offer(self):
        """Test driver rejecting ride offer"""
        # Create ride offer
        offer = RideOffer.objects.create(
            ride=self.ride,
            driver=self.driver_user,
            estimated_arrival_time=10,
            driver_latitude=self.driver.current_location_lat,
            driver_longitude=self.driver.current_location_lng,
            expires_at=timezone.now() + timedelta(minutes=2)
        )
        
        result = self.controller.reject_ride_offer(offer)
        
        self.assertTrue(result['success'])
        
        # Check updates
        offer.refresh_from_db()
        self.assertEqual(offer.status, RideOffer.OfferStatus.REJECTED)


class RideMatchingAPITest(APITestCase):
    """Test ride matching API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.customer = User.objects.create_user(
            username='customer1',
            email='customer@test.com',
            password='testpass123'
        )
        
        self.driver_user = User.objects.create_user(
            username='driver1',
            email='driver@test.com',
            password='testpass123'
        )
        
        self.driver = Driver.objects.create(
            user=self.driver_user,
            license_number='DL123456',
            phone_number='+2348012345678',
            status=Driver.DriverStatus.ACTIVE,
            subscription_tier=Driver.SubscriptionTier.PREMIUM,
            is_online=True,
            is_available=True,
            current_location_lat=Decimal('6.5244'),
            current_location_lng=Decimal('3.3792')
        )
    
    def test_request_ride_authenticated(self):
        """Test ride request with authentication"""
        self.client.force_authenticate(user=self.customer)
        
        data = {
            'ride_type': RideType.NORMAL,
            'pickup_address': 'Test Pickup',
            'pickup_latitude': '6.5200',
            'pickup_longitude': '3.3800',
            'destination_address': 'Test Destination',
            'destination_latitude': '6.5300',
            'destination_longitude': '3.3900'
        }
        
        with patch.object(
            RideMatchingController, 'process_ride_request',
            return_value={
                'success': True,
                'drivers_found': 1,
                'offers_created': 1,
                'surge_multiplier': 1.0,
                'driver_scores': []
            }
        ):
            response = self.client.post(
                '/api/rides/matching/request_ride/',
                data,
                format='json'
            )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['matching_result']['success'])
    
    def test_request_ride_unauthenticated(self):
        """Test ride request without authentication"""
        data = {
            'ride_type': RideType.NORMAL,
            'pickup_address': 'Test Pickup',
            'pickup_latitude': '6.5200',
            'pickup_longitude': '3.3800',
            'destination_address': 'Test Destination',
            'destination_latitude': '6.5300',
            'destination_longitude': '3.3900'
        }
        
        response = self.client.post(
            '/api/rides/matching/request_ride/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_driver_response_accept(self):
        """Test driver accepting ride offer"""
        self.client.force_authenticate(user=self.driver_user)
        
        # Create test ride and offer
        ride = Ride.objects.create(
            customer=self.customer,
            customer_tier=UserTier.PREMIUM,
            ride_type=RideType.NORMAL,
            pickup_address='Test Pickup',
            pickup_latitude=Decimal('6.5200'),
            pickup_longitude=Decimal('3.3800'),
            destination_address='Test Destination',
            destination_latitude=Decimal('6.5300'),
            destination_longitude=Decimal('3.3900'),
            status=RideStatus.REQUESTED
        )
        
        offer = RideOffer.objects.create(
            ride=ride,
            driver=self.driver_user,
            estimated_arrival_time=10,
            driver_latitude=self.driver.current_location_lat,
            driver_longitude=self.driver.current_location_lng,
            expires_at=timezone.now() + timedelta(minutes=2)
        )
        
        data = {
            'offer_id': str(offer.id),
            'accepted': True
        }
        
        response = self.client.post(
            '/api/rides/matching/driver_response/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
    
    def test_driver_status_update(self):
        """Test driver status update"""
        self.client.force_authenticate(user=self.driver_user)
        
        data = {
            'is_available': False,
            'current_location': {
                'latitude': 6.5300,
                'longitude': 3.3850
            }
        }
        
        response = self.client.patch(
            '/api/rides/matching/driver_status/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'updated')
        
        # Check driver was updated
        self.driver.refresh_from_db()
        self.assertFalse(self.driver.is_available)
        self.assertEqual(
            self.driver.current_location_lat,
            Decimal('6.5300')
        )
    
    def test_active_offers_for_driver(self):
        """Test getting active offers for driver"""
        self.client.force_authenticate(user=self.driver_user)
        
        # Create test offer
        ride = Ride.objects.create(
            customer=self.customer,
            customer_tier=UserTier.PREMIUM,
            ride_type=RideType.NORMAL,
            pickup_address='Test Pickup',
            pickup_latitude=Decimal('6.5200'),
            pickup_longitude=Decimal('3.3800'),
            destination_address='Test Destination',
            destination_latitude=Decimal('6.5300'),
            destination_longitude=Decimal('3.3900'),
            status=RideStatus.REQUESTED
        )
        
        offer = RideOffer.objects.create(
            ride=ride,
            driver=self.driver_user,
            estimated_arrival_time=10,
            driver_latitude=self.driver.current_location_lat,
            driver_longitude=self.driver.current_location_lng,
            expires_at=timezone.now() + timedelta(minutes=2)
        )
        
        response = self.client.get('/api/rides/matching/active_offers/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(len(response.data['offers']), 1)


class SurgeZoneTest(TestCase):
    """Test surge zone functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            is_staff=True
        )
        
        self.surge_zone = SurgeZone.objects.create(
            name='Test Zone',
            center_latitude=Decimal('6.5244'),
            center_longitude=Decimal('3.3792'),
            radius_km=5.0,
            surge_multiplier=Decimal('1.5'),
            is_active=True,
            active_from=timezone.now() - timedelta(hours=1),
            active_until=timezone.now() + timedelta(hours=1),
            created_by=self.admin_user
        )
    
    def test_surge_zone_is_active(self):
        """Test surge zone activity check"""
        self.assertTrue(self.surge_zone.is_currently_active)
        
        # Deactivate zone
        self.surge_zone.is_active = False
        self.surge_zone.save()
        
        self.assertFalse(self.surge_zone.is_currently_active)
    
    def test_surge_zone_expiry(self):
        """Test surge zone expiry"""
        # Set zone to expire
        self.surge_zone.active_until = timezone.now() - timedelta(minutes=1)
        self.surge_zone.save()
        
        self.assertFalse(self.surge_zone.is_currently_active)
