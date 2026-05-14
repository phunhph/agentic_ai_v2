import uuid
import logging
from typing import Any, Dict, List

from core.tools.mcp_tool import MCPTool
from core.utils.infra.audit import log_agent_event
from core.utils.infra.checkpoint import CheckpointStore
from pydantic import BaseModel
from core.utils.llm import generate_structured_output

logger = logging.getLogger(__name__)

class SQLOutput(BaseModel):
    sql: str

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
            task_sql = self._build_task_sql(task, schema_context, prompt)
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

    def _build_task_sql(self, task: Dict[str, Any], schema_context: dict[str, Any], prompt: str) -> str:
        views = schema_context.get("views", [])
        details = schema_context.get("details", [])
        description = task.get("description") or ""

        system_prompt = f"""
        You are a Postgres SQL Expert Agent.
        Your task is to write a syntactically correct and safe PostgreSQL query to satisfy the current execution task.
        
        Original User Request: "{prompt}"
        Current Task: "{description}"
        
        Available Schema Context:
        Views: {views}
        Details: {details}
        
        IMPORTANT: Return ONLY the raw SQL query. Do not wrap in markdown or add explanations.
        """
        
        try:
            llm_result = generate_structured_output(system_prompt, SQLOutput)
            sql = llm_result.sql.replace('```sql', '').replace('```', '').strip()
            return sql
        except Exception as e:
            logger.error(f"ExecutionAgent SQL generation error: {e}")
            target = views[0] if views else "business_zone.v_hbl_accounts"
            if "count" in description.lower() or "aggregate" in description.lower():
                return f"SELECT COUNT(*) AS count FROM {target}"
            return f"SELECT * FROM {target} LIMIT 10"

