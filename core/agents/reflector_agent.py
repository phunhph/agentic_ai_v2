import logging
from typing import Any, Dict, List

from core.utils.infra.audit import log_agent_event
from core.utils.infra.checkpoint import CheckpointStore
from core.utils.llm import generate_structured_output
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class ReflectionOutput(BaseModel):
    status: str # pass, fail, warn
    issues: List[str]
    suggested_action: str # retry, continue

class ReflectorAgent:
    def __init__(self) -> None:
        self.store = CheckpointStore()

    def evaluate(
        self,
        execution_state: Dict[str, Any],
        reasoning_state: Dict[str, Any],
        planning_state: Dict[str, Any],
        thread_id: str,
        session_id: str,
    ) -> Dict[str, Any]:
        
        system_prompt = f"""
        You are a Database Reflector Agent. Your job is to evaluate the results of an SQL execution process.
        
        Business Intent: {reasoning_state.get('business_intent')}
        Planning Tasks: {planning_state.get('tasks')}
        Execution Tasks Results: {execution_state.get('tasks')}
        Overall Execution Status: {execution_state.get('status')}
        Overall Error: {execution_state.get('error')}
        
        Analyze the execution.
        If there are SQL syntax errors, missing columns, or bad results (e.g. 0 rows when expecting data), set status to "fail" and suggest "retry" with detailed issues.
        If results look good, set status to "pass" and suggest "continue".
        """
        
        try:
            llm_result = generate_structured_output(system_prompt, ReflectionOutput)
            status = llm_result.status
            issues = llm_result.issues
            suggested_action = llm_result.suggested_action
        except Exception as e:
            logger.error(f"ReflectorAgent LLM error: {e}. Using fallback logic.")
            issues: List[str] = []
            status = "pass"

            if execution_state.get("status") != "success":
                status = "fail"
                issues.append(execution_state.get("error", "Execution failed"))

            zero_row_tasks: list[str] = []
            completed_tasks = 0

            for task in execution_state.get("tasks", []):
                if task.get("status") != "completed":
                    status = "fail"
                    issues.append(f"Task {task.get('task_id')} failed or rejected")
                    continue

                completed_tasks += 1
                result = task.get("result")
                if isinstance(result, dict) and result.get("count") == 0:
                    zero_row_tasks.append(task.get("task_id", "unknown"))
                    issues.append(f"Task {task.get('task_id')} returned no rows")

            if completed_tasks > 0 and len(zero_row_tasks) == completed_tasks:
                status = "fail"
            elif status == "pass" and zero_row_tasks:
                status = "warn"

            if status == "pass" and not issues:
                status = "pass"
            elif status == "warn" and not issues:
                status = "warn"
                
            suggested_action = "retry" if status == "fail" else "continue"

        reflection_state = {
            "reflection_id": f"reflect-{thread_id}",
            "thread_id": thread_id,
            "session_id": session_id,
            "status": status,
            "issues": issues,
            "suggested_action": suggested_action,
        }

        log_agent_event(thread_id, "reflection", reflection_state)
        self.store.save_state(
            thread_id=thread_id,
            session_id=session_id,
            state_data=reflection_state,
            state_type="reflection",
            previous_checkpoint_id=execution_state.get("execution_id"),
        )
        return reflection_state
