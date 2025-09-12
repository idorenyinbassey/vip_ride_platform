#!/usr/bin/env python
"""
Test Flutter activation API directly with HTTP requests
"""
import requests
import json
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vip_ride_platform.dev_settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.premium_card_models import PremiumDigitalCard

User = get_user_model()

def test_flutter_api():
    """Test the Flutter API endpoints with HTTP requests"""
    print("🧪 Testing Flutter API Endpoints via HTTP")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8001/api/v1/accounts"
    
    # Get test user and card
    superuser = User.objects.filter(is_superuser=True).first()
    available_card = PremiumDigitalCard.objects.filter(status='available').first()
    
    if not superuser or not available_card:
        print("❌ Need superuser and available card for testing")
        return
    
    print(f"Testing with user: {superuser.email}")
    print(f"Testing with card: {available_card.card_number}")
    
    # First get login token
    print("\n1. Getting authentication token...")
    login_data = {
        "email": superuser.email,
        "password": "testpass123"  # Updated password
    }
    
    try:
        login_response = requests.post(f"{base_url}/login/", json=login_data)
        print(f"   Login status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            tokens = login_response.json()
            access_token = tokens.get('access')
            print(f"   ✅ Got access token")
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Test tier status endpoint
            print("\n2. Testing tier status endpoint...")
            tier_response = requests.get(f"{base_url}/flutter/tier-status/", headers=headers)
            print(f"   Status: {tier_response.status_code}")
            
            if tier_response.status_code == 200:
                tier_data = tier_response.json()
                print(f"   Current tier: {tier_data.get('user', {}).get('tier')}")
                print(f"   Tier display: {tier_data.get('user', {}).get('tier_display')}")
                print(f"   Requires MFA: {tier_data.get('tier_info', {}).get('requires_mfa')}")
                print(f"   Features: {tier_data.get('tier_info', {}).get('features', [])[:3]}...")
            else:
                print(f"   ❌ Error: {tier_response.text}")
            
            # Test card activation endpoint
            print("\n3. Testing card activation endpoint...")
            activation_data = {
                "card_number": available_card.card_number,
                "verification_code": available_card.verification_code,
                "device_name": "Test Flutter App"
            }
            
            activation_response = requests.post(f"{base_url}/flutter/activate-card/", 
                                              json=activation_data, headers=headers)
            print(f"   Status: {activation_response.status_code}")
            
            if activation_response.status_code == 200:
                activation_data = activation_response.json()
                print(f"   ✅ Card activated successfully!")
                print(f"   New tier: {activation_data.get('user', {}).get('tier')}")
                print(f"   Message: {activation_data.get('message')}")
                print(f"   Device trusted: {activation_data.get('device', {}).get('trusted')}")
                print(f"   Should refresh: {activation_data.get('next_steps', {}).get('should_refresh_session')}")
            else:
                print(f"   ❌ Activation failed: {activation_response.text}")
            
            # Test tier status again after activation
            print("\n4. Checking tier status after activation...")
            final_tier_response = requests.get(f"{base_url}/flutter/tier-status/", headers=headers)
            if final_tier_response.status_code == 200:
                final_data = final_tier_response.json()
                print(f"   Final tier: {final_data.get('user', {}).get('tier')}")
                print(f"   Premium cards: {final_data.get('premium_cards', {}).get('total')}")
                print(f"   Device trusted: {final_data.get('device', {}).get('is_trusted')}")
            
        else:
            print(f"   ❌ Login failed: {login_response.text}")
            print("   Make sure the superuser password is 'admin123' or update the script")
    
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Django server. Make sure it's running on http://127.0.0.1:8001")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_flutter_api()