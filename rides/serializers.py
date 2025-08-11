# rides/serializers.py
"""
VIP Ride-Hailing Platform - API Serializers
Serializers for ride workflow system API endpoints
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Ride, RideTracking, RideRating, RideOffer,
    EmergencyContact, SurgeZone, RideMatchingLog, RideStatus
)
from .status_models import RideStatusHistory, WorkflowAction, CancellationRecord
from accounts.models import UserTier

User = get_user_model()


class RideSerializer(serializers.ModelSerializer):
    """Serializer for Ride model with workflow fields"""
    
    rider_email = serializers.CharField(source='rider.email', read_only=True)
    driver_name = serializers.CharField(source='driver.user.get_full_name', read_only=True)
    vehicle_info = serializers.CharField(source='vehicle.model_name', read_only=True)
    fleet_company_name = serializers.CharField(source='fleet_company.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    ride_type_display = serializers.CharField(source='get_ride_type_display', read_only=True)
    rider_tier_display = serializers.CharField(source='get_rider_tier_display', read_only=True)
    
    # Calculated fields
    estimated_total_fare = serializers.SerializerMethodField()
    is_vip = serializers.BooleanField(source='is_vip_ride', read_only=True)
    requires_encryption = serializers.BooleanField(source='requires_encrypted_tracking', read_only=True)
    
    class Meta:
        model = Ride
        fields = [
            'id', 'rider', 'driver', 'vehicle', 'fleet_company',
            'rider_email', 'driver_name', 'vehicle_info', 'fleet_company_name',
            'ride_type', 'rider_tier', 'status', 'billing_model',
            'ride_type_display', 'rider_tier_display', 'status_display',
            'pickup_latitude', 'pickup_longitude', 'pickup_address',
            'destination_latitude', 'destination_longitude', 'destination_address',
            'pickup_landmark', 'destination_landmark', 'waypoints',
            'estimated_distance_km', 'estimated_duration_minutes', 'estimated_fare',
            'actual_distance_km', 'actual_duration_minutes', 'total_fare',
            'platform_commission_rate', 'platform_commission', 'driver_earnings',
            'requires_baby_seat', 'requires_wheelchair_access', 'requires_premium_vehicle',
            'special_instructions', 'customer_notes',
            'vip_priority_level', 'assigned_control_center_agent',
            'surge_multiplier', 'weather_conditions', 'traffic_conditions',
            'workflow_step', 'auto_transitions_enabled',
            'created_at', 'updated_at', 'driver_accepted_at', 'driver_en_route_at',
            'driver_arrived_at', 'started_at', 'completed_at', 'cancelled_at',
            'is_sos_triggered', 'sos_triggered_at', 'sos_resolved',
            'estimated_total_fare', 'is_vip', 'requires_encryption'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'total_fare', 'platform_commission',
            'driver_earnings', 'workflow_step', 'is_sos_triggered', 'sos_triggered_at'
        ]
    
    def get_estimated_total_fare(self, obj):
        """Calculate estimated total fare"""
        try:
            return float(obj.calculate_flexible_fare())
        except:
            return None


class RideCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new rides"""
    
    class Meta:
        model = Ride
        fields = [
            'pickup_latitude', 'pickup_longitude', 'pickup_address',
            'destination_latitude', 'destination_longitude', 'destination_address',
            'pickup_landmark', 'destination_landmark', 'waypoints',
            'ride_type', 'estimated_distance_km', 'estimated_duration_minutes',
            'scheduled_pickup_time', 'requires_baby_seat', 'requires_wheelchair_access',
            'requires_premium_vehicle', 'special_instructions', 'customer_notes'
        ]
    
    def create(self, validated_data):
        """Create ride with rider from request user"""
        validated_data['rider'] = self.context['request'].user
        validated_data['rider_tier'] = validated_data['rider'].tier
        
        # Set platform commission rate based on tier
        tier_commission_rates = {
            UserTier.NORMAL: 17.5,
            UserTier.PREMIUM: 22.5,
            UserTier.VIP: 27.5,
        }
        validated_data['platform_commission_rate'] = tier_commission_rates.get(
            validated_data['rider_tier'], 17.5
        )
        
        return super().create(validated_data)


class RideStatusHistorySerializer(serializers.ModelSerializer):
    """Serializer for ride status history"""
    
    old_status_display = serializers.CharField(source='get_old_status_display', read_only=True)
    new_status_display = serializers.CharField(source='get_new_status_display', read_only=True)
    changed_by_name = serializers.CharField(source='changed_by.get_full_name', read_only=True)
    
    class Meta:
        model = RideStatusHistory
        fields = [
            'id', 'ride', 'old_status', 'new_status', 'changed_by', 'reason',
            'timestamp', 'old_status_display', 'new_status_display', 'changed_by_name'
        ]
        read_only_fields = ['id', 'timestamp']


class WorkflowActionSerializer(serializers.ModelSerializer):
    """Serializer for workflow actions"""
    
    ride_id = serializers.CharField(source='ride.id', read_only=True)
    action_type_display = serializers.CharField(source='get_action_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = WorkflowAction
        fields = [
            'id', 'ride', 'ride_id', 'action_type', 'action_type_display',
            'target_status', 'scheduled_at', 'executed_at', 'status', 'status_display',
            'error_message', 'retry_count', 'max_retries', 'created_at'
        ]
        read_only_fields = ['id', 'executed_at', 'error_message', 'retry_count', 'created_at']


class CancellationRecordSerializer(serializers.ModelSerializer):
    """Serializer for cancellation records"""
    
    ride_id = serializers.CharField(source='ride.id', read_only=True)
    cancelled_by_name = serializers.CharField(source='cancelled_by.get_full_name', read_only=True)
    
    class Meta:
        model = CancellationRecord
        fields = [
            'id', 'ride', 'ride_id', 'cancelled_by', 'cancelled_by_name',
            'reason', 'cancellation_fee', 'refund_amount', 'policy_applied',
            'cancelled_at'
        ]
        read_only_fields = ['id', 'cancelled_at']


class RideTrackingSerializer(serializers.ModelSerializer):
    """Serializer for ride tracking data"""
    
    class Meta:
        model = RideTracking
        fields = [
            'id', 'ride', 'latitude', 'longitude', 'speed_kmh',
            'heading', 'accuracy_meters', 'recorded_at'
        ]
        read_only_fields = ['id', 'recorded_at', 'encrypted_location_data']


class RideRatingSerializer(serializers.ModelSerializer):
    """Serializer for ride ratings"""
    
    rater_name = serializers.CharField(source='rater.get_full_name', read_only=True)
    rated_user_name = serializers.CharField(source='rated_user.get_full_name', read_only=True)
    rating_type_display = serializers.CharField(source='get_rating_type_display', read_only=True)
    
    class Meta:
        model = RideRating
        fields = [
            'id', 'ride', 'rater', 'rated_user', 'rating_type',
            'rater_name', 'rated_user_name', 'rating_type_display',
            'rating', 'review', 'punctuality', 'cleanliness',
            'safety', 'communication', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class RideOfferSerializer(serializers.ModelSerializer):
    """Serializer for ride offers"""
    
    driver_name = serializers.CharField(source='driver.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = RideOffer
        fields = [
            'id', 'ride', 'driver', 'driver_name', 'estimated_arrival_time',
            'offered_fare', 'status', 'status_display', 'driver_latitude',
            'driver_longitude', 'created_at', 'expires_at', 'is_expired'
        ]
        read_only_fields = ['id', 'created_at', 'is_expired']


class EmergencyContactSerializer(serializers.ModelSerializer):
    """Serializer for emergency contacts"""
    
    class Meta:
        model = EmergencyContact
        fields = [
            'id', 'user', 'name', 'phone_number', 'email',
            'relationship', 'is_primary', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SurgeZoneSerializer(serializers.ModelSerializer):
    """Serializer for surge zones"""
    
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    is_currently_active = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = SurgeZone
        fields = [
            'id', 'name', 'center_latitude', 'center_longitude', 'radius_km',
            'surge_multiplier', 'is_active', 'active_from', 'active_until',
            'min_demand_ratio', 'min_ride_requests', 'created_at', 'created_by',
            'created_by_name', 'is_currently_active'
        ]
        read_only_fields = ['id', 'created_at', 'is_currently_active']


class RideMatchingLogSerializer(serializers.ModelSerializer):
    """Serializer for ride matching logs"""
    
    ride_id = serializers.CharField(source='ride.id', read_only=True)
    surge_zone_name = serializers.CharField(source='surge_zone.name', read_only=True)
    
    class Meta:
        model = RideMatchingLog
        fields = [
            'id', 'ride', 'ride_id', 'timestamp', 'search_radius_km',
            'drivers_in_radius', 'drivers_eligible', 'drivers_contacted',
            'offers_created', 'match_successful', 'match_duration_seconds',
            'surge_multiplier', 'surge_zone', 'surge_zone_name',
            'rider_tier', 'ride_type'
        ]
        read_only_fields = ['id', 'timestamp']


# Workflow-specific serializers
class RideStatusUpdateSerializer(serializers.Serializer):
    """Serializer for ride status updates via workflow"""
    
    new_status = serializers.ChoiceField(choices=RideStatus.choices)
    reason = serializers.CharField(max_length=500, required=False, allow_blank=True)
    
    def validate(self, data):
        """Validate status transition"""
        ride = self.context['ride']
        new_status = data['new_status']
        
        # Import here to avoid circular imports
        from .workflow import RideWorkflow
        
        workflow = RideWorkflow(ride)
        if not workflow.can_transition_to(new_status):
            available_transitions = workflow.get_available_transitions()
            raise serializers.ValidationError(
                f"Cannot transition from {ride.status} to {new_status}. "
                f"Available transitions: {available_transitions}"
            )
        
        return data


class DriverAcceptanceSerializer(serializers.Serializer):
    """Serializer for driver ride acceptance"""
    
    estimated_arrival_minutes = serializers.IntegerField(min_value=1, max_value=60)
    notes = serializers.CharField(max_length=500, required=False, allow_blank=True)


class RideCancellationSerializer(serializers.Serializer):
    """Serializer for ride cancellation"""
    
    reason = serializers.CharField(max_length=500)
    
    def validate(self, data):
        """Validate cancellation"""
        ride = self.context['ride']
        user = self.context['request'].user
        
        # Import here to avoid circular imports
        from .workflow import CancellationPolicy
        
        # Check if cancellation is allowed
        is_allowed, message = CancellationPolicy.can_cancel_ride(ride, user)
        if not is_allowed:
            raise serializers.ValidationError(message)
        
        return data


class SOSActivationSerializer(serializers.Serializer):
    """Serializer for SOS activation"""
    
    emergency_type = serializers.ChoiceField(choices=[
        ('medical', 'Medical Emergency'),
        ('safety', 'Safety Concern'),
        ('breakdown', 'Vehicle Breakdown'),
        ('other', 'Other Emergency')
    ])
    description = serializers.CharField(max_length=1000, required=False, allow_blank=True)
    location_latitude = serializers.DecimalField(max_digits=10, decimal_places=8, required=False)
    location_longitude = serializers.DecimalField(max_digits=11, decimal_places=8, required=False)
    
    def validate(self, data):
        """Validate SOS activation"""
        ride = self.context['ride']
        
        if not ride.is_vip_ride:
            raise serializers.ValidationError("SOS feature is only available for VIP rides")
        
        if ride.is_sos_triggered:
            raise serializers.ValidationError("SOS is already activated for this ride")
        
        return data


# Response serializers
class WorkflowStatusResponse(serializers.Serializer):
    """Response serializer for workflow status"""
    
    success = serializers.BooleanField()
    message = serializers.CharField()
    ride_status = serializers.CharField()
    available_transitions = serializers.ListField(child=serializers.CharField())
    next_actions = serializers.ListField(child=serializers.CharField())


class CancellationPolicyResponse(serializers.Serializer):
    """Response serializer for cancellation policy"""
    
    can_cancel = serializers.BooleanField()
    message = serializers.CharField()
    cancellation_fee = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    refund_amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    policy_details = serializers.DictField(required=False)
