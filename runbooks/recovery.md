# Recovery Runbook

## Use case

Follow this runbook when data or service recovery is required after a failure.

## Recovery steps

1. Verify the most recent good backup file exists.
2. Stop the affected service(s).
3. Restore the database from backup.
4. Start the service(s) back up.
5. Validate health endpoints.
6. Run a smoke test query against the API.
7. Confirm audit logs and checkpoints are present.

## Database restore

Use the backup file created by `scripts/backup.py`.

Example restore command:

```bash
pg_restore --clean --no-owner --dbname=$DB_NAME agentic_backup_<timestamp>.sql
```

## Post-recovery validation

- [ ] API `/health` returns 200
- [ ] API `/ready` returns 200
- [ ] Sample query completes successfully
- [ ] Audit logs contain recent operations
- [ ] No new critical errors appear in logs
