"""
Vehicle Leasing services
"""

from decimal import Decimal
from django.db.models import Sum, Count, Avg
from .models import VehicleLease, LeasePayment


class VehicleLeasingService:
    """Main service for vehicle leasing operations"""
    
    def calculate_lease_terms(self, vehicle_id, revenue_share_model, **kwargs):
        """Calculate lease terms based on revenue share model"""
        
        expected_monthly_rides = kwargs.get('expected_monthly_rides', 100)
        average_ride_value = Decimal(str(kwargs.get('average_ride_value', 2500)))
        
        # Calculate estimated monthly revenue
        estimated_monthly_revenue = expected_monthly_rides * average_ride_value
        
        if revenue_share_model == VehicleLease.RevenueShareModel.FIXED_MONTHLY:
            fixed_payment = Decimal(str(kwargs.get('fixed_monthly_payment', 50000)))
            owner_share = fixed_payment
            fleet_share = estimated_monthly_revenue - fixed_payment
            
        elif revenue_share_model == VehicleLease.RevenueShareModel.PERCENTAGE_REVENUE:
            revenue_percentage = Decimal(str(kwargs.get('revenue_percentage', 30))) / 100
            owner_share = estimated_monthly_revenue * revenue_percentage
            fleet_share = estimated_monthly_revenue * (1 - revenue_percentage)
            
        elif revenue_share_model == VehicleLease.RevenueShareModel.PER_RIDE:
            per_ride_commission = Decimal(str(kwargs.get('per_ride_commission', 500)))
            owner_share = expected_monthly_rides * per_ride_commission
            fleet_share = estimated_monthly_revenue - owner_share
            
        else:  # HYBRID
            fixed_payment = Decimal(str(kwargs.get('fixed_monthly_payment', 30000)))
            revenue_percentage = Decimal(str(kwargs.get('revenue_percentage', 15))) / 100
            variable_share = estimated_monthly_revenue * revenue_percentage
            owner_share = fixed_payment + variable_share
            fleet_share = estimated_monthly_revenue - owner_share
        
        return {
            'vehicle_id': vehicle_id,
            'revenue_share_model': revenue_share_model,
            'estimated_monthly_revenue': str(estimated_monthly_revenue),
            'owner_share': str(owner_share),
            'fleet_share': str(fleet_share),
            'expected_monthly_rides': expected_monthly_rides,
            'average_ride_value': str(average_ride_value)
        }
    
    def get_lease_analytics(self, lease_id):
        """Get analytics for a specific lease"""
        try:
            lease = VehicleLease.objects.get(id=lease_id)
            
            # Calculate total payments
            total_payments = lease.lease_payments.aggregate(
                total=Sum('amount')
            )['total'] or 0
            
            # Calculate payment stats
            payment_stats = lease.lease_payments.aggregate(
                count=Count('id'),
                avg_amount=Avg('amount')
            )
            
            return {
                'lease_id': lease_id,
                'status': lease.status,
                'total_payments': total_payments,
                'payment_count': payment_stats['count'],
                'average_payment': payment_stats['avg_amount'] or 0
            }
            
        except VehicleLease.DoesNotExist:
            return None


class LeaseCalculationService:
    """Service for lease calculations"""
    
    def calculate_lease_terms(
        self,
        vehicle_value,
        lease_duration,
        down_payment=0,
        interest_rate=8.5
    ):
        """Calculate lease terms"""
        principal = Decimal(str(vehicle_value)) - Decimal(str(down_payment))
        
        # Simple calculation - in production use proper lease formulas
        monthly_payment = principal / lease_duration
        total_amount = monthly_payment * lease_duration
        
        return {
            'vehicle_value': vehicle_value,
            'down_payment': down_payment,
            'lease_duration': lease_duration,
            'monthly_payment': float(monthly_payment),
            'total_amount': float(total_amount),
            'interest_rate': interest_rate
        }


class VehicleSearchService:
    """Service for vehicle search"""
    
    def search_vehicles(self, search_params):
        """Search vehicles based on parameters"""
        # Placeholder implementation
        return {
            'vehicles': [],
            'total_count': 0,
            'filters_applied': search_params
        }
