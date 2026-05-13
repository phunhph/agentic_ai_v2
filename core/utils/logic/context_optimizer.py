from __future__ import annotations
from typing import Any, Dict, List


class ContextOptimizer:
    def optimize(
        self,
        ingest_state: Dict[str, Any] | None,
        schema_context: Dict[str, Any],
        thread_id: str,
        session_id: str | None = None,
    ) -> Dict[str, Any]:
        views = schema_context.get("views", [])
        related_views = self._prune_views(views, ingest_state)
        history_summary = self._summarize_history(ingest_state)
        mini_schema = self._build_mini_schema(related_views)

        return {
            "thread_id": thread_id,
            "session_id": session_id,
            "related_views": related_views,
            "history_summary": history_summary,
            "mini_schema": mini_schema,
            "context_score": self._estimate_context_size(related_views, history_summary),
        }

    def _prune_views(self, views: List[str], ingest_state: Dict[str, Any] | None) -> List[str]:
        if not ingest_state or not views:
            return views[:2]

        entities = ingest_state.get("entities", {})
        if entities.get("labels"):
            labels = [label.lower() for label in entities["labels"]]
            return [view for view in views if any(label in view for label in labels)] or views[:2]
        return views[:2]

    def _summarize_history(self, ingest_state: Dict[str, Any] | None) -> str:
        if not ingest_state:
            return "No prior context."
        metadata = ingest_state.get("metadata", {})
        resume_thread_id = metadata.get("resume_thread_id")
        if resume_thread_id:
            return f"Resuming from thread {resume_thread_id}."
        return "Recent user intent preserved."

    def _build_mini_schema(self, views: List[str]) -> str:
        if not views:
            return "Using default semantic views for accounts and contacts."
        return f"Mini schema includes: {', '.join(views)}."

    def _estimate_context_size(self, views: List[str], history_summary: str) -> int:
        return len(views) * 50 + len(history_summary.split())
