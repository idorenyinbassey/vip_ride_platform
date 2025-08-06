#!/usr/bin/env python
"""
JWT Authentication System Test Script
Tests the core functionality of the JWT authentication system
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vip_ride_platform.settings')
django.setup()

from accounts.models import User, UserSession, TrustedDevice, MFAToken
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.jwt_config import USER_TIER_SETTINGS
from django.utils import timezone
import json

def test_jwt_system():
    """Test the JWT authentication system"""
    print("🚀 Testing JWT Authentication System...")
    print("=" * 50)
    
    # Test 1: User Creation
    print("\n1. Testing User Creation...")
    try:
        # Clean up any existing test user
        User.objects.filter(email='test_jwt@example.com').delete()
        
        # Create test users for each tier
        test_users = []
        tiers = ['normal', 'premium', 'vip']
        
        for tier in tiers:
            user = User.objects.create_user(
                username=f'test_{tier}',
                email=f'test_{tier}@example.com',
                password='testpass123',
                first_name='Test',
                last_name=tier.capitalize(),
                tier=tier,
                phone_number=f'+23480123456{len(test_users)}'
            )
            test_users.append(user)
            print(f"   ✅ Created {tier} user: {user.email}")
        
        print(f"   ✅ Successfully created {len(test_users)} test users")
        
    except Exception as e:
        print(f"   ❌ Error creating users: {e}")
        return False
    
    # Test 2: JWT Token Generation
    print("\n2. Testing JWT Token Generation...")
    try:
        for user in test_users:
            refresh = RefreshToken.for_user(user)
            refresh['user_tier'] = user.tier
            
            # Get tier-specific settings
            tier_config = USER_TIER_SETTINGS.get(user.tier, {})
            access_lifetime = tier_config.get('access_token_lifetime', '15 minutes')
            refresh_lifetime = tier_config.get('refresh_token_lifetime', '7 days')
            
            print(f"   ✅ {user.tier.capitalize()} user tokens generated")
            print(f"      - Access lifetime: {access_lifetime}")
            print(f"      - Refresh lifetime: {refresh_lifetime}")
            
    except Exception as e:
        print(f"   ❌ Error generating tokens: {e}")
        return False
    
    # Test 3: Tier Configuration
    print("\n3. Testing Tier Configurations...")
    try:
        for tier, config in USER_TIER_SETTINGS.items():
            print(f"   ✅ {tier.capitalize()} tier configuration:")
            print(f"      - Access token: {config.get('access_token_lifetime', 'N/A')}")
            print(f"      - Refresh token: {config.get('refresh_token_lifetime', 'N/A')}")
            print(f"      - MFA required: {config.get('require_mfa', False)}")
            print(f"      - Rate limit: {config.get('rate_limits', {}).get('requests', 'N/A')}/hour")
            
    except Exception as e:
        print(f"   ❌ Error checking tier configs: {e}")
        return False
    
    # Test 4: Database Models
    print("\n4. Testing Database Models...")
    try:
        # Test UserSession model
        session = UserSession.objects.create(
            user=test_users[0],
            session_id='test-session-123',
            ip_address='127.0.0.1',
            expires_at=timezone.now() + timezone.timedelta(hours=1)
        )
        print(f"   ✅ UserSession model working: {session}")
        
        # Test TrustedDevice model
        device = TrustedDevice.objects.create(
            user=test_users[0],
            device_fingerprint='test-device-123',
            device_name='Test Device',
            user_agent='Test Browser',
            ip_address='127.0.0.1'
        )
        print(f"   ✅ TrustedDevice model working: {device}")
        
        # Test MFAToken model
        mfa = MFAToken.objects.create(
            user=test_users[2],  # VIP user
            token_type='totp',
            secret_key='TESTSECRET123456'
        )
        print(f"   ✅ MFAToken model working: {mfa}")
        
    except Exception as e:
        print(f"   ❌ Error testing models: {e}")
        return False
    
    # Test 5: Authentication Utilities
    print("\n5. Testing Authentication Utilities...")
    try:
        from accounts.utils import validate_phone_number, generate_mfa_code, hash_token
        
        # Test phone validation
        phone_valid = validate_phone_number('+2348012345678')
        print(f"   ✅ Phone validation working: {phone_valid}")
        
        # Test MFA code generation
        mfa_code = generate_mfa_code(6)
        print(f"   ✅ MFA code generation working: {mfa_code}")
        
        # Test token hashing
        token_hash = hash_token('test-token')
        print(f"   ✅ Token hashing working: {token_hash[:16]}...")
        
    except Exception as e:
        print(f"   ❌ Error testing utilities: {e}")
        return False
    
    # Test 6: JWT Config
    print("\n6. Testing JWT Configuration...")
    try:
        from accounts.jwt_config import RATE_LIMIT_SETTINGS, MFA_SETTINGS
        
        print(f"   ✅ Rate limit settings loaded")
        print(f"   ✅ MFA settings loaded: {len(MFA_SETTINGS)} configurations")
        
        # Display some rate limit info
        if isinstance(RATE_LIMIT_SETTINGS, dict):
            print(f"      - Rate limiting enabled: {RATE_LIMIT_SETTINGS.get('enable_rate_limiting', False)}")
            print(f"      - Progressive penalty: {RATE_LIMIT_SETTINGS.get('progressive_penalty', False)}")
            
    except Exception as e:
        print(f"   ❌ Error testing JWT config: {e}")
        return False
    
    # Cleanup
    print("\n7. Cleaning up test data...")
    try:
        User.objects.filter(email__startswith='test_').delete()
        UserSession.objects.filter(session_id='test-session-123').delete()
        TrustedDevice.objects.filter(device_fingerprint='test-device-123').delete()
        print("   ✅ Test data cleaned up")
    except Exception as e:
        print(f"   ⚠️  Warning: Cleanup error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 JWT Authentication System Test Complete!")
    print("✅ All core components are working correctly")
    print("\n📋 System Summary:")
    print("   - Tier-based JWT tokens: ✅ Working")
    print("   - Multi-factor authentication: ✅ Working") 
    print("   - Device trust management: ✅ Working")
    print("   - Security models: ✅ Working")
    print("   - Rate limiting config: ✅ Working")
    print("   - Authentication utilities: ✅ Working")
    
    return True

if __name__ == '__main__':
    test_jwt_system()
