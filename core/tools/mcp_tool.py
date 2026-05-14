from __future__ import annotations

import logging
from typing import Any, Dict, List

import sqlglot
from pydantic import BaseModel

from .security import is_sql_safe, is_tool_allowed, redact_secrets
from core.utils.infra.audit import log_agent_event
from core.utils.infra.db import query
from core.utils.logic.rls_manager import RLSManager

logger = logging.getLogger(__name__)


class MCPResult(BaseModel):
    rows: List[Dict[str, Any]]
    count: int

    def dict(self, *args, **kwargs):  # for compatibility with older code
        return super().model_dump(*args, **kwargs)


class MCPPreviewResponse(BaseModel):
    sql: str
    allowed: bool

    def dict(self, *args, **kwargs):
        return super().model_dump(*args, **kwargs)


class MCPTool:
    """Tool for executing user‑provided SQL with RLS enforcement and audit logging.

    The tool validates SQL using ``sqlglot`` to ensure syntactic safety and then
    applies row‑level‑security (RLS) clauses before execution.
    """

    def __init__(self) -> None:
        self.name = "mcp_execute"
        self.rls_manager = RLSManager()

    def _validate_sql(self, sql: str) -> str:
        """Parse and normalise the SQL statement with ``sqlglot``.

        Raises ``ValueError`` if parsing fails or the statement is not a SELECT/INSERT/UPDATE.
        """
        try:
            parsed = sqlglot.parse_one(sql, read="postgres")
        except Exception as exc:
            logger.error(f"SQL parsing failed: {exc}")
            raise ValueError("SQL statement is not syntactically valid.")
        # Only allow SELECT (DQL), INSERT, UPDATE (DML) – block DELETE, DROP, ALTER, etc.
        if parsed.key not in {"SELECT", "INSERT", "UPDATE"}:
            raise ValueError("Only SELECT, INSERT, and UPDATE statements are allowed. DELETE, DROP, and ALTER are not permitted.")
        # Return the formatted SQL string (standardises whitespace)
        return parsed.sql(dialect="postgres")

    def execute(self, thread_id: str, sql: str, session_id: str | None = None) -> Dict[str, Any]:
        """Execute a safe, RLS‑aware SQL statement and return a JSON‑serialisable result.

        The result adheres to the ``MCPResult`` model. Audit events are logged before and after execution.
        """
        if not is_tool_allowed(self.name):
            raise PermissionError("MCP execution tool is not allowed by policy.")

        # First, ensure the caller‑provided SQL passes our custom safety checks.
        if not is_sql_safe(sql):
            raise ValueError("SQL statement is not permitted for execution.")

        # Use sqlglot for strict parsing / normalisation.
        safe_sql = self._validate_sql(sql)

        # Apply RLS clause based on the session context.
        safe_sql = self.rls_manager.apply_rls_clause(safe_sql, session_id)

        # Log request.
        log_agent_event(thread_id, "mcp_request", {"sql": safe_sql, "session_id": session_id})

        rows = query(safe_sql)
        result = MCPResult(rows=rows, count=len(rows))

        # Log response, redacting any secrets.
        log_agent_event(thread_id, "mcp_response", redact_secrets(result.dict()))
        return result.dict()

    def preview(self, sql: str) -> Dict[str, Any]:
        """Return a lightweight preview indicating whether the SQL is allowed.

        The response follows ``MCPPreviewResponse``.
        """
        allowed = is_sql_safe(sql)
        preview = MCPPreviewResponse(sql=sql, allowed=allowed)
        return preview.dict()
