# Premium Digital Card Models
"""
Models for Premium Digital Card system
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import RegexValidator
import uuid
import secrets
import string

User = get_user_model()


class PremiumDigitalCard(models.Model):
    """Premium Digital Card that users can purchase and activate"""
    
    CARD_STATUS_CHOICES = [
        ('available', 'Available for Purchase'),
        ('sold', 'Sold but Not Activated'),
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('suspended', 'Suspended'),
    ]
    
    TIER_CHOICES = [
        ('vip', 'VIP'),
        ('vip_premium', 'VIP Premium'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Card Details
    card_number = models.CharField(
        max_length=16, 
        unique=True,
        help_text="16-digit card number displayed to user"
    )
    verification_code = models.CharField(
        max_length=8,
        unique=True,
        validators=[RegexValidator(regex=r'^\d{8}$', message='Must be exactly 8 digits')],
        help_text="8-digit verification code for activation"
    )
    
    # Card Properties
    tier = models.CharField(max_length=15, choices=TIER_CHOICES, default='vip')
    status = models.CharField(max_length=20, choices=CARD_STATUS_CHOICES, default='available')
    
    # Pricing and Validity
    price = models.DecimalField(max_digits=10, decimal_places=2, default=99.99)
    validity_months = models.PositiveIntegerField(default=12, help_text="Card validity in months")
    
    # User Association
    owner = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='premium_cards'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    purchased_at = models.DateTimeField(null=True, blank=True)
    activated_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    purchase_transaction_id = models.CharField(max_length=100, blank=True, null=True)
    activation_ip = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        db_table = 'premium_digital_cards'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['card_number']),
            models.Index(fields=['verification_code']),
            models.Index(fields=['owner', 'status']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Card {self.card_number} - {self.tier.title()} ({self.status})"
    
    @classmethod
    def generate_card_number(cls):
        """Generate unique 16-digit card number"""
        while True:
            # Generate 16-digit number starting with 4 (like Visa)
            card_number = '4' + ''.join(secrets.choice(string.digits) for _ in range(15))
            if not cls.objects.filter(card_number=card_number).exists():
                return card_number
    
    @classmethod
    def generate_verification_code(cls):
        """Generate unique 8-digit verification code"""
        while True:
            code = ''.join(secrets.choice(string.digits) for _ in range(8))
            if not cls.objects.filter(verification_code=code).exists():
                return code
    
    def activate_card(self, user, ip_address=None):
        """Activate card for a user"""
        if self.status != 'sold':
            raise ValueError("Card must be purchased before activation")
        
        if self.owner != user:
            raise ValueError("Card can only be activated by the owner")
        
        # Activate card
        self.status = 'active'
        self.activated_at = timezone.now()
        self.expires_at = timezone.now() + timezone.timedelta(days=30 * self.validity_months)
        self.activation_ip = ip_address
        self.save()
        
        # Update user tier
        user.tier = self.tier
        user.save()
        
        return True
    
    def is_active(self):
        """Check if card is currently active"""
        if self.status != 'active':
            return False
        
        if self.expires_at and self.expires_at < timezone.now():
            # Auto-expire card
            self.status = 'expired'
            self.save()
            
            # Revert user tier to normal
            if self.owner:
                self.owner.tier = 'normal'
                self.owner.save()
            
            return False
        
        return True
    
    def days_until_expiry(self):
        """Get days until card expires"""
        if not self.expires_at:
            return None
        
        delta = self.expires_at - timezone.now()
        return max(0, delta.days)


class PremiumCardTransaction(models.Model):
    """Track Premium Card purchase transactions"""
    
    TRANSACTION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    card = models.ForeignKey(PremiumDigitalCard, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Transaction Details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS_CHOICES, default='pending')
    
    # Payment Details
    payment_method = models.CharField(max_length=50)  # 'stripe', 'paypal', etc.
    payment_reference = models.CharField(max_length=200, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'premium_card_transactions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Transaction {self.id} - {self.card.card_number} - {self.status}"
