from __future__ import annotations
import uuid
from typing import Any, Dict, List

from core.tools.mcp_tool import MCPTool
from core.utils.infra.audit import log_agent_event
from core.utils.infra.checkpoint import CheckpointStore


class ExecutionAgent:
    def __init__(self) -> None:
        self.mcp_tool = MCPTool()
        self.store = CheckpointStore()

    def execute(
        self,
        planning_state: Dict[str, Any],
        thread_id: str,
        session_id: str,
        schema_context: dict[str, Any],
        prompt: str,
    ) -> Dict[str, Any]:
        tasks = planning_state.get("tasks", [])
        task_results: List[Dict[str, Any]] = []
        overall_status = "success"
        error = None

        for task in tasks:
            task_sql = self._build_task_sql(task, schema_context)
            preview = self.mcp_tool.preview(task_sql)
            task_result = {
                "task_id": task.get("task_id"),
                "description": task.get("description"),
                "sql": task_sql,
                "allowed": preview.get("allowed", False),
            }

            if not preview.get("allowed", False):
                task_result["status"] = "rejected"
                task_result["error"] = "SQL not allowed by policy"
                overall_status = "failed"
                error = task_result["error"]
                task_results.append(task_result)
                break

            try:
                result = self.mcp_tool.execute(thread_id, task_sql, session_id)
                task_result["status"] = "completed"
                task_result["result"] = result
            except Exception as exc:
                task_result["status"] = "failed"
                task_result["error"] = str(exc)
                overall_status = "failed"
                error = str(exc)

            task_results.append(task_result)
            if overall_status == "failed":
                break

        execution_state = {
            "execution_id": str(uuid.uuid4()),
            "thread_id": thread_id,
            "session_id": session_id,
            "status": overall_status,
            "tasks": task_results,
            "error": error,
        }

        log_agent_event(thread_id, "execution", execution_state)
        self.store.save_state(
            thread_id=thread_id,
            session_id=session_id,
            state_data=execution_state,
            state_type="execution",
            previous_checkpoint_id=planning_state.get("plan_id"),
        )
        return execution_state

    def _build_task_sql(self, task: Dict[str, Any], schema_context: dict[str, Any]) -> str:
        views = schema_context.get("views", [])
        target = views[0] if views else "business_zone.v_hbl_accounts"
        description = (task.get("description") or "").lower()

        if "count" in description or "aggregate" in description:
            return f"SELECT COUNT(*) AS count FROM {target}"
        if "rank" in description or "sort" in description:
            return f"SELECT * FROM {target} ORDER BY created_at DESC LIMIT 10"
        if "compare" in description or "temporal" in description:
            return f"SELECT * FROM {target} LIMIT 5"
        return f"SELECT * FROM {target} LIMIT 5"
