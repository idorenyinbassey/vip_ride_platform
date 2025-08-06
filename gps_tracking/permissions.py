"""
Custom permissions for GPS tracking
"""

from rest_framework import permissions


class IsVIPUserOrControlCenter(permissions.BasePermission):
    """
    Permission to allow access only to VIP users or control center staff
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Allow control center staff
        if (request.user.is_staff or 
            hasattr(request.user, 'role') and 
            request.user.role in ['ADMIN', 'CONTROL_CENTER']):
            return True
        
        # Allow VIP users
        if hasattr(request.user, 'tier') and request.user.tier == 'VIP':
            return True
        
        return False


class IsDriverOrCustomer(permissions.BasePermission):
    """
    Permission to allow access to drivers and customers
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Check if user is a driver or customer in the system
        return (hasattr(request.user, 'driver_profile') or 
                hasattr(request.user, 'customer_profile') or
                request.user.is_staff)


class IsOwnerOrVIPMonitoring(permissions.BasePermission):
    """
    Permission to allow access to resource owner or VIP monitoring staff
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Object owner always has access
        if obj.user == request.user:
            return True
        
        # VIP monitoring staff can access VIP user data
        if (hasattr(obj.user, 'tier') and obj.user.tier == 'VIP' and
            request.user.is_staff):
            return True
        
        return False


class IsRideParticipant(permissions.BasePermission):
    """
    Permission to allow access only to ride participants
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Check if user is participant in the ride
        if hasattr(obj, 'ride') and obj.ride:
            return (request.user == obj.ride.customer or 
                    request.user == obj.ride.driver.user)
        
        return obj.user == request.user
