from __future__ import annotations
import json
from typing import Any

from .db import get_connection


def log_agent_event(thread_id: str, event_type: str, payload: dict[str, Any]) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO audit_zone.agent_logs (thread_id, event_type, payload) VALUES (%s, %s, %s)",
                (thread_id, event_type, json.dumps(payload)),
            )
        conn.commit()
