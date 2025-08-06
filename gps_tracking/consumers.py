"""
WebSocket Consumers for Real-time GPS Tracking
Handles live location updates, geofencing events, and VIP tracking
"""

import json
import asyncio
from datetime import datetime, timedelta
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
# from django.contrib.gis.geos import Point  # Removed GeoDjango dependency
from django.utils import timezone
from django.core.cache import cache
from decimal import Decimal
import logging

from .models import GPSLocation, GeofenceZone, GeofenceEvent, RouteOptimization
from .services import GPSValidationService, GeofenceService, RouteOptimizationService

logger = logging.getLogger(__name__)
User = get_user_model()


class GPSTrackingConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time GPS tracking"""
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.user = self.scope["user"]
        self.user_id = str(self.user.id)
        self.room_group_name = f"gps_tracking_{self.user_id}"
        
        # Authentication check
        if not self.user.is_authenticated:
            await self.close(code=4001)
            return
        
        # Join GPS tracking group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'GPS tracking connected',
            'user_id': self.user_id,
            'timestamp': timezone.now().isoformat()
        }))
        
        logger.info(f"GPS tracking connected for user {self.user_id}")
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Leave GPS tracking group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        # Update user's last seen timestamp
        await self.update_last_seen()
        
        logger.info(f"GPS tracking disconnected for user {self.user_id} (code: {close_code})")
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'gps_update':
                await self.handle_gps_update(data)
            elif message_type == 'heartbeat':
                await self.handle_heartbeat(data)
            elif message_type == 'route_update_request':
                await self.handle_route_update_request(data)
            elif message_type == 'offline_sync':
                await self.handle_offline_sync(data)
            else:
                await self.send_error('Unknown message type', message_type)
                
        except json.JSONDecodeError:
            await self.send_error('Invalid JSON format')
        except Exception as e:
            logger.error(f"Error handling GPS message: {str(e)}")
            await self.send_error('Server error processing message')
    
    async def handle_gps_update(self, data):
        """Process GPS location update"""
        try:
            # Extract GPS data
            location_data = data.get('location', {})
            latitude = location_data.get('latitude')
            longitude = location_data.get('longitude')
            accuracy = location_data.get('accuracy', 0)
            device_timestamp = location_data.get('timestamp')
            
            # Validate required fields
            if not all([latitude, longitude, device_timestamp]):
                await self.send_error('Missing required location data')
                return
            
            # Validate GPS accuracy
            validation_service = GPSValidationService()
            is_valid, accuracy_level = await validation_service.validate_location(
                latitude, longitude, accuracy
            )
            
            if not is_valid:
                await self.send_error('GPS location validation failed')
                return
            
            # Create GPS location record
            gps_location = await self.create_gps_location(
                latitude=latitude,
                longitude=longitude,
                accuracy_meters=accuracy,
                accuracy_level=accuracy_level,
                device_timestamp=device_timestamp,
                location_data=location_data
            )
            
            # Check geofencing
            geofence_events = await self.check_geofencing(gps_location)
            
            # Update route optimization if in active ride
            ride_id = data.get('ride_id')
            if ride_id:
                await self.update_route_optimization(ride_id, gps_location)
            
            # Send confirmation with processed data
            await self.send(text_data=json.dumps({
                'type': 'gps_update_processed',
                'location_id': str(gps_location.id),
                'accuracy_level': accuracy_level,
                'geofence_events': geofence_events,
                'timestamp': timezone.now().isoformat()
            }))
            
            # Broadcast to relevant groups (drivers, control center)
            await self.broadcast_location_update(gps_location, data)
            
        except Exception as e:
            logger.error(f"Error processing GPS update: {str(e)}")
            await self.send_error('Failed to process GPS update')
    
    async def handle_heartbeat(self, data):
        """Handle heartbeat message to keep connection alive"""
        await self.send(text_data=json.dumps({
            'type': 'heartbeat_response',
            'timestamp': timezone.now().isoformat(),
            'status': 'alive'
        }))
    
    async def handle_route_update_request(self, data):
        """Handle request for route optimization update"""
        try:
            ride_id = data.get('ride_id')
            if not ride_id:
                await self.send_error('Missing ride_id for route update')
                return
            
            # Get current route optimization
            route_optimization = await self.get_route_optimization(ride_id)
            if not route_optimization:
                await self.send_error('Route optimization not found')
                return
            
            # Update ETA and route
            route_service = RouteOptimizationService()
            updated_route = await route_service.update_route_real_time(
                route_optimization, 
                self.user
            )
            
            await self.send(text_data=json.dumps({
                'type': 'route_update',
                'ride_id': ride_id,
                'eta': updated_route.current_eta.isoformat(),
                'distance_remaining': updated_route.distance_meters,
                'traffic_level': updated_route.traffic_level,
                'timestamp': timezone.now().isoformat()
            }))
            
        except Exception as e:
            logger.error(f"Error updating route: {str(e)}")
            await self.send_error('Failed to update route')
    
    async def handle_offline_sync(self, data):
        """Handle synchronization of offline GPS data"""
        try:
            buffered_locations = data.get('buffered_locations', [])
            device_id = data.get('device_id')
            
            if not buffered_locations:
                await self.send_error('No buffered locations to sync')
                return
            
            # Process offline GPS buffer
            created_locations, errors = await self.process_offline_buffer(
                buffered_locations, device_id
            )
            
            await self.send(text_data=json.dumps({
                'type': 'offline_sync_complete',
                'synced_count': len(created_locations),
                'error_count': len(errors),
                'errors': errors[:5],  # Send first 5 errors only
                'timestamp': timezone.now().isoformat()
            }))
            
        except Exception as e:
            logger.error(f"Error syncing offline data: {str(e)}")
            await self.send_error('Failed to sync offline data')
    
    async def send_error(self, message, details=None):
        """Send error message to client"""
        error_data = {
            'type': 'error',
            'message': message,
            'timestamp': timezone.now().isoformat()
        }
        if details:
            error_data['details'] = details
        
        await self.send(text_data=json.dumps(error_data))
    
    @database_sync_to_async
    def create_gps_location(self, **kwargs):
        """Create GPS location record in database"""
        return GPSLocation.objects.create_encrypted_location(
            user=self.user,
            **kwargs
        )
    
    @database_sync_to_async
    def check_geofencing(self, gps_location):
        """Check geofence boundaries and create events"""
        geofence_service = GeofenceService()
        return geofence_service.check_location_geofences(gps_location)
    
    @database_sync_to_async
    def update_route_optimization(self, ride_id, gps_location):
        """Update route optimization with new location"""
        try:
            route_optimization = RouteOptimization.objects.select_related('ride').get(
                ride_id=ride_id
            )
            route_service = RouteOptimizationService()
            route_service.update_eta_real_time(route_optimization, gps_location)
        except RouteOptimization.DoesNotExist:
            pass
    
    @database_sync_to_async
    def get_route_optimization(self, ride_id):
        """Get route optimization for ride"""
        try:
            return RouteOptimization.objects.select_related('ride').get(
                ride_id=ride_id
            )
        except RouteOptimization.DoesNotExist:
            return None
    
    @database_sync_to_async
    def process_offline_buffer(self, buffered_locations, device_id):
        """Process offline GPS buffer"""
        from .models import OfflineGPSBuffer
        
        # Create offline buffer record
        offline_buffer = OfflineGPSBuffer.objects.create(
            user=self.user,
            device_id=device_id,
            buffered_locations=buffered_locations,
            start_timestamp=timezone.now() - timedelta(hours=1),
            end_timestamp=timezone.now(),
            total_locations=len(buffered_locations),
            app_version="1.0.0",
            device_info={}
        )
        
        # Process buffered locations
        return offline_buffer.process_buffered_locations()
    
    @database_sync_to_async
    def update_last_seen(self):
        """Update user's last seen timestamp"""
        cache.set(f"gps_last_seen_{self.user_id}", timezone.now(), timeout=300)
    
    async def broadcast_location_update(self, gps_location, original_data):
        """Broadcast location update to relevant groups"""
        channel_layer = get_channel_layer()
        
        # Broadcast to control center if VIP user
        if hasattr(self.user, 'tier') and self.user.tier == 'VIP':
            await channel_layer.group_send(
                "control_center_vip",
                {
                    'type': 'vip_location_update',
                    'user_id': self.user_id,
                    'location_id': str(gps_location.id),
                    'encrypted': True,
                    'timestamp': timezone.now().isoformat()
                }
            )
        
        # Broadcast to active ride participants
        ride_id = original_data.get('ride_id')
        if ride_id:
            await channel_layer.group_send(
                f"ride_{ride_id}",
                {
                    'type': 'ride_location_update',
                    'user_id': self.user_id,
                    'location_id': str(gps_location.id),
                    'timestamp': timezone.now().isoformat()
                }
            )
    
    # Message handlers for group messages
    async def vip_location_update(self, event):
        """Handle VIP location update from group"""
        await self.send(text_data=json.dumps({
            'type': 'vip_location_update',
            'user_id': event['user_id'],
            'location_id': event['location_id'],
            'encrypted': event['encrypted'],
            'timestamp': event['timestamp']
        }))
    
    async def ride_location_update(self, event):
        """Handle ride location update from group"""
        await self.send(text_data=json.dumps({
            'type': 'ride_location_update',
            'user_id': event['user_id'],
            'location_id': event['location_id'],
            'timestamp': event['timestamp']
        }))
    
    async def geofence_alert(self, event):
        """Handle geofence alert from group"""
        await self.send(text_data=json.dumps({
            'type': 'geofence_alert',
            'zone_name': event['zone_name'],
            'event_type': event['event_type'],
            'message': event['message'],
            'timestamp': event['timestamp']
        }))


class ControlCenterConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for control center monitoring"""
    
    async def connect(self):
        """Handle control center connection"""
        self.user = self.scope["user"]
        
        # Check if user has control center access
        if not self.user.is_authenticated or not self.has_control_center_access():
            await self.close(code=4003)
            return
        
        # Join control center groups
        await self.channel_layer.group_add("control_center_vip", self.channel_name)
        await self.channel_layer.group_add("control_center_alerts", self.channel_name)
        
        await self.accept()
        
        # Send active VIP users count
        vip_count = await self.get_active_vip_count()
        await self.send(text_data=json.dumps({
            'type': 'control_center_connected',
            'active_vip_users': vip_count,
            'timestamp': timezone.now().isoformat()
        }))
    
    async def disconnect(self, close_code):
        """Handle control center disconnection"""
        await self.channel_layer.group_discard("control_center_vip", self.channel_name)
        await self.channel_layer.group_discard("control_center_alerts", self.channel_name)
    
    async def receive(self, text_data):
        """Handle control center messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'request_vip_locations':
                await self.handle_vip_locations_request(data)
            elif message_type == 'emergency_alert':
                await self.handle_emergency_alert(data)
            elif message_type == 'geofence_monitor':
                await self.handle_geofence_monitor(data)
                
        except json.JSONDecodeError:
            await self.send_error('Invalid JSON format')
        except Exception as e:
            logger.error(f"Error in control center: {str(e)}")
            await self.send_error('Server error')
    
    @database_sync_to_async
    def has_control_center_access(self):
        """Check if user has control center access"""
        return (self.user.is_staff or 
                hasattr(self.user, 'role') and 
                self.user.role in ['ADMIN', 'CONTROL_CENTER'])
    
    @database_sync_to_async
    def get_active_vip_count(self):
        """Get count of active VIP users"""
        # Implementation would count active VIP users in last 5 minutes
        return 0
    
    async def handle_vip_locations_request(self, data):
        """Handle request for VIP user locations"""
        # Implementation for getting VIP locations
        pass
    
    async def handle_emergency_alert(self, data):
        """Handle emergency alert from control center"""
        # Implementation for emergency alerts
        pass
    
    async def handle_geofence_monitor(self, data):
        """Handle geofence monitoring requests"""
        # Implementation for geofence monitoring
        pass
    
    async def send_error(self, message):
        """Send error to control center"""
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': message,
            'timestamp': timezone.now().isoformat()
        }))
    
    # Group message handlers
    async def vip_location_update(self, event):
        """Forward VIP location update to control center"""
        await self.send(text_data=json.dumps(event))
    
    async def emergency_alert(self, event):
        """Forward emergency alert to control center"""
        await self.send(text_data=json.dumps(event))
    
    async def geofence_violation(self, event):
        """Forward geofence violation to control center"""
        await self.send(text_data=json.dumps(event))


class RideTrackingConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for ride-specific tracking"""
    
    async def connect(self):
        """Handle ride tracking connection"""
        self.user = self.scope["user"]
        self.ride_id = self.scope['url_route']['kwargs']['ride_id']
        self.room_group_name = f"ride_{self.ride_id}"
        
        # Verify user is part of this ride
        if not await self.user_in_ride():
            await self.close(code=4004)
            return
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        """Handle ride tracking disconnection"""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    @database_sync_to_async
    def user_in_ride(self):
        """Check if user is participant in ride"""
        from rides.models import Ride
        try:
            ride = Ride.objects.get(id=self.ride_id)
            return (self.user == ride.customer or 
                    self.user == ride.driver.user)
        except Ride.DoesNotExist:
            return False
    
    async def ride_location_update(self, event):
        """Handle ride location update"""
        await self.send(text_data=json.dumps(event))
    
    async def eta_update(self, event):
        """Handle ETA update"""
        await self.send(text_data=json.dumps(event))
    
    async def route_update(self, event):
        """Handle route update"""
        await self.send(text_data=json.dumps(event))
