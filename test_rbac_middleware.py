# Test RBAC Middleware in Action
"""
Simple test to verify RBAC middleware is working
"""

from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from accounts.permissions import IsVIPUser, IsPremiumUser, IsNormalUser
from accounts.models import SecurityEvent

User = get_user_model()


def test_rbac_middleware():
    """Test RBAC middleware functionality"""
    
    print("Testing RBAC Middleware...")
    
    # Test with different user tiers
    test_users = User.objects.filter(email__contains='test')
    
    factory = RequestFactory()
    
    for user in test_users:
        print(f"\nTesting user: {user.email} (tier: {user.tier})")
        
        # Test VIP permission
        request = factory.get('/api/vip-data/')
        request.user = user
        
        vip_permission = IsVIPUser()
        has_vip_access = vip_permission.has_permission(request, None)
        
        should_have_vip = user.tier in ['vip', 'concierge', 'admin']
        
        print(f"  VIP access: {has_vip_access} (expected: {should_have_vip})")
        
        # Test Premium permission
        premium_permission = IsPremiumUser()
        has_premium_access = premium_permission.has_permission(request, None)
        
        should_have_premium = user.tier in ['premium', 'vip', 'concierge', 'admin']
        
        print(f"  Premium access: {has_premium_access} (expected: {should_have_premium})")
        
        # Verify results
        if has_vip_access == should_have_vip and has_premium_access == should_have_premium:
            print(f"  ✅ {user.tier} user permissions working correctly")
        else:
            print(f"  ❌ {user.tier} user permissions not working")
    
    # Check if security events were created
    total_events = SecurityEvent.objects.count()
    print(f"\nTotal security events: {total_events}")
    
    if total_events > 0:
        recent_events = SecurityEvent.objects.order_by('-created_at')[:3]
        print("Recent events:")
        for event in recent_events:
            print(f"  - {event.event_type} ({event.severity}): {event.description[:80]}...")
    
    print("\n🎉 RBAC Middleware Test Complete!")


if __name__ == "__main__":
    test_rbac_middleware()
