from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class QueryFilter(BaseModel):
    column: str
    op: Literal["=", "ilike", "in"] = "="
    value: Any


class QueryJoin(BaseModel):
    left_table: str
    left_column: str
    right_table: str
    right_column: str


class QueryPlan(BaseModel):
    strategy: Literal["single_table", "join"] = "single_table"
    base_table: str
    select: list[str] = Field(default_factory=list)
    filters: list[QueryFilter] = Field(default_factory=list)
    joins: list[QueryJoin] = Field(default_factory=list)
    limit: int = 50
