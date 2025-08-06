-- Main Application Tables (Public Schema)
-- User Management and Authentication

-- Users table - Basic user information (non-sensitive)
CREATE TABLE public.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    user_type user_type NOT NULL DEFAULT 'customer',
    tier user_tier NOT NULL DEFAULT 'normal',
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE,
    gender VARCHAR(10),
    profile_image_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    email_verified_at TIMESTAMP,
    phone_verified_at TIMESTAMP,
    last_login TIMESTAMP,
    failed_login_attempts INTEGER DEFAULT 0,
    account_locked_until TIMESTAMP,
    preferred_language VARCHAR(10) DEFAULT 'en',
    timezone VARCHAR(50) DEFAULT 'UTC',
    marketing_consent BOOLEAN DEFAULT FALSE,
    data_processing_consent BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP -- Soft delete
);

-- Fleet Companies
CREATE TABLE public.fleet_companies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    legal_name VARCHAR(255) NOT NULL,
    registration_number VARCHAR(100) UNIQUE NOT NULL,
    tax_id VARCHAR(50),
    email VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    website_url TEXT,
    logo_url TEXT,
    description TEXT,
    headquarters_address TEXT NOT NULL,
    operating_cities TEXT[] DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    verification_documents JSONB DEFAULT '{}',
    rating DECIMAL(3,2) DEFAULT 0.00,
    total_ratings INTEGER DEFAULT 0,
    commission_rate DECIMAL(5,2) NOT NULL, -- Percentage
    preferred_payment_method VARCHAR(50),
    bank_account_details JSONB, -- Encrypted in production
    insurance_policy_number VARCHAR(100),
    insurance_expiry_date DATE,
    license_expiry_date DATE,
    emergency_contact JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);

-- Drivers
CREATE TABLE public.drivers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    fleet_company_id UUID REFERENCES public.fleet_companies(id) ON DELETE SET NULL,
    license_number VARCHAR(50) UNIQUE NOT NULL,
    license_expiry_date DATE NOT NULL,
    category driver_category NOT NULL DEFAULT 'private_driver',
    subscription_tier subscription_tier NOT NULL DEFAULT 'basic',
    subscription_expires_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending', -- pending, approved, suspended, rejected
    is_online BOOLEAN DEFAULT FALSE,
    is_available BOOLEAN DEFAULT FALSE,
    current_location POINT, -- PostGIS point for location
    last_location_update TIMESTAMP,
    vehicle_id UUID, -- Will reference vehicles table
    rating DECIMAL(3,2) DEFAULT 0.00,
    total_ratings INTEGER DEFAULT 0,
    total_rides INTEGER DEFAULT 0,
    total_earnings DECIMAL(12,2) DEFAULT 0.00,
    background_check_status VARCHAR(20) DEFAULT 'pending',
    background_check_date TIMESTAMP,
    training_completed BOOLEAN DEFAULT FALSE,
    training_completion_date TIMESTAMP,
    emergency_contact JSONB,
    preferred_work_hours JSONB, -- {"start": "06:00", "end": "22:00", "days": [1,2,3,4,5]}
    documents JSONB DEFAULT '{}', -- Document URLs and metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);

-- Vehicles
CREATE TABLE public.vehicles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    fleet_company_id UUID REFERENCES public.fleet_companies(id) ON DELETE CASCADE,
    make VARCHAR(50) NOT NULL,
    model VARCHAR(50) NOT NULL,
    year INTEGER NOT NULL,
    color VARCHAR(30) NOT NULL,
    license_plate VARCHAR(20) UNIQUE NOT NULL,
    vin VARCHAR(17) UNIQUE NOT NULL,
    vehicle_type vehicle_type NOT NULL,
    seating_capacity INTEGER NOT NULL,
    engine_type VARCHAR(50), -- V6, V8, 4-stroke, electric, hybrid
    fuel_type VARCHAR(20), -- petrol, diesel, electric, hybrid
    transmission VARCHAR(20), -- manual, automatic
    features TEXT[], -- ['GPS', 'AC', 'WiFi', 'USB_charging']
    is_luxury BOOLEAN DEFAULT FALSE,
    is_electric BOOLEAN DEFAULT FALSE,
    is_accessible BOOLEAN DEFAULT FALSE, -- Wheelchair accessible
    insurance_policy_number VARCHAR(100) NOT NULL,
    insurance_expiry_date DATE NOT NULL,
    registration_expiry_date DATE NOT NULL,
    last_maintenance_date DATE,
    next_maintenance_due DATE,
    mileage INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    is_available BOOLEAN DEFAULT TRUE,
    current_driver_id UUID REFERENCES public.drivers(id) ON DELETE SET NULL,
    location POINT, -- Current location
    documents JSONB DEFAULT '{}', -- Insurance, registration docs
    maintenance_history JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);

-- Update drivers table to reference vehicles
ALTER TABLE public.drivers ADD CONSTRAINT fk_drivers_vehicle
    FOREIGN KEY (vehicle_id) REFERENCES public.vehicles(id) ON DELETE SET NULL;

-- Vehicle Leasing (for vehicle owners leasing to fleet companies)
CREATE TABLE public.vehicle_leases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vehicle_owner_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    fleet_company_id UUID NOT NULL REFERENCES public.fleet_companies(id) ON DELETE CASCADE,
    vehicle_id UUID NOT NULL REFERENCES public.vehicles(id) ON DELETE CASCADE,
    lease_type VARCHAR(20) NOT NULL, -- fixed_rate, revenue_share, hybrid
    fixed_monthly_rate DECIMAL(10,2),
    revenue_share_percentage DECIMAL(5,2),
    minimum_monthly_guarantee DECIMAL(10,2),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'active', -- active, completed, terminated, suspended
    terms_and_conditions TEXT,
    insurance_responsibility VARCHAR(20) DEFAULT 'fleet', -- owner, fleet, shared
    maintenance_responsibility VARCHAR(20) DEFAULT 'fleet', -- owner, fleet, shared
    mileage_limit_monthly INTEGER,
    excess_mileage_rate DECIMAL(8,4),
    security_deposit DECIMAL(10,2),
    early_termination_fee DECIMAL(10,2),
    auto_renewal BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP,
    
    CONSTRAINT unique_active_lease_per_vehicle 
        UNIQUE (vehicle_id, status) 
        DEFERRABLE INITIALLY DEFERRED
);

-- Hotel Partners
CREATE TABLE public.hotel_partners (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    brand VARCHAR(100),
    chain VARCHAR(100),
    email VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    website_url TEXT,
    description TEXT,
    address TEXT NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100),
    country VARCHAR(100) NOT NULL,
    postal_code VARCHAR(20),
    location POINT, -- Latitude, longitude
    star_rating INTEGER CHECK (star_rating >= 1 AND star_rating <= 5),
    partnership_tier partnership_tier NOT NULL DEFAULT 'standard',
    commission_rate DECIMAL(5,2) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    amenities TEXT[], -- ['pool', 'gym', 'spa', 'restaurant', 'parking']
    check_in_time TIME DEFAULT '15:00',
    check_out_time TIME DEFAULT '11:00',
    cancellation_policy TEXT,
    contact_person_name VARCHAR(100),
    contact_person_phone VARCHAR(20),
    contact_person_email VARCHAR(255),
    payment_terms VARCHAR(50), -- 'immediate', 'net_30', 'net_15'
    images JSONB DEFAULT '[]', -- Array of image URLs
    documents JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);

-- Hotel Rooms
CREATE TABLE public.hotel_rooms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    hotel_id UUID NOT NULL REFERENCES public.hotel_partners(id) ON DELETE CASCADE,
    room_number VARCHAR(20) NOT NULL,
    room_type VARCHAR(50) NOT NULL, -- single, double, suite, deluxe
    floor_number INTEGER,
    max_occupancy INTEGER NOT NULL,
    size_sqm DECIMAL(8,2),
    bed_type VARCHAR(50), -- single, double, queen, king, twin
    bed_count INTEGER DEFAULT 1,
    base_price_per_night DECIMAL(10,2) NOT NULL,
    weekend_surcharge_percentage DECIMAL(5,2) DEFAULT 0,
    peak_season_surcharge_percentage DECIMAL(5,2) DEFAULT 0,
    amenities TEXT[], -- ['balcony', 'sea_view', 'kitchenette', 'jacuzzi']
    is_accessible BOOLEAN DEFAULT FALSE,
    is_smoking_allowed BOOLEAN DEFAULT FALSE,
    is_available BOOLEAN DEFAULT TRUE,
    images JSONB DEFAULT '[]',
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP,
    
    CONSTRAINT unique_room_per_hotel UNIQUE (hotel_id, room_number)
);

-- Indexes for main tables
CREATE INDEX idx_users_email ON public.users(email);
CREATE INDEX idx_users_phone ON public.users(phone_number);
CREATE INDEX idx_users_type_tier ON public.users(user_type, tier);
CREATE INDEX idx_users_active ON public.users(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_users_created_at ON public.users(created_at);

CREATE INDEX idx_drivers_license ON public.drivers(license_number);
CREATE INDEX idx_drivers_status ON public.drivers(status);
CREATE INDEX idx_drivers_online_available ON public.drivers(is_online, is_available);
CREATE INDEX idx_drivers_fleet_company ON public.drivers(fleet_company_id);
CREATE INDEX idx_drivers_location ON public.drivers USING GIST(current_location);
CREATE INDEX idx_drivers_rating ON public.drivers(rating DESC);

CREATE INDEX idx_vehicles_license_plate ON public.vehicles(license_plate);
CREATE INDEX idx_vehicles_fleet_company ON public.vehicles(fleet_company_id);
CREATE INDEX idx_vehicles_type ON public.vehicles(vehicle_type);
CREATE INDEX idx_vehicles_available ON public.vehicles(is_available) WHERE is_available = TRUE;
CREATE INDEX idx_vehicles_location ON public.vehicles USING GIST(location);

CREATE INDEX idx_fleet_companies_active ON public.fleet_companies(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_fleet_companies_verified ON public.fleet_companies(is_verified) WHERE is_verified = TRUE;

CREATE INDEX idx_hotel_partners_active ON public.hotel_partners(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_hotel_partners_location ON public.hotel_partners USING GIST(location);
CREATE INDEX idx_hotel_partners_tier ON public.hotel_partners(partnership_tier);

CREATE INDEX idx_hotel_rooms_hotel ON public.hotel_rooms(hotel_id);
CREATE INDEX idx_hotel_rooms_available ON public.hotel_rooms(is_available) WHERE is_available = TRUE;
CREATE INDEX idx_hotel_rooms_price ON public.hotel_rooms(base_price_per_night);

-- Row Level Security (RLS) Setup
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.drivers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.vehicles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.fleet_companies ENABLE ROW LEVEL SECURITY;

-- Basic RLS policies (will be expanded in security file)
CREATE POLICY user_own_data ON public.users
    FOR ALL
    TO authenticated_user
    USING (id = current_setting('app.current_user_id')::UUID);

-- Audit triggers for main tables
CREATE TRIGGER audit_users_trigger
    AFTER INSERT OR UPDATE OR DELETE ON public.users
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_drivers_trigger
    AFTER INSERT OR UPDATE OR DELETE ON public.drivers
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_vehicles_trigger
    AFTER INSERT OR UPDATE OR DELETE ON public.vehicles
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_fleet_companies_trigger
    AFTER INSERT OR UPDATE OR DELETE ON public.fleet_companies
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

-- Comments for documentation
COMMENT ON TABLE public.users IS 'Main user table for all platform users (customers, drivers, admins)';
COMMENT ON TABLE public.drivers IS 'Driver-specific information and status';
COMMENT ON TABLE public.vehicles IS 'Vehicle registry with detailed specifications';
COMMENT ON TABLE public.fleet_companies IS 'Fleet company management and details';
COMMENT ON TABLE public.vehicle_leases IS 'Vehicle leasing contracts between owners and fleet companies';
COMMENT ON TABLE public.hotel_partners IS 'Hotel partnership management';
COMMENT ON TABLE public.hotel_rooms IS 'Hotel room inventory and pricing';
