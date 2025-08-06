-- Analytics and Archive Schema for Business Intelligence and Long-term Storage

-- =======================
-- ANALYTICS SCHEMA
-- =======================

-- Ride Analytics Materialized View
CREATE MATERIALIZED VIEW analytics.ride_metrics AS
SELECT 
    DATE_TRUNC('day', r.requested_at) as date,
    r.customer_tier,
    r.ride_type,
    fc.name as fleet_company_name,
    COUNT(*) as total_rides,
    COUNT(*) FILTER (WHERE r.status = 'completed') as completed_rides,
    COUNT(*) FILTER (WHERE r.status = 'cancelled') as cancelled_rides,
    COUNT(*) FILTER (WHERE r.vip_priority_level > 0) as vip_rides,
    COUNT(*) FILTER (WHERE r.is_sos_triggered = TRUE) as emergency_rides,
    
    -- Financial metrics
    AVG(r.total_fare) as avg_fare,
    SUM(r.total_fare) FILTER (WHERE r.status = 'completed') as total_revenue,
    AVG(r.surge_multiplier) as avg_surge_multiplier,
    
    -- Performance metrics
    AVG(EXTRACT(EPOCH FROM (r.actual_pickup_time - r.requested_at))/60) as avg_pickup_time_minutes,
    AVG(r.actual_duration_minutes) as avg_ride_duration_minutes,
    AVG(r.actual_distance_km) as avg_distance_km,
    
    -- Quality metrics
    AVG(r.customer_rating) as avg_customer_rating,
    AVG(r.driver_rating) as avg_driver_rating,
    AVG(r.service_quality_score) as avg_quality_score
FROM public.rides r
LEFT JOIN public.fleet_companies fc ON r.fleet_company_id = fc.id
WHERE r.requested_at >= CURRENT_DATE - INTERVAL '1 year'
GROUP BY 
    DATE_TRUNC('day', r.requested_at),
    r.customer_tier,
    r.ride_type,
    fc.name;

-- Driver Performance Analytics
CREATE MATERIALIZED VIEW analytics.driver_performance AS
SELECT 
    d.id as driver_id,
    u.first_name || ' ' || u.last_name as driver_name,
    d.category as driver_category,
    fc.name as fleet_company_name,
    
    -- Activity metrics
    COUNT(r.id) as total_rides,
    COUNT(r.id) FILTER (WHERE r.status = 'completed') as completed_rides,
    COUNT(r.id) FILTER (WHERE r.status = 'cancelled' AND r.cancelled_by_user_type = 'driver') as driver_cancellations,
    COUNT(r.id) FILTER (WHERE r.vip_priority_level > 0) as vip_rides_served,
    
    -- Performance metrics
    AVG(r.customer_rating) as avg_customer_rating,
    AVG(EXTRACT(EPOCH FROM (r.actual_pickup_time - r.requested_at))/60) as avg_pickup_time_minutes,
    SUM(r.total_fare) FILTER (WHERE r.status = 'completed') as total_earnings,
    
    -- Quality metrics
    COUNT(*) FILTER (WHERE r.customer_rating >= 4.0) * 100.0 / NULLIF(COUNT(*) FILTER (WHERE r.customer_rating IS NOT NULL), 0) as high_rating_percentage,
    
    -- Time period
    DATE_TRUNC('month', MIN(r.requested_at)) as first_ride_month,
    DATE_TRUNC('month', MAX(r.requested_at)) as last_ride_month
FROM public.drivers d
JOIN public.users u ON d.user_id = u.id
LEFT JOIN public.fleet_companies fc ON d.fleet_company_id = fc.id
LEFT JOIN public.rides r ON r.driver_id = d.id
WHERE r.requested_at >= CURRENT_DATE - INTERVAL '1 year'
GROUP BY d.id, u.first_name, u.last_name, d.category, fc.name;

-- Fleet Company Performance
CREATE MATERIALIZED VIEW analytics.fleet_performance AS
SELECT 
    fc.id as fleet_company_id,
    fc.name as company_name,
    
    -- Fleet size metrics
    COUNT(DISTINCT d.id) as total_drivers,
    COUNT(DISTINCT v.id) as total_vehicles,
    COUNT(DISTINCT d.id) FILTER (WHERE d.is_online = TRUE) as online_drivers,
    COUNT(DISTINCT v.id) FILTER (WHERE v.is_available = TRUE) as available_vehicles,
    
    -- Performance metrics
    COUNT(r.id) as total_rides,
    COUNT(r.id) FILTER (WHERE r.status = 'completed') as completed_rides,
    SUM(r.total_fare) FILTER (WHERE r.status = 'completed') as total_revenue,
    
    -- Commission metrics
    SUM(cr.commission_amount) as total_commission_earned,
    AVG(cr.commission_rate) as avg_commission_rate,
    
    -- Quality metrics
    AVG(r.customer_rating) as avg_customer_rating,
    AVG(d.rating) as avg_driver_rating,
    fc.rating as company_rating
FROM public.fleet_companies fc
LEFT JOIN public.drivers d ON d.fleet_company_id = fc.id
LEFT JOIN public.vehicles v ON v.fleet_company_id = fc.id
LEFT JOIN public.rides r ON r.fleet_company_id = fc.id AND r.requested_at >= CURRENT_DATE - INTERVAL '1 year'
LEFT JOIN public.commission_records cr ON cr.fleet_company_id = fc.id AND cr.earned_date >= CURRENT_DATE - INTERVAL '1 year'
WHERE fc.is_active = TRUE
GROUP BY fc.id, fc.name, fc.rating;

-- Financial Analytics
CREATE MATERIALIZED VIEW analytics.financial_summary AS
SELECT 
    DATE_TRUNC('month', p.initiated_at) as month,
    p.payment_type,
    p.currency,
    
    -- Payment volumes
    COUNT(*) as transaction_count,
    COUNT(*) FILTER (WHERE p.status = 'completed') as successful_transactions,
    COUNT(*) FILTER (WHERE p.status = 'failed') as failed_transactions,
    
    -- Financial amounts
    SUM(p.amount) FILTER (WHERE p.status = 'completed') as total_amount,
    SUM(p.platform_fee) FILTER (WHERE p.status = 'completed') as total_platform_fees,
    SUM(p.payment_processor_fee) FILTER (WHERE p.status = 'completed') as total_processor_fees,
    SUM(p.net_amount) FILTER (WHERE p.status = 'completed') as total_net_amount,
    
    -- Refunds and disputes
    SUM(p.refunded_amount) as total_refunds,
    COUNT(*) FILTER (WHERE p.dispute_status IS NOT NULL) as disputed_transactions,
    
    -- Average metrics
    AVG(p.amount) FILTER (WHERE p.status = 'completed') as avg_transaction_amount,
    AVG(p.risk_score) as avg_risk_score
FROM public.payments p
WHERE p.initiated_at >= CURRENT_DATE - INTERVAL '2 years'
GROUP BY 
    DATE_TRUNC('month', p.initiated_at),
    p.payment_type,
    p.currency;

-- Customer Analytics
CREATE MATERIALIZED VIEW analytics.customer_insights AS
SELECT 
    u.id as customer_id,
    u.tier as customer_tier,
    u.created_at as registration_date,
    
    -- Activity metrics
    COUNT(r.id) as total_rides,
    COUNT(r.id) FILTER (WHERE r.status = 'completed') as completed_rides,
    COUNT(r.id) FILTER (WHERE r.status = 'cancelled' AND r.cancelled_by_user_type = 'customer') as customer_cancellations,
    
    -- Spending metrics
    SUM(p.amount) FILTER (WHERE p.status = 'completed' AND p.payment_type = 'ride_fare') as total_ride_spending,
    SUM(p.amount) FILTER (WHERE p.status = 'completed' AND p.payment_type = 'hotel_booking') as total_hotel_spending,
    AVG(r.total_fare) as avg_ride_fare,
    
    -- Service usage
    COUNT(DISTINCT r.ride_type) as ride_types_used,
    COUNT(hb.id) as hotel_bookings_made,
    COUNT(r.id) FILTER (WHERE r.vip_priority_level > 0) as vip_services_used,
    
    -- Quality metrics
    AVG(r.customer_rating) as avg_rating_given,
    AVG(rr.rating) FILTER (WHERE rr.rated_user_id = u.id) as avg_rating_received,
    
    -- Temporal metrics
    DATE_TRUNC('month', MIN(r.requested_at)) as first_ride_month,
    DATE_TRUNC('month', MAX(r.requested_at)) as last_ride_month,
    EXTRACT(DAYS FROM (MAX(r.requested_at) - MIN(r.requested_at))) as customer_lifetime_days
FROM public.users u
LEFT JOIN public.rides r ON r.customer_id = u.id
LEFT JOIN public.payments p ON p.payer_id = u.id
LEFT JOIN public.hotel_bookings hb ON hb.customer_id = u.id
LEFT JOIN public.ride_ratings rr ON rr.rated_user_id = u.id
WHERE u.user_type = 'customer'
  AND u.created_at >= CURRENT_DATE - INTERVAL '2 years'
GROUP BY u.id, u.tier, u.created_at;

-- =======================
-- ARCHIVE SCHEMA
-- =======================

-- Archived Rides (for data older than retention period)
CREATE TABLE archive.rides_archive (
    LIKE public.rides INCLUDING ALL
);

-- Archived Payments
CREATE TABLE archive.payments_archive (
    LIKE public.payments INCLUDING ALL
);

-- Archived Audit Logs
CREATE TABLE archive.audit_log_archive (
    LIKE audit.audit_log INCLUDING ALL
) PARTITION BY RANGE (timestamp);

-- Archived VIP Location Data
CREATE TABLE archive.vip_location_archive (
    LIKE vip_data.vip_location_history INCLUDING ALL
) PARTITION BY RANGE (recorded_at);

-- Data Archival Functions
CREATE OR REPLACE FUNCTION archive.archive_old_data(
    table_name TEXT,
    retention_months INTEGER DEFAULT 84 -- 7 years default
) RETURNS INTEGER AS $$
DECLARE
    archive_date DATE;
    archived_count INTEGER := 0;
BEGIN
    archive_date := CURRENT_DATE - (retention_months || ' months')::INTERVAL;
    
    CASE table_name
        WHEN 'rides' THEN
            INSERT INTO archive.rides_archive 
            SELECT * FROM public.rides 
            WHERE requested_at < archive_date AND vip_priority_level = 0;
            
            GET DIAGNOSTICS archived_count = ROW_COUNT;
            
            DELETE FROM public.rides 
            WHERE requested_at < archive_date AND vip_priority_level = 0;
            
        WHEN 'payments' THEN
            INSERT INTO archive.payments_archive 
            SELECT * FROM public.payments 
            WHERE initiated_at < archive_date;
            
            GET DIAGNOSTICS archived_count = ROW_COUNT;
            
            DELETE FROM public.payments 
            WHERE initiated_at < archive_date;
            
        ELSE
            RAISE EXCEPTION 'Unknown table for archival: %', table_name;
    END CASE;
    
    -- Log the archival
    INSERT INTO audit.data_retention_log (
        table_name, retention_policy, action, records_processed,
        criteria_used, retention_period_months, legal_basis,
        processed_by_system, executed_at, completed_at
    ) VALUES (
        table_name, 'automated_archival', 'archive', archived_count,
        'Date older than ' || retention_months || ' months',
        retention_months, 'Data retention policy compliance',
        'archive_job', NOW(), NOW()
    );
    
    RETURN archived_count;
END;
$$ LANGUAGE plpgsql;

-- Refresh Analytics Views
CREATE OR REPLACE FUNCTION analytics.refresh_all_views()
RETURNS VOID AS $$
BEGIN
    REFRESH MATERIALIZED VIEW analytics.ride_metrics;
    REFRESH MATERIALIZED VIEW analytics.driver_performance;
    REFRESH MATERIALIZED VIEW analytics.fleet_performance;
    REFRESH MATERIALIZED VIEW analytics.financial_summary;
    REFRESH MATERIALIZED VIEW analytics.customer_insights;
END;
$$ LANGUAGE plpgsql;

-- Business Intelligence Views
CREATE VIEW analytics.vip_service_analytics AS
SELECT 
    DATE_TRUNC('month', r.requested_at) as month,
    COUNT(*) as total_vip_rides,
    COUNT(*) FILTER (WHERE r.is_sos_triggered = TRUE) as emergency_incidents,
    AVG(r.total_fare) as avg_vip_fare,
    AVG(EXTRACT(EPOCH FROM (r.actual_pickup_time - r.requested_at))/60) as avg_response_time_minutes,
    SUM(r.total_fare) as total_vip_revenue,
    
    -- Emergency response metrics
    COUNT(vee.id) as emergency_events,
    AVG(vee.actual_response_time_minutes) as avg_emergency_response_time,
    COUNT(vee.id) FILTER (WHERE vee.resolution_status = 'resolved') as resolved_emergencies
FROM public.rides r
LEFT JOIN vip_data.vip_emergency_events vee ON vee.ride_id = r.id
WHERE r.vip_priority_level > 0
  AND r.requested_at >= CURRENT_DATE - INTERVAL '1 year'
GROUP BY DATE_TRUNC('month', r.requested_at)
ORDER BY month DESC;

-- Revenue Analytics by Tier
CREATE VIEW analytics.revenue_by_tier AS
SELECT 
    DATE_TRUNC('month', r.requested_at) as month,
    r.customer_tier,
    COUNT(*) as ride_count,
    SUM(r.total_fare) as total_revenue,
    AVG(r.total_fare) as avg_fare,
    SUM(cr.commission_amount) as total_commission,
    AVG(cr.commission_rate) as avg_commission_rate
FROM public.rides r
LEFT JOIN public.commission_records cr ON cr.ride_id = r.id
WHERE r.status = 'completed'
  AND r.requested_at >= CURRENT_DATE - INTERVAL '1 year'
GROUP BY 
    DATE_TRUNC('month', r.requested_at),
    r.customer_tier
ORDER BY month DESC, r.customer_tier;

-- Hotel Partnership Analytics
CREATE VIEW analytics.hotel_partnership_performance AS
SELECT 
    hp.id as hotel_partner_id,
    hp.name as hotel_name,
    hp.partnership_tier,
    COUNT(hb.id) as total_bookings,
    COUNT(hb.id) FILTER (WHERE hb.status = 'completed') as completed_bookings,
    SUM(hb.total_amount) FILTER (WHERE hb.status NOT IN ('cancelled', 'no_show')) as total_revenue,
    AVG(hb.total_amount) as avg_booking_value,
    SUM(cr.commission_amount) as total_commission_earned,
    AVG(hr.base_price_per_night) as avg_room_rate
FROM public.hotel_partners hp
LEFT JOIN public.hotel_rooms hr ON hr.hotel_id = hp.id
LEFT JOIN public.hotel_bookings hb ON hb.hotel_id = hp.id
LEFT JOIN public.commission_records cr ON cr.hotel_booking_id = hb.id
WHERE hb.booked_at >= CURRENT_DATE - INTERVAL '1 year' OR hb.booked_at IS NULL
GROUP BY hp.id, hp.name, hp.partnership_tier
ORDER BY total_revenue DESC NULLS LAST;

-- Indexes for analytics tables
CREATE INDEX idx_ride_metrics_date ON analytics.ride_metrics(date DESC);
CREATE INDEX idx_ride_metrics_tier ON analytics.ride_metrics(customer_tier);

CREATE INDEX idx_driver_performance_driver_id ON analytics.driver_performance(driver_id);
CREATE INDEX idx_driver_performance_rating ON analytics.driver_performance(avg_customer_rating DESC);

CREATE INDEX idx_fleet_performance_company_id ON analytics.fleet_performance(fleet_company_id);
CREATE INDEX idx_fleet_performance_revenue ON analytics.fleet_performance(total_revenue DESC);

CREATE INDEX idx_financial_summary_month ON analytics.financial_summary(month DESC);
CREATE INDEX idx_financial_summary_type ON analytics.financial_summary(payment_type);

CREATE INDEX idx_customer_insights_customer_id ON analytics.customer_insights(customer_id);
CREATE INDEX idx_customer_insights_tier ON analytics.customer_insights(customer_tier);
CREATE INDEX idx_customer_insights_spending ON analytics.customer_insights(total_ride_spending DESC);

-- Archive table indexes
CREATE INDEX idx_rides_archive_requested_at ON archive.rides_archive(requested_at);
CREATE INDEX idx_rides_archive_customer_id ON archive.rides_archive(customer_id);

CREATE INDEX idx_payments_archive_initiated_at ON archive.payments_archive(initiated_at);
CREATE INDEX idx_payments_archive_payer_id ON archive.payments_archive(payer_id);

-- Scheduled jobs (to be implemented in application or cron)
-- These would typically be scheduled to run:
-- 1. Refresh analytics views: Daily at 2 AM
-- 2. Archive old data: Monthly
-- 3. Cleanup expired sessions: Daily
-- 4. Generate compliance reports: Weekly

-- Comments
COMMENT ON SCHEMA analytics IS 'Business intelligence and analytics data for reporting and insights';
COMMENT ON SCHEMA archive IS 'Long-term storage for historical data beyond retention period';

COMMENT ON MATERIALIZED VIEW analytics.ride_metrics IS 'Daily ride metrics aggregated by tier, type, and fleet company';
COMMENT ON MATERIALIZED VIEW analytics.driver_performance IS 'Driver performance metrics and ratings over time';
COMMENT ON MATERIALIZED VIEW analytics.fleet_performance IS 'Fleet company performance and utilization metrics';
COMMENT ON MATERIALIZED VIEW analytics.financial_summary IS 'Monthly financial transaction summary by type and currency';
COMMENT ON MATERIALIZED VIEW analytics.customer_insights IS 'Customer behavior and spending analytics';

COMMENT ON VIEW analytics.vip_service_analytics IS 'VIP service performance and emergency response metrics';
COMMENT ON VIEW analytics.revenue_by_tier IS 'Revenue analysis segmented by customer tier';
COMMENT ON VIEW analytics.hotel_partnership_performance IS 'Hotel partnership revenue and booking analytics';

COMMENT ON FUNCTION archive.archive_old_data(TEXT, INTEGER) IS 'Archives data older than specified retention period';
COMMENT ON FUNCTION analytics.refresh_all_views() IS 'Refreshes all materialized views for updated analytics';
