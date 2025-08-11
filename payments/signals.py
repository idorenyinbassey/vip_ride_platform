# payments/signals.py
"""
Payment system signals for automated business logic
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from decimal import Decimal

from .payment_models import Payment, PaymentAuditLog, DriverPayout
from accounts.models import UserTier


@receiver(pre_save, sender=Payment)
def calculate_payment_amounts(sender, instance, **kwargs):
    """Auto-calculate commission and net amounts before saving payment"""
    if instance.amount and instance.user_tier:
        # Calculate commission based on user tier
        instance.calculate_commission()
        
        # Calculate net amount (amount - fees)
        gateway_fee = instance.gateway_fee or Decimal('0.00')
        platform_fee = instance.platform_fee or Decimal('0.00')
        instance.net_amount = instance.amount - gateway_fee - platform_fee


@receiver(post_save, sender=Payment)
def log_payment_activity(sender, instance, created, **kwargs):
    """Create audit log entry for payment activities"""
    if created:
        action_type = PaymentAuditLog.ActionType.PAYMENT_CREATED
        description = f"Payment {instance.id} created for {instance.amount} {instance.currency.code}"
    else:
        action_type = PaymentAuditLog.ActionType.PAYMENT_PROCESSED
        description = f"Payment {instance.id} updated to status: {instance.status}"
    
    PaymentAuditLog.objects.create(
        action_type=action_type,
        description=description,
        payment=instance,
        user=getattr(instance, 'user', None),
        metadata={
            'amount': str(instance.amount),
            'currency': instance.currency.code,
            'status': instance.status,
            'gateway': instance.gateway.name if instance.gateway else None
        }
    )


@receiver(post_save, sender=Payment)
def handle_successful_payment(sender, instance, **kwargs):
    """Handle successful payment completion"""
    if instance.status == Payment.PaymentStatus.SUCCEEDED:
        # Update processed timestamp
        if not instance.processed_at:
            instance.processed_at = timezone.now()
            Payment.objects.filter(id=instance.id).update(processed_at=instance.processed_at)
        
        # Log successful payment
        PaymentAuditLog.objects.create(
            action_type=PaymentAuditLog.ActionType.PAYMENT_PROCESSED,
            description=f"Payment {instance.id} successfully completed",
            payment=instance,
            metadata={
                'net_amount': str(instance.net_amount),
                'commission': str(instance.commission_amount),
                'driver_payout': str(instance.driver_payout_amount)
            }
        )


@receiver(post_save, sender=Payment)
def handle_failed_payment(sender, instance, **kwargs):
    """Handle failed payment"""
    if instance.status == Payment.PaymentStatus.FAILED:
        # Update failed timestamp
        if not instance.failed_at:
            instance.failed_at = timezone.now()
            Payment.objects.filter(id=instance.id).update(failed_at=instance.failed_at)
        
        # Log failed payment
        PaymentAuditLog.objects.create(
            action_type=PaymentAuditLog.ActionType.PAYMENT_FAILED,
            description=f"Payment {instance.id} failed: {instance.failure_reason}",
            payment=instance,
            metadata={
                'failure_reason': instance.failure_reason,
                'retry_count': instance.retry_count
            }
        )


@receiver(post_save, sender=DriverPayout)
def log_payout_activity(sender, instance, created, **kwargs):
    """Log driver payout activities"""
    if created:
        PaymentAuditLog.objects.create(
            action_type=PaymentAuditLog.ActionType.PAYOUT_PROCESSED,
            description=f"Driver payout {instance.id} created for {instance.net_payout_amount} {instance.currency.code}",
            payout=instance,
            metadata={
                'driver_id': str(instance.driver.id) if instance.driver else None,
                'gross_earnings': str(instance.gross_earnings),
                'net_payout': str(instance.net_payout_amount),
                'status': instance.status
            }
        )
