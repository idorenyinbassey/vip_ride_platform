"""
Serializers for GPS Tracking API
"""

from rest_framework import serializers
# from django.contrib.gis.geos import Point  # Removed GeoDjango dependency
from django.utils import timezone
from .models import (
    GPSLocation, GeofenceZone, GeofenceEvent, 
    RouteOptimization, OfflineGPSBuffer
)


class GPSLocationSerializer(serializers.ModelSerializer):
    """Serializer for GPS location data"""
    
    coordinates = serializers.SerializerMethodField()
    distance_from_pickup = serializers.SerializerMethodField()
    
    class Meta:
        model = GPSLocation
        fields = [
            'id', 'user', 'coordinates', 'accuracy_meters', 
            'accuracy_level', 'altitude', 'bearing', 'speed_kmh',
            'location_source', 'device_timestamp', 'server_timestamp',
            'battery_level', 'is_mock_location', 'ride',
            'is_offline_buffered', 'sync_status', 'distance_from_pickup'
        ]
        read_only_fields = [
            'id', 'user', 'server_timestamp', 'coordinates', 
            'distance_from_pickup'
        ]
    
    def get_coordinates(self, obj):
        """Get coordinates (encrypted or plain)"""
        lat, lng = obj.coordinates
        if lat is not None and lng is not None:
            return {'latitude': float(lat), 'longitude': float(lng)}
        return None
    
    def get_distance_from_pickup(self, obj):
        """Calculate distance from pickup point if in ride"""
        if not obj.ride or not obj.point:
            return None
        
        try:
            pickup_point = {
                'longitude': obj.ride.pickup_longitude,
                'latitude': obj.ride.pickup_latitude
            }
            distance_meters = obj.point.distance(pickup_point) * 111319.9
            return round(distance_meters, 2)
        except Exception:
            return None


class GPSLocationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating GPS locations"""
    
    latitude = serializers.DecimalField(max_digits=10, decimal_places=7)
    longitude = serializers.DecimalField(max_digits=10, decimal_places=7)
    device_timestamp = serializers.DateTimeField()
    
    class Meta:
        model = GPSLocation
        fields = [
            'latitude', 'longitude', 'accuracy_meters', 'accuracy_level',
            'altitude', 'bearing', 'speed_kmh', 'location_source',
            'device_timestamp', 'battery_level', 'is_mock_location', 'ride'
        ]
    
    def create(self, validated_data):
        """Create GPS location with proper encryption for VIP users"""
        user = self.context['request'].user
        latitude = validated_data.pop('latitude')
        longitude = validated_data.pop('longitude')
        
        return GPSLocation.objects.create_encrypted_location(
            user=user,
            latitude=latitude,
            longitude=longitude,
            **validated_data
        )


class GeofenceZoneSerializer(serializers.ModelSerializer):
    """Serializer for geofence zones"""
    
    center_coordinates = serializers.SerializerMethodField()
    boundary_coordinates = serializers.SerializerMethodField()
    
    class Meta:
        model = GeofenceZone
        fields = [
            'id', 'name', 'zone_type', 'center_coordinates', 
            'boundary_coordinates', 'radius_meters', 'is_active',
            'requires_vip', 'max_wait_time_minutes', 'priority_level',
            'surge_multiplier', 'minimum_driver_rating', 'description',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_center_coordinates(self, obj):
        """Get center point coordinates"""
        return {
            'latitude': obj.center_point.y,
            'longitude': obj.center_point.x
        }
    
    def get_boundary_coordinates(self, obj):
        """Get boundary polygon coordinates"""
        coords = obj.boundary.coords[0]  # Get exterior ring
        return [
            {'latitude': lat, 'longitude': lng} 
            for lng, lat in coords
        ]


class GeofenceEventSerializer(serializers.ModelSerializer):
    """Serializer for geofence events"""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    zone_name = serializers.CharField(source='geofence_zone.name', read_only=True)
    location_coordinates = serializers.SerializerMethodField()
    
    class Meta:
        model = GeofenceEvent
        fields = [
            'id', 'user', 'user_name', 'geofence_zone', 'zone_name',
            'gps_location', 'location_coordinates', 'event_type',
            'event_timestamp', 'ride', 'duration_seconds', 'triggered_actions'
        ]
        read_only_fields = [
            'id', 'user_name', 'zone_name', 'location_coordinates', 
            'event_timestamp'
        ]
    
    def get_location_coordinates(self, obj):
        """Get GPS location coordinates"""
        lat, lng = obj.gps_location.coordinates
        if lat is not None and lng is not None:
            return {'latitude': float(lat), 'longitude': float(lng)}
        return None


class RouteOptimizationSerializer(serializers.ModelSerializer):
    """Serializer for route optimization data"""
    
    pickup_coordinates = serializers.SerializerMethodField()
    dropoff_coordinates = serializers.SerializerMethodField()
    eta_minutes = serializers.SerializerMethodField()
    delay_minutes = serializers.SerializerMethodField()
    
    class Meta:
        model = RouteOptimization
        fields = [
            'id', 'ride', 'pickup_coordinates', 'dropoff_coordinates',
            'waypoints', 'distance_meters', 'duration_seconds',
            'duration_in_traffic_seconds', 'original_eta', 'current_eta',
            'eta_minutes', 'delay_minutes', 'eta_accuracy_percentage',
            'status', 'traffic_level', 'algorithm_used',
            'calculation_time_ms', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'pickup_coordinates', 'dropoff_coordinates',
            'eta_minutes', 'delay_minutes', 'created_at', 'updated_at'
        ]
    
    def get_pickup_coordinates(self, obj):
        """Get pickup point coordinates"""
        return {
            'latitude': obj.pickup_point.y,
            'longitude': obj.pickup_point.x
        }
    
    def get_dropoff_coordinates(self, obj):
        """Get dropoff point coordinates"""
        return {
            'latitude': obj.dropoff_point.y,
            'longitude': obj.dropoff_point.x
        }
    
    def get_eta_minutes(self, obj):
        """Get ETA in minutes from now"""
        if obj.current_eta:
            delta = obj.current_eta - timezone.now()
            return max(0, int(delta.total_seconds() / 60))
        return None
    
    def get_delay_minutes(self, obj):
        """Get delay in minutes compared to original ETA"""
        if obj.original_eta and obj.current_eta:
            delta = obj.current_eta - obj.original_eta
            return int(delta.total_seconds() / 60)
        return 0


class RouteOptimizationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating route optimization"""
    
    pickup_latitude = serializers.DecimalField(max_digits=10, decimal_places=7)
    pickup_longitude = serializers.DecimalField(max_digits=10, decimal_places=7)
    dropoff_latitude = serializers.DecimalField(max_digits=10, decimal_places=7)
    dropoff_longitude = serializers.DecimalField(max_digits=10, decimal_places=7)
    
    class Meta:
        model = RouteOptimization
        fields = [
            'ride', 'pickup_latitude', 'pickup_longitude',
            'dropoff_latitude', 'dropoff_longitude', 'waypoints'
        ]
    
    def create(self, validated_data):
        """Create route optimization with calculated route"""
        pickup_lat = validated_data.pop('pickup_latitude')
        pickup_lng = validated_data.pop('pickup_longitude')
        dropoff_lat = validated_data.pop('dropoff_latitude')
        dropoff_lng = validated_data.pop('dropoff_longitude')
        
        pickup_point = {
            'latitude': float(pickup_lat),
            'longitude': float(pickup_lng)
        }
        dropoff_point = {
            'latitude': float(dropoff_lat),
            'longitude': float(dropoff_lng)
        }
        
        # Create basic route optimization
        route_optimization = RouteOptimization.objects.create(
            pickup_point=pickup_point,
            dropoff_point=dropoff_point,
            distance_meters=1000,  # Placeholder
            duration_seconds=600,   # Placeholder
            original_eta=timezone.now() + timezone.timedelta(minutes=10),
            current_eta=timezone.now() + timezone.timedelta(minutes=10),
            route_polyline='',
            **validated_data
        )
        
        # Trigger async route calculation
        from .tasks import calculate_route_optimization
        calculate_route_optimization.delay(route_optimization.id)
        
        return route_optimization


class OfflineGPSBufferSerializer(serializers.ModelSerializer):
    """Serializer for offline GPS buffer"""
    
    sync_success_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = OfflineGPSBuffer
        fields = [
            'id', 'user', 'device_id', 'start_timestamp', 'end_timestamp',
            'total_locations', 'is_synced', 'sync_timestamp',
            'sync_success_rate', 'app_version', 'created_at'
        ]
        read_only_fields = [
            'id', 'user', 'sync_success_rate', 'created_at'
        ]
    
    def get_sync_success_rate(self, obj):
        """Calculate sync success rate"""
        if obj.total_locations == 0:
            return 100.0
        
        error_count = len(obj.sync_errors)
        success_count = obj.total_locations - error_count
        return round((success_count / obj.total_locations) * 100, 2)


class OfflineGPSSyncSerializer(serializers.Serializer):
    """Serializer for offline GPS synchronization"""
    
    device_id = serializers.CharField(max_length=100)
    app_version = serializers.CharField(max_length=20, default="1.0.0")
    device_info = serializers.DictField(default=dict)
    buffered_locations = serializers.ListField(
        child=serializers.DictField(),
        min_length=1,
        max_length=1000
    )
    
    def validate_buffered_locations(self, value):
        """Validate buffered location data"""
        required_fields = ['latitude', 'longitude', 'timestamp', 'accuracy']
        
        for i, location in enumerate(value):
            for field in required_fields:
                if field not in location:
                    raise serializers.ValidationError(
                        f"Missing required field '{field}' in location {i}"
                    )
            
            # Validate coordinates
            lat = location['latitude']
            lng = location['longitude']
            if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
                raise serializers.ValidationError(
                    f"Invalid coordinates in location {i}"
                )
        
        return value


class GPSTrackingStatsSerializer(serializers.Serializer):
    """Serializer for GPS tracking statistics"""
    
    total_locations = serializers.IntegerField()
    locations_today = serializers.IntegerField()
    average_accuracy = serializers.FloatField()
    high_accuracy_percentage = serializers.FloatField()
    active_rides_count = serializers.IntegerField()
    geofence_events_today = serializers.IntegerField()
    offline_buffers_pending = serializers.IntegerField()
    last_location_timestamp = serializers.DateTimeField(allow_null=True)
