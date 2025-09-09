#!/bin/bash
# VIP Ride Platform Backup Script

set -e

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
DB_CONTAINER="vip_ride_platform_db_1"
MEDIA_DIR="/app/media"

mkdir -p $BACKUP_DIR

# Database backup
echo "Creating database backup..."
docker exec $DB_CONTAINER pg_dump -U $DB_USER $DB_NAME > $BACKUP_DIR/db_backup_$TIMESTAMP.sql
gzip $BACKUP_DIR/db_backup_$TIMESTAMP.sql

# Media files backup
echo "Creating media files backup..."
tar -czf $BACKUP_DIR/media_backup_$TIMESTAMP.tar.gz $MEDIA_DIR

# Cleanup old backups (keep last 7 days)
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "Backup completed: $TIMESTAMP"
