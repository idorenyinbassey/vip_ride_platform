"""
Django Admin Configuration for Rides App
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import (
    Ride, RideTracking, RideRating, SurgeZone, 
    RideMatchingLog, RideOffer, EmergencyContact, DriverPreference
)


@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    """Admin for Ride model"""
    
    list_display = [
        'id', 'rider', 'driver', 'status', 'ride_type',
        'created_at'
    ]
    list_filter = [
        'status', 'ride_type', 'created_at'
    ]
    search_fields = [
        'id', 'rider__email', 'pickup_address', 'destination_address'
    ]
    readonly_fields = ['id', 'created_at']


@admin.register(RideTracking)
class RideTrackingAdmin(admin.ModelAdmin):
    """Admin for Ride Tracking"""
    
    list_display = ['ride', 'recorded_at']
    list_filter = ['recorded_at']
    search_fields = ['ride__id']
    readonly_fields = ['id', 'recorded_at']


@admin.register(RideRating)
class RideRatingAdmin(admin.ModelAdmin):
    """Admin for Ride Ratings"""
    
    list_display = ['ride', 'rating_type', 'rating', 'created_at']
    list_filter = ['rating_type', 'rating', 'created_at']
    search_fields = ['ride__id', 'comment']
    readonly_fields = ['id', 'created_at']


@admin.register(SurgeZone)
class SurgeZoneAdmin(admin.ModelAdmin):
    """Admin for Surge Zones"""
    
    list_display = ['name', 'surge_multiplier', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at']


@admin.register(RideMatchingLog)
class RideMatchingLogAdmin(admin.ModelAdmin):
    """Admin for Ride Matching Logs"""
    
    list_display = ['ride', 'timestamp']
    list_filter = ['timestamp']
    search_fields = ['ride__id']
    readonly_fields = ['id', 'ride', 'timestamp']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(RideOffer)
class RideOfferAdmin(admin.ModelAdmin):
    """Admin for Ride Offers"""
    
    list_display = ['ride', 'driver', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['ride__id']
    readonly_fields = ['id', 'created_at']


@admin.register(EmergencyContact)
class EmergencyContactAdmin(admin.ModelAdmin):
    """Admin for Emergency Contacts"""
    
    list_display = ['user', 'name', 'relationship', 'is_primary', 'created_at']
    list_filter = ['relationship', 'is_primary', 'created_at']
    search_fields = ['user__email', 'name']
    readonly_fields = ['id', 'created_at']


@admin.register(DriverPreference)
class DriverPreferenceAdmin(admin.ModelAdmin):
    """Admin for Driver Preferences"""
    
    list_display = ['driver', 'updated_at']
    list_filter = ['updated_at']
    search_fields = ['driver__user__email']
    readonly_fields = ['id', 'updated_at']
