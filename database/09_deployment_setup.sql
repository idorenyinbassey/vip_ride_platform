-- Database Deployment and Setup Scripts

-- Database Deployment Script
-- This script should be run by a database administrator with appropriate privileges

-- ==========================================
-- DEPLOYMENT CHECKLIST AND INSTRUCTIONS
-- ==========================================

/*
DEPLOYMENT CHECKLIST:

1. Prerequisites:
   □ PostgreSQL 14+ installed
   □ PostGIS extension available
   □ Appropriate database user with SUPERUSER privileges
   □ Backup and recovery procedures in place
   □ Environment-specific configuration values ready

2. Database Setup:
   □ Create database: CREATE DATABASE vip_ride_platform_db;
   □ Create application users and roles
   □ Set up connection pooling (PgBouncer recommended)
   □ Configure SSL/TLS for connections

3. Security Setup:
   □ Configure firewall rules
   □ Set up database user privileges
   □ Configure SSL certificates
   □ Set up encryption key management
   □ Configure backup encryption

4. Monitoring Setup:
   □ Configure PostgreSQL logging
   □ Set up performance monitoring (pg_stat_statements)
   □ Configure alert thresholds
   □ Set up backup monitoring

5. Performance Optimization:
   □ Configure PostgreSQL settings for production
   □ Set up connection pooling
   □ Configure index optimization
   □ Set up query performance monitoring

6. Backup and Recovery:
   □ Configure automated backups
   □ Test restore procedures
   □ Set up point-in-time recovery
   □ Document recovery procedures
*/

-- ==========================================
-- CREATE DATABASE ROLES AND USERS
-- ==========================================

-- Administrative roles
CREATE ROLE system_admin;
CREATE ROLE audit_admin;
CREATE ROLE compliance_officer;

-- Application roles
CREATE ROLE authenticated_user;
CREATE ROLE customer_user;
CREATE ROLE driver_user;
CREATE ROLE fleet_admin;
CREATE ROLE vip_admin;
CREATE ROLE vip_operator;
CREATE ROLE emergency_responder;
CREATE ROLE support_agent;
CREATE ROLE analytics_user;
CREATE ROLE hotel_staff;

-- Grant role hierarchies
GRANT authenticated_user TO customer_user, driver_user, fleet_admin, support_agent;
GRANT vip_operator TO vip_admin;
GRANT emergency_responder TO vip_admin;

-- Application users (replace with actual usernames/passwords)
CREATE USER app_backend WITH PASSWORD 'CHANGE_ME_SECURE_PASSWORD' IN ROLE authenticated_user;
CREATE USER app_admin WITH PASSWORD 'CHANGE_ME_SECURE_PASSWORD' IN ROLE system_admin;
CREATE USER app_analytics WITH PASSWORD 'CHANGE_ME_SECURE_PASSWORD' IN ROLE analytics_user;
CREATE USER app_audit WITH PASSWORD 'CHANGE_ME_SECURE_PASSWORD' IN ROLE audit_admin;
CREATE USER app_emergency WITH PASSWORD 'CHANGE_ME_SECURE_PASSWORD' IN ROLE emergency_responder;

-- ==========================================
-- GRANT SCHEMA PERMISSIONS
-- ==========================================

-- Public schema permissions
GRANT USAGE ON SCHEMA public TO authenticated_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO authenticated_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO authenticated_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO authenticated_user;

-- VIP schema permissions (restricted)
GRANT USAGE ON SCHEMA vip_data TO vip_admin, vip_operator, emergency_responder;
GRANT ALL ON ALL TABLES IN SCHEMA vip_data TO vip_admin;
GRANT SELECT ON ALL TABLES IN SCHEMA vip_data TO vip_operator, emergency_responder;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA vip_data TO vip_admin, vip_operator, emergency_responder;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA vip_data TO vip_admin, vip_operator, emergency_responder;

-- Audit schema permissions
GRANT USAGE ON SCHEMA audit TO audit_admin, compliance_officer, system_admin;
GRANT ALL ON ALL TABLES IN SCHEMA audit TO audit_admin;
GRANT SELECT ON ALL TABLES IN SCHEMA audit TO compliance_officer;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA audit TO audit_admin, compliance_officer;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA audit TO audit_admin, system_admin;

-- Analytics schema permissions
GRANT USAGE ON SCHEMA analytics TO analytics_user, system_admin;
GRANT SELECT ON ALL TABLES IN SCHEMA analytics TO analytics_user;
GRANT SELECT ON ALL TABLES IN SCHEMA analytics TO system_admin;

-- Archive schema permissions
GRANT USAGE ON SCHEMA archive TO system_admin, audit_admin;
GRANT ALL ON ALL TABLES IN SCHEMA archive TO system_admin;
GRANT SELECT ON ALL TABLES IN SCHEMA archive TO audit_admin;

-- ==========================================
-- PRODUCTION POSTGRESQL CONFIGURATION
-- ==========================================

/*
Recommended postgresql.conf settings for production:

# Memory Configuration
shared_buffers = 256MB                    # 25% of RAM for dedicated server
effective_cache_size = 1GB                # 75% of RAM
work_mem = 4MB                            # Per connection
maintenance_work_mem = 64MB               # For maintenance operations

# Connection Configuration
max_connections = 200                     # Adjust based on expected load
max_prepared_transactions = 200           # For two-phase commits

# Write-Ahead Logging (WAL)
wal_level = replica                       # For streaming replication
wal_buffers = 16MB                        # WAL buffer size
checkpoint_completion_target = 0.9        # Checkpoint completion time
max_wal_size = 1GB                        # Maximum WAL size
min_wal_size = 80MB                       # Minimum WAL size

# Query Planning
random_page_cost = 1.1                    # For SSD storage
effective_io_concurrency = 200            # For SSD storage

# Logging
log_destination = 'stderr'                # Log to stderr
logging_collector = on                    # Enable log collector
log_directory = 'pg_log'                  # Log directory
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_rotation_age = 1d                     # Rotate logs daily
log_rotation_size = 100MB                 # Rotate when file reaches 100MB
log_min_duration_statement = 1000         # Log slow queries (>1s)
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
log_checkpoints = on                      # Log checkpoint activity
log_connections = on                      # Log connections
log_disconnections = on                   # Log disconnections
log_lock_waits = on                       # Log lock waits

# Performance Monitoring
shared_preload_libraries = 'pg_stat_statements'
track_activities = on
track_counts = on
track_io_timing = on
track_functions = all

# Security
ssl = on                                  # Enable SSL
ssl_cert_file = 'server.crt'            # SSL certificate
ssl_key_file = 'server.key'             # SSL private key
password_encryption = scram-sha-256       # Strong password encryption
*/

-- ==========================================
-- MONITORING AND ALERTING QUERIES
-- ==========================================

-- Create monitoring views for database health
CREATE VIEW monitoring.database_health AS
SELECT 
    'connections' as metric,
    COUNT(*) as current_value,
    current_setting('max_connections')::int as max_value,
    (COUNT(*) * 100.0 / current_setting('max_connections')::int) as usage_percentage
FROM pg_stat_activity
UNION ALL
SELECT 
    'active_connections' as metric,
    COUNT(*) as current_value,
    current_setting('max_connections')::int as max_value,
    (COUNT(*) * 100.0 / current_setting('max_connections')::int) as usage_percentage
FROM pg_stat_activity 
WHERE state = 'active'
UNION ALL
SELECT 
    'database_size_mb' as metric,
    (pg_database_size(current_database()) / 1024 / 1024)::int as current_value,
    NULL as max_value,
    NULL as usage_percentage;

-- Create view for performance monitoring
CREATE VIEW monitoring.performance_metrics AS
SELECT 
    schemaname,
    tablename,
    n_tup_ins as inserts,
    n_tup_upd as updates,
    n_tup_del as deletes,
    n_tup_hot_upd as hot_updates,
    n_live_tup as live_tuples,
    n_dead_tup as dead_tuples,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    last_autoanalyze
FROM pg_stat_user_tables
ORDER BY n_tup_ins + n_tup_upd + n_tup_del DESC;

-- Create view for security monitoring
CREATE VIEW monitoring.security_alerts AS
SELECT 
    'failed_logins' as alert_type,
    COUNT(*) as count,
    MAX(timestamp) as latest_occurrence
FROM audit.audit_log 
WHERE operation = 'LOGIN_FAILED' 
  AND timestamp >= NOW() - INTERVAL '1 hour'
UNION ALL
SELECT 
    'high_risk_vip_access' as alert_type,
    COUNT(*) as count,
    MAX(accessed_at) as latest_occurrence
FROM audit.vip_access_log 
WHERE high_risk_access = TRUE 
  AND accessed_at >= NOW() - INTERVAL '1 hour'
UNION ALL
SELECT 
    'emergency_incidents' as alert_type,
    COUNT(*) as count,
    MAX(triggered_at) as latest_occurrence
FROM vip_data.vip_emergency_events 
WHERE resolution_status = 'open'
  AND triggered_at >= NOW() - INTERVAL '1 hour';

-- ==========================================
-- BACKUP AND RECOVERY PROCEDURES
-- ==========================================

/*
Backup Strategy:

1. Full Backup (Daily):
   pg_dump -h localhost -U app_backend -Fc -f backup_$(date +%Y%m%d).dump vip_ride_platform_db

2. Incremental Backup (Continuous):
   Configure WAL archiving for point-in-time recovery
   
3. VIP Data Backup (Additional Security):
   pg_dump -h localhost -U app_backend -Fc -n vip_data -f vip_backup_$(date +%Y%m%d).dump vip_ride_platform_db

4. Schema-only Backup (For testing):
   pg_dump -h localhost -U app_backend -s -f schema_backup_$(date +%Y%m%d).sql vip_ride_platform_db

Recovery Procedures:

1. Full Restore:
   pg_restore -h localhost -U app_backend -d vip_ride_platform_db backup_YYYYMMDD.dump

2. Point-in-time Recovery:
   Use pg_basebackup + WAL replay to specific timestamp

3. Selective Restore:
   pg_restore -h localhost -U app_backend -d vip_ride_platform_db -t specific_table backup_YYYYMMDD.dump
*/

-- ==========================================
-- MAINTENANCE PROCEDURES
-- ==========================================

-- Create maintenance procedures
CREATE OR REPLACE FUNCTION maintenance.vacuum_analyze_all()
RETURNS void AS $$
DECLARE
    table_record RECORD;
BEGIN
    FOR table_record IN 
        SELECT schemaname, tablename 
        FROM pg_tables 
        WHERE schemaname IN ('public', 'vip_data', 'audit')
    LOOP
        EXECUTE 'VACUUM ANALYZE ' || quote_ident(table_record.schemaname) || '.' || quote_ident(table_record.tablename);
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Create function to update table statistics
CREATE OR REPLACE FUNCTION maintenance.update_statistics()
RETURNS void AS $$
BEGIN
    ANALYZE;
    
    -- Update materialized views
    PERFORM analytics.refresh_all_views();
    
    -- Log maintenance activity
    INSERT INTO audit.audit_log (
        table_name, operation, user_id, timestamp, 
        business_context, application_name
    ) VALUES (
        'maintenance', 'STATISTICS_UPDATE', NULL, NOW(),
        'scheduled_maintenance', 'maintenance_job'
    );
END;
$$ LANGUAGE plpgsql;

-- ==========================================
-- DEPLOYMENT VERIFICATION QUERIES
-- ==========================================

-- Verify schema deployment
SELECT 
    schema_name,
    COUNT(*) as table_count
FROM information_schema.tables 
WHERE table_schema IN ('public', 'vip_data', 'audit', 'analytics', 'archive')
GROUP BY schema_name
ORDER BY schema_name;

-- Verify indexes
SELECT 
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes 
WHERE schemaname IN ('public', 'vip_data', 'audit', 'analytics')
ORDER BY schemaname, tablename, indexname;

-- Verify foreign key constraints
SELECT 
    tc.table_schema,
    tc.table_name,
    kcu.column_name,
    ccu.table_schema AS foreign_table_schema,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
    AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_schema IN ('public', 'vip_data', 'audit')
ORDER BY tc.table_schema, tc.table_name;

-- Verify RLS policies
SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual
FROM pg_policies
WHERE schemaname IN ('public', 'vip_data', 'audit')
ORDER BY schemaname, tablename, policyname;

-- ==========================================
-- POST-DEPLOYMENT TASKS
-- ==========================================

/*
Post-Deployment Checklist:

1. Data Validation:
   □ Insert test data to verify constraints
   □ Test RLS policies with different user roles
   □ Verify encryption/decryption functions
   □ Test partition creation and maintenance

2. Performance Testing:
   □ Run EXPLAIN ANALYZE on critical queries
   □ Test concurrent connection limits
   □ Verify index usage
   □ Test backup and restore procedures

3. Security Testing:
   □ Verify user role permissions
   □ Test VIP data access restrictions
   □ Verify audit logging functionality
   □ Test encryption key management

4. Monitoring Setup:
   □ Configure monitoring dashboards
   □ Set up alerting thresholds
   □ Test backup notifications
   □ Verify log rotation

5. Documentation:
   □ Update database documentation
   □ Document backup/recovery procedures
   □ Create troubleshooting guides
   □ Document security procedures
*/

-- Sample data insertion (for testing only - remove in production)
-- INSERT INTO public.users (email, phone_number, first_name, last_name, user_type, tier) 
-- VALUES ('test@example.com', '+1234567890', 'Test', 'User', 'customer', 'normal');

-- Comments
COMMENT ON VIEW monitoring.database_health IS 'Real-time database health metrics for monitoring';
COMMENT ON VIEW monitoring.performance_metrics IS 'Table-level performance statistics for optimization';
COMMENT ON VIEW monitoring.security_alerts IS 'Security alerts and incidents requiring attention';
COMMENT ON FUNCTION maintenance.vacuum_analyze_all() IS 'Maintenance function to vacuum and analyze all tables';
COMMENT ON FUNCTION maintenance.update_statistics() IS 'Updates table statistics and refreshes materialized views';
