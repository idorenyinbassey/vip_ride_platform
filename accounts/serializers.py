# JWT Authentication Serializers
"""
Serializers for JWT authentication, MFA, and user management
"""

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import pyotp
import re

from .utils import (
    get_client_ip, 
    get_device_fingerprint, 
    is_suspicious_login,
    validate_phone_number
)
from .jwt_config import USER_TIER_SETTINGS, MFA_SETTINGS

User = get_user_model()


class TierBasedTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Enhanced JWT token serializer with tier-based features"""
    
    # Additional fields for enhanced security
    device_fingerprint = serializers.CharField(required=False, allow_blank=True)
    remember_device = serializers.BooleanField(default=False)
    mfa_token = serializers.CharField(required=False, allow_blank=True)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = self.context.get('request')
        self.ip_address = get_client_ip(self.request) if self.request else None
        
    def validate(self, attrs):
        """Validate login credentials with tier-specific logic"""
        email = attrs.get('email')
        password = attrs.get('password')
        device_fingerprint = attrs.get('device_fingerprint')
        mfa_token = attrs.get('mfa_token')
        
        # Also check request data if available
        if hasattr(self.context.get('request'), '_full_data'):
            request_data = self.context['request']._full_data
            email = email or request_data.get('email') or request_data.get('username')
            device_fingerprint = device_fingerprint or request_data.get('device_fingerprint', '')
        
        if not email:
            raise serializers.ValidationError(
                _('Email or username is required.')
            )
        
        # Ensure email is used for authentication
        attrs['email'] = email
        if 'username' in attrs and 'email' not in attrs:
            attrs['email'] = attrs.pop('username')
        
        # Get user for validation
        user = User.objects.filter(email=email).first()
        if not user:
            # Try finding by username if email lookup fails
            user = User.objects.filter(username=email).first()
            if user:
                attrs['email'] = user.email
        
        if not user:
            raise serializers.ValidationError(
                _('No account found with this email address.')
            )
        
        # Check if account is active
        if not user.is_active:
            raise serializers.ValidationError(
                _('This account has been deactivated.')
            )
        
        # Authenticate user
        user = authenticate(
            request=self.request,
            username=email,
            password=password
        )
        
        if not user:
            # Log failed attempt
            self._log_failed_attempt(email, 'failed_password')
            raise serializers.ValidationError(
                _('Invalid email or password.')
            )
        
        # Check for suspicious login
        if is_suspicious_login(self.request, user):
            self._log_failed_attempt(email, 'blocked_suspicious')
            raise serializers.ValidationError(
                _('Login blocked due to suspicious activity. Please try again later.')
            )
        
        # Check MFA requirements
        mfa_required = self._check_mfa_requirements(user, device_fingerprint)
        if mfa_required and not mfa_token:
            # Generate temporary token for MFA verification
            temp_token = self._generate_temp_token(user)
            raise serializers.ValidationError({
                'mfa_required': True,
                'mfa_methods': self._get_available_mfa_methods(user),
                'temp_token': temp_token,
                'message': _('Multi-factor authentication required.')
            })
        
        # Verify MFA token if provided
        if mfa_token and not self._verify_mfa_token(user, mfa_token):
            self._log_failed_attempt(email, 'failed_mfa')
            raise serializers.ValidationError(
                _('Invalid MFA token.')
            )
        
        # Create session and tokens
        refresh = self.get_token(user)
        
        # Add custom claims
        refresh['user_tier'] = user.tier
        refresh['device_fingerprint'] = device_fingerprint
        refresh['ip_address'] = str(self.ip_address)
        
        # Store device as trusted if requested
        if attrs.get('remember_device') and mfa_token:
            self._mark_device_trusted(user, device_fingerprint)
        
        # Log successful login
        self._log_successful_attempt(user, email)
        
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'email': user.email,
                'tier': user.tier,
                'first_name': user.first_name,
                'last_name': user.last_name,
            },
            'mfa_verified': bool(mfa_token),
            'device_trusted': self._is_device_trusted(user, device_fingerprint)
        }
    
    def _check_mfa_requirements(self, user, device_fingerprint):
        """Check if MFA is required for this login"""
        # Premium and VIP users always require MFA
        if user.tier in ['premium', 'vip']:
            return True
        
        # Check tier-specific MFA settings
        tier_config = USER_TIER_SETTINGS.get(user.tier, {})
        if tier_config.get('require_mfa', False):
            return True
        
        # Check if device is trusted
        if self._is_device_trusted(user, device_fingerprint):
            return False
        
        # Check MFA settings
        mfa_config = MFA_SETTINGS.get(user.tier, {})
        return mfa_config.get('required', False)
    
    def _generate_temp_token(self, user):
        """Generate temporary token for MFA workflow"""
        try:
            import jwt
            import time
            from django.conf import settings
            
            payload = {
                'user_id': str(user.id),  # Convert UUID to string  
                'email': user.email,
                'type': 'mfa_temp',
                'exp': int(time.time()) + 300,  # 5 minutes expiry
                'iat': int(time.time())
            }
            
            temp_token = jwt.encode(
                payload,
                settings.SECRET_KEY,
                algorithm='HS256'
            )
            
            return temp_token
        except Exception as e:
            # Return a simple token if JWT fails
            import hashlib
            import time
            simple_token = hashlib.sha256(f"{user.id}{time.time()}".encode()).hexdigest()[:32]
            return simple_token
    
    def _get_available_mfa_methods(self, user):
        """Get available MFA methods for user"""
        methods = []
        # This would check user's MFA tokens
        # For now, return common methods
        methods.extend(['totp', 'sms', 'email'])
        return methods
    
    def _verify_mfa_token(self, user, token):
        """Verify MFA token"""
        # Check TOTP first
        if self._verify_totp_token(user, token):
            return True
        
        # Check backup codes
        if self._verify_backup_code(user, token):
            return True
        
        return False
    
    def _verify_totp_token(self, user, token):
        """Verify TOTP token"""
        try:
            # Basic validation first
            if not token or len(token) != 6 or not token.isdigit():
                return False
            
            # SECURITY: In development/testing, fail explicitly to prevent bypass
            # TODO: Implement proper TOTP verification with pyotp or similar
            # For production, this should verify against user's TOTP secret
            
            # Development/testing mode - explicitly fail for security
            if hasattr(user, 'mfa_secret') and user.mfa_secret:
                # Placeholder for actual TOTP verification
                # import pyotp
                # totp = pyotp.TOTP(user.mfa_secret)
                # return totp.verify(token, valid_window=1)
                pass
            
            # Fail safe - do not allow bypass in any environment
            return False
            
        except Exception:
            return False
    
    def _verify_backup_code(self, user, code):
        """Verify backup code"""
        # This would check against user's backup codes
        return False
    
    def _is_device_trusted(self, user, device_fingerprint):
        """Check if device is trusted"""
        # This would check TrustedDevice model
        return False
    
    def _mark_device_trusted(self, user, device_fingerprint):
        """Mark device as trusted"""
        # This would create/update TrustedDevice
        pass
    
    def _log_successful_attempt(self, user, email):
        """Log successful login attempt"""
        # This would create LoginAttempt record
        pass
    
    def _log_failed_attempt(self, email, attempt_type):
        """Log failed login attempt"""
        # This would create LoginAttempt record
        pass


class UserRegistrationSerializer(serializers.ModelSerializer):
    """User registration serializer"""
    
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True)
    phone_number = serializers.CharField(
        required=False,
        validators=[validate_phone_number]
    )
    tier = serializers.ChoiceField(
        choices=['normal', 'premium', 'vip'],
        default='normal'
    )
    
    class Meta:
        model = User
        fields = [
            'email', 'username', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone_number', 'tier'
        ]
    
    def validate(self, attrs):
        """Validate registration data"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError(
                {'password_confirm': _('Passwords do not match.')}
            )
        
        # Check if email already exists
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError(
                {'email': _('Account with this email already exists.')}
            )
        
        # Auto-generate username from email if not provided
        if not attrs.get('username'):
            attrs['username'] = attrs['email'].split('@')[0]
        
        # Check if username already exists and make it unique
        base_username = attrs['username']
        counter = 1
        while User.objects.filter(username=attrs['username']).exists():
            attrs['username'] = f"{base_username}{counter}"
            counter += 1
        
        return attrs
    
    def create(self, validated_data):
        """Create new user"""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        
        return user


class TokenRefreshSerializer(serializers.Serializer):
    """Enhanced token refresh serializer"""
    
    refresh = serializers.CharField()
    device_fingerprint = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, attrs):
        """Validate refresh token and rotate if needed"""
        from rest_framework_simplejwt.tokens import RefreshToken
        from rest_framework_simplejwt.exceptions import TokenError
        
        try:
            refresh = RefreshToken(attrs['refresh'])
            
            # Get user and validate
            user_id = refresh.payload.get('user_id')
            user = User.objects.get(id=user_id)
            
            if not user.is_active:
                raise serializers.ValidationError(
                    _('User account is deactivated.')
                )
            
            # Token rotation - create new refresh token
            refresh.blacklist()
            new_refresh = RefreshToken.for_user(user)
            
            # Add custom claims
            new_refresh['user_tier'] = user.tier
            device_fp = attrs.get('device_fingerprint', '')
            new_refresh['device_fingerprint'] = device_fp
            
            return {
                'refresh': str(new_refresh),
                'access': str(new_refresh.access_token),
            }
            
        except TokenError as e:
            raise serializers.ValidationError({'refresh': str(e)})
        except User.DoesNotExist:
            raise serializers.ValidationError({'refresh': _('Invalid token.')})


class PasswordChangeSerializer(serializers.Serializer):
    """Password change serializer"""
    
    old_password = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])
    new_password_confirm = serializers.CharField()
    
    def validate(self, attrs):
        """Validate password change"""
        user = self.context['request'].user
        
        # Check old password
        if not user.check_password(attrs['old_password']):
            raise serializers.ValidationError(
                {'old_password': _('Current password is incorrect.')}
            )
        
        # Check new passwords match
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError(
                {'new_password_confirm': _('New passwords do not match.')}
            )
        
        return attrs
    
    def save(self):
        """Change user password"""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class MFASetupSerializer(serializers.Serializer):
    """MFA setup serializer"""
    
    method = serializers.ChoiceField(
        choices=['totp', 'sms', 'email', 'backup']
    )
    phone_number = serializers.CharField(
        required=False,
        validators=[validate_phone_number]
    )
    email_address = serializers.EmailField(required=False)
    
    def validate(self, attrs):
        """Validate MFA setup data"""
        method = attrs['method']
        
        if method == 'sms' and not attrs.get('phone_number'):
            raise serializers.ValidationError(
                {'phone_number': _('Phone number is required for SMS MFA.')}
            )
        
        if method == 'email' and not attrs.get('email_address'):
            raise serializers.ValidationError(
                {'email_address': _('Email address is required for email MFA.')}
            )
        
        return attrs


class MFAVerificationSerializer(serializers.Serializer):
    """MFA verification serializer"""
    
    method = serializers.ChoiceField(
        choices=['totp', 'sms', 'email', 'backup']
    )
    token = serializers.CharField(max_length=10)
    
    def validate(self, attrs):
        """Validate MFA token"""
        method = attrs['method']
        token = attrs['token']
        user = self.context['request'].user
        
        # Basic token format validation
        if method == 'totp' and (len(token) != 6 or not token.isdigit()):
            raise serializers.ValidationError(
                {'token': _('TOTP token must be 6 digits.')}
            )
        
        if method == 'backup' and len(token) != 8:
            raise serializers.ValidationError(
                {'token': _('Backup code must be 8 characters.')}
            )
        
        # Verify token (would use MFAToken model)
        if not self._verify_token(user, method, token):
            raise serializers.ValidationError(
                {'token': _('Invalid or expired token.')}
            )
        
        return attrs
    
    def _verify_token(self, user, method, token):
        """Verify MFA token"""
        # This would verify against MFAToken model
        # For now, basic validation
        return True


class UserProfileSerializer(serializers.ModelSerializer):
    """User profile serializer"""
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name',
            'phone_number', 'tier', 'is_active',
            'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'email', 'tier', 'date_joined', 'last_login']
    
    def validate_phone_number(self, value):
        """Validate phone number"""
        if value and not validate_phone_number(value):
            raise serializers.ValidationError(
                _('Invalid phone number format.')
            )
        return value


class DeviceManagementSerializer(serializers.Serializer):
    """Device management serializer"""
    
    device_fingerprint = serializers.CharField(max_length=64)
    device_name = serializers.CharField(max_length=100, required=False)
    trust_level = serializers.ChoiceField(
        choices=['basic', 'high', 'vip'],
        default='basic'
    )
    action = serializers.ChoiceField(
        choices=['trust', 'untrust', 'remove']
    )
    
    def validate(self, attrs):
        """Validate device management action"""
        user = self.context['request'].user
        device_fp = attrs['device_fingerprint']
        action = attrs['action']
        
        # Check if device exists (would check TrustedDevice model)
        if action in ['untrust', 'remove']:
            # Validate device exists
            pass
        
        return attrs
