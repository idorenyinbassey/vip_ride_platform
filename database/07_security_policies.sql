-- Row Level Security (RLS) Policies and Advanced Security Configuration

-- Create database roles for different access levels
-- Note: These should be created by a database administrator

-- Role definitions (to be created manually)
/*
CREATE ROLE authenticated_user;
CREATE ROLE vip_admin;
CREATE ROLE vip_operator;
CREATE ROLE fleet_admin;
CREATE ROLE driver_user;
CREATE ROLE customer_user;
CREATE ROLE audit_admin;
CREATE ROLE analytics_user;
CREATE ROLE system_admin;
CREATE ROLE emergency_responder;
CREATE ROLE support_agent;
CREATE ROLE compliance_officer;
*/

-- Grant schema usage permissions
-- GRANT USAGE ON SCHEMA public TO authenticated_user, customer_user, driver_user, fleet_admin;
-- GRANT USAGE ON SCHEMA vip_data TO vip_admin, vip_operator, emergency_responder;
-- GRANT USAGE ON SCHEMA audit TO audit_admin, compliance_officer, system_admin;

-- =======================
-- PUBLIC SCHEMA RLS POLICIES
-- =======================

-- Users table policies
DROP POLICY IF EXISTS user_own_data ON public.users;
CREATE POLICY user_own_data ON public.users
    FOR ALL
    TO authenticated_user
    USING (
        id = current_setting('app.current_user_id', true)::UUID
        OR current_setting('app.user_role', true) IN ('admin', 'support_agent')
    );

CREATE POLICY user_public_data_select ON public.users
    FOR SELECT
    TO authenticated_user
    USING (
        -- Drivers can see basic info of customers they're serving
        EXISTS (
            SELECT 1 FROM public.rides r 
            WHERE (r.customer_id = users.id OR r.driver_id = users.id)
            AND (r.customer_id = current_setting('app.current_user_id', true)::UUID 
                 OR r.driver_id = current_setting('app.current_user_id', true)::UUID)
            AND r.status IN ('driver_assigned', 'driver_arrived', 'in_progress')
        )
        OR 
        -- Fleet admins can see their drivers
        (current_setting('app.user_role', true) = 'fleet_admin' 
         AND EXISTS (
             SELECT 1 FROM public.drivers d 
             JOIN public.fleet_companies fc ON d.fleet_company_id = fc.id
             WHERE d.user_id = users.id 
             AND fc.id = current_setting('app.fleet_company_id', true)::UUID
         ))
    );

-- Drivers table policies
CREATE POLICY driver_own_data ON public.drivers
    FOR ALL
    TO driver_user
    USING (user_id = current_setting('app.current_user_id', true)::UUID);

CREATE POLICY driver_fleet_admin_access ON public.drivers
    FOR ALL
    TO fleet_admin
    USING (
        fleet_company_id = current_setting('app.fleet_company_id', true)::UUID
    );

CREATE POLICY driver_customer_view ON public.drivers
    FOR SELECT
    TO customer_user
    USING (
        -- Customers can see basic info of drivers assigned to their rides
        EXISTS (
            SELECT 1 FROM public.rides r 
            WHERE r.driver_id = drivers.id 
            AND r.customer_id = current_setting('app.current_user_id', true)::UUID
            AND r.status IN ('driver_assigned', 'driver_arrived', 'in_progress')
        )
    );

-- Vehicles table policies
CREATE POLICY vehicle_fleet_access ON public.vehicles
    FOR ALL
    TO fleet_admin
    USING (fleet_company_id = current_setting('app.fleet_company_id', true)::UUID);

CREATE POLICY vehicle_driver_access ON public.vehicles
    FOR SELECT
    TO driver_user
    USING (
        current_driver_id = (
            SELECT id FROM public.drivers 
            WHERE user_id = current_setting('app.current_user_id', true)::UUID
        )
    );

CREATE POLICY vehicle_customer_view ON public.vehicles
    FOR SELECT
    TO customer_user
    USING (
        -- Customers can see vehicle info for their current rides
        EXISTS (
            SELECT 1 FROM public.rides r 
            WHERE r.vehicle_id = vehicles.id 
            AND r.customer_id = current_setting('app.current_user_id', true)::UUID
            AND r.status IN ('driver_assigned', 'driver_arrived', 'in_progress')
        )
    );

-- Fleet companies table policies
CREATE POLICY fleet_company_own_data ON public.fleet_companies
    FOR ALL
    TO fleet_admin
    USING (id = current_setting('app.fleet_company_id', true)::UUID);

CREATE POLICY fleet_company_public_view ON public.fleet_companies
    FOR SELECT
    TO authenticated_user
    USING (is_active = TRUE AND is_verified = TRUE);

-- Rides table policies
CREATE POLICY ride_customer_access ON public.rides
    FOR ALL
    TO customer_user
    USING (customer_id = current_setting('app.current_user_id', true)::UUID);

CREATE POLICY ride_driver_access ON public.rides
    FOR ALL
    TO driver_user
    USING (
        driver_id = (
            SELECT id FROM public.drivers 
            WHERE user_id = current_setting('app.current_user_id', true)::UUID
        )
    );

CREATE POLICY ride_fleet_access ON public.rides
    FOR SELECT
    TO fleet_admin
    USING (
        fleet_company_id = current_setting('app.fleet_company_id', true)::UUID
    );

-- Special VIP ride access - only for authorized personnel
CREATE POLICY ride_vip_emergency_access ON public.rides
    FOR ALL
    TO emergency_responder
    USING (
        vip_priority_level > 0 
        AND (is_sos_triggered = TRUE OR status = 'emergency')
    );

-- Ride tracking policies
CREATE POLICY ride_tracking_participant_access ON public.ride_tracking
    FOR ALL
    TO authenticated_user
    USING (
        EXISTS (
            SELECT 1 FROM public.rides r 
            WHERE r.id = ride_tracking.ride_id 
            AND (r.customer_id = current_setting('app.current_user_id', true)::UUID
                 OR r.driver_id = (
                     SELECT id FROM public.drivers 
                     WHERE user_id = current_setting('app.current_user_id', true)::UUID
                 ))
        )
    );

-- Hotel bookings policies
CREATE POLICY hotel_booking_customer_access ON public.hotel_bookings
    FOR ALL
    TO customer_user
    USING (customer_id = current_setting('app.current_user_id', true)::UUID);

CREATE POLICY hotel_booking_hotel_access ON public.hotel_bookings
    FOR SELECT
    TO authenticated_user
    USING (
        -- Hotel staff can see bookings for their hotel
        hotel_id = current_setting('app.hotel_partner_id', true)::UUID
        AND current_setting('app.user_role', true) = 'hotel_staff'
    );

-- Payments policies
CREATE POLICY payment_payer_access ON public.payments
    FOR ALL
    TO authenticated_user
    USING (
        payer_id = current_setting('app.current_user_id', true)::UUID
        OR payee_id = current_setting('app.current_user_id', true)::UUID
    );

CREATE POLICY payment_fleet_commission_access ON public.payments
    FOR SELECT
    TO fleet_admin
    USING (
        payment_type = 'commission'
        AND EXISTS (
            SELECT 1 FROM public.rides r 
            WHERE r.id = payments.ride_id 
            AND r.fleet_company_id = current_setting('app.fleet_company_id', true)::UUID
        )
    );

-- Driver subscriptions policies
CREATE POLICY driver_subscription_own_access ON public.driver_subscriptions
    FOR ALL
    TO driver_user
    USING (
        driver_id = (
            SELECT id FROM public.drivers 
            WHERE user_id = current_setting('app.current_user_id', true)::UUID
        )
    );

-- Wallet policies
CREATE POLICY wallet_owner_access ON public.user_wallets
    FOR ALL
    TO authenticated_user
    USING (user_id = current_setting('app.current_user_id', true)::UUID);

CREATE POLICY wallet_transaction_owner_access ON public.wallet_transactions
    FOR ALL
    TO authenticated_user
    USING (user_id = current_setting('app.current_user_id', true)::UUID);

-- Emergency contacts policies
CREATE POLICY emergency_contact_owner_access ON public.emergency_contacts
    FOR ALL
    TO authenticated_user
    USING (user_id = current_setting('app.current_user_id', true)::UUID);

-- Emergency responders can access emergency contacts during emergencies
CREATE POLICY emergency_contact_responder_access ON public.emergency_contacts
    FOR SELECT
    TO emergency_responder
    USING (
        EXISTS (
            SELECT 1 FROM public.rides r 
            WHERE r.customer_id = emergency_contacts.user_id 
            AND (r.is_sos_triggered = TRUE OR r.status = 'emergency')
        )
        OR
        EXISTS (
            SELECT 1 FROM vip_data.vip_emergency_events vee 
            WHERE vee.user_id = emergency_contacts.user_id 
            AND vee.resolution_status = 'open'
        )
    );

-- =======================
-- VIP SCHEMA RLS POLICIES
-- =======================

-- VIP profiles - restricted access
CREATE POLICY vip_profile_admin_access ON vip_data.vip_profiles
    FOR ALL
    TO vip_admin
    USING (TRUE);

CREATE POLICY vip_profile_operator_read ON vip_data.vip_profiles
    FOR SELECT
    TO vip_operator
    USING (TRUE);

CREATE POLICY vip_profile_emergency_access ON vip_data.vip_profiles
    FOR SELECT
    TO emergency_responder
    USING (
        priority_level >= 3 -- Only high-priority VIPs
        OR threat_assessment_level IN ('high', 'critical')
    );

CREATE POLICY vip_profile_owner_limited_access ON vip_data.vip_profiles
    FOR SELECT
    TO customer_user
    USING (
        user_id = current_setting('app.current_user_id', true)::UUID
        -- Users can only see non-sensitive fields of their own profile
    );

-- VIP location history - highly restricted
CREATE POLICY vip_location_admin_access ON vip_data.vip_location_history
    FOR ALL
    TO vip_admin
    USING (TRUE);

CREATE POLICY vip_location_emergency_access ON vip_data.vip_location_history
    FOR SELECT
    TO emergency_responder
    USING (
        is_emergency_location = TRUE
        OR is_panic_mode = TRUE
        OR EXISTS (
            SELECT 1 FROM vip_data.vip_emergency_events vee 
            WHERE vee.user_id = vip_location_history.user_id 
            AND vee.resolution_status = 'open'
        )
    );

-- VIP communications - restricted access
CREATE POLICY vip_communication_admin_access ON vip_data.vip_communications
    FOR ALL
    TO vip_admin
    USING (TRUE);

CREATE POLICY vip_communication_emergency_access ON vip_data.vip_communications
    FOR SELECT
    TO emergency_responder
    USING (is_emergency_communication = TRUE);

-- VIP emergency events
CREATE POLICY vip_emergency_responder_access ON vip_data.vip_emergency_events
    FOR ALL
    TO emergency_responder
    USING (TRUE);

CREATE POLICY vip_emergency_admin_access ON vip_data.vip_emergency_events
    FOR ALL
    TO vip_admin
    USING (TRUE);

-- VIP service preferences
CREATE POLICY vip_preferences_owner_access ON vip_data.vip_service_preferences
    FOR ALL
    TO customer_user
    USING (user_id = current_setting('app.current_user_id', true)::UUID);

CREATE POLICY vip_preferences_admin_access ON vip_data.vip_service_preferences
    FOR SELECT
    TO vip_admin, vip_operator
    USING (TRUE);

-- VIP data access log - audit only
CREATE POLICY vip_access_log_audit_access ON vip_data.vip_data_access_log
    FOR ALL
    TO audit_admin
    USING (TRUE);

CREATE POLICY vip_access_log_own_access ON vip_data.vip_data_access_log
    FOR SELECT
    TO authenticated_user
    USING (
        vip_user_id = current_setting('app.current_user_id', true)::UUID
        OR accessor_user_id = current_setting('app.current_user_id', true)::UUID
    );

-- =======================
-- AUDIT SCHEMA RLS POLICIES
-- =======================

-- Audit log - restricted to audit personnel
CREATE POLICY audit_log_admin_access ON audit.audit_log
    FOR ALL
    TO audit_admin
    USING (TRUE);

CREATE POLICY audit_log_compliance_access ON audit.audit_log
    FOR SELECT
    TO compliance_officer
    USING (compliance_category IS NOT NULL);

CREATE POLICY audit_log_own_actions ON audit.audit_log
    FOR SELECT
    TO authenticated_user
    USING (
        user_id = current_setting('app.current_user_id', true)::UUID
        AND sensitivity_level IN ('low', 'normal')
    );

-- VIP access log - audit access
CREATE POLICY vip_access_audit_admin ON audit.vip_access_log
    FOR ALL
    TO audit_admin
    USING (TRUE);

CREATE POLICY vip_access_compliance_access ON audit.vip_access_log
    FOR SELECT
    TO compliance_officer
    USING (TRUE);

-- Security incidents
CREATE POLICY security_incident_responder_access ON audit.security_incidents
    FOR ALL
    TO emergency_responder, audit_admin
    USING (TRUE);

CREATE POLICY security_incident_affected_user ON audit.security_incidents
    FOR SELECT
    TO authenticated_user
    USING (
        current_setting('app.current_user_id', true)::UUID = ANY(affected_users)
    );

-- =======================
-- SECURITY FUNCTIONS
-- =======================

-- Function to check if user has VIP data access permission
CREATE OR REPLACE FUNCTION check_vip_data_access(
    target_user_id UUID,
    access_reason TEXT DEFAULT 'routine'
) RETURNS BOOLEAN AS $$
DECLARE
    current_user_role TEXT;
    is_emergency BOOLEAN := FALSE;
BEGIN
    current_user_role := current_setting('app.user_role', true);
    
    -- Check if there's an active emergency
    SELECT EXISTS (
        SELECT 1 FROM vip_data.vip_emergency_events 
        WHERE user_id = target_user_id 
        AND resolution_status = 'open'
    ) INTO is_emergency;
    
    -- VIP admins always have access
    IF current_user_role = 'vip_admin' THEN
        RETURN TRUE;
    END IF;
    
    -- Emergency responders have access during emergencies
    IF current_user_role = 'emergency_responder' AND is_emergency THEN
        RETURN TRUE;
    END IF;
    
    -- VIP operators have read-only access
    IF current_user_role = 'vip_operator' AND access_reason IN ('support', 'monitoring') THEN
        RETURN TRUE;
    END IF;
    
    -- Users can access their own data (limited fields)
    IF target_user_id = current_setting('app.current_user_id', true)::UUID THEN
        RETURN TRUE;
    END IF;
    
    RETURN FALSE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to log and validate high-risk data access
CREATE OR REPLACE FUNCTION validate_high_risk_access(
    table_name TEXT,
    operation TEXT,
    business_justification TEXT
) RETURNS BOOLEAN AS $$
DECLARE
    user_role TEXT;
    requires_approval BOOLEAN := FALSE;
BEGIN
    user_role := current_setting('app.user_role', true);
    
    -- Determine if approval is required
    IF table_name LIKE 'vip_%' AND operation IN ('UPDATE', 'DELETE') THEN
        requires_approval := TRUE;
    END IF;
    
    IF table_name = 'vip_location_history' AND user_role != 'emergency_responder' THEN
        requires_approval := TRUE;
    END IF;
    
    -- Log the access attempt
    INSERT INTO audit.vip_access_log (
        vip_user_id, accessor_user_id, table_name, operation,
        access_reason, business_justification, high_risk_access,
        ip_address, accessed_at
    ) VALUES (
        current_setting('app.target_user_id', true)::UUID,
        current_setting('app.current_user_id', true)::UUID,
        table_name,
        operation,
        current_setting('app.access_reason', true),
        business_justification,
        requires_approval,
        current_setting('app.client_ip', true)::INET,
        NOW()
    );
    
    -- For high-risk access, require additional validation
    IF requires_approval THEN
        -- Check if supervisor approval exists
        IF current_setting('app.supervisor_approval_id', true) IS NULL THEN
            RAISE EXCEPTION 'Supervisor approval required for this operation';
        END IF;
    END IF;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to enforce data retention policies
CREATE OR REPLACE FUNCTION enforce_data_retention()
RETURNS INTEGER AS $$
DECLARE
    retention_count INTEGER := 0;
BEGIN
    -- Archive old ride data (older than 7 years for non-VIP)
    WITH archived_rides AS (
        DELETE FROM public.rides 
        WHERE requested_at < NOW() - INTERVAL '7 years'
        AND vip_priority_level = 0
        RETURNING *
    )
    INSERT INTO archive.rides_archive SELECT * FROM archived_rides;
    
    GET DIAGNOSTICS retention_count = ROW_COUNT;
    
    -- Log retention action
    INSERT INTO audit.data_retention_log (
        table_name, retention_policy, action, records_processed,
        criteria_used, retention_period_months, legal_basis,
        processed_by_system, executed_at, completed_at
    ) VALUES (
        'public.rides', 'standard_7_year', 'archive', retention_count,
        'requested_at < NOW() - INTERVAL ''7 years'' AND vip_priority_level = 0',
        84, 'Business requirement and legal compliance',
        'automated_retention_job', NOW(), NOW()
    );
    
    RETURN retention_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Comments
COMMENT ON FUNCTION check_vip_data_access(UUID, TEXT) IS 'Validates VIP data access permissions based on user role and context';
COMMENT ON FUNCTION validate_high_risk_access(TEXT, TEXT, TEXT) IS 'Logs and validates high-risk data access attempts';
COMMENT ON FUNCTION enforce_data_retention() IS 'Automated data retention policy enforcement';

-- Grant execute permissions
-- GRANT EXECUTE ON FUNCTION check_vip_data_access(UUID, TEXT) TO authenticated_user;
-- GRANT EXECUTE ON FUNCTION validate_high_risk_access(TEXT, TEXT, TEXT) TO vip_admin, emergency_responder;
-- GRANT EXECUTE ON FUNCTION enforce_data_retention() TO system_admin;
