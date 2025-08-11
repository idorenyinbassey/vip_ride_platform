# Development Guide - VIP Ride-Hailing Platform

## 🚀 Getting Started

### 1. Environment Setup
```bash
# Navigate to project directory
cd "c:\Users\Frankie_PC\Desktop\RIDE HAILING APP"

# Activate virtual environment
source venv/Scripts/activate

# Install dependencies (if not already done)
pip install -r requirements.txt
```

### 2. Database Configuration

#### Option A: SQLite (Development Only)
Update `vip_ride_platform/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

#### Option B: PostgreSQL (Recommended)
1. Install PostgreSQL
2. Create database:
   ```sql
   CREATE DATABASE vip_ride_platform;
   CREATE USER vip_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE vip_ride_platform TO vip_user;
   ```
3. Update `.env` file with database credentials

### 3. Run Migrations
```bash
python manage.py migrate
```

### 4. Create Superuser
```bash
python manage.py createsuperuser
```

### 5. Start Development Server
```bash
python manage.py runserver
```

## 📁 Project Structure Guide

### Core Django Apps

#### `accounts/` - User Management
- **Models**: User, UserProfile, DriverProfile
- **Purpose**: Authentication, user tiers, driver verification
- **Key Features**: Multi-tier users, NDPR compliance, driver subscriptions

#### `rides/` - Ride Operations
- **Models**: Ride, RideTracking, RideRating, RideOffer, EmergencyContact
- **Purpose**: Core ride booking and tracking functionality
- **Key Features**: GPS encryption for VIP, SOS emergency system

#### `fleet_management/` - Vehicle Operations
- **Models**: Vehicle, FleetCompany, FleetVehicle, VehicleLeaseContract
- **Purpose**: Vehicle and fleet management
- **Key Features**: Multi-category vehicles, fleet partnerships

#### `hotels/` - Partnership Integration
- **Models**: HotelPartner, RoomType, HotelBooking, HotelReview
- **Purpose**: Hotel booking integration for Premium/VIP users
- **Key Features**: Partner management, booking system

## 🔧 Development Workflow

### 1. Adding New Features

#### Step 1: Model Changes
```bash
# After modifying models
python manage.py makemigrations app_name
python manage.py migrate
```

#### Step 2: Create Views
```python
# Example: accounts/views.py
from rest_framework import viewsets
from .models import User
from .serializers import UserSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
```

#### Step 3: Add Serializers
```python
# Example: accounts/serializers.py
from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'tier']
```

#### Step 4: Configure URLs
```python
# Example: accounts/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
```

### 2. Testing

#### Run Tests
```bash
python manage.py test
```

#### Create Test Files
```python
# Example: accounts/tests.py
from django.test import TestCase
from .models import User

class UserModelTest(TestCase):
    def test_user_creation(self):
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(user.email, 'test@example.com')
```

## 🏗️ API Development Priority

### Phase 1: Core Authentication
1. User registration/login
2. JWT token management
3. User profile management
4. Driver application system

### Phase 2: Ride System
1. Ride request/booking
2. Driver matching
3. Real-time tracking
4. Fare calculation

### Phase 3: Fleet Management
1. Vehicle registration
2. Fleet company management
3. Driver-vehicle assignments

### Phase 4: Additional Features
1. Hotel booking integration
2. Payment processing
3. Notification system
4. Emergency response

## 📱 Mobile Development Setup

### React Native Environment
```bash
# Install React Native CLI
npm install -g react-native-cli

# Create new React Native app
cd mobile/
npx react-native init CustomerApp --template react-native-template-typescript
npx react-native init DriverApp --template react-native-template-typescript
```

### Key Libraries to Install
```bash
# Navigation
npm install @react-navigation/native @react-navigation/stack

# State management
npm install @reduxjs/toolkit react-redux

# API calls
npm install @reduxjs/toolkit/query

# Maps
npm install react-native-maps

# Location services
npm install @react-native-community/geolocation
```

## 🔐 Security Implementation

### 1. GPS Encryption for VIP Users
```python
# In rides/models.py
def encrypt_gps_data(self, data):
    if self.customer_tier == UserTier.VIP:
        from django.conf import settings
        from cryptography.fernet import Fernet
        
        key = settings.ENCRYPTION_KEY.encode()[:32]
        fernet = Fernet(key)
        return fernet.encrypt(str(data).encode()).decode()
    return data
```

### 2. API Authentication
```python
# Add to settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

## 📊 Database Optimization

### Key Indexes Already Implemented
- User email, phone_number, user_type, tier
- Ride customer, driver, status, requested_at
- Vehicle license_plate, owner, category, status
- Hotel bookings customer, hotel, status, check_in_date

### Performance Tips
1. Use `select_related()` for foreign keys
2. Use `prefetch_related()` for many-to-many relationships
3. Add database indexes for frequently queried fields
4. Use Redis for caching frequently accessed data

## 🚀 Deployment Preparation

### 1. Environment Variables
```bash
# Production .env
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgres://user:pass@host:port/db
REDIS_URL=redis://host:port/0
```

### 2. Static Files
```python
# settings.py for production
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### 3. Security Settings
```python
# Add to production settings
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
```

## 📈 Monitoring & Analytics

### Logging Setup
- Django logs configured in `settings.py`
- Celery task monitoring with Flower
- Database query monitoring
- API endpoint performance tracking

### Metrics to Track
- User registration and retention
- Ride completion rates
- Driver earnings and satisfaction
- API response times
- Error rates and types

## 🤝 Contributing Guidelines

### Code Style
1. Follow PEP 8 for Python code
2. Use meaningful variable and function names
3. Add docstrings to all functions and classes
4. Write tests for new features

### Git Workflow
1. Create feature branches from main
2. Make atomic commits with clear messages
3. Test before pushing
4. Create pull requests for review

### Documentation
1. Update README.md for new features
2. Document API endpoints
3. Add inline comments for complex logic
4. Update this development guide as needed

## 🔍 Debugging Tips

### Common Issues
1. **Migration conflicts**: Use `python manage.py migrate --fake-initial`
2. **Redis connection**: Ensure Redis server is running
3. **Database encoding**: Use UTF-8 encoding for PostgreSQL
4. **Static files**: Run `python manage.py collectstatic` for production

### Useful Commands
```bash
# Check Django version
python -m django --version

# Show migrations
python manage.py showmigrations

# Django shell
python manage.py shell

# Create app
python manage.py startapp app_name

# Check deployment readiness
python manage.py check --deploy
```

This guide will help you navigate the development process and implement new features efficiently!
