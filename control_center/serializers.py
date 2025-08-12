"""
Control Center Serializers
Secure serializers for emergency and monitoring systems
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
import re

from .models import (
    EmergencyIncident, VIPMonitoringSession, ControlOperator,
    IncidentResponse, SOSConfiguration,
    IncidentType, IncidentPriority, IncidentStatus
)

User = get_user_model()


class EmergencyIncidentSerializer(serializers.ModelSerializer):
    """Emergency incident serializer with security controls"""
    
    user_name = serializers.CharField(
        source='user.get_full_name', read_only=True
    )
    driver_name = serializers.CharField(
        source='driver.get_full_name', read_only=True
    )
    operator_name = serializers.CharField(
        source='assigned_operator.get_full_name', read_only=True
    )
    response_time_minutes = serializers.ReadOnlyField()
    is_critical = serializers.ReadOnlyField()
    requires_immediate_response = serializers.ReadOnlyField()
    
    class Meta:
        model = EmergencyIncident
        fields = [
            'id', 'incident_type', 'priority', 'status', 'user', 'user_name',
            'driver', 'driver_name', 'ride', 'vehicle',
            'incident_latitude', 'incident_longitude', 'address', 'landmark',
            'description', 'automated_trigger', 'user_triggered',
            'assigned_operator', 'operator_name', 'response_team_type',
            'response_team_contacted', 'response_time_seconds',
            'response_time_minutes', 'emergency_contacts_notified',
            'police_notified', 'medical_services_notified',
            'resolution_notes', 'resolved_by', 'is_critical',
            'requires_immediate_response', 'created_at',
            'first_response_at', 'resolved_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user_name', 'driver_name', 'operator_name',
            'response_time_minutes', 'is_critical',
            'requires_immediate_response', 'created_at', 'updated_at'
        ]
    
    def validate_incident_latitude(self, value):
        """Validate latitude"""
        if not -90 <= value <= 90:
            raise serializers.ValidationError(
                "Latitude must be between -90 and 90 degrees"
            )
        return value
    
    def validate_incident_longitude(self, value):
        """Validate longitude"""
        if not -180 <= value <= 180:
            raise serializers.ValidationError(
                "Longitude must be between -180 and 180 degrees"
            )
        return value
    
    def validate_description(self, value):
        """Validate description"""
        if len(value.strip()) < 10:
            raise serializers.ValidationError(
                "Description must be at least 10 characters"
            )
        return value.strip()
    
    def validate(self, attrs):
        """Cross-field validation"""
        # Ensure either user_triggered or automated_trigger is True
        user_triggered = attrs.get('user_triggered', True)
        automated_trigger = attrs.get('automated_trigger', False)
        
        if not user_triggered and not automated_trigger:
            raise serializers.ValidationError(
                "Either user_triggered or automated_trigger must be True"
            )
        
        return attrs


class EmergencyIncidentCreateSerializer(EmergencyIncidentSerializer):
    """Serializer for creating emergency incidents"""
    
    class Meta(EmergencyIncidentSerializer.Meta):
        fields = [
            'incident_type', 'priority', 'user', 'driver', 'ride',
            'vehicle', 'incident_latitude', 'incident_longitude',
            'address', 'landmark', 'description', 'automated_trigger',
            'user_triggered'
        ]
    
    def create(self, validated_data):
        """Create incident with automatic priority assignment"""
        # Auto-assign critical priority for certain incident types
        critical_types = [
            IncidentType.SOS,
            IncidentType.PANIC,
            IncidentType.ACCIDENT,
            IncidentType.MEDICAL
        ]
        
        if validated_data['incident_type'] in critical_types:
            validated_data['priority'] = IncidentPriority.CRITICAL
        
        return super().create(validated_data)


class VIPMonitoringSessionSerializer(serializers.ModelSerializer):
    """VIP monitoring session serializer"""
    
    user_name = serializers.CharField(
        source='user.get_full_name', read_only=True
    )
    driver_name = serializers.CharField(
        source='driver.get_full_name', read_only=True
    )
    operator_name = serializers.CharField(
        source='assigned_operator.get_full_name', read_only=True
    )
    is_overdue_checkin = serializers.ReadOnlyField()
    
    class Meta:
        model = VIPMonitoringSession
        fields = [
            'id', 'user', 'user_name', 'ride', 'driver', 'driver_name',
            'vehicle', 'monitoring_level', 'assigned_operator',
            'operator_name', 'planned_route', 'current_latitude',
            'current_longitude', 'last_location_update', 'is_active',
            'route_deviation_alert', 'speed_alert', 'duration_alert',
            'session_start', 'session_end', 'estimated_arrival',
            'panic_button_enabled', 'auto_check_in_enabled',
            'check_in_interval_minutes', 'last_check_in',
            'is_overdue_checkin', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user_name', 'driver_name', 'operator_name',
            'is_overdue_checkin', 'created_at', 'updated_at'
        ]
    
    def validate_current_latitude(self, value):
        """Validate latitude"""
        if value is not None and not -90 <= value <= 90:
            raise serializers.ValidationError(
                "Latitude must be between -90 and 90 degrees"
            )
        return value
    
    def validate_current_longitude(self, value):
        """Validate longitude"""
        if value is not None and not -180 <= value <= 180:
            raise serializers.ValidationError(
                "Longitude must be between -180 and 180 degrees"
            )
        return value
    
    def validate_check_in_interval_minutes(self, value):
        """Validate check-in interval"""
        if value < 5 or value > 60:
            raise serializers.ValidationError(
                "Check-in interval must be between 5 and 60 minutes"
            )
        return value


class ControlOperatorSerializer(serializers.ModelSerializer):
    """Control operator serializer"""
    
    operator_name = serializers.CharField(
        source='user.get_full_name', read_only=True
    )
    supervisor_name = serializers.CharField(
        source='supervisor.user.get_full_name', read_only=True
    )
    
    class Meta:
        model = ControlOperator
        fields = [
            'id', 'user', 'operator_name', 'operator_id',
            'security_clearance_level', 'can_handle_emergencies',
            'can_contact_authorities', 'can_escalate_incidents',
            'can_monitor_vip', 'is_active', 'is_on_duty',
            'current_shift_start', 'total_incidents_handled',
            'average_response_time_seconds', 'successful_resolutions',
            'supervisor', 'supervisor_name', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'operator_name', 'supervisor_name', 'total_incidents_handled',
            'average_response_time_seconds', 'successful_resolutions',
            'created_at', 'updated_at'
        ]
    
    def validate_operator_id(self, value):
        """Validate operator ID format"""
        if not re.match(r'^OP[0-9]{4,6}$', value):
            raise serializers.ValidationError(
                "Operator ID must be in format OP#### (e.g., OP0001)"
            )
        return value


class IncidentResponseSerializer(serializers.ModelSerializer):
    """Incident response serializer"""
    
    operator_name = serializers.CharField(
        source='operator.user.get_full_name', read_only=True
    )
    
    class Meta:
        model = IncidentResponse
        fields = [
            'id', 'incident', 'action_type', 'description', 'operator',
            'operator_name', 'authority_contacted', 'authority_reference',
            'team_dispatched', 'estimated_arrival_time', 'created_at'
        ]
        read_only_fields = ['id', 'operator_name', 'created_at']
    
    def validate_description(self, value):
        """Validate response description"""
        if len(value.strip()) < 5:
            raise serializers.ValidationError(
                "Response description must be at least 5 characters"
            )
        return value.strip()


class SOSConfigurationSerializer(serializers.ModelSerializer):
    """SOS configuration serializer"""
    
    class Meta:
        model = SOSConfiguration
        fields = [
            'id', 'user_tier', 'auto_response_enabled',
            'max_response_time_seconds', 'escalation_time_seconds',
            'auto_contact_police', 'auto_contact_medical',
            'requires_supervisor_approval', 'real_time_monitoring',
            'gps_tracking_frequency_seconds', 'route_deviation_alert',
            'notify_emergency_contacts', 'max_emergency_contacts',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_max_response_time_seconds(self, value):
        """Validate response time"""
        if value < 30 or value > 1800:  # 30 seconds to 30 minutes
            raise serializers.ValidationError(
                "Response time must be between 30 and 1800 seconds"
            )
        return value
    
    def validate_gps_tracking_frequency_seconds(self, value):
        """Validate GPS tracking frequency"""
        if value < 10 or value > 300:  # 10 seconds to 5 minutes
            raise serializers.ValidationError(
                "GPS tracking frequency must be between 10 and 300 seconds"
            )
        return value
    
    def validate_max_emergency_contacts(self, value):
        """Validate emergency contacts limit"""
        if value < 1 or value > 10:
            raise serializers.ValidationError(
                "Emergency contacts must be between 1 and 10"
            )
        return value


class SOSTriggerSerializer(serializers.Serializer):
    """Serializer for SOS trigger requests"""
    
    incident_type = serializers.ChoiceField(
        choices=IncidentType.choices,
        default=IncidentType.SOS
    )
    latitude = serializers.DecimalField(max_digits=10, decimal_places=7)
    longitude = serializers.DecimalField(max_digits=10, decimal_places=7)
    description = serializers.CharField(
        max_length=1000,
        help_text='Description of the emergency'
    )
    ride_id = serializers.UUIDField(required=False, allow_null=True)
    vehicle_id = serializers.UUIDField(required=False, allow_null=True)
    
    def validate_latitude(self, value):
        """Validate latitude"""
        if not -90 <= value <= 90:
            raise serializers.ValidationError(
                "Latitude must be between -90 and 90 degrees"
            )
        return value
    
    def validate_longitude(self, value):
        """Validate longitude"""
        if not -180 <= value <= 180:
            raise serializers.ValidationError(
                "Longitude must be between -180 and 180 degrees"
            )
        return value
    
    def validate_description(self, value):
        """Validate description"""
        if len(value.strip()) < 5:
            raise serializers.ValidationError(
                "Description must be at least 5 characters"
            )
        return value.strip()


class IncidentUpdateSerializer(serializers.Serializer):
    """Serializer for incident status updates"""
    
    status = serializers.ChoiceField(choices=IncidentStatus.choices)
    response_notes = serializers.CharField(
        max_length=1000,
        help_text='Notes about the response action'
    )
    operator_id = serializers.UUIDField(required=False)
    authority_contacted = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True
    )
    team_dispatched = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True
    )
    
    def validate_response_notes(self, value):
        """Validate response notes"""
        if len(value.strip()) < 5:
            raise serializers.ValidationError(
                "Response notes must be at least 5 characters"
            )
        return value.strip()


class MonitoringDashboardSerializer(serializers.Serializer):
    """Serializer for monitoring dashboard data"""
    
    active_incidents = serializers.IntegerField()
    critical_incidents = serializers.IntegerField()
    active_vip_sessions = serializers.IntegerField()
    operators_on_duty = serializers.IntegerField()
    average_response_time = serializers.DecimalField(
        max_digits=8, decimal_places=2
    )
    incidents_today = serializers.IntegerField()
    resolved_today = serializers.IntegerField()
    recent_incidents = EmergencyIncidentSerializer(many=True)
    overdue_checkins = VIPMonitoringSessionSerializer(many=True)
