from __future__ import annotations
import json
import uuid
from typing import Any, Dict

from core.utils.infra.db import get_connection
from core.utils.infra.audit import log_agent_event


class LearningAgent:
    def learn(
        self,
        execution_state: Dict[str, Any],
        reflection_state: Dict[str, Any],
        reasoning_state: Dict[str, Any],
        planning_state: Dict[str, Any],
        thread_id: str,
        session_id: str,
    ) -> Dict[str, Any]:
        content = json.dumps(
            {
                "thread_id": thread_id,
                "execution_status": execution_state.get("status"),
                "reflection_status": reflection_state.get("status"),
                "business_intent": reasoning_state.get("business_intent"),
                "task_count": planning_state.get("task_count"),
                "issues": reflection_state.get("issues"),
            }
        )
        source_id = str(uuid.uuid4())
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO knowledge_zone.agent_embeddings (source_schema, source_table, source_id, content, embedding) VALUES (%s, %s, %s, %s, %s)",
                    (
                        "phase_6",
                        "learning_log",
                        source_id,
                        content,
                        None,
                    ),
                )
            conn.commit()

        learning_state = {
            "learning_id": str(uuid.uuid4()),
            "thread_id": thread_id,
            "session_id": session_id,
            "stored_source_id": source_id,
            "status": "recorded",
        }
        log_agent_event(thread_id, "learning", learning_state)
        return learning_state
