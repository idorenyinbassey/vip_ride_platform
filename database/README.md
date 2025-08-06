# VIP Ride-Hailing Platform - PostgreSQL Database Schema

## Overview

This directory contains the comprehensive PostgreSQL database schema for the VIP ride-hailing platform, designed with enterprise-grade security, scalability, and compliance features.

## Schema Architecture

### 🏗️ **Multi-Schema Design**
- **`public`** - Main application data (non-sensitive)
- **`vip_data`** - Isolated VIP user data with encryption
- **`audit`** - Comprehensive audit logging and compliance
- **`analytics`** - Business intelligence and reporting
- **`archive`** - Long-term historical data storage

### 🔐 **Security Features**
- **Row-Level Security (RLS)** - Granular access control
- **AES-256-GCM Encryption** - VIP data protection
- **Role-Based Access Control** - Hierarchical user permissions
- **Audit Logging** - Complete activity tracking
- **Data Retention Policies** - NDPR/GDPR compliance

### 📊 **Scalability Features**
- **Table Partitioning** - Monthly partitions for rides and location data
- **Materialized Views** - Pre-computed analytics
- **Optimized Indexes** - Performance-tuned queries
- **Connection Pooling Ready** - Prepared for high concurrency

## File Structure

```
database/
├── 01_extensions_and_schemas.sql     # Extensions, schemas, and base functions
├── 02_main_tables.sql               # Core application tables
├── 03_vip_schema.sql                # VIP data with encryption
├── 04_rides_and_bookings.sql        # Rides system with partitioning
├── 05_payments_and_finance.sql      # Payment processing and finance
├── 06_audit_schema.sql              # Audit logging and compliance
├── 07_security_policies.sql         # RLS policies and security
├── 08_analytics_and_archive.sql     # Analytics and archival
├── 09_deployment_setup.sql          # Deployment and configuration
└── README.md                        # This documentation
```

## Key Features

### 🚨 **VIP Data Protection**
- **Separate Schema Isolation** - VIP data in dedicated schema
- **Field-Level Encryption** - Sensitive data encrypted at rest
- **Access Logging** - Every VIP data access tracked
- **Emergency Override** - Emergency responder access during incidents
- **Geofencing Alerts** - Location-based security monitoring

### 💳 **Multi-Tier Commission System**
- **Dynamic Commission Rates** - Tier-based commission calculation
- **Normal Users**: 15-20% commission
- **Premium Users**: 20-25% commission  
- **VIP Users**: 25-30% commission
- **Revenue Sharing** - Vehicle lease integration

### 🚗 **Fleet Management**
- **Multi-Category Drivers** - Private drivers, fleet drivers, owner-operators
- **Vehicle Leasing** - Revenue-sharing contracts
- **Subscription Tiers** - $99-$299 monthly driver subscriptions
- **Performance Tracking** - Driver and fleet analytics

### 🏨 **Hotel Integration**
- **Partnership Tiers** - Standard, preferred, exclusive
- **Room Management** - Dynamic pricing and availability
- **Booking Integration** - Seamless ride + hotel booking
- **Commission Tracking** - Partner revenue management

### 📈 **Analytics & Reporting**
- **Real-Time Metrics** - Performance dashboards
- **Business Intelligence** - Revenue and usage analytics
- **Compliance Reporting** - NDPR/GDPR compliance tracking
- **Predictive Analytics** - Customer behavior insights

## Deployment Instructions

### Prerequisites
```bash
# PostgreSQL 14+ with extensions
sudo apt-get install postgresql-14 postgresql-14-postgis-3
sudo apt-get install postgresql-contrib-14

# Create database
createdb vip_ride_platform_db
```

### Step 1: Basic Setup
```sql
-- Connect as superuser
psql -U postgres -d vip_ride_platform_db

-- Run schema files in order
\i 01_extensions_and_schemas.sql
\i 02_main_tables.sql
\i 03_vip_schema.sql
```

### Step 2: Application Features
```sql
\i 04_rides_and_bookings.sql
\i 05_payments_and_finance.sql
\i 06_audit_schema.sql
```

### Step 3: Security & Analytics
```sql
\i 07_security_policies.sql
\i 08_analytics_and_archive.sql
\i 09_deployment_setup.sql
```

### Step 4: Create Application Users
```sql
-- Create application roles (see deployment_setup.sql)
CREATE USER app_backend WITH PASSWORD 'secure_password';
GRANT authenticated_user TO app_backend;
```

## Security Configuration

### User Roles Hierarchy
```
system_admin
├── audit_admin
├── compliance_officer
└── authenticated_user
    ├── vip_admin
    │   ├── vip_operator
    │   └── emergency_responder
    ├── fleet_admin
    ├── driver_user
    ├── customer_user
    ├── support_agent
    └── hotel_staff
```

### VIP Data Access Control
- **VIP Admin**: Full access to all VIP data
- **VIP Operator**: Read-only access to VIP profiles
- **Emergency Responder**: Access during emergencies only
- **Customer**: Limited access to own profile data

### Encryption Implementation
```sql
-- Encrypt VIP location data
SELECT encrypt_vip_data('{"lat": 6.5244, "lng": 3.3792}');

-- Decrypt for authorized access
SELECT decrypt_vip_data(encrypted_coordinates) 
FROM vip_data.vip_location_history 
WHERE user_id = 'vip_user_uuid';
```

## Performance Optimization

### Partitioning Strategy
- **Rides Table**: Monthly partitions by `requested_at`
- **VIP Location**: Monthly partitions by `recorded_at`
- **Audit Logs**: Monthly partitions by `timestamp`

### Index Strategy
- **Primary Keys**: UUID with btree indexes
- **Foreign Keys**: btree indexes for joins
- **Location Data**: GiST indexes for geospatial queries
- **Text Search**: GIN indexes for full-text search
- **Time Series**: btree indexes on timestamp columns

### Query Optimization
```sql
-- Efficient VIP user lookup
SELECT * FROM vip_data.vip_profiles 
WHERE user_id = $1; -- Uses primary key index

-- Efficient ride history query
SELECT * FROM public.rides 
WHERE customer_id = $1 
  AND requested_at >= $2 
  AND requested_at < $3; -- Uses partition elimination
```

## Compliance Features

### NDPR/GDPR Compliance
- **Data Retention**: Automated archival after 7 years
- **Right to Erasure**: Soft delete with anonymization
- **Data Portability**: Export functions for user data
- **Consent Tracking**: User consent management
- **Breach Notification**: Automated incident reporting

### Audit Trail
```sql
-- Complete audit trail for all changes
SELECT * FROM audit.audit_log 
WHERE table_name = 'users' 
  AND record_id = 'user_uuid'
ORDER BY timestamp DESC;

-- VIP data access monitoring
SELECT * FROM audit.vip_access_log 
WHERE vip_user_id = 'vip_user_uuid'
ORDER BY accessed_at DESC;
```

## Monitoring & Maintenance

### Health Monitoring
```sql
-- Database health check
SELECT * FROM monitoring.database_health;

-- Performance metrics
SELECT * FROM monitoring.performance_metrics;

-- Security alerts
SELECT * FROM monitoring.security_alerts;
```

### Maintenance Tasks
```sql
-- Daily maintenance
SELECT maintenance.vacuum_analyze_all();
SELECT maintenance.update_statistics();

-- Monthly archival
SELECT archive.archive_old_data('rides', 84); -- 7 years
```

## Backup Strategy

### Full Backup (Daily)
```bash
pg_dump -h localhost -U app_backend -Fc \
  -f backup_$(date +%Y%m%d).dump \
  vip_ride_platform_db
```

### VIP Data Backup (Additional Security)
```bash
pg_dump -h localhost -U app_backend -Fc \
  -n vip_data \
  -f vip_backup_$(date +%Y%m%d).dump \
  vip_ride_platform_db
```

### Point-in-Time Recovery
```bash
# Configure WAL archiving in postgresql.conf
archive_mode = on
archive_command = 'cp %p /backup/archive/%f'
```

## API Integration

### Django Model Mapping
The database schema is designed to work seamlessly with the Django models:

- `public.users` → `accounts.models.User`
- `public.drivers` → `accounts.models.Driver`
- `public.rides` → `rides.models.Ride`
- `vip_data.vip_profiles` → `accounts.models.VIPProfile`
- `public.payments` → `payments.models.Payment`

### Connection String
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'vip_ride_platform_db',
        'USER': 'app_backend',
        'PASSWORD': 'secure_password',
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'sslmode': 'require',
        }
    }
}
```

## Troubleshooting

### Common Issues

1. **Permission Denied on VIP Schema**
   ```sql
   GRANT USAGE ON SCHEMA vip_data TO app_backend;
   GRANT vip_operator TO app_backend;
   ```

2. **Partition Creation Errors**
   ```sql
   SELECT create_monthly_ride_partition('2025-09-01'::DATE);
   ```

3. **Encryption Key Issues**
   ```sql
   -- Verify encryption functions
   SELECT encrypt_vip_data('test'), decrypt_vip_data(encrypt_vip_data('test'));
   ```

## Support & Documentation

For additional support:
- **Schema Documentation**: See comments in SQL files
- **Performance Tuning**: Check `monitoring` schema views
- **Security Guidelines**: Review `07_security_policies.sql`
- **Compliance**: Check `audit` schema documentation

## Version History

- **v1.0** - Initial schema with basic features
- **v1.1** - Added VIP data encryption and isolation
- **v1.2** - Enhanced audit logging and compliance
- **v1.3** - Added partitioning and performance optimizations
- **v1.4** - Complete security policies and monitoring

---

**Note**: This schema is designed for production use with proper security measures. Always review and adapt security settings for your specific environment and compliance requirements.
