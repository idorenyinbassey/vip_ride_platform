-- VIP Data Schema - Encrypted and Isolated VIP User Data
-- This schema contains sensitive VIP user information with enhanced security

-- VIP User Profiles (Encrypted sensitive data)
CREATE TABLE vip_data.vip_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    
    -- Encrypted personal information
    encrypted_full_address TEXT, -- Encrypted home/billing address
    encrypted_emergency_contacts TEXT, -- Encrypted emergency contact details
    encrypted_medical_info TEXT, -- Encrypted medical conditions/allergies
    encrypted_preferences TEXT, -- Encrypted personal preferences
    encrypted_payment_info TEXT, -- Encrypted payment method details
    encrypted_id_documents TEXT, -- Encrypted government ID information
    
    -- VIP-specific features
    dedicated_concierge_id UUID, -- Assigned VIP concierge
    priority_level INTEGER DEFAULT 1 CHECK (priority_level >= 1 AND priority_level <= 5),
    background_check_level VARCHAR(20) DEFAULT 'enhanced', -- standard, enhanced, premium
    security_clearance_level VARCHAR(20), -- government, corporate, celebrity
    
    -- Risk assessment
    threat_assessment_level VARCHAR(20) DEFAULT 'low', -- low, medium, high, critical
    security_notes TEXT, -- Encrypted security-related notes
    
    -- Access controls
    two_factor_required BOOLEAN DEFAULT TRUE,
    biometric_required BOOLEAN DEFAULT FALSE,
    device_restriction BOOLEAN DEFAULT TRUE,
    ip_whitelist TEXT[], -- Allowed IP addresses
    
    -- Audit fields
    last_security_review TIMESTAMP,
    next_security_review TIMESTAMP,
    security_reviewed_by UUID,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP,
    
    CONSTRAINT unique_vip_profile_per_user UNIQUE (user_id)
);

-- VIP Location Tracking (Encrypted GPS data)
CREATE TABLE vip_data.vip_location_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    ride_id UUID, -- Will reference rides table
    
    -- Encrypted location data
    encrypted_coordinates TEXT NOT NULL, -- Encrypted lat/lng
    encrypted_address TEXT, -- Encrypted reverse-geocoded address
    
    -- Location metadata
    accuracy_meters DECIMAL(8,2),
    speed_kmh DECIMAL(6,2),
    heading_degrees INTEGER CHECK (heading_degrees >= 0 AND heading_degrees <= 360),
    altitude_meters DECIMAL(8,2),
    
    -- Context
    location_type VARCHAR(20), -- pickup, dropoff, waypoint, emergency, routine
    is_safe_zone BOOLEAN DEFAULT TRUE,
    geofence_alerts TEXT[], -- Array of triggered geofence alert IDs
    
    -- Security flags
    is_panic_mode BOOLEAN DEFAULT FALSE,
    is_emergency_location BOOLEAN DEFAULT FALSE,
    location_shared_with TEXT[], -- Array of user IDs who can see this location
    
    recorded_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
) PARTITION BY RANGE (recorded_at);

-- VIP Communication Logs (Encrypted messages and calls)
CREATE TABLE vip_data.vip_communications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    ride_id UUID, -- Will reference rides table
    
    communication_type VARCHAR(20) NOT NULL, -- call, message, video, emergency
    direction VARCHAR(10) NOT NULL, -- inbound, outbound
    
    -- Encrypted communication data
    encrypted_content TEXT, -- Message content or call summary
    encrypted_participants TEXT, -- Other participants (drivers, support, emergency)
    
    -- Communication metadata
    duration_seconds INTEGER, -- For calls
    quality_score DECIMAL(3,2), -- Call quality or message delivery score
    encryption_key_id VARCHAR(100), -- Reference to encryption key used
    
    -- Security context
    is_emergency_communication BOOLEAN DEFAULT FALSE,
    is_recorded BOOLEAN DEFAULT FALSE, -- Whether call/video was recorded
    recording_location TEXT, -- Encrypted path to recording
    
    -- Compliance
    retention_until TIMESTAMP, -- When this record should be purged
    legal_hold BOOLEAN DEFAULT FALSE, -- Prevents deletion if under legal hold
    
    initiated_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- VIP Emergency Events
CREATE TABLE vip_data.vip_emergency_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    ride_id UUID, -- Will reference rides table
    
    event_type VARCHAR(30) NOT NULL, -- panic_button, medical, security, vehicle_breakdown
    severity_level INTEGER NOT NULL CHECK (severity_level >= 1 AND severity_level <= 5),
    
    -- Encrypted event details
    encrypted_location TEXT NOT NULL, -- Encrypted emergency location
    encrypted_description TEXT, -- Encrypted event description
    encrypted_response_notes TEXT, -- Encrypted response team notes
    
    -- Response information
    response_team_dispatched BOOLEAN DEFAULT FALSE,
    estimated_response_time_minutes INTEGER,
    actual_response_time_minutes INTEGER,
    response_team_members TEXT[], -- Array of responder IDs
    
    -- Emergency contacts notified
    contacts_notified TEXT[], -- Array of contact IDs notified
    authorities_contacted BOOLEAN DEFAULT FALSE,
    authority_case_number VARCHAR(100),
    
    -- Resolution
    resolution_status VARCHAR(20) DEFAULT 'open', -- open, investigating, resolved, false_alarm
    resolution_time TIMESTAMP,
    resolution_summary TEXT, -- Encrypted resolution details
    
    -- Follow-up
    follow_up_required BOOLEAN DEFAULT FALSE,
    follow_up_scheduled TIMESTAMP,
    incident_report_filed BOOLEAN DEFAULT FALSE,
    
    triggered_at TIMESTAMP NOT NULL,
    acknowledged_at TIMESTAMP,
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- VIP Service Preferences (Encrypted preferences)
CREATE TABLE vip_data.vip_service_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    
    -- Encrypted preference data
    encrypted_vehicle_preferences TEXT, -- Preferred vehicle types, features
    encrypted_driver_preferences TEXT, -- Preferred driver characteristics
    encrypted_route_preferences TEXT, -- Preferred routes, areas to avoid
    encrypted_dietary_restrictions TEXT, -- For hotel/dining services
    encrypted_accessibility_needs TEXT, -- Special accessibility requirements
    encrypted_business_preferences TEXT, -- Business travel specific needs
    
    -- Service level preferences
    preferred_pickup_buffer_minutes INTEGER DEFAULT 5,
    preferred_driver_rating_minimum DECIMAL(3,2) DEFAULT 4.5,
    allow_driver_substitution BOOLEAN DEFAULT FALSE,
    require_vehicle_inspection BOOLEAN DEFAULT TRUE,
    
    -- Privacy preferences
    location_sharing_level VARCHAR(20) DEFAULT 'minimal', -- none, minimal, selective, full
    communication_preferences JSONB DEFAULT '{}', -- How they prefer to be contacted
    data_retention_preference VARCHAR(20) DEFAULT 'minimum', -- minimum, standard, extended
    
    -- Notification preferences
    real_time_tracking_alerts BOOLEAN DEFAULT TRUE,
    geofence_notifications BOOLEAN DEFAULT TRUE,
    emergency_auto_dial BOOLEAN DEFAULT TRUE,
    family_notifications BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT unique_vip_preferences_per_user UNIQUE (user_id)
);

-- VIP Access Logs (Who accessed VIP data when)
CREATE TABLE vip_data.vip_data_access_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vip_user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    accessor_user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    
    access_type VARCHAR(30) NOT NULL, -- view, edit, export, emergency_access
    data_category VARCHAR(50) NOT NULL, -- profile, location, communications, preferences
    specific_field VARCHAR(100), -- Which field was accessed
    
    -- Access context
    access_reason VARCHAR(100) NOT NULL, -- customer_request, emergency, audit, support
    business_justification TEXT, -- Required justification for access
    supervisor_approval_id UUID, -- Required for sensitive access
    
    -- Technical details
    ip_address INET,
    user_agent TEXT,
    session_id VARCHAR(100),
    api_endpoint TEXT,
    
    -- Data accessed
    records_accessed INTEGER DEFAULT 1,
    data_exported BOOLEAN DEFAULT FALSE,
    export_format VARCHAR(20), -- pdf, csv, json
    
    accessed_at TIMESTAMP NOT NULL DEFAULT NOW(),
    session_ended_at TIMESTAMP
);

-- Create partitions for VIP location history (monthly partitions)
CREATE TABLE vip_data.vip_location_history_2025_01 PARTITION OF vip_data.vip_location_history
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE vip_data.vip_location_history_2025_02 PARTITION OF vip_data.vip_location_history
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');

CREATE TABLE vip_data.vip_location_history_2025_03 PARTITION OF vip_data.vip_location_history
    FOR VALUES FROM ('2025-03-01') TO ('2025-04-01');

-- Function to automatically create monthly partitions
CREATE OR REPLACE FUNCTION vip_data.create_monthly_location_partition(start_date DATE)
RETURNS VOID AS $$
DECLARE
    partition_name TEXT;
    end_date DATE;
BEGIN
    end_date := start_date + INTERVAL '1 month';
    partition_name := 'vip_location_history_' || to_char(start_date, 'YYYY_MM');
    
    EXECUTE format('CREATE TABLE IF NOT EXISTS vip_data.%I PARTITION OF vip_data.vip_location_history
                    FOR VALUES FROM (%L) TO (%L)',
                   partition_name, start_date, end_date);
END;
$$ LANGUAGE plpgsql;

-- Indexes for VIP tables
CREATE INDEX idx_vip_profiles_user_id ON vip_data.vip_profiles(user_id);
CREATE INDEX idx_vip_profiles_priority ON vip_data.vip_profiles(priority_level DESC);
CREATE INDEX idx_vip_profiles_threat_level ON vip_data.vip_profiles(threat_assessment_level);

CREATE INDEX idx_vip_location_user_id ON vip_data.vip_location_history(user_id);
CREATE INDEX idx_vip_location_recorded_at ON vip_data.vip_location_history(recorded_at DESC);
CREATE INDEX idx_vip_location_emergency ON vip_data.vip_location_history(is_emergency_location) WHERE is_emergency_location = TRUE;

CREATE INDEX idx_vip_communications_user_id ON vip_data.vip_communications(user_id);
CREATE INDEX idx_vip_communications_emergency ON vip_data.vip_communications(is_emergency_communication) WHERE is_emergency_communication = TRUE;
CREATE INDEX idx_vip_communications_initiated_at ON vip_data.vip_communications(initiated_at DESC);

CREATE INDEX idx_vip_emergency_user_id ON vip_data.vip_emergency_events(user_id);
CREATE INDEX idx_vip_emergency_severity ON vip_data.vip_emergency_events(severity_level DESC);
CREATE INDEX idx_vip_emergency_status ON vip_data.vip_emergency_events(resolution_status);
CREATE INDEX idx_vip_emergency_triggered_at ON vip_data.vip_emergency_events(triggered_at DESC);

CREATE INDEX idx_vip_access_log_vip_user ON vip_data.vip_data_access_log(vip_user_id);
CREATE INDEX idx_vip_access_log_accessor ON vip_data.vip_data_access_log(accessor_user_id);
CREATE INDEX idx_vip_access_log_accessed_at ON vip_data.vip_data_access_log(accessed_at DESC);

-- Row Level Security for VIP schema
ALTER TABLE vip_data.vip_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE vip_data.vip_location_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE vip_data.vip_communications ENABLE ROW LEVEL SECURITY;
ALTER TABLE vip_data.vip_emergency_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE vip_data.vip_service_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE vip_data.vip_data_access_log ENABLE ROW LEVEL SECURITY;

-- VIP Access logging triggers
CREATE TRIGGER vip_access_log_profiles
    AFTER SELECT OR INSERT OR UPDATE OR DELETE ON vip_data.vip_profiles
    FOR EACH ROW EXECUTE FUNCTION log_vip_access();

CREATE TRIGGER vip_access_log_location
    AFTER SELECT OR INSERT OR UPDATE OR DELETE ON vip_data.vip_location_history
    FOR EACH ROW EXECUTE FUNCTION log_vip_access();

CREATE TRIGGER vip_access_log_communications
    AFTER SELECT OR INSERT OR UPDATE OR DELETE ON vip_data.vip_communications
    FOR EACH ROW EXECUTE FUNCTION log_vip_access();

-- Audit triggers for VIP tables
CREATE TRIGGER audit_vip_profiles_trigger
    AFTER INSERT OR UPDATE OR DELETE ON vip_data.vip_profiles
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_vip_emergency_trigger
    AFTER INSERT OR UPDATE OR DELETE ON vip_data.vip_emergency_events
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

-- Data retention policies
CREATE OR REPLACE FUNCTION vip_data.cleanup_expired_vip_data()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER := 0;
BEGIN
    -- Delete VIP communications past retention period
    DELETE FROM vip_data.vip_communications 
    WHERE retention_until < NOW() AND legal_hold = FALSE;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    -- Archive old location data (older than 2 years)
    INSERT INTO archive.vip_location_archive 
    SELECT * FROM vip_data.vip_location_history 
    WHERE recorded_at < NOW() - INTERVAL '2 years';
    
    DELETE FROM vip_data.vip_location_history 
    WHERE recorded_at < NOW() - INTERVAL '2 years';
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Comments
COMMENT ON SCHEMA vip_data IS 'Isolated schema for VIP user data with enhanced encryption and security';
COMMENT ON TABLE vip_data.vip_profiles IS 'Encrypted VIP user profiles with enhanced security information';
COMMENT ON TABLE vip_data.vip_location_history IS 'Partitioned table for encrypted VIP location tracking';
COMMENT ON TABLE vip_data.vip_communications IS 'Encrypted VIP communication logs';
COMMENT ON TABLE vip_data.vip_emergency_events IS 'VIP emergency event tracking and response';
COMMENT ON TABLE vip_data.vip_service_preferences IS 'Encrypted VIP service preferences and requirements';
COMMENT ON TABLE vip_data.vip_data_access_log IS 'Audit trail for all VIP data access';
