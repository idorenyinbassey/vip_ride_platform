"""
Django Admin Configuration for GPS Tracking
"""

from django.contrib import admin
# Removed GeoDjango dependency
# from django.contrib.gis.admin import OSMGeoAdmin
from .models import (
    GPSLocation, GeofenceZone, GeofenceEvent, 
    RouteOptimization, OfflineGPSBuffer
)


@admin.register(GPSLocation)
class GPSLocationAdmin(admin.ModelAdmin):
    """Admin for GPS locations"""
    
    list_display = [
        'user', 'accuracy_level', 'location_source', 
        'device_timestamp', 'server_timestamp', 'ride'
    ]
    list_filter = [
        'accuracy_level', 'location_source', 'is_offline_buffered',
        'sync_status', 'server_timestamp'
    ]
    search_fields = ['user__username', 'user__email', 'ride__id']
    readonly_fields = [
        'id', 'server_timestamp', 'coordinates', 'encrypted_coordinates'
    ]
    raw_id_fields = ['user', 'ride']
    
    def coordinates(self, obj):
        """Display coordinates (encrypted or plain)"""
        lat, lng = obj.coordinates
        if lat and lng:
            return f"{lat:.6f}, {lng:.6f}"
        return "Encrypted/Unavailable"
    coordinates.short_description = "Coordinates"


@admin.register(GeofenceZone)
class GeofenceZoneAdmin(admin.ModelAdmin):
    """Admin for geofence zones with map"""
    
    list_display = [
        'name', 'zone_type', 'is_active', 'requires_vip',
        'radius_meters', 'priority_level', 'created_at'
    ]
    list_filter = [
        'zone_type', 'is_active', 'requires_vip', 'created_at'
    ]
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    # Map settings
    default_zoom = 12
    map_width = 800
    map_height = 600


@admin.register(GeofenceEvent)
class GeofenceEventAdmin(admin.ModelAdmin):
    """Admin for geofence events"""
    
    list_display = [
        'user', 'geofence_zone', 'event_type',
        'event_timestamp', 'ride', 'duration_seconds'
    ]
    list_filter = [
        'event_type', 'event_timestamp', 'geofence_zone__zone_type'
    ]
    search_fields = [
        'user__username', 'geofence_zone__name', 'ride__id'
    ]
    readonly_fields = [
        'id', 'event_timestamp', 'triggered_actions'
    ]
    raw_id_fields = ['user', 'geofence_zone', 'gps_location', 'ride']


@admin.register(RouteOptimization)
class RouteOptimizationAdmin(admin.ModelAdmin):
    """Admin for route optimizations"""
    
    list_display = [
        'ride', 'status', 'distance_meters', 'duration_seconds',
        'traffic_level', 'created_at'
    ]
    list_filter = [
        'status', 'traffic_level', 'algorithm_used', 'created_at'
    ]
    search_fields = ['ride__id', 'ride__customer__username']
    readonly_fields = [
        'id', 'pickup_coordinates', 'dropoff_coordinates',
        'created_at', 'updated_at'
    ]
    raw_id_fields = ['ride']
    
    def pickup_coordinates(self, obj):
        """Display pickup coordinates"""
        return f"{obj.pickup_point.y:.6f}, {obj.pickup_point.x:.6f}"
    pickup_coordinates.short_description = "Pickup Coordinates"
    
    def dropoff_coordinates(self, obj):
        """Display dropoff coordinates"""
        return f"{obj.dropoff_point.y:.6f}, {obj.dropoff_point.x:.6f}"
    dropoff_coordinates.short_description = "Dropoff Coordinates"


@admin.register(OfflineGPSBuffer)
class OfflineGPSBufferAdmin(admin.ModelAdmin):
    """Admin for offline GPS buffers"""
    
    list_display = [
        'user', 'device_id', 'total_locations', 'is_synced',
        'sync_timestamp', 'created_at'
    ]
    list_filter = [
        'is_synced', 'created_at', 'sync_timestamp', 'app_version'
    ]
    search_fields = ['user__username', 'device_id']
    readonly_fields = [
        'id', 'sync_success_rate', 'created_at'
    ]
    raw_id_fields = ['user']
    
    def sync_success_rate(self, obj):
        """Calculate sync success rate"""
        if obj.total_locations == 0:
            return "100%"
        
        error_count = len(obj.sync_errors)
        success_count = obj.total_locations - error_count
        rate = (success_count / obj.total_locations) * 100
        return f"{rate:.1f}%"
    sync_success_rate.short_description = "Sync Success Rate"
