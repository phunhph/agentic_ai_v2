# Deployment Guide

This document describes the deployment and operational flow for Agentic AI.

## Environment

Required environment variables:

- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `OPENAI_API_KEY` or other provider credentials

## Recommended deployment flow

1. Initialize the database:
   - `python scripts/init_db.py`
2. Run the application:
   - `python run.py api`
   - `python run.py ui`
3. Validate the service:
   - `http://localhost:8000/health`
   - `http://localhost:8000/ready`

## Production checklist

See `docs/deployment/production_checklist.md` for an operational checklist.

## Backup and recovery

- Use `python scripts/backup.py` to create a PostgreSQL dump
- Use `runbooks/recovery.md` to restore from backup if needed

## Monitoring

- Use `python scripts/monitor.py` for simple health checks
- Integrate into production monitoring based on this pattern
