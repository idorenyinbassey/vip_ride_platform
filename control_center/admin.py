"""
Django Admin Configuration for Control Center App
"""

from django.contrib import admin
from .models import (
    ControlOperator, EmergencyIncident, IncidentResponse,
    VIPMonitoringSession, SOSConfiguration
)


@admin.register(ControlOperator)
class ControlOperatorAdmin(admin.ModelAdmin):
    """Admin for Control Operators"""
    
    list_display = ['user', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(EmergencyIncident)
class EmergencyIncidentAdmin(admin.ModelAdmin):
    """Admin for Emergency Incidents"""
    
    list_display = [
        'user', 'incident_type', 'priority', 'status', 'created_at'
    ]
    list_filter = ['incident_type', 'priority', 'status', 'created_at']
    search_fields = ['user__email', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(IncidentResponse)
class IncidentResponseAdmin(admin.ModelAdmin):
    """Admin for Incident Responses"""
    
    list_display = ['incident', 'operator', 'created_at']
    list_filter = ['created_at']
    search_fields = ['incident__id', 'operator__user__email']
    readonly_fields = ['id', 'created_at']


@admin.register(VIPMonitoringSession)
class VIPMonitoringSessionAdmin(admin.ModelAdmin):
    """Admin for VIP Monitoring Sessions"""
    
    list_display = ['user', 'assigned_operator', 'monitoring_level', 'is_active', 'created_at']
    list_filter = ['is_active', 'monitoring_level', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Session Information', {
            'fields': ('user', 'ride_id', 'driver', 'vehicle_id')
        }),
        ('Monitoring', {
            'fields': ('monitoring_level', 'assigned_operator', 'is_active')
        }),
        ('Location & Route', {
            'fields': ('planned_route', 'current_latitude', 'current_longitude', 'last_location_update')
        }),
        ('Alerts', {
            'fields': ('route_deviation_alert', 'speed_alert', 'duration_alert')
        }),
        ('Emergency Features', {
            'fields': ('panic_button_enabled', 'auto_check_in_enabled', 'check_in_interval_minutes', 'last_check_in')
        }),
        ('Timestamps', {
            'fields': ('session_start', 'session_end', 'estimated_arrival', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(SOSConfiguration)
class SOSConfigurationAdmin(admin.ModelAdmin):
    """Admin for SOS Configuration"""
    
    list_display = ['id', 'created_at']
    list_filter = ['created_at']
    search_fields = []
    readonly_fields = ['id', 'created_at', 'updated_at']
