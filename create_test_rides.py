#!/usr/bin/env python3
"""
Create test rides for GPS encryption testing
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
from rides.models import Ride, RideStatus, RideType
import uuid

User = get_user_model()

def create_test_rides():
    """Create test rides for GPS encryption testing"""
    print("🚗 Creating test rides for GPS encryption testing...")
    
    test_ride_data = [
        {
            'ride_id': 'f8d8af0a-045a-4057-8375-5819c914bcc1',  # UUID for VIP test
            'user_email': 'vip@test.com',
            'ride_type': RideType.VIP
        },
        {
            'ride_id': '17ad0c40-c478-49f2-b7b0-09ee18a0453b',  # UUID for VIP Premium test
            'user_email': 'vip_premium@test.com',
            'ride_type': RideType.VIP
        },
        {
            'ride_id': 'f25a9c53-aa8c-4481-99da-6ceb14e7883e',  # UUID for Normal test
            'user_email': 'normal@test.com',
            'ride_type': RideType.NORMAL
        }
    ]
    
    created_count = 0
    
    for ride_data in test_ride_data:
        ride_id = ride_data['ride_id']
        user_email = ride_data['user_email']
        
        try:
            # Get user
            user = User.objects.get(email=user_email)
            
            # Check if ride already exists
            if Ride.objects.filter(id=ride_id).exists():
                print(f"✅ Ride {ride_id} already exists")
                continue
            
            # Create ride
            ride = Ride.objects.create(
                id=ride_id,
                rider=user,  # User field is called 'rider'
                ride_type=ride_data['ride_type'],
                status=RideStatus.REQUESTED,
                pickup_address="Test Pickup Location",
                destination_address="Test Dropoff Location",
                pickup_latitude=6.5244,
                pickup_longitude=3.3792,
                destination_latitude=6.5270,
                destination_longitude=3.3820,
                estimated_fare=1000.00,
                estimated_distance_km=5.0,
                estimated_duration_minutes=15,
                platform_commission_rate=20.00  # 20% commission rate
            )
            
            print(f"✅ Created ride: {ride_id} for {user_email}")
            created_count += 1
            
        except User.DoesNotExist:
            print(f"❌ User {user_email} not found")
        except Exception as e:
            print(f"❌ Failed to create ride {ride_id}: {e}")
    
    print(f"\n🎉 Setup complete! Created {created_count} new test rides")
    print("🧪 You can now run GPS encryption tests with valid ride IDs")

if __name__ == "__main__":
    create_test_rides()
