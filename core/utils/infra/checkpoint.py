from typing import Any, Dict, List, Optional

from core.utils.infra.db import get_connection
from core.utils.infra.json_utils import json_dumps


class CheckpointStore:
    def save_state(
        self,
        thread_id: str,
        session_id: str | None,
        state_data: Dict[str, Any],
        state_type: str = "checkpoint",
        previous_checkpoint_id: Optional[str] = None,
    ) -> str | None:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute(
                        """
                        INSERT INTO audit_zone.checkpoints
                            (thread_id, session_id, tenant_id, checkpoint_data, previous_checkpoint_id, state_type)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        RETURNING id
                        """,
                        (thread_id, session_id, session_id, json_dumps(state_data), previous_checkpoint_id, state_type),
                    )
                    row = cursor.fetchone()
                except Exception:
                    conn.rollback()
                    cursor.execute(
                        """
                        INSERT INTO audit_zone.checkpoints
                            (thread_id, session_id, checkpoint_data, previous_checkpoint_id, state_type)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING id
                        """,
                        (thread_id, session_id, json_dumps(state_data), previous_checkpoint_id, state_type),
                    )
                    row = cursor.fetchone()
            conn.commit()
        return str(row[0]) if row else None

    def create_checkpoint(
        self,
        thread_id: str,
        session_id: str | None,
        checkpoint_data: Dict[str, Any],
        previous_checkpoint_id: Optional[str] = None,
    ) -> str | None:
        return self.save_state(
            thread_id=thread_id,
            session_id=session_id,
            state_data=checkpoint_data,
            state_type="checkpoint",
            previous_checkpoint_id=previous_checkpoint_id,
        )

    def list_checkpoints(self, thread_id: str) -> List[Dict[str, Any]]:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, thread_id, session_id, checkpoint_data, previous_checkpoint_id, state_type, created_at
                    FROM audit_zone.checkpoints
                    WHERE thread_id = %s
                    ORDER BY created_at ASC
                    """,
                    (thread_id,),
                )
                rows = cursor.fetchall()
        return [
            {
                "id": row[0],
                "thread_id": row[1],
                "session_id": row[2],
                "checkpoint_data": row[3],
                "previous_checkpoint_id": row[4],
                "state_type": row[5],
                "created_at": row[6].isoformat() if row[6] else None,
            }
            for row in rows
        ]

    def get_latest_checkpoint(
        self,
        thread_id: str,
        state_type: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        sql = """
            SELECT id, checkpoint_data
            FROM audit_zone.checkpoints
            WHERE thread_id = %s
        """
        params: List[Any] = [thread_id]
        if state_type:
            sql += " AND state_type = %s"
            params.append(state_type)
        sql += " ORDER BY created_at DESC LIMIT 1"

        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, tuple(params))
                row = cursor.fetchone()
        if row:
            return {"id": row[0], "checkpoint_data": row[1]}
        return None

    def list_recent_states(
        self,
        thread_id: str,
        limit: int = 12,
    ) -> List[Dict[str, Any]]:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, thread_id, session_id, checkpoint_data, previous_checkpoint_id, state_type, created_at
                    FROM audit_zone.checkpoints
                    WHERE thread_id = %s
                    ORDER BY created_at DESC
                    LIMIT %s
                    """,
                    (thread_id, limit),
                )
                rows = cursor.fetchall()
        return [
            {
                "id": row[0],
                "thread_id": row[1],
                "session_id": row[2],
                "checkpoint_data": row[3],
                "previous_checkpoint_id": row[4],
                "state_type": row[5],
                "created_at": row[6].isoformat() if row[6] else None,
            }
            for row in rows
        ]

    def build_thread_context(self, thread_id: str, limit: int = 12) -> Dict[str, Any]:
        states = list(reversed(self.list_recent_states(thread_id, limit=limit)))
        latest_by_type: Dict[str, Any] = {}
        timeline: list[dict[str, Any]] = []
        for state in states:
            state_type = state.get("state_type")
            data = state.get("checkpoint_data") or {}
            latest_by_type[state_type] = data
            timeline.append(
                {
                    "state_type": state_type,
                    "created_at": state.get("created_at"),
                    "summary": self._summarize_state(state_type, data),
                }
            )
        return {
            "thread_id": thread_id,
            "latest_by_type": latest_by_type,
            "timeline": timeline,
            "summary": " | ".join(item["summary"] for item in timeline if item.get("summary"))[-1200:],
        }

    def _summarize_state(self, state_type: str | None, data: Dict[str, Any]) -> str:
        if state_type == "checkpoint":
            return f"user asked: {data.get('normalized_prompt') or data.get('prompt') or ''}".strip()
        if state_type == "reasoning":
            return f"intent: {data.get('business_intent')} complexity: {data.get('complexity')}"
        if state_type == "planning":
            return f"planned {data.get('task_count')} tasks: {data.get('summary')}"
        if state_type == "execution":
            tasks = data.get("tasks", [])
            return f"execution {data.get('status')} with {len(tasks)} tasks"
        if state_type == "reflection":
            return f"reflection {data.get('status')}: {', '.join(data.get('issues', [])[:2])}"
        if state_type == "learning":
            return f"learning {data.get('status')}"
        return f"{state_type}: stored"
