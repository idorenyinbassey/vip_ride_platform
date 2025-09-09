from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
import json

from .models import User

User = get_user_model()


class UserModelTestCase(TestCase):
    """Test User model functionality"""
    
    def test_create_normal_user(self):
        """Test creating a normal user"""
        user = User.objects.create_user(
            username='normaluser',
            email='normal@example.com',
            password='testpass123',
            user_tier='NORMAL'
        )
        
        self.assertEqual(user.username, 'normaluser')
        self.assertEqual(user.email, 'normal@example.com')
        self.assertEqual(user.user_tier, 'NORMAL')
        self.assertTrue(user.check_password('testpass123'))
    
    def test_create_vip_user(self):
        """Test creating a VIP user"""
        user = User.objects.create_user(
            username='vipuser',
            email='vip@example.com',
            password='testpass123',
            user_tier='VIP'
        )
        
        self.assertEqual(user.user_tier, 'VIP')
        self.assertTrue(user.has_vip_features)
    
    def test_user_permissions_by_tier(self):
        """Test user permissions based on tier"""
        normal_user = User.objects.create_user(
            username='normal',
            email='normal@example.com',
            password='test123',
            user_tier='NORMAL'
        )
        
        vip_user = User.objects.create_user(
            username='vip',
            email='vip@example.com',
            password='test123',
            user_tier='VIP'
        )
        
        # Normal users shouldn't have VIP permissions
        self.assertFalse(normal_user.has_vip_features)
        
        # VIP users should have VIP permissions
        self.assertTrue(vip_user.has_vip_features)


class AuthenticationAPITestCase(APITestCase):
    """Test authentication API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'user_tier': 'NORMAL'
        }
        
        self.user = User.objects.create_user(**self.user_data)
    
    def test_user_registration(self):
        """Test user registration endpoint"""
        url = reverse('accounts:register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'password_confirm': 'newpass123',
            'user_tier': 'NORMAL'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_user_login(self):
        """Test user login endpoint"""
        url = reverse('accounts:login')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_protected_endpoint_requires_auth(self):
        """Test that protected endpoints require authentication"""
        url = reverse('accounts:profile')
        
        # Without authentication
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # With authentication
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_jwt_token_refresh(self):
        """Test JWT token refresh"""
        # Login to get tokens
        login_url = reverse('accounts:login')
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        login_response = self.client.post(login_url, login_data)
        refresh_token = login_response.data['refresh']
        
        # Use refresh token to get new access token
        refresh_url = reverse('token_refresh')
        refresh_data = {'refresh': refresh_token}
        refresh_response = self.client.post(refresh_url, refresh_data)
        
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', refresh_response.data)


class RBACTestCase(TestCase):
    """Test Role-Based Access Control"""
    
    def setUp(self):
        self.client = Client()
        
        # Create users with different roles
        self.normal_user = User.objects.create_user(
            username='normal',
            email='normal@example.com',
            password='test123',
            user_tier='NORMAL'
        )
        
        self.vip_user = User.objects.create_user(
            username='vip',
            email='vip@example.com',
            password='test123',
            user_tier='VIP'
        )
        
        self.driver = User.objects.create_user(
            username='driver',
            email='driver@example.com',
            password='test123',
            user_type='DRIVER'
        )
    
    def test_normal_user_access_restrictions(self):
        """Test normal user access restrictions"""
        self.client.force_login(self.normal_user)
        
        # Normal users should be able to access basic ride features
        response = self.client.get(reverse('rides:list'))
        self.assertEqual(response.status_code, 200)
        
        # But not VIP features (if endpoint exists)
        # This would depend on your actual URL patterns
    
    def test_vip_user_enhanced_access(self):
        """Test VIP user enhanced access"""
        self.client.force_login(self.vip_user)
        
        # VIP users should have access to all user features
        response = self.client.get(reverse('rides:list'))
        self.assertEqual(response.status_code, 200)
    
    def test_driver_specific_permissions(self):
        """Test driver-specific permissions"""
        self.client.force_login(self.driver)
        
        # Drivers should have access to ride management
        # but not user-specific features
