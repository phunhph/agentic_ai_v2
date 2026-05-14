#!/bin/bash
# Backup PostgreSQL database
set -e

# Load environment variables
if [ -f ../.env ]; then
  source ../.env
fi

DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5433}
DB_USER=${DB_USER:-postgres}
DB_NAME=${DB_NAME:-agentic_ai}

BACKUP_DIR="../data/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/${DB_NAME}_backup_$DATE.sql"

mkdir -p $BACKUP_DIR

echo "Starting backup of $DB_NAME to $BACKUP_FILE..."
PGPASSWORD=$DB_PASSWORD pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER -F c -b -v -f $BACKUP_FILE $DB_NAME

echo "Backup completed successfully!"
