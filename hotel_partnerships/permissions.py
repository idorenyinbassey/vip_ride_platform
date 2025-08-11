from rest_framework import permissions
from .models import HotelStaff


class IsHotelStaff(permissions.BasePermission):
    """
    Permission class for hotel staff users
    """
    
    def _get_hotel_staff(self, request):
        """Get hotel staff instance with caching"""
        # Return cached instance if available
        if hasattr(request, '_hotel_staff'):
            return request._hotel_staff
        
        try:
            hotel_staff = HotelStaff.objects.select_related('hotel').filter(
                user=request.user, 
                is_active=True
            ).first()
            
            # Cache the result
            request._hotel_staff = hotel_staff
            return hotel_staff
        except (HotelStaff.DoesNotExist, HotelStaff.MultipleObjectsReturned):
            return None
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        hotel_staff = self._get_hotel_staff(request)
        return hotel_staff and hotel_staff.can_make_bookings
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        
        hotel_staff = self._get_hotel_staff(request)
        
        if not hotel_staff:
            return False
        
        # Check if the object belongs to the staff's hotel
        if hasattr(obj, 'hotel'):
            return obj.hotel == hotel_staff.hotel
        elif hasattr(obj, 'hotel_id'):
            return obj.hotel_id == hotel_staff.hotel.id
        
        return False


class IsHotelStaffOrReadOnly(permissions.BasePermission):
    """
    Permission class that allows read access to all, 
    but write access only to hotel staff
    """
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return IsHotelStaff().has_permission(request, view)
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return IsHotelStaff().has_object_permission(request, view, obj)


class IsHotelAdmin(permissions.BasePermission):
    """
    Permission class for hotel administrators
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        try:
            hotel_staff = HotelStaff.objects.filter(
                user=request.user, 
                is_active=True
            ).order_by('id').first()
            
            if hotel_staff:
                return (hotel_staff.role in ['ADMIN', 'MANAGER'] and 
                        hotel_staff.permission_level == 'FULL')
            return False
        except Exception:
            return False


class CanViewReports(permissions.BasePermission):
    """
    Permission class for viewing reports and analytics
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        try:
            hotel_staff = HotelStaff.objects.get(
                user=request.user, 
                is_active=True
            )
            return hotel_staff.can_view_analytics
        except HotelStaff.DoesNotExist:
            return False
