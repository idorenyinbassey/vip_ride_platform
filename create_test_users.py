#!/usr/bin/env python3
"""
Create test users for GPS encryption testing
"""

import os
import sys
import django
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vip_ride_platform.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def create_test_users():
    """Create test users for GPS encryption testing"""
    print("🔧 Creating test users for GPS encryption testing...")
    
    test_users = [
        {
            'email': 'vip@test.com',
            'password': 'testpass123',
            'tier': 'vip',  # Lowercase to match UserTier.VIP value
            'first_name': 'VIP',
            'last_name': 'User',
            'phone_number': '+2348012345001'
        },
        {
            'email': 'vip_premium@test.com',
            'password': 'testpass123',
            'tier': 'vip_premium',  # Lowercase to match UserTier.VIP_PREMIUM value
            'first_name': 'VIP Premium',
            'last_name': 'User',
            'phone_number': '+2348012345002'
        },
        {
            'email': 'normal@test.com',
            'password': 'testpass123',
            'tier': 'normal',  # Lowercase to match UserTier.NORMAL value
            'first_name': 'Normal',
            'last_name': 'User',
            'phone_number': '+2348012345003'
        }
    ]
    
    created_count = 0
    
    for user_data in test_users:
        email = user_data['email']
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            print(f"✅ User {email} already exists")
            continue
        
        try:
            # Create user
            user = User.objects.create_user(
                email=user_data['email'],
                password=user_data['password'],
                tier=user_data['tier'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                phone_number=user_data['phone_number']
            )
            
            print(f"✅ Created user: {email} (Tier: {user_data['tier']})")
            created_count += 1
            
        except Exception as e:
            print(f"❌ Failed to create user {email}: {e}")
    
    print(f"\n🎉 Setup complete! Created {created_count} new test users")
    print("📱 You can now run GPS encryption tests")
    
    return created_count

if __name__ == "__main__":
    create_test_users()
