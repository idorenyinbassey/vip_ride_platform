"""
Premium Card Batch Generation Models and Admin

Handles bulk generation of Premium Digital Cards for production efficiency.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
import uuid

User = get_user_model()


class PremiumCardBatchGeneration(models.Model):
    """Track batch generation of Premium Digital Cards for admin purposes"""
    
    BATCH_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('generated', 'Generated'),
        ('distributed', 'Distributed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    batch_id = models.CharField(max_length=50, unique=True)
    tier = models.CharField(max_length=15, choices=[
        ('vip', 'VIP'),
        ('vip_premium', 'VIP Premium'),
    ])
    quantity = models.PositiveIntegerField()
    price_per_card = models.DecimalField(max_digits=10, decimal_places=2, default=99.99)
    validity_months = models.PositiveIntegerField(default=12)
    status = models.CharField(max_length=20, choices=BATCH_STATUS_CHOICES, default='pending')
    
    # Generation tracking
    generated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='generated_premium_card_batches'
    )
    generated_date = models.DateTimeField(auto_now_add=True)
    completed_date = models.DateTimeField(null=True, blank=True)
    
    # Distribution tracking
    distributed_to = models.CharField(max_length=255, blank=True, help_text="Where cards were distributed")
    distributed_date = models.DateTimeField(null=True, blank=True)
    distribution_notes = models.TextField(blank=True)
    
    # Additional settings
    notes = models.TextField(blank=True, help_text="Additional notes about this batch")
    
    class Meta:
        db_table = 'premium_card_batch_generation'
        ordering = ['-generated_date']
        indexes = [
            models.Index(fields=['batch_id']),
            models.Index(fields=['tier', 'status']),
            models.Index(fields=['generated_by', 'generated_date']),
        ]
        verbose_name = 'Premium Card Batch Generation'
        verbose_name_plural = 'Premium Card Batch Generations'
    
    def __str__(self):
        return f"Batch {self.batch_id} - {self.quantity} {self.tier.upper()} cards ({self.status})"
    
    def save(self, *args, **kwargs):
        """Auto-generate batch ID if not provided"""
        if not self.batch_id:
            self.batch_id = self.generate_batch_id(self.tier, self.quantity)
        super().save(*args, **kwargs)
    
    @classmethod
    def generate_batch_id(cls, tier, quantity):
        """Generate unique batch ID"""
        from datetime import datetime
        
        tier_prefix = 'PREM' if tier == 'vip_premium' else 'VIP'
        timestamp = datetime.now().strftime('%Y%m%d%H%M')
        return f"{tier_prefix}_BATCH_{timestamp}_{quantity}"
    
    def generate_cards(self):
        """Generate the actual Premium Digital Cards for this batch"""
        from .premium_card_models import PremiumDigitalCard
        
        if self.status != 'pending':
            raise ValueError(f"Cannot generate cards for batch with status: {self.status}")
        
        cards_created = []
        
        try:
            with transaction.atomic():
                for i in range(self.quantity):
                    card = PremiumDigitalCard.objects.create(
                        tier=self.tier,
                        price=self.price_per_card,
                        validity_months=self.validity_months,
                        status='available',  # Cards start as available for purchase
                        batch_generation=self  # Link card to this batch
                    )
                    cards_created.append(card)
                
                # Update batch status
                self.status = 'generated'
                self.completed_date = timezone.now()
                self.save()
                
                return cards_created
                
        except Exception as e:
            # If generation fails, mark batch as cancelled
            self.status = 'cancelled'
            self.notes = f"Generation failed: {str(e)}"
            self.save()
            raise
    
    def mark_distributed(self, distributed_to, notes=""):
        """Mark batch as distributed"""
        if self.status != 'generated':
            raise ValueError("Can only distribute generated batches")
        
        self.status = 'distributed'
        self.distributed_to = distributed_to
        self.distributed_date = timezone.now()
        self.distribution_notes = notes
        self.save()
    
    def get_generated_cards(self):
        """Get all cards generated in this batch"""
        # Use the proper relationship to get cards linked to this batch
        return self.generated_cards.all()
    
    @property
    def total_value(self):
        """Calculate total value of the batch"""
        return self.quantity * self.price_per_card
    
    @property
    def cards_generated_count(self):
        """Count of cards actually generated"""
        return self.get_generated_cards().count()
    
    @property
    def success_rate(self):
        """Success rate of card generation"""
        if self.quantity == 0:
            return 0
        return (self.cards_generated_count / self.quantity) * 100