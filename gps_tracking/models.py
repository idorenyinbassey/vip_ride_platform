"""
GPS Tracking Models for VIP Ride-Hailing Platform
Includes real-time location tracking, geofencing, and VIP encryption
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import json
import math
import uuid
from decimal import Decimal

User = get_user_model()


class GPSLocationManager(models.Manager):
    """Custom manager for GPS locations with encryption support"""
    
    def create_encrypted_location(self, user, latitude, longitude, **kwargs):
        """Create location with VIP encryption if user is VIP tier"""
        location = self.model(user=user, **kwargs)
        
        if hasattr(user, 'tier') and user.tier == 'VIP':
            location.set_encrypted_coordinates(latitude, longitude)
        else:
            location.latitude = latitude
            location.longitude = longitude
            
        location.save()
        return location


class GPSLocation(models.Model):
    """Real-time GPS location tracking with VIP encryption"""
    
    ACCURACY_CHOICES = [
        ('HIGH', 'High (0-10m)'),
        ('MEDIUM', 'Medium (10-50m)'),
        ('LOW', 'Low (50m+)'),
        ('UNKNOWN', 'Unknown'),
    ]
    
    LOCATION_SOURCE_CHOICES = [
        ('GPS', 'GPS Satellite'),
        ('NETWORK', 'Network/WiFi'),
        ('PASSIVE', 'Passive Location'),
        ('FUSED', 'Fused Location'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='gps_locations'
    )
    
    # Standard coordinates (for Normal/Premium users)
    latitude = models.DecimalField(
        max_digits=10, decimal_places=7, null=True, blank=True,
        validators=[MinValueValidator(-90), MaxValueValidator(90)]
    )
    longitude = models.DecimalField(
        max_digits=10, decimal_places=7, null=True, blank=True,
        validators=[MinValueValidator(-180), MaxValueValidator(180)]
    )
    
    # Encrypted coordinates (for VIP users)
    encrypted_coordinates = models.TextField(null=True, blank=True)
    encryption_key_hash = models.CharField(
        max_length=64, null=True, blank=True
    )
    
    # Location metadata
    accuracy_meters = models.FloatField(
        validators=[MinValueValidator(0)],
        help_text="GPS accuracy in meters"
    )
    accuracy_level = models.CharField(
        max_length=10, choices=ACCURACY_CHOICES, default='UNKNOWN'
    )
    altitude = models.FloatField(null=True, blank=True)
    bearing = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(360)],
        help_text="Direction in degrees (0-360)"
    )
    speed_kmh = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(0)],
        help_text="Speed in km/h"
    )
    
    # Technical details
    location_source = models.CharField(
        max_length=10, choices=LOCATION_SOURCE_CHOICES, default='GPS'
    )
    device_timestamp = models.DateTimeField()
    server_timestamp = models.DateTimeField(auto_now_add=True)
    battery_level = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    is_mock_location = models.BooleanField(default=False)
    
    # Ride context
    ride = models.ForeignKey(
        'rides.Ride',
        on_delete=models.CASCADE,
        related_name='gps_locations',
        null=True,
        blank=True,
    )
    
    # Offline support
    is_offline_buffered = models.BooleanField(default=False)
    sync_status = models.CharField(
        max_length=20,
        choices=[
            ('SYNCED', 'Synced'),
            ('PENDING', 'Pending Sync'),
            ('FAILED', 'Sync Failed'),
        ],
        default='SYNCED'
    )
    
    objects = GPSLocationManager()
    
    class Meta:
        db_table = 'gps_locations'
        indexes = [
            models.Index(fields=['user', '-server_timestamp']),
            models.Index(fields=['ride', '-server_timestamp']),
            models.Index(fields=['device_timestamp']),
            models.Index(fields=['sync_status']),
        ]
        ordering = ['-server_timestamp']
    
    def __str__(self):
        return f"GPS Location for {self.user} at {self.server_timestamp}"
    
    def _get_encryption_key(self, user_key):
        """Generate encryption key from user-specific data"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=str(
                getattr(self, 'user_id', None) or getattr(self.user, 'pk', '')
            ).encode(),
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(user_key.encode()))
        return Fernet(key)
    
    def set_encrypted_coordinates(self, lat_value, lng_value):
        """Encrypt coordinates for VIP users"""
        if getattr(self.user, 'tier', None) != 'VIP':
            raise ValueError("Encryption only available for VIP users")
        
        # Use user-specific encryption key
        _joined = getattr(self.user, 'date_joined', timezone.now())
        _uid = getattr(self, 'user_id', None) or getattr(self.user, 'pk', '')
        user_key = (f"vip_gps_{_uid}_" f"{_joined.isoformat()}")
        cipher = self._get_encryption_key(user_key)
        
        # Encrypt coordinates
        coordinates_data = {
            'lat': float(lat_value),
            'lng': float(lng_value),
            'timestamp': timezone.now().isoformat()
        }
        
        encrypted_data = cipher.encrypt(json.dumps(coordinates_data).encode())
        self.encrypted_coordinates = base64.urlsafe_b64encode(
            encrypted_data
        ).decode()
        self.encryption_key_hash = base64.urlsafe_b64encode(
            hashes.Hash(hashes.SHA256()).finalize()
        ).decode()[:64]
    
    def get_decrypted_coordinates(self):
        """Decrypt coordinates for VIP users"""
        if not self.encrypted_coordinates:
            return self.latitude, self.longitude

        _joined = getattr(self.user, 'date_joined', timezone.now())
        _uid = getattr(self, 'user_id', None) or getattr(self.user, 'pk', '')
        user_key = (f"vip_gps_{_uid}_" f"{_joined.isoformat()}")
        cipher = self._get_encryption_key(user_key)

        try:
            encrypted_data = base64.urlsafe_b64decode(
                self.encrypted_coordinates.encode()
            )
            decrypted_data = cipher.decrypt(encrypted_data)
            coordinates = json.loads(decrypted_data.decode())
            return coordinates['lat'], coordinates['lng']
        except Exception:
            return None, None
    
    @property
    def coordinates(self):
        """Get coordinates (encrypted or plain)"""
        if self.encrypted_coordinates:
            return self.get_decrypted_coordinates()
        return self.latitude, self.longitude
    
    @property
    def point(self):
        """Get coordinates as dict"""
        lat, lng = self.coordinates
        if lat is not None and lng is not None:
            return {
                'latitude': float(lat),
                'longitude': float(lng)
            }
        return None


class GeofenceZone(models.Model):
    """Geofencing zones for pickup/dropoff areas"""
    
    ZONE_TYPE_CHOICES = [
        ('PICKUP', 'Pickup Zone'),
        ('DROPOFF', 'Dropoff Zone'),
        ('RESTRICTED', 'Restricted Area'),
        ('AIRPORT', 'Airport Zone'),
        ('HOTEL', 'Hotel Zone'),
        ('VIP_ONLY', 'VIP Only Zone'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    zone_type = models.CharField(max_length=15, choices=ZONE_TYPE_CHOICES)
    
    # Geographic boundary (stored as polygon coordinates JSON)
    boundary_coordinates = models.JSONField(
        help_text="Polygon boundary as array of [lat, lng] coordinates"
    )
    center_latitude = models.DecimalField(
        max_digits=10, decimal_places=7,
        validators=[MinValueValidator(-90), MaxValueValidator(90)]
    )
    center_longitude = models.DecimalField(
        max_digits=10, decimal_places=7,
        validators=[MinValueValidator(-180), MaxValueValidator(180)]
    )
    radius_meters = models.FloatField(
        validators=[MinValueValidator(0)],
        help_text="Approximate radius in meters"
    )
    
    # Zone configuration
    is_active = models.BooleanField(default=True)
    requires_vip = models.BooleanField(default=False)
    max_wait_time_minutes = models.IntegerField(
        default=10,
        validators=[MinValueValidator(1), MaxValueValidator(60)]
    )
    priority_level = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    
    # Business rules
    surge_multiplier = models.DecimalField(
        max_digits=3, decimal_places=2, default=Decimal('1.00'),
        validators=[MinValueValidator(1.0), MaxValueValidator(5.0)]
    )
    minimum_driver_rating = models.DecimalField(
        max_digits=3, decimal_places=2, default=Decimal('0.00'),
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )
    
    # Metadata
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'geofence_zones'
        indexes = [
            models.Index(fields=['zone_type', 'is_active']),
            models.Index(fields=['requires_vip']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.zone_type})"
    
    def contains_point(self, point_or_latitude, longitude=None):
        """Check if point is within geofence boundary using ray casting.
        Accepts either a dict {'latitude','longitude'} or latitude, longitude floats.
        """
        if not self.boundary_coordinates:
            return False

        # Support both dict and separate args
        if longitude is None and isinstance(point_or_latitude, dict):
            latitude = float(point_or_latitude.get('latitude'))
            longitude = float(point_or_latitude.get('longitude'))
        else:
            latitude = float(point_or_latitude)
            longitude = float(longitude)

        x, y = float(longitude), float(latitude)
        polygon = self.boundary_coordinates
        
        n = len(polygon)
        inside = False
        
        p1x, p1y = polygon[0]
        for i in range(1, n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        xinters = None
                        if p1y != p2y:
                            xinters = ((y - p1y) * (p2x - p1x) /
                                       (p2y - p1y) + p1x)
                        if p1x == p2x or (xinters and x <= xinters):
                            inside = not inside
            p1x, p1y = p2x, p2y
        
        return inside
    
    def distance_to_point(self, latitude, longitude):
        """Calculate distance from center to point in meters"""
        return self._calculate_distance(
            float(self.center_latitude), float(self.center_longitude),
            latitude, longitude
        )
    
    def _calculate_distance(self, lat1, lng1, lat2, lng2):
        """Calculate distance using Haversine formula"""
        R = 6371000  # Earth's radius in meters
        
        dlat = math.radians(lat2 - lat1)
        dlng = math.radians(lng2 - lng1)
        
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlng / 2) ** 2)
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        
        return distance


class GeofenceEvent(models.Model):
    """Track geofence entry/exit events"""
    
    EVENT_TYPE_CHOICES = [
        ('ENTER', 'Entered Zone'),
        ('EXIT', 'Exited Zone'),
        ('DWELL', 'Dwelling in Zone'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='geofence_events'
    )
    geofence_zone = models.ForeignKey(
        GeofenceZone, on_delete=models.CASCADE, related_name='events'
    )
    gps_location = models.ForeignKey(
        GPSLocation, on_delete=models.CASCADE, related_name='geofence_events'
    )
    
    event_type = models.CharField(max_length=10, choices=EVENT_TYPE_CHOICES)
    event_timestamp = models.DateTimeField(auto_now_add=True)
    
    # Event context
    ride = models.ForeignKey(
        'rides.Ride', on_delete=models.CASCADE,
        related_name='geofence_events', null=True, blank=True
    )
    duration_seconds = models.IntegerField(
        null=True, blank=True,
        help_text="Duration in zone (for DWELL events)"
    )
    
    # Metadata
    triggered_actions = models.JSONField(
        default=list,
        help_text="Actions triggered by this event"
    )
    
    class Meta:
        db_table = 'geofence_events'
        indexes = [
            models.Index(fields=['user', '-event_timestamp']),
            models.Index(fields=['geofence_zone', '-event_timestamp']),
            models.Index(fields=['ride', '-event_timestamp']),
            models.Index(fields=['event_type']),
        ]
        ordering = ['-event_timestamp']
    
    def __str__(self):
        return f"{self.user} {self.event_type} {self.geofence_zone.name}"


class RouteOptimization(models.Model):
    """Store route optimization data and ETA calculations"""
    
    ROUTE_STATUS_CHOICES = [
        ('CALCULATING', 'Calculating Route'),
        ('OPTIMIZED', 'Route Optimized'),
        ('ACTIVE', 'Route Active'),
        ('COMPLETED', 'Route Completed'),
        ('CANCELLED', 'Route Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ride = models.OneToOneField(
        'rides.Ride', on_delete=models.CASCADE, related_name='route_optimization'
    )
    
    # Route points (stored as lat/lng coordinates)
    pickup_latitude = models.DecimalField(
        max_digits=10, decimal_places=7,
        validators=[MinValueValidator(-90), MaxValueValidator(90)]
    )
    pickup_longitude = models.DecimalField(
        max_digits=10, decimal_places=7,
        validators=[MinValueValidator(-180), MaxValueValidator(180)]
    )
    dropoff_latitude = models.DecimalField(
        max_digits=10, decimal_places=7,
        validators=[MinValueValidator(-90), MaxValueValidator(90)]
    )
    dropoff_longitude = models.DecimalField(
        max_digits=10, decimal_places=7,
        validators=[MinValueValidator(-180), MaxValueValidator(180)]
    )
    
    waypoints = models.JSONField(
        default=list,
        help_text="Intermediate waypoints as [lat, lng] pairs"
    )
    
    # Route data
    optimized_route = models.JSONField(
        default=dict,
        help_text="Google Maps route response"
    )
    route_polyline = models.TextField(
        help_text="Encoded polyline for route visualization"
    )
    
    # Distance and time estimates
    distance_meters = models.IntegerField(
        validators=[MinValueValidator(0)]
    )
    duration_seconds = models.IntegerField(
        validators=[MinValueValidator(0)]
    )
    duration_in_traffic_seconds = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(0)]
    )
    
    # ETA tracking
    original_eta = models.DateTimeField()
    current_eta = models.DateTimeField()
    eta_accuracy_percentage = models.FloatField(
        default=85.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Route status
    status = models.CharField(
        max_length=15, choices=ROUTE_STATUS_CHOICES, default='CALCULATING'
    )
    traffic_level = models.CharField(
        max_length=10,
        choices=[
            ('LOW', 'Low Traffic'),
            ('MODERATE', 'Moderate Traffic'),
            ('HEAVY', 'Heavy Traffic'),
            ('SEVERE', 'Severe Traffic'),
        ],
        default='MODERATE'
    )
    
    # Optimization metadata
    algorithm_used = models.CharField(
        max_length=50, default='google_maps_api',
        help_text="Route optimization algorithm used"
    )
    calculation_time_ms = models.IntegerField(
        null=True, blank=True,
        help_text="Time taken to calculate route in milliseconds"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'route_optimizations'
        indexes = [
            models.Index(fields=['ride']),
            models.Index(fields=['status']),
            models.Index(fields=['-updated_at']),
        ]
    
    def __str__(self):
        return f"Route for {self.ride} - {self.status}"
    
    @property
    def pickup_point(self):
        """Get pickup point as dict"""
        return {
            'latitude': float(self.pickup_latitude),
            'longitude': float(self.pickup_longitude)
        }
    
    @property
    def dropoff_point(self):
        """Get dropoff point as dict"""
        return {
            'latitude': float(self.dropoff_latitude),
            'longitude': float(self.dropoff_longitude)
        }
    
    def update_eta(self, current_location_point):
        """Update ETA based on current location and traffic"""
        # This would integrate with Google Maps API for real-time updates
        pass
    
    @property
    def estimated_arrival_time(self):
        """Get current ETA"""
        return self.current_eta
    
    @property
    def is_delayed(self):
        """Check if ride is delayed compared to original ETA"""
        return self.current_eta > self.original_eta


class OfflineGPSBuffer(models.Model):
    """Buffer GPS data when device is offline"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='offline_gps_buffer')
    device_id = models.CharField(max_length=100)
    
    # Buffered location data (legacy JSON for backward compatibility)
    buffered_locations = models.JSONField(
        default=list,
        help_text="Array of GPS locations recorded offline (legacy)"
    )
    
    # Buffer metadata
    start_timestamp = models.DateTimeField()
    end_timestamp = models.DateTimeField()
    total_locations = models.IntegerField(default=0)
    
    # Sync status
    is_synced = models.BooleanField(default=False)
    sync_timestamp = models.DateTimeField(null=True, blank=True)
    sync_errors = models.JSONField(
        default=list,
        help_text="Errors encountered during sync"
    )
    
    # Technical details
    app_version = models.CharField(max_length=20)
    device_info = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'offline_gps_buffers'
        indexes = [
            models.Index(fields=['user', 'is_synced']),
            models.Index(fields=['device_id']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"Offline GPS Buffer for {self.user} ({self.total_locations} locations)"
    
    def process_buffered_locations(self):
        """Process and create GPSLocation objects from buffered data"""
        if self.is_synced:
            return
        
        created_locations = []
        errors = []
        
        # Prefer normalized related rows if present
        # Access reverse relation via getattr to satisfy static analyzers
        _points_manager = (
            getattr(self, 'buffered_points', None)
            or getattr(self, 'bufferedlocation_set', None)
        )
        normalized_points = []
        if _points_manager is not None:
            normalized_points = list(_points_manager.all().values(
                'latitude', 'longitude', 'timestamp', 'accuracy',
                'altitude', 'bearing', 'speed_kmh', 'battery_level'
            ))
        locations_iter = normalized_points or self.buffered_locations

        for location_data in locations_iter:
            try:
                gps_location = GPSLocation.objects.create(
                    user=self.user,
                    latitude=location_data.get('latitude'),
                    longitude=location_data.get('longitude'),
                    accuracy_meters=(
                        location_data.get('accuracy')
                        or location_data.get('accuracy_meters', 0)
                    ),
                    device_timestamp=location_data.get('timestamp'),
                    is_offline_buffered=True,
                    sync_status='SYNCED'
                )
                created_locations.append(gps_location.id)
            except Exception as e:
                errors.append({
                    'location_data': location_data,
                    'error': str(e)
                })
        
        self.is_synced = len(errors) == 0
        self.sync_timestamp = timezone.now()
        self.sync_errors = errors
        self.save()
        
        return created_locations, errors


class BufferedLocation(models.Model):
    """Normalized buffered GPS point linked to OfflineGPSBuffer"""
    buffer = models.ForeignKey(
        OfflineGPSBuffer,
        on_delete=models.CASCADE,
        related_name='buffered_points'
    )
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField()
    accuracy = models.FloatField(default=0)
    altitude = models.FloatField(null=True, blank=True)
    bearing = models.FloatField(null=True, blank=True)
    speed_kmh = models.FloatField(null=True, blank=True)
    battery_level = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'buffered_locations'
        indexes = [
            models.Index(fields=['buffer']),
            models.Index(fields=['timestamp']),
        ]
