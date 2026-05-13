from __future__ import annotations

from core.schemas.agent_contracts import PlanningStateModel, ReasoningStateModel


def test_reasoning_contract_validation() -> None:
    state = {
        "reasoning_id": "r-1",
        "thread_id": "t-1",
        "session_id": "s-1",
        "business_intent": "revenue_analysis",
        "complexity": "standard",
        "related_views": ["accounts"],
        "assumptions": ["recent period aggregation"],
        "reasoning_steps": [{"step": "define_entities", "detail": "Identify entities"}],
        "normalized_prompt": "top accounts this month",
        "metadata": {},
        "created_at": "2026-01-01T00:00:00Z",
    }
    validated = ReasoningStateModel.model_validate(state)
    assert validated.business_intent == "revenue_analysis"


def test_planning_contract_and_execution_handoff_shape() -> None:
    planning_state = {
        "plan_id": "p-1",
        "thread_id": "t-1",
        "session_id": "s-1",
        "business_intent": "revenue_analysis",
        "complexity": "standard",
        "task_count": 2,
        "tasks": [
            {"task_id": "task_1", "description": "Map entities", "depends_on": [], "status": "pending"},
            {"task_id": "task_2", "description": "Prepare ordered execution plan", "depends_on": ["task_1"], "status": "pending"},
        ],
        "summary": "Planned 2 steps",
        "metadata": {},
        "created_at": "2026-01-01T00:00:00Z",
    }
    validated = PlanningStateModel.model_validate(planning_state)
    assert validated.task_count == len(validated.tasks)
    assert validated.tasks[1].depends_on == ["task_1"]


def test_reasoning_contract_allows_missing_session_id() -> None:
    state = {
        "reasoning_id": "r-2",
        "thread_id": "t-2",
        "session_id": None,
        "business_intent": "sales_performance",
        "complexity": "simple",
        "related_views": ["accounts"],
        "assumptions": [],
        "reasoning_steps": [{"step": "identify_revenue_source", "detail": "Determine revenue fields."}],
        "normalized_prompt": "show sales accounts",
        "metadata": {},
        "created_at": "2026-01-01T01:00:00Z",
    }
    validated = ReasoningStateModel.model_validate(state)
    assert validated.session_id is None
