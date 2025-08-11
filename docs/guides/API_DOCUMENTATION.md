# VIP Ride-Hailing Platform - API Endpoints Documentation

## 🚀 API Overview

The VIP Ride-Hailing Platform provides a comprehensive REST API with **126+ endpoints** across 11 core modules. All endpoints are versioned under `/api/v1/` and require proper authentication.

### 📊 **API Endpoint Count Summary**

| Module | Endpoints | Description |
|--------|-----------|-------------|
| **Accounts** | 12 | User authentication, profiles, MFA, security |
| **Rides** | 22 | Ride matching, workflow, status management |
| **Fleet Management** | 8+ | Vehicle and fleet company management |
| **Vehicle Leasing** | 15+ | Vehicle marketplace and lease management |
| **Hotels** | 17+ | Hotel booking and customer services |
| **Hotel Partnerships** | 32+ | B2B hotel partnership management |
| **Payments** | 18+ | Payment processing, disputes, payouts |
| **Pricing** | 7 | Dynamic pricing, surge, quotes |
| **Notifications** | 12+ | Push notifications and preferences |
| **Control Center** | 8+ | Emergency response and VIP monitoring |
| **GPS Tracking** | 3 | Location tracking and route optimization |
| **Admin** | 1 | Django admin interface |
| **API Auth** | 1 | DRF authentication |

**Total Estimated Endpoints: 126+**

---

## 🔐 **Authentication Endpoints** (`/api/v1/accounts/`)

### Core Authentication
- `POST /api/v1/accounts/login/` - User login with tier-based tokens
- `POST /api/v1/accounts/refresh/` - Refresh JWT tokens
- `POST /api/v1/accounts/logout/` - User logout
- `POST /api/v1/accounts/register/` - User registration

### Security & MFA
- `POST /api/v1/accounts/password/change/` - Change password
- `POST /api/v1/accounts/mfa/setup/` - Setup multi-factor authentication
- `POST /api/v1/accounts/mfa/verify/` - Verify MFA codes
- `GET /api/v1/accounts/security/status/` - Get security status
- `POST /api/v1/accounts/security/logout-all/` - Force logout all sessions

### Profile & Device Management
- `GET /api/v1/accounts/profile/` - Get user profile
- `PUT /api/v1/accounts/profile/` - Update user profile
- `GET /api/v1/accounts/devices/` - List user devices
- `POST /api/v1/accounts/devices/` - Register new device

---

## 🚗 **Rides Module** (`/api/v1/rides/`)

### Ride Matching (`/api/v1/rides/matching/`)
- `GET /api/v1/rides/matching/` - List ride matching requests
- `POST /api/v1/rides/matching/request-ride/` - Request a new ride
- `POST /api/v1/rides/matching/driver-response/` - Driver response to ride request
- `GET /api/v1/rides/matching/active-offers/` - Get active ride offers
- `PATCH /api/v1/rides/matching/driver-status/` - Update driver status
- `GET /api/v1/rides/matching/surge-zones/` - Get surge pricing zones
- `GET /api/v1/rides/matching/stats/` - Get matching statistics
- `GET /api/v1/rides/matching/{id}/status/` - Get specific ride status
- `POST /api/v1/rides/matching/cancel/` - Cancel ride request

### Ride Workflow (`/api/v1/rides/workflow/`)
- `POST /api/v1/rides/workflow/request/` - Create ride request
- `POST /api/v1/rides/workflow/{ride_id}/accept/` - Driver accept ride
- `POST /api/v1/rides/workflow/{ride_id}/cancel/` - Cancel ride
- `PATCH /api/v1/rides/workflow/{ride_id}/status/` - Update ride status
- `POST /api/v1/rides/workflow/{ride_id}/complete/` - Complete ride
- `GET /api/v1/rides/workflow/{ride_id}/history/` - Get status history
- `GET /api/v1/rides/workflow/{ride_id}/workflow/` - Get workflow status
- `GET /api/v1/rides/workflow/active/` - Get user's active rides
- `GET /api/v1/rides/workflow/cancellation-policy/` - Get cancellation policy
- `GET /api/v1/rides/workflow/{ride_id}/cancellation-policy/` - Get ride-specific policy
- `POST /api/v1/rides/workflow/{ride_id}/sos/` - Trigger SOS emergency
- **ViewSet Operations**: `GET`, `POST`, `PUT`, `PATCH`, `DELETE` for ride management

---

## 🚐 **Fleet Management** (`/api/v1/fleet/`)

### Vehicle Management (`/api/v1/fleet/api/vehicles/`)
- `GET /api/v1/fleet/api/vehicles/` - List all vehicles
- `POST /api/v1/fleet/api/vehicles/` - Create new vehicle
- `GET /api/v1/fleet/api/vehicles/{id}/` - Get vehicle details
- `PUT /api/v1/fleet/api/vehicles/{id}/` - Update vehicle
- `PATCH /api/v1/fleet/api/vehicles/{id}/` - Partial update vehicle
- `DELETE /api/v1/fleet/api/vehicles/{id}/` - Delete vehicle

### Fleet Company Management (`/api/v1/fleet/api/companies/`)
- `GET /api/v1/fleet/api/companies/` - List fleet companies
- `POST /api/v1/fleet/api/companies/` - Create fleet company
- `GET /api/v1/fleet/api/companies/{id}/` - Get company details
- `PUT /api/v1/fleet/api/companies/{id}/` - Update company
- `PATCH /api/v1/fleet/api/companies/{id}/` - Partial update company
- `DELETE /api/v1/fleet/api/companies/{id}/` - Delete company

---

## 🏎️ **Vehicle Leasing** (`/api/v1/leasing/`)

### Vehicle Listings
- `GET /api/v1/leasing/vehicles/` - List available vehicles
- `POST /api/v1/leasing/vehicles/` - Create vehicle listing
- `GET /api/v1/leasing/vehicles/{id}/` - Get vehicle details
- `PUT /api/v1/leasing/vehicles/{id}/` - Update vehicle listing
- `DELETE /api/v1/leasing/vehicles/{id}/` - Delete listing

### Lease Management
- `GET /api/v1/leasing/leases/` - List leases
- `POST /api/v1/leasing/leases/` - Create new lease
- `GET /api/v1/leasing/leases/{id}/` - Get lease details
- `PUT /api/v1/leasing/leases/{id}/` - Update lease
- `DELETE /api/v1/leasing/leases/{id}/` - Terminate lease

### Lease Payments
- `GET /api/v1/leasing/payments/` - List lease payments
- `POST /api/v1/leasing/payments/` - Process payment
- `GET /api/v1/leasing/payments/{id}/` - Get payment details

### Custom Endpoints
- `GET /api/v1/leasing/search/` - Search vehicles with filters
- `POST /api/v1/leasing/calculate-lease/` - Calculate lease pricing
- `GET /api/v1/leasing/owner-dashboard/` - Vehicle owner dashboard
- `GET /api/v1/leasing/fleet-dashboard/` - Fleet company dashboard

---

## 🏨 **Hotels Module** (`/api/v1/hotels/`)

### Hotel Management
- `GET /api/v1/hotels/hotels/` - List hotels
- `POST /api/v1/hotels/hotels/` - Create hotel (admin)
- `GET /api/v1/hotels/hotels/{id}/` - Get hotel details
- `PUT /api/v1/hotels/hotels/{id}/` - Update hotel
- `DELETE /api/v1/hotels/hotels/{id}/` - Delete hotel

### Hotel Bookings
- `GET /api/v1/hotels/bookings/` - List user bookings
- `POST /api/v1/hotels/bookings/` - Create new booking
- `GET /api/v1/hotels/bookings/{id}/` - Get booking details
- `PUT /api/v1/hotels/bookings/{id}/` - Update booking
- `DELETE /api/v1/hotels/bookings/{id}/` - Cancel booking

### Hotel Reviews
- `GET /api/v1/hotels/reviews/` - List hotel reviews
- `POST /api/v1/hotels/reviews/` - Submit review
- `GET /api/v1/hotels/reviews/{id}/` - Get review details
- `PUT /api/v1/hotels/reviews/{id}/` - Update review
- `DELETE /api/v1/hotels/reviews/{id}/` - Delete review

### Custom Hotel Endpoints
- `GET /api/v1/hotels/search/` - Search hotels with filters
- `POST /api/v1/hotels/availability/` - Check room availability
- `GET /api/v1/hotels/popular/` - Get popular hotels
- `GET /api/v1/hotels/nearby/` - Find nearby hotels
- `GET /api/v1/hotels/amenities/` - List available amenities

---

## 🤝 **Hotel Partnerships** (`/api/v1/hotel-partnerships/`)

### B2B Hotel Management (32+ endpoints)
- `GET /api/v1/hotel-partnerships/api/hotels/` - List partner hotels
- `POST /api/v1/hotel-partnerships/api/hotels/` - Register hotel
- Full CRUD operations for: Hotels, Staff, Rooms, Guests, Bookings
- Bulk operations and reporting endpoints

### Partner-Specific Operations
- **Hotel ViewSet**: 6 endpoints (CRUD + list/detail)
- **Staff ViewSet**: 6 endpoints (staff management)
- **Room ViewSet**: 6 endpoints (room inventory)
- **Guest ViewSet**: 6 endpoints (guest management)
- **Booking ViewSet**: 6 endpoints (booking management)
- **Bulk Events ViewSet**: 2+ endpoints (bulk operations)
- **Commission Reports ViewSet**: 6 endpoints (financial reporting)

---

## 💳 **Payments Module** (`/api/v1/payments/`)

### Payment Processing
- `GET /api/v1/payments/payments/` - List payments
- `POST /api/v1/payments/payments/` - Process payment
- `GET /api/v1/payments/payments/{id}/` - Get payment details
- `PUT /api/v1/payments/payments/{id}/` - Update payment
- `DELETE /api/v1/payments/payments/{id}/` - Void payment

### Payment Methods
- `GET /api/v1/payments/payment-methods/` - List payment methods
- `POST /api/v1/payments/payment-methods/` - Add payment method
- `GET /api/v1/payments/payment-methods/{id}/` - Get method details
- `DELETE /api/v1/payments/payment-methods/{id}/` - Remove method

### Driver Payouts
- `GET /api/v1/payments/driver-payouts/` - List payouts
- `POST /api/v1/payments/driver-payouts/` - Process payout
- `GET /api/v1/payments/driver-payouts/{id}/` - Get payout details

### Disputes & Webhooks
- Full CRUD for disputes
- `POST /api/v1/payments/webhooks/paystack/` - Paystack webhook
- `POST /api/v1/payments/webhooks/flutterwave/` - Flutterwave webhook
- `POST /api/v1/payments/webhooks/stripe/` - Stripe webhook

### Custom Payment Endpoints
- `GET /api/v1/payments/commission-reports/` - Commission reports
- `GET /api/v1/payments/payment-history/` - Payment history
- `GET /api/v1/payments/gateway-status/` - Gateway status

---

## 💰 **Pricing Module** (`/api/v1/pricing/`)

### Public Pricing
- `GET /api/v1/pricing/quote/` - Get price quote
- `GET /api/v1/pricing/surge-levels/` - Current surge levels
- `GET /api/v1/pricing/zones/` - Pricing zones
- `GET /api/v1/pricing/transparency/` - Price breakdown

### User Features
- `POST /api/v1/pricing/validate-promo/` - Validate promo codes

### Admin Features
- `POST /api/v1/pricing/admin/zones/{zone_id}/update-surge/` - Update zone surge
- `POST /api/v1/pricing/admin/update-all-surge/` - Update all surge pricing

---

## 🔔 **Notifications Module** (`/api/v1/notifications/`)

### Notification Management
- `GET /api/v1/notifications/notifications/` - List notifications
- `POST /api/v1/notifications/notifications/` - Create notification
- `GET /api/v1/notifications/notifications/{id}/` - Get notification
- `PUT /api/v1/notifications/notifications/{id}/` - Update notification
- `DELETE /api/v1/notifications/notifications/{id}/` - Delete notification

### Preferences & Templates
- Full CRUD for notification preferences
- Full CRUD for notification templates

### Custom Notification Endpoints
- `POST /api/v1/notifications/send/` - Send single notification
- `POST /api/v1/notifications/send-bulk/` - Send bulk notifications
- `GET /api/v1/notifications/delivery-status/` - Check delivery status
- `POST /api/v1/notifications/mark-all-read/` - Mark all as read
- `GET /api/v1/notifications/unread-count/` - Get unread count

---

## 🚨 **Control Center** (`/api/v1/control-center/`)

### Emergency Management
- `GET /api/v1/control-center/api/incidents/` - List incidents
- `POST /api/v1/control-center/api/incidents/` - Create incident
- `GET /api/v1/control-center/api/incidents/{id}/` - Get incident details
- `PUT /api/v1/control-center/api/incidents/{id}/` - Update incident

### VIP Monitoring
- `GET /api/v1/control-center/api/vip-sessions/` - List VIP sessions
- `POST /api/v1/control-center/api/vip-sessions/` - Create session
- `GET /api/v1/control-center/api/vip-sessions/{id}/` - Get session details
- `PUT /api/v1/control-center/api/vip-sessions/{id}/` - Update session

### Emergency Features
- `POST /api/v1/control-center/api/sos/trigger/` - Trigger SOS emergency
- `GET /api/v1/control-center/api/dashboard/` - Monitoring dashboard

---

## 📍 **GPS Tracking** (`/api/v1/gps/`)

### Location Tracking
- `GET /api/v1/gps/locations/` - List GPS locations
- `POST /api/v1/gps/locations/` - Create location entry
- `GET /api/v1/gps/locations/{id}/` - Get location details

### Route Optimization
- `GET /api/v1/gps/routes/{id}/` - Get route optimization details

---

## 🎯 **API Features & Standards**

### Authentication
- **JWT Token-Based**: All endpoints require valid JWT tokens
- **Tier-Based Access**: Different access levels (Normal, Premium, VIP)
- **MFA Support**: Multi-factor authentication for security
- **Device Management**: Track and manage user devices

### Security Features
- **Rate Limiting**: API throttling to prevent abuse
- **CORS Protection**: Cross-origin request security
- **CSRF Protection**: Cross-site request forgery protection
- **Input Validation**: Comprehensive data validation
- **Audit Logging**: Security monitoring and logging

### API Standards
- **RESTful Design**: Follows REST architectural principles
- **Consistent Responses**: Standardized JSON responses
- **Error Handling**: Comprehensive error codes and messages
- **Pagination**: Efficient data pagination
- **Filtering**: Advanced filtering and search capabilities
- **Versioning**: API versioning with `/v1/` prefix

### Response Formats
```json
{
  "status": "success|error",
  "message": "Human readable message",
  "data": {},
  "errors": {},
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "pages": 5
  }
}
```

---

## 🚀 **Development Access**

### Development Server
```bash
# Start with development settings
python manage.py runserver 127.0.0.1:8001 --settings=vip_ride_platform.dev_settings
```

### API Base URLs
- **Development**: `http://127.0.0.1:8001/api/v1/`
- **Admin Panel**: `http://127.0.0.1:8001/admin/`
- **API Auth**: `http://127.0.0.1:8001/api-auth/`

### API Testing
- **Postman Collection**: Available for comprehensive API testing
- **Django Admin**: Full admin interface for all models
- **API Browser**: DRF browsable API for development
- **Documentation**: Auto-generated API documentation

---

**Total API Endpoints: 126+ across 11 core modules** 🎉
