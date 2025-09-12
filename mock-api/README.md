# VIP Ride Platform - Mock API Server

This is a comprehensive mock API server that mimics all the Django backend endpoints needed for testing the Flutter mobile application.

## Features

🔐 **Authentication & Authorization**
- JWT-based login/register
- Session and device tracking
- Multi-factor authentication (MFA) setup

👥 **User Management**
- Multiple user tiers (Regular, VIP, VIP Premium)
- Profile management
- Tier status endpoint

🎫 **Card Activation**
- Digital card activation with tier upgrades
- Realistic activation flow
- Automatic user tier promotion

🚗 **Ride Management**
- Ride booking and status tracking
- Priority handling for VIP users
- Active ride monitoring

🏨 **Hotel Partnerships** (VIP Premium only)
- Nearby hotels listing
- VIP perks and amenities

🔒 **Security Features**
- Password hashing with bcrypt
- JWT token validation
- Device fingerprinting

## Installation & Setup

### Prerequisites
- Node.js 16+ installed
- npm or yarn package manager

### Quick Start

1. **Install dependencies:**
```bash
cd mock-api
npm install
```

2. **Start the server:**
```bash
npm start
```

3. **For development (auto-restart):**
```bash
npm run dev
```

The server will start on `http://localhost:8000`

## Test Data

### Test Users

| Email | Password | Tier | Features |
|-------|----------|------|----------|
| `admin@email.com` | `password` | Regular | Basic ride booking |
| `vip@email.com` | `password` | VIP | Priority matching, premium vehicles |
| `premium@email.com` | `password` | VIP Premium | All VIP + hotels, encryption, concierge |

### Test Cards for Activation

| Card Number | Verification Code | Upgrades To |
|-------------|------------------|-------------|
| `TEST-1234-5678-9012` | `TEST123` | VIP |
| `PREM-2345-6789-0123` | `PREM456` | VIP Premium |

## API Endpoints

### Authentication
- `POST /api/v1/accounts/login/` - User login with device registration
- `POST /api/v1/accounts/register/` - User registration
- `GET /api/v1/accounts/profile/` - Get user profile (legacy)
- `GET /api/v1/accounts/flutter/tier-status/` - **Enhanced tier status endpoint**

### Card Management
- `POST /api/v1/accounts/flutter/activate-card/` - **Activate digital cards**

### Ride Management
- `POST /api/v1/rides/workflow/request/` - Request a ride
- `GET /api/v1/rides/workflow/active/` - Get active rides

### Hotel Partnerships (VIP Premium only)
- `GET /api/v1/hotel-partnerships/hotels/nearby/` - Get nearby partner hotels

### MFA (Multi-Factor Authentication)
- `POST /api/v1/accounts/auth/mfa/setup/` - Setup MFA
- `POST /api/v1/accounts/auth/mfa/verify/` - Verify MFA token

### Admin/Debug Endpoints
- `GET /health/` - Health check
- `GET /mock/admin/sessions` - View all user sessions
- `GET /mock/admin/devices` - View all trusted devices
- `GET /mock/admin/users` - View all users

## Testing the Flutter App

### 1. Update Flutter API Configuration

In your Flutter app, update the API base URL to point to the mock server:

```dart
// mobile/lib/config/api_config.dart
class ApiConfig {
  static const String baseUrl = 'http://localhost:8000'; // Mock API
  static const String apiVersion = 'v1';
  // ... rest of config
}
```

### 2. Test Authentication Flow

1. **Login Test:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/accounts/login/ \
     -H "Content-Type: application/json" \
     -d '{
       "email": "admin@email.com",
       "password": "password",
       "device_name": "Test Device",
       "device_type": "mobile",
       "device_os": "android"
     }'
   ```

2. **Tier Status Test:**
   ```bash
   curl -X GET http://localhost:8000/api/v1/accounts/flutter/tier-status/ \
     -H "Authorization: Bearer YOUR_TOKEN_HERE"
   ```

### 3. Test Card Activation

```bash
curl -X POST http://localhost:8000/api/v1/accounts/flutter/activate-card/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "card_number": "TEST-1234-5678-9012",
    "verification_code": "TEST123",
    "device_name": "Flutter App"
  }'
```

### 4. Verify Session/Device Tracking

Check if sessions and devices are being tracked:

```bash
# View registered sessions
curl http://localhost:8000/mock/admin/sessions

# View trusted devices
curl http://localhost:8000/mock/admin/devices

# View all users
curl http://localhost:8000/mock/admin/users
```

## Flutter Integration Testing

### Step 1: Update API Config in Flutter

```dart
// mobile/lib/config/api_config.dart
class ApiConfig {
  static const bool useMockApi = true; // Toggle for mock vs real API
  static const String mockApiUrl = 'http://localhost:8000';
  static const String realApiUrl = 'https://your-production-api.com';
  
  static String get baseUrl => useMockApi ? mockApiUrl : realApiUrl;
}
```

### Step 2: Test Complete Flow

1. **Start Mock Server:**
   ```bash
   cd mock-api && npm start
   ```

2. **Run Flutter App:**
   ```bash
   cd mobile && flutter run
   ```

3. **Test Scenarios:**
   - Login with test users
   - Check tier routing (Regular → VIP → VIP Premium)
   - Activate test cards
   - Verify session tracking in mock admin endpoints
   - Test ride booking flow
   - Test hotel partnerships (VIP Premium only)

## Mock Data Responses

### User Tier Status Response
```json
{
  "user": {
    "id": "user-1",
    "tier": "vip_premium",
    "tier_display": "VIP Premium"
  },
  "tier_info": {
    "benefits": ["Priority ride matching", "Luxury vehicles", "Hotel partnerships"],
    "features": ["hotel_booking", "encrypted_tracking", "vip_support"]
  },
  "premium_cards": [...],
  "device_status": {
    "device_id": "device-123",
    "is_registered": true
  },
  "session_status": {
    "session_id": "session-456",
    "is_active": true
  }
}
```

### Card Activation Response
```json
{
  "success": true,
  "message": "Card activated successfully! Upgraded from regular to vip",
  "card": {...},
  "user": {
    "tier": "vip",
    "tier_display": "VIP"
  },
  "next_steps": {
    "requires_mfa_setup": false,
    "should_refresh_session": true,
    "redirect_to": "vip_dashboard"
  }
}
```

## Development Features

- **Real JWT tokens** - Proper authentication simulation
- **Password hashing** - Secure password handling with bcrypt
- **Session persistence** - Sessions maintained in memory during server runtime
- **Device tracking** - Unique device IDs and fingerprinting
- **Tier progression** - Realistic user tier upgrades
- **Error handling** - Proper HTTP status codes and error messages
- **CORS enabled** - Cross-origin requests allowed for Flutter testing

## Production Notes

⚠️ **This is for testing only!**

- Data is stored in memory (resets on server restart)
- Uses simple JWT secret (not secure for production)
- No database persistence
- Mock MFA implementation
- Simplified authentication logic

For production, use the real Django backend with proper database, security, and authentication systems.

## Troubleshooting

### Common Issues

1. **CORS errors:** Make sure the server is running and CORS is enabled
2. **Connection refused:** Check if the server is running on port 8000
3. **Token errors:** Use fresh tokens from login endpoint
4. **Flutter network issues:** Ensure Android emulator/iOS simulator can reach localhost

### Debug Endpoints

- **Health Check:** `GET /health/` - Verify server is running
- **Session Debug:** `GET /mock/admin/sessions` - See all active sessions
- **Device Debug:** `GET /mock/admin/devices` - See all registered devices
- **User Debug:** `GET /mock/admin/users` - See all users and their tiers

## Next Steps

Once the Flutter app is working with the mock API, you can:

1. Switch back to the real Django backend by changing `useMockApi` to `false`
2. Deploy both mobile app and backend to production
3. Use this mock API for automated testing and CI/CD
4. Extend mock data for more comprehensive testing scenarios