# Rollback Runbook

## When to use

Use this runbook when a deployment introduces a failure that cannot be immediately fixed in production.

## Steps

1. Identify the failed deployment and affected services.
2. Notify stakeholders and operations owner.
3. Verify the latest known-good backup exists.
4. Stop the failing services:
   - API
   - UI
5. Restore the previous release or container image.
6. If a database restore is required, follow `runbooks/recovery.md`.
7. Restart services and validate:
   - `http://localhost:8000/health`
   - `http://localhost:8000/ready`
8. Confirm the issue is resolved.
9. Document the rollback action and update incident notes.

## Post-rollback validation

- [ ] API returns 200 on `/health`
- [ ] API returns 200 on `/ready`
- [ ] Sample user query returns expected trace data
- [ ] Audit logs are intact
