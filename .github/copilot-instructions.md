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
    "api_endpoints": {
      "login": "/api/auth/login/",
      "signup": "/api/auth/signup/",
      "profile": "/api/users/profile/",
      "rides": "/api/rides/",
      "vehicles": "/api/vehicles/",
      "fleet": "/api/fleet/",
      "fleet_drivers": "/api/fleet/drivers/",
      "lease": "/api/lease/",
      "earnings": "/api/drivers/earnings/",
      "hotels": "/api/hotels/",
      "hotel_bookings": "/api/hotels/bookings/",
      "payments": "/api/payments/",
      "sos": "/api/security/sos/"
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
