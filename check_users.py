#!/usr/bin/env python
"""
Quick script to check and manage user accounts for testing
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vip_ride_platform.settings')
sys.path.append('/home/idorenyinbassey/My projects/workspace1/vip_ride_platform')

django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

User = get_user_model()

def list_users():
    """List all users"""
    users = User.objects.all()
    print(f"\n📋 Total users: {users.count()}")
    for user in users:
        print(f"  • {user.email} (ID: {user.id}, Active: {user.is_active}, Staff: {user.is_staff})")
        print(f"    Tier: {user.tier}, Type: {getattr(user, 'user_type', 'N/A')}")
        print(f"    Last Login: {user.last_login}")
        print()

def create_test_user():
    """Create a test user"""
    email = "test@vipride.com"
    password = "TestPass123!"
    
    # Check if user already exists
    if User.objects.filter(email=email).exists():
        print(f"❌ User {email} already exists")
        return
    
    # Create user
    user = User.objects.create_user(
        email=email,
        password=password,
        first_name="Test",
        last_name="User",
        tier="normal",
        is_active=True
    )
    
    print(f"✅ Test user created:")
    print(f"   Email: {email}")
    print(f"   Password: {password}")
    print(f"   User ID: {user.id}")

def reset_password(email, new_password):
    """Reset password for a user"""
    try:
        user = User.objects.get(email=email)
        user.set_password(new_password)
        user.is_active = True  # Ensure user is active
        user.save()
        print(f"✅ Password reset for {email}")
        print(f"   New password: {new_password}")
    except User.DoesNotExist:
        print(f"❌ User {email} not found")

def activate_user(email):
    """Activate a user account"""
    try:
        user = User.objects.get(email=email)
        user.is_active = True
        user.save()
        print(f"✅ User {email} activated")
    except User.DoesNotExist:
        print(f"❌ User {email} not found")

if __name__ == "__main__":
    print("🔍 VIP Ride User Management")
    print("=" * 40)
    
    # List all users
    list_users()
    
    # Check for the registered user
    registered_email = "idorenyinbassey@gmail.com"
    
    try:
        user = User.objects.get(email=registered_email)
        print(f"📧 Found user: {registered_email}")
        print(f"   Active: {user.is_active}")
        print(f"   Staff: {user.is_staff}")
        print(f"   Tier: {user.tier}")
        print(f"   Last Login: {user.last_login}")
        
        # Reset password
        new_password = "NewPassword123!"
        reset_password(registered_email, new_password)
        
        # Activate user
        activate_user(registered_email)
        
    except User.DoesNotExist:
        print(f"❌ User {registered_email} not found")
        print("🔧 Creating test user instead...")
        create_test_user()
    
    print("\n✅ Done!")
