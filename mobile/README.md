# VIP Ride-Hailing Mobile App

This directory will contain the React Native mobile applications for the VIP ride-hailing platform.

## Planned Structure

```
mobile/
├── customer-app/          # Customer mobile app
├── driver-app/           # Driver mobile app
├── fleet-manager-app/    # Fleet manager app
└── shared/              # Shared components and utilities
```

## Features to Implement

### Customer App
- User registration and authentication
- Ride booking with tier selection
- Real-time ride tracking
- In-app payments
- Hotel booking integration
- Emergency SOS (VIP users)
- Rating and reviews

### Driver App
- Driver registration and verification
- Ride acceptance and navigation
- Earnings tracking
- Vehicle management
- Subscription management
- Fleet integration

### Fleet Manager App
- Fleet vehicle management
- Driver assignment
- Performance analytics
- Revenue tracking
- Maintenance scheduling

## Tech Stack
- React Native 0.80.2
- TypeScript
- React Navigation
- Redux Toolkit
- RTK Query for API calls
- React Native Maps
- Push notifications
- Offline storage

## Development Setup

Instructions will be added when mobile development begins.

## API Integration

All mobile apps will connect to the Django backend via REST API endpoints:
- Base URL: `http://localhost:8000/api/v1/`
- Authentication: JWT tokens
- Real-time features: WebSocket connections
