import uuid
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from core.schemas.agent_contracts import ReasoningStateModel
from core.utils.infra.checkpoint import CheckpointStore
from core.utils.llm import generate_structured_output

logger = logging.getLogger(__name__)

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
        
        normalized_prompt = ingest_state.get("normalized_prompt", prompt) if ingest_state else prompt.strip()
        detected_language = ingest_state.get("detected_language", "en") if ingest_state else "en"
        
        system_prompt = f"""
        You are an expert Business Analyst Agent.
        Your task is to analyze the user's prompt and extract reasoning steps, assumptions, complexity, related CRM views, and business intent.
        
        User Language: {detected_language}
        (Note: Always respond with reasoning steps in the User Language).
        
        User Prompt: "{normalized_prompt}"
        
        Analyze the prompt carefully and return the structured analysis.
        """
        
        try:
            # Note: We create a dummy response object to ensure reasoning_id and other server-side fields are populated 
            # after the LLM returns the partial schema.
            # But the schema validation in llm.py expects the full model, so we need a simplified model for output or 
            # we just let the LLM generate the whole thing and overwrite the IDs.
            
            # Let's let the LLM generate the full ReasoningStateModel, but we will overwrite IDs and timestamps to be safe.
            llm_result = generate_structured_output(system_prompt, ReasoningStateModel)
            state = llm_result.model_dump(mode="json")
            
        except Exception as e:
            logger.error(f"ReasoningAgent LLM error: {e}. Falling back to default state.")
            state = {
                "business_intent": "general_analysis",
                "complexity": "standard",
                "related_views": ["accounts", "contacts"],
                "assumptions": ["Assuming general analysis"],
                "reasoning_steps": [{"step": "fallback_step", "detail": "Fallback due to LLM error"}],
            }
            
        # Ensure mandatory and secure fields are set by the server, not the LLM
        state["reasoning_id"] = str(uuid.uuid4())
        state["thread_id"] = thread_id
        state["session_id"] = session_id
        state["normalized_prompt"] = normalized_prompt
        state["detected_language"] = detected_language
        state["metadata"] = metadata or {}
        state["created_at"] = datetime.utcnow().isoformat() + "Z"

        validated_state = ReasoningStateModel.model_validate(state).model_dump(mode="json")

        self.store.save_state(
            thread_id=thread_id,
            session_id=session_id,
            state_data=validated_state,
            state_type="reasoning",
            previous_checkpoint_id=(ingest_state or {}).get("checkpoint_id") if ingest_state else None,
        )
        return validated_state
