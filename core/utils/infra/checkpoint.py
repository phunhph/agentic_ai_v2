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
    ) -> None:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO audit_zone.checkpoints
                        (thread_id, session_id, checkpoint_data, previous_checkpoint_id, state_type)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (thread_id, session_id, json_dumps(state_data), previous_checkpoint_id, state_type),
                )
            conn.commit()

    def create_checkpoint(
        self,
        thread_id: str,
        session_id: str | None,
        checkpoint_data: Dict[str, Any],
        previous_checkpoint_id: Optional[str] = None,
    ) -> None:
        self.save_state(
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
