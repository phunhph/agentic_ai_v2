#!/bin/bash
# Restore PostgreSQL database
set -e

if [ -z "$1" ]; then
  echo "Usage: $0 <path_to_backup_file>"
  exit 1
fi

BACKUP_FILE=$1

# Load environment variables
if [ -f ../.env ]; then
  source ../.env
fi

DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5433}
DB_USER=${DB_USER:-postgres}
DB_NAME=${DB_NAME:-agentic_ai}

echo "Restoring database $DB_NAME from $BACKUP_FILE..."
PGPASSWORD=$DB_PASSWORD pg_restore -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -1 $BACKUP_FILE

echo "Restore completed successfully!"
