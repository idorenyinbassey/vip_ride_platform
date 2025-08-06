-- Audit Schema - Comprehensive Audit Logging and Compliance

-- Main Audit Log Table
CREATE TABLE audit.audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- What was changed
    table_name VARCHAR(100) NOT NULL,
    operation VARCHAR(10) NOT NULL, -- INSERT, UPDATE, DELETE
    record_id UUID, -- ID of the affected record
    
    -- Data changes
    old_data JSONB, -- Previous state (for UPDATE/DELETE)
    new_data JSONB, -- New state (for INSERT/UPDATE)
    changed_fields TEXT[], -- List of fields that changed (for UPDATE)
    
    -- Who made the change
    user_id UUID, -- User who made the change
    user_type VARCHAR(20), -- customer, driver, admin, system
    user_email VARCHAR(255),
    
    -- When and where
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    ip_address INET,
    user_agent TEXT,
    session_id VARCHAR(100),
    
    -- Application context
    application_name VARCHAR(50), -- web_app, mobile_app, admin_panel, api
    api_endpoint VARCHAR(255),
    request_id UUID, -- For tracing requests across services
    
    -- Additional metadata
    business_context VARCHAR(100), -- ride_booking, payment_processing, user_registration
    compliance_category VARCHAR(50), -- NDPR, financial, safety, security
    sensitivity_level VARCHAR(20) DEFAULT 'normal', -- low, normal, high, critical
    
    -- Retention and legal hold
    retention_until TIMESTAMP,
    legal_hold BOOLEAN DEFAULT FALSE,
    legal_hold_reason VARCHAR(255),
    
    created_at TIMESTAMP DEFAULT NOW()
) PARTITION BY RANGE (timestamp);

-- Create monthly partitions for audit log
CREATE TABLE audit.audit_log_2025_01 PARTITION OF audit.audit_log
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE audit.audit_log_2025_02 PARTITION OF audit.audit_log
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');

CREATE TABLE audit.audit_log_2025_03 PARTITION OF audit.audit_log
    FOR VALUES FROM ('2025-03-01') TO ('2025-04-01');

-- Function to create monthly audit partitions
CREATE OR REPLACE FUNCTION audit.create_monthly_audit_partition(start_date DATE)
RETURNS VOID AS $$
DECLARE
    partition_name TEXT;
    end_date DATE;
BEGIN
    end_date := start_date + INTERVAL '1 month';
    partition_name := 'audit_log_' || to_char(start_date, 'YYYY_MM');
    
    EXECUTE format('CREATE TABLE IF NOT EXISTS audit.%I PARTITION OF audit.audit_log
                    FOR VALUES FROM (%L) TO (%L)',
                   partition_name, start_date, end_date);
                   
    -- Create indexes on the new partition
    EXECUTE format('CREATE INDEX IF NOT EXISTS idx_%I_table_name ON audit.%I(table_name)', 
                   partition_name, partition_name);
    EXECUTE format('CREATE INDEX IF NOT EXISTS idx_%I_user_id ON audit.%I(user_id)', 
                   partition_name, partition_name);
    EXECUTE format('CREATE INDEX IF NOT EXISTS idx_%I_record_id ON audit.%I(record_id)', 
                   partition_name, partition_name);
END;
$$ LANGUAGE plpgsql;

-- VIP Data Access Audit
CREATE TABLE audit.vip_access_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- VIP user whose data was accessed
    vip_user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    
    -- Who accessed the data
    accessor_user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    accessor_role VARCHAR(50) NOT NULL, -- vip_admin, emergency_responder, support_agent
    accessor_department VARCHAR(100), -- security, customer_service, emergency_response
    
    -- What was accessed
    table_name VARCHAR(100) NOT NULL,
    operation VARCHAR(20) NOT NULL, -- SELECT, INSERT, UPDATE, DELETE
    records_accessed INTEGER DEFAULT 1,
    data_sensitivity VARCHAR(20) NOT NULL, -- low, medium, high, critical
    
    -- Access context
    access_reason VARCHAR(100) NOT NULL, -- emergency_response, customer_support, audit, investigation
    business_justification TEXT NOT NULL,
    supervisor_approval_id UUID, -- Required for sensitive access
    incident_reference VARCHAR(100), -- Related incident/case number
    
    -- Technical details
    ip_address INET NOT NULL,
    user_agent TEXT,
    session_id VARCHAR(100),
    api_endpoint VARCHAR(255),
    
    -- Data handling
    data_downloaded BOOLEAN DEFAULT FALSE,
    download_format VARCHAR(20), -- json, csv, pdf
    data_shared BOOLEAN DEFAULT FALSE,
    shared_with TEXT[], -- Array of recipients
    
    -- Compliance
    gdpr_basis VARCHAR(50), -- consent, contract, legal_obligation, vital_interests
    retention_period_days INTEGER DEFAULT 2555, -- 7 years default
    auto_delete_after TIMESTAMP,
    
    accessed_at TIMESTAMP NOT NULL DEFAULT NOW(),
    session_ended_at TIMESTAMP,
    
    -- Alerts and notifications
    high_risk_access BOOLEAN DEFAULT FALSE,
    alert_triggered BOOLEAN DEFAULT FALSE,
    privacy_officer_notified BOOLEAN DEFAULT FALSE
);

-- Data Export/Download Audit
CREATE TABLE audit.data_export_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Who exported data
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    user_role VARCHAR(50) NOT NULL,
    
    -- What was exported
    export_type VARCHAR(30) NOT NULL, -- user_data, ride_history, financial_data, vip_data
    tables_included TEXT[] NOT NULL,
    record_count INTEGER NOT NULL,
    date_range_start DATE,
    date_range_end DATE,
    
    -- Export details
    file_format VARCHAR(20) NOT NULL, -- pdf, csv, json, xml
    file_size_bytes BIGINT,
    encryption_used BOOLEAN DEFAULT FALSE,
    password_protected BOOLEAN DEFAULT FALSE,
    
    -- Recipients
    exported_for_user_id UUID REFERENCES public.users(id) ON DELETE SET NULL,
    third_party_recipient VARCHAR(255), -- Legal authority, insurance company, etc.
    delivery_method VARCHAR(30), -- download, email, secure_portal, physical_media
    
    -- Legal basis
    legal_basis VARCHAR(50) NOT NULL, -- user_request, legal_obligation, court_order
    request_reference VARCHAR(100),
    approval_reference VARCHAR(100),
    
    -- Compliance tracking
    gdpr_request_type VARCHAR(30), -- access, portability, rectification, erasure
    response_deadline DATE,
    completed_on_time BOOLEAN,
    
    -- Security
    access_logs_included BOOLEAN DEFAULT TRUE,
    sensitive_data_redacted BOOLEAN DEFAULT FALSE,
    redaction_reason TEXT,
    
    requested_at TIMESTAMP NOT NULL,
    approved_at TIMESTAMP,
    completed_at TIMESTAMP,
    downloaded_at TIMESTAMP,
    expires_at TIMESTAMP, -- When download link expires
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Security Incidents
CREATE TABLE audit.security_incidents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Incident classification
    incident_type VARCHAR(50) NOT NULL, -- data_breach, unauthorized_access, system_compromise, fraud
    severity_level INTEGER NOT NULL CHECK (severity_level >= 1 AND severity_level <= 5),
    category VARCHAR(30) NOT NULL, -- security, privacy, safety, financial
    
    -- Affected entities
    affected_users UUID[] DEFAULT '{}', -- Array of affected user IDs
    affected_systems TEXT[] DEFAULT '{}', -- Array of affected system components
    data_categories_affected TEXT[] DEFAULT '{}', -- personal_data, financial_data, location_data
    
    -- Incident details
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    impact_assessment TEXT,
    root_cause TEXT,
    
    -- Discovery and timeline
    discovered_at TIMESTAMP NOT NULL,
    discovered_by_user_id UUID REFERENCES public.users(id) ON DELETE SET NULL,
    discovery_method VARCHAR(50), -- automated_alert, user_report, audit, external_notification
    incident_start_time TIMESTAMP, -- When incident actually started
    incident_end_time TIMESTAMP, -- When incident was contained
    
    -- Response and resolution
    response_team_lead UUID REFERENCES public.users(id) ON DELETE SET NULL,
    response_team_members UUID[] DEFAULT '{}',
    containment_actions TEXT,
    remediation_actions TEXT,
    
    -- Status tracking
    status VARCHAR(20) DEFAULT 'open', -- open, investigating, contained, resolved, closed
    priority VARCHAR(20) DEFAULT 'medium', -- low, medium, high, critical
    resolution_summary TEXT,
    
    -- External notifications
    authorities_notified BOOLEAN DEFAULT FALSE,
    notification_deadline TIMESTAMP, -- NDPR requires 72 hours for data breaches
    authority_notification_sent_at TIMESTAMP,
    users_notified BOOLEAN DEFAULT FALSE,
    user_notification_sent_at TIMESTAMP,
    
    -- Legal and compliance
    legal_review_required BOOLEAN DEFAULT FALSE,
    legal_review_completed BOOLEAN DEFAULT FALSE,
    regulatory_impact BOOLEAN DEFAULT FALSE,
    insurance_claim_filed BOOLEAN DEFAULT FALSE,
    
    -- Lessons learned
    preventive_measures TEXT,
    policy_changes_required BOOLEAN DEFAULT FALSE,
    training_required BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    closed_at TIMESTAMP
);

-- Compliance Monitoring
CREATE TABLE audit.compliance_checks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Check details
    check_type VARCHAR(50) NOT NULL, -- data_retention, access_review, privacy_assessment
    regulation VARCHAR(30) NOT NULL, -- NDPR, GDPR, PCI_DSS, SOX
    check_category VARCHAR(50) NOT NULL, -- automated, manual, external_audit
    
    -- Scope
    table_name VARCHAR(100),
    user_segment VARCHAR(50), -- all_users, vip_users, inactive_users
    date_range_start DATE,
    date_range_end DATE,
    
    -- Results
    records_checked INTEGER,
    violations_found INTEGER,
    compliance_score DECIMAL(5,2), -- Percentage
    risk_level VARCHAR(20), -- low, medium, high, critical
    
    -- Findings
    findings TEXT,
    recommendations TEXT,
    remediation_required BOOLEAN DEFAULT FALSE,
    remediation_deadline DATE,
    
    -- Execution details
    executed_by_user_id UUID REFERENCES public.users(id) ON DELETE SET NULL,
    execution_method VARCHAR(30), -- automated_script, manual_review, third_party_audit
    evidence_collected BOOLEAN DEFAULT FALSE,
    evidence_location TEXT,
    
    -- Follow-up
    follow_up_required BOOLEAN DEFAULT FALSE,
    follow_up_date DATE,
    status VARCHAR(20) DEFAULT 'completed', -- pending, in_progress, completed, failed
    
    scheduled_at TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Data Retention Policy Tracking
CREATE TABLE audit.data_retention_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- What was processed
    table_name VARCHAR(100) NOT NULL,
    retention_policy VARCHAR(100) NOT NULL,
    
    -- Retention action
    action VARCHAR(20) NOT NULL, -- archive, anonymize, delete, extend_retention
    records_processed INTEGER NOT NULL,
    criteria_used TEXT NOT NULL,
    
    -- Legal basis
    retention_period_months INTEGER NOT NULL,
    legal_basis VARCHAR(100) NOT NULL,
    business_justification TEXT,
    
    -- Processing details
    processed_by_system VARCHAR(50), -- automated_job, manual_process
    job_reference VARCHAR(100),
    
    -- Results
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    error_details TEXT,
    
    -- Archive location (if applicable)
    archive_location TEXT,
    archive_format VARCHAR(20),
    archive_encrypted BOOLEAN DEFAULT TRUE,
    
    executed_at TIMESTAMP NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP,
    verified_at TIMESTAMP -- When retention action was verified
);

-- Indexes for audit tables
CREATE INDEX idx_audit_log_table_name ON audit.audit_log(table_name);
CREATE INDEX idx_audit_log_user_id ON audit.audit_log(user_id);
CREATE INDEX idx_audit_log_timestamp ON audit.audit_log(timestamp DESC);
CREATE INDEX idx_audit_log_record_id ON audit.audit_log(record_id);
CREATE INDEX idx_audit_log_operation ON audit.audit_log(operation);
CREATE INDEX idx_audit_log_sensitivity ON audit.audit_log(sensitivity_level);
CREATE INDEX idx_audit_log_compliance ON audit.audit_log(compliance_category);

CREATE INDEX idx_vip_access_log_vip_user ON audit.vip_access_log(vip_user_id);
CREATE INDEX idx_vip_access_log_accessor ON audit.vip_access_log(accessor_user_id);
CREATE INDEX idx_vip_access_log_accessed_at ON audit.vip_access_log(accessed_at DESC);
CREATE INDEX idx_vip_access_log_table_name ON audit.vip_access_log(table_name);
CREATE INDEX idx_vip_access_log_high_risk ON audit.vip_access_log(high_risk_access) WHERE high_risk_access = TRUE;

CREATE INDEX idx_data_export_log_user_id ON audit.data_export_log(user_id);
CREATE INDEX idx_data_export_log_exported_for ON audit.data_export_log(exported_for_user_id);
CREATE INDEX idx_data_export_log_requested_at ON audit.data_export_log(requested_at DESC);
CREATE INDEX idx_data_export_log_export_type ON audit.data_export_log(export_type);

CREATE INDEX idx_security_incidents_severity ON audit.security_incidents(severity_level DESC);
CREATE INDEX idx_security_incidents_status ON audit.security_incidents(status);
CREATE INDEX idx_security_incidents_discovered_at ON audit.security_incidents(discovered_at DESC);
CREATE INDEX idx_security_incidents_type ON audit.security_incidents(incident_type);

CREATE INDEX idx_compliance_checks_regulation ON audit.compliance_checks(regulation);
CREATE INDEX idx_compliance_checks_completed_at ON audit.compliance_checks(completed_at DESC);
CREATE INDEX idx_compliance_checks_risk_level ON audit.compliance_checks(risk_level);

CREATE INDEX idx_data_retention_log_table_name ON audit.data_retention_log(table_name);
CREATE INDEX idx_data_retention_log_executed_at ON audit.data_retention_log(executed_at DESC);
CREATE INDEX idx_data_retention_log_action ON audit.data_retention_log(action);

-- Row Level Security for audit tables
ALTER TABLE audit.audit_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit.vip_access_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit.security_incidents ENABLE ROW LEVEL SECURITY;

-- Functions for audit automation
CREATE OR REPLACE FUNCTION audit.log_high_risk_access(
    p_vip_user_id UUID,
    p_accessor_user_id UUID,
    p_table_name VARCHAR(100),
    p_access_reason VARCHAR(100)
) RETURNS VOID AS $$
BEGIN
    -- Log high-risk access and trigger alerts
    INSERT INTO audit.vip_access_log (
        vip_user_id, accessor_user_id, table_name, operation,
        access_reason, high_risk_access, alert_triggered,
        ip_address, accessed_at
    ) VALUES (
        p_vip_user_id, p_accessor_user_id, p_table_name, 'SELECT',
        p_access_reason, TRUE, TRUE,
        current_setting('app.client_ip', true)::INET, NOW()
    );
    
    -- TODO: Add notification logic for security team
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Automated compliance checking
CREATE OR REPLACE FUNCTION audit.check_data_retention_compliance()
RETURNS INTEGER AS $$
DECLARE
    violation_count INTEGER := 0;
BEGIN
    -- Check for data past retention period
    -- This is a simplified example - would be expanded for production
    
    INSERT INTO audit.compliance_checks (
        check_type, regulation, check_category,
        records_checked, violations_found, compliance_score,
        findings, executed_by_user_id, execution_method,
        started_at, completed_at
    ) 
    SELECT 
        'data_retention',
        'NDPR',
        'automated',
        COUNT(*),
        COUNT(*) FILTER (WHERE created_at < NOW() - INTERVAL '7 years'),
        CASE 
            WHEN COUNT(*) = 0 THEN 100.0
            ELSE 100.0 - (COUNT(*) FILTER (WHERE created_at < NOW() - INTERVAL '7 years') * 100.0 / COUNT(*))
        END,
        'Automated retention period compliance check',
        NULL,
        'automated_script',
        NOW(),
        NOW()
    FROM audit.audit_log
    WHERE timestamp >= NOW() - INTERVAL '1 day';
    
    GET DIAGNOSTICS violation_count = ROW_COUNT;
    
    RETURN violation_count;
END;
$$ LANGUAGE plpgsql;

-- Comments
COMMENT ON SCHEMA audit IS 'Comprehensive audit logging and compliance tracking schema';
COMMENT ON TABLE audit.audit_log IS 'Main audit trail for all data changes - partitioned by month';
COMMENT ON TABLE audit.vip_access_log IS 'Specialized audit log for VIP data access with enhanced monitoring';
COMMENT ON TABLE audit.data_export_log IS 'Tracking of all data exports for compliance and GDPR';
COMMENT ON TABLE audit.security_incidents IS 'Security incident tracking and response management';
COMMENT ON TABLE audit.compliance_checks IS 'Automated and manual compliance monitoring results';
COMMENT ON TABLE audit.data_retention_log IS 'Data retention policy execution and verification';
