import uuid
import logging
import re
from typing import Any, Dict, List

from core.tools.mcp_tool import MCPTool
from core.query import DynamicQueryPlanner, QueryCompiler, SchemaCatalog
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
        self.catalog = SchemaCatalog()
        self.dynamic_planner = DynamicQueryPlanner(self.catalog)
        self.query_compiler = QueryCompiler(self.catalog)

    def execute(
        self,
        planning_state: Dict[str, Any],
        thread_id: str,
        session_id: str,
        schema_context: dict[str, Any],
        prompt: str,
    ) -> Dict[str, Any]:
        logger.info(f"[EXECUTION] Starting ExecutionAgent | Thread: {thread_id} | Session: {session_id}")
        logger.info(f"[EXECUTION] User Prompt: {prompt}")
        
        tasks = planning_state.get("tasks", [])
        task_order = self._topological_sort(tasks)
        task_results: List[Dict[str, Any]] = []
        execution_context: Dict[str, Any] = {}
        overall_status = "success"
        error = None

        for task in task_order:
            missing_dependencies = [
                dep for dep in task.get("depends_on", []) if dep not in execution_context
            ]
            task_result = {
                "task_id": task.get("task_id"),
                "description": task.get("description"),
                "depends_on": task.get("depends_on", []),
                "task_type": task.get("task_type", "query"),
                "input_refs": task.get("input_refs", []),
                "output_key": task.get("output_key"),
            }
            if missing_dependencies:
                task_result["status"] = "blocked"
                task_result["error"] = f"Missing dependencies: {', '.join(missing_dependencies)}"
                overall_status = "failed"
                error = task_result["error"]
                task_results.append(task_result)
                break

            if task.get("task_type") == "synthesis":
                task_result["status"] = "completed"
                task_result["result"] = self._synthesize_task_result(task, execution_context)
                execution_context[task.get("task_id", "")] = task_result
                output_key = task.get("output_key")
                if output_key:
                    execution_context[output_key] = task_result
                task_results.append(task_result)
                continue

            task_sql = self._build_task_sql(task, schema_context, prompt, execution_context)
            logger.info(f"[EXECUTION] Built SQL for task '{task.get('description')}': {task_sql}")
            
            preview = self.mcp_tool.preview(task_sql)
            task_result["sql"] = task_sql
            task_result["allowed"] = preview.get("allowed", False)

            if not preview.get("allowed", False):
                logger.error(f"[EXECUTION] SQL Rejected by policy: {task_sql}")
                task_result["status"] = "rejected"
                task_result["error"] = "SQL not allowed by policy"
                overall_status = "failed"
                error = task_result["error"]
                task_results.append(task_result)
                break

            try:
                logger.info(f"[EXECUTION] Executing task: {task.get('task_id')}")
                result = self.mcp_tool.execute(thread_id, task_sql, session_id)
                task_result["status"] = "completed"
                task_result["result"] = result
                execution_context[task.get("task_id", "")] = task_result
                output_key = task.get("output_key")
                if output_key:
                    execution_context[output_key] = task_result
                logger.info(f"[EXECUTION] Task completed successfully: {task.get('task_id')}")
            except Exception as exc:
                logger.error(f"[EXECUTION] Task failed with error: {exc}")
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
            "execution_context_keys": list(execution_context.keys()),
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
        logger.info(f"[EXECUTION] ExecutionAgent completed with status: {overall_status}")
        return execution_state

    def _build_task_sql(
        self,
        task: Dict[str, Any],
        schema_context: dict[str, Any],
        prompt: str,
        execution_context: Dict[str, Any] | None = None,
    ) -> str:
        views = schema_context.get("views", [])
        details = schema_context.get("details", [])
        description = task.get("description") or ""
        execution_context = execution_context or {}

        logger.info(f"[SQL_BUILDER] Building SQL for task: {description}")
        logger.info(f"[SQL_BUILDER] Available views: {views}")
        logger.info(f"[SQL_BUILDER] Schema details: {details}")

        dynamic_sql = self._build_dynamic_sql(prompt, description)
        if dynamic_sql:
            logger.info(f"[SQL_BUILDER] Using dynamic compiled SQL: {dynamic_sql}")
            return dynamic_sql

        # Guardrail SQL patterns for common tasks when the catalog compiler cannot plan.
        task_lower = description.lower()
        
        # Account/customer listing tasks
        if any(keyword in task_lower for keyword in ["danh sách", "list", "khách hàng", "account", "customer"]):
            if "business_zone.v_hbl_accounts" in views:
                account_name = self._extract_account_name(prompt)
                if account_name:
                    safe_name = account_name.replace("'", "''")
                    sql = (
                        "SELECT * FROM business_zone.v_hbl_accounts "
                        f"WHERE account_name ILIKE '%{safe_name}%' OR name ILIKE '%{safe_name}%' "
                        "LIMIT 50"
                    )
                else:
                    sql = "SELECT * FROM business_zone.v_hbl_accounts LIMIT 50"
                logger.info(f"[SQL_BUILDER] Using predefined SQL: {sql}")
                return sql
        
        # Contact listing tasks  
        if any(keyword in task_lower for keyword in ["contact", "liên hệ"]):
            if "business_zone.v_hbl_contacts" in views:
                account_name = self._extract_account_name(prompt)
                if account_name:
                    safe_name = account_name.replace("'", "''")
                    sql = (
                        "SELECT * FROM business_zone.v_hbl_contacts "
                        f"WHERE account_name ILIKE '%{safe_name}%' "
                        "LIMIT 50"
                    )
                    logger.info(f"[SQL_BUILDER] Using account-name contact SQL: {sql}")
                    return sql
                account_ids = self._extract_values_from_context(execution_context, ["account_id"])
                if account_ids:
                    quoted_ids = ", ".join(f"'{value}'" for value in account_ids[:50])
                    sql = f"SELECT * FROM business_zone.v_hbl_contacts WHERE account_id IN ({quoted_ids}) LIMIT 50"
                else:
                    sql = "SELECT * FROM business_zone.v_hbl_contacts LIMIT 50"
                logger.info(f"[SQL_BUILDER] Using predefined SQL: {sql}")
                return sql
        
        # Count tasks
        if any(keyword in task_lower for keyword in ["count", "đếm", "số lượng"]):
            if "business_zone.v_hbl_accounts" in views:
                sql = "SELECT COUNT(*) as total_accounts FROM business_zone.v_hbl_accounts"
                logger.info(f"[SQL_BUILDER] Using predefined SQL: {sql}")
                return sql

        # Fallback to LLM generation
        logger.info(f"[SQL_BUILDER] No predefined pattern, using LLM generation")
        context_summary = self._summarize_execution_context(execution_context)
        system_prompt = f"""
        You are a Postgres SQL Expert Agent.
        Your task is to write a syntactically correct and safe PostgreSQL query to satisfy the current execution task.
        
        Original User Request: "{prompt}"
        Current Task: "{description}"
        
        Available Schema Context:
        Views: {views}
        Details: {details}
        Upstream Execution Context:
        {context_summary}
        
        IMPORTANT: 
        - Return ONLY the raw SQL query. Do not wrap in markdown or add explanations.
        - Use simple SELECT statements, avoid complex JOINs unless necessary.
        - Prefer single table queries over multi-table JOINs.
        """
        
        try:
            logger.info(f"[SQL_BUILDER] Calling LLM to generate SQL")
            llm_result = generate_structured_output(system_prompt, SQLOutput)
            sql = llm_result.sql.replace('```sql', '').replace('```', '').strip()
            logger.info(f"[SQL_BUILDER] Generated SQL: {sql}")
            return sql
        except Exception as e:
            logger.error(f"[SQL_BUILDER] SQL generation error: {e}")
            target = views[0] if views else "business_zone.v_hbl_accounts"
            if "count" in description.lower() or "aggregate" in description.lower():
                fallback_sql = f"SELECT COUNT(*) AS count FROM {target}"
            else:
                fallback_sql = f"SELECT * FROM {target} LIMIT 10"
            logger.info(f"[SQL_BUILDER] Using fallback SQL: {fallback_sql}")
            return fallback_sql

    def _topological_sort(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        remaining = {task.get("task_id"): task for task in tasks if task.get("task_id")}
        ordered: List[Dict[str, Any]] = []
        resolved: set[str] = set()

        while remaining:
            progressed = False
            for task_id, task in list(remaining.items()):
                dependencies = set(task.get("depends_on", []))
                if dependencies.issubset(resolved):
                    ordered.append(task)
                    resolved.add(task_id)
                    remaining.pop(task_id)
                    progressed = True
            if not progressed:
                ordered.extend(remaining.values())
                break
        return ordered

    def _extract_values_from_context(
        self,
        execution_context: Dict[str, Any],
        candidate_keys: List[str],
    ) -> List[str]:
        values: list[str] = []
        for context_value in execution_context.values():
            if not isinstance(context_value, dict):
                continue
            result = context_value.get("result", {})
            rows = result.get("rows", []) if isinstance(result, dict) else []
            for row in rows:
                if not isinstance(row, dict):
                    continue
                for key in candidate_keys:
                    value = row.get(key)
                    if value is not None:
                        values.append(str(value).replace("'", "''"))
        return list(dict.fromkeys(values))

    def _summarize_execution_context(self, execution_context: Dict[str, Any]) -> str:
        if not execution_context:
            return "No upstream task results."
        summary: list[str] = []
        for key, value in execution_context.items():
            if not isinstance(value, dict) or "result" not in value:
                continue
            result = value.get("result") or {}
            count = result.get("count") if isinstance(result, dict) else None
            rows = result.get("rows", []) if isinstance(result, dict) else []
            sample = rows[:3] if isinstance(rows, list) else []
            summary.append(f"{key}: count={count}, sample_rows={sample}")
        return "\n".join(summary) or "No upstream query rows."

    def _synthesize_task_result(
        self,
        task: Dict[str, Any],
        execution_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        upstream = {
            key: value
            for key, value in execution_context.items()
            if isinstance(value, dict) and "result" in value
        }
        return {
            "summary": task.get("description"),
            "upstream_task_ids": list(upstream.keys()),
            "count": len(upstream),
            "rows": [],
        }

    def _extract_account_name(self, prompt: str) -> str | None:
        patterns = [
            r"account\s+([A-Z][A-Za-z0-9&.,' -]{2,80})",
            r"tài khoản\s+([A-Z][A-Za-z0-9&.,' -]{2,80})",
            r"khách hàng\s+([A-Z][A-Za-z0-9&.,' -]{2,80})",
        ]
        for pattern in patterns:
            match = re.search(pattern, prompt)
            if match:
                value = match.group(1).strip(" .,'\"")
                value = re.split(r",|\bcùng\b|\bvà\b|\bwith\b|\band\b", value, maxsplit=1, flags=re.IGNORECASE)[0]
                return value.strip(" .,'\"") or None
        return None

    def _build_dynamic_sql(self, prompt: str, description: str) -> str | None:
        try:
            query_plan = self.dynamic_planner.build_plan(prompt, description)
            if query_plan is None:
                return None
            return self.query_compiler.compile(query_plan)
        except Exception as exc:
            logger.warning("[SQL_BUILDER] Dynamic compiler skipped: %s", exc)
            return None

