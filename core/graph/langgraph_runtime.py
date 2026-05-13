from __future__ import annotations
import time
from typing import Any
from uuid import uuid4

from core.agents.execution_agent import ExecutionAgent
from core.agents.learning_agent import LearningAgent
from core.agents.planning_agent import PlanningAgent
from core.agents.reflector_agent import ReflectorAgent
from core.agents.reasoning_agent import ReasoningAgent
from core.tools.mcp_tool import MCPTool
from core.tools.semantic_schema import SemanticSchemaRetriever
from core.utils.infra.checkpoint import CheckpointStore
from core.utils.infra.metrics import log_metric
from core.utils.logic.context_optimizer import ContextOptimizer
from core.utils.logic.cost_router import CostRouter
from core.utils.logic.rls_manager import RLSManager
from core.utils.logic.retry_policy import RetryPolicy
from core.utils.logic.tenant_guard import TenantGuard


class LangGraphRuntime:
    """A Phase 7-aware LangGraph workflow runtime with optimization and cost routing."""

    def __init__(self) -> None:
        self.schema_retriever = SemanticSchemaRetriever()
        self.mcp_tool = MCPTool()
        self.reasoning_agent = ReasoningAgent()
        self.planning_agent = PlanningAgent()
        self.execution_agent = ExecutionAgent()
        self.reflector_agent = ReflectorAgent()
        self.learning_agent = LearningAgent()
        self.context_optimizer = ContextOptimizer()
        self.cost_router = CostRouter()
        self.tenant_guard = TenantGuard()
        self.rls_manager = RLSManager()
        self.retry_policy = RetryPolicy(max_attempts=3)
        self.store = CheckpointStore()

    def run(
        self,
        thread_id: str,
        prompt: str,
        session_id: str | None = None,
        ingest_state: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if ingest_state is not None:
            prompt = ingest_state.get("normalized_prompt", prompt)

        schema_context = self.schema_retriever.retrieve_relevant(prompt)
        optimized_context = self.context_optimizer.optimize(
            ingest_state=ingest_state,
            schema_context=schema_context,
            thread_id=thread_id,
            session_id=session_id,
        )

        if session_id:
            self.tenant_guard.assign_tenant(session_id, session_id)
        if not self.tenant_guard.validate_access(thread_id, session_id):
            raise PermissionError("Tenant validation failed for the requested session.")

        reasoning_state = self.reasoning_agent.process(
            prompt=prompt,
            thread_id=thread_id,
            session_id=session_id, # type: ignore
            ingest_state=ingest_state,
        )
        planning_state = self.planning_agent.plan(
            reasoning_state=reasoning_state,
            thread_id=thread_id,
            session_id=session_id, # type: ignore
        )

        route = self.cost_router.route(
            prompt,
            complexity=reasoning_state.get("complexity", "standard"),
        )
        selected_model = route["selected"]["model"]
        selected_key = next(
            (key for key, value in self.cost_router.policy.items() if value == route["selected"]),
            "default",
        )
        cost_estimate = self.cost_router.estimate_cost(
            token_count=len(prompt.split()),
            model_key=selected_key,
        )
        log_metric(
            "model_cost_estimate",
            cost_estimate,
            {"session_id": session_id or "anonymous", "complexity": reasoning_state.get("complexity", "standard"), "model_key": selected_key},
        )

        sql_preview = None
        if any(keyword in prompt.lower() for keyword in ["sql", "query", "select", "table"]):
            sql = f"SELECT * FROM {schema_context['views'][0]} LIMIT 5"
            sql_preview = self.mcp_tool.preview(sql)

        execution_input = {
            "views": optimized_context.get("related_views", schema_context.get("views", [])),
            "details": [optimized_context.get("mini_schema", "")],
        }
        execution_state = self.execution_agent.execute(
            planning_state=planning_state,
            thread_id=thread_id,
            session_id=session_id or "",
            schema_context=execution_input,
            prompt=prompt,
        )
        reflection_state = self.reflector_agent.evaluate(
            execution_state=execution_state,
            reasoning_state=reasoning_state,
            planning_state=planning_state,
            thread_id=thread_id,
            session_id=session_id or "",
        )
        retry_attempts: list[dict[str, Any]] = []
        attempt = 1

        while reflection_state.get("status") == "fail":
            error_label = self._classify_execution_error(execution_state, reflection_state)
            retry_exception = RuntimeError(error_label)
            if not self.retry_policy.should_retry(attempt, retry_exception):
                break

            backoff_seconds = self.retry_policy.get_backoff(attempt)
            retry_attempts.append(
                {
                    "attempt": attempt,
                    "error_class": error_label,
                    "backoff_seconds": backoff_seconds,
                }
            )
            time.sleep(min(backoff_seconds, 0.2))
            execution_state = self.execution_agent.execute(
                planning_state=planning_state,
                thread_id=thread_id,
                session_id=session_id or "",
                schema_context=execution_input,
                prompt=prompt,
            )
            reflection_state = self.reflector_agent.evaluate(
                execution_state=execution_state,
                reasoning_state=reasoning_state,
                planning_state=planning_state,
                thread_id=thread_id,
                session_id=session_id or "",
            )
            attempt += 1

        dlq_record = None
        if reflection_state.get("status") == "fail":
            dlq_record = self._move_to_dlq(
                thread_id=thread_id,
                session_id=session_id or "",
                planning_state=planning_state,
                execution_state=execution_state,
                reflection_state=reflection_state,
                retry_attempts=retry_attempts,
            )

        learning_state = self.learning_agent.learn(
            execution_state=execution_state,
            reflection_state=reflection_state,
            reasoning_state=reasoning_state,
            planning_state=planning_state,
            thread_id=thread_id,
            session_id=session_id or "",
        )

        result_text = self._build_result(
            prompt,
            selected_model,
            schema_context,
            reasoning_state,
            planning_state,
            execution_state,
            reflection_state,
            sql_preview,
            retry_attempts,
            dlq_record,
        )
        trace = self._build_trace(
            prompt,
            route,
            schema_context,
            reasoning_state,
            planning_state,
            execution_state,
            reflection_state,
            sql_preview,
            retry_attempts,
            dlq_record,
        )

        return {
            "thread_id": thread_id,
            "session_id": session_id,
            "result": result_text,
            "trace": trace,
            "reasoning_state": reasoning_state,
            "planning_state": planning_state,
            "execution_state": execution_state,
            "reflection_state": reflection_state,
            "learning_state": learning_state,
            "retry_attempts": retry_attempts,
            "dlq_record": dlq_record,
        }

    def _build_result(
        self,
        prompt: str,
        model: str,
        schema_context: dict[str, Any],
        reasoning_state: dict[str, Any],
        planning_state: dict[str, Any],
        execution_state: dict[str, Any],
        reflection_state: dict[str, Any],
        sql_preview: dict[str, Any] | None,
        retry_attempts: list[dict[str, Any]],
        dlq_record: dict[str, Any] | None,
    ) -> str:
        intent = reasoning_state.get("business_intent", "unknown")
        complexity = reasoning_state.get("complexity", "unknown")
        task_count = planning_state.get("task_count", 0)
        execution_status = execution_state.get("status", "unknown")
        reflection_status = reflection_state.get("status", "unknown")
        execution_error = execution_state.get("error") or ""
        reflection_issues = "; ".join(reflection_state.get("issues", []))
        task_results = execution_state.get("tasks", [])
        task_summary = ""
        if task_results:
            first_task = task_results[0]
            if first_task.get("result"):
                row_count = first_task.get("result", {}).get("count")
                if row_count is not None:
                    task_summary = f" First task rows: {row_count}."

        detail_lines = [
            f"Phase 6 response via {model}.",
            f"Business intent: {intent}.",
            f"Complexity: {complexity}.",
            f"Planned {task_count} task(s).",
            f"Execution status: {execution_status}.",
            f"Reflection status: {reflection_status}.",
            f"Relevant semantic views: {', '.join(schema_context.get('views', []))}.",
        ]

        if execution_error:
            detail_lines.append(f"Execution error: {execution_error}.")
        if reflection_issues:
            detail_lines.append(f"Reflection issues: {reflection_issues}.")
        if task_summary:
            detail_lines.append(task_summary)

        completed_tasks = [task for task in execution_state.get("tasks", []) if task.get("status") == "completed"]
        task_rows = [
            f"{task.get('task_id')}: {task.get('result', {}).get('count', 'n/a')} rows"
            for task in completed_tasks
        ]
        if task_rows:
            detail_lines.append(f"Task results: {', '.join(task_rows)}.")

        failed_tasks = [task for task in execution_state.get("tasks", []) if task.get("status") != "completed"]
        if failed_tasks:
            failed_descriptions = [
                f"{task.get('task_id')} ({task.get('status')}): {task.get('error', 'unknown error')}"
                for task in failed_tasks
            ]
            detail_lines.append(f"Failed or rejected tasks: {', '.join(failed_descriptions)}.")

        if retry_attempts:
            detail_lines.append(f"Retry attempts: {len(retry_attempts)}.")
        if dlq_record:
            detail_lines.append(f"DLQ record created: {dlq_record.get('dlq_id')}.")

        detail_lines.append("Execution completed in Phase 6.")
        return "\n".join(detail_lines)

    def _build_trace(
        self,
        prompt: str,
        route: dict[str, Any],
        schema_context: dict[str, Any],
        reasoning_state: dict[str, Any],
        planning_state: dict[str, Any],
        execution_state: dict[str, Any],
        reflection_state: dict[str, Any],
        sql_preview: dict[str, Any] | None,
        retry_attempts: list[dict[str, Any]],
        dlq_record: dict[str, Any] | None,
    ) -> dict[str, Any]:
        steps = [
            {"step": "route", "detail": f"Selected model {route['selected']['model']}"},
            {"step": "reasoning", "detail": f"Business intent {reasoning_state.get('business_intent')}"},
            {"step": "planning", "detail": f"Task count {planning_state.get('task_count')}"},
            {"step": "execution", "detail": f"Execution status {execution_state.get('status')}"},
            {"step": "reflection", "detail": f"Reflection status {reflection_state.get('status')}"},
            {"step": "schema", "detail": "; ".join(schema_context['details'])},
        ]
        if sql_preview is not None:
            steps.append({"step": "mcp", "detail": f"SQL preview allowed={sql_preview['allowed']}"})
        return {
            "trace_id": str(uuid4()),
            "input": prompt,
            "selected_model": route["selected"],
            "fallback": route["fallback"],
            "schema": schema_context,
            "steps": steps,
            "sql_debug": sql_preview,
            "reasoning_state": reasoning_state,
            "planning_state": planning_state,
            "execution_state": execution_state,
            "reflection_state": reflection_state,
            "retry_attempts": retry_attempts,
            "dlq_record": dlq_record,
        }

    def _classify_execution_error(
        self,
        execution_state: dict[str, Any],
        reflection_state: dict[str, Any],
    ) -> str:
        error_text = (execution_state.get("error") or "").lower()
        issues_text = " ".join(reflection_state.get("issues", [])).lower()
        merged = f"{error_text} {issues_text}".strip()

        if any(keyword in merged for keyword in ["timeout", "timed out"]):
            return "timeout"
        if any(keyword in merged for keyword in ["rate limit", "429"]):
            return "rate limit"
        if any(keyword in merged for keyword in ["connection", "network", "temporary"]):
            return "transient"
        if merged:
            return "logic"
        return "unknown"

    def _move_to_dlq(
        self,
        thread_id: str,
        session_id: str,
        planning_state: dict[str, Any],
        execution_state: dict[str, Any],
        reflection_state: dict[str, Any],
        retry_attempts: list[dict[str, Any]],
    ) -> dict[str, Any]:
        dlq_record = {
            "dlq_id": str(uuid4()),
            "thread_id": thread_id,
            "session_id": session_id,
            "plan_id": planning_state.get("plan_id"),
            "execution_id": execution_state.get("execution_id"),
            "reflection_id": reflection_state.get("reflection_id"),
            "reason": execution_state.get("error") or "; ".join(reflection_state.get("issues", [])),
            "retry_attempts": retry_attempts,
            "status": "queued_for_manual_replay",
        }
        self.store.save_state(
            thread_id=thread_id,
            session_id=session_id,
            state_data=dlq_record,
            state_type="dlq",
            previous_checkpoint_id=execution_state.get("execution_id"),
        )
        return dlq_record
