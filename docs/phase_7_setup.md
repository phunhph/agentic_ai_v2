# Phase 7: Optimization, Cost Routing, and Multitenancy

This phase introduces Phase 7 functionality for optimization, cost-aware model routing, tenant-level safety, and observability.

## Goals

- Add a context optimizer that builds a mini-schema, prunes unrelated views, and summarizes conversation history.
- Add cost-aware LLM routing that chooses a model profile based on prompt complexity.
- Add tenant guard and row-level security helpers for session-level isolation.
- Add metrics tracing for API and reasoning events.
- Integrate Phase 7 logic into the runtime pipeline without changing the existing Phase 6 runtime flow.

## New Modules

- `core/utils/logic/context_optimizer.py`
- `core/utils/logic/cost_router.py`
- `core/utils/logic/tenant_guard.py`
- `core/utils/logic/rls_manager.py`
- `core/utils/logic/retry_policy.py`
- `core/utils/infra/metrics.py`

## Integration Points

- `core/graph/langgraph_runtime.py`
  - use `ContextOptimizer` to compress prompt context before generation
  - use `CostRouter` to select an appropriate model profile
  - preserve tenant session continuity using `TenantGuard`
- `core/tools/llm_router.py`
  - support a stable, cost-aware model selection path

## Metrics

A new metrics table is introduced under `audit_zone.api_metrics` to capture microservice latency and cost metrics.
