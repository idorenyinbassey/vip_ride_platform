#!/bin/bash
# VIP Ride Platform Restore Script

set -e

if [ $# -eq 0 ]; then
    echo "Usage: $0 <backup_timestamp>"
    echo "Available backups:"
    ls -la /backups/
    exit 1
fi

TIMESTAMP=$1
BACKUP_DIR="/backups"
DB_CONTAINER="vip_ride_platform_db_1"

# Restore database
if [ -f "$BACKUP_DIR/db_backup_$TIMESTAMP.sql.gz" ]; then
    echo "Restoring database from backup: $TIMESTAMP"
    gunzip -c $BACKUP_DIR/db_backup_$TIMESTAMP.sql.gz | docker exec -i $DB_CONTAINER psql -U $DB_USER $DB_NAME
else
    echo "Database backup not found: $BACKUP_DIR/db_backup_$TIMESTAMP.sql.gz"
    exit 1
fi

# Restore media files
if [ -f "$BACKUP_DIR/media_backup_$TIMESTAMP.tar.gz" ]; then
    echo "Restoring media files from backup: $TIMESTAMP"
    tar -xzf $BACKUP_DIR/media_backup_$TIMESTAMP.tar.gz -C /
else
    echo "Media backup not found: $BACKUP_DIR/media_backup_$TIMESTAMP.tar.gz"
fi

echo "Restore completed: $TIMESTAMP"
