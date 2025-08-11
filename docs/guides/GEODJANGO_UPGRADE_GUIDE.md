# GeoDjango Upgrade Guide
## Migrating from Simplified Coordinates to Advanced Spatial Features

### Overview
This guide provides step-by-step instructions for upgrading the VIP Ride-Hailing Platform from the current simplified coordinate system to GeoDjango with PostGIS for enhanced geographic precision.

---

## Prerequisites

### System Requirements
- **Operating System**: Ubuntu 20.04+ / CentOS 8+ / macOS 10.15+
- **Python**: 3.10+
- **PostgreSQL**: 12+ with PostGIS extension
- **Django**: 5.2.5+
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: Additional 2GB for spatial data

### Before You Begin
1. **Backup Current Database**
   ```bash
   python manage.py dumpdata > backup_before_geodjango.json
   sqlite3 db.sqlite3 ".backup backup_db.sqlite3"
   ```

2. **Test Environment Setup**
   - Create a separate test environment
   - Verify all current functionality works
   - Document current pricing calculations

---

## Phase 1: Infrastructure Setup

### 1.1 Install PostGIS Dependencies

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo apt-get install postgis postgresql-14-postgis-3
sudo apt-get install gdal-bin libgdal-dev
sudo apt-get install python3-gdal binutils libproj-dev
```

#### macOS (using Homebrew)
```bash
brew install postgresql
brew install postgis
brew install gdal
```

#### Windows
```bash
# Install OSGeo4W or use conda
conda install -c conda-forge gdal
```

### 1.2 PostgreSQL Database Setup
```bash
# Create database and user
sudo -u postgres createdb vip_ride_geodjango
sudo -u postgres createuser geodjango_user
sudo -u postgres psql

# In PostgreSQL shell:
ALTER USER geodjango_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE vip_ride_geodjango TO geodjango_user;

# Connect to the database and enable PostGIS
\c vip_ride_geodjango
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;
SELECT PostGIS_version();
\q
```

### 1.3 Python Dependencies
```bash
# Install GeoDjango dependencies
pip install psycopg2-binary
pip install GDAL
pip install django-leaflet
pip install geojson
```

---

## Phase 2: Django Configuration

### 2.1 Settings Update
```python
# settings_geodjango.py
import os
from pathlib import Path

# GDAL Configuration
if os.name == 'nt':  # Windows
    VENV_BASE = os.environ['VIRTUAL_ENV']
    os.environ['PATH'] = os.path.join(VENV_BASE, 'Lib\\site-packages\\osgeo') + ';' + os.environ['PATH']
    os.environ['PROJ_LIB'] = os.path.join(VENV_BASE, 'Lib\\site-packages\\osgeo\\data\\proj') + ';' + os.environ['PATH']

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'vip_ride_geodjango',
        'USER': 'geodjango_user',
        'PASSWORD': 'secure_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',  # Add this
    'leaflet',  # For map widgets
    'pricing',
    'accounts',
    'rides',
    'fleet_management',
    'payments',
]

# Leaflet Configuration for Admin Maps
LEAFLET_CONFIG = {
    'DEFAULT_CENTER': (6.5244, 3.3792),  # Lagos coordinates
    'DEFAULT_ZOOM': 10,
    'MIN_ZOOM': 8,
    'MAX_ZOOM': 18,
    'TILES': [
        ('OpenStreetMap', 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            'attribution': '© OpenStreetMap contributors'
        }),
    ],
}
```

---

## Phase 3: Model Migration

### 3.1 Create GeoDjango Models
```python
# pricing/models_geodjango.py
from django.contrib.gis.db import models as gis_models
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
import uuid
from datetime import timedelta
from typing import Tuple

class PricingZone(models.Model):
    """Geographic pricing zones with precise polygon boundaries"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, help_text="Zone name")
    description = models.TextField(blank=True)
    city = models.CharField(max_length=50)
    country = models.CharField(max_length=50, default='Nigeria')
    
    # GeoDjango fields
    boundary = gis_models.PolygonField(
        help_text="Precise geographic boundary of the pricing zone",
        srid=4326  # WGS84 coordinate system
    )
    center_point = gis_models.PointField(
        help_text="Center point of the zone for quick calculations",
        srid=4326,
        null=True,
        blank=True
    )
    
    # Pricing configuration (unchanged)
    base_multiplier = models.DecimalField(
        max_digits=5, decimal_places=3, default=Decimal('1.000'),
        validators=[MinValueValidator(Decimal('0.1')), MaxValueValidator(Decimal('10.0'))],
        help_text="Base pricing multiplier for this zone"
    )
    is_premium_zone = models.BooleanField(default=False)
    
    # Surge configuration (unchanged)
    surge_enabled = models.BooleanField(default=True)
    max_surge_multiplier = models.DecimalField(
        max_digits=5, decimal_places=3, default=Decimal('5.000'),
        validators=[MinValueValidator(Decimal('1.0')), MaxValueValidator(Decimal('10.0'))]
    )
    
    # Geographic metadata
    area_sq_km = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Area of the zone in square kilometers"
    )
    perimeter_km = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Perimeter of the zone in kilometers"
    )
    
    # Status (unchanged)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'pricing_zones_geo'
        indexes = [
            models.Index(fields=['city', 'is_active']),
            models.Index(fields=['is_premium_zone', 'is_active']),
        ]
    
    def save(self, *args, **kwargs):
        """Auto-calculate geographic properties"""
        if self.boundary:
            # Calculate center point
            self.center_point = self.boundary.centroid
            
            # Calculate area (in square meters, convert to km²)
            if self.boundary.area:
                self.area_sq_km = Decimal(str(self.boundary.area * 12345.679))  # Approximate conversion
            
            # Calculate perimeter
            if self.boundary.length:
                self.perimeter_km = Decimal(str(self.boundary.length * 111.32))  # Approximate conversion
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} ({self.city})"
    
    def contains_point(self, latitude: Decimal, longitude: Decimal) -> bool:
        """Check if a point is within this zone's boundaries"""
        from django.contrib.gis.geos import Point
        point = Point(float(longitude), float(latitude), srid=4326)
        return self.boundary.contains(point)
    
    def distance_to_point(self, latitude: Decimal, longitude: Decimal) -> Decimal:
        """Calculate distance from zone center to a point in kilometers"""
        from django.contrib.gis.geos import Point
        point = Point(float(longitude), float(latitude), srid=4326)
        if self.center_point:
            # Distance in meters, convert to kilometers
            distance_m = self.center_point.distance(point) * 111320  # Approximate
            return Decimal(str(distance_m / 1000))
        return Decimal('0')


class SpecialEvent(models.Model):
    """Special events affecting pricing with precise location"""
    
    class EventType(models.TextChoices):
        CONCERT = 'concert', 'Concert'
        SPORTS = 'sports', 'Sports Event'
        CONFERENCE = 'conference', 'Conference'
        FESTIVAL = 'festival', 'Festival'
        HOLIDAY = 'holiday', 'Holiday'
        WEATHER = 'weather', 'Weather Event'
        EMERGENCY = 'emergency', 'Emergency'
        OTHER = 'other', 'Other'
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    event_type = models.CharField(max_length=20, choices=EventType.choices)
    venue_name = models.CharField(max_length=200, blank=True)
    organizer = models.CharField(max_length=200, blank=True)
    
    # Event timing (unchanged)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    
    # GeoDjango location fields
    location = gis_models.PointField(
        help_text="Exact event location",
        srid=4326,
        null=True,
        blank=True
    )
    impact_radius_km = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal('2.0'),
        help_text="Radius in kilometers where this event affects pricing"
    )
    affected_zones = models.ManyToManyField(PricingZone, blank=True)
    
    # Pricing configuration (unchanged)
    base_multiplier = models.DecimalField(
        max_digits=5, decimal_places=3, default=Decimal('1.500'),
        validators=[MinValueValidator(Decimal('1.0')), MaxValueValidator(Decimal('10.0'))]
    )
    peak_multiplier = models.DecimalField(
        max_digits=5, decimal_places=3, default=Decimal('2.000'),
        validators=[MinValueValidator(Decimal('1.0')), MaxValueValidator(Decimal('10.0'))]
    )
    
    # Peak timing offsets (unchanged)
    peak_start_offset = models.DurationField(
        default=timedelta(minutes=-30),
        help_text="Peak starts this duration before event start"
    )
    peak_end_offset = models.DurationField(
        default=timedelta(minutes=60),
        help_text="Peak ends this duration after event start"
    )
    
    # Status (unchanged)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'special_events_geo'
        indexes = [
            models.Index(fields=['start_datetime', 'end_datetime']),
            models.Index(fields=['event_type', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.start_datetime.date()})"
    
    def affects_location(self, latitude: Decimal, longitude: Decimal) -> bool:
        """Check if event affects a specific location"""
        if not self.location or not self.impact_radius_km:
            return False
        
        from django.contrib.gis.geos import Point
        point = Point(float(longitude), float(latitude), srid=4326)
        
        # Create a circle around the event location
        from django.contrib.gis.measure import Distance
        radius = Distance(km=float(self.impact_radius_km))
        
        return self.location.distance(point) <= radius.m
```

### 3.2 Create Migration Strategy
```python
# pricing/management/commands/migrate_to_geodjango.py
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Polygon, Point
from decimal import Decimal
import json

class Command(BaseCommand):
    help = 'Migrate existing pricing zones to GeoDjango format'
    
    def handle(self, *args, **options):
        from pricing.models import PricingZone as OldPricingZone
        from pricing.models_geodjango import PricingZone as NewPricingZone
        
        # Migrate existing zones
        for old_zone in OldPricingZone.objects.all():
            # Convert rectangular bounds to polygon
            min_lat = float(old_zone.min_latitude)
            max_lat = float(old_zone.max_latitude)
            min_lng = float(old_zone.min_longitude)
            max_lng = float(old_zone.max_longitude)
            
            # Create polygon from bounds
            polygon_coords = [
                (min_lng, min_lat),  # Bottom-left
                (max_lng, min_lat),  # Bottom-right
                (max_lng, max_lat),  # Top-right
                (min_lng, max_lat),  # Top-left
                (min_lng, min_lat),  # Close polygon
            ]
            
            polygon = Polygon(polygon_coords, srid=4326)
            
            # Create new GeoDjango zone
            new_zone = NewPricingZone.objects.create(
                name=old_zone.name,
                description=old_zone.description,
                city=old_zone.city,
                country=old_zone.country,
                boundary=polygon,
                base_multiplier=old_zone.base_multiplier,
                is_premium_zone=old_zone.is_premium_zone,
                surge_enabled=old_zone.surge_enabled,
                max_surge_multiplier=old_zone.max_surge_multiplier,
                is_active=old_zone.is_active,
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Migrated zone: {new_zone.name}')
            )
        
        self.stdout.write(
            self.style.SUCCESS('Migration completed successfully!')
        )
```

---

## Phase 4: Admin Interface Upgrade

### 4.1 GeoDjango Admin
```python
# pricing/admin_geodjango.py
from django.contrib.gis import admin
from leaflet.admin import LeafletGeoAdmin
from .models_geodjango import PricingZone, SpecialEvent

@admin.register(PricingZone)
class PricingZoneAdmin(LeafletGeoAdmin):
    """Admin interface for pricing zones with interactive map"""
    
    list_display = [
        'name', 'city', 'base_multiplier', 'is_premium_zone',
        'area_sq_km', 'is_active', 'created_at'
    ]
    list_filter = [
        'is_active', 'is_premium_zone', 'surge_enabled',
        'city', 'created_at'
    ]
    search_fields = ['name', 'description', 'city']
    readonly_fields = ['area_sq_km', 'perimeter_km', 'center_point', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'city', 'country')
        }),
        ('Geographic Boundary', {
            'fields': ('boundary', 'center_point', 'area_sq_km', 'perimeter_km'),
            'classes': ('wide',)
        }),
        ('Pricing Configuration', {
            'fields': (
                'base_multiplier', 'is_premium_zone',
                'surge_enabled', 'max_surge_multiplier'
            )
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        })
    )
    
    # Map settings
    settings_overrides = {
        'DEFAULT_CENTER': (6.5244, 3.3792),  # Lagos
        'DEFAULT_ZOOM': 10,
    }

@admin.register(SpecialEvent)
class SpecialEventAdmin(LeafletGeoAdmin):
    """Admin interface for special events with location mapping"""
    
    list_display = [
        'name', 'event_type', 'start_datetime', 'end_datetime',
        'impact_radius_km', 'base_multiplier', 'is_active'
    ]
    list_filter = [
        'is_active', 'event_type', 'start_datetime'
    ]
    search_fields = ['name', 'description', 'venue_name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Event Information', {
            'fields': (
                'name', 'description', 'event_type',
                'venue_name', 'organizer'
            )
        }),
        ('Schedule', {
            'fields': ('start_datetime', 'end_datetime')
        }),
        ('Location & Impact', {
            'fields': ('location', 'impact_radius_km', 'affected_zones'),
            'classes': ('wide',)
        }),
        ('Pricing', {
            'fields': (
                'base_multiplier', 'peak_multiplier',
                'peak_start_offset', 'peak_end_offset'
            )
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        })
    )
    
    filter_horizontal = ['affected_zones']
```

---

## Phase 5: Testing & Validation

### 5.1 Comprehensive Test Suite
```python
# pricing/tests/test_geodjango.py
from django.test import TestCase
from django.contrib.gis.geos import Polygon, Point
from decimal import Decimal
from pricing.models_geodjango import PricingZone, SpecialEvent

class GeoDjangoTestCase(TestCase):
    def setUp(self):
        """Create test zones with various shapes"""
        
        # Simple rectangular zone (Victoria Island)
        vi_polygon = Polygon([
            (3.4000, 6.4200),  # Bottom-left
            (3.4350, 6.4200),  # Bottom-right
            (3.4350, 6.4450),  # Top-right
            (3.4000, 6.4450),  # Top-left
            (3.4000, 6.4200),  # Close
        ], srid=4326)
        
        self.vi_zone = PricingZone.objects.create(
            name="Victoria Island",
            city="Lagos",
            boundary=vi_polygon,
            base_multiplier=Decimal('1.300'),
            is_premium_zone=True
        )
        
        # Complex shaped zone (Irregular mainland area)
        mainland_polygon = Polygon([
            (3.3000, 6.4500),
            (3.5000, 6.4500),
            (3.5000, 6.6000),
            (3.4000, 6.6000),
            (3.4000, 6.5500),
            (3.3000, 6.5500),
            (3.3000, 6.4500),
        ], srid=4326)
        
        self.mainland_zone = PricingZone.objects.create(
            name="Lagos Mainland",
            city="Lagos",
            boundary=mainland_polygon,
            base_multiplier=Decimal('1.000'),
            is_premium_zone=False
        )
    
    def test_zone_detection_accuracy(self):
        """Test point-in-polygon detection"""
        
        # Test points in Victoria Island
        vi_point = Point(3.4150, 6.4350, srid=4326)
        self.assertTrue(self.vi_zone.boundary.contains(vi_point))
        
        # Test points in Mainland
        mainland_point = Point(3.3800, 6.5200, srid=4326)
        self.assertTrue(self.mainland_zone.boundary.contains(mainland_point))
        
        # Test point outside both zones
        outside_point = Point(3.2000, 6.3000, srid=4326)
        self.assertFalse(self.vi_zone.boundary.contains(outside_point))
        self.assertFalse(self.mainland_zone.boundary.contains(outside_point))
    
    def test_zone_area_calculation(self):
        """Test automatic area calculation"""
        self.assertIsNotNone(self.vi_zone.area_sq_km)
        self.assertGreater(self.vi_zone.area_sq_km, 0)
    
    def test_distance_calculation(self):
        """Test distance calculations"""
        distance = self.vi_zone.distance_to_point(
            Decimal('6.4350'), Decimal('3.4150')
        )
        self.assertIsInstance(distance, Decimal)
        self.assertGreaterEqual(distance, 0)
    
    def test_special_event_impact(self):
        """Test special event location impact"""
        event_location = Point(3.4180, 6.4180, srid=4326)
        
        event = SpecialEvent.objects.create(
            name="Test Concert",
            event_type="concert",
            start_datetime=timezone.now(),
            end_datetime=timezone.now() + timedelta(hours=4),
            location=event_location,
            impact_radius_km=Decimal('2.0'),
            base_multiplier=Decimal('1.5')
        )
        
        # Test if nearby location is affected
        nearby_affected = event.affects_location(
            Decimal('6.4200'), Decimal('3.4200')
        )
        self.assertTrue(nearby_affected)
        
        # Test if far location is not affected
        far_not_affected = event.affects_location(
            Decimal('6.6000'), Decimal('3.6000')
        )
        self.assertFalse(far_not_affected)
```

### 5.2 Performance Benchmarks
```python
# pricing/management/commands/benchmark_geodjango.py
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from decimal import Decimal
import time
import random

class Command(BaseCommand):
    help = 'Benchmark GeoDjango vs simplified coordinate performance'
    
    def handle(self, *args, **options):
        from pricing.models_geodjango import PricingZone
        
        # Generate random test points
        test_points = []
        for _ in range(1000):
            lat = Decimal(str(random.uniform(6.3, 6.7)))
            lng = Decimal(str(random.uniform(3.2, 3.6)))
            test_points.append((lat, lng))
        
        # Benchmark zone detection
        zones = PricingZone.objects.all()
        
        start_time = time.time()
        for lat, lng in test_points:
            for zone in zones:
                zone.contains_point(lat, lng)
        end_time = time.time()
        
        avg_time = (end_time - start_time) / len(test_points)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'GeoDjango Performance: {avg_time:.4f}s per point detection'
            )
        )
        
        # Test spatial queries
        test_point = Point(3.4150, 6.4350, srid=4326)
        
        start_time = time.time()
        zones_containing = PricingZone.objects.filter(
            boundary__contains=test_point
        )
        list(zones_containing)  # Force evaluation
        end_time = time.time()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Spatial Query Performance: {end_time - start_time:.4f}s'
            )
        )
```

---

## Phase 6: Deployment Strategy

### 6.1 Blue-Green Deployment
```bash
# Deploy GeoDjango version alongside current system
# Create new database
createdb vip_ride_geodjango_v2

# Run migrations on new database
python manage.py migrate --database=geodjango

# Test thoroughly
python manage.py test --settings=settings_geodjango

# Switch traffic gradually
```

### 6.2 Rollback Plan
```python
# pricing/management/commands/rollback_geodjango.py
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Rollback to simplified coordinate system if needed'
    
    def handle(self, *args, **options):
        # Export GeoDjango data to simplified format
        from pricing.models_geodjango import PricingZone as GeoPricingZone
        from pricing.models import PricingZone as SimplePricingZone
        
        for geo_zone in GeoPricingZone.objects.all():
            # Extract bounds from polygon
            bounds = geo_zone.boundary.extent  # (min_lng, min_lat, max_lng, max_lat)
            
            SimplePricingZone.objects.create(
                name=geo_zone.name,
                description=geo_zone.description,
                city=geo_zone.city,
                country=geo_zone.country,
                min_latitude=Decimal(str(bounds[1])),
                max_latitude=Decimal(str(bounds[3])),
                min_longitude=Decimal(str(bounds[0])),
                max_longitude=Decimal(str(bounds[2])),
                base_multiplier=geo_zone.base_multiplier,
                is_premium_zone=geo_zone.is_premium_zone,
                surge_enabled=geo_zone.surge_enabled,
                max_surge_multiplier=geo_zone.max_surge_multiplier,
                is_active=geo_zone.is_active,
            )
        
        self.stdout.write(
            self.style.SUCCESS('Rollback data prepared successfully!')
        )
```

---

## Benefits of GeoDjango Upgrade

### Enhanced Precision
- **Accurate Boundaries**: Complex zone shapes instead of rectangles
- **Better Coverage**: No gaps or overlaps in coverage areas
- **Precise Distance**: Accurate distance calculations for surge pricing

### Advanced Features
- **Spatial Queries**: Fast database-level spatial operations
- **Event Impact**: Circular impact zones for special events
- **Route Optimization**: Better path planning within zones

### Business Value
- **Revenue Optimization**: More accurate pricing in premium areas
- **Customer Satisfaction**: Fair pricing based on precise location
- **Operational Efficiency**: Better driver allocation within zones

### Technical Advantages
- **Scalability**: Optimized spatial indexes for performance
- **Standards Compliance**: OGC-compliant spatial operations
- **Future-Proof**: Foundation for advanced GIS features

---

## Timeline & Resources

### Development Timeline
- **Week 1-2**: Infrastructure setup and testing
- **Week 3-4**: Model development and migration scripts
- **Week 5-6**: Admin interface and testing
- **Week 7-8**: Performance optimization and deployment

### Required Resources
- **1 Backend Developer**: GeoDjango implementation
- **1 DevOps Engineer**: Infrastructure and deployment
- **1 QA Tester**: Comprehensive testing
- **1 Geographic Analyst**: Zone boundary definition (optional)

### Budget Considerations
- **Infrastructure**: PostGIS hosting costs
- **Development**: 160 development hours
- **Testing**: 40 testing hours
- **Deployment**: 24 hours for cutover

---

This upgrade guide provides a comprehensive path from the current simplified coordinate system to a full GeoDjango implementation, ensuring enhanced precision while maintaining system reliability and performance.
