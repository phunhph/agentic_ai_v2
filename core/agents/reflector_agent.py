from __future__ import annotations
from typing import Any, Dict, List

from core.utils.infra.audit import log_agent_event
from core.utils.infra.checkpoint import CheckpointStore


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

        reflection_state = {
            "reflection_id": f"reflect-{thread_id}",
            "thread_id": thread_id,
            "session_id": session_id,
            "status": status,
            "issues": issues,
            "suggested_action": "retry" if status == "fail" else "continue",
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
