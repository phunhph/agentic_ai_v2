from __future__ import annotations
import re
from typing import Any, Dict


class RLSManager:
    def build_filter(self, session_id: str | None) -> str:
        if not session_id:
            return "TRUE"
        escaped = session_id.replace("'", "''")
        return f"tenant_id = '{escaped}'"

    def generate_rls_policy(self, table_name: str, tenant_id: str | None = None) -> str:
        tenant_expr = (
            f"'{tenant_id.replace(chr(39), chr(39) + chr(39))}'"
            if tenant_id
            else "current_setting('app.tenant_id', true)"
        )
        policy_name = table_name.replace(".", "_").replace('"', "").replace("'", "")
        return (
            f"ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY;\n"
            f"CREATE POLICY {policy_name}_tenant_isolation ON {table_name} "
            f"USING (tenant_id = {tenant_expr});"
        )

    def apply_rls_clause(self, sql: str, session_id: str | None) -> str:
        filter_clause = self.build_filter(session_id)
        trimmed_sql = sql.strip()
        terminator = "" if not trimmed_sql.endswith(";") else ";"
        sql_body = trimmed_sql[:-1] if terminator else trimmed_sql

        boundary = re.search(
            r"\b(ORDER\s+BY|LIMIT|OFFSET|FETCH|FOR\s+UPDATE)\b",
            sql_body,
            flags=re.IGNORECASE,
        )
        if boundary:
            insert_pos = boundary.start()
            if re.search(r"\bWHERE\b", sql_body[:insert_pos], flags=re.IGNORECASE):
                before_boundary = sql_body[:insert_pos].rstrip()
                where_match = re.search(r"\bWHERE\b", before_boundary, flags=re.IGNORECASE)
                if where_match:
                    prefix = before_boundary[: where_match.end()]
                    condition = before_boundary[where_match.end() :].strip()
                    return f"{prefix} ({condition}) AND {filter_clause} {sql_body[insert_pos:]}{terminator}"
            return f"{sql_body[:insert_pos]} WHERE {filter_clause} {sql_body[insert_pos:]}{terminator}"

        where_match = re.search(r"\bWHERE\b", sql_body, flags=re.IGNORECASE)
        if where_match:
            prefix = sql_body[: where_match.end()]
            condition = sql_body[where_match.end() :].strip()
            return f"{prefix} ({condition}) AND {filter_clause}{terminator}"

        return f"{sql_body} WHERE {filter_clause}{terminator}"
