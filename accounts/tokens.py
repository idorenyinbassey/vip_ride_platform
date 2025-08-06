# Custom JWT Token Classes with Tier-based Features
"""
Custom JWT tokens with enhanced security features for VIP ride-hailing platform
Supports tier-based token lifetimes, MFA integration, and advanced security
"""

import uuid
from datetime import timedelta
from typing import Dict

from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone

from .jwt_config import USER_TIER_SETTINGS, MFA_SETTINGS
from .models import UserSession, MFAToken

User = get_user_model()


class TierBasedAccessToken(AccessToken):
    """Custom access token with tier-based lifetime and enhanced security"""
    
    def __init__(self, token=None, verify=True):
        super().__init__(token, verify)
        
        if token is None:
            # Set tier-based lifetime during token creation
            user_id = self.get('user_id')
            if user_id:
                try:
                    user = User.objects.get(id=user_id)
                    tier_config = USER_TIER_SETTINGS.get(
                        user.tier, 
                        USER_TIER_SETTINGS['normal']
                    )
                    self.set_exp(
                        from_time=self.current_time,
                        lifetime=tier_config['access_token_lifetime']
                    )
                except User.DoesNotExist:
                    pass

    @classmethod
    def for_user(cls, user, **kwargs):
        """Create access token for specific user with tier-based settings"""
        token = cls()
        token[cls.token_type_claim] = cls.token_type
        token[cls.user_id_claim] = getattr(user, cls.user_id_field)
        
        # Add custom claims
        token['user_tier'] = user.tier
        token['user_type'] = user.user_type
        token['session_id'] = str(uuid.uuid4())
        token['device_id'] = kwargs.get('device_id', '')
        token['ip_address'] = kwargs.get('ip_address', '')
        token['mfa_verified'] = kwargs.get('mfa_verified', False)
        
        # Add VIP-specific claims
        if user.tier == 'vip':
            token['vip_priority'] = True
            token['encrypted_session'] = True
            token['location_tracking'] = True
        
        # Set tier-based expiration
        tier_config = USER_TIER_SETTINGS.get(user.tier, USER_TIER_SETTINGS['normal'])
        token.set_exp(lifetime=tier_config['access_token_lifetime'])
        
        return token

    def verify(self, verify_signature=True):
        """Enhanced verification with security checks"""
        super().verify(verify_signature)
        
        # Check if token is blacklisted
        token_id = self.get('jti')
        if cache.get(f'blacklisted_token:{token_id}'):
            raise TokenError('Token is blacklisted')
        
        # Verify MFA for VIP users if required
        user_tier = self.get('user_tier', 'normal')
        mfa_verified = self.get('mfa_verified', False)
        
        if (user_tier in ['vip', 'concierge'] and 
            MFA_SETTINGS['providers']['totp']['enabled'] and 
            not mfa_verified):
            raise TokenError('MFA verification required for VIP users')
        
        # Check concurrent session limits
        user_id = self.get('user_id')
        session_id = self.get('session_id')
        if user_id and session_id:
            self._check_session_limits(user_id, session_id, user_tier)

    def _check_session_limits(self, user_id: str, session_id: str, user_tier: str):
        """Check concurrent session limits based on user tier"""
        from .jwt_config import SECURITY_SETTINGS
        
        max_sessions = SECURITY_SETTINGS['max_concurrent_sessions'].get(
            user_tier, 3
        )
        
        # Count active sessions for user
        active_sessions = UserSession.objects.filter(
            user_id=user_id,
            is_active=True,
            expires_at__gt=timezone.now()
        ).count()
        
        if active_sessions > max_sessions:
            # Deactivate oldest sessions
            oldest_sessions = UserSession.objects.filter(
                user_id=user_id,
                is_active=True
            ).order_by('created_at')[:-max_sessions]
            
            for session in oldest_sessions:
                session.is_active = False
                session.save()
                # Blacklist associated tokens
                cache.set(
                    f'blacklisted_session:{session.session_id}',
                    True,
                    timeout=86400  # 24 hours
                )


class TierBasedRefreshToken(RefreshToken):
    """Custom refresh token with rotation and tier-based features"""
    
    access_token_class = TierBasedAccessToken
    
    def __init__(self, token=None, verify=True):
        super().__init__(token, verify)
        
        if token is None:
            # Set tier-based lifetime during token creation
            user_id = self.get('user_id')
            if user_id:
                try:
                    user = User.objects.get(id=user_id)
                    tier_config = USER_TIER_SETTINGS.get(
                        user.tier, 
                        USER_TIER_SETTINGS['normal']
                    )
                    self.set_exp(
                        from_time=self.current_time,
                        lifetime=tier_config['refresh_token_lifetime']
                    )
                except User.DoesNotExist:
                    pass

    @classmethod
    def for_user(cls, user, **kwargs):
        """Create refresh token for specific user"""
        token = cls()
        token[cls.token_type_claim] = cls.token_type
        token[cls.user_id_claim] = getattr(user, cls.user_id_field)
        
        # Add custom claims
        token['user_tier'] = user.tier
        token['session_id'] = str(uuid.uuid4())
        token['device_fingerprint'] = kwargs.get('device_fingerprint', '')
        token['created_ip'] = kwargs.get('ip_address', '')
        
        # Set tier-based expiration
        tier_config = USER_TIER_SETTINGS.get(user.tier, USER_TIER_SETTINGS['normal'])
        token.set_exp(lifetime=tier_config['refresh_token_lifetime'])
        
        # Create user session record
        UserSession.objects.create(
            user=user,
            session_id=token['session_id'],
            device_fingerprint=token['device_fingerprint'],
            ip_address=token['created_ip'],
            user_agent=kwargs.get('user_agent', ''),
            expires_at=timezone.now() + tier_config['refresh_token_lifetime'],
            is_active=True
        )
        
        return token

    def rotate(self, **kwargs):
        """Rotate refresh token with enhanced security"""
        # Blacklist current token
        self.blacklist()
        
        # Create new token with same user
        user_id = self.get('user_id')
        user = User.objects.get(id=user_id)
        
        new_token = self.__class__.for_user(user, **kwargs)
        
        # Transfer session context
        old_session_id = self.get('session_id')
        new_session_id = new_token.get('session_id')
        
        # Update session record
        try:
            session = UserSession.objects.get(session_id=old_session_id)
            session.session_id = new_session_id
            session.updated_at = timezone.now()
            session.save()
        except UserSession.DoesNotExist:
            pass
        
        return new_token

    def blacklist(self):
        """Blacklist token and associated session"""
        super().blacklist()
        
        # Blacklist session
        session_id = self.get('session_id')
        if session_id:
            UserSession.objects.filter(
                session_id=session_id
            ).update(is_active=False)
            
            cache.set(
                f'blacklisted_session:{session_id}',
                True,
                timeout=86400  # 24 hours
            )


class VIPSecureToken(TierBasedAccessToken):
    """Enhanced secure token for VIP users with additional security layers"""
    
    def __init__(self, token=None, verify=True):
        super().__init__(token, verify)
        
        if token is None:
            # Add VIP-specific security claims
            self['security_level'] = 'high'
            self['biometric_required'] = True
            self['location_bound'] = True

    @classmethod
    def for_user(cls, user, **kwargs):
        """Create VIP secure token with enhanced security"""
        if user.tier not in ['vip', 'concierge']:
            raise TokenError('VIP secure tokens only for VIP/Concierge users')
        
        token = super().for_user(user, **kwargs)
        
        # Add VIP security features
        token['security_level'] = 'high'
        token['emergency_contact_id'] = kwargs.get('emergency_contact_id')
        token['concierge_id'] = kwargs.get('concierge_id')
        token['panic_mode_enabled'] = True
        
        # Location binding for enhanced security
        if kwargs.get('location'):
            token['bound_location'] = kwargs['location']
            token['location_radius_km'] = 50  # Allow 50km radius
        
        return token

    def verify(self, verify_signature=True):
        """Enhanced verification for VIP tokens"""
        super().verify(verify_signature)
        
        # Additional VIP security checks
        user_id = self.get('user_id')
        session_id = self.get('session_id')
        
        # Check for panic mode or emergency status
        if self._check_emergency_status(user_id):
            # Allow emergency access with reduced verification
            return
        
        # Location verification for VIP users
        current_location = self.get('current_location')
        bound_location = self.get('bound_location')
        
        if bound_location and current_location:
            if not self._verify_location_bounds(bound_location, current_location):
                raise TokenError('Location verification failed')

    def _check_emergency_status(self, user_id: str) -> bool:
        """Check if user is in emergency mode"""
        from rides.models import Ride
        
        # Check for active emergency rides
        emergency_rides = Ride.objects.filter(
            customer_id=user_id,
            is_sos_triggered=True,
            status__in=['in_progress', 'emergency']
        ).exists()
        
        return emergency_rides

    def _verify_location_bounds(self, bound_location: Dict, current_location: Dict) -> bool:
        """Verify current location is within allowed bounds"""
        # Simplified distance calculation (in production, use proper geolocation)
        bound_lat = float(bound_location.get('lat', 0))
        bound_lng = float(bound_location.get('lng', 0))
        current_lat = float(current_location.get('lat', 0))
        current_lng = float(current_location.get('lng', 0))
        
        # Simple distance check (for production, use haversine formula)
        lat_diff = abs(bound_lat - current_lat)
        lng_diff = abs(bound_lng - current_lng)
        
        # Rough approximation: 1 degree ≈ 111km
        distance_km = ((lat_diff ** 2 + lng_diff ** 2) ** 0.5) * 111
        
        max_radius = self.get('location_radius_km', 50)
        return distance_km <= max_radius


class MFAVerificationToken:
    """Token for MFA verification process"""
    
    def __init__(self, user, mfa_method: str, **kwargs):
        self.user = user
        self.mfa_method = mfa_method
        self.token_id = str(uuid.uuid4())
        self.created_at = timezone.now()
        self.expires_at = self.created_at + timedelta(minutes=10)
        self.verified = False
        
        # Store in cache for temporary verification
        cache_key = f'mfa_verification:{self.token_id}'
        cache.set(cache_key, {
            'user_id': str(user.id),
            'mfa_method': mfa_method,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat(),
            'verified': False,
            **kwargs
        }, timeout=600)  # 10 minutes

    def verify_code(self, code: str) -> bool:
        """Verify MFA code"""
        cache_key = f'mfa_verification:{self.token_id}'
        token_data = cache.get(cache_key)
        
        if not token_data or token_data['verified']:
            return False
        
        # Verify based on MFA method
        if self.mfa_method == 'sms':
            return self._verify_sms_code(code, token_data)
        elif self.mfa_method == 'email':
            return self._verify_email_code(code, token_data)
        elif self.mfa_method == 'totp':
            return self._verify_totp_code(code)
        
        return False

    def _verify_sms_code(self, code: str, token_data: Dict) -> bool:
        """Verify SMS code"""
        stored_code = token_data.get('sms_code')
        if stored_code and stored_code == code:
            self._mark_verified()
            return True
        return False

    def _verify_email_code(self, code: str, token_data: Dict) -> bool:
        """Verify email code"""
        stored_code = token_data.get('email_code')
        if stored_code and stored_code == code:
            self._mark_verified()
            return True
        return False

    def _verify_totp_code(self, code: str) -> bool:
        """Verify TOTP code"""
        try:
            mfa_token = MFAToken.objects.get(
                user=self.user,
                token_type='totp',
                is_active=True
            )
            if mfa_token.verify_totp(code):
                self._mark_verified()
                return True
        except MFAToken.DoesNotExist:
            pass
        return False

    def _mark_verified(self):
        """Mark token as verified"""
        cache_key = f'mfa_verification:{self.token_id}'
        token_data = cache.get(cache_key)
        if token_data:
            token_data['verified'] = True
            cache.set(cache_key, token_data, timeout=600)
            self.verified = True

    def is_valid(self) -> bool:
        """Check if token is still valid"""
        return timezone.now() < self.expires_at and not self.verified

    def get_token_id(self) -> str:
        """Get token ID for client reference"""
        return self.token_id
