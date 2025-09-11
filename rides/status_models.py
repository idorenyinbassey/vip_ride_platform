# rides/status_models.py
"""
VIP Ride-Hailing Platform - Ride Status History and Workflow Models
Models for tracking ride status changes and workflow operations
"""

from django.db import models
from django.conf import settings
import uuid
from django.utils import timezone


class RideStatusHistory(models.Model):
    """Track all ri    # Context
    user_tier = models.CharField(max_length=15) status changes for audit and analytics"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    ride = models.ForeignKey(
        'rides.Ride',
        on_delete=models.CASCADE,
        related_name='status_history'
    )
    
    from_status = models.CharField(max_length=25)
    to_status = models.CharField(max_length=25)
    
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='status_changes_made'
    )
    
    reason = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'ride_status_history'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['ride']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['from_status', 'to_status']),
            models.Index(fields=['changed_by']),
        ]
    
    def __str__(self):
        return f'{self.ride.id}: {self.from_status} → {self.to_status}'


class WorkflowAction(models.Model):
    """Track automatic workflow actions and their results"""
    
    class ActionType(models.TextChoices):
        STATUS_TRANSITION = 'status_transition', 'Status Transition'
        DRIVER_SEARCH = 'driver_search', 'Driver Search'
        PAYMENT_PROCESS = 'payment_process', 'Payment Processing'
        NOTIFICATION_SEND = 'notification_send', 'Notification Sent'
        CANCELLATION_FEE = 'cancellation_fee', 'Cancellation Fee'
        GPS_TRACKING_START = 'gps_tracking_start', 'GPS Tracking Started'
        SOS_TRIGGER = 'sos_trigger', 'SOS Triggered'
    
    class ActionStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'
        SKIPPED = 'skipped', 'Skipped'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    ride = models.ForeignKey(
        'rides.Ride',
        on_delete=models.CASCADE,
        related_name='workflow_actions'
    )
    
    action_type = models.CharField(
        max_length=20,
        choices=ActionType.choices
    )
    
    action_status = models.CharField(
        max_length=15,
        choices=ActionStatus.choices,
        default=ActionStatus.PENDING
    )
    
    triggered_by_status = models.CharField(max_length=25)
    
    # Action details
    action_data = models.JSONField(default=dict)
    result_data = models.JSONField(default=dict)
    error_message = models.TextField(blank=True)
    
    # Timing
    scheduled_at = models.DateTimeField(default=timezone.now)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Retry logic
    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=3)
    next_retry_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'workflow_actions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['ride']),
            models.Index(fields=['action_type']),
            models.Index(fields=['action_status']),
            models.Index(fields=['scheduled_at']),
            models.Index(fields=['next_retry_at']),
        ]
    
    def __str__(self):
        return f'{self.ride.id}: {self.action_type} - {self.action_status}'
    
    def mark_started(self):
        """Mark action as started"""
        self.action_status = self.ActionStatus.IN_PROGRESS
        self.started_at = timezone.now()
        self.save()
    
    def mark_completed(self, result_data=None):
        """Mark action as completed"""
        self.action_status = self.ActionStatus.COMPLETED
        self.completed_at = timezone.now()
        if result_data:
            self.result_data.update(result_data)
        self.save()
    
    def mark_failed(self, error_message, schedule_retry=True):
        """Mark action as failed and optionally schedule retry"""
        self.action_status = self.ActionStatus.FAILED
        self.error_message = error_message
        self.retry_count += 1
        
        if schedule_retry and self.retry_count < self.max_retries:
            # Schedule next retry with exponential backoff
            retry_delay = min(300 * (2 ** self.retry_count), 3600)  # Max 1 hour
            self.next_retry_at = timezone.now() + timezone.timedelta(
                seconds=retry_delay
            )
            self.action_status = self.ActionStatus.PENDING
        
        self.save()


class CancellationRecord(models.Model):
    """Track ride cancellations and their financial implications"""
    
    class CancellationType(models.TextChoices):
        RIDER_FREE = 'rider_free', 'Rider Cancellation (Free)'
        RIDER_PAID = 'rider_paid', 'Rider Cancellation (Fee Applied)'
        DRIVER = 'driver', 'Driver Cancellation'
        SYSTEM = 'system', 'System Cancellation'
        EMERGENCY = 'emergency', 'Emergency Cancellation'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    ride = models.OneToOneField(
        'rides.Ride',
        on_delete=models.CASCADE,
        related_name='cancellation_record'
    )
    
    cancellation_type = models.CharField(
        max_length=15,
        choices=CancellationType.choices
    )
    
    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    reason = models.TextField()
    
    # Financial details
    cancellation_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    refund_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    
    # Policy information
    user_tier = models.CharField(max_length=15)
    free_cancellation_window_minutes = models.IntegerField()
    time_since_request_minutes = models.IntegerField()
    
    # Driver compensation (if applicable)
    driver_compensation = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    
    cancelled_at = models.DateTimeField(default=timezone.now)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'cancellation_records'
        indexes = [
            models.Index(fields=['ride']),
            models.Index(fields=['cancellation_type']),
            models.Index(fields=['cancelled_by']),
            models.Index(fields=['cancelled_at']),
        ]
    
    def __str__(self):
        return f'{self.ride.id}: {self.get_cancellation_type_display()}'


class PaymentWorkflow(models.Model):
    """Track payment processing workflow for rides"""
    
    class PaymentStep(models.TextChoices):
        INITIATED = 'initiated', 'Payment Initiated'
        AUTHORIZATION = 'authorization', 'Authorization in Progress'
        AUTHORIZED = 'authorized', 'Payment Authorized'
        CAPTURE = 'capture', 'Capture in Progress'
        CAPTURED = 'captured', 'Payment Captured'
        SETTLEMENT = 'settlement', 'Settlement in Progress'
        COMPLETED = 'completed', 'Payment Completed'
        FAILED = 'failed', 'Payment Failed'
        REFUNDED = 'refunded', 'Payment Refunded'
        DISPUTED = 'disputed', 'Payment Disputed'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    ride = models.OneToOneField(
        'rides.Ride',
        on_delete=models.CASCADE,
        related_name='payment_workflow'
    )
    
    current_step = models.CharField(
        max_length=15,
        choices=PaymentStep.choices,
        default=PaymentStep.INITIATED
    )
    
    # Payment details
    payment_method = models.CharField(max_length=50)
    payment_gateway = models.CharField(max_length=50)
    transaction_reference = models.CharField(max_length=100, unique=True)
    
    # Amount breakdown
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    platform_commission = models.DecimalField(max_digits=10, decimal_places=2)
    driver_earnings = models.DecimalField(max_digits=10, decimal_places=2)
    gateway_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Workflow tracking
    step_history = models.JSONField(default=list)
    retry_attempts = models.IntegerField(default=0)
    
    # Timing
    initiated_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Error handling
    last_error = models.TextField(blank=True)
    requires_manual_review = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'payment_workflows'
        indexes = [
            models.Index(fields=['ride']),
            models.Index(fields=['current_step']),
            models.Index(fields=['transaction_reference']),
            models.Index(fields=['payment_gateway']),
            models.Index(fields=['initiated_at']),
        ]
    
    def __str__(self):
        return f'{self.ride.id}: Payment {self.get_current_step_display()}'
    
    def advance_step(self, new_step, details=None):
        """Advance payment to next step"""
        old_step = self.current_step
        self.current_step = new_step
        
        # Record step change in history
        step_entry = {
            'from_step': old_step,
            'to_step': new_step,
            'timestamp': timezone.now().isoformat(),
            'details': details or {}
        }
        self.step_history.append(step_entry)
        
        if new_step == self.PaymentStep.COMPLETED:
            self.completed_at = timezone.now()
        
        self.save()


class DriverTimeoutRecord(models.Model):
    """Track driver response timeouts for analytics"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    ride = models.ForeignKey(
        'rides.Ride',
        on_delete=models.CASCADE,
        related_name='driver_timeouts'
    )
    
    driver = models.ForeignKey(
        'accounts.Driver',
        on_delete=models.CASCADE,
        related_name='timeout_records'
    )
    
    # Timeout details
    timeout_duration_seconds = models.IntegerField()
    expected_response_time_seconds = models.IntegerField()
    
    # Context
    user_tier = models.CharField(max_length=10)
    ride_type = models.CharField(max_length=15)
    distance_to_pickup_km = models.DecimalField(
        max_digits=6, 
        decimal_places=2
    )
    
    # Driver state at timeout
    driver_was_online = models.BooleanField()
    driver_was_available = models.BooleanField()
    driver_active_rides = models.IntegerField(default=0)
    
    occurred_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'driver_timeout_records'
        indexes = [
            models.Index(fields=['ride']),
            models.Index(fields=['driver']),
            models.Index(fields=['occurred_at']),
            models.Index(fields=['user_tier']),
        ]
    
    def __str__(self):
        return f'Timeout: {self.driver} for {self.ride.id}'


class RideCompletionWorkflow(models.Model):
    """Track ride completion process and confirmation"""
    
    class CompletionStep(models.TextChoices):
        DRIVER_COMPLETED = 'driver_completed', 'Driver Marked Complete'
        RIDER_CONFIRMATION = 'rider_confirmation', 'Awaiting Rider Confirmation'
        CONFIRMED = 'confirmed', 'Completion Confirmed'
        DISPUTED = 'disputed', 'Completion Disputed'
        AUTO_CONFIRMED = 'auto_confirmed', 'Auto-Confirmed'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    ride = models.OneToOneField(
        'rides.Ride',
        on_delete=models.CASCADE,
        related_name='completion_workflow'
    )
    
    current_step = models.CharField(
        max_length=20,
        choices=CompletionStep.choices,
        default=CompletionStep.DRIVER_COMPLETED
    )
    
    # Completion details
    driver_completion_time = models.DateTimeField()
    rider_confirmation_deadline = models.DateTimeField()
    rider_confirmed_at = models.DateTimeField(null=True, blank=True)
    auto_confirmation_at = models.DateTimeField(null=True, blank=True)
    
    # Final details
    final_pickup_location = models.JSONField(default=dict)
    final_dropoff_location = models.JSONField(default=dict)
    actual_route_data = models.JSONField(default=dict)
    
    # Discrepancy tracking
    has_route_discrepancy = models.BooleanField(default=False)
    has_fare_discrepancy = models.BooleanField(default=False)
    discrepancy_notes = models.TextField(blank=True)
    
    # Rider feedback collection
    feedback_requested_at = models.DateTimeField(null=True, blank=True)
    feedback_received_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ride_completion_workflows'
        indexes = [
            models.Index(fields=['ride']),
            models.Index(fields=['current_step']),
            models.Index(fields=['rider_confirmation_deadline']),
            models.Index(fields=['auto_confirmation_at']),
        ]
    
    def __str__(self):
        return f'{self.ride.id}: {self.get_current_step_display()}'
    
    def confirm_by_rider(self):
        """Mark as confirmed by rider"""
        self.current_step = self.CompletionStep.CONFIRMED
        self.rider_confirmed_at = timezone.now()
        self.save()
    
    def auto_confirm(self):
        """Auto-confirm after timeout"""
        self.current_step = self.CompletionStep.AUTO_CONFIRMED
        self.auto_confirmation_at = timezone.now()
        self.save()
