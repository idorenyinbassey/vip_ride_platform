# rides/workflow.py
"""
VIP Ride-Hailing Platform - Ride Status Workflow System
Comprehensive state machine for ride progression with tier-based policies
"""

from datetime import datetime, timedelta
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from typing import Dict, List, Optional, Tuple
import logging

from .models import Ride, RideStatus
from .status_models import RideStatusHistory
from accounts.models import User

logger = logging.getLogger(__name__)


class RideWorkflowError(Exception):
    """Custom exception for ride workflow errors"""
    pass


class CancellationPolicy:
    """Tier-based cancellation policies"""
    
    POLICIES = {
        'normal': {
            'free_cancellation_window': 300,  # 5 minutes
            'cancellation_fee': 0.00,
            'max_cancellations_per_day': 3,
            'driver_acceptance_timeout': 180,  # 3 minutes
        },
        'premium': {
            'free_cancellation_window': 600,  # 10 minutes
            'cancellation_fee': 0.00,
            'max_cancellations_per_day': 5,
            'driver_acceptance_timeout': 120,  # 2 minutes
        },
        'vip': {
            'free_cancellation_window': 900,  # 15 minutes
            'cancellation_fee': 0.00,
            'max_cancellations_per_day': 10,
            'driver_acceptance_timeout': 60,  # 1 minute
        }
    }
    
    @classmethod
    def get_policy(cls, user_tier: str) -> Dict:
        """Get cancellation policy for user tier"""
        return cls.POLICIES.get(user_tier.lower(), cls.POLICIES['normal'])
    
    @classmethod
    def can_cancel_free(cls, ride, user_tier: str) -> Tuple[bool, str]:
        """Check if user can cancel for free"""
        policy = cls.get_policy(user_tier)
        time_since_request = (timezone.now() - ride.created_at).total_seconds()
        
        if time_since_request <= policy['free_cancellation_window']:
            return True, "Free cancellation within allowed window"
        
        # Check if driver has been assigned
        if ride.status in [RideStatus.DRIVER_FOUND.value, RideStatus.DRIVER_ACCEPTED.value]:
            return False, f"Cancellation fee applies: ${policy['cancellation_fee']}"
        
        return True, "Free cancellation allowed"
    
    @classmethod
    def check_daily_cancellation_limit(cls, user, user_tier: str) -> Tuple[bool, str]:
        """Check if user has exceeded daily cancellation limit"""
        policy = cls.get_policy(user_tier)
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        today_cancellations = Ride.objects.filter(
            rider=user,
            created_at__gte=today_start,
            status__in=[
                RideStatus.CANCELLED_BY_RIDER.value,
                RideStatus.CANCELLED_BY_DRIVER.value
            ]
        ).count()
        
        if today_cancellations >= policy['max_cancellations_per_day']:
            return False, f"Daily cancellation limit exceeded ({policy['max_cancellations_per_day']})"
        
        return True, "Within daily cancellation limit"


class RideWorkflow:
    """State machine for ride status workflow"""
    
    # Valid state transitions
    VALID_TRANSITIONS = {
        RideStatus.REQUESTED: [
            RideStatus.DRIVER_SEARCH,
            RideStatus.CANCELLED_BY_RIDER,
            RideStatus.CANCELLED_BY_SYSTEM
        ],
        RideStatus.DRIVER_SEARCH: [
            RideStatus.DRIVER_FOUND,
            RideStatus.CANCELLED_BY_RIDER,
            RideStatus.CANCELLED_BY_SYSTEM
        ],
        RideStatus.DRIVER_FOUND: [
            RideStatus.DRIVER_ACCEPTED,
            RideStatus.DRIVER_REJECTED,
            RideStatus.CANCELLED_BY_RIDER,
            RideStatus.CANCELLED_BY_SYSTEM
        ],
        RideStatus.DRIVER_ACCEPTED: [
            RideStatus.DRIVER_EN_ROUTE,
            RideStatus.CANCELLED_BY_RIDER,
            RideStatus.CANCELLED_BY_DRIVER
        ],
        RideStatus.DRIVER_REJECTED: [
            RideStatus.DRIVER_SEARCH,
            RideStatus.CANCELLED_BY_SYSTEM
        ],
        RideStatus.DRIVER_EN_ROUTE: [
            RideStatus.DRIVER_ARRIVED,
            RideStatus.CANCELLED_BY_RIDER,
            RideStatus.CANCELLED_BY_DRIVER
        ],
        RideStatus.DRIVER_ARRIVED: [
            RideStatus.IN_PROGRESS,
            RideStatus.CANCELLED_BY_RIDER,
            RideStatus.CANCELLED_BY_DRIVER
        ],
        RideStatus.IN_PROGRESS: [
            RideStatus.COMPLETED,
            RideStatus.CANCELLED_BY_DRIVER,
            RideStatus.DISPUTED
        ],
        RideStatus.COMPLETED: [
            RideStatus.PAYMENT_PENDING,
            RideStatus.DISPUTED
        ],
        RideStatus.PAYMENT_PENDING: [
            RideStatus.PAYMENT_COMPLETED,
            RideStatus.PAYMENT_FAILED,
            RideStatus.DISPUTED
        ],
        RideStatus.PAYMENT_FAILED: [
            RideStatus.PAYMENT_PENDING,
            RideStatus.CANCELLED_BY_SYSTEM,
            RideStatus.DISPUTED
        ],
        RideStatus.PAYMENT_COMPLETED: [
            RideStatus.DISPUTED
        ],
        # Terminal states
        RideStatus.CANCELLED_BY_RIDER: [],
        RideStatus.CANCELLED_BY_DRIVER: [],
        RideStatus.CANCELLED_BY_SYSTEM: [],
        RideStatus.DISPUTED: [RideStatus.REFUNDED],
        RideStatus.REFUNDED: []
    }
    
    def __init__(self, ride: Ride):
        self.ride = ride
        self.current_status = RideStatus(ride.status)
    
    def can_transition_to(self, new_status: RideStatus) -> bool:
        """Check if transition to new status is valid"""
        return new_status in self.VALID_TRANSITIONS.get(self.current_status, [])
    
    @transaction.atomic
    def transition_to(self, new_status: RideStatus, user: User = None, reason: str = None) -> bool:
        """Transition ride to new status with validation and logging"""
        try:
            if not self.can_transition_to(new_status):
                raise RideWorkflowError(
                    f"Invalid transition from {self.current_status.value} to {new_status.value}"
                )
            
            old_status = self.current_status
            self.ride.status = new_status.value
            self.ride.updated_at = timezone.now()
            
            # Update specific fields based on status
            self._update_ride_fields(new_status)
            
            self.ride.save()
            
            # Log status change
            self._log_status_change(old_status, new_status, user, reason)
            
            # Trigger automatic actions
            self._trigger_status_actions(new_status)
            
            self.current_status = new_status
            
            logger.info(f"Ride {self.ride.id} transitioned from {old_status.value} to {new_status.value}")
            return True
            
        except Exception as e:
            logger.error(f"Error transitioning ride {self.ride.id}: {str(e)}")
            raise RideWorkflowError(f"Transition failed: {str(e)}")
    
    def _update_ride_fields(self, new_status: RideStatus):
        """Update ride fields based on new status"""
        if new_status == RideStatus.DRIVER_ACCEPTED:
            self.ride.driver_accepted_at = timezone.now()
        elif new_status == RideStatus.DRIVER_EN_ROUTE:
            self.ride.driver_en_route_at = timezone.now()
        elif new_status == RideStatus.DRIVER_ARRIVED:
            self.ride.driver_arrived_at = timezone.now()
        elif new_status == RideStatus.IN_PROGRESS:
            self.ride.started_at = timezone.now()
        elif new_status == RideStatus.COMPLETED:
            self.ride.completed_at = timezone.now()
            self.ride.calculate_final_fare()
        elif new_status in [
            RideStatus.CANCELLED_BY_RIDER,
            RideStatus.CANCELLED_BY_DRIVER,
            RideStatus.CANCELLED_BY_SYSTEM
        ]:
            self.ride.cancelled_at = timezone.now()
    
    def _log_status_change(self, old_status: RideStatus, new_status: RideStatus, 
                          user: User = None, reason: str = None):
        """Log status change in history"""
        RideStatusHistory.objects.create(
            ride=self.ride,
            from_status=old_status.value,
            to_status=new_status.value,
            changed_by=user,
            reason=reason or f"Automatic transition to {new_status.value}",
            timestamp=timezone.now()
        )
    
    def _trigger_status_actions(self, new_status: RideStatus):
        """Trigger automatic actions based on new status"""
        actions = {
            RideStatus.DRIVER_SEARCH: self._start_driver_search,
            RideStatus.DRIVER_FOUND: self._notify_driver_assignment,
            RideStatus.DRIVER_ACCEPTED: self._notify_rider_driver_accepted,
            RideStatus.DRIVER_EN_ROUTE: self._notify_rider_driver_en_route,
            RideStatus.DRIVER_ARRIVED: self._notify_rider_driver_arrived,
            RideStatus.IN_PROGRESS: self._start_ride_tracking,
            RideStatus.COMPLETED: self._initiate_payment,
            RideStatus.PAYMENT_COMPLETED: self._finalize_ride,
            RideStatus.CANCELLED_BY_RIDER: self._handle_rider_cancellation,
            RideStatus.CANCELLED_BY_DRIVER: self._handle_driver_cancellation,
        }
        
        action = actions.get(new_status)
        if action:
            try:
                action()
            except Exception as e:
                logger.error(f"Error executing action for status {new_status.value}: {str(e)}")
    
    def _start_driver_search(self):
        """Start searching for available drivers"""
        from .matching import RideMatchingService
        matching_service = RideMatchingService()
        matching_service.find_drivers_for_ride(self.ride)
    
    def _notify_driver_assignment(self):
        """Notify driver of ride assignment"""
        if self.ride.driver:
            Notification.objects.create(
                user=self.ride.driver.user,
                title="New Ride Request",
                message=f"You have a new ride request from {self.ride.pickup_address}",
                notification_type="ride_assignment",
                data={
                    'ride_id': self.ride.id,
                    'pickup_address': self.ride.pickup_address,
                    'destination_address': self.ride.destination_address,
                    'estimated_fare': str(self.ride.estimated_fare)
                }
            )
    
    def _notify_rider_driver_accepted(self):
        """Notify rider that driver accepted"""
        Notification.objects.create(
            user=self.ride.rider,
            title="Driver Accepted",
            message=f"Your driver {self.ride.driver.user.get_full_name()} is on the way",
            notification_type="driver_accepted",
            data={
                'ride_id': self.ride.id,
                'driver_name': self.ride.driver.user.get_full_name(),
                'vehicle_info': f"{self.ride.driver.vehicle_make} {self.ride.driver.vehicle_model}",
                'license_plate': self.ride.driver.license_plate
            }
        )
    
    def _notify_rider_driver_en_route(self):
        """Notify rider that driver is en route"""
        Notification.objects.create(
            user=self.ride.rider,
            title="Driver En Route",
            message="Your driver is on the way to pick you up",
            notification_type="driver_en_route",
            data={'ride_id': self.ride.id}
        )
    
    def _notify_rider_driver_arrived(self):
        """Notify rider that driver has arrived"""
        Notification.objects.create(
            user=self.ride.rider,
            title="Driver Arrived",
            message="Your driver has arrived at the pickup location",
            notification_type="driver_arrived",
            data={'ride_id': self.ride.id}
        )
    
    def _start_ride_tracking(self):
        """Start real-time ride tracking"""
        # Enable GPS tracking for the ride
        from gps_tracking.services import GPSTrackingService
        gps_service = GPSTrackingService()
        gps_service.start_ride_tracking(self.ride)
    
    def _initiate_payment(self):
        """Initiate payment processing"""
        try:
            from payments.services import PaymentService
            payment_service = PaymentService()
            
            # Create payment transaction
            transaction = payment_service.create_ride_payment(self.ride)
            
            if transaction:
                self.transition_to(RideStatus.PAYMENT_PENDING)
            else:
                self.transition_to(RideStatus.PAYMENT_FAILED)
                
        except Exception as e:
            logger.error(f"Payment initiation failed for ride {self.ride.id}: {str(e)}")
            self.transition_to(RideStatus.PAYMENT_FAILED)
    
    def _finalize_ride(self):
        """Finalize ride after successful payment"""
        # Update driver earnings
        if self.ride.driver:
            self.ride.driver.total_earnings += self.ride.driver_earnings
            self.ride.driver.total_rides += 1
            self.ride.driver.save()
        
        # Send completion notifications
        Notification.objects.create(
            user=self.ride.rider,
            title="Ride Completed",
            message="Your ride has been completed successfully",
            notification_type="ride_completed",
            data={'ride_id': self.ride.id}
        )
        
        if self.ride.driver:
            Notification.objects.create(
                user=self.ride.driver.user,
                title="Ride Completed",
                message="Ride completed successfully. Payment processed.",
                notification_type="ride_completed",
                data={'ride_id': self.ride.id}
            )
    
    def _handle_rider_cancellation(self):
        """Handle ride cancellation by rider"""
        # Check cancellation policy
        user_tier = getattr(self.ride.rider, 'tier', 'normal')
        can_cancel_free, message = CancellationPolicy.can_cancel_free(self.ride, user_tier)
        
        if not can_cancel_free:
            # Apply cancellation fee
            self._apply_cancellation_fee(user_tier)
        
        # Notify driver if assigned
        if self.ride.driver:
            Notification.objects.create(
                user=self.ride.driver.user,
                title="Ride Cancelled",
                message="The ride has been cancelled by the rider",
                notification_type="ride_cancelled",
                data={'ride_id': self.ride.id}
            )
    
    def _handle_driver_cancellation(self):
        """Handle ride cancellation by driver"""
        # Find new driver
        self.transition_to(RideStatus.DRIVER_SEARCH)
        
        # Notify rider
        Notification.objects.create(
            user=self.ride.rider,
            title="Driver Cancelled",
            message="Your driver had to cancel. We're finding you a new driver.",
            notification_type="driver_cancelled",
            data={'ride_id': self.ride.id}
        )
    
    def _apply_cancellation_fee(self, user_tier: str):
        """Apply cancellation fee based on user tier"""
        policy = CancellationPolicy.get_policy(user_tier)
        fee = policy['cancellation_fee']
        
        if fee > 0:
            from payments.services import PaymentService
            payment_service = PaymentService()
            payment_service.charge_cancellation_fee(self.ride, fee)


class RideWorkflowManager:
    """Manager for ride workflow operations"""
    
    @staticmethod
    def request_ride(rider: User, pickup_location: dict, destination_location: dict, 
                    ride_type: str = 'normal') -> Ride:
        """Create new ride request and start workflow"""
        try:
            with transaction.atomic():
                # Create ride
                ride = Ride.objects.create(
                    rider=rider,
                    pickup_latitude=pickup_location['latitude'],
                    pickup_longitude=pickup_location['longitude'],
                    pickup_address=pickup_location.get('address', ''),
                    destination_latitude=destination_location['latitude'],
                    destination_longitude=destination_location['longitude'],
                    destination_address=destination_location.get('address', ''),
                    ride_type=ride_type,
                    status=RideStatus.REQUESTED.value
                )
                
                # Start workflow
                workflow = RideWorkflow(ride)
                workflow.transition_to(RideStatus.DRIVER_SEARCH, user=rider)
                
                return ride
                
        except Exception as e:
            logger.error(f"Error creating ride request: {str(e)}")
            raise RideWorkflowError(f"Failed to create ride request: {str(e)}")
    
    @staticmethod
    def driver_accept_ride(ride: Ride, driver_user: User) -> bool:
        """Handle driver accepting ride"""
        try:
            workflow = RideWorkflow(ride)
            
            if workflow.current_status != RideStatus.DRIVER_FOUND:
                raise RideWorkflowError("Ride not in correct state for acceptance")
            
            # Assign driver
            from fleet_management.models import Driver
            driver = Driver.objects.get(user=driver_user)
            ride.driver = driver
            ride.save()
            
            # Transition status
            workflow.transition_to(RideStatus.DRIVER_ACCEPTED, user=driver_user)
            
            # Auto-transition to en route after short delay
            from django.utils import timezone
            from datetime import timedelta
            
            # Schedule en route transition (this would be done via Celery in production)
            workflow.transition_to(RideStatus.DRIVER_EN_ROUTE, user=driver_user)
            
            return True
            
        except Exception as e:
            logger.error(f"Error in driver acceptance: {str(e)}")
            return False
    
    @staticmethod
    def driver_reject_ride(ride: Ride, driver_user: User, reason: str = None) -> bool:
        """Handle driver rejecting ride"""
        try:
            workflow = RideWorkflow(ride)
            workflow.transition_to(RideStatus.DRIVER_REJECTED, user=driver_user, reason=reason)
            
            # Continue searching for another driver
            workflow.transition_to(RideStatus.DRIVER_SEARCH)
            
            return True
            
        except Exception as e:
            logger.error(f"Error in driver rejection: {str(e)}")
            return False
    
    @staticmethod
    def cancel_ride(ride: Ride, user: User, reason: str = None) -> Tuple[bool, str]:
        """Handle ride cancellation with policy checks"""
        try:
            workflow = RideWorkflow(ride)
            
            # Determine cancellation type
            if user == ride.rider:
                # Check cancellation policy
                user_tier = getattr(user, 'tier', 'normal')
                can_cancel, limit_message = CancellationPolicy.check_daily_cancellation_limit(user, user_tier)
                
                if not can_cancel:
                    return False, limit_message
                
                can_cancel_free, fee_message = CancellationPolicy.can_cancel_free(ride, user_tier)
                
                workflow.transition_to(RideStatus.CANCELLED_BY_RIDER, user=user, reason=reason)
                return True, fee_message
                
            elif hasattr(user, 'driver') and ride.driver and user == ride.driver.user:
                workflow.transition_to(RideStatus.CANCELLED_BY_DRIVER, user=user, reason=reason)
                return True, "Ride cancelled by driver"
            else:
                return False, "User not authorized to cancel this ride"
                
        except Exception as e:
            logger.error(f"Error cancelling ride: {str(e)}")
            return False, str(e)
    
    @staticmethod
    def complete_ride(ride: Ride, driver_user: User) -> bool:
        """Handle ride completion"""
        try:
            workflow = RideWorkflow(ride)
            
            if workflow.current_status != RideStatus.IN_PROGRESS:
                raise RideWorkflowError("Ride not in progress")
            
            workflow.transition_to(RideStatus.COMPLETED, user=driver_user)
            return True
            
        except Exception as e:
            logger.error(f"Error completing ride: {str(e)}")
            return False
    
    @staticmethod
    def confirm_payment(ride: Ride, payment_success: bool) -> bool:
        """Confirm payment processing result"""
        try:
            workflow = RideWorkflow(ride)
            
            if payment_success:
                workflow.transition_to(RideStatus.PAYMENT_COMPLETED)
            else:
                workflow.transition_to(RideStatus.PAYMENT_FAILED)
            
            return True
            
        except Exception as e:
            logger.error(f"Error confirming payment: {str(e)}")
            return False


# Utility functions for workflow management
def get_ride_workflow(ride_id: int) -> RideWorkflow:
    """Get workflow instance for ride"""
    try:
        ride = Ride.objects.get(id=ride_id)
        return RideWorkflow(ride)
    except Ride.DoesNotExist:
        raise RideWorkflowError(f"Ride {ride_id} not found")


def get_rides_by_status(status: RideStatus) -> List[Ride]:
    """Get all rides with specific status"""
    return Ride.objects.filter(status=status.value)


def get_user_active_rides(user: User) -> List[Ride]:
    """Get user's active rides"""
    active_statuses = [
        RideStatus.REQUESTED.value,
        RideStatus.DRIVER_SEARCH.value,
        RideStatus.DRIVER_FOUND.value,
        RideStatus.DRIVER_ACCEPTED.value,
        RideStatus.DRIVER_EN_ROUTE.value,
        RideStatus.DRIVER_ARRIVED.value,
        RideStatus.IN_PROGRESS.value,
        RideStatus.PAYMENT_PENDING.value
    ]
    
    return Ride.objects.filter(
        rider=user,
        status__in=active_statuses
    ).order_by('-created_at')
