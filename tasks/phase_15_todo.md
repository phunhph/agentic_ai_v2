# Phase 15 To-Do: Agent Analytics & Feedback Loops

## 1. Human-in-the-loop Feedback UI
- [x] Integrate 👍/👎 feedback buttons into Streamlit assistant messages
- [x] Create API endpoint `/feedback` to capture user ratings
- [x] Implement feedback storage linked to `audit_zone.agent_logs`

## 2. Audit Zone Enhancement
- [x] Update `audit_zone.agent_logs` schema:
    - [x] Add `token_usage` (INT)
    - [x] Add `cost_usd` (FLOAT)
    - [x] Add `response_time_ms` (INT)
    - [x] Add `user_feedback` (INT)
- [x] Implement automatic telemetry capture for every Agent request

## 3. Analytics & KPI Dashboards
- [x] Implement Cost Analytics (Usage by Agent, Provider, Day)
- [x] Implement Latency Analytics and Performance Benchmarking
- [x] Create Streamlit Dashboard for system-wide KPIs (Success Rate, ROI, Error frequency)

## 4. Knowledge Purification System
- [x] Implement `failed_patterns` registry for SQL patterns with negative feedback
- [x] Implement `Memory Purification` cron job to flag/remove low-rated recipes
- [x] Implement `Feedback-weighted Retrieval` (prioritize high-rated patterns)

## 5. Negative Learning (Anti-patterns)
- [x] Implement `Anti-pattern Injection` into the Reasoning Agent prompt
- [x] Test if Agent avoids known bad joins/aggregations after purification
- [x] Implement `Knowledge Curator` agent to suggest manual prompt fixes based on frequent failures
