"""
GPS Tracking Services for VIP Ride-Hailing Platform
Includes GPS validation, geofencing, and route optimization
"""

import math
import asyncio
from datetime import datetime, timedelta
from typing import Tuple, List, Dict, Optional
# from django.contrib.gis.geos import Point, Polygon  # Removed GeoDjango dependency
# from django.contrib.gis.measure import Distance  # Removed GeoDjango dependency
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings
import googlemaps
import logging

from .models import (
    GPSLocation, GeofenceZone, GeofenceEvent, 
    RouteOptimization, OfflineGPSBuffer
)

logger = logging.getLogger(__name__)


class GPSValidationService:
    """Service for validating GPS location accuracy and authenticity"""
    
    # GPS accuracy thresholds (in meters)
    ACCURACY_THRESHOLDS = {
        'HIGH': 10,
        'MEDIUM': 50,
        'LOW': 100,
        'UNKNOWN': float('inf')
    }
    
    # Speed validation thresholds (km/h)
    MAX_REASONABLE_SPEED = 200  # Maximum reasonable vehicle speed
    MAX_WALKING_SPEED = 10      # Maximum walking speed
    
    def __init__(self):
        self.gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY) if hasattr(settings, 'GOOGLE_MAPS_API_KEY') else None
    
    async def validate_location(self, latitude: float, longitude: float, 
                              accuracy: float, user=None, 
                              previous_location: GPSLocation = None) -> Tuple[bool, str]:
        """
        Validate GPS location for accuracy and authenticity
        
        Returns:
            Tuple[bool, str]: (is_valid, accuracy_level)
        """
        try:
            # Basic coordinate validation
            if not self._validate_coordinates(latitude, longitude):
                return False, 'UNKNOWN'
            
            # Accuracy level determination
            accuracy_level = self._determine_accuracy_level(accuracy)
            
            # Speed validation if previous location exists
            if previous_location:
                is_speed_valid = await self._validate_speed(
                    latitude, longitude, previous_location, user
                )
                if not is_speed_valid:
                    return False, accuracy_level
            
            # Mock location detection (basic checks)
            if await self._detect_mock_location(latitude, longitude, accuracy):
                return False, accuracy_level
            
            # Additional validation for VIP users
            if user and hasattr(user, 'tier') and user.tier == 'VIP':
                is_vip_valid = await self._validate_vip_location(
                    latitude, longitude, accuracy, user
                )
                if not is_vip_valid:
                    return False, accuracy_level
            
            return True, accuracy_level
            
        except Exception as e:
            logger.error(f"GPS validation error: {str(e)}")
            return False, 'UNKNOWN'
    
    def _validate_coordinates(self, latitude: float, longitude: float) -> bool:
        """Validate coordinate ranges"""
        return (-90 <= latitude <= 90) and (-180 <= longitude <= 180)
    
    def _determine_accuracy_level(self, accuracy: float) -> str:
        """Determine accuracy level based on accuracy value"""
        for level, threshold in self.ACCURACY_THRESHOLDS.items():
            if accuracy <= threshold:
                return level
        return 'UNKNOWN'
    
    async def _validate_speed(self, latitude: float, longitude: float,
                            previous_location: GPSLocation, user) -> bool:
        """Validate movement speed between locations"""
        try:
            # Get previous coordinates
            prev_lat, prev_lng = previous_location.coordinates
            if prev_lat is None or prev_lng is None:
                return True  # Cannot validate without previous coordinates
            
            # Calculate distance using Haversine formula
            distance_km = self._calculate_distance(
                prev_lat, prev_lng, latitude, longitude
            )
            
            # Calculate time difference
            time_diff = timezone.now() - previous_location.server_timestamp
            time_hours = time_diff.total_seconds() / 3600
            
            if time_hours == 0:
                return True  # Cannot calculate speed with zero time
            
            # Calculate speed
            speed_kmh = distance_km / time_hours
            
            # Check against reasonable limits
            if speed_kmh > self.MAX_REASONABLE_SPEED:
                logger.warning(
                    f"Unreasonable speed detected: {speed_kmh:.2f} km/h for user {user.id}"
                )
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Speed validation error: {str(e)}")
            return True  # Default to valid if validation fails
    
    def _calculate_distance(self, lat1: float, lng1: float, 
                          lat2: float, lng2: float) -> float:
        """Calculate distance between two points using Haversine formula"""
        R = 6371  # Earth's radius in kilometers
        
        dlat = math.radians(lat2 - lat1)
        dlng = math.radians(lng2 - lng1)
        
        a = (math.sin(dlat / 2) ** 2 + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
             math.sin(dlng / 2) ** 2)
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        
        return distance
    
    async def _detect_mock_location(self, latitude: float, longitude: float, 
                                  accuracy: float) -> bool:
        """Basic mock location detection"""
        # Check for suspiciously perfect accuracy
        if accuracy == 0 or accuracy < 1:
            return True
        
        # Check for repeated exact coordinates
        cache_key = f"gps_coords_{latitude}_{longitude}"
        repeat_count = cache.get(cache_key, 0)
        cache.set(cache_key, repeat_count + 1, timeout=300)  # 5 minutes
        
        if repeat_count > 10:  # Same coordinates reported too many times
            return True
        
        return False
    
    async def _validate_vip_location(self, latitude: float, longitude: float,
                                   accuracy: float, user) -> bool:
        """Additional validation for VIP users"""
        # VIP users require higher accuracy
        if accuracy > 20:  # VIP requires accuracy within 20 meters
            return False
        
        # Check if location is in a restricted area for VIP users
        # (Implementation would check against restricted zones)
        
        return True


class GeofenceService:
    """Service for managing geofencing operations"""
    
    def __init__(self):
        self.active_zones_cache_timeout = 300  # 5 minutes
    
    def check_location_geofences(self, gps_location: GPSLocation) -> List[Dict]:
        """
        Check if location triggers any geofence events
        
        Returns:
            List of geofence events triggered
        """
        try:
            point = gps_location.point
            if not point:
                return []
            
            # Get active geofence zones from cache or database
            active_zones = self._get_active_geofence_zones()
            
            events = []
            for zone in active_zones:
                # Check if point is within zone boundary
                if zone.contains_point(point):
                    event = self._handle_zone_entry(gps_location, zone)
                    if event:
                        events.append({
                            'zone_id': str(zone.id),
                            'zone_name': zone.name,
                            'event_type': 'ENTER',
                            'timestamp': timezone.now().isoformat()
                        })
                else:
                    # Check if user was previously in this zone (exit event)
                    exit_event = self._check_zone_exit(gps_location, zone)
                    if exit_event:
                        events.append({
                            'zone_id': str(zone.id),
                            'zone_name': zone.name,
                            'event_type': 'EXIT',
                            'timestamp': timezone.now().isoformat()
                        })
            
            return events
            
        except Exception as e:
            logger.error(f"Geofence checking error: {str(e)}")
            return []
    
    def _get_active_geofence_zones(self) -> List[GeofenceZone]:
        """Get active geofence zones with caching"""
        cache_key = "active_geofence_zones"
        zones = cache.get(cache_key)
        
        if zones is None:
            zones = list(GeofenceZone.objects.filter(is_active=True))
            cache.set(cache_key, zones, timeout=self.active_zones_cache_timeout)
        
        return zones
    
    def _handle_zone_entry(self, gps_location: GPSLocation, 
                          zone: GeofenceZone) -> Optional[GeofenceEvent]:
        """Handle geofence zone entry"""
        try:
            # Check if user was not already in this zone
            recent_entry = GeofenceEvent.objects.filter(
                user=gps_location.user,
                geofence_zone=zone,
                event_type='ENTER',
                event_timestamp__gte=timezone.now() - timedelta(minutes=5)
            ).exists()
            
            if recent_entry:
                return None  # Already entered recently
            
            # Create entry event
            event = GeofenceEvent.objects.create(
                user=gps_location.user,
                geofence_zone=zone,
                gps_location=gps_location,
                event_type='ENTER',
                ride=gps_location.ride
            )
            
            # Trigger zone-specific actions
            self._trigger_zone_actions(event, zone)
            
            return event
            
        except Exception as e:
            logger.error(f"Zone entry handling error: {str(e)}")
            return None
    
    def _check_zone_exit(self, gps_location: GPSLocation, 
                        zone: GeofenceZone) -> Optional[GeofenceEvent]:
        """Check and handle geofence zone exit"""
        try:
            # Check if user was recently in this zone
            recent_entry = GeofenceEvent.objects.filter(
                user=gps_location.user,
                geofence_zone=zone,
                event_type='ENTER',
                event_timestamp__gte=timezone.now() - timedelta(hours=1)
            ).order_by('-event_timestamp').first()
            
            if not recent_entry:
                return None  # User was not in this zone
            
            # Check if exit event already exists
            exit_exists = GeofenceEvent.objects.filter(
                user=gps_location.user,
                geofence_zone=zone,
                event_type='EXIT',
                event_timestamp__gt=recent_entry.event_timestamp
            ).exists()
            
            if exit_exists:
                return None  # Exit already recorded
            
            # Create exit event
            event = GeofenceEvent.objects.create(
                user=gps_location.user,
                geofence_zone=zone,
                gps_location=gps_location,
                event_type='EXIT',
                ride=gps_location.ride,
                duration_seconds=(
                    timezone.now() - recent_entry.event_timestamp
                ).total_seconds()
            )
            
            return event
            
        except Exception as e:
            logger.error(f"Zone exit checking error: {str(e)}")
            return None
    
    def _trigger_zone_actions(self, event: GeofenceEvent, zone: GeofenceZone):
        """Trigger actions based on geofence zone rules"""
        actions = []
        
        # Airport zone actions
        if zone.zone_type == 'AIRPORT':
            actions.append('airport_notification')
            # Notify customer about airport procedures
        
        # VIP zone actions
        elif zone.zone_type == 'VIP_ONLY' and not zone.requires_vip:
            if not hasattr(event.user, 'tier') or event.user.tier != 'VIP':
                actions.append('unauthorized_vip_zone')
                # Alert control center
        
        # Hotel zone actions
        elif zone.zone_type == 'HOTEL':
            actions.append('hotel_partnership_notification')
            # Notify about hotel services
        
        # Restricted area actions
        elif zone.zone_type == 'RESTRICTED':
            actions.append('restricted_area_alert')
            # Alert control center and user
        
        # Save triggered actions
        event.triggered_actions = actions
        event.save()


class RouteOptimizationService:
    """Service for route optimization and ETA calculation"""
    
    def __init__(self):
        self.gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY) if hasattr(settings, 'GOOGLE_MAPS_API_KEY') else None
    
    async def calculate_optimized_route(self, pickup_point: dict,
                                      dropoff_point: dict,
                                      waypoints: Optional[List[dict]] = None) -> Dict:
        """
        Calculate optimized route with real-time traffic
        
        Returns:
            Dictionary with route data
        """
        try:
            if not self.gmaps:
                return await self._fallback_route_calculation(pickup_point, dropoff_point)
            
            # Prepare waypoints
            waypoint_coords = []
            if waypoints:
                waypoint_coords = [
                    {'lat': point['latitude'], 'lng': point['longitude']} for point in waypoints
                ]
            
            # Google Maps API request
            directions_result = self.gmaps.directions(
                origin={
                    'lat': pickup_point['latitude'],
                    'lng': pickup_point['longitude']
                },
                destination={
                    'lat': dropoff_point['latitude'],
                    'lng': dropoff_point['longitude']
                },
                waypoints=waypoint_coords,
                optimize_waypoints=True,
                departure_time=datetime.now(),
                traffic_model='best_guess',
                mode='driving'
            )
            
            if not directions_result:
                return await self._fallback_route_calculation(pickup_point, dropoff_point)
            
            route = directions_result[0]
            leg = route['legs'][0]
            
            # Extract route data
            route_data = {
                'distance_meters': leg['distance']['value'],
                'duration_seconds': leg['duration']['value'],
                'duration_in_traffic_seconds': leg.get('duration_in_traffic', {}).get('value'),
                'polyline': route['overview_polyline']['points'],
                'steps': [step['html_instructions'] for step in leg['steps']],
                'traffic_level': self._determine_traffic_level(leg),
                'optimized_waypoint_order': route.get('waypoint_order', [])
            }
            
            return route_data
            
        except Exception as e:
            logger.error(f"Route calculation error: {str(e)}")
            return await self._fallback_route_calculation(pickup_point, dropoff_point)
    
    async def _fallback_route_calculation(
            self, pickup_point: dict, dropoff_point: dict) -> Dict:
        """Fallback route calculation without Google Maps API"""
        # Calculate straight-line distance
        distance = self._calculate_straight_line_distance(pickup_point, dropoff_point)
        
        # Estimate driving distance (factor of 1.3 for city driving)
        estimated_distance = distance * 1.3 * 1000  # Convert to meters
        
        # Estimate duration (assuming average speed of 30 km/h in city)
        estimated_duration = (estimated_distance / 1000) / 30 * 3600  # In seconds
        
        return {
            'distance_meters': int(estimated_distance),
            'duration_seconds': int(estimated_duration),
            'duration_in_traffic_seconds': int(estimated_duration * 1.2),
            'polyline': '',
            'steps': ['Navigate to destination'],
            'traffic_level': 'MODERATE',
            'optimized_waypoint_order': []
        }
    
    def _calculate_straight_line_distance(
            self, point1: dict, point2: dict) -> float:
        """Calculate straight-line distance between two points in kilometers"""
        R = 6371  # Earth's radius in kilometers
        
        lat1, lng1 = (math.radians(point1['latitude']), 
                      math.radians(point1['longitude']))
        lat2, lng2 = (math.radians(point2['latitude']), 
                      math.radians(point2['longitude']))
        
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        
        a = (math.sin(dlat / 2) ** 2 + 
             math.cos(lat1) * math.cos(lat2) * math.sin(dlng / 2) ** 2)
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        
        return distance
    
    def _determine_traffic_level(self, leg: Dict) -> str:
        """Determine traffic level from Google Maps data"""
        if 'duration_in_traffic' not in leg:
            return 'MODERATE'
        
        normal_duration = leg['duration']['value']
        traffic_duration = leg['duration_in_traffic']['value']
        
        ratio = traffic_duration / normal_duration
        
        if ratio < 1.1:
            return 'LOW'
        elif ratio < 1.3:
            return 'MODERATE'
        elif ratio < 1.5:
            return 'HEAVY'
        else:
            return 'SEVERE'
    
    async def update_route_real_time(self, route_optimization: RouteOptimization, 
                                   user) -> RouteOptimization:
        """Update route with real-time data"""
        try:
            # Get user's current location
            latest_location = GPSLocation.objects.filter(
                user=user,
                ride=route_optimization.ride
            ).order_by('-server_timestamp').first()
            
            if not latest_location:
                return route_optimization
            
            current_point = latest_location.point
            if not current_point:
                return route_optimization
            
            # Recalculate route from current location to destination
            updated_route_data = await self.calculate_optimized_route(
                current_point,
                route_optimization.dropoff_point
            )
            
            # Update ETA
            new_eta = timezone.now() + timedelta(
                seconds=updated_route_data['duration_in_traffic_seconds'] or 
                       updated_route_data['duration_seconds']
            )
            
            # Update route optimization
            route_optimization.current_eta = new_eta
            route_optimization.distance_meters = updated_route_data['distance_meters']
            route_optimization.duration_seconds = updated_route_data['duration_seconds']
            route_optimization.duration_in_traffic_seconds = updated_route_data.get('duration_in_traffic_seconds')
            route_optimization.traffic_level = updated_route_data['traffic_level']
            route_optimization.save()
            
            return route_optimization
            
        except Exception as e:
            logger.error(f"Real-time route update error: {str(e)}")
            return route_optimization
    
    def update_eta_real_time(self, route_optimization: RouteOptimization, 
                           gps_location: GPSLocation):
        """Update ETA based on current GPS location"""
        try:
            current_point = gps_location.point
            if not current_point:
                return
            
            # Calculate remaining distance to destination
            remaining_distance = self._calculate_straight_line_distance(
                current_point, route_optimization.dropoff_point
            )
            
            # Estimate remaining time based on current speed and traffic
            current_speed = gps_location.speed_kmh or 30  # Default 30 km/h
            
            # Adjust for traffic
            traffic_multiplier = {
                'LOW': 1.0,
                'MODERATE': 1.2,
                'HEAVY': 1.5,
                'SEVERE': 2.0
            }.get(route_optimization.traffic_level, 1.2)
            
            estimated_time_hours = (remaining_distance * traffic_multiplier) / current_speed
            estimated_time_seconds = estimated_time_hours * 3600
            
            # Update ETA
            new_eta = timezone.now() + timedelta(seconds=estimated_time_seconds)
            route_optimization.current_eta = new_eta
            route_optimization.save()
            
        except Exception as e:
            logger.error(f"ETA update error: {str(e)}")


class OfflineGPSService:
    """Service for handling offline GPS data synchronization"""
    
    def __init__(self):
        self.max_buffer_size = 1000  # Maximum locations per buffer
        self.max_offline_duration = timedelta(hours=24)  # Maximum offline duration
    
    async def process_offline_buffer(self, user, device_id: str, 
                                   buffered_locations: List[Dict]) -> Tuple[List, List]:
        """
        Process offline GPS buffer and create location records
        
        Returns:
            Tuple of (created_location_ids, errors)
        """
        try:
            if len(buffered_locations) > self.max_buffer_size:
                buffered_locations = buffered_locations[-self.max_buffer_size:]
            
            # Create offline buffer record
            offline_buffer = OfflineGPSBuffer.objects.create(
                user=user,
                device_id=device_id,
                buffered_locations=buffered_locations,
                start_timestamp=timezone.now() - timedelta(hours=1),
                end_timestamp=timezone.now(),
                total_locations=len(buffered_locations),
                app_version="1.0.0",
                device_info={}
            )
            
            # Process each buffered location
            created_locations = []
            errors = []
            
            validation_service = GPSValidationService()
            
            for location_data in buffered_locations:
                try:
                    # Validate location data
                    latitude = location_data.get('latitude')
                    longitude = location_data.get('longitude')
                    accuracy = location_data.get('accuracy', 0)
                    
                    if not all([latitude, longitude]):
                        errors.append({
                            'location_data': location_data,
                            'error': 'Missing coordinates'
                        })
                        continue
                    
                    # Validate GPS accuracy
                    is_valid, accuracy_level = await validation_service.validate_location(
                        latitude, longitude, accuracy, user
                    )
                    
                    if not is_valid:
                        errors.append({
                            'location_data': location_data,
                            'error': 'Location validation failed'
                        })
                        continue
                    
                    # Create GPS location
                    gps_location = GPSLocation.objects.create_encrypted_location(
                        user=user,
                        latitude=latitude,
                        longitude=longitude,
                        accuracy_meters=accuracy,
                        accuracy_level=accuracy_level,
                        device_timestamp=location_data.get('timestamp'),
                        is_offline_buffered=True,
                        sync_status='SYNCED',
                        **{k: v for k, v in location_data.items() 
                           if k in ['altitude', 'bearing', 'speed_kmh', 'battery_level']}
                    )
                    
                    created_locations.append(str(gps_location.id))
                    
                except Exception as e:
                    errors.append({
                        'location_data': location_data,
                        'error': str(e)
                    })
            
            # Update buffer sync status
            offline_buffer.is_synced = len(errors) == 0
            offline_buffer.sync_timestamp = timezone.now()
            offline_buffer.sync_errors = errors
            offline_buffer.save()
            
            return created_locations, errors
            
        except Exception as e:
            logger.error(f"Offline buffer processing error: {str(e)}")
            return [], [{'error': str(e)}]
