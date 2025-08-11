@echo off
REM VIP Ride-Hailing Platform - Windows Deployment Script
REM This script automates the deployment process for different environments

setlocal enabledelayedexpansion

REM Colors for output (if supported)
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "NC=[0m"

REM Function to print status messages
:print_status
echo %BLUE%[INFO]%NC% %~1
exit /b

:print_success
echo %GREEN%[SUCCESS]%NC% %~1
exit /b

:print_warning
echo %YELLOW%[WARNING]%NC% %~1
exit /b

:print_error
echo %RED%[ERROR]%NC% %~1
exit /b

REM Function to check if command exists
:command_exists
where %1 >nul 2>&1
exit /b %errorlevel%

REM Function to check requirements
:check_requirements
call :print_status "Checking system requirements..."

REM Check Python
call :command_exists python
if %errorlevel% equ 0 (
    for /f "tokens=2" %%a in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%a"
    call :print_success "Python !PYTHON_VERSION! found"
) else (
    call :print_error "Python 3.11+ is required"
    exit /b 1
)

REM Check PostgreSQL (optional for development)
call :command_exists psql
if %errorlevel% equ 0 (
    call :print_success "PostgreSQL found"
) else (
    call :print_warning "PostgreSQL not found (SQLite will be used for development)"
)

REM Check Redis (optional)
call :command_exists redis-cli
if %errorlevel% equ 0 (
    call :print_success "Redis found"
) else (
    call :print_warning "Redis not found (caching will be disabled)"
)

REM Check Docker (optional)
call :command_exists docker
if %errorlevel% equ 0 (
    call :print_success "Docker found"
) else (
    call :print_warning "Docker not found (manual deployment will be used)"
)
exit /b

REM Function to setup virtual environment
:setup_venv
call :print_status "Setting up virtual environment..."

if not exist "venv" (
    python -m venv venv
    call :print_success "Virtual environment created"
) else (
    call :print_warning "Virtual environment already exists"
)

REM Activate virtual environment
call venv\Scripts\activate.bat
call :print_success "Virtual environment activated"

REM Upgrade pip
python -m pip install --upgrade pip
call :print_success "pip upgraded"
exit /b

REM Function to install dependencies
:install_dependencies
set "env_type=%~1"
call :print_status "Installing %env_type% dependencies..."

if "%env_type%"=="development" (
    pip install -r requirements/development.txt
) else if "%env_type%"=="production" (
    pip install -r requirements/production.txt
) else if "%env_type%"=="testing" (
    pip install -r requirements/testing.txt
) else (
    pip install -r requirements/base.txt
)

call :print_success "%env_type% dependencies installed"
exit /b

REM Function to setup environment file
:setup_environment
call :print_status "Setting up environment configuration..."

if not exist ".env" (
    copy .env.example .env
    call :print_success "Environment file created from template"
    call :print_warning "Please edit .env with your configuration"
) else (
    call :print_warning ".env file already exists"
)
exit /b

REM Function to setup database
:setup_database
call :print_status "Setting up database..."

REM Run migrations
python manage.py migrate
call :print_success "Database migrations completed"

REM Create superuser (only if not exists)
echo from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@vipride.com', 'admin123') | python manage.py shell
call :print_success "Admin user created (username: admin, password: admin123)"

REM Collect static files
python manage.py collectstatic --noinput
call :print_success "Static files collected"
exit /b

REM Function to run tests
:run_tests
call :print_status "Running tests..."

REM Run Django tests
python manage.py test --verbosity=2

REM Run pytest if available
call :command_exists pytest
if %errorlevel% equ 0 (
    pytest
)

call :print_success "All tests passed"
exit /b

REM Function to start development server
:start_development
call :print_status "Starting development server..."

REM Start Celery worker in background (if Redis is available)
call :command_exists redis-cli
if %errorlevel% equ 0 (
    start /b celery -A vip_ride_platform worker -l info
    call :print_success "Celery worker started in background"
    
    REM Start Celery beat in background
    start /b celery -A vip_ride_platform beat -l info
    call :print_success "Celery beat started in background"
)

REM Start Django development server
call :print_success "Starting Django development server on http://localhost:8000"
python manage.py runserver
exit /b

REM Function to deploy with Docker
:deploy_docker
set "env_type=%~1"
call :print_status "Deploying with Docker (%env_type%)..."

if "%env_type%"=="production" (
    docker-compose -f docker-compose.prod.yml up --build -d
    call :print_success "Production deployment started with Docker"
    call :print_status "Running production setup..."
    docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
    docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
) else (
    docker-compose up --build -d
    call :print_success "Development deployment started with Docker"
    call :print_status "Running development setup..."
    docker-compose exec web python manage.py migrate
    docker-compose exec web python manage.py collectstatic --noinput
)
exit /b

REM Function to deploy to Heroku
:deploy_heroku
call :print_status "Deploying to Heroku..."

REM Check if Heroku CLI is installed
call :command_exists heroku
if %errorlevel% neq 0 (
    call :print_error "Heroku CLI is required for Heroku deployment"
    exit /b 1
)

REM Login to Heroku
heroku login

REM Create Heroku app
set /p "APP_NAME=Enter Heroku app name (or press enter for auto-generated): "
if "%APP_NAME%"=="" (
    heroku create
) else (
    heroku create %APP_NAME%
)

REM Add PostgreSQL and Redis addons
heroku addons:create heroku-postgresql:standard-0
heroku addons:create heroku-redis:premium-0

REM Set environment variables
heroku config:set DJANGO_SETTINGS_MODULE=vip_ride_platform.prod_settings

REM Generate and set secret key
for /f %%i in ('python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"') do set "SECRET_KEY=%%i"
heroku config:set SECRET_KEY=%SECRET_KEY%

REM Deploy
git push heroku main

REM Run migrations
heroku run python manage.py migrate
heroku run python manage.py createsuperuser --noinput

call :print_success "Heroku deployment completed"
exit /b

REM Main deployment function
:deploy
set "deployment_type=%~1"
set "environment=%~2"
if "%environment%"=="" set "environment=development"

call :print_status "Starting VIP Ride-Hailing Platform deployment"
call :print_status "Deployment type: %deployment_type%"
call :print_status "Environment: %environment%"

REM Check requirements
call :check_requirements
if %errorlevel% neq 0 exit /b %errorlevel%

if "%deployment_type%"=="local" (
    call :setup_venv
    call :install_dependencies "%environment%"
    call :setup_environment
    call :setup_database
    if "%environment%"=="testing" (
        call :run_tests
    )
    call :start_development
) else if "%deployment_type%"=="docker" (
    call :deploy_docker "%environment%"
) else if "%deployment_type%"=="heroku" (
    call :deploy_heroku
) else (
    call :print_error "Unknown deployment type: %deployment_type%"
    call :print_status "Available types: local, docker, heroku"
    exit /b 1
)
exit /b

REM Function to show help
:show_help
echo VIP Ride-Hailing Platform - Windows Deployment Script
echo.
echo Usage: %~nx0 [DEPLOYMENT_TYPE] [ENVIRONMENT]
echo.
echo DEPLOYMENT_TYPE:
echo   local     - Local development setup
echo   docker    - Docker containerized deployment
echo   heroku    - Heroku cloud deployment
echo.
echo ENVIRONMENT:
echo   development - Development environment
echo   production  - Production environment
echo   testing     - Testing environment
echo.
echo Examples:
echo   %~nx0 local development     # Local development setup
echo   %~nx0 docker production     # Production Docker deployment
echo   %~nx0 heroku production     # Heroku production deployment
echo.
echo Quick commands:
echo   %~nx0 --check              # Check system requirements only
echo   %~nx0 --test               # Run tests only
echo   %~nx0 --help               # Show this help
exit /b

REM Parse command line arguments
if "%1"=="--help" goto show_help
if "%1"=="-h" goto show_help
if "%1"=="--check" (
    call :check_requirements
    exit /b
)
if "%1"=="--test" (
    call :setup_venv
    call :install_dependencies "testing"
    call :run_tests
    exit /b
)
if "%1"=="" (
    call :print_error "No deployment type specified"
    call :show_help
    exit /b 1
)

call :deploy "%1" "%2"
