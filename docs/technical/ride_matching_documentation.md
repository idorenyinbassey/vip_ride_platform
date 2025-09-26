# Ride Matching Algorithm Documentation

## Overview

The VIP Ride-Hailing Platform uses a sophisticated multi-tier ride matching algorithm that considers user tiers, vehicle types, distance, driver preferences, surge pricing, and availability status to provide optimal driver-rider matches.

## Core Features

### 1. Tier-Based Matching
- **Normal Tier**: Matched with any available driver
- **Premium Tier**: Requires Premium or VIP subscription drivers with suitable vehicles
- **VIP Tier**: Priority matching with VIP drivers, encrypted GPS tracking, trusted driver preferences

### 2. Distance-Based Optimization
- Haversine distance calculation for accurate GPS-based matching
- Dynamic search radius based on customer tier (Normal: 20km, VIP: 50km)
- Optimized for minimum driver travel time and customer wait time

### 3. Vehicle Type Consideration
- **Standard Vehicles**: For normal rides
- **Premium/Classic Vehicles**: For premium tier customers
- **Luxury Vehicles**: Priority for VIP customers
- Special requirements: baby seats, wheelchair access, premium features

### 4. VIP Trusted Driver System
- Customer-driver relationship tracking
- Bonus scoring for previously successful VIP rides
- Preferred driver selection for repeat customers

### 5. Dynamic Surge Pricing
- Real-time demand/supply ratio calculation
- Geographic surge zones with configurable multipliers
- Tier-based surge limits (VIP: 2.0x max, Premium: 2.5x max)
- Special event and time-based surge activation

### 6. Driver Availability Management
- Real-time online/offline status tracking
- Location update frequency monitoring
- Subscription tier verification
- Completion rate and rating considerations

## Algorithm Components

### Scoring System

The matching algorithm uses a weighted scoring system:

```
Total Score = (Distance Score × 0.3) + 
              (Tier Match Score × 0.25) + 
              (Vehicle Match Score × 0.2) + 
              (Rating Score × 0.15) + 
              (Availability Score × 0.1) + 
              Bonus Scores
```

#### Distance Score
- Closer drivers score higher
- Formula: `max(0, (max_radius - distance) / max_radius)`
- Encourages shorter pickup times

#### Tier Match Score
- VIP driver serving VIP customer: 1.0
- Premium driver serving VIP customer: 0.8
- Premium driver serving Premium customer: 1.0
- Basic driver serving Premium/VIP: 0.0 (not allowed)

#### Vehicle Match Score
- Base score: 0.5
- Premium/Luxury vehicle for VIP: +0.4
- Premium/Classic vehicle for Premium: +0.3
- Special requirements match: +0.2 each

#### Rating Score
- Driver rating normalized to 0-1 scale
- Formula: `rating / 5.0`

#### Availability Score
- Recent location update: +0.3 (< 5 min), +0.2 (< 15 min)
- High completion rate (≥95%): +0.2, (≥85%): +0.1

#### Bonus Scores
- VIP trusted driver: +0.1 to +0.3 based on history
- Fleet company driver: +0.05 to +0.15 based on tier

### Surge Pricing Logic

#### Dynamic Surge Calculation
1. **Demand Analysis**: Count ride requests in 30-minute window within 3km radius
2. **Supply Analysis**: Count available drivers in same area
3. **Ratio Calculation**: `demand_supply_ratio = rides / drivers`
4. **Surge Multiplier**:
   - Ratio ≥ 2.0: 2.5x surge
   - Ratio ≥ 1.5: 2.0x surge
   - Ratio ≥ 1.0: 1.5x surge
   - Ratio ≥ 0.7: 1.3x surge
   - Ratio < 0.7: 1.0x surge

#### Predefined Surge Zones
- Airport zones: 1.5x multiplier
- Business districts: 1.2-1.3x multiplier
- Event locations: Custom multipliers
- Time-based activation (rush hours, weekends)

## API Endpoints

### Customer Endpoints

#### Request Ride
```http
POST /api/rides/matching/request_ride/
```

**Request Body:**
```json
{
    "ride_type": "normal",
    "pickup_address": "123 Main St",
    "pickup_latitude": 6.5244,
    "pickup_longitude": 3.3792,
    "destination_address": "456 Oak Ave",
    "destination_latitude": 6.5300,
    "destination_longitude": 3.3900,
    "requires_baby_seat": false,
    "requires_wheelchair_access": false,
    "requires_premium_vehicle": false,
    "preferred_driver_id": "uuid",
    "passenger_count": 1,
    "special_instructions": "Please call when arrived"
}
```

**Response:**
```json
{
    "ride_id": "uuid",
    "status": "matching_started",
    "matching_result": {
        "success": true,
        "drivers_found": 3,
        "offers_created": 3,
        "surge_multiplier": 1.2,
        "driver_scores": [...]
    },
    "estimated_matching_time": "2-5 minutes"
}
```

#### Get Ride Status
```http
GET /api/rides/matching/{ride_id}/ride_status/
```

#### Cancel Ride
```http
POST /api/rides/matching/cancel_ride/
```

### Driver Endpoints

#### Respond to Offer
```http
POST /api/rides/matching/driver_response/
```

**Request Body:**
```json
{
    "offer_id": "uuid",
    "accepted": true,
    "estimated_arrival_minutes": 8,
    "current_latitude": 6.5244,
    "current_longitude": 3.3792
}
```

#### Get Active Offers
```http
GET /api/rides/matching/active_offers/
```

#### Update Driver Status
```http
PATCH /api/rides/matching/driver_status/
```

**Request Body:**
```json
{
    "is_available": true,
    "current_location": {
        "latitude": 6.5244,
        "longitude": 3.3792
    }
}
```

### Admin Endpoints

#### Get Surge Zones
```http
GET /api/rides/matching/surge_zones/
```

#### Get Matching Statistics
```http
GET /api/rides/matching/matching_stats/
```

## Database Models

### RideOffer
Tracks ride offers sent to drivers:
- Offer status (pending, accepted, rejected, expired)
- Estimated arrival time
- Driver location at offer time
- Expiration timestamp
- Surge multiplier at time of offer

### SurgeZone
Manages geographic surge pricing areas:
- Center coordinates and radius
- Surge multiplier and activation conditions
- Time-based activation schedules
- Demand thresholds for automatic activation

### RideMatchingLog
Analytics and debugging data:
- Search parameters and results
- Driver counts and eligibility
- Match success/failure tracking
- Performance metrics

### DriverPreference
Driver-specific matching preferences:
- Geographic preferences (pickup areas, avoided zones)
- Ride type preferences (airport, long-distance, night rides)
- Customer preferences (VIP only, familiar customers)
- Working schedule preferences

### CustomerPreference
Customer-specific matching preferences:
- Preferred and blocked drivers
- Vehicle type preferences
- Service requirements (non-smoking, AC, special needs)
- Price sensitivity settings

## Setup Instructions

### 1. Run Database Migrations
```bash
python manage.py makemigrations rides
python manage.py migrate
```

### 2. Initialize Matching System
```bash
python manage.py init_matching --setup-surge-zones
```

### 3. Add URL Configuration
In your main `urls.py`:
```python
from django.urls import path, include

urlpatterns = [
    # ... other patterns
    path('api/rides/', include('rides.matching_urls')),
]
```

### 4. Configure Settings
Add to `settings.py`:
```python
# Ride Matching Configuration
RIDE_MATCHING = {
    'MAX_SEARCH_RADIUS_KM': 20.0,
    'VIP_SEARCH_RADIUS_KM': 50.0,
    'OFFER_TIMEOUT_MINUTES': 2,
    'MAX_DRIVERS_PER_REQUEST': 5,
    'ENABLE_SURGE_PRICING': True,
    'VIP_SURGE_LIMIT': 2.0,
    'PREMIUM_SURGE_LIMIT': 2.5,
}
```

## Testing

### Run Matching Tests
```bash
python manage.py test rides.test_matching
```

### Test Coverage Areas
- Distance calculation accuracy
- Tier-based matching logic
- Vehicle compatibility scoring
- Surge pricing calculations
- Driver eligibility verification
- API endpoint functionality
- Database model relationships

## Performance Considerations

### Optimization Strategies
1. **Database Indexing**: Location-based queries are indexed
2. **Caching**: Surge zones and driver locations cached in Redis
3. **Async Processing**: Notifications sent asynchronously
4. **Connection Pooling**: Database connections optimized
5. **Query Optimization**: Prefetch related objects to reduce N+1 queries

### Scalability Features
- Horizontal scaling with load balancers
- Database sharding by geographic regions
- Microservice architecture ready
- Event-driven notifications
- Real-time WebSocket updates

## Monitoring and Analytics

### Key Metrics Tracked
- Match success rate by tier
- Average matching time
- Driver utilization rates
- Customer satisfaction scores
- Surge pricing effectiveness
- Geographic distribution analysis

### Monitoring Tools
- Match success/failure logging
- Performance metrics collection
- Real-time dashboard integration
- Alert system for low match rates
- Driver availability monitoring

## Security Considerations

### VIP Data Protection
- GPS coordinates encrypted with AES-256-GCM
- Restricted access to VIP customer data
- Audit logging for all VIP rides
- Trusted driver verification process

### API Security
- JWT authentication required
- Role-based access control
- Rate limiting on matching requests
- Input validation and sanitization
- HTTPS encryption for all communications

## Future Enhancements

### Planned Features
1. **Machine Learning Integration**: Predictive demand modeling
2. **Route Optimization**: Multi-stop ride planning
3. **Shared Rides**: Algorithm for ride sharing matches
4. **Dynamic Pricing**: AI-driven surge adjustments
5. **Driver Behavior Analysis**: Performance-based scoring
6. **Real-time Traffic Integration**: ETA adjustments
7. **Weather-based Adjustments**: Demand prediction
8. **Fleet Optimization**: Corporate account management

### API Evolution
- GraphQL endpoint support
- WebSocket real-time updates
- Mobile SDK development
- Third-party integration APIs
- Analytics API for dashboards
