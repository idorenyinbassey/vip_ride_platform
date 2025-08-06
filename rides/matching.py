# Ride Matching Algorithm
"""
Comprehensive ride matching algorithm that handles:
- Tier-based driver matching
- Vehicle type consideration for premium/VIP requests
- Distance-based matching with optimization
- VIP trusted driver preferences
- Dynamic surge pricing logic
- Driver availability status management
"""

import math
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

from django.db import models, transaction
# from django.contrib.gis.geos import Point
# from django.contrib.gis.measure import Distance
from django.utils import timezone
from django.conf import settings

from accounts.models import Driver, UserTier
from fleet_management.models import Vehicle
from .models import Ride, RideOffer, RideStatus, RideType, BillingModel

logger = logging.getLogger(__name__)


@dataclass
class DriverScore:
    """Data class for driver scoring in matching algorithm"""
    driver: Driver
    vehicle: Vehicle
    distance_km: float
    estimated_arrival_minutes: int
    surge_multiplier: Decimal
    score: float
    match_reasons: List[str]


@dataclass
class SurgeZone:
    """Data class for surge pricing zones"""
    latitude: float
    longitude: float
    radius_km: float
    surge_multiplier: Decimal
    active_until: datetime


class RideMatchingService:
    """Service class for intelligent ride matching"""
    
    # Configuration constants
    MAX_SEARCH_RADIUS_KM = 20.0  # Maximum search radius for drivers
    VIP_SEARCH_RADIUS_KM = 50.0  # Extended search for VIP rides
    MAX_DRIVERS_TO_CONSIDER = 50  # Limit drivers to consider for performance
    
    # Scoring weights
    DISTANCE_WEIGHT = 0.3
    TIER_MATCH_WEIGHT = 0.25
    VEHICLE_MATCH_WEIGHT = 0.2
    RATING_WEIGHT = 0.15
    AVAILABILITY_WEIGHT = 0.1
    
    # Surge pricing thresholds
    SURGE_DEMAND_THRESHOLD = 10  # Rides requested in last 30 mins to trigger surge
    SURGE_SUPPLY_RATIO = 0.5     # Driver to ride ratio for surge calculation
    
    def __init__(self):
        self.surge_zones: List[SurgeZone] = []
        self.load_active_surge_zones()
    
    def find_best_drivers(
        self, 
        ride: Ride, 
        max_drivers: int = 5
    ) -> List[DriverScore]:
        """
        Find the best drivers for a ride request using comprehensive matching algorithm
        
        Args:
            ride: The ride request to match
            max_drivers: Maximum number of drivers to return
            
        Returns:
            List of scored drivers ordered by match quality
        """
        logger.info(f"Starting driver search for ride {ride.id} - {ride.ride_type} - {ride.customer_tier}")
        
        # Calculate surge multiplier for ride location
        surge_multiplier = self.calculate_surge_multiplier(
            float(ride.pickup_latitude),
            float(ride.pickup_longitude),
            ride.customer_tier
        )
        ride.surge_multiplier = surge_multiplier
        
        # Get search radius based on ride tier
        search_radius = self.get_search_radius(ride.customer_tier, ride.ride_type)
        
        # Find available drivers in radius
        available_drivers = self.get_available_drivers(
            float(ride.pickup_latitude),
            float(ride.pickup_longitude),
            search_radius,
            ride.customer_tier,
            ride.ride_type
        )
        
        logger.info(f"Found {len(available_drivers)} available drivers in {search_radius}km radius")
        
        if not available_drivers:
            logger.warning(f"No available drivers found for ride {ride.id}")
            return []
        
        # Score and rank drivers
        scored_drivers = []
        
        for driver_data in available_drivers:
            driver = driver_data['driver']
            vehicle = driver_data['vehicle']
            distance_km = driver_data['distance_km']
            
            try:
                score_data = self.score_driver_for_ride(
                    driver, vehicle, ride, distance_km, surge_multiplier
                )
                scored_drivers.append(score_data)
            except Exception as e:
                logger.error(f"Error scoring driver {driver.id}: {e}")
                continue
        
        # Sort by score (highest first) and return top drivers
        scored_drivers.sort(key=lambda x: x.score, reverse=True)
        top_drivers = scored_drivers[:max_drivers]
        
        logger.info(f"Returning top {len(top_drivers)} drivers for ride {ride.id}")
        for i, driver_score in enumerate(top_drivers):
            logger.debug(
                f"Driver #{i+1}: {driver_score.driver.user.get_full_name()} "
                f"(Score: {driver_score.score:.2f}, Distance: {driver_score.distance_km:.1f}km, "
                f"ETA: {driver_score.estimated_arrival_minutes}min)"
            )
        
        return top_drivers
    
    def get_available_drivers(
        self,
        pickup_lat: float,
        pickup_lng: float,
        radius_km: float,
        customer_tier: str,
        ride_type: str
    ) -> List[Dict]:
        """
        Get available drivers within radius who can serve the ride tier
        
        Returns list of dicts with driver, vehicle, and distance information
        """
        # Base query for available drivers
        drivers_query = Driver.objects.filter(
            status=Driver.DriverStatus.ACTIVE,
            is_online=True,
            is_available=True,
            current_location_lat__isnull=False,
            current_location_lng__isnull=False,
        ).select_related('user', 'fleet_company').prefetch_related('assigned_vehicles')
        
        # Filter by tier capability
        if customer_tier == UserTier.VIP:
            drivers_query = drivers_query.filter(
                subscription_tier__in=[
                    Driver.SubscriptionTier.VIP,
                    Driver.SubscriptionTier.PREMIUM
                ]
            )
        elif customer_tier == UserTier.PREMIUM:
            drivers_query = drivers_query.filter(
                subscription_tier__in=[
                    Driver.SubscriptionTier.VIP,
                    Driver.SubscriptionTier.PREMIUM
                ]
            )
        
        # Get drivers with distance calculation
        available_drivers = []
        
        for driver in drivers_query[:self.MAX_DRIVERS_TO_CONSIDER]:
            try:
                # Calculate distance
                distance_km = self.calculate_distance(
                    pickup_lat, pickup_lng,
                    float(driver.current_location_lat or 0),
                    float(driver.current_location_lng or 0)
                )
                
                # Skip if outside radius
                if distance_km > radius_km:
                    continue
                
                # Get driver's vehicle
                vehicle = self.get_driver_vehicle(driver, ride_type, customer_tier)
                if not vehicle:
                    continue
                
                # Check if driver can accept this ride type
                if not self.can_driver_accept_ride(driver, customer_tier, ride_type):
                    continue
                
                available_drivers.append({
                    'driver': driver,
                    'vehicle': vehicle,
                    'distance_km': distance_km
                })
                
            except Exception as e:
                logger.error(f"Error processing driver {driver.user.id}: {e}")
                continue
        
        return available_drivers
    
    def get_driver_vehicle(
        self, 
        driver: Driver, 
        ride_type: str, 
        customer_tier: str
    ) -> Optional[Vehicle]:
        """
        Get the most appropriate vehicle for the driver based on ride requirements
        """
        # Get driver's available vehicles
        if hasattr(driver, 'assigned_vehicles') and driver.assigned_vehicles.exists():
            vehicles = driver.assigned_vehicles.filter(
                status='ACTIVE'
            )
        else:
            # Driver is vehicle owner
            vehicles = Vehicle.objects.filter(
                owner=driver.user,
                status='ACTIVE'
            )
        
        if not vehicles.exists():
            return None
        
        # For VIP rides, prefer premium vehicles
        if customer_tier == UserTier.VIP:
            premium_vehicles = vehicles.filter(
                category__in=['PREMIUM', 'LUXURY']
            )
            if premium_vehicles.exists():
                return premium_vehicles.first()
        
        # For premium rides, prefer premium or classic vehicles
        if customer_tier == UserTier.PREMIUM:
            suitable_vehicles = vehicles.filter(
                category__in=['PREMIUM', 'CLASSIC']
            )
            if suitable_vehicles.exists():
                return suitable_vehicles.first()
        
        # Return any available vehicle for normal rides
        return vehicles.first()
    
    def score_driver_for_ride(
        self,
        driver: Driver,
        vehicle: Vehicle,
        ride: Ride,
        distance_km: float,
        surge_multiplier: Decimal
    ) -> DriverScore:
        """
        Calculate a comprehensive score for driver-ride matching
        
        Higher score = better match
        """
        score = 0.0
        match_reasons = []
        
        # 1. Distance Score (closer is better)
        max_distance = self.get_search_radius(ride.customer_tier, ride.ride_type)
        distance_score = max(0, (max_distance - distance_km) / max_distance)
        score += distance_score * self.DISTANCE_WEIGHT
        match_reasons.append(f"Distance: {distance_km:.1f}km")
        
        # 2. Tier Match Score
        tier_score = self.calculate_tier_match_score(driver, ride.customer_tier)
        score += tier_score * self.TIER_MATCH_WEIGHT
        match_reasons.append(f"Tier match: {tier_score:.2f}")
        
        # 3. Vehicle Match Score
        vehicle_score = self.calculate_vehicle_match_score(vehicle, ride)
        score += vehicle_score * self.VEHICLE_MATCH_WEIGHT
        match_reasons.append(f"Vehicle match: {vehicle_score:.2f}")
        
        # 4. Driver Rating Score
        rating_score = float(driver.average_rating) / 5.0 if driver.average_rating else 0.5
        score += rating_score * self.RATING_WEIGHT
        match_reasons.append(f"Rating: {driver.average_rating:.1f}/5.0")
        
        # 5. Availability Score (considers recent activity)
        availability_score = self.calculate_availability_score(driver)
        score += availability_score * self.AVAILABILITY_WEIGHT
        match_reasons.append(f"Availability: {availability_score:.2f}")
        
        # 6. VIP Trusted Driver Bonus
        if ride.customer_tier == UserTier.VIP:
            trusted_bonus = self.calculate_vip_trusted_bonus(driver, ride.customer)
            score += trusted_bonus
            if trusted_bonus > 0:
                match_reasons.append("VIP trusted driver")
        
        # 7. Fleet Priority Bonus
        fleet_bonus = self.calculate_fleet_priority_bonus(driver, ride.customer_tier)
        score += fleet_bonus
        if fleet_bonus > 0:
            match_reasons.append("Fleet priority")
        
        # Calculate estimated arrival time
        estimated_arrival_minutes = self.calculate_estimated_arrival(distance_km, surge_multiplier)
        
        return DriverScore(
            driver=driver,
            vehicle=vehicle,
            distance_km=distance_km,
            estimated_arrival_minutes=estimated_arrival_minutes,
            surge_multiplier=surge_multiplier,
            score=score,
            match_reasons=match_reasons
        )
    
    def calculate_tier_match_score(self, driver: Driver, customer_tier: str) -> float:
        """Calculate how well driver's subscription matches customer tier"""
        if customer_tier == UserTier.VIP:
            if driver.subscription_tier == Driver.SubscriptionTier.VIP:
                return 1.0
            elif driver.subscription_tier == Driver.SubscriptionTier.PREMIUM:
                return 0.8
            else:
                return 0.0
        elif customer_tier == UserTier.PREMIUM:
            if driver.subscription_tier in [Driver.SubscriptionTier.VIP, Driver.SubscriptionTier.PREMIUM]:
                return 1.0
            else:
                return 0.5
        else:  # Normal tier
            return 1.0  # All drivers can serve normal rides
    
    def calculate_vehicle_match_score(self, vehicle: Vehicle, ride: Ride) -> float:
        """Calculate how well vehicle matches ride requirements"""
        score = 0.5  # Base score
        
        # Vehicle category match
        if ride.customer_tier == UserTier.VIP:
            if vehicle.category in ['PREMIUM', 'LUXURY']:
                score += 0.4
        elif ride.customer_tier == UserTier.PREMIUM:
            if vehicle.category in ['PREMIUM', 'CLASSIC']:
                score += 0.3
        
        # Special requirements
        if ride.requires_baby_seat and vehicle.has_baby_seat:
            score += 0.2
        
        if ride.requires_wheelchair_access and vehicle.has_wheelchair_access:
            score += 0.2
        
        if ride.requires_premium_vehicle and vehicle.category in ['PREMIUM', 'LUXURY']:
            score += 0.2
        
        return min(1.0, score)
    
    def calculate_availability_score(self, driver: Driver) -> float:
        """Calculate driver availability score based on recent activity"""
        score = 0.5  # Base score
        
        # Check how long driver has been online
        if driver.last_location_update:
            minutes_since_update = (timezone.now() - driver.last_location_update).total_seconds() / 60
            if minutes_since_update < 5:
                score += 0.3  # Very recent location update
            elif minutes_since_update < 15:
                score += 0.2  # Recent location update
        
        # Check completion rate
        if driver.completion_rate >= 95:
            score += 0.2
        elif driver.completion_rate >= 85:
            score += 0.1
        
        return min(1.0, score)
    
    def calculate_vip_trusted_bonus(self, driver: Driver, customer) -> float:
        """Calculate bonus for VIP trusted drivers"""
        # Check if driver has successfully completed VIP rides for this customer
        from .models import Ride
        
        completed_vip_rides = Ride.objects.filter(
            customer=customer,
            driver=driver.user,
            customer_tier=UserTier.VIP,
            status=RideStatus.COMPLETED
        ).count()
        
        if completed_vip_rides >= 5:
            return 0.3  # Highly trusted
        elif completed_vip_rides >= 2:
            return 0.2  # Somewhat trusted
        elif completed_vip_rides >= 1:
            return 0.1  # Previously served
        
        return 0.0
    
    def calculate_fleet_priority_bonus(self, driver: Driver, customer_tier: str) -> float:
        """Calculate bonus for fleet company drivers"""
        if not driver.fleet_company:
            return 0.0
        
        # Fleet companies get priority for VIP rides
        if customer_tier == UserTier.VIP:
            return 0.15
        elif customer_tier == UserTier.PREMIUM:
            return 0.1
        
        return 0.05
    
    def calculate_surge_multiplier(
        self, 
        pickup_lat: float, 
        pickup_lng: float,
        customer_tier: str
    ) -> Decimal:
        """
        Calculate surge pricing multiplier based on demand/supply ratio
        """
        # Check if location is in active surge zone
        for zone in self.surge_zones:
            if (timezone.now() < zone.active_until and 
                self.calculate_distance(pickup_lat, pickup_lng, zone.latitude, zone.longitude) <= zone.radius_km):
                logger.info(f"Location in surge zone with {zone.surge_multiplier}x multiplier")
                return zone.surge_multiplier
        
        # Calculate dynamic surge based on demand/supply
        surge_multiplier = self.calculate_dynamic_surge(pickup_lat, pickup_lng, customer_tier)
        
        # VIP customers get reduced surge impact
        if customer_tier == UserTier.VIP:
            surge_multiplier = min(surge_multiplier, Decimal('2.0'))
        elif customer_tier == UserTier.PREMIUM:
            surge_multiplier = min(surge_multiplier, Decimal('2.5'))
        
        return max(Decimal('1.0'), surge_multiplier)
    
    def calculate_dynamic_surge(
        self, 
        pickup_lat: float, 
        pickup_lng: float,
        customer_tier: str
    ) -> Decimal:
        """Calculate surge based on real-time demand/supply ratio"""
        from .models import Ride
        
        # Define search area (3km radius for demand calculation)
        search_radius = 3.0
        now = timezone.now()
        thirty_minutes_ago = now - timedelta(minutes=30)
        
        # Count recent ride requests in area
        recent_rides_count = 0
        all_recent_rides = Ride.objects.filter(
            requested_at__gte=thirty_minutes_ago,
            status__in=[RideStatus.REQUESTED, RideStatus.ACCEPTED, RideStatus.DRIVER_ARRIVING]
        )
        
        for ride in all_recent_rides:
            distance = self.calculate_distance(
                pickup_lat, pickup_lng,
                float(ride.pickup_latitude),
                float(ride.pickup_longitude)
            )
            if distance <= search_radius:
                recent_rides_count += 1
        
        # Count available drivers in area
        available_drivers_count = len(self.get_available_drivers(
            pickup_lat, pickup_lng, search_radius, customer_tier, RideType.NORMAL
        ))
        
        # Calculate surge multiplier
        if available_drivers_count == 0:
            return Decimal('3.0')  # Maximum surge when no drivers
        
        demand_supply_ratio = recent_rides_count / max(available_drivers_count, 1)
        
        if demand_supply_ratio >= 2.0:
            surge_multiplier = Decimal('2.5')
        elif demand_supply_ratio >= 1.5:
            surge_multiplier = Decimal('2.0')
        elif demand_supply_ratio >= 1.0:
            surge_multiplier = Decimal('1.5')
        elif demand_supply_ratio >= 0.7:
            surge_multiplier = Decimal('1.3')
        else:
            surge_multiplier = Decimal('1.0')
        
        logger.info(
            f"Dynamic surge calculation: {recent_rides_count} rides, "
            f"{available_drivers_count} drivers, ratio: {demand_supply_ratio:.2f}, "
            f"surge: {surge_multiplier}x"
        )
        
        return surge_multiplier
    
    def can_driver_accept_ride(
        self, 
        driver: Driver, 
        customer_tier: str, 
        ride_type: str
    ) -> bool:
        """Check if driver can accept ride based on subscription and status"""
        # Check subscription status
        if not driver.is_subscription_active:
            return False
        
        # Check tier access
        if not driver.can_accept_tier_rides(customer_tier):
            return False
        
        # Check if driver is available
        if not (driver.is_online and driver.is_available):
            return False
        
        # Check if driver has active subscription that allows this tier
        from payments.models import DriverSubscription
        
        try:
            subscription = DriverSubscription.objects.get(
                driver=driver,
                status='active'
            )
            return subscription.can_accept_ride(ride_type)
        except DriverSubscription.DoesNotExist:
            return False
    
    def get_search_radius(self, customer_tier: str, ride_type: str) -> float:
        """Get search radius based on customer tier and ride type"""
        if customer_tier == UserTier.VIP:
            return self.VIP_SEARCH_RADIUS_KM
        elif ride_type in [RideType.AIRPORT, RideType.CORPORATE]:
            return 30.0
        else:
            return self.MAX_SEARCH_RADIUS_KM
    
    def calculate_estimated_arrival(
        self, 
        distance_km: float, 
        surge_multiplier: Decimal
    ) -> int:
        """Calculate estimated arrival time in minutes"""
        # Base calculation: assume 30 km/h average speed in city
        base_minutes = (distance_km / 30.0) * 60
        
        # Add surge delay factor (more demand = slower movement)
        surge_delay_factor = 1.0 + (float(surge_multiplier) - 1.0) * 0.3
        
        # Add buffer time
        estimated_minutes = int(base_minutes * surge_delay_factor) + 2
        
        return max(1, min(60, estimated_minutes))  # Between 1-60 minutes
    
    def calculate_distance(
        self, 
        lat1: float, 
        lng1: float, 
        lat2: float, 
        lng2: float
    ) -> float:
        """Calculate haversine distance between two points in kilometers"""
        # Convert to radians
        lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        a = (math.sin(dlat/2)**2 + 
             math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2)
        c = 2 * math.asin(math.sqrt(a))
        
        # Earth's radius in kilometers
        earth_radius_km = 6371.0
        
        return c * earth_radius_km
    
    def load_active_surge_zones(self):
        """Load active surge zones from cache or database"""
        # This would typically load from Redis cache
        # For now, we'll implement basic surge zones
        self.surge_zones = []
        
        # Example: Airport surge zone
        self.surge_zones.append(SurgeZone(
            latitude=6.5244,  # Lagos Airport example
            longitude=3.3792,
            radius_km=5.0,
            surge_multiplier=Decimal('1.5'),
            active_until=timezone.now() + timedelta(hours=24)
        ))
    
    @transaction.atomic
    def create_ride_offers(
        self, 
        ride: Ride, 
        driver_scores: List[DriverScore],
        offer_timeout_minutes: int = 2
    ) -> List[RideOffer]:
        """
        Create ride offers for matched drivers
        """
        offers = []
        expires_at = timezone.now() + timedelta(minutes=offer_timeout_minutes)
        
        for driver_score in driver_scores:
            try:
                offer = RideOffer.objects.create(
                    ride=ride,
                    driver=driver_score.driver.user,
                    estimated_arrival_time=driver_score.estimated_arrival_minutes,
                    driver_latitude=driver_score.driver.current_location_lat,
                    driver_longitude=driver_score.driver.current_location_lng,
                    expires_at=expires_at
                )
                offers.append(offer)
                
                logger.info(
                    f"Created offer for driver {driver_score.driver.user.get_full_name()} "
                    f"for ride {ride.id}"
                )
                
            except Exception as e:
                logger.error(f"Failed to create offer for driver {driver_score.driver.id}: {e}")
        
        return offers
    
    def update_driver_availability(self, driver: Driver, is_available: bool):
        """Update driver availability status"""
        driver.is_available = is_available
        driver.save(update_fields=['is_available'])
        
        logger.info(f"Updated driver {driver.user.get_full_name()} availability to {is_available}")


class RideMatchingController:
    """Controller for managing the ride matching process"""
    
    def __init__(self):
        self.matching_service = RideMatchingService()
    
    def process_ride_request(self, ride: Ride) -> Dict:
        """
        Process a new ride request and find matching drivers
        
        Returns:
            Dict with matching results and offers created
        """
        logger.info(f"Processing ride request {ride.id}")
        
        try:
            # Find best drivers
            driver_scores = self.matching_service.find_best_drivers(ride, max_drivers=5)
            
            if not driver_scores:
                # No drivers found
                ride.status = RideStatus.NO_DRIVER_FOUND
                ride.save()
                
                return {
                    'success': False,
                    'message': 'No available drivers found',
                    'drivers_found': 0,
                    'offers_created': 0
                }
            
            # Create offers for matched drivers
            offers = self.matching_service.create_ride_offers(ride, driver_scores)
            
            # Update ride status
            ride.status = RideStatus.REQUESTED
            ride.save()
            
            # Send notifications to drivers (would be implemented separately)
            self.notify_drivers(offers)
            
            return {
                'success': True,
                'message': f'Found {len(driver_scores)} matching drivers',
                'drivers_found': len(driver_scores),
                'offers_created': len(offers),
                'surge_multiplier': float(ride.surge_multiplier),
                'driver_scores': [
                    {
                        'driver_name': ds.driver.user.get_full_name(),
                        'distance_km': ds.distance_km,
                        'estimated_arrival': ds.estimated_arrival_minutes,
                        'score': ds.score,
                        'match_reasons': ds.match_reasons
                    }
                    for ds in driver_scores
                ]
            }
            
        except Exception as e:
            logger.error(f"Error processing ride request {ride.id}: {e}")
            return {
                'success': False,
                'message': f'Error processing ride request: {str(e)}',
                'drivers_found': 0,
                'offers_created': 0
            }
    
    def handle_driver_response(self, offer: RideOffer, accepted: bool) -> Dict:
        """Handle driver response to ride offer"""
        if accepted:
            return self.accept_ride_offer(offer)
        else:
            return self.reject_ride_offer(offer)
    
    @transaction.atomic
    def accept_ride_offer(self, offer: RideOffer) -> Dict:
        """Process driver acceptance of ride offer"""
        try:
            # Check if offer is still valid
            if offer.is_expired:
                return {
                    'success': False,
                    'message': 'Offer has expired'
                }
            
            # Check if ride is still available
            if offer.ride.status != RideStatus.REQUESTED:
                return {
                    'success': False,
                    'message': 'Ride is no longer available'
                }
            
            # Accept the offer
            offer.status = RideOffer.OfferStatus.ACCEPTED
            offer.save()
            
            # Update ride
            ride = offer.ride
            ride.driver = offer.driver
            ride.status = RideStatus.ACCEPTED
            ride.accepted_at = timezone.now()
            ride.save()
            
            # Update driver availability
            driver = Driver.objects.get(user=offer.driver)
            self.matching_service.update_driver_availability(driver, False)
            
            # Reject all pending offers for this ride
            RideOffer.objects.filter(
                ride=ride,
                status='PENDING'
            ).exclude(id=offer.id).update(
                status='REJECTED'
            )
            
            logger.info(f"Driver {offer.driver.get_full_name()} accepted ride {ride.id}")
            
            return {
                'success': True,
                'message': 'Ride offer accepted successfully',
                'ride_id': str(ride.id),
                'driver_name': offer.driver.get_full_name()
            }
            
        except Exception as e:
            logger.error(f"Error accepting ride offer {offer.id}: {e}")
            return {
                'success': False,
                'message': f'Error accepting offer: {str(e)}'
            }
    
    def reject_ride_offer(self, offer: RideOffer) -> Dict:
        """Process driver rejection of ride offer"""
        offer.status = RideOffer.OfferStatus.REJECTED
        offer.save()
        
        logger.info(f"Driver {offer.driver.get_full_name()} rejected ride {offer.ride.id}")
        
        # Check if there are other pending offers
        pending_offers = RideOffer.objects.filter(
            ride=offer.ride,
            status=RideOffer.OfferStatus.PENDING
        ).exists()
        
        if not pending_offers:
            # No more pending offers, try to find more drivers
            self.find_additional_drivers(offer.ride)
        
        return {
            'success': True,
            'message': 'Ride offer rejected'
        }
    
    def find_additional_drivers(self, ride: Ride):
        """Find additional drivers when initial offers are rejected"""
        logger.info(f"Finding additional drivers for ride {ride.id}")
        
        # Expand search radius
        expanded_scores = self.matching_service.find_best_drivers(ride, max_drivers=3)
        
        if expanded_scores:
            # Create new offers
            new_offers = self.matching_service.create_ride_offers(ride, expanded_scores)
            self.notify_drivers(new_offers)
            logger.info(f"Created {len(new_offers)} additional offers for ride {ride.id}")
        else:
            # Still no drivers found
            ride.status = RideStatus.NO_DRIVER_FOUND
            ride.save()
            logger.warning(f"No additional drivers found for ride {ride.id}")
    
    def notify_drivers(self, offers: List[RideOffer]):
        """Send notifications to drivers about ride offers"""
        # This would integrate with your notification system
        # For now, just log the notifications
        for offer in offers:
            logger.info(
                f"Notification sent to driver {offer.driver.get_full_name()} "
                f"for ride {offer.ride.id}"
            )
    
    def get_ride_matching_stats(self) -> Dict:
        """Get statistics about ride matching performance"""
        from django.db.models import Avg, Count
        
        # Calculate stats for last 24 hours
        yesterday = timezone.now() - timedelta(days=1)
        
        stats = {
            'total_rides_requested': Ride.objects.filter(
                requested_at__gte=yesterday
            ).count(),
            
            'successful_matches': Ride.objects.filter(
                requested_at__gte=yesterday,
                status__in=[RideStatus.ACCEPTED, RideStatus.COMPLETED]
            ).count(),
            
            'no_driver_found': Ride.objects.filter(
                requested_at__gte=yesterday,
                status=RideStatus.NO_DRIVER_FOUND
            ).count(),
            
            'average_matching_time': RideOffer.objects.filter(
                created_at__gte=yesterday,
                status=RideOffer.OfferStatus.ACCEPTED
            ).aggregate(
                avg_time=Avg('ride__accepted_at') - Avg('created_at')
            )['avg_time'] or timedelta(0),
            
            'surge_zones_active': len(self.matching_service.surge_zones)
        }
        
        # Calculate success rate
        total_requests = stats['total_rides_requested']
        if total_requests > 0:
            stats['success_rate'] = stats['successful_matches'] / total_requests * 100
        else:
            stats['success_rate'] = 0
        
        return stats
