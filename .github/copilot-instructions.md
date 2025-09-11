# VIP Ride-Hailing Platform - Copilot Instructions

<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

## Project Overview
This is a VIP ride-hailing platform with Django 5.2.5 backend and React Native 0.80.2 mobile apps.

## Architecture
- **Backend**: Django 5.2.5 + Django REST Framework 3.16.0
- **Database**: PostgreSQL + Redis for caching
- **Mobile**: React Native 0.80.2 with TypeScript
- **Security**: AES-256-GCM encryption for VIP GPS tracking
- **Compliance**: NDPR (Nigeria Data Protection Regulation)

## User Tiers & Pricing
1. **Normal**: Standard rides (15-20% commission)
2. **Premium**: Luxury cars + hotel booking (20-25% commission)
3. **VIP**: Encrypted GPS, SOS, trusted drivers (25-30% commission)

## Driver & Vehicle Categories
1. **Private Drivers with Classic Cars**: Flexible billing by engine type (V6/V8/4-stroke)
2. **Fleet Companies with Premium Cars/Vans**: Fixed billing rates, priority VIP allocation
3. **Vehicle Owners**: Lease cars to fleet companies with revenue-sharing contracts

## Key Features
- Multi-tier user system with different service levels
- Hotel partnership integration
- Control Center for VIP monitoring and emergency response
- Multi-tier driver verification system
- SOS emergency protocols with location tracking
- Fleet management system
- Vehicle leasing marketplace
- Driver subscriptions: $99-299/month based on tier access

## Code Guidelines
- Use Django best practices with proper app separation
- Implement proper API versioning with DRF
- Use class-based views and serializers
- Implement proper authentication and authorization
- Use environment variables for sensitive configuration
- Follow NDPR compliance requirements for data handling
- Use AES-256-GCM for VIP user location encryption
- Implement proper error handling and logging
- Use Celery for background tasks (notifications, billing)
- Use Redis for caching and real-time features

## Security Requirements
- JWT authentication for API access
- Role-based permissions (Normal/Premium/VIP/Driver/Fleet/Admin)
- GPS encryption for VIP users
- Secure payment processing
- Data anonymization for NDPR compliance
- Rate limiting for API endpoints
- Input validation and sanitization

## Database Design
- Use PostgreSQL with proper indexing
- Implement soft deletes for audit trails
- Use UUID for sensitive IDs
- Proper foreign key relationships
- Migration best practices

## Futterwave UI (JSON Instructions)

{
  "project": "VIP Ride-Hailing Flutter App",
  "description": "A unified Flutter app with role-based navigation for Clients (Regular, VIP, VIP Premium) and Drivers (Independent, Fleet Owner, Fleet Driver, Leased). Integrated with Django backend using JWT. Uses OpenStreetMap instead of Google Maps.",
  "backend": {
    "framework": "Django",
    "auth": "JWT authentication",
    "base_url": "https://your-domain.com",
    "api_endpoints": {
      "authentication": {
        "login": "/api/v1/accounts/login/",
        "register": "/api/v1/accounts/register/",
        "refresh_token": "/api/v1/accounts/refresh/",
        "logout": "/api/v1/accounts/logout/",
        "password_change": "/api/v1/accounts/password/change/"
      },
      "mfa": {
        "setup": "/api/v1/accounts/auth/mfa/setup/",
        "verify": "/api/v1/accounts/auth/mfa/verify/",
        "confirm": "/api/v1/accounts/auth/mfa/confirm/",
        "status": "/api/v1/accounts/auth/mfa/status/"
      },
      "user_management": {
        "profile": "/api/v1/accounts/profile/",
        "tier_level": "/api/v1/accounts/tier/level/",
        "tier_benefits": "/api/v1/accounts/tier/benefits/",
        "security_status": "/api/v1/accounts/security/status/",
        "device_management": "/api/v1/accounts/devices/"
      },
      "vip_cards": {
        "generate": "/api/v1/accounts/cards/generate/",
        "activate": "/api/v1/accounts/cards/activate/",
        "user_cards": "/api/v1/accounts/cards/user/",
        "card_details": "/api/v1/accounts/cards/details/{serial_number}/",
        "activation_history": "/api/v1/accounts/cards/history/"
      },
      "premium_cards": {
        "list": "/api/v1/accounts/premium-cards/",
        "purchase": "/api/v1/accounts/premium-cards/purchase/",
        "activate": "/api/v1/accounts/premium-cards/activate/",
        "payment_intent": "/api/v1/accounts/premium-cards/payment-intent/",
        "premium_status": "/api/v1/accounts/premium-status/"
      },
      "rides": {
        "request_ride": "/api/v1/rides/workflow/request/",
        "active_rides": "/api/v1/rides/workflow/active/",
        "ride_status": "/api/v1/rides/workflow/{ride_id}/status/",
        "accept_ride": "/api/v1/rides/workflow/{ride_id}/accept/",
        "complete_ride": "/api/v1/rides/workflow/{ride_id}/complete/",
        "cancel_ride": "/api/v1/rides/workflow/{ride_id}/cancel/",
        "ride_history": "/api/v1/rides/workflow/{ride_id}/history/",
        "trigger_sos": "/api/v1/rides/workflow/{ride_id}/sos/"
      },
      "ride_matching": {
        "request_ride": "/api/v1/rides/matching/matching/request_ride/",
        "driver_response": "/api/v1/rides/matching/matching/driver_response/",
        "driver_status": "/api/v1/rides/matching/matching/driver_status/",
        "active_offers": "/api/v1/rides/matching/matching/active_offers/",
        "surge_zones": "/api/v1/rides/matching/matching/surge_zones/",
        "matching_stats": "/api/v1/rides/matching/matching/matching_stats/"
      },
      "gps_tracking": {
        "locations": "/api/v1/gps/locations/",
        "location_detail": "/api/v1/gps/locations/{id}/",
        "encrypt_gps": "/api/v1/gps/encrypt/",
        "decrypt_gps": "/api/v1/gps/decrypt/",
        "key_exchange": "/api/v1/gps/key-exchange/",
        "session_status": "/api/v1/gps/sessions/{session_id}/status/",
        "terminate_session": "/api/v1/gps/sessions/terminate/",
        "encryption_stats": "/api/v1/gps/stats/"
      },
      "fleet_management": {
        "companies": "/api/v1/fleet/api/companies/",
        "company_detail": "/api/v1/fleet/api/companies/{id}/",
        "company_vehicles": "/api/v1/fleet/api/companies/{id}/vehicles/",
        "company_analytics": "/api/v1/fleet/api/companies/{id}/analytics/",
        "verify_company": "/api/v1/fleet/api/companies/{id}/verify_company/",
        "vehicles": "/api/v1/fleet/api/vehicles/",
        "vehicle_detail": "/api/v1/fleet/api/vehicles/{id}/",
        "my_vehicles": "/api/v1/fleet/api/vehicles/my_vehicles/",
        "available_vehicles": "/api/v1/fleet/api/vehicles/available_vehicles/",
        "assign_driver": "/api/v1/fleet/api/vehicles/{id}/assign_driver/",
        "add_maintenance": "/api/v1/fleet/api/vehicles/{id}/add_maintenance/"
      },
      "hotel_partnerships": {
        "hotels": "/api/v1/hotel-partnerships/hotels/",
        "hotel_detail": "/api/v1/hotel-partnerships/hotels/{id}/",
        "nearby_hotels": "/api/v1/hotel-partnerships/hotels/nearby/",
        "popular_hotels": "/api/v1/hotel-partnerships/hotels/popular/",
        "search_hotels": "/api/v1/hotel-partnerships/hotels/search/",
        "bookings": "/api/v1/hotel-partnerships/bookings/",
        "booking_detail": "/api/v1/hotel-partnerships/bookings/{id}/",
        "cancel_booking": "/api/v1/hotel-partnerships/bookings/{id}/cancel/"
      },
      "hotel_admin": {
        "admin_hotels": "/api/v1/hotel-partnerships/admin/hotels/",
        "admin_bookings": "/api/v1/hotel-partnerships/admin/bookings/",
        "bulk_events": "/api/v1/hotel-partnerships/admin/bulk-events/",
        "commission_reports": "/api/v1/hotel-partnerships/admin/commission-reports/",
        "hotel_guests": "/api/v1/hotel-partnerships/admin/guests/",
        "hotel_rooms": "/api/v1/hotel-partnerships/admin/rooms/",
        "hotel_staff": "/api/v1/hotel-partnerships/admin/staff/",
        "pms_logs": "/api/v1/hotel-partnerships/admin/pms-logs/"
      },
      "vehicle_leasing": {
        "vehicles": "/api/v1/leasing/vehicles/",
        "vehicle_detail": "/api/v1/leasing/vehicles/{id}/",
        "search_vehicles": "/api/v1/leasing/search/",
        "leases": "/api/v1/leasing/leases/",
        "lease_detail": "/api/v1/leasing/leases/{id}/",
        "approve_lease": "/api/v1/leasing/leases/{id}/approve/",
        "terminate_lease": "/api/v1/leasing/leases/{id}/terminate/",
        "revenue_report": "/api/v1/leasing/leases/{id}/revenue_report/",
        "calculate_lease": "/api/v1/leasing/calculate-lease/",
        "owner_dashboard": "/api/v1/leasing/owner-dashboard/",
        "fleet_dashboard": "/api/v1/leasing/fleet-dashboard/",
        "payments": "/api/v1/leasing/payments/",
        "mark_payment_paid": "/api/v1/leasing/payments/{id}/mark_paid/"
      },
      "payments": {
        "payments": "/api/v1/payments/payments/",
        "payment_detail": "/api/v1/payments/payments/{id}/",
        "create_ride_payment": "/api/v1/payments/payments/create_ride_payment/",
        "verify_payment": "/api/v1/payments/payments/{id}/verify/",
        "refund_payment": "/api/v1/payments/payments/{id}/refund/",
        "payment_methods": "/api/v1/payments/payment-methods/",
        "payment_history": "/api/v1/payments/payment-history/",
        "driver_payouts": "/api/v1/payments/driver-payouts/",
        "earnings_summary": "/api/v1/payments/driver-payouts/earnings_summary/",
        "commission_reports": "/api/v1/payments/commission-reports/",
        "gateway_status": "/api/v1/payments/gateway-status/",
        "disputes": "/api/v1/payments/disputes/",
        "resolve_dispute": "/api/v1/payments/disputes/{id}/resolve/",
        "currencies": "/api/v1/payments/currencies/",
        "exchange_rates": "/api/v1/payments/currencies/exchange_rates/"
      },
      "pricing": {
        "price_quote": "/api/v1/pricing/quote/",
        "pricing_zones": "/api/v1/pricing/zones/",
        "surge_levels": "/api/v1/pricing/surge-levels/",
        "price_transparency": "/api/v1/pricing/transparency/",
        "validate_promo": "/api/v1/pricing/validate-promo/",
        "update_all_surge": "/api/v1/pricing/admin/update-all-surge/",
        "update_zone_surge": "/api/v1/pricing/admin/zones/{zone_id}/update-surge/"
      },
      "notifications": {
        "notifications": "/api/v1/notifications/notifications/",
        "notification_detail": "/api/v1/notifications/notifications/{id}/",
        "mark_read": "/api/v1/notifications/notifications/{id}/mark_read/",
        "unread_notifications": "/api/v1/notifications/notifications/unread/",
        "mark_all_read": "/api/v1/notifications/mark-all-read/",
        "unread_count": "/api/v1/notifications/unread-count/",
        "send_notification": "/api/v1/notifications/send/",
        "send_bulk": "/api/v1/notifications/send-bulk/",
        "preferences": "/api/v1/notifications/preferences/",
        "templates": "/api/v1/notifications/templates/",
        "delivery_status": "/api/v1/notifications/delivery-status/"
      },
      "control_center": {
        "dashboard": "/api/v1/control-center/api/dashboard/",
        "incidents": "/api/v1/control-center/api/incidents/",
        "incident_detail": "/api/v1/control-center/api/incidents/{id}/",
        "update_incident_status": "/api/v1/control-center/api/incidents/{id}/update_status/",
        "active_incidents": "/api/v1/control-center/api/incidents/active_incidents/",
        "critical_incidents": "/api/v1/control-center/api/incidents/critical_incidents/",
        "trigger_sos": "/api/v1/control-center/api/sos/trigger/",
        "vip_sessions": "/api/v1/control-center/api/vip-sessions/",
        "vip_session_detail": "/api/v1/control-center/api/vip-sessions/{id}/",
        "vip_check_in": "/api/v1/control-center/api/vip-sessions/{id}/check_in/",
        "update_vip_location": "/api/v1/control-center/api/vip-sessions/{id}/update_location/"
      },
      "webhooks": {
        "stripe_webhook": "/api/v1/payments/webhooks/stripe/",
        "flutterwave_webhook": "/api/v1/payments/webhooks/flutterwave/",
        "paystack_webhook": "/api/v1/payments/webhooks/paystack/"
      }
    }
  },
  "roles": {
    "client": {
      "types": ["regular", "vip", "VIP Premium"],
      "features": {
        "regular": [
          "Login/Signup/Logout (JWT)",
          "Book on-demand rides (pickup, drop-off, vehicle type, estimated fare)",
          "Track rides in real-time using OpenStreetMap",
          "View driver details, ETA, and route progress",
          "Payments via wallet, saved cards, or cash",
          "View ride history and receipts",
          "Receive ride notifications (status, driver arrival, trip completion)",
          "SOS emergency button → alerts backend security desk",
          "Basic support/help center"
        ],
        "vip": [
          "All regular client features",
          "Priority ride matching with best-rated drivers and premium vehicles",
          "Discreet booking (masked client identity until ride acceptance)",
          "Concierge support (chat/call with staff)",
          "VIP pricing tiers (dynamic fares, discounts for premium vehicles)",
          "Vehicle preference selection (SUV, executive sedan, etc.)",
          "Enhanced SOS: escalated alerts to VIP support team"
        ],
        "Premium": [
          "All VIP client features",
          "Hotel partnerships: hotel client view to browse partner hotels, perks, and book rides",
          "Pre-booked rides from hotels/concierge appear automatically in client dashboard",
          "Encrypted ride tracking: visible only to hotel staff and security desk if enabled",
          "Discreet mode: minimal client details shared with drivers",
          "Exclusive access to high-security vehicles (SUVs, armored, luxury)",
          "Concierge integration: hotel staff chat/assist directly via app",
          "Advanced SOS: alerts hotel security and central security team, includes encrypted live GPS feed",
          "Partnership perks: hotel offers, ride bundles, VIP lounges, priority fleet allocation"
        ]
      }
    },
    "driver": {
      "types": ["independent_driver", "fleet_owner", "fleet_driver", "leased_driver"],
      "features": {
        "independent_driver": [
          "Login/Signup",
          "Register and verify personal vehicle (model, plate, documents)",
          "Toggle availability (online/offline)",
          "Accept/decline ride requests",
          "Track rides in progress with OpenStreetMap navigation",
          "View earnings dashboard (daily, weekly, monthly)",
          "View passenger ratings and feedback",
          "Receive notifications for rides, payments, cancellations",
          "SOS button → alerts backend security desk"
        ],
        "fleet_owner": [
          "Login/Signup",
          "Register multiple vehicles under fleet",
          "Invite and manage drivers (approve/remove)",
          "Assign vehicles to fleet drivers",
          "Monitor fleet earnings (by driver, by vehicle, total fleet)",
          "Generate reports (driver activity, vehicle usage, performance)",
          "Receive notifications (maintenance reminders, expiring documents)",
          "Security: receive SOS alerts from any fleet driver"
        ],
        "fleet_driver": [
          "Login under fleet",
          "Drive only assigned vehicle",
          "Toggle availability",
          "Accept/decline rides",
          "Track ride with OpenStreetMap navigation",
          "View personal earnings (fleet owner sees full fleet earnings)",
          "SOS button → alerts fleet owner + backend"
        ],
        "leased_driver": [
          "Login/Signup",
          "Drive leased vehicle assigned under contract",
          "View lease terms (daily fee, percentage split, expiry)",
          "Accept/decline rides",
          "Track ride with OpenStreetMap navigation",
          "Earnings auto-split between driver and vehicle owner/fleet",
          "Receive notifications (lease reminders, payment status)",
          "SOS button → alerts lessor + backend"
        ]
      }
    }
  },
  "flutter_structure": {
    "folders": [
      "lib/screens/client/regular/*",
      "lib/screens/client/vip/*",
      "lib/screens/client/vip premium/*",
      "lib/screens/driver/independent/*",
      "lib/screens/driver/fleet_owner/*",
      "lib/screens/driver/fleet_driver/*",
      "lib/screens/driver/leased/*",
      "lib/screens/shared/*",
      "lib/services/*",
      "lib/models/*",
      "lib/widgets/*"
    ],
    "main_flow": [
      "Splash screen checks token",
      "Login/Signup",
      "Fetch user profile and role",
      "If client → check type (regular, vip, black_tier)",
      "If driver → check type (independent, fleet_owner, fleet_driver, leased)",
      "Navigate to appropriate dashboard with role-based features"
    ],
    "role_based_navigation": {
      "client_regular": "Load RegularClientApp()",
      "client_vip": "Load BlackTierClientApp()",
      "client_vip_premiun": "Load BlackTierClientApp() with hotel module",
      "driver_independent": "Load IndependentDriverApp()",
      "driver_fleet_owner": "Load FleetOwnerApp()",
      "driver_fleet_driver": "Load FleetDriverApp()",
      "driver_leased": "Load LeasedDriverApp()"
    }
  },
  "dependencies": [
    "provider or riverpod for state management",
    "dio or http for API calls",
    "shared_preferences or secure_storage for JWT",
    "flutter_map for OpenStreetMap integration",
    "latlong2 for geo-coordinates",
    "socket.io-client for real-time ride updates",
    "flutter_stripe or pay for payments",
    "intl for formatting dates/currency",
    "charts_flutter or fl_chart for earnings visualization"
  },
  "ui_design": {
    "theme": "modern, minimal, dark/light mode",
    "components": [
      "Bottom navigation bar for clients",
      "Drawer/sidebar for drivers",
      "OpenStreetMap with live ride tracking and navigation",
      "Hotel module for Black-Tier users (partner hotels, booking, perks)",
      "Ride booking forms",
      "Payments UI (wallet, card, receipts)",
      "Ride cards (history, receipts, upcoming rides)",
      "Fleet management dashboard",
      "Lease contract viewer",
      "Earnings charts (drivers and fleet)",
      "SOS button with escalation logic per role"
    ]
  },
  "build_steps": [
    "Setup Flutter project",
    "Configure API base URL + auth service",
    "Implement login/signup/logout with JWT",
    "Create unified role-based navigation for clients and drivers",
    "Build Regular client screens",
    "Build VIP client screens",
    "Build Black-Tier client screens (hotel module, encrypted tracking, advanced SOS)",
    "Build Independent Driver screens",
    "Build Fleet Owner screens (management, earnings, reports)",
    "Build Fleet Driver screens",
    "Build Leased Driver screens (lease terms, revenue split)",
    "Integrate OpenStreetMap with flutter_map",
    "Add real-time ride updates with socket.io",
    "Integrate payments system",
    "Build earnings dashboards with charts",
    "Test end-to-end with Django backend"
  ]
}
