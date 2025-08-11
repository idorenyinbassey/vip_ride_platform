"""
VIP Ride-Hailing Platform - Pricing Celery Tasks
Background tasks for automated surge pricing updates
"""

from celery import shared_task
from django.utils import timezone
from django.core.cache import cache
from django.db.models import Max, Avg, Count, Sum, F
from decimal import Decimal
import logging

from .models import PricingZone, DemandSurge, SpecialEvent
from .engines import SurgeManagementService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def update_surge_pricing(self):
    """
    Update surge pricing for all active zones
    Runs every 2-5 minutes during peak hours
    """
    try:
        logger.info("Starting surge pricing update task")
        
        # Get all active zones
        active_zones = PricingZone.objects.filter(
            is_active=True, 
            surge_enabled=True
        )
        
        updated_zones = 0
        for zone in active_zones:
            try:
                SurgeManagementService.update_zone_surge(str(zone.id))
                updated_zones += 1
            except Exception as e:
                logger.error(f"Failed to update surge for zone {zone.name}: {e}")
        
        logger.info(f"Surge pricing updated for {updated_zones} zones")
        
        # Cache the last update time
        cache.set('last_surge_update', timezone.now(), timeout=3600)
        
        return {
            'status': 'success',
            'zones_updated': updated_zones,
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as exc:
        logger.error(f"Surge pricing update failed: {exc}")
        
        # Retry with exponential backoff
        if self.request.retries < self.max_retries:
            retry_delay = 2 ** self.request.retries * 60  # 1, 2, 4 minutes
            logger.info(f"Retrying in {retry_delay} seconds")
            raise self.retry(countdown=retry_delay, exc=exc)
        
        # Final failure
        return {
            'status': 'failed',
            'error': str(exc),
            'timestamp': timezone.now().isoformat()
        }


@shared_task
def cleanup_expired_surge_data():
    """
    Clean up expired surge pricing data
    Runs every hour
    """
    try:
        logger.info("Starting surge data cleanup task")
        
        # Deactivate expired surge records
        expired_count = DemandSurge.objects.filter(
            expires_at__lt=timezone.now(),
            is_active=True
        ).update(is_active=False)
        
        # Delete old surge records (older than 24 hours)
        old_cutoff = timezone.now() - timezone.timedelta(hours=24)
        deleted_count = DemandSurge.objects.filter(
            calculated_at__lt=old_cutoff
        ).delete()[0]
        
        logger.info(
            f"Surge cleanup: {expired_count} expired, {deleted_count} deleted"
        )
        
        return {
            'status': 'success',
            'expired_records': expired_count,
            'deleted_records': deleted_count,
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Surge cleanup failed: {e}")
        return {
            'status': 'failed',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }


@shared_task
def update_event_pricing():
    """
    Update special event pricing multipliers
    Runs every 15 minutes during events
    """
    try:
        logger.info("Starting event pricing update task")
        
        # Get currently active events
        now = timezone.now()
        active_events = SpecialEvent.objects.filter(
            is_active=True,
            start_datetime__lte=now,
            end_datetime__gte=now
        )
        
        updated_events = 0
        for event in active_events:
            try:
                # Update event multiplier based on current time
                current_multiplier = event.get_current_multiplier()
                
                # Log significant multiplier changes
                if hasattr(event, '_cached_multiplier'):
                    old_multiplier = event._cached_multiplier
                    if abs(current_multiplier - old_multiplier) > Decimal('0.1'):
                        logger.info(
                            f"Event {event.name} multiplier changed: "
                            f"{old_multiplier} -> {current_multiplier}"
                        )
                
                event._cached_multiplier = current_multiplier
                updated_events += 1
                
            except Exception as e:
                logger.error(f"Failed to update event {event.name}: {e}")
        
        logger.info(f"Event pricing updated for {updated_events} events")
        
        return {
            'status': 'success',
            'events_updated': updated_events,
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Event pricing update failed: {e}")
        return {
            'status': 'failed',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }


@shared_task
def validate_promotional_codes():
    """
    Validate and deactivate expired promotional codes
    Runs daily
    """
    try:
        logger.info("Starting promotional code validation task")
        
        from .models import PromotionalCode
        
        now = timezone.now()
        
        # Deactivate expired codes
        expired_count = PromotionalCode.objects.filter(
            expires_at__lt=now,
            is_active=True
        ).update(is_active=False)
        
        # Deactivate codes that have reached max usage
        max_used_codes = PromotionalCode.objects.filter(
            usage_count__gte=F('max_uses'),
            max_uses__gt=0,
            is_active=True
        )
        
        max_used_count = 0
        for code in max_used_codes:
            code.is_active = False
            code.save()
            max_used_count += 1
        
        logger.info(
            f"Promo validation: {expired_count} expired, "
            f"{max_used_count} max used"
        )
        
        return {
            'status': 'success',
            'expired_codes': expired_count,
            'max_used_codes': max_used_count,
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Promotional code validation failed: {e}")
        return {
            'status': 'failed',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }


@shared_task
def generate_pricing_analytics():
    """
    Generate pricing analytics and insights
    Runs daily at midnight
    """
    try:
        logger.info("Starting pricing analytics generation task")
        
        from .models import PriceCalculationLog
        from django.db.models import Avg, Count, Sum
        
        # Get today's date
        today = timezone.now().date()
        yesterday = today - timezone.timedelta(days=1)
        
        # Calculate daily statistics
        daily_stats = PriceCalculationLog.objects.filter(
            created_at__date=yesterday
        ).aggregate(
            total_rides=Count('id'),
            avg_price=Avg('final_price'),
            total_revenue=Sum('final_price'),
            avg_surge=Avg('surge_multiplier'),
            total_discount=Sum('promo_discount')
        )
        
        # Calculate surge statistics by zone
        surge_stats = {}
        for zone in PricingZone.objects.filter(is_active=True):
            zone_logs = PriceCalculationLog.objects.filter(
                created_at__date=yesterday,
                pickup_location__within=zone.boundary
            )
            
            if zone_logs.exists():
                surge_stats[zone.name] = {
                    'avg_surge': zone_logs.aggregate(
                        avg=Avg('surge_multiplier')
                    )['avg'] or Decimal('1.0'),
                    'max_surge': zone_logs.aggregate(
                        max=Max('surge_multiplier')
                    )['max'] or Decimal('1.0'),
                    'ride_count': zone_logs.count()
                }
        
        # Cache analytics for reporting
        analytics_data = {
            'date': yesterday.isoformat(),
            'daily_stats': daily_stats,
            'surge_stats': surge_stats,
            'generated_at': timezone.now().isoformat()
        }
        
        cache.set(
            f'pricing_analytics_{yesterday.isoformat()}',
            analytics_data,
            timeout=86400 * 7  # Keep for 7 days
        )
        
        logger.info(f"Pricing analytics generated for {yesterday}")
        
        return {
            'status': 'success',
            'analytics_date': yesterday.isoformat(),
            'total_rides': daily_stats['total_rides'],
            'avg_price': str(daily_stats['avg_price'] or Decimal('0')),
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Pricing analytics generation failed: {e}")
        return {
            'status': 'failed',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }


@shared_task
def send_surge_notifications():
    """
    Send surge pricing notifications to drivers and users
    Runs when high surge detected
    """
    try:
        logger.info("Starting surge notification task")
        
        # Get high surge zones (>2.0x multiplier)
        high_surge_zones = DemandSurge.objects.filter(
            is_active=True,
            surge_multiplier__gte=Decimal('2.0'),
            expires_at__gt=timezone.now()
        ).select_related('zone')
        
        notifications_sent = 0
        
        for surge in high_surge_zones:
            # Check if notification already sent recently
            cache_key = f'surge_notification_{surge.zone.id}'
            if cache.get(cache_key):
                continue
                
            try:
                # Send notification to nearby drivers
                # This would integrate with your notification system
                logger.info(
                    f"High surge alert for {surge.zone.name}: "
                    f"{surge.surge_multiplier}x multiplier"
                )
                
                # Cache to prevent spam notifications
                cache.set(cache_key, True, timeout=1800)  # 30 minutes
                notifications_sent += 1
                
            except Exception as e:
                logger.error(
                    f"Failed to send surge notification for "
                    f"{surge.zone.name}: {e}"
                )
        
        logger.info(f"Sent {notifications_sent} surge notifications")
        
        return {
            'status': 'success',
            'notifications_sent': notifications_sent,
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Surge notification task failed: {e}")
        return {
            'status': 'failed',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }
