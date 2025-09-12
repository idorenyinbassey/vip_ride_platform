#!/usr/bin/env python
"""
Test Flutter card activation flow
"""
import os
import sys
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vip_ride_platform.dev_settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.premium_card_models import PremiumDigitalCard
from accounts.models import TrustedDevice

User = get_user_model()

def test_activation_flow():
    """Test the complete Flutter activation flow"""
    print("🧪 Testing Flutter Card Activation Flow")
    print("=" * 50)
    
    # 1. Check current users and their tiers
    print("\n1. Current Users and Tiers:")
    users = User.objects.all()
    for user in users:
        print(f"   - {user.email}: {user.tier}")
    
    # 2. Check available premium cards
    print("\n2. Available Premium Cards:")
    cards = PremiumDigitalCard.objects.all()
    for card in cards:
        print(f"   - Card: {card.card_number}, Tier: {card.tier}, Status: {card.status}, Owner: {card.owner}")
    
    # 3. Get a superuser for testing
    superuser = User.objects.filter(is_superuser=True).first()
    if not superuser:
        print("❌ No superuser found! Please create one first.")
        return
    
    print(f"\n3. Testing with user: {superuser.email} (Current tier: {superuser.tier})")
    
    # 4. Find an activated card for testing
    activated_card = PremiumDigitalCard.objects.filter(
        status='active',
        owner=superuser
    ).first()
    
    if not activated_card:
        print("❌ No activated premium card found for superuser!")
        print("   Let's check if there are any available cards to activate...")
        
        available_card = PremiumDigitalCard.objects.filter(status='available').first()
        if available_card:
            print(f"   Found available card: {available_card.card_number}")
            # Manually activate it for testing
            available_card.owner = superuser
            available_card.status = 'sold'
            activated = available_card.activate_card(
                user=superuser,
                ip_address='127.0.0.1',
                user_agent='Test Script',
                method='test'
            )
            if activated:
                print(f"   ✅ Card activated! User tier should now be: {superuser.tier}")
                activated_card = available_card
            else:
                print("   ❌ Card activation failed!")
                return
        else:
            print("   ❌ No available cards found!")
            return
    
    # 5. Test the Flutter API endpoints
    print(f"\n4. Testing Flutter API Endpoints:")
    print(f"   Card: {activated_card.card_number}")
    print(f"   Verification Code: {activated_card.verification_code}")
    
    # First, let's get user's current status
    print("\n   Testing tier status endpoint...")
    try:
        # This would normally require authentication token
        # For now, let's test the endpoint logic directly
        from accounts.premium_card_views import user_tier_status
        from django.test import RequestFactory
        from django.contrib.auth.models import AnonymousUser
        
        factory = RequestFactory()
        request = factory.get('/api/v1/accounts/flutter/tier-status/')
        request.user = superuser
        
        response = user_tier_status(request)
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            data = json.loads(response.content)
            print(f"   User Tier: {data.get('user', {}).get('tier')}")
            print(f"   Tier Display: {data.get('user', {}).get('tier_display')}")
            print(f"   Premium Cards: {data.get('premium_cards', {}).get('total')}")
        else:
            print(f"   Error: {response.content}")
    
    except Exception as e:
        print(f"   ❌ Tier status test failed: {str(e)}")
    
    # 6. Check trusted devices
    print(f"\n5. Trusted Devices for {superuser.email}:")
    devices = TrustedDevice.objects.filter(user=superuser)
    for device in devices:
        print(f"   - {device.device_name}: {device.trust_level} (Active: {device.is_active})")
    
    print(f"\n6. Summary:")
    print(f"   User: {superuser.email}")
    print(f"   Current Tier: {superuser.tier}")
    print(f"   Premium Cards: {PremiumDigitalCard.objects.filter(owner=superuser, status='active').count()}")
    print(f"   Trusted Devices: {TrustedDevice.objects.filter(user=superuser, is_active=True).count()}")
    
    # 7. Check if tier upgrade worked
    if superuser.tier != 'regular':
        print(f"   ✅ SUCCESS: User has been upgraded to {superuser.tier}")
    else:
        print(f"   ⚠️  WARNING: User is still on regular tier despite having premium card")
        
        # Let's check what went wrong
        print(f"\n7. Debugging tier upgrade issue...")
        if activated_card:
            print(f"   Card tier: {activated_card.tier}")
            print(f"   Card status: {activated_card.status}")
            print(f"   Card activated_at: {activated_card.activated_at}")
            
            # Check if activation actually updated user tier
            superuser.refresh_from_db()
            print(f"   User tier after refresh: {superuser.tier}")

if __name__ == "__main__":
    test_activation_flow()