# VIP Ride-Hailing Platform - Flutter Integration Guide

## 🚀 Backend Ready for Flutter Development!

Your Django backend is fully ready for Flutter mobile app development. Below is the comprehensive integration guide.

## 🌐 Base API Configuration

**Base URL**: `http://your-domain.com/api/v1/`
**Development URL**: `http://localhost:8001/api/v1/`

## 🔐 Authentication System

### JWT Token Authentication
```dart
// Flutter HTTP Headers
{
  'Authorization': 'Bearer ${token}',
  'Content-Type': 'application/json'
}
```

### Key Authentication Endpoints:
- **Login**: `POST /api/v1/accounts/login/`
- **Register**: `POST /api/v1/accounts/register/`
- **Token Refresh**: `POST /api/v1/accounts/refresh/`
- **Logout**: `POST /api/v1/accounts/logout/`
- **MFA Setup**: `POST /api/v1/accounts/mfa/setup/`
- **Password Change**: `POST /api/v1/accounts/password/change/`

## 👥 User Management (3-Tier System)

### User Profile & Tier Management
- **Profile**: `GET/PUT /api/v1/accounts/profile/`
- **Security Status**: `GET /api/v1/accounts/security/status/`
- **Device Management**: `POST /api/v1/accounts/devices/`

### User Tiers:
1. **Normal Users**: Standard ride features
2. **Premium Users**: Luxury cars + hotel bookings
3. **VIP Users**: Encrypted GPS tracking + SOS + priority support

## 🚗 Ride Management

### Core Ride Endpoints:
- **Request Ride**: `POST /api/v1/rides/workflow/request/`
- **Active Rides**: `GET /api/v1/rides/workflow/active/`
- **Ride Status**: `GET /api/v1/rides/workflow/{ride_id}/status/`
- **Cancel Ride**: `POST /api/v1/rides/workflow/{ride_id}/cancel/`
- **Complete Ride**: `POST /api/v1/rides/workflow/{ride_id}/complete/`

### Ride Matching System:
- **Request Ride**: `POST /api/v1/rides/matching/matching/request-ride/`
- **Active Offers**: `GET /api/v1/rides/matching/matching/active-offers/`
- **Driver Response**: `POST /api/v1/rides/matching/matching/driver-response/`
- **Matching Stats**: `GET /api/v1/rides/matching/matching/stats/`

## 📍 GPS Tracking (VIP Feature)

### Location Endpoints:
- **Location Updates**: `POST /api/v1/gps/locations/`
- **Location Detail**: `GET /api/v1/gps/locations/{id}/`
- **Route Optimization**: `GET /api/v1/gps/routes/{id}/`

**Note**: VIP users get AES-256-GCM encrypted GPS tracking for enhanced security.

## 🏨 Hotel Partnerships (Premium/VIP)

### Customer Hotel Booking:
- **Search Hotels**: `GET /api/v1/hotel-partnerships/hotels/search/`
- **Nearby Hotels**: `GET /api/v1/hotel-partnerships/hotels/nearby/`
- **Popular Hotels**: `GET /api/v1/hotel-partnerships/hotels/popular/`
- **Book Hotel**: `POST /api/v1/hotel-partnerships/bookings/`
- **Booking History**: `GET /api/v1/hotel-partnerships/bookings/`
- **Cancel Booking**: `POST /api/v1/hotel-partnerships/bookings/{id}/cancel/`

## 💳 Payment System

### Payment Management:
- **Payment Methods**: `GET/POST /api/v1/payments/payment-methods/`
- **Create Payment**: `POST /api/v1/payments/payments/create_ride_payment/`
- **Payment History**: `GET /api/v1/payments/payment-history/`
- **Verify Payment**: `POST /api/v1/payments/payments/{id}/verify/`
- **Request Refund**: `POST /api/v1/payments/payments/{id}/refund/`

### Supported Gateways:
- **Stripe**: `/api/v1/payments/webhooks/stripe/`
- **Paystack**: `/api/v1/payments/webhooks/paystack/`
- **Flutterwave**: `/api/v1/payments/webhooks/flutterwave/`

## 💰 Dynamic Pricing

### Pricing Endpoints:
- **Get Quote**: `GET /api/v1/pricing/quote/`
- **Surge Levels**: `GET /api/v1/pricing/surge-levels/`
- **Pricing Zones**: `GET /api/v1/pricing/zones/`
- **Validate Promo**: `POST /api/v1/pricing/validate-promo/`
- **Price Transparency**: `GET /api/v1/pricing/transparency/`

## 🚙 Fleet Management (For Drivers)

### Vehicle Management:
- **My Vehicles**: `GET /api/v1/fleet/api/vehicles/my_vehicles/`
- **Available Vehicles**: `GET /api/v1/fleet/api/vehicles/available_vehicles/`
- **Add Maintenance**: `POST /api/v1/fleet/api/vehicles/{id}/add_maintenance/`
- **Company Analytics**: `GET /api/v1/fleet/api/companies/{id}/analytics/`

## 🔔 Notifications

### Notification System:
- **Get Notifications**: `GET /api/v1/notifications/notifications/`
- **Unread Count**: `GET /api/v1/notifications/unread-count/`
- **Mark as Read**: `POST /api/v1/notifications/notifications/{id}/mark_read/`
- **Mark All Read**: `POST /api/v1/notifications/mark-all-read/`
- **Preferences**: `GET/PUT /api/v1/notifications/preferences/`

## 🚨 Emergency & SOS (VIP Feature)

### Control Center Integration:
- **Trigger SOS**: `POST /api/v1/control-center/api/sos/trigger/`
- **VIP Monitoring**: `GET /api/v1/control-center/api/vip-sessions/`
- **Emergency Incidents**: `GET /api/v1/control-center/api/incidents/`

## 🚗 Vehicle Leasing

### Leasing Marketplace:
- **Search Vehicles**: `GET /api/v1/leasing/search/`
- **Vehicle Listings**: `GET /api/v1/leasing/vehicles/`
- **Calculate Lease**: `POST /api/v1/leasing/calculate-lease/`
- **Owner Dashboard**: `GET /api/v1/leasing/owner-dashboard/`
- **Fleet Dashboard**: `GET /api/v1/leasing/fleet-dashboard/`

## 📱 Flutter Implementation Tips

### 1. HTTP Client Configuration
```dart
class ApiClient {
  static const String baseUrl = 'http://your-domain.com/api/v1/';
  static const Map<String, String> headers = {
    'Content-Type': 'application/json',
  };
  
  static Map<String, String> authHeaders(String token) => {
    ...headers,
    'Authorization': 'Bearer $token',
  };
}
```

### 2. User Tier Management
```dart
enum UserTier { normal, premium, vip }

class User {
  final String id;
  final String email;
  final UserTier tier;
  final Map<String, dynamic> permissions;
}
```

### 3. Real-time Features
- Use WebSocket for live ride tracking
- Implement push notifications for ride updates
- Real-time location sharing for VIP users

### 4. Security Implementation
- Store JWT tokens securely (Flutter Secure Storage)
- Implement biometric authentication for VIP users
- Use certificate pinning for API calls

## 🏗️ Architecture Recommendations

### State Management
- **Provider** or **Bloc** for state management
- **Get/GoRouter** for navigation
- **Dio** for HTTP requests

### Key Flutter Packages
```yaml
dependencies:
  flutter:
    sdk: flutter
  dio: ^5.0.0
  provider: ^6.0.0
  flutter_secure_storage: ^9.0.0
  google_maps_flutter: ^2.2.0
  geolocator: ^9.0.0
  firebase_messaging: ^14.0.0
  local_auth: ^2.1.0
```

## 🔧 Backend Features Already Implemented

✅ **Authentication**: JWT with MFA support  
✅ **User Management**: 3-tier system (Normal/Premium/VIP)  
✅ **Ride Matching**: Advanced algorithm with real-time updates  
✅ **Payment Processing**: Multi-gateway support  
✅ **GPS Tracking**: Encrypted for VIP users  
✅ **Hotel Integration**: Premium/VIP feature  
✅ **Fleet Management**: Multi-tier driver system  
✅ **Vehicle Leasing**: Marketplace with revenue sharing  
✅ **Dynamic Pricing**: Surge pricing with zones  
✅ **Emergency System**: SOS with control center  
✅ **Notifications**: Push notifications with preferences  
✅ **Monitoring**: Grafana + Prometheus metrics  
✅ **Security**: Rate limiting, RBAC, encryption  

## 🚀 Next Steps for Flutter Development

1. **Set up Flutter project structure**
2. **Implement authentication flow**
3. **Create user onboarding screens**
4. **Build ride booking interface**
5. **Integrate Google Maps for location**
6. **Implement payment gateway**
7. **Add push notifications**
8. **Create VIP-specific features**
9. **Implement offline support**
10. **Add comprehensive testing**

## 📋 API Testing

Test your APIs using the provided endpoints:
- **Health Check**: `GET /health/`
- **API Root**: `GET /api/v1/`
- **Prometheus Metrics**: `GET /metrics`

---

**Your Django backend is production-ready with comprehensive APIs for all VIP ride-hailing features!** 🎉

The Flutter app can now be built to consume these APIs and provide a seamless mobile experience for all user tiers.
