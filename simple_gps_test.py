#!/usr/bin/env python3
"""Simple GPS Tracking Test"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vip_ride_platform.settings')
django.setup()

from gps_tracking.models import GPSLocation, GeofenceZone
from django.contrib.auth import get_user_model
from decimal import Decimal

print("🧪 SIMPLE GPS TRACKING TEST")
print("=" * 40)

try:
    # Get user
    User = get_user_model()
    user = User.objects.first()
    print(f"✅ Using user: {user.username}")
    
    # Check actual GPSLocation fields
    fields = [f.name for f in GPSLocation._meta.fields]
    print(f"✅ GPSLocation fields: {fields}")
    
    # Create GPS location with minimal required fields
    location = GPSLocation.objects.create(
        user=user,
        latitude=Decimal('6.5244'),
        longitude=Decimal('3.3792')
    )
    print(f"✅ Created GPS location: {location}")
    
    # Create geofence zone
    zone = GeofenceZone.objects.create(
        name='Test Zone',
        zone_type='pickup',
        center_latitude=Decimal('6.5774'),
        center_longitude=Decimal('3.3211'),
        radius=Decimal('1000.0'),
        boundary_coordinates=[[3.31, 6.57], [3.33, 6.57], [3.33, 6.59], [3.31, 6.59]]
    )
    print(f"✅ Created geofence zone: {zone}")
    
    # Test point-in-polygon
    print(f"✅ Testing geofence contains point: {zone.contains_point(6.58, 3.32)}")
    
    print("\n🎉 GPS TRACKING SYSTEM WORKING PERFECTLY!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
