"""
URL configuration for vip_ride_platform project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # Root logout redirects to portal logout
    path(
        'logout/',
        RedirectView.as_view(
            pattern_name='portal:logout', permanent=False, query_string=True
        ),
        name='logout_redirect'
    ),
    # Common auth path alias to marketing login
    path(
        'accounts/login/',
        RedirectView.as_view(
            pattern_name='marketing:login', permanent=False, query_string=True
        ),
        name='accounts_login_alias'
    ),
    # Marketing site
    path('', include('marketing.urls')),
    # Web portal (client + driver)
    path('portal/', include('portal.urls')),
    # i18n endpoints (set_language)
    path('i18n/', include('django.conf.urls.i18n')),
    
    # API URLs
    path('api/v1/', include('vip_ride_platform.api_urls')),  # API Root
    path('api/v1/accounts/', include('accounts.urls')),
    path('api/v1/rides/', include('rides.urls')),
    path('api/v1/fleet/', include('fleet_management.urls')),
    path('api/v1/leasing/', include('vehicle_leasing.urls')),
    path('api/v1/hotel-partnerships/', include('hotel_partnerships.urls')),
    path('api/v1/payments/', include('payments.urls')),
    path('api/v1/pricing/', include('pricing.urls')),
    path('api/v1/notifications/', include('notifications.urls')),
    path('api/v1/control-center/', include('control_center.urls')),
    path('api/v1/gps/', include('gps_tracking.urls')),
    
    # Monitoring & Health
    path('', include('django_prometheus.urls')),  # Prometheus metrics endpoint at /metrics
    path('health/', include('health.urls')),  # Health check endpoint
    
    # API Authentication
    path('api-auth/', include('rest_framework.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )
