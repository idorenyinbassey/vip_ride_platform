# JWT Authentication URL Configuration
"""
URL pa    # Premium Digital Card endpoints
    path('premium-cards/payment-intent/', views.PaymentIntentView.as_view(), name='premium_card_payment_intent'),
    path('premium-cards/purchase/', views.PremiumCardPurchaseView.as_view(), name='premium_card_purchase'),erns for JWT authentication endpoints
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    TierBasedTokenObtainPairView,
    TierBasedTokenRefreshView,
    LogoutView,
    UserRegistrationView,
    PasswordChangeView,
    MFAVerificationView,
    MFACommunicationView,
    MFAConfirmationView,
    UserProfileView,
    DeviceManagementView,
    user_security_status,
    force_logout_all_sessions
)

from .premium_card_views import (
    PremiumCardPurchaseView,
    PremiumCardActivationView,
    PremiumCardListView,
    user_premium_status,
    PaymentIntentView
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
    
    # MFA endpoints
    path('auth/mfa/setup/', MFACommunicationView.as_view(), name='mfa-setup'),
    path('auth/mfa/confirm/', MFAConfirmationView.as_view(), name='mfa-confirmation'),
    path('auth/mfa/verify/', MFAVerificationView.as_view(), name='mfa-verification'),
    
    # User profile
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    
    # Device management
    path('devices/', DeviceManagementView.as_view(), name='device_management'),
    
    # Premium Digital Card endpoints
    path('premium-cards/payment-intent/', PaymentIntentView.as_view(), name='premium_card_payment_intent'),
    path('premium-cards/purchase/', PremiumCardPurchaseView.as_view(), name='premium_card_purchase'),
    path('premium-cards/activate/', PremiumCardActivationView.as_view(), name='premium_card_activation'),
    path('premium-cards/', PremiumCardListView.as_view(), name='premium_cards_list'),
    path('premium-status/', user_premium_status, name='user_premium_status'),
    
    # Security features
    path('security/status/', user_security_status, name='security_status'),
    path('security/logout-all/', force_logout_all_sessions, name='logout_all'),
]
