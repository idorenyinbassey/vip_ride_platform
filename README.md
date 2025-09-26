# 🚗 VIP Ride-Hailing Platform

[![Django Version](https://img.shields.io/badge/Django-5.2.5-green.svg)](https://www.djangoproject.com/)
[![Flutter](https://img.shields.io/badge/Flutter-3.9.2-blue.svg)](https://flutter.dev/)
[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

A comprehensive multi-tier ride-hailing platform with Django 5.2.5 backend and Flutter mobile app, supporting Regular, VIP, and VIP Premium service tiers with BlackTier card access system. Features advanced encrypted GPS tracking, hotel partnerships, emergency response systems, and 126+ API endpoints.

## 📋 Table of Contents

- [🚀 Quick Start](#-quick-start)
- [📖 Documentation](#-documentation)
- [🐳 Docker Deployment](#-docker-deployment)
- [💻 Desktop Development](#-desktop-development)
- [📱 Flutter Mobile App](#-flutter-mobile-app)
- [🌐 Production Deployment](#-production-deployment)
- [� Recent Updates](#-recent-updates)
- [�🏗️ Architecture](#️-architecture)
- [🛠️ Technology Stack](#️-technology-stack)
- [💼 Business Model](#-business-model)
- [🔒 Security](#-security)
- [🤝 Contributing](#-contributing)

## 🚀 Quick Start

### 🎯 Choose Your Deployment Method

| Method | Use Case | Time to Setup |
|--------|----------|---------------|
| **[🐳 Docker](#-docker-deployment)** | Production, Testing, CI/CD | 5 minutes |
| **[💻 Local Development](#-desktop-development)** | Development, Testing | 10 minutes |
| **[☁️ Cloud Production](#-production-deployment)** | Live deployment | 30 minutes |

### ⚡ Super Quick Start (Docker)

```bash
# Clone and start with Docker
git clone https://github.com/idorenyinbassey/vip_ride_platform.git
cd vip_ride_platform
cp .env.example .env
docker-compose up --build

# Access URLs:
# API: http://localhost:8000/api/v1/
# Admin: http://localhost:8000/admin/
```

### 🖥️ Super Quick Start (Local Development)

```bash
# Clone and start locally
git clone https://github.com/idorenyinbassey/vip_ride_platform.git
cd vip_ride_platform
python -m venv venv_new
source venv_new/Scripts/activate  # Windows
pip install -r requirements.txt
# Optional: use provided env file for local dev
cp .env.example .env
# Load .env in Git Bash (optional; PowerShell users can set $env:VAR)
set -a; . ./.env; set +a
python manage.py migrate
python manage.py runserver 127.0.0.1:8001
# Alternatively, pass settings explicitly if you prefer:
# python manage.py runserver 127.0.0.1:8001 --settings=vip_ride_platform.dev_settings

# Access URLs:
# API: http://127.0.0.1:8001/api/v1/
# Admin: http://127.0.0.1:8001/admin/
```

## 📖 Documentation

> 📚 **[Complete Documentation Index](./docs/INDEX.md)** - Master navigation for all documentation

### 🚀 Quick Access Documentation
- **[📘 Development Guide](./docs/development/DEVELOPMENT_CONFIGURATION_GUIDE.md)** - Complete local development setup
- **[🔌 API Documentation](./docs/guides/API_DOCUMENTATION.md)** - All 126+ API endpoints
- **[🐳 Docker Deployment Guide](#-docker-deployment)** - Containerized deployment
- **[🌐 Production Deployment Guide](./docs/deployment/DEPLOYMENT.md)** - Cloud deployment
- **[� Flutter Mobile App](./mobile/README.md)** - Mobile app setup & features

### 📂 Documentation Categories
- **[🏗️ Architecture](./docs/architecture/)** - System architecture overview
- **[� Implementation](./docs/implementation/)** - Feature implementations & fixes
- **[� Development](./docs/development/)** - Development configuration & milestones
- **[🧪 Testing](./docs/testing/)** - Testing guides & results
- **[� Security](./docs/security/)** - Security procedures & testing
- **[📋 Technical](./docs/technical/)** - Technical specifications & systems
- **[� Guides](./docs/guides/)** - Step-by-step implementation guides
- **[� Deployment](./docs/deployment/)** - Production deployment guides
- **[🧹 Maintenance](./docs/maintenance/)** - Project cleanup & optimization

### ⚙️ Configuration & Setup
- **[🌍 Environment Configuration](./.env.example)** - Environment variables
- **[� JWT Implementation Guide](./docs/guides/JWT_IMPLEMENTATION_GUIDE.md)** - Authentication system
- **[� GPS Encryption Setup](./docs/guides/GPS_ENCRYPTION_SETUP.md)** - VIP GPS security
- **[🏨 Hotel Partnership API](./hotel_partnerships/)** - Hotel booking integration

## 🐳 Docker Deployment

### 🚀 Quick Docker Setup

#### 1. Prerequisites
- Docker Desktop 4.0+
- Docker Compose V2
- 4GB RAM minimum

#### 2. Environment Setup
```bash
# Clone repository
git clone https://github.com/idorenyinbassey/vip_ride_platform.git
cd vip_ride_platform

# Copy environment file
cp .env.example .env

# Edit environment variables (optional for development)
# nano .env  # Linux/Mac
# notepad .env  # Windows
```

#### 3. Build and Start Services
```bash
# Development mode
docker-compose up --build

# Production mode
docker-compose -f docker-compose.prod.yml up --build -d

# Check service status
docker-compose ps
```

#### 4. Initialize Database
```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Load sample data (optional)
docker-compose exec web python manage.py loaddata fixtures/sample_data.json
```

### 🔧 Docker Configuration Files

#### `docker-compose.yml` (Development)
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/code
      - static_volume:/code/staticfiles
      - media_volume:/code/media
    environment:
      - DEBUG=True
      - DATABASE_URL=postgresql://vipride:password@db:5432/vipride_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    command: python manage.py runserver 0.0.0.0:8000

  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      - POSTGRES_DB=vipride_db
      - POSTGRES_USER=vipride
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  celery:
    build: .
    command: celery -A vip_ride_platform worker -l info
    volumes:
      - .:/code
    environment:
      - DEBUG=True
      - DATABASE_URL=postgresql://vipride:password@db:5432/vipride_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  flower:
    build: .
    command: celery -A vip_ride_platform flower
    ports:
      - "5555:5555"
    environment:
      - DEBUG=True
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis

volumes:
  postgres_data:
  static_volume:
  media_volume:
```

#### `docker-compose.prod.yml` (Production)
```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - static_volume:/var/www/static
      - media_volume:/var/www/media
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web

  web:
    build: 
      context: .
      dockerfile: Dockerfile.prod
    expose:
      - "8000"
    volumes:
      - static_volume:/code/staticfiles
      - media_volume:/code/media
    environment:
      - DEBUG=False
      - DATABASE_URL=postgresql://vipride:${DB_PASSWORD}@db:5432/vipride_db
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
      - SECURE_SSL_REDIRECT=True
    depends_on:
      - db
      - redis
    command: gunicorn vip_ride_platform.wsgi:application --bind 0.0.0.0:8000 --workers 4

  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      - POSTGRES_DB=vipride_db
      - POSTGRES_USER=vipride
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped

  celery:
    build: 
      context: .
      dockerfile: Dockerfile.prod
    command: celery -A vip_ride_platform worker -l info
    volumes:
      - .:/code
    environment:
      - DEBUG=False
      - DATABASE_URL=postgresql://vipride:${DB_PASSWORD}@db:5432/vipride_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    restart: unless-stopped

volumes:
  postgres_data:
  static_volume:
  media_volume:
```

#### `Dockerfile`
```dockerfile
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /code

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /code/

# Create staticfiles directory
RUN mkdir -p /code/staticfiles

# Create logs directory
RUN mkdir -p /code/logs

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

### 🎯 Docker Commands Reference

```bash
# Development Commands
docker-compose up --build              # Start all services
docker-compose down                    # Stop all services
docker-compose logs web                # View web service logs
docker-compose exec web bash           # Access web container shell

# Production Commands
docker-compose -f docker-compose.prod.yml up -d --build  # Start production
docker-compose -f docker-compose.prod.yml down           # Stop production
docker-compose -f docker-compose.prod.yml logs nginx     # View nginx logs

# Database Commands
docker-compose exec web python manage.py migrate         # Run migrations
docker-compose exec web python manage.py createsuperuser # Create admin user
docker-compose exec db psql -U vipride -d vipride_db     # Access database

# Monitoring Commands
docker-compose ps                      # Check service status
docker-compose top                     # View running processes
docker system prune                    # Clean up unused containers
```

## 💻 Desktop Development

### 🔧 Local Development Setup

#### 1. Prerequisites
```bash
# Check prerequisites
python --version    # Should be 3.11+
git --version      # Any recent version
```

#### 2. Environment Setup
```bash
# Clone repository
git clone https://github.com/idorenyinbassey/vip_ride_platform.git
cd vip_ride_platform

# Create virtual environment
python -m venv venv_new

# Activate virtual environment
# Windows:
venv_new\Scripts\activate
# Linux/Mac:
source venv_new/bin/activate

# Upgrade pip
python -m pip install --upgrade pip
```

#### 3. Install Dependencies
```bash
# Install Python packages
pip install -r requirements.txt

# Install additional development tools
pip install django-debug-toolbar pytest-django coverage
```

#### 4. Database Setup
```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load sample data (optional)
python manage.py loaddata fixtures/sample_data.json
```

#### 5. Start Development Server
```bash
# Start with development settings (HTTP-friendly)
python manage.py runserver 127.0.0.1:8001 --settings=vip_ride_platform.dev_settings

# If DJANGO_SETTINGS_MODULE=vip_ride_platform.dev_settings is set in .env,
# you can run without the --settings flag:
# python manage.py runserver 127.0.0.1:8001

# Or with production settings
python manage.py runserver 127.0.0.1:8001
```

#### 6. Redis & Celery (Local Development)

```bash
# Copy env (contains REDIS_URL and Celery settings)
cp .env.example .env

# Load .env in Git Bash (PowerShell users can set $env:VAR instead)
set -a; . ./.env; set +a

# Ensure Redis is running on 127.0.0.1:6379
# Optional (Docker):
# docker run --rm -p 6379:6379 redis:7-alpine

# Start Celery worker (new terminal, activate venv and load .env first)
celery -A vip_ride_platform worker -l info

# Optional: start Celery beat for scheduled tasks
celery -A vip_ride_platform beat -l info
```

Notes
- If `cp` isn’t available in your shell, use Python fallback:
  ```bash
  python - <<'PY'
  import shutil, os
  src='.env.example'; dst='.env'
  if not os.path.exists(dst):
      shutil.copy(src, dst)
  print('env copied')
  PY
  ```
- The `.env` sets `DJANGO_SETTINGS_MODULE=vip_ride_platform.dev_settings`, `REDIS_URL`, and `CELERY_*` so Celery and cache use your local Redis.

### 🎯 Development Access URLs

| Service | URL | Purpose |
|---------|-----|---------|
| **API Root** | http://127.0.0.1:8001/api/v1/ | Main API endpoints |
| **Admin Panel** | http://127.0.0.1:8001/admin/ | Django administration |
| **API Browser** | http://127.0.0.1:8001/api-auth/ | DRF browsable API |
| **Documentation** | http://127.0.0.1:8001/docs/ | API documentation |

### 🔧 Development Tools

#### Django Management Commands
```bash
# Development helpers
python manage.py check                 # Check for issues
python manage.py check --deploy        # Production readiness check
python manage.py test                  # Run test suite
python manage.py shell                 # Django shell
python manage.py dbshell              # Database shell

# Database operations
python manage.py makemigrations        # Create migrations
python manage.py migrate              # Apply migrations
python manage.py showmigrations       # Show migration status

# Static files
python manage.py collectstatic        # Collect static files
python manage.py findstatic filename  # Find static file location

# User management
python manage.py createsuperuser      # Create admin user
python manage.py changepassword user  # Change user password
```

#### Testing Commands
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test accounts
python manage.py test rides
python manage.py test payments

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html

# Run pytest
pytest
pytest --cov=. --cov-report=html
```

### 🔍 Development Debugging

#### Debug Settings (`dev_settings.py`)
```python
# Enables debugging features
DEBUG = True
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Console email backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Dummy cache for testing
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}
```

#### Common Development Issues

**Issue: HTTPS Errors**
```bash
# Solution: Use development settings
python manage.py runserver 127.0.0.1:8001 --settings=vip_ride_platform.dev_settings
```

**Issue: Database Locked**
```bash
# Solution: Reset SQLite database
rm db.sqlite3
python manage.py migrate
```

**Issue: Static Files Not Loading**
```bash
# Solution: Collect static files
python manage.py collectstatic --noinput
```

## 📱 Flutter Mobile App

### 🚀 Mobile App Features

#### Multi-Tier User Support
- **Regular Clients**: Standard ride booking with basic features
- **VIP Clients**: Access via Gold Card - priority booking, premium vehicles, enhanced SOS, concierge services
- **VIP Premium**: Access via Black Card - all VIP features + hotel partnerships, encrypted tracking, enhanced concierge
- **Drivers**: Independent, Fleet Owner, Fleet Driver, Leased Driver roles

#### 🃏 VIP Card System
- **Gold Card**: Unlocks VIP tier with 12-digit serial + 6-digit activation code
- **Black Card**: Unlocks VIP Premium tier with 12-digit serial + 6-digit activation code
- **Virtual Cards**: Generated upon purchase with secure activation process
- **Automatic Routing**: App automatically detects activated tier and routes to appropriate interface

#### Core Features
- **Real-time Ride Booking**: Live driver tracking with OpenStreetMap
- **Location Services**: GPS tracking with AES-256-GCM encryption for VIP users
- **Payment Integration**: Stripe, Flutterwave, and Paystack support
- **Emergency System**: SOS button with escalated alerts based on user tier
- **Hotel Integration**: Seamless hotel booking for VIP Premium users
- **Fleet Management**: Complete fleet operations for fleet owners

### 🔧 Mobile Development Setup

#### 1. Prerequisites
```bash
# Install Flutter SDK 3.9.2+
flutter --version

# Install dependencies
flutter doctor
```

#### 2. Setup Mobile App
```bash
# Navigate to mobile directory
cd mobile/

# Get Flutter dependencies
flutter pub get

# Run code generation (if needed)
flutter packages pub run build_runner build

# Check for issues
flutter analyze
```

#### 3. Configuration
```bash
# Copy mobile environment config
cp mobile/.env.example mobile/.env

# Update API endpoints in .env
API_BASE_URL=http://127.0.0.1:8001  # Local development
# API_BASE_URL=https://your-domain.com  # Production
```

#### 4. Run Mobile App
```bash
# Start Django backend first
python manage.py runserver 127.0.0.1:8001

# In mobile directory, run Flutter app
flutter run

# For specific platforms
flutter run -d chrome        # Web
flutter run -d android       # Android
flutter run -d ios          # iOS (macOS only)
```

### 📱 Mobile App Architecture

#### Role-Based Navigation
```dart
// Automatic role detection and routing
if (userRole == 'client_regular') {
  return RegularClientApp();
} else if (userRole == 'client_vip') {
  return VIPClientApp();
} else if (userRole == 'client_vip_premium') {
  return VIPPremiumClientApp();
} else if (userRole == 'driver_independent') {
  return IndependentDriverApp();
}
```

#### Key Directories
```
mobile/
├── lib/
│   ├── screens/
│   │   ├── client/regular/     # Regular client screens
│   │   ├── client/vip/         # VIP client screens  
│   │   ├── client/vip_premium/ # VIP Premium screens
│   │   ├── driver/independent/ # Independent driver screens
│   │   ├── driver/fleet_owner/ # Fleet owner screens
│   │   └── shared/             # Shared screens
│   ├── services/               # API and business logic
│   ├── models/                 # Data models
│   └── widgets/                # Reusable UI components
└── assets/                     # Images and static files
```

### 🔗 Backend Integration
- **Django API**: Full REST API integration with 126+ endpoints
- **JWT Authentication**: Secure token-based authentication
- **Real-time Updates**: WebSocket integration for live features
- **File Upload**: Image handling for profiles and documents
- **GPS Encryption**: Secure location tracking for VIP users

### 📱 Mobile App Documentation
- **[Mobile App README](./mobile/README.md)** - Detailed mobile app documentation
- **[Premium Integration Guide](./mobile/PREMIUM_INTEGRATION_GUIDE.md)** - VIP Premium features

## 🌐 Production Deployment

### ☁️ Cloud Platform Deployment

#### 🌊 DigitalOcean Deployment

##### 1. Create Droplet
```bash
# Create Ubuntu 22.04 droplet (2GB RAM minimum)
# Connect via SSH
ssh root@your-server-ip
```

##### 2. Server Setup
```bash
# Update system
apt update && apt upgrade -y

# Install dependencies
apt install -y python3-pip python3-venv postgresql postgresql-contrib redis-server nginx git

# Install Docker (optional)
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

##### 3. Application Deployment
```bash
# Create app user
adduser vipride
usermod -aG sudo vipride
su - vipride

# Clone repository
git clone https://github.com/idorenyinbassey/vip_ride_platform.git
cd vip_ride_platform

# Setup environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with production values (see Production .env below)
```

##### 4. Database Setup
```bash
# Setup PostgreSQL
sudo -u postgres psql
CREATE DATABASE vipride_db;
CREATE USER vipride WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE vipride_db TO vipride;
\q

# Run migrations
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### 🔐 Production .env (bare metal/VM)

Create/update `.env` with production-safe values:

```
DJANGO_SETTINGS_MODULE=vip_ride_platform.prod_settings
DEBUG=false
SECRET_KEY=your-strong-production-secret

# Database (choose one)
USE_POSTGRES=true
DB_NAME=vip_ride_platform
DB_USER=vip_user
DB_PASSWORD=change-me
DB_HOST=localhost
DB_PORT=5432
# Or single DSN:
# DATABASE_URL=postgresql://vip_user:change-me@localhost:5432/vip_ride_platform

# Redis for cache/channels/Celery
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Security
SECURE_SSL_REDIRECT=true
SESSION_COOKIE_SECURE=true
CSRF_COOKIE_SECURE=true
SECURE_HSTS_SECONDS=31536000
STRICT_PRODUCTION_MODE=true
```

Then:
- Ensure a `logs/` directory exists for file logging.
- Run migrations and collect static on the server.
- Start your WSGI server (gunicorn) behind Nginx.

##### 5. Nginx Configuration
```nginx
# /etc/nginx/sites-available/vipride
server {
    listen 80;
    server_name your-domain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /home/vipride/vip_ride_platform;
    }
    
    location /media/ {
        root /home/vipride/vip_ride_platform;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/vipride/vip_ride_platform/vipride.sock;
    }
}
```

##### 6. Systemd Service
```ini
# /etc/systemd/system/vipride.service
[Unit]
Description=VIP Ride Platform
After=network.target

[Service]
User=vipride
Group=www-data
WorkingDirectory=/home/vipride/vip_ride_platform
Environment="PATH=/home/vipride/vip_ride_platform/venv/bin"
ExecStart=/home/vipride/vip_ride_platform/venv/bin/gunicorn --workers 3 --bind unix:/home/vipride/vip_ride_platform/vipride.sock vip_ride_platform.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

#### ⏱️ Celery (systemd examples)

Create two services (worker and beat), loading the same env file.

```ini
# /etc/systemd/system/vipride-celery.service
[Unit]
Description=VIP Ride Celery Worker
After=network.target

[Service]
User=vipride
Group=www-data
WorkingDirectory=/home/vipride/vip_ride_platform
EnvironmentFile=/home/vipride/vip_ride_platform/.env
ExecStart=/home/vipride/vip_ride_platform/venv/bin/celery -A vip_ride_platform worker -l info
Restart=always

[Install]
WantedBy=multi-user.target
```

```ini
# /etc/systemd/system/vipride-celery-beat.service
[Unit]
Description=VIP Ride Celery Beat
After=network.target

[Service]
User=vipride
Group=www-data
WorkingDirectory=/home/vipride/vip_ride_platform
EnvironmentFile=/home/vipride/vip_ride_platform/.env
ExecStart=/home/vipride/vip_ride_platform/venv/bin/celery -A vip_ride_platform beat -l info
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```
sudo systemctl daemon-reload
sudo systemctl enable --now vipride-celery vipride-celery-beat
```

#### 🚀 AWS Deployment

##### 1. EC2 Instance Setup
```bash
# Launch EC2 instance (t3.medium minimum)
# Security groups: HTTP(80), HTTPS(443), SSH(22)
# Connect via SSH
ssh -i your-key.pem ubuntu@ec2-instance-ip
```

##### 2. Install Dependencies
```bash
# Update and install packages
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv postgresql postgresql-contrib redis-server nginx git

# Install AWS CLI
sudo apt install -y awscli
```

##### 3. Database Options

**Option A: Local PostgreSQL**
```bash
sudo -u postgres createdb vipride_db
sudo -u postgres createuser vipride
sudo -u postgres psql -c "ALTER USER vipride WITH PASSWORD 'secure_password';"
```

**Option B: RDS PostgreSQL**
```bash
# Create RDS instance via AWS Console
# Update .env with RDS endpoint
DATABASE_URL=postgresql://username:password@rds-endpoint:5432/dbname
```

##### 4. S3 Static Files (Optional)
```python
# settings.py additions
AWS_ACCESS_KEY_ID = 'your-access-key'
AWS_SECRET_ACCESS_KEY = 'your-secret-key'
AWS_STORAGE_BUCKET_NAME = 'your-bucket-name'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'storages.backends.s3boto3.StaticS3Boto3Storage'
```

#### 🎯 Heroku Deployment

##### 1. Heroku Setup
```bash
# Install Heroku CLI
# Create app
heroku create vip-ride-platform

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Add Redis
heroku addons:create heroku-redis:hobby-dev
```

##### 2. Configuration Files

**`Procfile`**
```
web: gunicorn vip_ride_platform.wsgi:application --bind 0.0.0.0:$PORT
worker: celery -A vip_ride_platform worker -l info
```

**`runtime.txt`**
```
python-3.13.0
```

##### 3. Deploy
```bash
# Set config vars
heroku config:set DEBUG=False
heroku config:set SECRET_KEY=your-secret-key
heroku config:set SECURE_SSL_REDIRECT=True

# Deploy
git push heroku main

# Run migrations
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

### 🐳 Docker Compose (Production) — .env tips

When using `docker-compose.prod.yml`, create a `.env` file in the project root with at least:

```
SECRET_KEY=your-strong-production-secret
DB_PASSWORD=postgres-password-for-db-service
```

Then build and start:
```
docker-compose -f docker-compose.prod.yml up -d --build
```

Run migrations and create admin:
```
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

### 🔒 Production Security Checklist

#### ✅ Django Security
- [ ] `DEBUG = False`
- [ ] Strong `SECRET_KEY`
- [ ] `SECURE_SSL_REDIRECT = True`
- [ ] `SESSION_COOKIE_SECURE = True`
- [ ] `CSRF_COOKIE_SECURE = True`
- [ ] `SECURE_HSTS_SECONDS` configured
- [ ] `ALLOWED_HOSTS` properly set

#### ✅ Database Security
- [ ] Strong database passwords
- [ ] Database firewall rules
- [ ] Regular backups configured
- [ ] SSL connections enabled

#### ✅ Server Security
- [ ] SSH key authentication
- [ ] Firewall configured
- [ ] Regular security updates
- [ ] SSL certificates installed
- [ ] Rate limiting enabled

#### ✅ Application Security
- [ ] Environment variables secured
- [ ] API rate limiting
- [ ] Input validation
- [ ] Error logging configured
- [ ] Monitoring set up

## � Recent Updates

### ✨ September 2025 - Major Cleanup & Organization
- **📚 Documentation Reorganization**: All documentation moved to structured `docs/` folder with 11 categories
- **🧹 Project Cleanup**: Removed 44 unused files (911.4KB saved) while preserving all core functionality
- **📱 Flutter Migration**: Updated from React Native to Flutter 3.9.2 for better cross-platform support
- **🔧 Development Optimization**: Streamlined project structure for better maintainability
- **📋 Master Documentation Index**: Created comprehensive navigation guide at `docs/INDEX.md`

### 🚀 Key Improvements
- **Clean Project Structure**: Professional organization following industry standards
- **Better Navigation**: Logical documentation categorization with master index
- **Mobile App Enhancement**: Flutter-based mobile app with role-based navigation
- **Production Ready**: All systems verified and deployment-ready
- **Developer Experience**: Improved setup guides and cleaner codebase

## �🏗️ Architecture

### 🎯 System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    VIP Ride-Hailing Platform                │
├─────────────────────────────────────────────────────────────┤
│  🌐 Frontend Layer                                         │
│  ├── Flutter Mobile Apps (iOS/Android/Web)                │
│  ├── Web Dashboard (React.js)                             │
│  └── Admin Portal (Django Admin)                          │
├─────────────────────────────────────────────────────────────┤
│  🔌 API Layer (126+ Endpoints)                            │
│  ├── Django REST Framework                                │
│  ├── JWT Authentication                                    │
│  ├── Rate Limiting & CORS                                 │
│  └── API Versioning (/api/v1/)                           │
├─────────────────────────────────────────────────────────────┤
│  💼 Business Logic Layer                                   │
│  ├── 👥 User Management (Multi-tier: Regular/VIP/VIP Premium) │
│  ├── 🃏 VIP Card System (Gold/Black Cards with Activation)│
│  ├── 🚗 Ride Matching & Workflow                          │
│  ├── 💳 Payment Processing (Multi-gateway)                │
│  ├── 🏨 Hotel Partnerships (B2B System)                   │
│  ├── 🚛 Fleet Management                                   │
│  ├── 🚨 Emergency Response (SOS/Control Center)            │
│  └── 🏎️ Vehicle Leasing Marketplace                       │
├─────────────────────────────────────────────────────────────┤
│  🗄️ Data Layer                                             │
│  ├── PostgreSQL (Primary database)                        │
│  ├── Redis (Caching & real-time)                         │
│  ├── AES-256-GCM Encryption (VIP GPS)                    │
│  └── Audit Logging (NDPR compliance)                      │
├─────────────────────────────────────────────────────────────┤
│  🔧 Infrastructure Layer                                   │
│  ├── Docker Containers                                    │
│  ├── Nginx (Load balancer)                               │
│  ├── Celery (Background tasks)                           │
│  └── Monitoring & Logging                                │
└─────────────────────────────────────────────────────────────┘
```

### 🎯 User Tier System

#### 🎭 BlackTier Services Access
- **🥇 Gold Card → VIP Access**: Purchase Gold Card to unlock VIP tier
- **🖤 Black Card → VIP Premium Access**: Purchase Black Card to unlock VIP Premium tier  
- **Virtual Card System**: Each card generates 12-digit serial number + 6-digit activation code
- **App Upgrade**: Card activation automatically routes app to respective tier (VIP/VIP Premium)

| Tier | Access Method | Commission | Features | Driver Benefits |
|------|---------------|------------|----------|-----------------|
| **Regular** | Default | 15-20% | Standard rides, basic booking | Standard commission |
| **VIP** | 🥇 Gold Card | 25-30% | Encrypted GPS, SOS, trusted drivers, concierge services | Premium rates |
| **VIP Premium** | 🖤 Black Card | 25-30% | All VIP + hotel partnerships, enhanced concierge | Premium rates |
| **Admin** | System Role | N/A | System management, analytics | N/A |

#### 🎩 Concierge Services
**Available exclusively to VIP and VIP Premium users:**
- Emergency response coordination
- VIP monitoring and assistance
- Priority customer support
- Personalized ride preferences

### 🚗 Driver Categories

1. **Private Drivers with Classic Cars**
   - Flexible billing by engine type (V6/V8/4-stroke)
   - Personal vehicle ownership
   - Commission-based earnings

2. **Fleet Companies with Premium Cars/Vans**
   - Fixed billing rates
   - Priority VIP allocation
   - Bulk vehicle management

3. **Vehicle Owners**
   - Lease cars to fleet companies
   - Revenue-sharing contracts
   - Marketplace integration

## �️ Technology Stack

### Backend Infrastructure
- **Framework**: Django 5.2.5 with Django REST Framework 3.16.0
- **Database**: PostgreSQL with Redis caching
- **Authentication**: JWT with djangorestframework-simplejwt 5.5.1
- **Real-time**: Django Channels 4.3.1 with Redis backend
- **Task Queue**: Celery 5.5.3 with Redis broker
- **Security**: AES-256-GCM encryption for VIP GPS tracking

### Mobile Application
- **Framework**: Flutter 3.9.2 with Dart SDK
- **Architecture**: Role-based navigation (Client/Driver tiers)
- **Maps**: OpenStreetMap with flutter_map integration
- **State Management**: Provider/Riverpod pattern
- **HTTP Client**: Dio for API communication
- **Payments**: Stripe, Flutterwave, Paystack integration

### DevOps & Infrastructure
- **Containerization**: Docker with docker-compose
- **Web Server**: Nginx with SSL/TLS
- **Monitoring**: Prometheus + Grafana
- **CI/CD**: GitHub Actions workflows
- **Cloud**: DigitalOcean, AWS, or Heroku ready

### Development Tools
- **Code Quality**: Django Debug Toolbar, Flutter Analyzer
- **Testing**: pytest-django, Flutter testing framework
- **Documentation**: Comprehensive docs with INDEX navigation
- **Version Control**: Git with professional project structure

## �💼 Business Model

### 💰 Revenue Streams

1. **Commission-based Pricing** (15-30% based on tier)
2. **BlackTier Card Sales** (Gold Cards for VIP, Black Cards for VIP Premium)
3. **Driver Subscriptions** ($99-299/month)
4. **Hotel Partnership Revenue** (10-15% booking commission)
5. **Vehicle Leasing Marketplace** (5-10% lease transaction fee)
6. **Premium Features** (VIP monitoring, emergency response)

### 📊 Financial Targets (2025)

| Metric | Target | Current |
|--------|--------|---------|
| Monthly GMV | ₦500M | Development |
| Active Drivers | 1,000+ | Setup Phase |
| Monthly Users | 50,000+ | Setup Phase |
| Hotel Partners | 50+ | 3 Registered |
| Fleet Companies | 20+ | Setup Phase |

## 🔒 Security

### 🛡️ RBAC Integration

The platform implements comprehensive Role-Based Access Control (RBAC) for multi-tier security:

#### Setup RBAC System

1. **Add RBAC Configuration**
```python
# Add to settings.py
exec(open(BASE_DIR / 'rbac_settings.py').read())

# Update middleware
MIDDLEWARE.extend([
    'accounts.rbac_middleware.RBACauditMiddleware',
    'accounts.rbac_middleware.SecurityMonitoringMiddleware',
])
```

2. **Create RBAC Permissions**
```python
# Custom permission classes
class AuditedTierPermission(BasePermission):
    def has_permission(self, request, view):
        # Check user tier and log access
        pass

class VIPDataPermission(BasePermission):
    def has_permission(self, request, view):
        # Special permission for VIP encrypted data
        pass
```

3. **Activate RBAC**
```bash
# Create RBAC management command
python manage.py setup_rbac

# Apply RBAC permissions
python manage.py migrate
```

### 🔐 Security Features

- **🔑 JWT Authentication** with refresh tokens
- **🛡️ Role-Based Access Control** (RBAC)
- **🔒 AES-256-GCM Encryption** for VIP GPS data
- **📝 Audit Logging** for NDPR compliance
- **🚨 Suspicious Activity Detection**
- **⚡ Rate Limiting** and IP blocking
- **💳 PCI DSS Compliance** for payments

### 📋 Compliance Standards

- **NDPR** (Nigeria Data Protection Regulation)
- **PCI DSS** (Payment Card Industry)
- **GDPR** compatibility
- **SOC 2** security controls

## 🤝 Contributing

### 🔄 Development Workflow

1. **Fork the repository**
2. **Create feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Follow coding standards**
   - Python: PEP 8 compliance
   - Django: Best practices
   - API: RESTful design
4. **Write comprehensive tests**
   ```bash
   python manage.py test
   coverage run --source='.' manage.py test
   ```
5. **Commit with descriptive messages**
   ```bash
   git commit -m "Add: VIP GPS encryption feature"
   ```
6. **Push and create Pull Request**
   ```bash
   git push origin feature/amazing-feature
   ```

### 📋 Code Standards

- **Python**: PEP 8 with type hints
- **Django**: Model-View-Serializer pattern
- **API**: RESTful with proper HTTP methods
- **Testing**: 90%+ coverage requirement
- **Documentation**: Comprehensive inline docs
- **Security**: Regular security audits

### 🧪 Testing Requirements

```bash
# Test coverage requirements
python manage.py test --keepdb
coverage report --fail-under=90

# Security testing
python manage.py check --deploy
bandit -r . -f json

# Performance testing
django-admin test --debug-mode
```

## 📞 Support & Resources

### 🔗 Quick Links

- **🐛 Issues**: [GitHub Issues](https://github.com/idorenyinbassey/vip_ride_platform/issues)
- **💬 Discussions**: [GitHub Discussions](https://github.com/idorenyinbassey/vip_ride_platform/discussions)
- **📖 Wiki**: [Project Wiki](https://github.com/idorenyinbassey/vip_ride_platform/wiki)
- **📧 Contact**: development@vipride.com

### 📚 Additional Resources

- **Django Documentation**: https://docs.djangoproject.com/
- **Django REST Framework**: https://www.django-rest-framework.org/
- **Docker Documentation**: https://docs.docker.com/
- **PostgreSQL Guide**: https://www.postgresql.org/docs/

### 🏆 Project Status

**Current Phase**: Production Ready (Phase 1 Complete)

✅ **Completed Features**:
- Advanced pricing system with surge algorithms
- Multi-tier user system (Normal/Premium/VIP)
- Hotel partnership B2B system
- Comprehensive API (126+ endpoints)
- Docker containerization
- Security implementations
- Admin interfaces

🚧 **Next Phase** (Q3 2025):
- Flutter mobile applications
- Production deployment
- Lagos market launch
- Payment gateway integration

---

## 📄 License

This project is proprietary software. All rights reserved.

**© 2025 VIP Ride-Hailing Platform. All rights reserved.**

---

**Built with ❤️ for Nigeria's premium transportation market**

*Ready for deployment across Docker, Desktop, and Cloud platforms* 🚀
