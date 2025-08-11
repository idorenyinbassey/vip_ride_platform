# VIP Ride-Hailing Platform - Development Guide

## 🚀 Quick Start for Development

### Prerequisites
- Python 3.11+
- Virtual Environment
- Git

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "RIDE HAILING APP"
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv_new
   # Windows
   venv_new\Scripts\activate
   # Linux/Mac
   source venv_new/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Start development server**
   ```bash
   # Use development settings (SSL disabled, DEBUG enabled)
   python manage.py runserver 127.0.0.1:8001 --settings=vip_ride_platform.dev_settings
   ```

### 🔧 Development Settings

The project has two settings configurations:

#### Production Settings (`settings.py`)
- `DEBUG = False`
- `SECURE_SSL_REDIRECT = False` (configurable via env)
- `SESSION_COOKIE_SECURE = False` (configurable via env)
- `CSRF_COOKIE_SECURE = False` (configurable via env)
- Strong SECRET_KEY for security

#### Development Settings (`dev_settings.py`)
- `DEBUG = True`
- `SECURE_SSL_REDIRECT = False` (disabled)
- `SESSION_COOKIE_SECURE = False` (disabled)
- `CSRF_COOKIE_SECURE = False` (disabled)
- All SSL/HTTPS requirements disabled for local development

### 🌐 Development URLs

When running with development settings:
- **Main Application**: http://127.0.0.1:8001/
- **Admin Panel**: http://127.0.0.1:8001/admin/
- **API Root**: http://127.0.0.1:8001/api/

### 🔐 Environment Variables

Create a `.env` file for local development:

```env
# Development Configuration
DEBUG=True
SECRET_KEY=your-development-secret-key

# Database (SQLite for development)
USE_POSTGRES=false

# Security (disabled for development)
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
STRICT_PRODUCTION_MODE=False

# Payment Gateways (test mode)
PAYSTACK_TEST_MODE=True
FLUTTERWAVE_TEST_MODE=True
STRIPE_TEST_MODE=True

# Redis (optional for development)
REDIS_URL=redis://localhost:6379/0
```

### 🐛 Common Development Issues & Solutions

#### Issue: HTTPS errors in development
**Error**: "You're accessing the development server over HTTPS, but it only supports HTTP"

**Solutions**:
1. Use development settings: `--settings=vip_ride_platform.dev_settings`
2. Use different port: `127.0.0.1:8001` instead of `8000`
3. Clear browser cache/data for localhost
4. Use incognito/private browsing mode

#### Issue: Django admin field errors
**Error**: Field mismatches in admin configurations

**Solution**: All admin configurations have been fixed to match model fields exactly.

#### Issue: Payment gateway validation errors
**Error**: Missing payment gateway keys

**Solution**: Set `STRICT_PRODUCTION_MODE=False` in development environment.

### 🏗️ Project Structure

```
RIDE HAILING APP/
├── vip_ride_platform/          # Main project settings
│   ├── settings.py             # Production settings
│   ├── dev_settings.py         # Development settings
│   ├── urls.py                 # Main URL configuration
│   └── wsgi.py/asgi.py        # WSGI/ASGI configuration
├── accounts/                   # User management & authentication
├── rides/                      # Ride booking & management
├── payments/                   # Payment processing
├── pricing/                    # Dynamic pricing & surge
├── hotels/                     # Hotel booking integration
├── hotel_partnerships/         # Hotel partnership management
├── notifications/              # Push notifications & alerts
├── control_center/            # Emergency monitoring & SOS
├── fleet_management/          # Vehicle & fleet management
├── vehicle_leasing/           # Vehicle leasing marketplace
├── gps_tracking/              # Real-time GPS & location services
├── static/                    # Static files (CSS, JS, images)
├── media/                     # User uploaded files
├── logs/                      # Application logs
└── requirements.txt           # Python dependencies
```

### 🎯 Development Workflow

1. **Feature Development**
   ```bash
   git checkout -b feature/your-feature-name
   # Make changes
   python manage.py test
   git commit -m "Add: your feature description"
   git push origin feature/your-feature-name
   ```

2. **Running Tests**
   ```bash
   python manage.py test
   # or for specific app
   python manage.py test accounts
   ```

3. **Database Migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Collecting Static Files**
   ```bash
   python manage.py collectstatic
   ```

### 📊 Django Admin

Access the admin panel at: http://127.0.0.1:8001/admin/

**Available Admin Interfaces:**
- User Management (accounts)
- Ride Management (rides)
- Payment Processing (payments)
- Fleet Management (fleet_management)
- Hotel Partnerships (hotel_partnerships)
- Emergency Incidents (control_center)
- Notifications (notifications)
- GPS Tracking (gps_tracking)
- Vehicle Leasing (vehicle_leasing)
- Pricing & Surge (pricing)

### 🔧 Development Tools

**Useful Django Management Commands:**
```bash
# Check for issues
python manage.py check
python manage.py check --deploy

# Database operations
python manage.py makemigrations
python manage.py migrate
python manage.py dbshell

# User management
python manage.py createsuperuser
python manage.py changepassword username

# Static files
python manage.py collectstatic
python manage.py findstatic filename

# Development utilities
python manage.py shell
python manage.py runserver
python manage.py test
```

### 🚀 Production Deployment

For production deployment, use:
```bash
# Production settings with full security
python manage.py check --deploy
python manage.py collectstatic --noinput
python manage.py migrate

# Set environment variables
export DEBUG=False
export SECURE_SSL_REDIRECT=True
export SESSION_COOKIE_SECURE=True
export CSRF_COOKIE_SECURE=True
export STRICT_PRODUCTION_MODE=True
```

### 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

### 🆘 Getting Help

- Check the Django documentation: https://docs.djangoproject.com/
- Review the project's GitHub issues
- Contact the development team

---

**Happy Coding! 🎉**
