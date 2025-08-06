-- Rides and Booking Tables with Partitioning Strategy

-- Main Rides table (partitioned by date for performance)
CREATE TABLE public.rides (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    driver_id UUID REFERENCES public.drivers(id) ON DELETE SET NULL,
    vehicle_id UUID REFERENCES public.vehicles(id) ON DELETE SET NULL,
    fleet_company_id UUID REFERENCES public.fleet_companies(id) ON DELETE SET NULL,
    
    -- Ride details
    ride_type VARCHAR(20) NOT NULL DEFAULT 'standard', -- standard, premium, vip, airport, long_distance
    customer_tier user_tier NOT NULL DEFAULT 'normal',
    billing_model billing_model NOT NULL DEFAULT 'per_ride',
    
    -- Location information (non-encrypted for normal users)
    pickup_address TEXT NOT NULL,
    pickup_coordinates POINT,
    destination_address TEXT NOT NULL,
    destination_coordinates POINT,
    actual_pickup_coordinates POINT,
    actual_destination_coordinates POINT,
    
    -- Timing
    requested_at TIMESTAMP NOT NULL DEFAULT NOW(),
    scheduled_pickup_time TIMESTAMP, -- For scheduled rides
    estimated_pickup_time TIMESTAMP,
    actual_pickup_time TIMESTAMP,
    estimated_arrival_time TIMESTAMP,
    actual_arrival_time TIMESTAMP,
    completed_at TIMESTAMP,
    cancelled_at TIMESTAMP,
    
    -- Status and progress
    status ride_status NOT NULL DEFAULT 'pending',
    cancellation_reason VARCHAR(100),
    cancelled_by_user_type user_type, -- customer, driver, admin
    
    -- Pricing
    estimated_fare DECIMAL(10,2),
    base_fare DECIMAL(10,2),
    distance_fare DECIMAL(10,2),
    time_fare DECIMAL(10,2),
    surge_multiplier DECIMAL(4,2) DEFAULT 1.00,
    surcharge_amount DECIMAL(8,2) DEFAULT 0.00,
    discount_amount DECIMAL(8,2) DEFAULT 0.00,
    total_fare DECIMAL(10,2),
    currency VARCHAR(3) DEFAULT 'NGN',
    
    -- Distance and duration
    estimated_distance_km DECIMAL(8,2),
    actual_distance_km DECIMAL(8,2),
    estimated_duration_minutes INTEGER,
    actual_duration_minutes INTEGER,
    
    -- VIP specific features
    vip_priority_level INTEGER DEFAULT 0, -- 0 = normal, 1-5 = VIP priority levels
    is_sos_triggered BOOLEAN DEFAULT FALSE,
    sos_triggered_at TIMESTAMP,
    security_escort_required BOOLEAN DEFAULT FALSE,
    route_deviation_alerts BOOLEAN DEFAULT FALSE,
    
    -- Additional services
    has_hotel_booking BOOLEAN DEFAULT FALSE,
    hotel_booking_id UUID, -- Will reference hotel bookings
    has_return_trip BOOLEAN DEFAULT FALSE,
    return_trip_id UUID REFERENCES public.rides(id) ON DELETE SET NULL,
    
    -- Service notes
    special_instructions TEXT,
    customer_notes TEXT,
    driver_notes TEXT,
    internal_notes TEXT, -- For admin/support use
    
    -- Quality metrics
    customer_rating DECIMAL(3,2),
    driver_rating DECIMAL(3,2),
    service_quality_score DECIMAL(3,2),
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
) PARTITION BY RANGE (requested_at);

-- Create monthly partitions for rides (current year + next year)
CREATE TABLE public.rides_2025_01 PARTITION OF public.rides
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE public.rides_2025_02 PARTITION OF public.rides
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');

CREATE TABLE public.rides_2025_03 PARTITION OF public.rides
    FOR VALUES FROM ('2025-03-01') TO ('2025-04-01');

CREATE TABLE public.rides_2025_04 PARTITION OF public.rides
    FOR VALUES FROM ('2025-04-01') TO ('2025-05-01');

CREATE TABLE public.rides_2025_05 PARTITION OF public.rides
    FOR VALUES FROM ('2025-05-01') TO ('2025-06-01');

CREATE TABLE public.rides_2025_06 PARTITION OF public.rides
    FOR VALUES FROM ('2025-06-01') TO ('2025-07-01');

CREATE TABLE public.rides_2025_07 PARTITION OF public.rides
    FOR VALUES FROM ('2025-07-01') TO ('2025-08-01');

CREATE TABLE public.rides_2025_08 PARTITION OF public.rides
    FOR VALUES FROM ('2025-08-01') TO ('2025-09-01');

CREATE TABLE public.rides_2025_09 PARTITION OF public.rides
    FOR VALUES FROM ('2025-09-01') TO ('2025-10-01');

CREATE TABLE public.rides_2025_10 PARTITION OF public.rides
    FOR VALUES FROM ('2025-10-01') TO ('2025-11-01');

CREATE TABLE public.rides_2025_11 PARTITION OF public.rides
    FOR VALUES FROM ('2025-11-01') TO ('2025-12-01');

CREATE TABLE public.rides_2025_12 PARTITION OF public.rides
    FOR VALUES FROM ('2025-12-01') TO ('2026-01-01');

-- Function to automatically create monthly ride partitions
CREATE OR REPLACE FUNCTION create_monthly_ride_partition(start_date DATE)
RETURNS VOID AS $$
DECLARE
    partition_name TEXT;
    end_date DATE;
BEGIN
    end_date := start_date + INTERVAL '1 month';
    partition_name := 'rides_' || to_char(start_date, 'YYYY_MM');
    
    EXECUTE format('CREATE TABLE IF NOT EXISTS public.%I PARTITION OF public.rides
                    FOR VALUES FROM (%L) TO (%L)',
                   partition_name, start_date, end_date);
                   
    -- Create indexes on the new partition
    EXECUTE format('CREATE INDEX IF NOT EXISTS idx_%I_customer_id ON public.%I(customer_id)', 
                   partition_name, partition_name);
    EXECUTE format('CREATE INDEX IF NOT EXISTS idx_%I_driver_id ON public.%I(driver_id)', 
                   partition_name, partition_name);
    EXECUTE format('CREATE INDEX IF NOT EXISTS idx_%I_status ON public.%I(status)', 
                   partition_name, partition_name);
    EXECUTE format('CREATE INDEX IF NOT EXISTS idx_%I_vip_priority ON public.%I(vip_priority_level) WHERE vip_priority_level > 0', 
                   partition_name, partition_name);
END;
$$ LANGUAGE plpgsql;

-- Ride Offers (driver responses to ride requests)
CREATE TABLE public.ride_offers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ride_id UUID NOT NULL REFERENCES public.rides(id) ON DELETE CASCADE,
    driver_id UUID NOT NULL REFERENCES public.drivers(id) ON DELETE CASCADE,
    
    offered_fare DECIMAL(10,2),
    estimated_pickup_time TIMESTAMP NOT NULL,
    estimated_arrival_time TIMESTAMP NOT NULL,
    driver_notes TEXT,
    
    status VARCHAR(20) DEFAULT 'pending', -- pending, accepted, rejected, expired, withdrawn
    offered_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,
    responded_at TIMESTAMP,
    
    CONSTRAINT unique_driver_offer_per_ride UNIQUE (ride_id, driver_id)
);

-- Real-time Ride Tracking
CREATE TABLE public.ride_tracking (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ride_id UUID NOT NULL REFERENCES public.rides(id) ON DELETE CASCADE,
    
    -- Location data (non-VIP users only - VIP uses encrypted schema)
    current_coordinates POINT,
    current_address TEXT,
    heading_degrees INTEGER CHECK (heading_degrees >= 0 AND heading_degrees <= 360),
    speed_kmh DECIMAL(6,2),
    
    -- Status updates
    tracking_status VARCHAR(20), -- en_route_pickup, arrived_pickup, en_route_destination, arrived_destination
    estimated_time_to_pickup INTEGER, -- minutes
    estimated_time_to_destination INTEGER, -- minutes
    
    -- Driver status
    driver_status VARCHAR(20), -- driving, stopped, waiting, arrived
    traffic_conditions VARCHAR(20), -- light, moderate, heavy, severe
    
    recorded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    INDEX idx_tracking_ride_recorded (ride_id, recorded_at DESC)
);

-- Ride Ratings and Reviews
CREATE TABLE public.ride_ratings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ride_id UUID NOT NULL REFERENCES public.rides(id) ON DELETE CASCADE,
    rated_by_user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    rated_user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE, -- Driver or customer being rated
    
    rating DECIMAL(3,2) NOT NULL CHECK (rating >= 1.0 AND rating <= 5.0),
    review_text TEXT,
    rating_categories JSONB, -- {"punctuality": 5, "cleanliness": 4, "safety": 5, "communication": 4}
    
    would_recommend BOOLEAN,
    is_anonymous BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT unique_rating_per_ride_user UNIQUE (ride_id, rated_by_user_id, rated_user_id)
);

-- Hotel Bookings
CREATE TABLE public.hotel_bookings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    hotel_id UUID NOT NULL REFERENCES public.hotel_partners(id) ON DELETE CASCADE,
    room_id UUID NOT NULL REFERENCES public.hotel_rooms(id) ON DELETE CASCADE,
    ride_booking_id UUID REFERENCES public.rides(id) ON DELETE SET NULL, -- Associated ride
    
    -- Booking details
    check_in_date DATE NOT NULL,
    check_out_date DATE NOT NULL,
    nights_count INTEGER NOT NULL,
    guest_count INTEGER NOT NULL DEFAULT 1,
    adult_count INTEGER NOT NULL DEFAULT 1,
    child_count INTEGER DEFAULT 0,
    
    -- Pricing
    room_rate_per_night DECIMAL(10,2) NOT NULL,
    total_room_cost DECIMAL(10,2) NOT NULL,
    taxes_and_fees DECIMAL(10,2) DEFAULT 0.00,
    discount_amount DECIMAL(8,2) DEFAULT 0.00,
    total_amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'NGN',
    
    -- Status
    status VARCHAR(20) DEFAULT 'confirmed', -- confirmed, checked_in, checked_out, cancelled, no_show
    booking_reference VARCHAR(50) UNIQUE NOT NULL,
    hotel_confirmation_number VARCHAR(50),
    
    -- Guest information
    primary_guest_name VARCHAR(200) NOT NULL,
    guest_phone VARCHAR(20) NOT NULL,
    guest_email VARCHAR(255) NOT NULL,
    special_requests TEXT,
    
    -- Service integration
    airport_transfer_required BOOLEAN DEFAULT FALSE,
    pickup_service_booked BOOLEAN DEFAULT FALSE,
    concierge_services JSONB DEFAULT '{}',
    
    -- Dates
    booked_at TIMESTAMP DEFAULT NOW(),
    cancelled_at TIMESTAMP,
    checked_in_at TIMESTAMP,
    checked_out_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);

-- Emergency Contacts
CREATE TABLE public.emergency_contacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    
    contact_name VARCHAR(100) NOT NULL,
    relationship VARCHAR(50) NOT NULL, -- spouse, parent, sibling, friend, colleague
    phone_number VARCHAR(20) NOT NULL,
    email VARCHAR(255),
    address TEXT,
    
    is_primary BOOLEAN DEFAULT FALSE,
    is_medical_contact BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Notification preferences
    notify_on_emergency BOOLEAN DEFAULT TRUE,
    notify_on_ride_start BOOLEAN DEFAULT FALSE,
    notify_on_ride_delay BOOLEAN DEFAULT FALSE,
    notify_on_route_change BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);

-- Indexes for ride-related tables
CREATE INDEX idx_rides_customer_id ON public.rides(customer_id);
CREATE INDEX idx_rides_driver_id ON public.rides(driver_id);
CREATE INDEX idx_rides_vehicle_id ON public.rides(vehicle_id);
CREATE INDEX idx_rides_fleet_company_id ON public.rides(fleet_company_id);
CREATE INDEX idx_rides_status ON public.rides(status);
CREATE INDEX idx_rides_requested_at ON public.rides(requested_at DESC);
CREATE INDEX idx_rides_ride_type ON public.rides(ride_type);
CREATE INDEX idx_rides_customer_tier ON public.rides(customer_tier);
CREATE INDEX idx_rides_billing_model ON public.rides(billing_model);
CREATE INDEX idx_rides_vip_priority ON public.rides(vip_priority_level) WHERE vip_priority_level > 0;
CREATE INDEX idx_rides_sos_triggered ON public.rides(is_sos_triggered) WHERE is_sos_triggered = TRUE;
CREATE INDEX idx_rides_scheduled_pickup ON public.rides(scheduled_pickup_time) WHERE scheduled_pickup_time IS NOT NULL;
CREATE INDEX idx_rides_pickup_coordinates ON public.rides USING GIST(pickup_coordinates);
CREATE INDEX idx_rides_destination_coordinates ON public.rides USING GIST(destination_coordinates);

CREATE INDEX idx_ride_offers_ride_id ON public.ride_offers(ride_id);
CREATE INDEX idx_ride_offers_driver_id ON public.ride_offers(driver_id);
CREATE INDEX idx_ride_offers_status ON public.ride_offers(status);
CREATE INDEX idx_ride_offers_expires_at ON public.ride_offers(expires_at);

CREATE INDEX idx_ride_tracking_ride_id ON public.ride_tracking(ride_id);
CREATE INDEX idx_ride_tracking_recorded_at ON public.ride_tracking(recorded_at DESC);

CREATE INDEX idx_ride_ratings_ride_id ON public.ride_ratings(ride_id);
CREATE INDEX idx_ride_ratings_rated_user_id ON public.ride_ratings(rated_user_id);
CREATE INDEX idx_ride_ratings_rating ON public.ride_ratings(rating);

CREATE INDEX idx_hotel_bookings_customer_id ON public.hotel_bookings(customer_id);
CREATE INDEX idx_hotel_bookings_hotel_id ON public.hotel_bookings(hotel_id);
CREATE INDEX idx_hotel_bookings_room_id ON public.hotel_bookings(room_id);
CREATE INDEX idx_hotel_bookings_status ON public.hotel_bookings(status);
CREATE INDEX idx_hotel_bookings_check_in_date ON public.hotel_bookings(check_in_date);
CREATE INDEX idx_hotel_bookings_check_out_date ON public.hotel_bookings(check_out_date);
CREATE INDEX idx_hotel_bookings_booked_at ON public.hotel_bookings(booked_at);
CREATE INDEX idx_hotel_bookings_ride_booking_id ON public.hotel_bookings(ride_booking_id);

CREATE INDEX idx_emergency_contacts_user_id ON public.emergency_contacts(user_id);
CREATE INDEX idx_emergency_contacts_primary ON public.emergency_contacts(is_primary) WHERE is_primary = TRUE;

-- Add foreign key reference from rides to hotel bookings
ALTER TABLE public.rides ADD CONSTRAINT fk_rides_hotel_booking
    FOREIGN KEY (hotel_booking_id) REFERENCES public.hotel_bookings(id) ON DELETE SET NULL;

-- Row Level Security for ride tables
ALTER TABLE public.rides ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ride_tracking ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.hotel_bookings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.emergency_contacts ENABLE ROW LEVEL SECURITY;

-- Audit triggers
CREATE TRIGGER audit_rides_trigger
    AFTER INSERT OR UPDATE OR DELETE ON public.rides
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_hotel_bookings_trigger
    AFTER INSERT OR UPDATE OR DELETE ON public.hotel_bookings
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

-- Automated partition creation (run monthly)
CREATE OR REPLACE FUNCTION create_next_month_partitions()
RETURNS VOID AS $$
DECLARE
    next_month DATE;
BEGIN
    next_month := date_trunc('month', NOW() + INTERVAL '2 months');
    
    -- Create ride partition
    PERFORM create_monthly_ride_partition(next_month);
    
    -- Create VIP location partition
    PERFORM vip_data.create_monthly_location_partition(next_month);
END;
$$ LANGUAGE plpgsql;

-- Comments
COMMENT ON TABLE public.rides IS 'Main rides table partitioned by month for performance';
COMMENT ON TABLE public.ride_offers IS 'Driver offers for ride requests';
COMMENT ON TABLE public.ride_tracking IS 'Real-time ride location tracking for non-VIP users';
COMMENT ON TABLE public.ride_ratings IS 'Ride ratings and reviews between customers and drivers';
COMMENT ON TABLE public.hotel_bookings IS 'Hotel booking integration with ride services';
COMMENT ON TABLE public.emergency_contacts IS 'Emergency contact information for users';
