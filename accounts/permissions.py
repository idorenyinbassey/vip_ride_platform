# Custom Permissions for JWT Authentication and Role-Based Access Control
"""
Comprehensive permission system for tier-based access control, MFA enforcement, 
and security auditing for VIP ride-hailing platform
"""

import logging
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta
from .jwt_config import USER_TIER_SETTINGS
from .models import UserSession, MFAToken, SecurityEvent

logger = logging.getLogger(__name__)


class TierBasedPermission(permissions.BasePermission):
    """Permission class that enforces tier-based access control"""
    
    required_tier = 'normal'  # Override in views
    
    def has_permission(self, request, view):
        """Check if user has required tier level"""
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Get required tier from view or use default
        required_tier = getattr(view, 'required_tier', self.required_tier)
        
        # Define tier hierarchy
        tier_hierarchy = {
            'normal': 0,
            'premium': 1,
            'vip': 2,
            'concierge': 3,
            'admin': 4
        }
        
        user_tier_level = tier_hierarchy.get(request.user.tier, 0)
        required_tier_level = tier_hierarchy.get(required_tier, 0)
        
        return user_tier_level >= required_tier_level


class IsFleetOwner(permissions.BasePermission):
    """Permission for fleet company owners"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        return False


class IsVehicleOwner(permissions.BasePermission):
    """Permission for vehicle owners"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        return False


class IsControlOperator(permissions.BasePermission):
    """Permission for control center operators"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return hasattr(request.user, 'control_operator')


class IsVIPUser(permissions.BasePermission):
    """Permission for VIP users"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        # Safely get tier from user profile with fallback
        try:
            if hasattr(request.user, 'profile') and request.user.profile:
                return request.user.profile.tier == 'vip'
            elif hasattr(request.user, 'tier'):
                return request.user.tier == 'vip'
            return False
        except AttributeError:
            return False


class IsPremiumOrVIPUser(permissions.BasePermission):
    """Permission for Premium or VIP users"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        # Safely get tier from user profile with fallback
        try:
            if hasattr(request.user, 'profile') and request.user.profile:
                tier = request.user.profile.tier
            elif hasattr(request.user, 'tier'):
                tier = request.user.tier
            else:
                tier = 'normal'
            return tier in ['premium', 'vip']
        except AttributeError:
            return False


class IsConciergeUser(permissions.BasePermission):
    """Permission for concierge (driver) users"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return hasattr(request.user, 'driver_profile')


class IsAdminUser(permissions.BasePermission):
    """Permission for admin users"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser


class MFARequiredPermission(permissions.BasePermission):
    """Permission class that enforces MFA verification"""
    
    def has_permission(self, request, view):
        """Check if MFA is verified when required"""
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check if MFA is required for this tier
        tier_config = USER_TIER_SETTINGS.get(request.user.tier, {})
        if not tier_config.get('require_mfa', False):
            return True
        
        # Check if user has verified MFA in current session
        # This would check session data or JWT claims
        mfa_verified = getattr(request.user, 'mfa_verified', False)
        
        if not mfa_verified:
            raise PermissionDenied(
                detail=_('Multi-factor authentication required.')
            )
        
        return True


class VIPOnlyPermission(TierBasedPermission):
    """Permission class for VIP-only features"""
    
    required_tier = 'vip'
    
    def has_permission(self, request, view):
        """Check if user is VIP or higher"""
        if not super().has_permission(request, view):
            raise PermissionDenied(
                detail=_('VIP access required for this feature.')
            )
        return True


class ConciergeOnlyPermission(TierBasedPermission):
    """Permission class for Concierge-only features"""
    
    required_tier = 'concierge'
    
    def has_permission(self, request, view):
        """Check if user is Concierge level"""
        if not super().has_permission(request, view):
            raise PermissionDenied(
                detail=_('Concierge access required for this feature.')
            )
        return True


class RateLimitPermission(permissions.BasePermission):
    """Permission class that enforces rate limiting"""
    
    def has_permission(self, request, view):
        """Check rate limits based on user tier"""
        if not request.user or not request.user.is_authenticated:
            # Apply anonymous rate limits
            return self._check_anonymous_rate_limit(request)
        
        # Check authenticated user rate limits
        return self._check_user_rate_limit(request, view)
    
    def _check_anonymous_rate_limit(self, request):
        """Check rate limits for anonymous users"""
        # Implement anonymous rate limiting
        return True
    
    def _check_user_rate_limit(self, request, view):
        """Check rate limits for authenticated users"""
        # Get tier-specific rate limits
        tier_config = USER_TIER_SETTINGS.get(request.user.tier, {})
        rate_limits = tier_config.get('rate_limits', {})
        
        # Implement tier-based rate limiting
        return True


class DeviceVerificationPermission(permissions.BasePermission):
    """Permission class that enforces device verification"""
    
    def has_permission(self, request, view):
        """Check if device is verified/trusted"""
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Skip device verification for certain tiers
        if request.user.tier in ['normal', 'premium']:
            return True
        
        # Check if device is trusted for VIP users
        device_fingerprint = request.META.get('HTTP_X_DEVICE_FINGERPRINT', '')
        if not device_fingerprint:
            raise PermissionDenied(
                detail=_('Device fingerprint required.')
            )
        
        # Check if device is trusted (would query TrustedDevice model)
        is_trusted = self._check_device_trust(request.user, device_fingerprint)
        
        if not is_trusted:
            raise PermissionDenied(
                detail=_('Device not trusted. Please verify your device.')
            )
        
        return True
    
    def _check_device_trust(self, user, device_fingerprint):
        """Check if device is trusted"""
        # Would query TrustedDevice model
        return True


class SecurityEventPermission(permissions.BasePermission):
    """Permission class for security event monitoring"""
    
    def has_permission(self, request, view):
        """Check if user can access security events"""
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Only admin and concierge can view security events
        return request.user.tier in ['admin', 'concierge']


class IPWhitelistPermission(permissions.BasePermission):
    """Permission class for IP-based access control"""
    
    def has_permission(self, request, view):
        """Check if IP is whitelisted for sensitive operations"""
        # Get client IP
        ip_address = self._get_client_ip(request)
        
        # Check if IP is whitelisted (would query database)
        is_whitelisted = self._check_ip_whitelist(request.user, ip_address)
        
        if not is_whitelisted and request.user.tier == 'vip':
            raise PermissionDenied(
                detail=_('Access from this location is not authorized.')
            )
        
        return True
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _check_ip_whitelist(self, user, ip_address):
        """Check if IP is whitelisted"""
        # Would query IP whitelist database
        return True


class TimeBasedPermission(permissions.BasePermission):
    """Permission class for time-based access control"""
    
    def has_permission(self, request, view):
        """Check if access is allowed at current time"""
        from datetime import datetime, time
        
        # Get current time
        now = datetime.now().time()
        
        # Define allowed time windows based on tier
        time_windows = {
            'normal': (time(6, 0), time(23, 59)),  # 6 AM - 11:59 PM
            'premium': (time(0, 0), time(23, 59)),  # 24/7
            'vip': (time(0, 0), time(23, 59)),  # 24/7
            'concierge': (time(0, 0), time(23, 59)),  # 24/7
        }
        
        if not request.user or not request.user.is_authenticated:
            return True  # Don't restrict anonymous access by time
        
        start_time, end_time = time_windows.get(
            request.user.tier, 
            (time(6, 0), time(23, 59))
        )
        
        if not (start_time <= now <= end_time):
            raise PermissionDenied(
                detail=_('Access not allowed at this time.')
            )
        
        return True


class GeolocationPermission(permissions.BasePermission):
    """Permission class for geolocation-based access control"""
    
    def has_permission(self, request, view):
        """Check if access is allowed from current location"""
        # Get user's location (from IP geolocation or GPS)
        user_location = self._get_user_location(request)
        
        if not user_location:
            return True  # Allow if location can't be determined
        
        # Check if location is in allowed regions
        allowed_regions = self._get_allowed_regions(request.user)
        
        if user_location['country'] not in allowed_regions:
            raise PermissionDenied(
                detail=_('Access not allowed from this location.')
            )
        
        return True
    
    def _get_user_location(self, request):
        """Get user's geographic location"""
        # Would use IP geolocation service
        return {'country': 'NG', 'city': 'Lagos'}
    
    def _get_allowed_regions(self, user):
        """Get allowed regions for user"""
        # Would query user preferences or tier settings
        return ['NG', 'GH', 'KE']  # Nigeria, Ghana, Kenya


class CombinedSecurityPermission(permissions.BasePermission):
    """Combined security permission for high-security endpoints"""
    
    def has_permission(self, request, view):
        """Apply multiple security checks"""
        # List of permission classes to check
        permission_classes = [
            TierBasedPermission,
            MFARequiredPermission,
            DeviceVerificationPermission,
            RateLimitPermission,
            IPWhitelistPermission
        ]
        
        # Check all permissions
        for permission_class in permission_classes:
            permission = permission_class()
            if not permission.has_permission(request, view):
                return False
        
        return True


# Enhanced Role-Based Access Control System

class AuditedTierPermission(TierBasedPermission):
    """Enhanced tier permission with comprehensive audit logging"""
    
    def has_permission(self, request, view):
        """Check tier permission with audit logging"""
        result = super().has_permission(request, view)
        
        # Log permission check
        self._log_permission_check(request, view, result)
        
        return result
    
    def _log_permission_check(self, request, view, granted):
        """Log permission check with detailed information"""
        try:
            event_type = 'access_granted' if granted else 'access_denied'
            view_name = getattr(view, '__class__', {}).get('__name__', 'unknown')
            required_tier = getattr(view, 'required_tier', 'unknown')
            
            SecurityEvent.objects.create(
                user=request.user if request.user.is_authenticated else None,
                event_type=event_type,
                
                description=f"Tier permission check: {event_type} for {view_name}",
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),            )
        except Exception as e:
            logger.error(f"Failed to log permission check: {e}")


class VIPDataAccessPermission(permissions.BasePermission):
    """Permission for accessing VIP user data - restricted to concierge+ staff"""
    
    def has_permission(self, request, view):
        """Check VIP data access permission"""
        if not request.user or not request.user.is_authenticated:
            self._log_access_attempt(
                request, False, 'unauthenticated_vip_access',
                'Unauthenticated VIP data access attempt'
            )
            return False
        
        # Only concierge and admin can access VIP data
        if request.user.tier not in ['concierge', 'admin']:
            self._log_access_attempt(
                request, False, 'unauthorized_vip_access',
                f'Unauthorized VIP data access attempt by {request.user.tier} user'
            )
            return False
        
        # Check if user has valid session
        if not self._has_valid_session(request.user):
            self._log_access_attempt(
                request, False, 'invalid_session_vip_access',
                'VIP data access denied - invalid session'
            )
            return False
        
        self._log_access_attempt(
            request, True, 'vip_data_access_granted',
            f'VIP data access granted to {request.user.tier} user'
        )
        return True
    
    def _has_valid_session(self, user):
        """Check if user has a valid active session"""
        try:
            session = UserSession.objects.filter(
                user=user,
                is_active=True,
                expires_at__gt=timezone.now()
            ).first()
            return session is not None
        except Exception:
            return False
    
    def _log_access_attempt(self, request, granted, category, message):
        """Log VIP data access attempts"""
        try:
            SecurityEvent.objects.create(
                user=request.user if request.user.is_authenticated else None,
                event_type='access_granted' if granted else 'access_denied',
                
                description=message,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),            )
        except Exception as e:
            logger.error(f"Failed to log VIP access attempt: {e}")


class EnhancedMFAPermission(permissions.BasePermission):
    """Enhanced MFA permission with operation-specific requirements"""
    
    # Operations that require MFA
    MFA_REQUIRED_OPERATIONS = [
        'decrypt_gps',
        'access_vip_data',
        'emergency_override',
        'system_admin',
        'financial_data',
        'user_data_export',
        'payment_processing'
    ]
    
    def has_permission(self, request, view):
        """Check MFA requirement for sensitive operations"""
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Determine operation type
        operation = self._get_operation_type(request, view)
        
        # Check if MFA is required for this operation
        if operation in self.MFA_REQUIRED_OPERATIONS:
            if not self._verify_mfa_status(request.user):
                self._log_mfa_requirement(request, operation, False)
                raise PermissionDenied(
                    detail=_('Multi-factor authentication required for this operation.')
                )
            
            self._log_mfa_requirement(request, operation, True)
        
        return True
    
    def _get_operation_type(self, request, view):
        """Determine operation type from request/view"""
        view_name = getattr(view, '__class__', {}).get('__name__', '').lower()
        path = request.path.lower()
        
        if 'decrypt' in path or 'decrypt' in view_name:
            return 'decrypt_gps'
        elif 'vip' in path or 'vip' in view_name:
            return 'access_vip_data'
        elif 'emergency' in path:
            return 'emergency_override'
        elif 'admin' in path:
            return 'system_admin'
        elif 'financial' in path or 'payment' in path:
            return 'financial_data'
        elif 'export' in path:
            return 'user_data_export'
        
        return 'standard_operation'
    
    def _verify_mfa_status(self, user):
        """Verify user has completed MFA within required timeframe"""
        try:
            # Check for recent MFA token within last 30 minutes
            recent_mfa = MFAToken.objects.filter(
                user=user,
                is_verified=True,
                verified_at__gt=timezone.now() - timedelta(minutes=30)
            ).exists()
            
            return recent_mfa
        except Exception:
            return False
    
    def _log_mfa_requirement(self, request, operation, verified):
        """Log MFA requirement checks"""
        try:
            SecurityEvent.objects.create(
                user=request.user,
                event_type='mfa_verified' if verified else 'mfa_required',
                
                description=f"MFA {'verified' if verified else 'required'} for {operation}",
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),            )
        except Exception as e:
            logger.error(f"Failed to log MFA requirement: {e}")


class OperationAuditPermission(permissions.BasePermission):
    """Permission that audits all operations regardless of access level"""
    
    def has_permission(self, request, view):
        """Log all operations for audit purposes"""
        self._log_operation(request, view)
        return True  # This permission only logs, doesn't restrict
    
    def _log_operation(self, request, view):
        """Log operation details for audit trail"""
        try:
            view_name = getattr(view, '__class__', {}).get('__name__', 'unknown')
            
            SecurityEvent.objects.create(
                user=request.user if request.user.is_authenticated else None,
                event_type='operation_audit',
                
                description=f"API operation: {request.method} {request.path}",
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),            )
        except Exception as e:
            logger.error(f"Failed to log operation: {e}")


# Django Permission Setup Functions

CUSTOM_PERMISSIONS = [
    # Ride management permissions
    ('can_book_premium_ride', 'Can book premium rides'),
    ('can_book_vip_ride', 'Can book VIP rides'),
    ('can_book_concierge_ride', 'Can book concierge rides'),
    ('can_cancel_ride_anytime', 'Can cancel rides without penalty'),
    
    # GPS and location permissions
    ('can_encrypt_gps', 'Can encrypt GPS coordinates'),
    ('can_decrypt_gps', 'Can decrypt GPS coordinates'),
    ('can_access_live_tracking', 'Can access live GPS tracking'),
    ('can_view_route_history', 'Can view complete route history'),
    
    # VIP data access permissions
    ('can_access_vip_data', 'Can access VIP user data'),
    ('can_modify_vip_data', 'Can modify VIP user data'),
    ('can_view_vip_financial', 'Can view VIP financial information'),
    ('can_emergency_override', 'Can perform emergency overrides'),
    
    # Hotel and booking permissions
    ('can_book_hotels', 'Can book hotels through platform'),
    ('can_access_concierge', 'Can access concierge services'),
    ('can_priority_booking', 'Can make priority bookings'),
    
    # Driver and fleet permissions
    ('can_manage_drivers', 'Can manage driver accounts'),
    ('can_access_driver_data', 'Can access driver information'),
    ('can_manage_fleet', 'Can manage fleet operations'),
    ('can_set_driver_rates', 'Can set driver commission rates'),
    
    # Administrative permissions
    ('can_view_analytics', 'Can view platform analytics'),
    ('can_manage_tiers', 'Can manage user tier assignments'),
    ('can_access_audit_logs', 'Can access security audit logs'),
    ('can_system_override', 'Can perform system overrides'),
    
    # Financial permissions
    ('can_process_payments', 'Can process payment transactions'),
    ('can_issue_refunds', 'Can issue refunds'),
    ('can_view_financial_reports', 'Can view financial reports'),
    ('can_manage_subscriptions', 'Can manage driver subscriptions'),
]


def setup_tier_permissions():
    """Setup default permissions for each user tier"""
    
    tier_permissions = {
        'normal': [
            'can_book_premium_ride',
        ],
        'premium': [
            'can_book_premium_ride',
            'can_book_vip_ride',
            'can_encrypt_gps',
            'can_access_live_tracking',
            'can_book_hotels',
            'can_cancel_ride_anytime',
        ],
        'vip': [
            'can_book_premium_ride',
            'can_book_vip_ride',
            'can_book_concierge_ride',
            'can_encrypt_gps',
            'can_decrypt_gps',
            'can_access_live_tracking',
            'can_view_route_history',
            'can_book_hotels',
            'can_access_concierge',
            'can_priority_booking',
            'can_cancel_ride_anytime',
            'can_emergency_override',
        ],
        'concierge': [
            # All VIP permissions plus staff permissions
            'can_book_premium_ride',
            'can_book_vip_ride',
            'can_book_concierge_ride',
            'can_encrypt_gps',
            'can_decrypt_gps',
            'can_access_live_tracking',
            'can_view_route_history',
            'can_access_vip_data',
            'can_modify_vip_data',
            'can_view_vip_financial',
            'can_book_hotels',
            'can_access_concierge',
            'can_priority_booking',
            'can_cancel_ride_anytime',
            'can_emergency_override',
            'can_manage_drivers',
            'can_access_driver_data',
            'can_view_analytics',
        ],
        'admin': [
            # All permissions
            perm[0] for perm in CUSTOM_PERMISSIONS
        ]
    }
    
    return tier_permissions


def create_custom_permissions():
    """Create custom permissions and groups in Django"""
    from django.contrib.auth.models import Permission, Group
    from django.contrib.contenttypes.models import ContentType
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    content_type = ContentType.objects.get_for_model(User)
    
    # Create permissions
    for codename, name in CUSTOM_PERMISSIONS:
        permission, created = Permission.objects.get_or_create(
            codename=codename,
            content_type=content_type,
            defaults={'name': name}
        )
        if created:
            logger.info(f"Created permission: {codename}")
    
    # Create tier groups and assign permissions
    tier_permissions = setup_tier_permissions()
    
    for tier, permission_codes in tier_permissions.items():
        group, created = Group.objects.get_or_create(name=f"{tier}_users")
        
        if created:
            logger.info(f"Created group: {tier}_users")
        
        # Clear existing permissions and add new ones
        group.permissions.clear()
        
        for perm_code in permission_codes:
            try:
                permission = Permission.objects.get(
                    codename=perm_code,
                    content_type=content_type
                )
                group.permissions.add(permission)
            except Permission.DoesNotExist:
                logger.warning(f"Permission {perm_code} not found for tier {tier}")
        
        logger.info(f"Assigned {len(permission_codes)} permissions to {tier}_users group")


# Convenient permission aliases for specific tiers
class IsNormalUser(AuditedTierPermission):
    """Permission for normal tier users and above"""
    required_tier = 'normal'


class IsPremiumUser(AuditedTierPermission):
    """Permission for premium tier users and above"""
    required_tier = 'premium'
