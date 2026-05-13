import re
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from core.schemas import ReasoningStateModel
from core.utils.infra.checkpoint import CheckpointStore

BUSINESS_INTENT_MAP = {
    "revenue": "revenue_analysis",
    "sales": "sales_performance",
    "renewal": "renewal_forecast",
    "support": "support_ticket_summary",
    "customer": "customer_health_assessment",
    "pipeline": "pipeline_insight",
    "trend": "trend_analysis",
    "forecast": "forecasting",
}

COMPLEXITY_KEYWORDS = {
    "complex": ["trend", "compare", "history", "forecast", "cohort"],
    "nested": ["group by", "breakdown", "by region", "by industry", "by product"],
    "standard": ["top", "best", "highest", "average", "summary", "count"],
}

RELATED_VIEW_KEYWORDS = {
    "accounts": ["account", "customer", "client"],
    "contacts": ["contact", "lead", "email", "phone"],
    "embeddings": ["insight", "similarity", "embedding", "search"],
    "logs": ["audit", "trace", "history", "event"],
}


class ReasoningAgent:
    def __init__(self) -> None:
        self.store = CheckpointStore()

    def process(
        self,
        prompt: str,
        thread_id: str,
        session_id: str | None = None,
        ingest_state: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        normalized_prompt = ingest_state.get("normalized_prompt", prompt) if ingest_state else self._normalize_prompt(prompt)
        business_intent = self._deep_intent(normalized_prompt, ingest_state)
        complexity = self._classify_complexity(normalized_prompt)
        related_views = self._map_related_views(normalized_prompt)
        assumptions = self._extract_assumptions(normalized_prompt)
        steps = self._decompose_steps(normalized_prompt, business_intent)

        state = {
            "reasoning_id": str(uuid.uuid4()),
            "thread_id": thread_id,
            "session_id": session_id,
            "business_intent": business_intent,
            "complexity": complexity,
            "related_views": related_views,
            "assumptions": assumptions,
            "reasoning_steps": steps,
            "normalized_prompt": normalized_prompt,
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat() + "Z",
        }

        validated_state = ReasoningStateModel.model_validate(state).model_dump(mode="json")

        self.store.save_state(
            thread_id=thread_id,
            session_id=session_id,
            state_data=validated_state,
            state_type="reasoning",
            previous_checkpoint_id=(ingest_state or {}).get("checkpoint_id") if ingest_state else None,
        )
        return validated_state

    def _normalize_prompt(self, prompt: str) -> str:
        text = prompt.strip()
        text = re.sub(r"\s+", " ", text)
        return text

    def _deep_intent(self, prompt: str, ingest_state: Optional[Dict[str, Any]] = None) -> str:
        lower = prompt.lower()
        if ingest_state and ingest_state.get("intent"):
            base_intent = ingest_state["intent"]
        else:
            base_intent = "general"

        for token, intent in BUSINESS_INTENT_MAP.items():
            if token in lower:
                return intent

        if "report" in lower or "dashboard" in lower:
            return "report_generation"
        if "insight" in lower or "analysis" in lower:
            return "business_insight"
        return f"{base_intent}_analysis"

    def _classify_complexity(self, prompt: str) -> str:
        lower = prompt.lower()
        if any(keyword in lower for keyword in COMPLEXITY_KEYWORDS["complex"]):
            return "complex"
        if any(keyword in lower for keyword in COMPLEXITY_KEYWORDS["nested"]):
            return "nested"
        if any(keyword in lower for keyword in COMPLEXITY_KEYWORDS["standard"]):
            return "standard"
        return "simple"

    def _map_related_views(self, prompt: str) -> List[str]:
        lower = prompt.lower()
        views: List[str] = []
        for view_name, keywords in RELATED_VIEW_KEYWORDS.items():
            if any(token in lower for token in keywords):
                views.append(view_name)
        return views or ["accounts", "contacts"]

    def _extract_assumptions(self, prompt: str) -> List[str]:
        assumptions: List[str] = []
        lower = prompt.lower()
        if "quarter" in lower:
            assumptions.append("quarterly time window")
        if "month" in lower or "weekly" in lower:
            assumptions.append("recent period aggregation")
        if "top" in lower or "rank" in lower:
            assumptions.append("results should be sorted by value")
        if "trend" in lower or "compare" in lower:
            assumptions.append("requires temporal comparison")
        return assumptions

    def _decompose_steps(self, prompt: str, business_intent: str) -> List[Dict[str, str]]:
        lower = prompt.lower()
        steps: List[Dict[str, str]] = []

        if "revenue" in lower:
            steps.append({"step": "identify_revenue_source", "detail": "Determine revenue fields and related accounts."})
        if "top" in lower or "rank" in lower:
            steps.append({"step": "rank_entities", "detail": "Sort entities by the requested KPI."})
        if "trend" in lower or "compare" in lower or "history" in lower:
            steps.append({"step": "compare_periods", "detail": "Compare values across time periods."})
        if not steps:
            steps.append({"step": "define_entities", "detail": "Identify key CRM entities and business goals."})

        steps.append({"step": "validate_intent", "detail": f"Confirm business intent as {business_intent}."})
        return steps
