# rides/workflow_serializers.py
"""
VIP Ride-Hailing Platform - Workflow Serializers
Serializers for ride workflow API responses
"""

from rest_framework import serializers
from django.utils import timezone
from .models import Ride
from .status_models import (
    RideStatusHistory, WorkflowAction, CancellationRecord,
    PaymentWorkflow, RideCompletionWorkflow
)
from accounts.serializers import UserBasicSerializer
from fleet_management.serializers import DriverBasicSerializer


class RideStatusHistorySerializer(serializers.ModelSerializer):
    """Serializer for ride status history"""
    
    changed_by = UserBasicSerializer(read_only=True)
    duration_in_status = serializers.SerializerMethodField()
    
    class Meta:
        model = RideStatusHistory
        fields = [
            'id', 'from_status', 'to_status', 'changed_by',
            'reason', 'metadata', 'timestamp', 'duration_in_status'
        ]
        read_only_fields = fields
    
    def get_duration_in_status(self, obj):
        """Calculate time spent in previous status"""
        if not obj.ride.status_history.exists():
            return None
        
        try:
            previous_history = obj.ride.status_history.filter(
                timestamp__lt=obj.timestamp
            ).first()
            
            if previous_history:
                duration = obj.timestamp - previous_history.timestamp
                return int(duration.total_seconds())
            
            # If no previous history, calculate from ride creation
            creation_time = obj.ride.created_at
            duration = obj.timestamp - creation_time
            return int(duration.total_seconds())
            
        except Exception:
            return None


class WorkflowActionSerializer(serializers.ModelSerializer):
    """Serializer for workflow actions"""
    
    duration = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkflowAction
        fields = [
            'id', 'action_type', 'action_status', 'triggered_by_status',
            'action_data', 'result_data', 'error_message',
            'scheduled_at', 'started_at', 'completed_at',
            'retry_count', 'max_retries', 'next_retry_at',
            'duration', 'is_overdue'
        ]
        read_only_fields = fields
    
    def get_duration(self, obj):
        """Calculate action duration"""
        if obj.started_at and obj.completed_at:
            duration = obj.completed_at - obj.started_at
            return int(duration.total_seconds())
        elif obj.started_at:
            duration = timezone.now() - obj.started_at
            return int(duration.total_seconds())
        return None
    
    def get_is_overdue(self, obj):
        """Check if action is overdue"""
        if obj.action_status in [
            WorkflowAction.ActionStatus.COMPLETED,
            WorkflowAction.ActionStatus.FAILED,
            WorkflowAction.ActionStatus.SKIPPED
        ]:
            return False
        
        # Consider overdue if pending for more than 5 minutes
        overdue_threshold = timezone.now() - timezone.timedelta(minutes=5)
        return obj.scheduled_at < overdue_threshold


class CancellationRecordSerializer(serializers.ModelSerializer):
    """Serializer for cancellation records"""
    
    cancelled_by = UserBasicSerializer(read_only=True)
    time_since_request = serializers.SerializerMethodField()
    
    class Meta:
        model = CancellationRecord
        fields = [
            'id', 'cancellation_type', 'cancelled_by', 'reason',
            'cancellation_fee', 'refund_amount', 'user_tier',
            'free_cancellation_window_minutes', 'time_since_request_minutes',
            'driver_compensation', 'cancelled_at', 'processed_at',
            'time_since_request'
        ]
        read_only_fields = fields
    
    def get_time_since_request(self, obj):
        """Get human-readable time since ride request"""
        if obj.ride.created_at:
            duration = obj.cancelled_at - obj.ride.created_at
            minutes = int(duration.total_seconds() / 60)
            
            if minutes < 60:
                return f"{minutes} minutes"
            elif minutes < 1440:  # 24 hours
                hours = minutes // 60
                remaining_minutes = minutes % 60
                return f"{hours}h {remaining_minutes}m"
            else:
                days = minutes // 1440
                return f"{days} days"
        return None


class PaymentWorkflowSerializer(serializers.ModelSerializer):
    """Serializer for payment workflow"""
    
    step_count = serializers.SerializerMethodField()
    processing_time = serializers.SerializerMethodField()
    
    class Meta:
        model = PaymentWorkflow
        fields = [
            'id', 'current_step', 'payment_method', 'payment_gateway',
            'transaction_reference', 'total_amount', 'platform_commission',
            'driver_earnings', 'gateway_fee', 'step_history',
            'retry_attempts', 'initiated_at', 'completed_at',
            'last_error', 'requires_manual_review',
            'step_count', 'processing_time'
        ]
        read_only_fields = fields
    
    def get_step_count(self, obj):
        """Get number of workflow steps completed"""
        return len(obj.step_history)
    
    def get_processing_time(self, obj):
        """Get payment processing time"""
        if obj.completed_at:
            duration = obj.completed_at - obj.initiated_at
            return int(duration.total_seconds())
        else:
            duration = timezone.now() - obj.initiated_at
            return int(duration.total_seconds())


class RideCompletionWorkflowSerializer(serializers.ModelSerializer):
    """Serializer for ride completion workflow"""
    
    confirmation_window_remaining = serializers.SerializerMethodField()
    auto_confirm_in = serializers.SerializerMethodField()
    
    class Meta:
        model = RideCompletionWorkflow
        fields = [
            'id', 'current_step', 'driver_completion_time',
            'rider_confirmation_deadline', 'rider_confirmed_at',
            'auto_confirmation_at', 'final_pickup_location',
            'final_dropoff_location', 'actual_route_data',
            'has_route_discrepancy', 'has_fare_discrepancy',
            'discrepancy_notes', 'feedback_requested_at',
            'feedback_received_at', 'confirmation_window_remaining',
            'auto_confirm_in'
        ]
        read_only_fields = fields
    
    def get_confirmation_window_remaining(self, obj):
        """Get remaining time for rider confirmation"""
        if obj.current_step != RideCompletionWorkflow.CompletionStep.RIDER_CONFIRMATION:
            return None
        
        if obj.rider_confirmation_deadline:
            remaining = obj.rider_confirmation_deadline - timezone.now()
            if remaining.total_seconds() > 0:
                return int(remaining.total_seconds())
        
        return 0
    
    def get_auto_confirm_in(self, obj):
        """Get time until auto-confirmation"""
        if obj.auto_confirmation_at and obj.auto_confirmation_at > timezone.now():
            remaining = obj.auto_confirmation_at - timezone.now()
            return int(remaining.total_seconds())
        return None


class RideWorkflowSerializer(serializers.ModelSerializer):
    """Enhanced ride serializer with workflow information"""
    
    rider = UserBasicSerializer(read_only=True)
    driver = DriverBasicSerializer(read_only=True)
    status_history = RideStatusHistorySerializer(many=True, read_only=True)
    workflow_actions = WorkflowActionSerializer(many=True, read_only=True)
    cancellation_record = CancellationRecordSerializer(read_only=True)
    payment_workflow = PaymentWorkflowSerializer(read_only=True)
    completion_workflow = RideCompletionWorkflowSerializer(read_only=True)
    
    # Calculated fields
    total_duration = serializers.SerializerMethodField()
    current_step_duration = serializers.SerializerMethodField()
    next_possible_statuses = serializers.SerializerMethodField()
    can_cancel = serializers.SerializerMethodField()
    cancellation_policy = serializers.SerializerMethodField()
    
    class Meta:
        model = Ride
        fields = [
            'id', 'rider', 'driver', 'ride_type', 'rider_tier', 'status',
            'workflow_step', 'auto_transitions_enabled',
            'pickup_latitude', 'pickup_longitude', 'pickup_address',
            'destination_latitude', 'destination_longitude', 'destination_address',
            'created_at', 'updated_at', 'driver_accepted_at',
            'driver_en_route_at', 'driver_arrived_at', 'started_at',
            'completed_at', 'cancelled_at', 'estimated_fare', 'total_fare',
            'platform_commission', 'driver_earnings', 'status_history',
            'workflow_actions', 'cancellation_record', 'payment_workflow',
            'completion_workflow', 'total_duration', 'current_step_duration',
            'next_possible_statuses', 'can_cancel', 'cancellation_policy'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'driver_accepted_at',
            'driver_en_route_at', 'driver_arrived_at', 'started_at',
            'completed_at', 'cancelled_at', 'platform_commission',
            'driver_earnings', 'status_history', 'workflow_actions',
            'cancellation_record', 'payment_workflow', 'completion_workflow'
        ]
    
    def get_total_duration(self, obj):
        """Get total ride duration from request to completion/cancellation"""
        end_time = obj.completed_at or obj.cancelled_at or timezone.now()
        duration = end_time - obj.created_at
        return int(duration.total_seconds())
    
    def get_current_step_duration(self, obj):
        """Get duration in current status"""
        latest_history = obj.status_history.first()
        if latest_history:
            duration = timezone.now() - latest_history.timestamp
            return int(duration.total_seconds())
        else:
            duration = timezone.now() - obj.created_at
            return int(duration.total_seconds())
    
    def get_next_possible_statuses(self, obj):
        """Get possible next statuses for this ride"""
        from .workflow import RideWorkflow, RideStatus
        
        try:
            workflow = RideWorkflow(obj)
            possible_transitions = []
            
            for status in RideStatus:
                if workflow.can_transition_to(status):
                    possible_transitions.append({
                        'status': status.value,
                        'display': status.name.replace('_', ' ').title()
                    })
            
            return possible_transitions
        except Exception:
            return []
    
    def get_can_cancel(self, obj):
        """Check if ride can be cancelled by current user"""
        request = self.context.get('request')
        if not request or not request.user:
            return False
        
        # Check if user is authorized to cancel
        if request.user == obj.rider:
            from .workflow import CancellationPolicy
            
            user_tier = getattr(request.user, 'tier', 'normal')
            can_cancel_daily, _ = CancellationPolicy.check_daily_cancellation_limit(
                request.user, user_tier
            )
            
            # Check if ride is in cancellable state
            cancellable_statuses = [
                'requested', 'driver_search', 'driver_found',
                'driver_accepted', 'driver_en_route', 'driver_arrived'
            ]
            
            return obj.status in cancellable_statuses and can_cancel_daily
        
        elif hasattr(request.user, 'driver') and request.user.driver == obj.driver:
            # Drivers can cancel before pickup
            cancellable_statuses = [
                'driver_accepted', 'driver_en_route', 'driver_arrived'
            ]
            return obj.status in cancellable_statuses
        
        return False
    
    def get_cancellation_policy(self, obj):
        """Get cancellation policy information for the ride"""
        request = self.context.get('request')
        if not request or not request.user or request.user != obj.rider:
            return None
        
        from .workflow import CancellationPolicy
        
        user_tier = getattr(request.user, 'tier', 'normal')
        can_cancel_free, fee_message = CancellationPolicy.can_cancel_free(
            obj, user_tier
        )
        can_cancel_daily, limit_message = CancellationPolicy.check_daily_cancellation_limit(
            request.user, user_tier
        )
        
        return {
            'can_cancel_free': can_cancel_free,
            'fee_message': fee_message,
            'can_cancel_daily': can_cancel_daily,
            'limit_message': limit_message,
            'policy': CancellationPolicy.get_policy(user_tier)
        }


class RideStatusUpdateRequestSerializer(serializers.Serializer):
    """Serializer for ride status update requests"""
    
    status = serializers.CharField(required=True)
    reason = serializers.CharField(required=False, allow_blank=True)
    metadata = serializers.JSONField(required=False, default=dict)
    
    def validate_status(self, value):
        """Validate status value"""
        from .workflow import RideStatus
        
        try:
            RideStatus(value)
            return value
        except ValueError:
            valid_statuses = [status.value for status in RideStatus]
            raise serializers.ValidationError(
                f"Invalid status. Valid options: {', '.join(valid_statuses)}"
            )


class RideCancellationRequestSerializer(serializers.Serializer):
    """Serializer for ride cancellation requests"""
    
    reason = serializers.CharField(required=True, max_length=500)
    emergency = serializers.BooleanField(default=False)
    
    def validate_reason(self, value):
        """Validate cancellation reason"""
        if len(value.strip()) < 5:
            raise serializers.ValidationError(
                "Cancellation reason must be at least 5 characters long"
            )
        return value.strip()


class SOSTriggerRequestSerializer(serializers.Serializer):
    """Serializer for SOS trigger requests"""
    
    emergency_type = serializers.ChoiceField(
        choices=[
            ('general', 'General Emergency'),
            ('medical', 'Medical Emergency'),
            ('security', 'Security Threat'),
            ('accident', 'Vehicle Accident'),
            ('harassment', 'Harassment'),
            ('other', 'Other Emergency')
        ],
        default='general'
    )
    description = serializers.CharField(required=False, max_length=1000)
    location_override = serializers.JSONField(required=False)
    
    def validate_description(self, value):
        """Validate emergency description"""
        if value and len(value.strip()) < 10:
            raise serializers.ValidationError(
                "Emergency description should be at least 10 characters"
            )
        return value.strip() if value else ""
