import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from core.schemas import PlanningStateModel
from core.utils.infra.checkpoint import CheckpointStore


class PlanningAgent:
    def __init__(self) -> None:
        self.store = CheckpointStore()

    def plan(
        self,
        reasoning_state: Dict[str, Any],
        thread_id: str,
        session_id: str | None = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        task_descriptions = self._plan_tasks(reasoning_state)
        tasks = self._build_task_queue(task_descriptions)

        state = {
            "plan_id": str(uuid.uuid4()),
            "thread_id": thread_id,
            "session_id": session_id,
            "business_intent": reasoning_state.get("business_intent"),
            "complexity": reasoning_state.get("complexity"),
            "task_count": len(tasks),
            "tasks": tasks,
            "summary": f"Planned {len(tasks)} step(s) for intent {reasoning_state.get('business_intent')}",
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat() + "Z",
        }

        validated_state = PlanningStateModel.model_validate(state).model_dump(mode="json")

        self.store.save_state(
            thread_id=thread_id,
            session_id=session_id,
            state_data=validated_state,
            state_type="planning",
            previous_checkpoint_id=reasoning_state.get("reasoning_id"),
        )
        return validated_state

    def _plan_tasks(self, reasoning_state: Dict[str, Any]) -> List[str]:
        complexity = reasoning_state.get("complexity", "simple")
        steps = reasoning_state.get("reasoning_steps", [])
        descriptions: List[str] = []

        if complexity == "simple":
            descriptions = [
                "Confirm entities and intent.",
                "Generate the final data extraction plan.",
            ]
        elif complexity == "standard":
            descriptions = [
                "Map entities to semantic views.",
                "Define aggregation and ranking operations.",
                "Prepare ordered execution plan." 
            ]
        else:
            descriptions = [
                "Decompose the complex request into sub-queries.",
                "Establish joins and lookup relationships.",
                "Validate temporal and grouping logic.",
                "Sequence task execution for safe planning." 
            ]

        if any(step.get("step") == "compare_periods" for step in steps):
            descriptions.insert(0, "Analyze period comparisons and temporal context.")
        return descriptions

    def _build_task_queue(self, descriptions: List[str]) -> List[Dict[str, Any]]:
        tasks: List[Dict[str, Any]] = []
        previous_id: Optional[str] = None
        for index, description in enumerate(descriptions, start=1):
            task_id = f"task_{index}"
            tasks.append(
                {
                    "task_id": task_id,
                    "description": description,
                    "depends_on": [previous_id] if previous_id else [],
                    "status": "pending",
                }
            )
            previous_id = task_id
        return tasks
