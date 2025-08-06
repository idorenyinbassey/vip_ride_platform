# Authentication Utilities
"""
Utility functions for JWT authentication and security features
"""

import hashlib
import uuid
from datetime import timedelta
from typing import Optional
from django.contrib.gis.geoip2 import GeoIP2
from django.utils import timezone


def get_client_ip(request) -> str:
    """Extract client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip or '127.0.0.1'


def get_device_fingerprint(request) -> str:
    """Generate device fingerprint from request headers"""
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
    accept_encoding = request.META.get('HTTP_ACCEPT_ENCODING', '')
    
    # Create fingerprint from browser characteristics
    fingerprint_data = f"{user_agent}|{accept_language}|{accept_encoding}"
    
    # Hash to create consistent fingerprint
    return hashlib.sha256(fingerprint_data.encode()).hexdigest()[:32]


def get_location_from_ip(ip_address: str) -> Optional[dict]:
    """Get approximate location from IP address"""
    try:
        g = GeoIP2()
        location = g.city(ip_address)
        return {
            'country': location.get('country_name'),
            'city': location.get('city'),
            'latitude': location.get('latitude'),
            'longitude': location.get('longitude'),
        }
    except Exception:
        return None


def validate_device_trust(request, user) -> bool:
    """Validate if device is trusted for the user"""
    device_fingerprint = get_device_fingerprint(request)
    
    # Check if device is in user's trusted devices
    from .models import TrustedDevice
    
    try:
        trusted_device = TrustedDevice.objects.get(
            user=user,
            device_fingerprint=device_fingerprint,
            is_active=True
        )
        trusted_device.last_used_at = timezone.now()
        trusted_device.save()
        return True
    except TrustedDevice.DoesNotExist:
        return False


def generate_backup_codes(count: int = 10) -> list:
    """Generate backup codes for MFA"""
    codes = []
    for _ in range(count):
        code = str(uuid.uuid4()).replace('-', '')[:8].upper()
        codes.append(code)
    return codes


def is_suspicious_login(request, user) -> bool:
    """Detect suspicious login patterns"""
    current_ip = get_client_ip(request)
    
    # Check recent login history
    from .models import LoginAttempt
    
    recent_attempts = LoginAttempt.objects.filter(
        user=user,
        created_at__gte=timezone.now() - timedelta(hours=24)
    ).order_by('-created_at')[:5]
    
    if not recent_attempts:
        return False  # First login, not suspicious
    
    # Check for different IPs
    recent_ips = set(attempt.ip_address for attempt in recent_attempts)
    if len(recent_ips) > 3:  # More than 3 different IPs in 24h
        return True
    
    # Check for different devices
    recent_devices = set(
        attempt.device_fingerprint for attempt in recent_attempts
    )
    if len(recent_devices) > 2:  # More than 2 different devices
        return True
    
    # Check geographic distance
    if len(recent_ips) > 1:
        current_location = get_location_from_ip(current_ip)
        if current_location:
            for attempt in recent_attempts[:2]:  # Check last 2 attempts
                attempt_location = get_location_from_ip(attempt.ip_address)
                if attempt_location and current_location:
                    distance = calculate_distance(
                        current_location['latitude'],
                        current_location['longitude'],
                        attempt_location['latitude'],
                        attempt_location['longitude']
                    )
                    if distance > 1000:  # More than 1000km apart
                        return True
    
    return False


def calculate_distance(lat1: float, lon1: float,
                       lat2: float, lon2: float) -> float:
    """Calculate distance between two points using Haversine formula"""
    import math
    
    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2)
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of Earth in kilometers
    r = 6371
    
    return c * r


def generate_mfa_code(length: int = 6) -> str:
    """Generate random MFA code"""
    import random
    import string
    
    return ''.join(random.choices(string.digits, k=length))


def hash_token(token: str) -> str:
    """Hash token for secure storage"""
    return hashlib.sha256(token.encode()).hexdigest()


def verify_token_hash(token: str, token_hash: str) -> bool:
    """Verify token against stored hash"""
    return hash_token(token) == token_hash


def validate_phone_number(phone_number: str) -> bool:
    """Validate phone number format"""
    import re
    
    if not phone_number:
        return False
    
    # Remove all non-digit characters except +
    cleaned = re.sub(r'[^\d+]', '', phone_number)
    
    # Check various international formats
    patterns = [
        r'^\+234[789]\d{9}$',  # Nigeria: +234XXXXXXXXX
        r'^234[789]\d{9}$',    # Nigeria: 234XXXXXXXXX
        r'^0[789]\d{9}$',      # Nigeria: 0XXXXXXXXX
        r'^\+\d{10,15}$',      # International: +XXXXXXXXXX
        r'^\d{10,15}$',        # Local: XXXXXXXXXX
    ]
    
    for pattern in patterns:
        if re.match(pattern, cleaned):
            return True
    
    return False


def format_phone_number(phone_number: str) -> str:
    """Format phone number to international format"""
    import re
    
    if not phone_number:
        return phone_number
    
    # Remove all non-digit characters except +
    cleaned = re.sub(r'[^\d+]', '', phone_number)
    
    # Convert Nigerian numbers to international format
    if cleaned.startswith('0') and len(cleaned) == 11:
        # Nigerian local format: 0XXXXXXXXX -> +234XXXXXXXXX
        return '+234' + cleaned[1:]
    elif cleaned.startswith('234') and len(cleaned) == 13:
        # Nigerian without +: 234XXXXXXXXX -> +234XXXXXXXXX
        return '+' + cleaned
    elif cleaned.startswith('+'):
        # Already international format
        return cleaned
    elif len(cleaned) >= 10:
        # Assume international number without +
        return '+' + cleaned
    
    return phone_number
