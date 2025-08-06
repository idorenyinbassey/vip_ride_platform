# VIP Ride-Hailing Platform

A comprehensive enterprise-grade ride-hailing platform with multi-tier user system, GPS tracking, and VIP security features built with Django 5.2.5 and React Native.

## 🚀 Project Overview

This is a sophisticated ride-hailing platform designed for the Nigerian market with three distinct user tiers:
- **Normal**: Standard rides (15-20% commission)
- **Premium**: Luxury cars + hotel booking (20-25% commission)  
- **VIP**: Encrypted GPS, SOS, trusted drivers (25-30% commission)

## 🏗️ Architecture

- **Backend**: Django 5.2.5 + Django REST Framework 3.16.0
- **Database**: PostgreSQL + Redis for caching
- **Mobile**: React Native 0.80.2 with TypeScript
- **Security**: AES-256-GCM encryption for VIP GPS tracking
- **Compliance**: NDPR (Nigeria Data Protection Regulation)
- **Real-time**: WebSocket support via Django Channels
- **Background Tasks**: Celery for async processing

## 📱 User Tiers & Features

### Normal Tier
- Standard ride booking
- Basic GPS tracking
- Standard customer support
- 15-20% commission

### Premium Tier
- Luxury vehicle access
- Hotel booking integration
- Priority customer support
- Enhanced GPS tracking
- 20-25% commission

### VIP Tier
- Military-grade GPS encryption (AES-256-GCM)
- SOS emergency protocols
- Trusted verified drivers only
- Control center monitoring
- Real-time location encryption
- Emergency response team
- 25-30% commission

## 🚗 Driver & Vehicle Categories

### 1. Private Drivers with Classic Cars
- Flexible billing by engine type (V6/V8/4-stroke)
- Individual driver verification
- Personal vehicle registration

### 2. Fleet Companies with Premium Cars/Vans
- Fixed billing rates
- Priority VIP allocation
- Bulk driver management
- Fleet tracking and analytics

### 3. Vehicle Owners
- Lease cars to fleet companies
- Revenue-sharing contracts
- Vehicle maintenance tracking

## 🔐 Security Features

- **JWT Authentication**: Secure API access
- **Role-Based Permissions**: Multi-level access control
- **GPS Encryption**: AES-256-GCM for VIP users
- **Payment Security**: Secure payment processing
- **Data Anonymization**: NDPR compliance
- **Rate Limiting**: API protection
- **Input Validation**: SQL injection prevention

## 🗄️ Database Design

- **PostgreSQL**: Primary database with proper indexing
- **Redis**: Caching and real-time features
- **Soft Deletes**: Audit trail maintenance
- **UUID**: Sensitive ID protection
- **Migration Management**: Version control for schema

## 📊 Key Components

### GPS Tracking System
- Real-time location tracking
- Geofencing capabilities
- Route optimization
- Offline GPS buffering
- VIP location encryption
- Emergency SOS integration

### Control Center
- VIP monitoring dashboard
- Emergency response protocols
- Driver verification system
- Fleet management interface

### Payment Processing
- Multi-gateway support
- Commission calculation
- Driver payouts
- Revenue analytics

### Hotel Integration
- Partner hotel booking
- Premium user benefits
- Revenue sharing

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/idorenyinbassey/vip_ride_platform.git
   cd vip_ride_platform
   ```

2. **Set up Python virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment setup**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Database setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

## 🔧 Configuration

### Environment Variables
- `DEBUG`: Development mode toggle
- `SECRET_KEY`: Django secret key
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis server URL
- `GOOGLE_MAPS_API_KEY`: For route optimization
- `VIP_ENCRYPTION_KEY`: For VIP GPS encryption
- `PAYSTACK_SECRET_KEY`: Payment processing

### Driver Subscriptions
- **Basic**: $99/month (Normal tier access)
- **Premium**: $199/month (Normal + Premium tier access)
- **VIP**: $299/month (All tier access + priority allocation)

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Test GPS tracking system
python test_gps_system.py

# Test JWT authentication
python test_jwt_system.py

# Test RBAC middleware
python test_rbac_middleware.py

# Django tests
python manage.py test
```

## 📱 Mobile App Structure

```
mobile/
├── android/
├── ios/
├── src/
│   ├── components/
│   ├── screens/
│   ├── navigation/
│   ├── services/
│   └── utils/
└── package.json
```

## 🏢 Fleet Management

### Revenue Sharing Models
- **Vehicle Owners**: 60-70% of ride revenue
- **Fleet Companies**: 20-30% management fee
- **Platform**: 15-30% commission (tier-based)

### Driver Verification Levels
- **Level 1**: Basic background check
- **Level 2**: Enhanced verification + training
- **Level 3**: VIP clearance + ongoing monitoring

## 📈 Analytics & Monitoring

- Real-time ride analytics
- Driver performance metrics
- Revenue tracking and reporting
- GPS tracking analytics
- Emergency response metrics

## 🔒 NDPR Compliance

- Data minimization principles
- User consent management
- Data anonymization
- Right to deletion
- Privacy by design

## 🚨 Emergency Protocols

### SOS System
- One-touch emergency button
- Automatic location sharing
- Control center alerts
- Emergency contact notification
- Police/medical service integration

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is proprietary software. All rights reserved.

## 📞 Support

For technical support and business inquiries:
- Email: support@vipride.ng
- Phone: +234-XXX-XXX-XXXX
- Website: https://vipride.ng

## 🔄 Version History

- **v1.0.0**: Initial release with basic ride-hailing features
- **v1.1.0**: Added VIP tier with GPS encryption
- **v1.2.0**: Hotel integration and premium features
- **v1.3.0**: Fleet management system
- **v1.4.0**: Control center and emergency protocols

---

Built with ❤️ in Nigeria for the Nigerian market
