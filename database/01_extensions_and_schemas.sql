-- VIP Ride-Hailing Platform - PostgreSQL Database Schema
-- Extensions and Schema Setup

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "hstore";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";
CREATE EXTENSION IF NOT EXISTS "unaccent";

-- Create separate schemas for data isolation
CREATE SCHEMA IF NOT EXISTS public;
CREATE SCHEMA IF NOT EXISTS vip_data;
CREATE SCHEMA IF NOT EXISTS audit;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS archive;

-- Grant appropriate permissions
GRANT USAGE ON SCHEMA public TO PUBLIC;
GRANT USAGE ON SCHEMA vip_data TO vip_admin, vip_operator;
GRANT USAGE ON SCHEMA audit TO audit_admin, system_admin;
GRANT USAGE ON SCHEMA analytics TO analytics_user, system_admin;
GRANT USAGE ON SCHEMA archive TO archive_admin, system_admin;

-- Create custom types for better data integrity
CREATE TYPE user_tier AS ENUM ('normal', 'premium', 'vip');
CREATE TYPE user_type AS ENUM ('customer', 'driver', 'fleet_admin', 'admin');
CREATE TYPE ride_status AS ENUM ('pending', 'driver_assigned', 'driver_arrived', 'in_progress', 'completed', 'cancelled', 'emergency');
CREATE TYPE payment_status AS ENUM ('pending', 'processing', 'completed', 'failed', 'refunded', 'disputed');
CREATE TYPE driver_category AS ENUM ('private_driver', 'fleet_driver', 'owner_operator');
CREATE TYPE vehicle_type AS ENUM ('sedan', 'suv', 'luxury', 'van', 'premium');
CREATE TYPE billing_model AS ENUM ('per_ride', 'time_based', 'distance_based', 'flat_rate', 'surge_pricing');
CREATE TYPE subscription_tier AS ENUM ('basic', 'premium', 'elite');
CREATE TYPE partnership_tier AS ENUM ('standard', 'preferred', 'exclusive');

-- Create encryption key management
CREATE OR REPLACE FUNCTION generate_encryption_key() 
RETURNS TEXT AS $$
BEGIN
    RETURN encode(gen_random_bytes(32), 'hex');
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- VIP data encryption functions
CREATE OR REPLACE FUNCTION encrypt_vip_data(data TEXT, key_id TEXT DEFAULT 'vip_master_key')
RETURNS TEXT AS $$
BEGIN
    -- In production, retrieve actual key from secure key management system
    RETURN pgp_sym_encrypt(data, key_id);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION decrypt_vip_data(encrypted_data TEXT, key_id TEXT DEFAULT 'vip_master_key')
RETURNS TEXT AS $$
BEGIN
    -- In production, retrieve actual key from secure key management system
    RETURN pgp_sym_decrypt(encrypted_data, key_id);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Audit logging function
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit.audit_log (
            table_name, operation, new_data, user_id, timestamp, ip_address
        ) VALUES (
            TG_TABLE_NAME, TG_OP, to_jsonb(NEW), 
            current_setting('app.current_user_id', true)::UUID,
            NOW(), 
            current_setting('app.client_ip', true)
        );
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit.audit_log (
            table_name, operation, old_data, new_data, user_id, timestamp, ip_address
        ) VALUES (
            TG_TABLE_NAME, TG_OP, to_jsonb(OLD), to_jsonb(NEW),
            current_setting('app.current_user_id', true)::UUID,
            NOW(),
            current_setting('app.client_ip', true)
        );
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit.audit_log (
            table_name, operation, old_data, user_id, timestamp, ip_address
        ) VALUES (
            TG_TABLE_NAME, TG_OP, to_jsonb(OLD),
            current_setting('app.current_user_id', true)::UUID,
            NOW(),
            current_setting('app.client_ip', true)
        );
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- VIP access logging function
CREATE OR REPLACE FUNCTION log_vip_access()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit.vip_access_log (
        user_id, table_name, operation, accessed_at, ip_address, user_agent
    ) VALUES (
        current_setting('app.current_user_id', true)::UUID,
        TG_TABLE_NAME,
        TG_OP,
        NOW(),
        current_setting('app.client_ip', true),
        current_setting('app.user_agent', true)
    );
    
    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
        RETURN NEW;
    ELSE
        RETURN OLD;
    END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Comment on schemas
COMMENT ON SCHEMA public IS 'Main application schema for non-sensitive data';
COMMENT ON SCHEMA vip_data IS 'Isolated schema for VIP user sensitive data with enhanced security';
COMMENT ON SCHEMA audit IS 'Audit logging and compliance tracking schema';
COMMENT ON SCHEMA analytics IS 'Business intelligence and analytics data';
COMMENT ON SCHEMA archive IS 'Historical data archive for long-term storage';
