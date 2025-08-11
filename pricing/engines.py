"""
VIP Ride-Hailing Platform - Dynamic Pricing Engine
Advanced surge pricing system with demand-based calculations, tier preferences, and transparent pricing
"""

from django.utils import timezone
from django.db.models import Q
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Tuple, Optional
import logging
from datetime import timedelta

from .models import (
    PricingZone, TimeBasedPricing, SpecialEvent, DemandSurge, 
    PromotionalCode, PricingRule, PriceCalculationLog
)
from accounts.models import UserTier

logger = logging.getLogger(__name__)


class PricingEngine:
    """Main pricing calculation engine for dynamic surge pricing"""
    
    def __init__(self):
        self.calculation_log = {}
    
    def calculate_ride_price(
        self, 
        user, 
        pickup_lat: Decimal, 
        pickup_lng: Decimal,
        dropoff_lat: Decimal,
        dropoff_lng: Decimal,
        distance_km: Decimal,
        estimated_duration_minutes: int,
        vehicle_type: str,
        promo_code: str = None,
        ride_time: timezone.datetime = None
    ) -> Dict:
        """
        Calculate comprehensive ride price with all factors
        
        Returns:
        {
            'base_price': Decimal,
            'surge_price': Decimal,
            'final_price': Decimal,
            'discount': Decimal,
            'pricing_breakdown': Dict,
            'transparency_info': Dict
        }
        """
        if not ride_time:
            ride_time = timezone.now()
        
        self.calculation_log = {
            'user_tier': user.tier,
            'vehicle_type': vehicle_type,
            'distance_km': str(distance_km),
            'duration_minutes': estimated_duration_minutes,
            'calculation_time': ride_time.isoformat(),
            'factors_applied': []
        }
        
        # Step 1: Get base pricing rule
        pricing_rule = self._get_pricing_rule(pickup_lat, pickup_lng, vehicle_type)
        if not pricing_rule:
            raise ValueError(f"No pricing rule found for {vehicle_type} at location")
        
        # Step 2: Calculate base fare
        base_fare = self._calculate_base_fare(
            pricing_rule, distance_km, estimated_duration_minutes
        )
        
        # Step 3: Apply zone-based pricing
        zone = self._get_pricing_zone(pickup_lat, pickup_lng)
        zone_multiplier = zone.base_multiplier if zone else Decimal('1.000')
        
        # Step 4: Apply time-based pricing
        time_multiplier = self._get_time_multiplier(ride_time, user.tier)
        
        # Step 5: Apply surge pricing
        surge_multiplier = self._get_surge_multiplier(pickup_lat, pickup_lng, ride_time)
        
        # Step 6: Apply special event pricing
        event_multiplier = self._get_event_multiplier(pickup_lat, pickup_lng, ride_time)
        
        # Step 7: Apply tier-based adjustments
        tier_multiplier = self._get_tier_multiplier(user.tier, pricing_rule)
        
        # Calculate price before discounts
        subtotal = (
            base_fare *
            zone_multiplier *
            time_multiplier *
            surge_multiplier *
            event_multiplier *
            tier_multiplier
        )
        
        # Ensure minimum fare
        subtotal = max(subtotal, pricing_rule.minimum_fare)
        
        # Step 8: Apply promotional discounts
        promo_discount, promo_details = self._apply_promo_code(
            promo_code, user, subtotal, surge_multiplier
        )
        
        final_price = subtotal - promo_discount
        
        # Round to nearest cent
        final_price = final_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # Log the calculation
        self._log_calculation(
            user, pickup_lat, pickup_lng, dropoff_lat, dropoff_lng, distance_km, 
            estimated_duration_minutes, vehicle_type, pricing_rule,
            zone_multiplier, time_multiplier, surge_multiplier,
            event_multiplier, tier_multiplier, base_fare, 
            subtotal, promo_discount, final_price, promo_code
        )
        
        return {
            'base_price': base_fare,
            'surge_price': subtotal,
            'final_price': final_price,
            'discount': promo_discount,
            'pricing_breakdown': {
                'base_fare': base_fare,
                'zone_multiplier': zone_multiplier,
                'time_multiplier': time_multiplier,
                'surge_multiplier': surge_multiplier,
                'event_multiplier': event_multiplier,
                'tier_multiplier': tier_multiplier,
                'subtotal': subtotal,
                'promo_discount': promo_discount,
                'minimum_fare': pricing_rule.minimum_fare,
                'booking_fee': pricing_rule.booking_fee
            },
            'transparency_info': self._generate_transparency_info(
                zone, surge_multiplier, event_multiplier, promo_details
            ),
            'calculation_log': self.calculation_log
        }
    
    def _get_pricing_rule(self, pickup_lat: Decimal, pickup_lng: Decimal, vehicle_type: str) -> Optional[PricingRule]:
        """Get applicable pricing rule for location and vehicle type"""
        zone = self._get_pricing_zone(pickup_lat, pickup_lng)
        if not zone:
            # Fallback to default zone or raise error
            return None
        
        rules = PricingRule.objects.filter(
            vehicle_type=vehicle_type,
            zone=zone,
            is_active=True
        ).filter(
            effective_from__lte=timezone.now()
        ).filter(
            Q(effective_until__isnull=True) | Q(effective_until__gte=timezone.now())
        ).order_by('-effective_from')
        
        return rules.first()
    
    def _get_pricing_zone(self, latitude: Decimal, longitude: Decimal) -> Optional[PricingZone]:
        """Find pricing zone for given coordinates"""
        zones = PricingZone.objects.filter(is_active=True)
        
        for zone in zones:
            if zone.contains_point(latitude, longitude):
                return zone
        
        return None
    
    def _calculate_base_fare(
        self, 
        pricing_rule: PricingRule, 
        distance_km: Decimal, 
        duration_minutes: int
    ) -> Decimal:
        """Calculate base fare before any multipliers"""
        base_fare = pricing_rule.base_fare
        distance_fare = pricing_rule.per_km_rate * distance_km
        time_fare = pricing_rule.per_minute_rate * Decimal(str(duration_minutes))
        
        total = base_fare + distance_fare + time_fare + pricing_rule.booking_fee
        
        self.calculation_log['base_calculation'] = {
            'base_fare': str(base_fare),
            'distance_fare': str(distance_fare),
            'time_fare': str(time_fare),
            'booking_fee': str(pricing_rule.booking_fee),
            'total': str(total)
        }
        
        return total
    
    def _get_time_multiplier(self, ride_time: timezone.datetime, user_tier: str) -> Decimal:
        """Get time-based pricing multiplier"""
        applicable_rules = TimeBasedPricing.objects.filter(
            is_active=True
        ).order_by('-priority')
        
        for rule in applicable_rules:
            if rule.is_applicable_now():
                # Apply tier-specific multiplier
                tier_multiplier = getattr(rule, f'{user_tier}_tier_multiplier', Decimal('1.000'))
                final_multiplier = rule.multiplier * tier_multiplier
                
                self.calculation_log['factors_applied'].append({
                    'type': 'time_based',
                    'rule_name': rule.name,
                    'base_multiplier': str(rule.multiplier),
                    'tier_adjustment': str(tier_multiplier),
                    'final_multiplier': str(final_multiplier)
                })
                
                return final_multiplier
        
        return Decimal('1.000')
    
    def get_surge_multiplier(self, pickup_lat: Decimal, pickup_lng: Decimal, ride_time: timezone.datetime) -> Decimal:
        """Public method to get surge multiplier"""
        return self._get_surge_multiplier(pickup_lat, pickup_lng, ride_time)
    
    def get_event_multiplier(self, pickup_lat: Decimal, pickup_lng: Decimal, ride_time: timezone.datetime) -> Decimal:
        """Public method to get event multiplier"""
        return self._get_event_multiplier(pickup_lat, pickup_lng, ride_time)
    
    def _get_surge_multiplier(self, pickup_lat: Decimal, pickup_lng: Decimal, ride_time: timezone.datetime) -> Decimal:
        """Calculate real-time surge multiplier based on demand"""
        zone = self._get_pricing_zone(pickup_lat, pickup_lng)
        if not zone:
            return Decimal('1.000')
        
        # Get current surge data
        current_surge = DemandSurge.objects.filter(
            zone=zone,
            is_active=True,
            expires_at__gt=ride_time
        ).order_by('-calculated_at').first()
        
        if current_surge and current_surge.is_valid():
            multiplier = current_surge.surge_multiplier
            
            self.calculation_log['factors_applied'].append({
                'type': 'surge_pricing',
                'zone': zone.name,
                'surge_level': current_surge.surge_level,
                'demand_ratio': str(current_surge.demand_ratio),
                'multiplier': str(multiplier)
            })
            
            return multiplier
        
        # Calculate real-time surge if no current data
        return self._calculate_real_time_surge(zone, ride_time)
    
    def _calculate_real_time_surge(self, zone: PricingZone, ride_time: timezone.datetime) -> Decimal:
        """Calculate surge based on real-time demand metrics"""
        from rides.models import Ride
        
        # Get current metrics (last 15 minutes)
        time_window = ride_time - timedelta(minutes=15)
        
        # Count active rides and pending requests in zone
        active_rides = Ride.objects.filter(
            pickup_location__within=zone.boundary,
            status__in=['accepted', 'driver_arriving', 'in_progress'],
            created_at__gte=time_window
        ).count()
        
        pending_requests = Ride.objects.filter(
            pickup_location__within=zone.boundary,
            status='pending',
            created_at__gte=time_window
        ).count()
        
        # Estimate available drivers (simplified)
        from accounts.models import Driver
        available_drivers = Driver.objects.filter(
            is_online=True,
            is_available=True,
            # Approximate location filtering would go here
        ).count()
        
        # Calculate demand ratio
        total_demand = active_rides + pending_requests
        supply = max(available_drivers, 1)  # Avoid division by zero
        demand_ratio = Decimal(str(total_demand / supply))
        
        # Create or update surge record
        surge, created = DemandSurge.objects.update_or_create(
            zone=zone,
            defaults={
                'active_rides': active_rides,
                'pending_requests': pending_requests,
                'available_drivers': available_drivers,
                'demand_ratio': demand_ratio,
                'expires_at': ride_time + timedelta(minutes=5),
                'is_active': True
            }
        )
        
        # Calculate surge level and multiplier
        surge_level, multiplier = surge.calculate_surge_level()
        surge.surge_level = surge_level
        surge.surge_multiplier = multiplier
        surge.save()
        
        self.calculation_log['factors_applied'].append({
            'type': 'real_time_surge',
            'zone': zone.name,
            'active_rides': active_rides,
            'pending_requests': pending_requests,
            'available_drivers': available_drivers,
            'demand_ratio': str(demand_ratio),
            'surge_level': surge_level,
            'multiplier': str(multiplier)
        })
        
        return multiplier
    
    def _get_event_multiplier(self, pickup_lat: Decimal, pickup_lng: Decimal, ride_time: timezone.datetime) -> Decimal:
        """Get special event pricing multiplier"""
        # Check for events affecting the pickup location
        active_events = SpecialEvent.objects.filter(
            is_active=True
        )
        
        highest_multiplier = Decimal('1.000')
        event_info = None
        
        for event in active_events:
            if event.is_active_now():
                # Check if event affects the pickup location (simplified)
                if event.latitude and event.longitude:
                    # Simple distance check (would be more sophisticated in production)
                    lat_diff = abs(event.latitude - pickup_lat)
                    lng_diff = abs(event.longitude - pickup_lng)
                    if lat_diff <= Decimal('0.05') and lng_diff <= Decimal('0.05'):  # ~5km radius
                        multiplier = event.get_current_multiplier()
                        if multiplier > highest_multiplier:
                            highest_multiplier = multiplier
                            event_info = {
                                'name': event.name,
                                'type': event.event_type,
                                'multiplier': str(multiplier)
                            }
                
                # Check affected zones
                zone = self._get_pricing_zone(pickup_lat, pickup_lng)
                if zone and zone in event.affected_zones.all():
                    multiplier = event.get_current_multiplier()
                    if multiplier > highest_multiplier:
                        highest_multiplier = multiplier
                        event_info = {
                            'name': event.name,
                            'type': event.event_type,
                            'multiplier': str(multiplier)
                        }
        
        if event_info:
            self.calculation_log['factors_applied'].append({
                'type': 'special_event',
                **event_info
            })
        
        return highest_multiplier
    
    def _get_tier_multiplier(self, user_tier: str, pricing_rule: PricingRule) -> Decimal:
        """Get user tier-based multiplier"""
        multiplier_map = {
            UserTier.NORMAL: pricing_rule.normal_multiplier,
            UserTier.PREMIUM: pricing_rule.premium_multiplier,
            UserTier.VIP: pricing_rule.vip_multiplier
        }
        
        multiplier = multiplier_map.get(user_tier, Decimal('1.000'))
        
        if multiplier != Decimal('1.000'):
            self.calculation_log['factors_applied'].append({
                'type': 'tier_pricing',
                'tier': user_tier,
                'multiplier': str(multiplier)
            })
        
        return multiplier
    
    def _apply_promo_code(
        self, 
        promo_code: str, 
        user, 
        subtotal: Decimal, 
        surge_multiplier: Decimal
    ) -> Tuple[Decimal, Dict]:
        """Apply promotional code discount"""
        if not promo_code:
            return Decimal('0.00'), {}
        
        try:
            promo = PromotionalCode.objects.get(code=promo_code.upper())
            
            # Check if user can use this code
            can_use, reason = promo.can_user_use(user)
            if not can_use:
                return Decimal('0.00'), {'error': reason}
            
            # Calculate discount
            discount_amount = Decimal('0.00')
            
            if promo.code_type == PromotionalCode.CodeType.SURGE_WAIVER:
                # Remove surge pricing
                if surge_multiplier > Decimal('1.000'):
                    base_amount = subtotal / surge_multiplier
                    discount_amount = subtotal - base_amount
            else:
                # Apply discount to subtotal
                discount_amount = promo.calculate_discount(subtotal, user.tier)
                
                # Check if discount applies to surge pricing
                if not promo.applies_to_surge and surge_multiplier > Decimal('1.000'):
                    # Apply discount only to base amount
                    base_amount = subtotal / surge_multiplier
                    discount_amount = promo.calculate_discount(base_amount, user.tier)
            
            # Ensure discount doesn't exceed subtotal
            discount_amount = min(discount_amount, subtotal)
            
            promo_details = {
                'code': promo.code,
                'type': promo.code_type,
                'discount_amount': str(discount_amount),
                'description': promo.description
            }
            
            self.calculation_log['factors_applied'].append({
                'type': 'promotional_discount',
                **promo_details
            })
            
            return discount_amount, promo_details
            
        except PromotionalCode.DoesNotExist:
            return Decimal('0.00'), {'error': 'Invalid promo code'}
        except Exception as e:
            logger.error(f"Error applying promo code {promo_code}: {e}")
            return Decimal('0.00'), {'error': 'Unable to apply promo code'}
    
    def _generate_transparency_info(
        self, 
        zone: PricingZone, 
        surge_multiplier: Decimal, 
        event_multiplier: Decimal,
        promo_details: Dict
    ) -> Dict:
        """Generate transparent pricing information for users"""
        info = {
            'pricing_factors': [],
            'user_friendly_explanation': []
        }
        
        # Zone pricing
        if zone and zone.base_multiplier != Decimal('1.000'):
            info['pricing_factors'].append({
                'factor': 'Location',
                'description': f'Pricing for {zone.name}',
                'multiplier': str(zone.base_multiplier)
            })
        
        # Surge pricing
        if surge_multiplier > Decimal('1.000'):
            surge_percentage = (surge_multiplier - Decimal('1.000')) * 100
            info['pricing_factors'].append({
                'factor': 'High Demand',
                'description': f'{surge_percentage:.0f}% increase due to high demand',
                'multiplier': str(surge_multiplier),
                'icon': 'surge'
            })
            info['user_friendly_explanation'].append(
                f"Prices are {surge_percentage:.0f}% higher due to increased demand in your area."
            )
        
        # Event pricing
        if event_multiplier > Decimal('1.000'):
            event_percentage = (event_multiplier - Decimal('1.000')) * 100
            info['pricing_factors'].append({
                'factor': 'Special Event',
                'description': f'{event_percentage:.0f}% increase due to special event',
                'multiplier': str(event_multiplier),
                'icon': 'event'
            })
            info['user_friendly_explanation'].append(
                f"Prices are {event_percentage:.0f}% higher due to a special event nearby."
            )
        
        # Promotional discount
        if promo_details and 'discount_amount' in promo_details:
            info['pricing_factors'].append({
                'factor': 'Promotion',
                'description': f"Promo code '{promo_details['code']}' applied",
                'discount': promo_details['discount_amount'],
                'icon': 'promo'
            })
            info['user_friendly_explanation'].append(
                f"You saved with promo code '{promo_details['code']}'!"
            )
        
        return info
    
    def _log_calculation(
        self, user, pickup_lat, pickup_lng, dropoff_lat, dropoff_lng, distance_km, 
        estimated_duration_minutes, vehicle_type, pricing_rule,
        zone_multiplier, time_multiplier, surge_multiplier,
        event_multiplier, tier_multiplier, base_fare, 
        subtotal, promo_discount, final_price, promo_code
    ):
        """Log detailed price calculation for auditing"""
        try:
            PriceCalculationLog.objects.create(
                user=user,
                pickup_latitude=pickup_lat,
                pickup_longitude=pickup_lng,
                dropoff_latitude=dropoff_lat,
                dropoff_longitude=dropoff_lng,
                distance_km=distance_km,
                estimated_duration_minutes=estimated_duration_minutes,
                vehicle_type=vehicle_type,
                base_fare=base_fare,
                distance_fare=pricing_rule.per_km_rate * distance_km,
                time_fare=pricing_rule.per_minute_rate * Decimal(str(estimated_duration_minutes)),
                subtotal=base_fare,
                zone_multiplier=zone_multiplier,
                time_multiplier=time_multiplier,
                surge_multiplier=surge_multiplier,
                event_multiplier=event_multiplier,
                tier_multiplier=tier_multiplier,
                total_before_discount=subtotal,
                promo_discount=promo_discount,
                final_price=final_price,
                applied_promo_code=promo_code or '',
                pricing_factors=self.calculation_log
            )
        except Exception as e:
            logger.error(f"Failed to log price calculation: {e}")


class SurgeManagementService:
    """Service for managing real-time surge pricing"""
    
    @staticmethod
    def update_zone_surge(zone_id: str):
        """Update surge pricing for a specific zone"""
        try:
            zone = PricingZone.objects.get(id=zone_id)
            engine = PricingEngine()
            engine._calculate_real_time_surge(zone, timezone.now())
        except PricingZone.DoesNotExist:
            logger.error(f"Zone {zone_id} not found")
        except Exception as e:
            logger.error(f"Error updating surge for zone {zone_id}: {e}")
    
    @staticmethod
    def update_all_zones_surge():
        """Update surge pricing for all active zones"""
        active_zones = PricingZone.objects.filter(is_active=True)
        for zone in active_zones:
            SurgeManagementService.update_zone_surge(str(zone.id))
    
    @staticmethod
    def get_current_surge_levels() -> Dict:
        """Get current surge levels for all zones"""
        surge_data = {}
        current_surges = DemandSurge.objects.filter(
            is_active=True,
            expires_at__gt=timezone.now()
        ).select_related('zone')
        
        for surge in current_surges:
            surge_data[surge.zone.name] = {
                'level': surge.surge_level,
                'multiplier': str(surge.surge_multiplier),
                'demand_ratio': str(surge.demand_ratio)
            }
        
        return surge_data
