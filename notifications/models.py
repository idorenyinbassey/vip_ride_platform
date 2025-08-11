"""
Notifications Models
Multi-channel notification system for the VIP ride-hailing platform
"""

from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
import uuid


class NotificationType(models.TextChoices):
    RIDE_REQUEST = 'ride_request', 'Ride Request'
    RIDE_ACCEPTED = 'ride_accepted', 'Ride Accepted'
    RIDE_STARTED = 'ride_started', 'Ride Started'
    RIDE_COMPLETED = 'ride_completed', 'Ride Completed'
    RIDE_CANCELLED = 'ride_cancelled', 'Ride Cancelled'
    DRIVER_ARRIVED = 'driver_arrived', 'Driver Arrived'
    PAYMENT_PROCESSED = 'payment_processed', 'Payment Processed'
    PAYMENT_FAILED = 'payment_failed', 'Payment Failed'
    EMERGENCY_ALERT = 'emergency_alert', 'Emergency Alert'
    SOS_TRIGGERED = 'sos_triggered', 'SOS Triggered'
    PROMO_OFFER = 'promo_offer', 'Promotional Offer'
    SYSTEM_UPDATE = 'system_update', 'System Update'
    HOTEL_BOOKING = 'hotel_booking', 'Hotel Booking'
    MAINTENANCE_ALERT = 'maintenance_alert', 'Maintenance Alert'


class NotificationChannel(models.TextChoices):
    PUSH = 'push', 'Push Notification'
    SMS = 'sms', 'SMS'
    EMAIL = 'email', 'Email'
    IN_APP = 'in_app', 'In-App Notification'
    WHATSAPP = 'whatsapp', 'WhatsApp'


class NotificationPriority(models.TextChoices):
    LOW = 'low', 'Low'
    NORMAL = 'normal', 'Normal'
    HIGH = 'high', 'High'
    URGENT = 'urgent', 'Urgent'
    CRITICAL = 'critical', 'Critical'


class NotificationStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    SENT = 'sent', 'Sent'
    DELIVERED = 'delivered', 'Delivered'
    READ = 'read', 'Read'
    FAILED = 'failed', 'Failed'
    EXPIRED = 'expired', 'Expired'


class Notification(models.Model):
    """Core notification model"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Recipient Information
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    
    # Notification Details
    notification_type = models.CharField(
        max_length=25,
        choices=NotificationType.choices
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Channel and Priority
    channel = models.CharField(
        max_length=15,
        choices=NotificationChannel.choices,
        default=NotificationChannel.PUSH
    )
    priority = models.CharField(
        max_length=10,
        choices=NotificationPriority.choices,
        default=NotificationPriority.NORMAL
    )
    
    # Status Tracking
    status = models.CharField(
        max_length=15,
        choices=NotificationStatus.choices,
        default=NotificationStatus.PENDING
    )
    
    # Related Object (Generic Foreign Key)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    object_id = models.CharField(max_length=100, null=True, blank=True)
    related_object = GenericForeignKey('content_type', 'object_id')
    
    # Delivery Tracking
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    
    # Retry Logic
    retry_count = models.PositiveIntegerField(default=0)
    max_retries = models.PositiveIntegerField(default=3)
    next_retry_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    external_id = models.CharField(
        max_length=100,
        blank=True,
        help_text='External service notification ID'
    )
    
    # Expiration
    expires_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notifications'
        indexes = [
            models.Index(fields=['recipient', 'status']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['channel']),
            models.Index(fields=['priority']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['sent_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.notification_type} - {self.recipient.get_full_name()}"
    
    @property
    def is_read(self):
        """Check if notification is read"""
        return self.status == NotificationStatus.READ
    
    @property
    def is_expired(self):
        """Check if notification is expired"""
        if self.expires_at:
            from django.utils import timezone
            return timezone.now() > self.expires_at
        return False
    
    def mark_as_read(self):
        """Mark notification as read"""
        if self.status != NotificationStatus.READ:
            self.status = NotificationStatus.READ
            self.read_at = timezone.now()
            self.save()


class NotificationPreference(models.Model):
    """User notification preferences"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_preferences'
    )
    
    # Channel Preferences
    push_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=True)
    email_enabled = models.BooleanField(default=True)
    whatsapp_enabled = models.BooleanField(default=False)
    
    # Notification Type Preferences
    ride_notifications = models.BooleanField(default=True)
    payment_notifications = models.BooleanField(default=True)
    promotional_notifications = models.BooleanField(default=True)
    emergency_notifications = models.BooleanField(default=True)
    system_notifications = models.BooleanField(default=True)
    
    # Advanced Settings
    quiet_hours_enabled = models.BooleanField(default=False)
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)
    
    # Priority Filtering
    minimum_priority = models.CharField(
        max_length=10,
        choices=NotificationPriority.choices,
        default=NotificationPriority.LOW
    )
    
    # Contact Information
    preferred_phone = models.CharField(
        max_length=20,
        blank=True,
        help_text='Preferred phone for SMS/WhatsApp'
    )
    preferred_email = models.EmailField(
        blank=True,
        help_text='Preferred email for notifications'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_preferences'
    
    def __str__(self):
        return f"Preferences - {self.user.get_full_name()}"
    
    def is_notification_allowed(self, notification_type, channel, priority):
        """Check if notification is allowed based on preferences"""
        from django.utils import timezone
        import datetime
        
        # Check channel preference
        if channel == NotificationChannel.PUSH and not self.push_enabled:
            return False
        elif channel == NotificationChannel.SMS and not self.sms_enabled:
            return False
        elif channel == NotificationChannel.EMAIL and not self.email_enabled:
            return False
        elif channel == NotificationChannel.WHATSAPP and not self.whatsapp_enabled:
            return False
        
        # Check notification type preference
        type_mapping = {
            'ride_request': self.ride_notifications,
            'ride_accepted': self.ride_notifications,
            'ride_started': self.ride_notifications,
            'ride_completed': self.ride_notifications,
            'ride_cancelled': self.ride_notifications,
            'driver_arrived': self.ride_notifications,
            'payment_processed': self.payment_notifications,
            'payment_failed': self.payment_notifications,
            'promo_offer': self.promotional_notifications,
            'emergency_alert': self.emergency_notifications,
            'sos_triggered': self.emergency_notifications,
            'system_update': self.system_notifications,
        }
        
        if not type_mapping.get(notification_type, True):
            return False
        
        # Check priority filtering
        priority_order = ['low', 'normal', 'high', 'urgent', 'critical']
        min_priority_index = priority_order.index(self.minimum_priority)
        current_priority_index = priority_order.index(priority)
        
        if current_priority_index < min_priority_index:
            return False
        
        # Check quiet hours (except for critical notifications)
        if (self.quiet_hours_enabled and 
                priority != NotificationPriority.CRITICAL and
                self.quiet_hours_start and self.quiet_hours_end):
            
            current_time = timezone.now().time()
            
            if self.quiet_hours_start <= self.quiet_hours_end:
                # Same day quiet hours
                if self.quiet_hours_start <= current_time <= self.quiet_hours_end:
                    return False
            else:
                # Overnight quiet hours
                if current_time >= self.quiet_hours_start or current_time <= self.quiet_hours_end:
                    return False
        
        return True


class NotificationTemplate(models.Model):
    """Notification message templates"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Template Identification
    notification_type = models.CharField(
        max_length=25,
        choices=NotificationType.choices,
        unique=True
    )
    
    # Template Content
    title_template = models.CharField(
        max_length=200,
        help_text='Title template with placeholders'
    )
    message_template = models.TextField(
        help_text='Message template with placeholders'
    )
    
    # Channel-Specific Templates
    sms_template = models.TextField(
        blank=True,
        help_text='SMS-specific template (shorter)'
    )
    email_subject_template = models.CharField(
        max_length=200,
        blank=True,
        help_text='Email subject template'
    )
    email_body_template = models.TextField(
        blank=True,
        help_text='Email body template (HTML supported)'
    )
    
    # Metadata
    is_active = models.BooleanField(default=True)
    supports_html = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_templates'
    
    def __str__(self):
        return f"Template - {self.notification_type}"
    
    def render_title(self, context):
        """Render title with context variables"""
        try:
            return self.title_template.format(**context)
        except (KeyError, ValueError):
            return self.title_template
    
    def render_message(self, context):
        """Render message with context variables"""
        try:
            return self.message_template.format(**context)
        except (KeyError, ValueError):
            return self.message_template


class NotificationDeliveryLog(models.Model):
    """Detailed delivery tracking"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name='delivery_logs'
    )
    
    # Delivery Attempt
    attempt_number = models.PositiveIntegerField()
    delivery_channel = models.CharField(
        max_length=15,
        choices=NotificationChannel.choices
    )
    
    # Provider Information
    provider_name = models.CharField(
        max_length=50,
        help_text='SMS/Email/Push provider name'
    )
    provider_message_id = models.CharField(
        max_length=100,
        blank=True,
        help_text='Provider-specific message ID'
    )
    
    # Status and Response
    delivery_status = models.CharField(
        max_length=15,
        choices=NotificationStatus.choices
    )
    error_message = models.TextField(blank=True)
    provider_response = models.JSONField(default=dict, blank=True)
    
    # Timing
    sent_at = models.DateTimeField()
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    # Cost Tracking (for paid services)
    cost_amount = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text='Cost per message'
    )
    cost_currency = models.CharField(max_length=3, default='USD')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notification_delivery_logs'
        indexes = [
            models.Index(fields=['notification']),
            models.Index(fields=['delivery_status']),
            models.Index(fields=['provider_name']),
            models.Index(fields=['sent_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Delivery - {self.notification.id} - {self.delivery_channel}"
