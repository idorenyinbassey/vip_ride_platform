"""
Fleet Management Permissions
Custom permissions for fleet and vehicle operations
"""

from rest_framework.permissions import BasePermission


class IsFleetOwner(BasePermission):
    """Permission for fleet company owners"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Check if user owns the fleet company
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        return False


class IsVehicleOwner(BasePermission):
    """Permission for vehicle owners"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Check if user owns the vehicle
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        return False


class IsFleetManagerOrOwner(BasePermission):
    """Permission for fleet managers or vehicle owners"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # Vehicle owner has permission
        if hasattr(obj, 'owner') and obj.owner == user:
            return True
        
        # Fleet manager has permission for vehicles leased to their fleets
        if hasattr(user, 'fleet_companies'):
            fleet_companies = user.fleet_companies.all()
            if (fleet_companies.exists() and 
                hasattr(obj, 'ownership_status') and 
                obj.ownership_status == 'leased_to_fleet' and
                hasattr(obj, 'fleet_company') and
                obj.fleet_company in fleet_companies):
                return True
        
        return False


class CanManageFleetVehicles(BasePermission):
    """Permission to manage vehicles in fleet"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # Superuser has all permissions
        if user.is_superuser:
            return True
        
        # Fleet owner can manage vehicles in their specific fleet
        try:
            from .models import FleetCompany
            fleet_companies = FleetCompany.objects.filter(owner=user)
            if fleet_companies.exists():
                # Check if the object is related to one of user's fleets
                if hasattr(obj, 'fleet_company'):
                    return obj.fleet_company in fleet_companies
                elif hasattr(obj, 'owner') and obj.owner == user:
                    return True
            return False
        except ImportError:
            return False
