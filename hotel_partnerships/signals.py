from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import HotelBooking, HotelCommissionReport, PMSIntegrationLog
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=HotelBooking)
def booking_status_changed(sender, instance, created, **kwargs):
    """Handle booking status changes and commission calculations"""
    
    if created:
        # Log booking creation
        logger.info(f"New hotel booking created: {instance.booking_reference}")
        
        # Calculate initial commission (avoid double save)
        if instance.final_fare and instance.hotel.commission_rate:
            commission = instance.calculate_commission()
            # Use update to avoid triggering signals again
            HotelBooking.objects.filter(id=instance.id).update(
                hotel_commission=commission,
                commission_rate_used=instance.hotel.commission_rate
            )
        
        # Log PMS integration attempt
        if instance.hotel.pms_type != 'NONE':
            PMSIntegrationLog.objects.create(
                hotel=instance.hotel,
                action_type='BOOKING_CREATE',
                booking_reference=instance.booking_reference,
                success=True,  # TODO: Implement actual PMS integration
                request_data={
                    'booking_reference': instance.booking_reference,
                    'guest_name': instance.guest_name,
                    'pickup_datetime': instance.pickup_datetime.isoformat(),
                    'destination': instance.destination
                }
            )
    
    else:
        # Handle status updates
        if instance.status == 'COMPLETED' and not instance.completed_at:
            # Use update to avoid double saves
            HotelBooking.objects.filter(id=instance.id).update(
                completed_at=timezone.now()
            )
            
            # Recalculate commission if final fare is set
            if instance.final_fare:
                commission = instance.calculate_commission()
                HotelBooking.objects.filter(id=instance.id).update(
                    hotel_commission=commission,
                    commission_rate_used=instance.hotel.commission_rate
                )
            
            logger.info(f"Booking completed: {instance.booking_reference}")


@receiver(pre_save, sender=HotelBooking)
def validate_booking_data(sender, instance, **kwargs):
    """Validate booking data before saving"""
    
    # Ensure pickup time is in the future for new bookings
    if not instance.pk and instance.pickup_datetime <= timezone.now():
        raise ValueError("Pickup time must be in the future")
    
    # Validate passenger count
    if instance.passenger_count < 1 or instance.passenger_count > 8:
        raise ValueError("Passenger count must be between 1 and 8")
    
    # Auto-generate booking reference if not set
    if not instance.booking_reference:
        instance.booking_reference = instance.generate_booking_reference()


def create_monthly_commission_reports():
    """
    Create monthly commission reports for all active hotels
    This should be called by a cron job at the end of each month
    """
    from django.db.models import Sum, Count, Avg
    from decimal import Decimal
    from datetime import date
    
    # Get last month's first day
    today = date.today()
    if today.month == 1:
        report_month = date(today.year - 1, 12, 1)
    else:
        report_month = date(today.year, today.month - 1, 1)
    
    # Get all active hotels
    from .models import Hotel
    active_hotels = Hotel.objects.filter(status='ACTIVE')
    
    for hotel in active_hotels:
        # Check if report already exists
        if HotelCommissionReport.objects.filter(
            hotel=hotel, 
            report_month=report_month
        ).exists():
            continue
        
        # Get bookings for the month
        month_bookings = HotelBooking.objects.filter(
            hotel=hotel,
            created_at__year=report_month.year,
            created_at__month=report_month.month
        )
        
        # Calculate metrics
        total_bookings = month_bookings.count()
        completed_bookings = month_bookings.filter(status='COMPLETED').count()
        cancelled_bookings = month_bookings.filter(status='CANCELLED').count()
        
        # Financial calculations
        completed_rides = month_bookings.filter(
            status='COMPLETED', 
            final_fare__isnull=False
        )
        
        financial_data = completed_rides.aggregate(
            total_value=Sum('final_fare'),
            total_commission=Sum('hotel_commission'),
            avg_commission_rate=Avg('commission_rate_used')
        )
        
        total_ride_value = financial_data['total_value'] or Decimal('0.00')
        total_commission = financial_data['total_commission'] or Decimal('0.00')
        avg_commission_rate = financial_data['avg_commission_rate'] or Decimal('0.00')
        
        # Create detailed breakdown
        detailed_data = {
            'booking_types': list(
                month_bookings.values('booking_type')
                .annotate(count=Count('id'))
                .order_by('-count')
            ),
            'vehicle_types': list(
                month_bookings.values('vehicle_type')
                .annotate(count=Count('id'))
                .order_by('-count')
            ),
            'daily_breakdown': {},  # TODO: Add daily breakdown
            'top_destinations': list(
                completed_rides.values('destination')
                .annotate(count=Count('id'))
                .order_by('-count')[:10]
            )
        }
        
        # Create the report
        HotelCommissionReport.objects.create(
            hotel=hotel,
            report_month=report_month,
            total_bookings=total_bookings,
            completed_bookings=completed_bookings,
            cancelled_bookings=cancelled_bookings,
            total_ride_value=total_ride_value,
            total_commission_earned=total_commission,
            average_commission_rate=avg_commission_rate,
            detailed_data=detailed_data,
            payment_due_date=date(
                report_month.year + (1 if report_month.month >= 12 else 0),
                1 if report_month.month >= 12 else report_month.month + 1,
                15
            )
        )
        
        logger.info(f"Created commission report for {hotel.name} - {report_month}")


def send_hotel_notification(booking, update_type, data=None):
    """
    Send real-time notification to hotel systems
    This integrates with hotel PMS and communication systems
    """
    if not booking.hotel.send_real_time_updates:
        return
    
    notification_data = {
        'booking_reference': booking.booking_reference,
        'hotel_id': str(booking.hotel.id),
        'update_type': update_type,
        'timestamp': timezone.now().isoformat(),
        'status': booking.status,
        'guest_name': booking.guest_name,
        'guest_room': booking.guest_room_number,
        'pickup_datetime': booking.pickup_datetime.isoformat(),
        'destination': booking.destination,
    }
    
    if data:
        notification_data.update(data)
    
    # TODO: Implement actual notification sending
    # This could be:
    # 1. WebSocket push to hotel portal
    # 2. HTTP webhook to hotel PMS
    # 3. SMS/Email to hotel staff
    # 4. Integration with hotel communication systems
    
    logger.info(f"Notification sent to {booking.hotel.name}: {update_type}")
    
    # Log the notification attempt
    PMSIntegrationLog.objects.create(
        hotel=booking.hotel,
        action_type='STATUS_UPDATE',
        booking_reference=booking.booking_reference,
        success=True,  # TODO: Based on actual sending result
        request_data=notification_data
    )
