from __future__ import annotations
import json
from typing import Any

from .security import is_sql_safe, is_tool_allowed, redact_secrets
from core.utils.infra.audit import log_agent_event
from core.utils.infra.db import query
from core.utils.logic.rls_manager import RLSManager


class MCPTool:
    def __init__(self) -> None:
        self.name = "mcp_execute"
        self.rls_manager = RLSManager()

    def execute(self, thread_id: str, sql: str, session_id: str | None = None) -> dict[str, Any]:
        if not is_tool_allowed(self.name):
            raise PermissionError("MCP execution tool is not allowed by policy.")

        if not is_sql_safe(sql):
            raise ValueError("SQL statement is not permitted for execution.")

        safe_sql = self.rls_manager.apply_rls_clause(sql, session_id)
        log_agent_event(thread_id, "mcp_request", {"sql": safe_sql, "session_id": session_id})
        rows = query(safe_sql)
        result = {"rows": rows, "count": len(rows)}
        log_agent_event(thread_id, "mcp_response", redact_secrets(result))
        return result

    def preview(self, sql: str) -> dict[str, Any]:
        safe = is_sql_safe(sql)
        return {"sql": sql, "allowed": safe}
