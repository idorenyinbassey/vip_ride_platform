# 🔧 Development vs Production Configuration Guide

## ✅ **HTTPS Issue Fixed!**

Your VIP Ride-Hailing Platform now has proper **separation between development and production configurations**, eliminating the forced HTTPS redirects during local development.

---

## 🎯 **Quick Start Commands**

### 🖥️ **Development Mode (HTTP-friendly)**
```bash
# Method 1: Use development settings explicitly
python manage.py runserver 127.0.0.1:8001 --settings=vip_ride_platform.dev_settings

# Method 2: Set in .env and run normally
# (Your .env is already configured for this)
source .env && python manage.py runserver 127.0.0.1:8001
```

### 🌐 **Production Mode (HTTPS-enforced)**
```bash
# Production settings (for deployment)
python manage.py runserver 127.0.0.1:8001 --settings=vip_ride_platform.settings
```

---

## 📋 **Configuration Summary**

### 🔧 **Development Settings** (`vip_ride_platform.dev_settings`)
- ✅ **DEBUG = True** (Detailed error pages)
- ✅ **SECURE_SSL_REDIRECT = False** (No HTTPS forcing)
- ✅ **SESSION_COOKIE_SECURE = False** (HTTP cookies allowed)
- ✅ **CSRF_COOKIE_SECURE = False** (HTTP CSRF protection)
- ✅ **SECURE_HSTS_SECONDS = 0** (No HSTS headers)
- ✅ **ALLOWED_HOSTS = ['*']** (Flexible host matching)
- ✅ **CORS_ALLOW_ALL_ORIGINS = True** (Easy frontend testing)
- ✅ **EMAIL_BACKEND = console** (Emails in terminal)

### 🛡️ **Production Settings** (`vip_ride_platform.settings`)
- 🔒 **DEBUG = False** (Secure error handling)
- 🔒 **SECURE_SSL_REDIRECT = True** (Force HTTPS)
- 🔒 **SESSION_COOKIE_SECURE = True** (HTTPS-only cookies)
- 🔒 **CSRF_COOKIE_SECURE = True** (HTTPS-only CSRF)
- 🔒 **SECURE_HSTS_SECONDS = 31536000** (1 year HSTS)
- 🔒 **ALLOWED_HOSTS = [specific domains]** (Restricted hosts)
- 🔒 **Full security headers enabled**

---

## 🚀 **Current Server Status**

Your development server is now running successfully with:

| Service | URL | Status | Configuration |
|---------|-----|--------|---------------|
| **Django Server** | http://127.0.0.1:8001/ | ✅ Running | dev_settings |
| **API Root** | http://127.0.0.1:8001/api/v1/ | ✅ HTTP | No HTTPS redirect |
| **Admin Panel** | http://127.0.0.1:8001/admin/ | ✅ HTTP | Development mode |
| **Metrics Endpoint** | http://127.0.0.1:8001/metrics | ✅ HTTP | Prometheus data |

---

## 📁 **Environment File Configuration**

### 🔧 **Development (.env)**
```env
# Development Mode - HTTP-friendly
DJANGO_SETTINGS_MODULE=vip_ride_platform.dev_settings
DEBUG=true
SECURE_SSL_REDIRECT=false  # Optional override
```

### 🌐 **Production (.env.production)**
```env
# Production Mode - HTTPS-enforced
DJANGO_SETTINGS_MODULE=vip_ride_platform.settings
DEBUG=false
SECURE_SSL_REDIRECT=true
SECRET_KEY=your-strong-production-secret
```

---

## 🎯 **Access URLs (All HTTP in Development)**

| Endpoint | URL | Purpose |
|----------|-----|---------|
| **Home** | http://127.0.0.1:8001/ | Marketing landing page |
| **API Root** | http://127.0.0.1:8001/api/v1/ | REST API browser |
| **Admin** | http://127.0.0.1:8001/admin/ | Django administration |
| **Metrics** | http://127.0.0.1:8001/metrics | Prometheus metrics |
| **API Auth** | http://127.0.0.1:8001/api-auth/ | DRF authentication |
| **Portal** | http://127.0.0.1:8001/portal/ | User dashboard |

---

## 🔄 **Switching Between Modes**

### ↗️ **Switch to Development Mode**
```bash
# Stop current server (Ctrl+C)
# Start with development settings
python manage.py runserver 127.0.0.1:8001 --settings=vip_ride_platform.dev_settings
```

### ↗️ **Switch to Production Mode**
```bash
# Stop current server (Ctrl+C)  
# Start with production settings
python manage.py runserver 127.0.0.1:8001 --settings=vip_ride_platform.settings
```

### 🔄 **Using Environment Variables**
```bash
# Development
export DJANGO_SETTINGS_MODULE=vip_ride_platform.dev_settings
python manage.py runserver 127.0.0.1:8001

# Production
export DJANGO_SETTINGS_MODULE=vip_ride_platform.settings
python manage.py runserver 127.0.0.1:8001
```

---

## 🐳 **Docker Configuration**

### 🔧 **Development Docker**
```yaml
# docker-compose.yml
services:
  web:
    environment:
      - DJANGO_SETTINGS_MODULE=vip_ride_platform.dev_settings
      - DEBUG=True
```

### 🌐 **Production Docker**
```yaml
# docker-compose.prod.yml
services:
  web:
    environment:
      - DJANGO_SETTINGS_MODULE=vip_ride_platform.settings
      - DEBUG=False
      - SECURE_SSL_REDIRECT=True
```

---

## 🛠️ **Development Tools Integration**

### 🔍 **VS Code Settings**
```json
{
    "python.defaultInterpreterPath": "./.venv/bin/python",
    "python.terminal.activateEnvironment": true,
    "django.settingsModule": "vip_ride_platform.dev_settings"
}
```

### 🧪 **Testing Configuration**
```bash
# Run tests with development settings
python manage.py test --settings=vip_ride_platform.dev_settings

# Run tests with production settings
python manage.py test --settings=vip_ride_platform.settings
```

---

## ❗ **Important Notes**

### ⚠️ **Security Reminders**
- **Never use development settings in production**
- **Development secret key is insecure by design**
- **Production requires strong SECRET_KEY**
- **HTTPS certificates needed for production**

### 🔄 **Migration Commands**
```bash
# Development migrations
python manage.py migrate --settings=vip_ride_platform.dev_settings

# Production migrations  
python manage.py migrate --settings=vip_ride_platform.settings
```

### 📦 **Static Files**
```bash
# Development (usually not needed)
python manage.py collectstatic --settings=vip_ride_platform.dev_settings

# Production (required)
python manage.py collectstatic --settings=vip_ride_platform.settings
```

---

## 🎉 **Success Confirmation**

✅ **HTTPS forcing issue resolved**  
✅ **Development server runs on HTTP**  
✅ **Production security maintained**  
✅ **Configuration separation complete**  
✅ **Environment switching functional**

Your VIP Ride-Hailing Platform now provides the best of both worlds:
- **Easy HTTP development** for local coding
- **Secure HTTPS production** for deployment

**The development server is ready at: http://127.0.0.1:8001/**

---

**Configuration completed on September 8, 2025**
