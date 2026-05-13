from __future__ import annotations
import re
from typing import Any, Dict


class RLSManager:
    def build_filter(self, session_id: str | None) -> str:
        if not session_id:
            return "TRUE"
        return f"tenant_id = '{session_id}'"

    def apply_rls_clause(self, sql: str, session_id: str | None) -> str:
        filter_clause = self.build_filter(session_id)
        trimmed_sql = sql.strip()
        terminator = "" if not trimmed_sql.endswith(";") else ";"
        sql_body = trimmed_sql[:-1] if terminator else trimmed_sql

        if re.search(r"\bWHERE\b", sql_body, flags=re.IGNORECASE):
            return f"{sql_body} AND {filter_clause}{terminator}"

        boundary = re.search(
            r"\b(ORDER\s+BY|LIMIT|OFFSET|FETCH|FOR\s+UPDATE)\b",
            sql_body,
            flags=re.IGNORECASE,
        )
        if boundary:
            insert_pos = boundary.start()
            return f"{sql_body[:insert_pos]} WHERE {filter_clause} {sql_body[insert_pos:]}{terminator}"

        return f"{sql_body} WHERE {filter_clause}{terminator}"
