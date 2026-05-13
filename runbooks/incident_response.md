# Incident Response Runbook

## Incident detection

Look for:

- API health failures
- readiness checks failing
- repeated errors in audit logs
- database availability issues
- abnormal latency or retry spikes

## Response plan

1. Acknowledge the incident.
2. Record the time and scope.
3. Identify the impacted component:
   - API
   - UI
   - Database
   - LLM provider
4. Collect logs and recent audit events.
5. Determine if immediate rollback is required.
6. Apply mitigation:
   - restart service
   - disable problematic feature
   - rollback deployment
7. Notify stakeholders and update the incident status.

## Communication

- Notify the team with an incident summary
- Share affected endpoints and current status
- Assign an owner for follow-up

## Recovery

- Validate service health after mitigation
- Check audit trace consistency
- Document root cause when resolved
