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
