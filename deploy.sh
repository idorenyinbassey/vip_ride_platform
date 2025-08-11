#!/bin/bash

# VIP Ride-Hailing Platform - Quick Deployment Script
# This script automates the deployment process for different environments

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check requirements
check_requirements() {
    print_status "Checking system requirements..."
    
    # Check Python
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python $PYTHON_VERSION found"
    else
        print_error "Python 3.11+ is required"
        exit 1
    fi
    
    # Check PostgreSQL (optional for development)
    if command_exists psql; then
        POSTGRES_VERSION=$(psql --version | cut -d' ' -f3)
        print_success "PostgreSQL $POSTGRES_VERSION found"
    else
        print_warning "PostgreSQL not found (SQLite will be used for development)"
    fi
    
    # Check Redis (optional)
    if command_exists redis-cli; then
        print_success "Redis found"
    else
        print_warning "Redis not found (caching will be disabled)"
    fi
    
    # Check Docker (optional)
    if command_exists docker; then
        DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | sed 's/,//')
        print_success "Docker $DOCKER_VERSION found"
    else
        print_warning "Docker not found (manual deployment will be used)"
    fi
}

# Function to setup virtual environment
setup_venv() {
    print_status "Setting up virtual environment..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    print_success "Virtual environment activated"
    
    # Upgrade pip
    pip install --upgrade pip
    print_success "pip upgraded"
}

# Function to install dependencies
install_dependencies() {
    local env_type="$1"
    print_status "Installing $env_type dependencies..."
    
    case $env_type in
        "development")
            pip install -r requirements/development.txt
            ;;
        "production")
            pip install -r requirements/production.txt
            ;;
        "testing")
            pip install -r requirements/testing.txt
            ;;
        *)
            pip install -r requirements/base.txt
            ;;
    esac
    
    print_success "$env_type dependencies installed"
}

# Function to setup environment file
setup_environment() {
    print_status "Setting up environment configuration..."
    
    if [ ! -f ".env" ]; then
        cp .env.example .env
        print_success "Environment file created from template"
        print_warning "Please edit .env with your configuration"
    else
        print_warning ".env file already exists"
    fi
}

# Function to setup database
setup_database() {
    print_status "Setting up database..."
    
    # Run migrations
    python manage.py migrate
    print_success "Database migrations completed"
    
    # Create superuser (only if not exists)
    echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@vipride.com', 'admin123')" | python manage.py shell
    print_success "Admin user created (username: admin, password: admin123)"
    
    # Collect static files
    python manage.py collectstatic --noinput
    print_success "Static files collected"
}

# Function to run tests
run_tests() {
    print_status "Running tests..."
    
    # Run Django tests
    python manage.py test --verbosity=2
    
    # Run pytest if available
    if command_exists pytest; then
        pytest
    fi
    
    print_success "All tests passed"
}

# Function to start development server
start_development() {
    print_status "Starting development server..."
    
    # Start Celery worker in background (if Redis is available)
    if command_exists redis-cli; then
        celery -A vip_ride_platform worker -l info &
        CELERY_PID=$!
        print_success "Celery worker started (PID: $CELERY_PID)"
        
        # Start Celery beat in background
        celery -A vip_ride_platform beat -l info &
        BEAT_PID=$!
        print_success "Celery beat started (PID: $BEAT_PID)"
    fi
    
    # Start Django development server
    print_success "Starting Django development server on http://localhost:8000"
    python manage.py runserver
}

# Function to deploy with Docker
deploy_docker() {
    local env_type="$1"
    print_status "Deploying with Docker ($env_type)..."
    
    if [ "$env_type" = "production" ]; then
        docker-compose -f docker-compose.prod.yml up --build -d
        print_success "Production deployment started with Docker"
        print_status "Running production setup..."
        docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
        docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
    else
        docker-compose up --build -d
        print_success "Development deployment started with Docker"
        print_status "Running development setup..."
        docker-compose exec web python manage.py migrate
        docker-compose exec web python manage.py collectstatic --noinput
    fi
}

# Function to deploy to Heroku
deploy_heroku() {
    print_status "Deploying to Heroku..."
    
    # Check if Heroku CLI is installed
    if ! command_exists heroku; then
        print_error "Heroku CLI is required for Heroku deployment"
        exit 1
    fi
    
    # Login to Heroku
    heroku login
    
    # Create Heroku app if needed
    read -p "Enter Heroku app name (or press enter for auto-generated): " APP_NAME
    if [ -z "$APP_NAME" ]; then
        heroku create
    else
        heroku create "$APP_NAME"
    fi
    
    # Add PostgreSQL and Redis addons
    heroku addons:create heroku-postgresql:standard-0
    heroku addons:create heroku-redis:premium-0
    
    # Set environment variables
    heroku config:set DJANGO_SETTINGS_MODULE=vip_ride_platform.prod_settings
    heroku config:set SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
    
    # Deploy
    git push heroku main
    
    # Run migrations
    heroku run python manage.py migrate
    heroku run python manage.py createsuperuser --noinput
    
    print_success "Heroku deployment completed"
}

# Main deployment function
deploy() {
    local deployment_type="$1"
    local environment="$2"
    
    print_status "Starting VIP Ride-Hailing Platform deployment"
    print_status "Deployment type: $deployment_type"
    print_status "Environment: $environment"
    
    # Check requirements
    check_requirements
    
    case $deployment_type in
        "local")
            setup_venv
            install_dependencies "$environment"
            setup_environment
            setup_database
            if [ "$environment" = "testing" ]; then
                run_tests
            fi
            start_development
            ;;
        "docker")
            deploy_docker "$environment"
            ;;
        "heroku")
            deploy_heroku
            ;;
        *)
            print_error "Unknown deployment type: $deployment_type"
            print_status "Available types: local, docker, heroku"
            exit 1
            ;;
    esac
}

# Function to show help
show_help() {
    echo "VIP Ride-Hailing Platform - Deployment Script"
    echo ""
    echo "Usage: $0 [DEPLOYMENT_TYPE] [ENVIRONMENT]"
    echo ""
    echo "DEPLOYMENT_TYPE:"
    echo "  local     - Local development setup"
    echo "  docker    - Docker containerized deployment"
    echo "  heroku    - Heroku cloud deployment"
    echo ""
    echo "ENVIRONMENT:"
    echo "  development - Development environment"
    echo "  production  - Production environment"
    echo "  testing     - Testing environment"
    echo ""
    echo "Examples:"
    echo "  $0 local development     # Local development setup"
    echo "  $0 docker production     # Production Docker deployment"
    echo "  $0 heroku production     # Heroku production deployment"
    echo ""
    echo "Quick commands:"
    echo "  $0 --check              # Check system requirements only"
    echo "  $0 --test               # Run tests only"
    echo "  $0 --help               # Show this help"
}

# Parse command line arguments
case "$1" in
    --help|-h)
        show_help
        exit 0
        ;;
    --check)
        check_requirements
        exit 0
        ;;
    --test)
        setup_venv
        install_dependencies "testing"
        run_tests
        exit 0
        ;;
    "")
        print_error "No deployment type specified"
        show_help
        exit 1
        ;;
    *)
        DEPLOYMENT_TYPE="$1"
        ENVIRONMENT="${2:-development}"
        deploy "$DEPLOYMENT_TYPE" "$ENVIRONMENT"
        ;;
esac
