from __future__ import annotations

from typing import Any

from .db import get_connection
from .json_utils import json_dumps


def log_agent_event(thread_id: str, event_type: str, payload: dict[str, Any]) -> None:
    tenant_id = payload.get("tenant_id") or payload.get("session_id")
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    "INSERT INTO audit_zone.agent_logs (thread_id, tenant_id, event_type, payload) VALUES (%s, %s, %s, %s)",
                    (thread_id, tenant_id, event_type, json_dumps(payload)),
                )
            except Exception:
                conn.rollback()
                cur.execute(
                    "INSERT INTO audit_zone.agent_logs (thread_id, event_type, payload) VALUES (%s, %s, %s)",
                    (thread_id, event_type, json_dumps(payload)),
                )
        conn.commit()
