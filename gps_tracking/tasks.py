"""
Celery tasks for GPS tracking and route optimization
"""

from celery import shared_task
# from django.contrib.gis.geos import Point  # Removed GeoDjango dependency
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import logging

from .models import RouteOptimization, GPSLocation, GeofenceEvent
from .services import RouteOptimizationService, GeofenceService

logger = logging.getLogger(__name__)
channel_layer = get_channel_layer()


@shared_task(bind=True, max_retries=3)
def calculate_route_optimization(self, route_optimization_id):
    """
    Calculate optimized route using Google Maps API
    """
    try:
        route_optimization = RouteOptimization.objects.get(
            id=route_optimization_id
        )
        
        route_service = RouteOptimizationService()
        
        # Calculate optimized route
        route_data = route_service.calculate_optimized_route(
            route_optimization.pickup_point,
            route_optimization.dropoff_point,
            waypoints=route_optimization.waypoints
        )
        
        # Update route optimization
        route_optimization.distance_meters = route_data['distance_meters']
        route_optimization.duration_seconds = route_data['duration_seconds']
        route_optimization.duration_in_traffic_seconds = route_data.get(
            'duration_in_traffic_seconds'
        )
        route_optimization.route_polyline = route_data['polyline']
        route_optimization.traffic_level = route_data['traffic_level']
        route_optimization.status = 'OPTIMIZED'
        
        # Calculate ETA
        eta_seconds = (route_data.get('duration_in_traffic_seconds') or 
                      route_data['duration_seconds'])
        route_optimization.current_eta = (
            timezone.now() + timezone.timedelta(seconds=eta_seconds)
        )
        
        route_optimization.save()
        
        # Notify WebSocket clients
        async_to_sync(channel_layer.group_send)(
            f"ride_{route_optimization.ride.id}",
            {
                'type': 'route_update',
                'route_id': str(route_optimization.id),
                'eta': route_optimization.current_eta.isoformat(),
                'distance_meters': route_optimization.distance_meters,
                'traffic_level': route_optimization.traffic_level,
                'status': route_optimization.status
            }
        )
        
        logger.info(f"Route optimization calculated for ride {route_optimization.ride.id}")
        
    except RouteOptimization.DoesNotExist:
        logger.error(f"Route optimization {route_optimization_id} not found")
    except Exception as e:
        logger.error(f"Route calculation error: {str(e)}")
        
        # Retry task
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60, exc=e)


@shared_task
def process_geofence_events(gps_location_id):
    """
    Process geofence events for GPS location
    """
    try:
        gps_location = GPSLocation.objects.get(id=gps_location_id)
        
        geofence_service = GeofenceService()
        events = geofence_service.check_location_geofences(gps_location)
        
        # Send notifications for important events
        for event_data in events:
            if event_data['event_type'] == 'ENTER':
                # Send geofence entry notification
                async_to_sync(channel_layer.group_send)(
                    f"user_{gps_location.user.id}",
                    {
                        'type': 'geofence_alert',
                        'zone_name': event_data['zone_name'],
                        'event_type': 'ENTER',
                        'message': f"Entered {event_data['zone_name']}",
                        'timestamp': event_data['timestamp']
                    }
                )
        
        logger.info(f"Processed {len(events)} geofence events for location {gps_location_id}")
        
    except GPSLocation.DoesNotExist:
        logger.error(f"GPS location {gps_location_id} not found")
    except Exception as e:
        logger.error(f"Geofence processing error: {str(e)}")


@shared_task
def update_route_eta_real_time(route_optimization_id, gps_location_id):
    """
    Update route ETA based on real-time GPS data
    """
    try:
        route_optimization = RouteOptimization.objects.get(
            id=route_optimization_id
        )
        gps_location = GPSLocation.objects.get(id=gps_location_id)
        
        route_service = RouteOptimizationService()
        route_service.update_eta_real_time(route_optimization, gps_location)
        
        # Notify WebSocket clients of ETA update
        async_to_sync(channel_layer.group_send)(
            f"ride_{route_optimization.ride.id}",
            {
                'type': 'eta_update',
                'route_id': str(route_optimization.id),
                'new_eta': route_optimization.current_eta.isoformat(),
                'delay_minutes': (
                    route_optimization.current_eta - route_optimization.original_eta
                ).total_seconds() / 60
            }
        )
        
    except (RouteOptimization.DoesNotExist, GPSLocation.DoesNotExist):
        logger.error("Route optimization or GPS location not found")
    except Exception as e:
        logger.error(f"ETA update error: {str(e)}")


@shared_task
def sync_offline_gps_buffer(offline_buffer_id):
    """
    Process offline GPS buffer asynchronously
    """
    try:
        from .models import OfflineGPSBuffer
        
        offline_buffer = OfflineGPSBuffer.objects.get(id=offline_buffer_id)
        created_locations, errors = offline_buffer.process_buffered_locations()
        
        # Notify user of sync completion
        async_to_sync(channel_layer.group_send)(
            f"user_{offline_buffer.user.id}",
            {
                'type': 'offline_sync_complete',
                'buffer_id': str(offline_buffer.id),
                'synced_count': len(created_locations),
                'error_count': len(errors),
                'success': len(errors) == 0
            }
        )
        
        logger.info(f"Offline GPS buffer {offline_buffer_id} synced: "
                   f"{len(created_locations)} locations, {len(errors)} errors")
        
    except Exception as e:
        logger.error(f"Offline GPS sync error: {str(e)}")


@shared_task
def cleanup_old_gps_data():
    """
    Cleanup old GPS location data (older than 30 days for non-VIP users)
    """
    try:
        from datetime import timedelta
        
        cutoff_date = timezone.now() - timedelta(days=30)
        
        # Delete old GPS locations for non-VIP users
        deleted_count = GPSLocation.objects.filter(
            server_timestamp__lt=cutoff_date
        ).exclude(
            user__tier='VIP'  # Keep VIP data longer
        ).delete()[0]
        
        # Delete old geofence events
        GeofenceEvent.objects.filter(
            event_timestamp__lt=cutoff_date
        ).delete()
        
        logger.info(f"Cleaned up {deleted_count} old GPS locations")
        
    except Exception as e:
        logger.error(f"GPS cleanup error: {str(e)}")


@shared_task
def monitor_vip_users():
    """
    Monitor VIP users for safety and compliance
    """
    try:
        from datetime import timedelta
        
        # Check for VIP users without recent GPS updates
        inactive_threshold = timezone.now() - timedelta(minutes=10)
        
        inactive_vip_users = GPSLocation.objects.filter(
            user__tier='VIP',
            server_timestamp__lt=inactive_threshold
        ).values_list('user_id', flat=True).distinct()
        
        # Alert control center about inactive VIP users
        if inactive_vip_users:
            async_to_sync(channel_layer.group_send)(
                "control_center_alerts",
                {
                    'type': 'vip_inactive_alert',
                    'inactive_users': list(inactive_vip_users),
                    'threshold_minutes': 10,
                    'timestamp': timezone.now().isoformat()
                }
            )
        
        logger.info(f"VIP monitoring: {len(inactive_vip_users)} inactive users")
        
    except Exception as e:
        logger.error(f"VIP monitoring error: {str(e)}")


@shared_task
def generate_daily_gps_report():
    """
    Generate daily GPS tracking report
    """
    try:
        from django.db.models import Count, Avg
        
        today = timezone.now().date()
        
        # Calculate daily statistics
        daily_stats = {
            'total_locations': GPSLocation.objects.filter(
                server_timestamp__date=today
            ).count(),
            'unique_users': GPSLocation.objects.filter(
                server_timestamp__date=today
            ).values('user').distinct().count(),
            'average_accuracy': GPSLocation.objects.filter(
                server_timestamp__date=today
            ).aggregate(avg_acc=Avg('accuracy_meters'))['avg_acc'] or 0,
            'geofence_events': GeofenceEvent.objects.filter(
                event_timestamp__date=today
            ).count(),
            'vip_locations': GPSLocation.objects.filter(
                server_timestamp__date=today,
                user__tier='VIP'
            ).count()
        }
        
        # Store report in cache for 24 hours
        from django.core.cache import cache
        cache.set(f"daily_gps_report_{today}", daily_stats, timeout=86400)
        
        logger.info(f"Daily GPS report generated: {daily_stats}")
        
    except Exception as e:
        logger.error(f"Daily report error: {str(e)}")


@shared_task
def check_geofence_violations():
    """
    Check for geofence violations and alert control center
    """
    try:
        # Check for unauthorized access to VIP zones
        vip_violations = GeofenceEvent.objects.filter(
            event_timestamp__gte=timezone.now() - timezone.timedelta(hours=1),
            geofence_zone__requires_vip=True,
            event_type='ENTER'
        ).exclude(
            user__tier='VIP'
        )
        
        for violation in vip_violations:
            # Alert control center
            async_to_sync(channel_layer.group_send)(
                "control_center_alerts",
                {
                    'type': 'geofence_violation',
                    'user_id': violation.user.id,
                    'user_name': violation.user.get_full_name(),
                    'zone_name': violation.geofence_zone.name,
                    'violation_type': 'unauthorized_vip_access',
                    'timestamp': violation.event_timestamp.isoformat()
                }
            )
        
        logger.info(f"Checked geofence violations: {len(vip_violations)} found")
        
    except Exception as e:
        logger.error(f"Geofence violation check error: {str(e)}")
