import uuid
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from core.schemas.agent_contracts import PlanningStateModel
from core.utils.infra.checkpoint import CheckpointStore
from core.utils.llm import generate_structured_output

logger = logging.getLogger(__name__)

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
        
        detected_language = reasoning_state.get("detected_language", "en")
        
        system_prompt = f"""
        You are an expert Planning Agent for a Business AI system.
        Your task is to take the output of the Reasoning Agent and build an ordered execution plan (a list of SQL/query tasks).
        
        User Language: {detected_language}
        (Always generate task descriptions and summaries in this language).
        
        Reasoning State:
        {reasoning_state}
        
        Generate a list of dependent tasks to execute this request against the CRM database.
        Make sure each task has a unique task_id, a clear description, and depends_on (list of previous task_ids it requires).
        Status should be 'pending'.
        """

        try:
            llm_result = generate_structured_output(system_prompt, PlanningStateModel)
            state = llm_result.model_dump(mode="json")
        except Exception as e:
            logger.error(f"PlanningAgent LLM error: {e}. Falling back to default plan.")
            state = {
                "tasks": [{"task_id": "task_1", "description": "Fallback task", "depends_on": [], "status": "pending"}],
                "task_count": 1,
                "summary": "Fallback plan due to error",
            }
            
        # Ensure mandatory server-side fields
        state["plan_id"] = str(uuid.uuid4())
        state["thread_id"] = thread_id
        state["session_id"] = session_id
        state["business_intent"] = reasoning_state.get("business_intent")
        state["complexity"] = reasoning_state.get("complexity")
        state["detected_language"] = detected_language
        state["metadata"] = metadata or {}
        state["created_at"] = datetime.utcnow().isoformat() + "Z"
        
        # Ensure tasks match task_count
        if "tasks" in state:
            state["task_count"] = len(state["tasks"])

        validated_state = PlanningStateModel.model_validate(state).model_dump(mode="json")

        self.store.save_state(
            thread_id=thread_id,
            session_id=session_id,
            state_data=validated_state,
            state_type="planning",
            previous_checkpoint_id=reasoning_state.get("reasoning_id"),
        )
        return validated_state
