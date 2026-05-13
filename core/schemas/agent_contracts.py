from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class ReasoningStep(BaseModel):
    step: str
    detail: str


class ReasoningStateModel(BaseModel):
    reasoning_id: str
    thread_id: str
    session_id: str | None = None
    business_intent: str
    complexity: Literal["simple", "standard", "nested", "complex"]
    related_views: list[str]
    assumptions: list[str]
    reasoning_steps: list[ReasoningStep]
    normalized_prompt: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class PlanningTaskModel(BaseModel):
    task_id: str
    description: str
    depends_on: list[str] = Field(default_factory=list)
    status: Literal["pending", "ready", "completed", "failed", "blocked"] = "pending"


class PlanningStateModel(BaseModel):
    plan_id: str
    thread_id: str
    session_id: str | None = None
    business_intent: str | None = None
    complexity: str | None = None
    task_count: int
    tasks: list[PlanningTaskModel]
    summary: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
