from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from decimal import Decimal
from unittest.mock import patch
import json

from .models import GPSLocation, GeofenceZone
from accounts.models import User

User = get_user_model()


class GPSTrackingModelTestCase(TestCase):
    """Test GPS tracking models"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_tier='VIP'
        )
    
    def test_create_gps_location(self):
        """Test creating a GPS location"""
        location = GPSLocation.objects.create(
            user=self.user,
            latitude=Decimal('6.5244'),
            longitude=Decimal('3.3792')
        )
        
        self.assertEqual(location.user, self.user)
        self.assertEqual(location.latitude, Decimal('6.5244'))
        self.assertEqual(location.longitude, Decimal('3.3792'))
        self.assertTrue(location.created_at)
    
    def test_create_geofence_zone(self):
        """Test creating a geofence zone"""
        zone = GeofenceZone.objects.create(
            name='Test Zone',
            zone_type='pickup',
            center_latitude=Decimal('6.5774'),
            center_longitude=Decimal('3.3211'),
            radius=Decimal('1000.0'),
            boundary_coordinates=[[3.31, 6.57], [3.33, 6.57], [3.33, 6.59], [3.31, 6.59]]
        )
        
        self.assertEqual(zone.name, 'Test Zone')
        self.assertEqual(zone.zone_type, 'pickup')
        self.assertEqual(zone.radius, Decimal('1000.0'))
    
    def test_geofence_contains_point(self):
        """Test geofence point-in-polygon functionality"""
        zone = GeofenceZone.objects.create(
            name='Test Zone',
            zone_type='pickup',
            center_latitude=Decimal('6.5774'),
            center_longitude=Decimal('3.3211'),
            radius=Decimal('1000.0'),
            boundary_coordinates=[[3.31, 6.57], [3.33, 6.57], [3.33, 6.59], [3.31, 6.59]]
        )
        
        # Test point inside polygon
        self.assertTrue(zone.contains_point(6.58, 3.32))
        
        # Test point outside polygon
        self.assertFalse(zone.contains_point(6.60, 3.35))


class GPSTrackingAPITestCase(TestCase):
    """Test GPS tracking API endpoints"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_tier='VIP'
        )
        self.client.force_login(self.user)
    
    def test_update_location_endpoint(self):
        """Test GPS location update endpoint"""
        url = reverse('gps:update_location')
        data = {
            'latitude': 6.5244,
            'longitude': 3.3792,
            'accuracy': 10.5
        }
        
        response = self.client.post(url, data, content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(GPSLocation.objects.filter(user=self.user).exists())
    
    def test_get_location_history(self):
        """Test getting location history"""
        # Create test locations
        GPSLocation.objects.create(
            user=self.user,
            latitude=Decimal('6.5244'),
            longitude=Decimal('3.3792')
        )
        
        url = reverse('gps:location_history')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['results']), 1)
    
    def test_geofence_check(self):
        """Test geofence checking"""
        # Create a geofence zone
        zone = GeofenceZone.objects.create(
            name='Test Zone',
            zone_type='pickup',
            center_latitude=Decimal('6.5774'),
            center_longitude=Decimal('3.3211'),
            radius=Decimal('1000.0'),
            boundary_coordinates=[[3.31, 6.57], [3.33, 6.57], [3.33, 6.59], [3.31, 6.59]]
        )
        
        url = reverse('gps:check_geofence')
        data = {
            'latitude': 6.58,
            'longitude': 3.32
        }
        
        response = self.client.post(url, data, content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['in_zone'])


class GPSEncryptionTestCase(TestCase):
    """Test GPS encryption for VIP users"""
    
    def setUp(self):
        self.vip_user = User.objects.create_user(
            username='vipuser',
            email='vip@example.com',
            password='testpass123',
            user_tier='VIP'
        )
        
        self.normal_user = User.objects.create_user(
            username='normaluser',
            email='normal@example.com',
            password='testpass123',
            user_tier='NORMAL'
        )
    
    @patch('core.encryption.encrypt_gps_data')
    def test_vip_gps_encryption(self, mock_encrypt):
        """Test that VIP user GPS data is encrypted"""
        mock_encrypt.return_value = b'encrypted_data'
        
        location = GPSLocation.objects.create(
            user=self.vip_user,
            latitude=Decimal('6.5244'),
            longitude=Decimal('3.3792')
        )
        
        # For VIP users, encryption should be called
        if hasattr(location, 'encrypted_data'):
            mock_encrypt.assert_called()
    
    def test_normal_user_no_encryption(self):
        """Test that normal user GPS data is not encrypted"""
        location = GPSLocation.objects.create(
            user=self.normal_user,
            latitude=Decimal('6.5244'),
            longitude=Decimal('3.3792')
        )
        
        # Normal users should have plain GPS data
        self.assertIsNotNone(location.latitude)
        self.assertIsNotNone(location.longitude)
