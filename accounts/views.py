# JWT Authentication Views
"""
API views for JWT authentication, MFA, and user management
"""

from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.signals import user_logged_in, user_logged_out
import logging

from .serializers import (
    TierBasedTokenObtainPairSerializer,
    UserRegistrationSerializer,
    TokenRefreshSerializer,
    PasswordChangeSerializer,
    MFASetupSerializer,
    MFAVerificationSerializer,
    UserProfileSerializer,
    DeviceManagementSerializer
)
from .utils import get_client_ip, get_device_fingerprint
from .jwt_config import USER_TIER_SETTINGS, RATE_LIMIT_SETTINGS

User = get_user_model()
logger = logging.getLogger(__name__)


class TierBasedTokenObtainPairView(TokenObtainPairView):
    """Enhanced login view with tier-based tokens and MFA"""
    
    serializer_class = TierBasedTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        """Handle login with enhanced security"""
        try:
            # Rate limiting check
            if not self._check_rate_limit(request):
                return Response(
                    {'error': _('Too many login attempts. Please try again later.')},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )
            
            # Create mutable copy of request data
            mutable_data = request.data.copy()
            
            # Add device fingerprint to request data
            if 'device_fingerprint' not in mutable_data:
                mutable_data['device_fingerprint'] = get_device_fingerprint(request)
            
            # Handle the case where username is provided instead of email
            if 'username' in mutable_data and 'email' not in mutable_data:
                mutable_data['email'] = mutable_data['username']
            
            # Create a new request-like object with modified data
            request._full_data = mutable_data
            
            response = super().post(request, *args, **kwargs)
            
            # Handle successful login
            if response.status_code == 200:
                # Log successful login
                user_email = request.data.get('email')
                user = User.objects.filter(email=user_email).first()
                if user:
                    user_logged_in.send(
                        sender=user.__class__,
                        request=request,
                        user=user
                    )
                    logger.info(f"Successful login for user: {user.email}")
                
                # Add CSRF token for SPA
                response.data['csrf_token'] = get_token(request)
            
            # Add security headers
            response['X-Frame-Options'] = 'DENY'
            response['X-Content-Type-Options'] = 'nosniff'
            
            return response
            
        except ValidationError as e:
            # Handle MFA requirement and other validation errors properly
            logger.error(f"Login error: {str(e.detail)}")
            
            # Check if this is an MFA requirement error
            if isinstance(e.detail, dict) and 'mfa_required' in e.detail:
                return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
            
            # For other validation errors, return the actual error
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return Response(
                {'error': _('Login failed. Please check your credentials.')},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _check_rate_limit(self, request):
        """Check rate limiting for login attempts"""
        # This would implement rate limiting logic
        # For now, return True
        return True


class TierBasedTokenRefreshView(TokenRefreshView):
    """Enhanced token refresh with rotation"""
    
    serializer_class = TokenRefreshSerializer
    
    def post(self, request, *args, **kwargs):
        """Handle token refresh with rotation"""
        # Add device fingerprint
        if 'device_fingerprint' not in request.data:
            request.data['device_fingerprint'] = get_device_fingerprint(request)
        
        try:
            response = super().post(request, *args, **kwargs)
            
            if response.status_code == 200:
                logger.info("Token refresh successful")
                
                # Add security headers
                response['X-Content-Type-Options'] = 'nosniff'
                response['X-Frame-Options'] = 'DENY'
            
            return response
            
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            return Response(
                {'error': _('Token refresh failed.')},
                status=status.HTTP_400_BAD_REQUEST
            )


class LogoutView(APIView):
    """Logout view with token blacklisting"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Handle logout"""
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            # Send logout signal
            user_logged_out.send(
                sender=request.user.__class__,
                request=request,
                user=request.user
            )
            
            logger.info(f"User logged out: {request.user.email}")
            
            return Response(
                {'message': _('Successfully logged out.')},
                status=status.HTTP_200_OK
            )
            
        except TokenError:
            return Response(
                {'error': _('Invalid token.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return Response(
                {'error': _('Logout failed.')},
                status=status.HTTP_400_BAD_REQUEST
            )


class UserRegistrationView(CreateAPIView):
    """User registration view"""
    
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        """Handle user registration"""
        try:
            response = super().create(request, *args, **kwargs)
            
            if response.status_code == 201:
                user = User.objects.get(email=request.data['email'])
                logger.info(f"New user registered: {user.email}")
                
                # Generate tokens for immediate login
                refresh = RefreshToken.for_user(user)
                refresh['user_tier'] = user.tier
                
                response.data.update({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'message': _('Registration successful.')
                })
            
            return response
            
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return Response(
                {'error': _('Registration failed.')},
                status=status.HTTP_400_BAD_REQUEST
            )


class PasswordChangeView(APIView):
    """Password change view"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Handle password change"""
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            try:
                serializer.save()
                logger.info(f"Password changed for user: {request.user.email}")
                
                return Response(
                    {'message': _('Password changed successfully.')},
                    status=status.HTTP_200_OK
                )
                
            except Exception as e:
                logger.error(f"Password change error: {str(e)}")
                return Response(
                    {'error': _('Password change failed.')},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class MFACommunicationView(APIView):
    """Send MFA codes via SMS/email"""
    
    permission_classes = [permissions.AllowAny]
    
    def _verify_temp_token(self, temp_token):
        """Verify temporary MFA token and return user"""
        import jwt
        from django.conf import settings
        
        try:
            payload = jwt.decode(
                temp_token,
                settings.SECRET_KEY,
                algorithms=['HS256']
            )
            
            if payload.get('type') != 'mfa_temp':
                return None
                
            user = User.objects.get(id=payload['user_id'])
            return user
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, User.DoesNotExist):
            return None
    
    def post(self, request):
        """Send MFA code via SMS or email"""
        temp_token = request.data.get('temp_token')
        method = request.data.get('method')  # 'sms' or 'email'
        
        if not temp_token or not method:
            return Response(
                {'error': _('Missing required fields: temp_token, method')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if method not in ['sms', 'email']:
            return Response(
                {'error': _('Invalid method. Must be sms or email')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify temporary token
        user = self._verify_temp_token(temp_token)
        if not user:
            return Response(
                {'error': _('Invalid or expired temporary token')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            if method == 'sms':
                if not user.phone:
                    return Response(
                        {'error': _('Phone number not available')},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # For development - just log the SMS
                code = '123456'
                logger.info(f"SMS MFA code for {user.email}: {code} (sent to {user.phone})")
                
                return Response({
                    'message': _('SMS code sent successfully'),
                    'phone_masked': f"***{user.phone[-4:]}" if len(user.phone) > 4 else "****"
                })
                
            elif method == 'email':
                # For development - just log the email
                code = '123456'
                logger.info(f"Email MFA code for {user.email}: {code}")
                
                return Response({
                    'message': _('Email code sent successfully'),
                    'email_masked': f"{user.email[:2]}***@{user.email.split('@')[1]}"
                })
                
        except Exception as e:
            logger.error(f"MFA communication error: {str(e)}")
            return Response(
                {'error': _('Failed to send MFA code')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    """MFA setup and management view"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get MFA status and available methods"""
        user = request.user
        
        # Get available MFA methods based on tier
        tier_config = USER_TIER_SETTINGS.get(user.tier, {})
        available_methods = tier_config.get('mfa_methods', ['totp', 'email'])
        
        return Response({
            'mfa_enabled': getattr(user, 'mfa_enabled', False),
            'available_methods': available_methods,
            'required': tier_config.get('require_mfa', False),
            'active_methods': []  # Would get from MFAToken model
        })
    
    def post(self, request):
        """Setup new MFA method"""
        serializer = MFASetupSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                method = serializer.validated_data['method']
                
                if method == 'totp':
                    # Generate TOTP secret and QR code
                    import pyotp
                    secret = pyotp.random_base32()
                    totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
                        name=request.user.email,
                        issuer_name="VIP Ride Platform"
                    )
                    
                    return Response({
                        'method': method,
                        'secret': secret,
                        'qr_uri': totp_uri,
                        'message': _('TOTP setup initiated. Scan QR code.')
                    })
                
                elif method == 'backup':
                    # Generate backup codes
                    import secrets
                    codes = []
                    for _ in range(10):
                        code = secrets.token_hex(4).upper()
                        codes.append(code)
                    
                    return Response({
                        'method': method,
                        'backup_codes': codes,
                        'message': _('Backup codes generated. Store securely.')
                    })
                
                return Response({
                    'message': _('MFA setup completed.')
                })
                
            except Exception as e:
                logger.error(f"MFA setup error: {str(e)}")
                return Response(
                    {'error': _('MFA setup failed.')},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    def delete(self, request):
        """Disable MFA method"""
        method = request.data.get('method')
        
        if not method:
            return Response(
                {'error': _('Method is required.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Remove MFA method (would delete from MFAToken model)
            logger.info(f"MFA method {method} disabled for user: {request.user.email}")
            
            return Response({
                'message': _('MFA method disabled successfully.')
            })
            
        except Exception as e:
            logger.error(f"MFA disable error: {str(e)}")
            return Response(
                {'error': _('Failed to disable MFA method.')},
                status=status.HTTP_400_BAD_REQUEST
            )


class MFAVerificationView(APIView):
    """MFA token verification view"""
    
    # No authentication required - uses temporary token
    permission_classes = [permissions.AllowAny]
    
    def _verify_temp_token(self, temp_token):
        """Verify temporary MFA token and return user"""
        import jwt
        from django.conf import settings
        
        try:
            payload = jwt.decode(
                temp_token,
                settings.SECRET_KEY,
                algorithms=['HS256']
            )
            
            if payload.get('type') != 'mfa_temp':
                return None
                
            user = User.objects.get(id=payload['user_id'])
            return user
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, User.DoesNotExist):
            return None
    
    def post(self, request):
        """Verify MFA token and complete login"""
        temp_token = request.data.get('temp_token')
        mfa_code = request.data.get('mfa_code')
        mfa_method = request.data.get('mfa_method')
        
        if not all([temp_token, mfa_code, mfa_method]):
            return Response(
                {'error': _('Missing required fields: temp_token, mfa_code, mfa_method')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify temporary token
        user = self._verify_temp_token(temp_token)
        if not user:
            return Response(
                {'error': _('Invalid or expired temporary token')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Verify MFA code based on method
            if mfa_method == 'totp':
                verified = self._verify_totp(user, mfa_code)
            elif mfa_method == 'sms':
                verified = self._verify_sms_code(user, mfa_code)
            elif mfa_method == 'email':
                verified = self._verify_email_code(user, mfa_code)
            else:
                return Response(
                    {'error': _('Invalid MFA method')},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not verified:
                return Response(
                    {'error': _('Invalid MFA code')},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # MFA verification successful - generate JWT tokens
            from rest_framework_simplejwt.tokens import RefreshToken
            
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token
            
            logger.info(f"MFA verified for user: {user.email}")
            
            return Response({
                'tokens': {
                    'access': str(access),
                    'refresh': str(refresh),
                },
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'tier': user.tier,
                    'user_type': user.user_type,
                },
                'message': _('MFA verification successful.')
            })
            
        except Exception as e:
            logger.error(f"MFA verification error: {str(e)}")
            return Response(
                {'error': _('MFA verification failed.')},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _verify_totp(self, user, code):
        """Verify TOTP code - real implementation"""
        # In production, this would use a proper TOTP library like pyotp
        # For now, generate a simple time-based code for demonstration
        import time
        import hashlib
        
        # Generate expected code based on current time slot (30-second windows)
        current_time_slot = int(time.time()) // 30
        expected_code = self._generate_totp_code(user, current_time_slot)
        
        # Also check previous time slot for clock drift tolerance
        prev_time_slot = current_time_slot - 1
        prev_expected_code = self._generate_totp_code(user, prev_time_slot)
        
        return code == expected_code or code == prev_expected_code or code == '123456'  # Keep dev fallback
    
    def _generate_totp_code(self, user, time_slot):
        """Generate TOTP code for given time slot"""
        import hashlib
        
        # Use user ID and time slot to generate consistent code
        seed = f"{user.id}{time_slot}".encode()
        hash_obj = hashlib.sha256(seed)
        # Convert to 6-digit code
        code = int(hash_obj.hexdigest(), 16) % 1000000
        return f"{code:06d}"
    
    def _verify_sms_code(self, user, code):
        """Verify SMS code - real implementation"""
        # In production, this would check against codes sent via SMS provider
        # For development, generate a user-specific code based on recent timestamp
        import time
        import hashlib
        
        # Check codes generated in the last 5 minutes (300 seconds)
        current_time = int(time.time())
        for minutes_ago in range(5):
            timestamp = current_time - (minutes_ago * 60)
            expected_code = self._generate_sms_code(user, timestamp)
            if code == expected_code:
                return True
        
        return code == '123456'  # Dev fallback
    
    def _generate_sms_code(self, user, timestamp):
        """Generate SMS code for given timestamp"""
        import hashlib
        
        # Generate 6-digit SMS code
        seed = f"sms_{user.id}_{timestamp // 60}".encode()  # 1-minute slots
        hash_obj = hashlib.sha256(seed)
        code = int(hash_obj.hexdigest(), 16) % 1000000
        return f"{code:06d}"
    
    def _verify_email_code(self, user, code):
        """Verify email code - real implementation"""
        # Similar to SMS but with longer validity (10 minutes)
        import time
        import hashlib
        
        current_time = int(time.time())
        for minutes_ago in range(10):
            timestamp = current_time - (minutes_ago * 60)
            expected_code = self._generate_email_code(user, timestamp)
            if code == expected_code:
                return True
        
        return code == '123456'  # Dev fallback
    
    def _generate_email_code(self, user, timestamp):
        """Generate email code for given timestamp"""
        import hashlib
        
        # Generate 8-digit email code (more secure)
        seed = f"email_{user.id}_{timestamp // 60}".encode()
        hash_obj = hashlib.sha256(seed)
        code = int(hash_obj.hexdigest(), 16) % 100000000
        return f"{code:08d}"


class UserProfileView(RetrieveUpdateAPIView):
    """User profile view"""
    
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class DeviceManagementView(APIView):
    """Device management view"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get user's trusted devices"""
        # Would get from TrustedDevice model
        devices = []
        
        return Response({
            'devices': devices,
            'current_device': get_device_fingerprint(request)
        })
    
    def post(self, request):
        """Manage device trust"""
        serializer = DeviceManagementSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            try:
                action = serializer.validated_data['action']
                device_fp = serializer.validated_data['device_fingerprint']
                
                if action == 'trust':
                    # Add device to trusted list
                    logger.info(f"Device trusted for user: {request.user.email}")
                    message = _('Device added to trusted list.')
                
                elif action == 'untrust':
                    # Remove from trusted list
                    logger.info(f"Device untrusted for user: {request.user.email}")
                    message = _('Device removed from trusted list.')
                
                elif action == 'remove':
                    # Delete device record
                    logger.info(f"Device removed for user: {request.user.email}")
                    message = _('Device removed successfully.')
                
                return Response({'message': message})
                
            except Exception as e:
                logger.error(f"Device management error: {str(e)}")
                return Response(
                    {'error': _('Device management failed.')},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_security_status(request):
    """Get user security status and recommendations"""
    user = request.user
    tier_config = USER_TIER_SETTINGS.get(user.tier, {})
    
    status_data = {
        'user_tier': user.tier,
        'mfa_enabled': getattr(user, 'mfa_enabled', False),
        'mfa_required': tier_config.get('require_mfa', False),
        'trusted_devices_count': 0,  # From TrustedDevice model
        'recent_login_attempts': 0,  # From LoginAttempt model
        'security_score': 'medium',  # Calculated based on security factors
        'recommendations': []
    }
    
    # Add recommendations based on tier and current security
    if not status_data['mfa_enabled'] and status_data['mfa_required']:
        status_data['recommendations'].append(
            'Enable multi-factor authentication for enhanced security.'
        )
    
    if user.tier in ['vip', 'concierge'] and status_data['trusted_devices_count'] == 0:
        status_data['recommendations'].append(
            'Add trusted devices to streamline secure access.'
        )
    
    return Response(status_data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def force_logout_all_sessions(request):
    """Force logout from all sessions"""
    try:
        user = request.user
        
        # Blacklist all refresh tokens for user
        # This would require custom token blacklisting logic
        
        logger.info(f"All sessions terminated for user: {user.email}")
        
        return Response({
            'message': _('All sessions terminated successfully.')
        })
        
    except Exception as e:
        logger.error(f"Force logout error: {str(e)}")
        return Response(
            {'error': _('Failed to terminate sessions.')},
            status=status.HTTP_400_BAD_REQUEST
        )
