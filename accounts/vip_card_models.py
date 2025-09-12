# VIP Digital Card Models for Serial Number + Activation Code System
"""
Enhanced Digital Card system matching Flutter app requirements
"""

from django.db import models, transaction
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
import uuid
import secrets
import string
import hashlib
from cryptography.fernet import Fernet
from django.conf import settings

User = get_user_model()


class VIPDigitalCard(models.Model):
    """VIP Digital Card with Serial Number and Activation Code system"""
    
    CARD_STATUS_CHOICES = [
        ('inactive', 'Inactive'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('expired', 'Expired'),
        ('revoked', 'Revoked'),
    ]
    
    TIER_CHOICES = [
        ('vip', 'VIP'),
        ('vip_premium', 'VIP Premium'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Card Identification
    serial_number = models.CharField(
        max_length=19,  # VIP-XXXX-XXXX-XXXX or VIPR-XXXX-XXXX-XXXX
        unique=True,
        validators=[RegexValidator(
            regex=r'^(VIP|VIPR)-\d{4}-\d{4}-\d{4}$',
            message='Serial number must be in format VIP-XXXX-XXXX-XXXX or VIPR-XXXX-XXXX-XXXX'
        )],
        help_text="Formatted serial number displayed to user"
    )
    activation_code = models.CharField(
        max_length=12,
        unique=True,
        validators=[RegexValidator(
            regex=r'^[A-Z0-9]{8,12}$',
            message='Activation code must be 8-12 alphanumeric characters'
        )],
        help_text="Alphanumeric activation code for card activation"
    )
    
    # Card Properties
    tier = models.CharField(max_length=15, choices=TIER_CHOICES)
    status = models.CharField(max_length=20, choices=CARD_STATUS_CHOICES, default='inactive')
    
    # Card Features (JSON field for flexibility)
    card_features = models.JSONField(default=dict, help_text="JSON object containing card-specific features")
    
    # Card Design
    primary_color = models.CharField(max_length=7, default='#FFD700')  # Hex color
    secondary_color = models.CharField(max_length=7, default='#FF8C00')  # Hex color
    background_image = models.URLField(blank=True, null=True)
    hologram_pattern = models.CharField(max_length=50, default='diamond')
    logo_url = models.URLField(blank=True, null=True)
    
    # Ownership and Validity
    activated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='activated_vip_cards'
    )
    issued_date = models.DateTimeField(auto_now_add=True)
    activated_date = models.DateTimeField(null=True, blank=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    
    # Security and Tracking
    activation_ip = models.GenericIPAddressField(null=True, blank=True)
    encrypted_metadata = models.TextField(blank=True, help_text="Encrypted sensitive card data")
    
    class Meta:
        db_table = 'vip_digital_cards'
        ordering = ['-issued_date']
        indexes = [
            models.Index(fields=['serial_number']),
            models.Index(fields=['activation_code']),
            models.Index(fields=['activated_by', 'status']),
            models.Index(fields=['tier', 'status']),
        ]
    
    def __str__(self):
        return f"{self.serial_number} - {self.tier.upper()} ({self.status})"
    
    def save(self, *args, **kwargs):
        """Auto-generate serial number, activation code, features, and metadata on creation"""
        if not self.serial_number:
            self.serial_number = self.generate_serial_number(self.tier)
        if not self.activation_code:
            self.activation_code = self.generate_activation_code()
        if not self.card_features or self.card_features == {}:
            self.card_features = VIPDigitalCard.get_tier_features(self.tier)
        if not self.encrypted_metadata or self.encrypted_metadata == '':
            self.encrypted_metadata = self.generate_encrypted_metadata()
        super().save(*args, **kwargs)
    
    @classmethod
    def generate_serial_number(cls, tier):
        """Generate unique serial number based on tier"""
        prefix = 'VIPR' if tier == 'vip_premium' else 'VIP'
        
        while True:
            # Generate three 4-digit groups
            groups = [
                ''.join(secrets.choice(string.digits) for _ in range(4))
                for _ in range(3)
            ]
            serial_number = f"{prefix}-{'-'.join(groups)}"
            
            if not cls.objects.filter(serial_number=serial_number).exists():
                return serial_number
    
    @classmethod
    def generate_activation_code(cls):
        """Generate unique activation code"""
        while True:
            # Generate 10-character alphanumeric code
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(10))
            if not cls.objects.filter(activation_code=code).exists():
                return code
    
    def generate_encrypted_metadata(self):
        """Generate encrypted metadata for the card"""
        import json
        
        metadata = {
            "card_type": self.tier.upper(),
            "security_level": "high" if self.tier == 'vip_premium' else "medium",
            "encryption_key_id": f"{self.tier}_2025",
            "access_permissions": {
                "hotel_booking": self.tier == 'vip_premium',
                "encrypted_gps": self.tier == 'vip_premium',
                "premium_fleet": True,
                "concierge_access": True,
                "armored_vehicles": self.tier == 'vip_premium'
            },
            "compliance": {
                "ndpr_compliant": True,
                "data_retention_days": 365 if self.tier == 'vip_premium' else 180,
                "encryption_standard": "AES-256-GCM"
            },
            "tier_specific": {
                "commission_rate": "25-30%" if self.tier == 'vip_premium' else "20-25%",
                "priority_level": 1 if self.tier == 'vip_premium' else 2,
                "enhanced_verification": self.tier == 'vip_premium',
                "hotel_partnerships": self.tier == 'vip_premium'
            },
            "generated_at": timezone.now().isoformat(),
            "card_id": str(self.id) if self.id else "pending"
        }
        
        # Convert to JSON string and encrypt (basic implementation)
        metadata_json = json.dumps(metadata, sort_keys=True)
        
        # Simple base64 encoding for now (in production, use proper encryption)
        import base64
        encoded_metadata = base64.b64encode(metadata_json.encode()).decode()
        
        return encoded_metadata
    
    @classmethod
    def create_card(cls, tier, features=None):
        """Create a new VIP card with auto-generated serial and activation code"""
        if tier not in ['vip', 'vip_premium']:
            raise ValueError("Tier must be 'vip' or 'vip_premium'")
        
        # Set default features based on tier
        default_features = cls.get_tier_features(tier)
        if features:
            default_features.update(features)
        
        # Set colors based on tier
        colors = cls.get_tier_colors(tier)
        
        card = cls.objects.create(
            serial_number=cls.generate_serial_number(tier),
            activation_code=cls.generate_activation_code(),
            tier=tier,
            card_features=default_features,
            primary_color=colors['primary'],
            secondary_color=colors['secondary']
        )
        
        return card
    
    @staticmethod
    def get_tier_colors(tier):
        """Get default colors for a tier"""
        if tier == 'vip':
            return {
                'primary': '#FFD700',  # Gold
                'secondary': '#FF8C00'  # Dark Orange
            }
        elif tier == 'vip_premium':
            return {
                'primary': '#9932CC',  # Dark Orchid
                'secondary': '#4B0082'  # Indigo
            }
        else:
            return {
                'primary': '#808080',  # Gray
                'secondary': '#A9A9A9'  # Dark Gray
            }
    
    def activate_card(self, user, client_ip=None, user_agent='', method='mobile_app', admin_user=None):
        """
        Activate card for a user and automatically update their tier
        """
        from django.db import transaction
        from .models import User
        from .activation_history_models import CardActivationHistory
        
        if self.status != 'inactive':
            raise ValueError(f"Card is already {self.status} and cannot be activated")
        
        if self.activated_by is not None:
            raise ValueError("Card has already been activated by another user")
        
        # Create activation history record
        activation_record = CardActivationHistory.create_vip_activation_record(
            vip_card=self,
            user=user,
            ip_address=client_ip,
            user_agent=user_agent,
            method=method,
            admin_user=admin_user
        )
        
        # Use transaction to ensure atomicity
        try:
            with transaction.atomic():
                # Activate the card
                self.status = 'active'
                self.activated_by = user
                self.activated_date = timezone.now()
                self.activation_ip = client_ip
                
                # Set expiry date (1 year for VIP, 18 months for VIP Premium)
                if self.tier == 'vip':
                    self.expiry_date = timezone.now() + timezone.timedelta(days=365)
                elif self.tier == 'vip_premium':
                    self.expiry_date = timezone.now() + timezone.timedelta(days=547)  # 18 months
                
                self.save()
                
                # Update user tier automatically (no duplicate users)
                old_tier = user.tier
                user.tier = self.tier
                
                # Automatically enable MFA for VIP and VIP Premium users
                if self.tier in ['vip', 'vip_premium']:
                    user.enable_mfa_for_tier(save=False)
                
                user.save()
                
                # Mark activation as successful
                activation_record.mark_successful()
                
                return True
                
        except Exception as e:
            # Mark activation as failed
            activation_record.mark_failed(str(e))
            raise
            
            # Create activation history record
            CardActivationHistory.objects.create(
                card=self,
                user=user,
                client_ip=client_ip,
                previous_tier=old_tier,
                new_tier=self.tier
            )
            
            return True
    
    def deactivate_card(self, reason="Manual deactivation"):
        """
        Deactivate card and optionally revert user tier
        """
        from django.db import transaction
        
        if self.status != 'active':
            raise ValueError(f"Card is not active (current status: {self.status})")
        
        with transaction.atomic():
            # Deactivate the card
            old_status = self.status
            self.status = 'suspended'
            self.save()
            
            # Create deactivation history
            CardActivationHistory.objects.create(
                card=self,
                user=self.activated_by,
                client_ip=None,
                previous_tier=self.activated_by.tier if self.activated_by else 'regular',
                new_tier='regular',
                notes=f"Card deactivated: {reason}"
            )
            
            # Optionally revert user to regular tier
            if self.activated_by:
                # Check if user has other active VIP cards
                other_active_cards = VIPDigitalCard.objects.filter(
                    activated_by=self.activated_by,
                    status='active'
                ).exclude(id=self.id)
                
                if not other_active_cards.exists():
                    # No other active cards, revert to regular
                    self.activated_by.tier = 'regular'
                    self.activated_by.save()
                else:
                    # Has other active cards, keep highest tier
                    highest_tier = 'regular'
                    for card in other_active_cards:
                        if card.tier == 'vip_premium':
                            highest_tier = 'vip_premium'
                            break
                        elif card.tier == 'vip' and highest_tier == 'regular':
                            highest_tier = 'vip'
                    
                    self.activated_by.tier = highest_tier
                    self.activated_by.save()
            
            return True
    
    @property
    def is_expired(self):
        """Check if card has expired"""
        return self.expiry_date and timezone.now() > self.expiry_date
    
    @property
    def days_until_expiry(self):
        """Get days until card expires"""
        if not self.expiry_date:
            return None
        
        delta = self.expiry_date - timezone.now()
        return max(0, delta.days)
    
    @property
    def can_be_activated(self):
        """Check if card can be activated"""
        return (
            self.status == 'inactive' and 
            not self.is_expired and 
            self.activated_by is None
        )
    
    @staticmethod
    def get_tier_features(tier):
        """Get default features for a tier"""
        tier_lower = tier.lower() if tier else ''
        
        if tier_lower in ['vip', 'vip']:
            return {
                'priority_matching': True,
                'discrete_booking': True,
                'premium_vehicles': True,
                'vip_drivers': True,
                'concierge_support': True,
                'enhanced_sos': True,
                'exclusive_discounts': True,
                'priority_support': True,
            }
        elif tier_lower in ['vip_premium', 'vip premium']:
            return {
                'priority_matching': True,
                'discrete_booking': True,
                'premium_vehicles': True,
                'vip_drivers': True,
                'concierge_support': True,
                'enhanced_sos': True,
                'exclusive_discounts': True,
                'priority_support': True,
                'hotel_partnerships': True,
                'encrypted_tracking': True,
                'high_security_vehicles': True,
                'hotel_staff_integration': True,
                'advanced_sos_gps': True,
                'vip_lounge_access': True,
                'partnership_perks': True,
                'armored_vehicles': True,
            }
        else:
            return {}


class CardBatchGeneration(models.Model):
    """Track batch generation of VIP cards for admin purposes"""
    
    BATCH_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('generated', 'Generated'),
        ('distributed', 'Distributed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    batch_id = models.CharField(max_length=50, unique=True)
    tier = models.CharField(max_length=15, choices=VIPDigitalCard.TIER_CHOICES)
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=BATCH_STATUS_CHOICES, default='pending')
    generated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='generated_card_batches'
    )
    generated_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    # Track distribution
    distributed_to = models.CharField(max_length=255, blank=True, help_text="Where cards were distributed")
    distributed_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'card_batch_generation'
        ordering = ['-generated_date']
        indexes = [
            models.Index(fields=['batch_id']),
            models.Index(fields=['tier', 'status']),
            models.Index(fields=['generated_by', 'generated_date']),
        ]
    
    def __str__(self):
        return f"Batch {self.batch_id} - {self.quantity} {self.tier.upper()} cards ({self.status})"
    
    @classmethod
    def generate_batch_id(cls, tier, quantity):
        """Generate unique batch ID"""
        from datetime import datetime
        
        tier_prefix = 'VIPR' if tier == 'vip_premium' else 'VIP'
        timestamp = datetime.now().strftime('%Y%m%d%H%M')
        return f"{tier_prefix}_BATCH_{timestamp}_{quantity}"
    
    def generate_cards(self):
        """Generate the actual VIP cards for this batch"""
        if self.status != 'pending':
            raise ValueError(f"Cannot generate cards for batch with status: {self.status}")
        
        cards_created = []
        
        try:
            with transaction.atomic():
                for i in range(self.quantity):
                    card = VIPDigitalCard.create_card(
                        tier=self.tier,
                        features={'batch_id': self.batch_id, 'batch_index': i + 1}
                    )
                    cards_created.append(card)
                
                # Update batch status
                self.status = 'generated'
                self.save()
                
                return cards_created
                
        except Exception as e:
            # If any error occurs, ensure no partial creation
            raise ValueError(f"Failed to generate batch: {str(e)}")
    
    @property
    def cards(self):
        """Get all cards in this batch"""
        return VIPDigitalCard.objects.filter(
            card_features__batch_id=self.batch_id
        )
    
    def activate_card(self, user, ip_address=None):
        """Activate card for a user"""
        if self.status != 'inactive':
            raise ValueError(f"Card cannot be activated. Current status: {self.status}")
        
        if self.is_expired():
            raise ValueError("Card has expired and cannot be activated")
        
        # Check if user already has an active card of the same or higher tier
        existing_card = VIPDigitalCard.objects.filter(
            activated_by=user,
            status='active'
        ).first()
        
        if existing_card:
            # If user has VIP Premium, don't allow VIP activation
            if existing_card.tier == 'vip_premium' and self.tier == 'vip':
                raise ValueError("Cannot activate lower tier card when VIP Premium is active")
            
            # Deactivate existing card if new card is higher tier
            if self.tier == 'vip_premium' and existing_card.tier == 'vip':
                existing_card.status = 'suspended'
                existing_card.save()
        
        # Activate card
        self.status = 'active'
        self.activated_by = user
        self.activated_date = timezone.now()
        self.activation_ip = ip_address
        
        # Set expiry date (VIP Premium: 18 months, VIP: 12 months)
        months = 18 if self.tier == 'vip_premium' else 12
        self.expiry_date = timezone.now() + timezone.timedelta(days=30 * months)
        
        self.save()
        
        # Update user tier
        user.tier = self.tier
        user.save()
        
        return True
    
    def deactivate_card(self, reason='manual'):
        """Deactivate card"""
        if self.status == 'active':
            self.status = 'suspended'
            self.save()
            
            # Check if user should be downgraded
            if self.activated_by:
                active_cards = VIPDigitalCard.objects.filter(
                    activated_by=self.activated_by,
                    status='active'
                ).exclude(id=self.id)
                
                if active_cards.exists():
                    # User has other active cards, use highest tier
                    highest_tier_card = active_cards.order_by(
                        models.Case(
                            models.When(tier='vip_premium', then=1),
                            models.When(tier='vip', then=2),
                            default=3
                        )
                    ).first()
                    self.activated_by.tier = highest_tier_card.tier
                else:
                    # No other active cards, downgrade to regular
                    self.activated_by.tier = 'regular'
                
                self.activated_by.save()
        
        return True
    
    def is_active(self):
        """Check if card is currently active and not expired"""
        if self.status != 'active':
            return False
        
        if self.is_expired():
            # Auto-expire card
            self.status = 'expired'
            self.save()
            
            # Update user tier if this was their only active card
            if self.activated_by:
                active_cards = VIPDigitalCard.objects.filter(
                    activated_by=self.activated_by,
                    status='active'
                ).exclude(id=self.id)
                
                if not active_cards.exists():
                    self.activated_by.tier = 'regular'
                    self.activated_by.save()
            
            return False
        
        return True
    
    def is_expired(self):
        """Check if card has expired"""
        if not self.expiry_date:
            return False
        return timezone.now() > self.expiry_date
    
    def days_until_expiry(self):
        """Get days until card expires"""
        if not self.expiry_date:
            return None
        
        delta = self.expiry_date - timezone.now()
        return max(0, delta.days)
    
    def get_tier_benefits(self):
        """Get list of benefits for this card's tier"""
        if self.tier == 'vip':
            return [
                'Priority ride matching with top-rated drivers',
                'Discrete booking mode for privacy',
                'Access to premium vehicle fleet',
                'VIP-exclusive driver network',
                '24/7 concierge support',
                'Enhanced SOS emergency system',
                'Priority customer support',
                'Exclusive ride discounts',
            ]
        elif self.tier == 'vip_premium':
            return [
                'All VIP tier benefits included',
                'Exclusive hotel partnership access',
                'Encrypted GPS tracking for security',
                'High-security armored vehicles',
                'Direct hotel staff integration',
                'Advanced SOS with live GPS feed',
                'VIP lounge access at partner hotels',
                'Complimentary hotel upgrades',
                'Priority airport transfers',
                'Personal concierge at partner properties',
            ]
        else:
            return []



