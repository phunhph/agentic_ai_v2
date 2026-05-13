# Production Deployment Checklist

## Pre-deployment

- [ ] Database initialized and schema applied
- [ ] Environment variables configured and secrets loaded securely
- [ ] Backup created and verified
- [ ] API health and readiness endpoints accessible
- [ ] Audit logging enabled
- [ ] RBAC and access controls documented

## Deployment

- [ ] API container or process started successfully
- [ ] UI (Streamlit) launched and reachable
- [ ] `health` endpoint returns 200
- [ ] `ready` endpoint returns 200
- [ ] Logs are flowing to the expected audit store
- [ ] Metrics ingestion is operational

## Post-deployment

- [ ] Smoke test sample queries
- [ ] Verify `trace` endpoint returns historical thread events
- [ ] Confirm backup schedule is defined
- [ ] Confirm incident runbooks are available and shared
- [ ] Review any monitoring alerts
