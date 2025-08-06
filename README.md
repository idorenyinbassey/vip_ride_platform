# VIP Ride-Hailing Platform

A comprehensive ride-hailing platform with multi-tier user system, fleet management, hotel partnerships, and advanced security features for VIP users.

## Features

### User Tiers
- **Normal**: Standard rides (15-20% commission)
- **Premium**: Luxury cars + hotel booking (20-25% commission)
- **VIP**: Encrypted GPS, SOS protocols, trusted drivers (25-30% commission)

### Driver & Vehicle Categories
1. **Private Drivers with Classic Cars**: Flexible billing by engine type (V6/V8/4-stroke)
2. **Fleet Companies with Premium Cars/Vans**: Fixed billing rates, priority VIP allocation
3. **Vehicle Owners**: Lease cars to fleet companies with revenue-sharing contracts

### Key Features
- Multi-tier driver verification system
- AES-256-GCM encryption for VIP GPS tracking
- SOS emergency protocols with real-time monitoring
- Hotel partnership integration
- Control Center for VIP monitoring
- Fleet management system
- Vehicle leasing marketplace
- NDPR (Nigeria Data Protection Regulation) compliance

## Tech Stack

- **Backend**: Django 5.2.5 + Django REST Framework 3.16.0
- **Database**: PostgreSQL + Redis
- **Mobile**: React Native 0.80.2 (to be developed)
- **Security**: AES-256-GCM encryption, JWT authentication
- **Task Queue**: Celery with Redis broker
- **Compliance**: NDPR data protection standards

## Project Structure

```
vip_ride_platform/
├── accounts/           # User management and authentication
├── rides/             # Ride booking and tracking
├── fleet_management/  # Vehicle and fleet management
├── vehicle_leasing/   # Vehicle leasing marketplace
├── hotels/           # Hotel partnership integration
├── payments/         # Payment processing
├── notifications/    # Notification system
├── control_center/   # VIP monitoring and emergency response
└── vip_ride_platform/ # Main project settings
```

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "RIDE HAILING APP"
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # Windows
   # or
   source venv/bin/activate      # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration
   ```

5. **Database Setup**
   ```bash
   # Create PostgreSQL database
   createdb vip_ride_platform
   
   # Run migrations
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start Redis Server**
   ```bash
   redis-server
   ```

8. **Start Celery Worker**
   ```bash
   celery -A vip_ride_platform worker --loglevel=info
   ```

9. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

## API Documentation

The API documentation will be available at `/api/docs/` when the server is running.

## Driver Subscriptions

- **Basic ($99/month)**: Access to Normal tier rides
- **Premium ($199/month)**: Access to Normal + Premium tier rides
- **VIP ($299/month)**: Access to all ride tiers with priority allocation

## Commission Structure

- **Normal Rides**: 15-20% platform commission
- **Premium Rides**: 20-25% platform commission
- **VIP Rides**: 25-30% platform commission

## Security Features

### VIP GPS Encryption
- Real-time location data encrypted using AES-256-GCM
- Secure transmission and storage of sensitive location data
- Access controlled by user tier and permissions

### SOS Emergency Protocol
- Immediate alert system for VIP users
- Real-time location sharing with emergency contacts
- Control center monitoring and response

### Data Protection (NDPR Compliance)
- User consent management
- Data anonymization and retention policies
- Right to data portability and deletion
- Transparent privacy controls

## Development

### Running Tests
```bash
python manage.py test
```

### Code Quality
```bash
# Run linting
flake8 .

# Run type checking
mypy .
```

### Database Migrations
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

## Deployment

### Production Settings
1. Set `DEBUG=False` in environment
2. Configure secure database credentials
3. Set up SSL/TLS certificates
4. Configure static file serving
5. Set up monitoring and logging

### Environment Variables
See `.env.example` for required environment variables.

## Mobile App Development

The React Native mobile app will be developed separately with the following features:
- Cross-platform iOS and Android support
- Real-time GPS tracking
- In-app payments
- Push notifications
- Offline capability for critical features

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is proprietary and confidential.

## Support

For technical support or questions about the platform, please contact the development team.
