"""
Card Activation History Models

Tracks all card activation attempts and successful activations
for both VIP and Premium cards with detailed logging.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()


class CardActivationHistory(models.Model):
    """Track card activation attempts and history"""
    
    ACTIVATION_STATUS_CHOICES = [
        ('success', 'Successful'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
        ('cancelled', 'Cancelled'),
    ]
    
    CARD_TYPE_CHOICES = [
        ('vip', 'VIP Digital Card'),
        ('premium', 'Premium Digital Card'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Card Information
    card_type = models.CharField(max_length=10, choices=CARD_TYPE_CHOICES, default='vip')
    vip_card = models.ForeignKey(
        'accounts.VIPDigitalCard',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='activation_history'
    )
    premium_card = models.ForeignKey(
        'accounts.PremiumDigitalCard',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='activation_history'
    )
    
    # User and Activation Details
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='card_activation_attempts'
    )
    status = models.CharField(max_length=10, choices=ACTIVATION_STATUS_CHOICES)
    
    # Timestamps
    attempted_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Network and Security Information
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    activation_method = models.CharField(
        max_length=20,
        choices=[
            ('mobile_app', 'Mobile App'),
            ('web_portal', 'Web Portal'),
            ('admin_panel', 'Admin Panel'),
            ('api_direct', 'Direct API'),
        ],
        default='mobile_app'
    )
    
    # Additional Details
    error_message = models.TextField(blank=True, help_text="Error details if activation failed")
    activation_code_used = models.CharField(max_length=20, blank=True)
    notes = models.TextField(blank=True, help_text="Additional notes about the activation")
    
    # Admin Information
    admin_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='admin_card_activations',
        help_text="Admin user who performed activation (if applicable)"
    )
    
    class Meta:
        db_table = 'card_activation_history'
        ordering = ['-attempted_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['card_type', 'status']),
            models.Index(fields=['attempted_at']),
            models.Index(fields=['ip_address']),
        ]
        verbose_name = 'Card Activation History'
        verbose_name_plural = 'Card Activation History'
    
    def __str__(self):
        card_identifier = (
            self.vip_card.serial_number if self.vip_card else 
            self.premium_card.card_number if self.premium_card else 
            'Unknown'
        )
        return f"{self.card_type.upper()} {card_identifier} - {self.status.title()} by {self.user.email}"
    
    @property
    def card_identifier(self):
        """Get the card identifier (serial number or card number)"""
        if self.vip_card:
            return self.vip_card.serial_number
        elif self.premium_card:
            return self.premium_card.card_number
        return 'N/A'
    
    @property
    def duration(self):
        """Get activation duration if completed"""
        if self.completed_at and self.attempted_at:
            return self.completed_at - self.attempted_at
        return None
    
    def mark_successful(self, completion_time=None):
        """Mark activation as successful"""
        self.status = 'success'
        self.completed_at = completion_time or timezone.now()
        self.save()
    
    def mark_failed(self, error_message, completion_time=None):
        """Mark activation as failed with error message"""
        self.status = 'failed'
        self.error_message = error_message
        self.completed_at = completion_time or timezone.now()
        self.save()
    
    @classmethod
    def create_vip_activation_record(cls, vip_card, user, ip_address=None, 
                                   user_agent='', method='mobile_app', admin_user=None):
        """Create activation history record for VIP card"""
        return cls.objects.create(
            card_type='vip',
            vip_card=vip_card,
            user=user,
            status='pending',
            ip_address=ip_address,
            user_agent=user_agent,
            activation_method=method,
            activation_code_used=vip_card.activation_code,
            admin_user=admin_user
        )
    
    @classmethod
    def create_premium_activation_record(cls, premium_card, user, ip_address=None,
                                       user_agent='', method='mobile_app', admin_user=None):
        """Create activation history record for Premium card"""
        return cls.objects.create(
            card_type='premium',
            premium_card=premium_card,
            user=user,
            status='pending',
            ip_address=ip_address,
            user_agent=user_agent,
            activation_method=method,
            activation_code_used=premium_card.verification_code,
            admin_user=admin_user
        )


class CardUsageLog(models.Model):
    """Track card usage events for analytics"""
    
    EVENT_TYPES = [
        ('ride_booking', 'Ride Booking'),
        ('hotel_booking', 'Hotel Booking'),
        ('concierge_request', 'Concierge Request'),
        ('sos_activation', 'SOS Activation'),
        ('tier_upgrade', 'Tier Upgrade'),
        ('benefit_redemption', 'Benefit Redemption'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Card Information
    vip_card = models.ForeignKey(
        'accounts.VIPDigitalCard',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='usage_logs'
    )
    premium_card = models.ForeignKey(
        'accounts.PremiumDigitalCard',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='usage_logs'
    )
    
    # Usage Details
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    event_description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Location and Context
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    location_data = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'card_usage_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'event_type']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        card_type = 'VIP' if self.vip_card else 'Premium'
        return f"{card_type} - {self.event_type} by {self.user.email} at {self.timestamp}"