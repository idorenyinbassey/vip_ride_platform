# pricing/signals.py
"""
Pricing system signals for automated business logic
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.cache import cache
from decimal import Decimal

from .models import PriceCalculationLog, PromotionalCode, DemandSurge


@receiver(post_save, sender=PriceCalculationLog)
def update_pricing_cache(sender, instance, created, **kwargs):
    """Update pricing cache when new calculations are logged"""
    if created:
        # Clear general pricing cache
        cache.delete('pricing_calculations_cache')
        
        # Log the pricing update
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Pricing cache updated for calculation {instance.id}")


@receiver(post_save, sender=PromotionalCode)
def handle_promo_code_changes(sender, instance, created, **kwargs):
    """Handle promotional code creation and updates"""
    if created:
        # Clear promotional codes cache
        cache.delete('active_promo_codes')
        
        # Log promo code creation
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"New promotional code created: {instance.code} "
                   f"({instance.discount_type}: {instance.discount_value})")
    
    elif not instance.is_active:
        # Clear cache when code is deactivated
        cache.delete('active_promo_codes')
        cache.delete(f'promo_code_{instance.code}')


@receiver(pre_save, sender=PromotionalCode)
def validate_promo_code(sender, instance, **kwargs):
    """Validate promotional code before saving"""
    # Ensure usage count doesn't exceed max_uses
    if instance.max_uses > 0 and instance.usage_count > instance.max_uses:
        instance.is_active = False
    
    # Deactivate expired codes
    if instance.expires_at and timezone.now() > instance.expires_at:
        instance.is_active = False


@receiver(post_save, sender=DemandSurge)
def handle_surge_changes(sender, instance, created, **kwargs):
    """Handle surge pricing changes"""
    if instance.zone:
        # Clear zone surge cache
        cache_key = f"surge_zone_{instance.zone.id}"
        cache.delete(cache_key)
        
        # Update zone's surge status
        if instance.is_active and instance.surge_multiplier > 1:
            cache.set(f"surge_active_{instance.zone.id}", True, 300)  # 5 min cache
        else:
            cache.delete(f"surge_active_{instance.zone.id}")


@receiver(post_save, sender=DemandSurge)
def log_surge_activity(sender, instance, created, **kwargs):
    """Log surge pricing activities"""
    import logging
    logger = logging.getLogger(__name__)
    
    if created:
        logger.info(f"Surge pricing activated for {instance.zone.name}: "
                   f"{instance.surge_multiplier}x multiplier")
    elif not instance.is_active:
        logger.info(f"Surge pricing deactivated for {instance.zone.name}")


def update_demand_metrics():
    """
    Update demand metrics for all zones
    This should be called periodically (every 5-10 minutes)
    """
    from .models import PricingZone
    from django.db.models import Count, Avg
    from datetime import timedelta
    
    # Get all active zones
    zones = PricingZone.objects.filter(is_active=True)
    
    for zone in zones:
        # Calculate demand metrics for the last hour
        one_hour_ago = timezone.now() - timedelta(hours=1)
        
        # Get recent ride requests in this zone
        # NOTE: This assumes you have a Ride model with location data
        try:
            from rides.models import Ride
            recent_rides = Ride.objects.filter(
                created_at__gte=one_hour_ago,
                pickup_latitude__gte=zone.min_latitude,
                pickup_latitude__lte=zone.max_latitude,
                pickup_longitude__gte=zone.min_longitude,
                pickup_longitude__lte=zone.max_longitude
            )
            
            ride_count = recent_rides.count()
            avg_wait_time = recent_rides.aggregate(
                avg_wait=Avg('driver_arrival_time')
            )['avg_wait'] or 0
            
            # Calculate demand score (rides per hour)
            demand_score = ride_count
            
            # Determine if surge should be activated
            surge_threshold = 5  # rides per hour
            surge_multiplier = Decimal('1.0')
            
            if demand_score >= surge_threshold:
                # Calculate surge multiplier based on demand
                if demand_score >= 15:
                    surge_multiplier = Decimal('3.0')
                elif demand_score >= 10:
                    surge_multiplier = Decimal('2.0')
                else:
                    surge_multiplier = Decimal('1.5')
                
                # Create or update surge pricing
                surge, created = DemandSurge.objects.get_or_create(
                    zone=zone,
                    defaults={
                        'surge_multiplier': surge_multiplier,
                        'demand_ratio': Decimal(str(demand_score)),
                        'is_active': True,
                        'calculated_at': timezone.now()
                    }
                )
                
                if not created and surge.surge_multiplier != surge_multiplier:
                    surge.surge_multiplier = surge_multiplier
                    surge.demand_ratio = Decimal(str(demand_score))
                    surge.is_active = True
                    surge.save()
            
            else:
                # Deactivate surge if demand is low
                DemandSurge.objects.filter(zone=zone, is_active=True).update(
                    is_active=False,
                    expires_at=timezone.now()
                )
        
        except ImportError:
            # rides app not available, skip demand calculation
            pass


def cleanup_old_pricing_data():
    """
    Clean up old pricing data to prevent database bloat
    This should be called daily
    """
    from datetime import timedelta
    
    # Delete old price calculation logs (older than 30 days)
    cutoff_date = timezone.now() - timedelta(days=30)
    
    deleted_logs = PriceCalculationLog.objects.filter(
        created_at__lt=cutoff_date
    ).delete()
    
    # Delete inactive surge records (older than 7 days)
    surge_cutoff = timezone.now() - timedelta(days=7)
    deleted_surge = DemandSurge.objects.filter(
        is_active=False,
        end_time__lt=surge_cutoff
    ).delete()
    
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Pricing cleanup: {deleted_logs[0]} logs, {deleted_surge[0]} surge records deleted")
