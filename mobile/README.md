# VIP Ride-Hailing Flutter Mobile App

A comprehensive Flutter mobile application for the VIP ride-hailing platform supporting multiple user types and tiers.

## Project Structure

```
mobile/
├── lib/
│   ├── config/           # App configuration and themes
│   │   ├── api_config.dart
│   │   └── theme.dart
│   ├── models/           # Data models
│   │   ├── user_model.dart
│   │   ├── ride_model.dart
│   │   ├── location_model.dart
│   │   ├── vehicle_model.dart
│   │   └── driver_model.dart
│   ├── services/         # API and business logic
│   │   ├── api_service.dart
│   │   └── auth_provider.dart
│   ├── screens/          # UI screens organized by user type
│   │   ├── auth/         # Login/Register screens
│   │   ├── client/       # Client apps by tier
│   │   │   ├── regular/
│   │   │   ├── vip/
│   │   │   └── black_tier/
│   │   └── driver/       # Driver apps by type
│   │       ├── independent/
│   │       ├── fleet_owner/
│   │       ├── fleet_driver/
│   │       └── leased/
│   └── main.dart         # App entry point
├── assets/               # Static assets
├── android/              # Android-specific files
├── ios/                  # iOS-specific files
├── web/                  # Web-specific files
└── pubspec.yaml          # Dependencies and configuration
```

## Features Implemented

### Authentication System
- User registration and login
- JWT token management
- Role-based authentication
- Secure token storage

### Multi-Tier Client Support
- **Regular Clients**: Standard ride booking
- **VIP Clients**: Premium services with enhanced features
- **Black-Tier Clients**: Luxury services with exclusive access

### Multi-Type Driver Support
- **Independent Drivers**: Solo drivers with personal vehicles
- **Fleet Owners**: Manage multiple vehicles and drivers
- **Fleet Drivers**: Employed by fleet companies
- **Leased Drivers**: Use leased vehicles from platform

### Core Features
- Real-time GPS tracking
- In-app payments (Stripe integration)
- Push notifications
- Role-based navigation
- Material Design 3 UI
- Dark/Light theme support
- Offline capability

## Tech Stack
- **Flutter 3.35.3** - UI framework
- **Dart SDK 3.9.0** - Programming language
- **Provider** - State management
- **Dio** - HTTP client for API calls
- **Flutter Secure Storage** - Token storage
- **Flutter Map + OpenStreetMap** - Maps without Google dependency
- **Socket.IO Client** - Real-time communication
- **Flutter Stripe** - Payment processing
- **Flutter Local Notifications** - Push notifications
## Development Setup

### Prerequisites
- Flutter SDK 3.35.3 or later
- Dart SDK 3.9.0 or later
- Android Studio / VS Code with Flutter extension
- Chrome browser for web testing

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd vip_ride_platform/mobile
   ```

2. **Install dependencies:**
   ```bash
   flutter pub get
   ```

3. **Run code generation (if needed):**
   ```bash
   flutter pub run build_runner build
   ```

4. **Run the app:**
   ```bash
   # Web (Chrome)
   flutter run -d chrome --release
   
   # Android device/emulator
   flutter run -d android
   
   # iOS simulator (macOS only)
   flutter run -d ios
   ```

### Development Commands

- **Hot Reload**: Press `r` while app is running
- **Hot Restart**: Press `R` while app is running
- **Clean build**: `flutter clean && flutter pub get`
- **Analyze code**: `flutter analyze`
- **Run tests**: `flutter test`

## API Integration

### Backend Configuration
The app connects to the Django backend via REST API:

- **Base URL**: `http://127.0.0.1:8001/api/v1/`
- **Authentication**: JWT tokens (Bearer authentication)
- **WebSocket URL**: `ws://127.0.0.1:8001/ws/`

### API Endpoints Used
- `POST /auth/login/` - User authentication
- `POST /auth/register/` - User registration  
- `GET /auth/user/` - Get user profile
- `POST /rides/request/` - Request a ride
- `GET /rides/` - List user rides
- `WebSocket /ws/gps/` - Real-time GPS tracking

### Configuration Files
- `lib/config/api_config.dart` - API endpoints and constants
- `lib/services/api_service.dart` - HTTP client with JWT handling

## User Types & Navigation

### Client Tiers
1. **Regular (NORMAL)**: Basic ride services
2. **VIP (PREMIUM)**: Enhanced services + hotel booking
3. **Black-Tier (VIP)**: Luxury services + encrypted GPS + SOS

### Driver Types  
1. **Independent Driver**: Personal vehicle, flexible schedule
2. **Fleet Owner**: Manage multiple vehicles and drivers
3. **Fleet Driver**: Employee of fleet company
4. **Leased Driver**: Use platform-provided vehicles

## Troubleshooting

### Common Issues

1. **"Something went wrong" on login/signup**:
   - Check Django backend is running on `http://127.0.0.1:8001`
   - Verify API endpoints in `api_config.dart`
   - Check browser console for network errors

2. **Dependencies issues**:
   ```bash
   flutter clean
   flutter pub get
   flutter pub upgrade
   ```

3. **Build errors**:
   ```bash
   flutter clean
   rm -rf .dart_tool
   flutter pub get
   flutter pub run build_runner clean
   flutter pub run build_runner build
   ```

### Debugging
- Enable browser developer tools for network inspection
- Check Flutter logs in terminal while app is running
- Use `debugPrint()` statements for debugging

## Contributing

1. Create feature branch from `main`
2. Follow Flutter/Dart style conventions
3. Add tests for new features
4. Update documentation as needed
5. Submit pull request for review
