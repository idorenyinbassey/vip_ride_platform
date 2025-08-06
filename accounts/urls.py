# JWT Authentication URL Configuration
"""
URL patterns for JWT authentication endpoints
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    TierBasedTokenObtainPairView,
    TierBasedTokenRefreshView,
    LogoutView,
    UserRegistrationView,
    PasswordChangeView,
    MFASetupView,
    MFAVerificationView,
    UserProfileView,
    DeviceManagementView,
    user_security_status,
    force_logout_all_sessions
)

app_name = 'accounts'

urlpatterns = [
    # Authentication endpoints
    path('login/', TierBasedTokenObtainPairView.as_view(), name='login'),
    path('refresh/', TierBasedTokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    
    # Password management
    path('password/change/', PasswordChangeView.as_view(), name='password_change'),
    
    # Multi-factor authentication
    path('mfa/setup/', MFASetupView.as_view(), name='mfa_setup'),
    path('mfa/verify/', MFAVerificationView.as_view(), name='mfa_verify'),
    
    # User profile
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    
    # Device management
    path('devices/', DeviceManagementView.as_view(), name='device_management'),
    
    # Security features
    path('security/status/', user_security_status, name='security_status'),
    path('security/logout-all/', force_logout_all_sessions, name='logout_all'),
]
