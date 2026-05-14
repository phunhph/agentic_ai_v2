from __future__ import annotations
import json
import logging
import os
import sys
import time
import uuid
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, request

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

# Configure logging to show all debug and info messages
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Console output
    ]
)

from core.agents.ingest_agent import IngestAgent
from core.graph.langgraph_runtime import LangGraphRuntime
from core.utils.infra.audit import log_agent_event
from core.utils.infra.checkpoint import CheckpointStore
from core.utils.infra.db import get_connection, query
from core.utils.infra.metrics import log_metric

app = Flask(__name__)

# Flask's logger
app.logger.setLevel(logging.INFO)

runtime = LangGraphRuntime()
ingest_agent = IngestAgent()
checkpoint_store = CheckpointStore()


@app.route("/health", methods=["GET"])
def health() -> tuple[dict[str, str], int]:
    return {"status": "ok"}, 200


@app.route("/ready", methods=["GET"])
def ready() -> tuple[dict[str, str], int]:
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
        return {"status": "ready"}, 200
    except Exception as exc:
        return {"status": "error", "message": str(exc)}, 503


@app.route("/v1/agent/chat", methods=["POST"])
def chat() -> tuple[dict[str, Any], int]:
    thread_id = str(uuid.uuid4())
    try:
        payload = request.get_json(force=True, silent=True)
        if not payload:
            return {"error": "JSON payload required"}, 400

        prompt = payload.get("prompt")
        if not prompt:
            return {"error": "Field 'prompt' is required."}, 400

        thread_id = payload.get("thread_id") or thread_id
        session_id = payload.get("session_id")
        resume_thread_id = payload.get("resume_thread_id")

        request_payload = {
            "thread_id": thread_id,
            "session_id": session_id,
            "prompt": prompt,
            "resume_thread_id": resume_thread_id,
        }

        previous_state = None
        if resume_thread_id:
            previous_state = checkpoint_store.get_latest_checkpoint(resume_thread_id, state_type="checkpoint")
            if previous_state:
                previous_state = previous_state["checkpoint_data"]

        ingest_state = ingest_agent.process(
            prompt=prompt,
            thread_id=thread_id,
            session_id=session_id,
            previous_state=previous_state,
            metadata={"resume_thread_id": resume_thread_id} if resume_thread_id else None,
        )

        log_agent_event(thread_id, "request", request_payload)
        log_agent_event(thread_id, "ingest", ingest_state)

        start_time = time.time()
        response = runtime.run(
            thread_id=thread_id,
            prompt=prompt,
            session_id=session_id,
            ingest_state=ingest_state,
        )
        duration_ms = (time.time() - start_time) * 1000.0
        log_metric("api_response_latency_ms", duration_ms, {"session_id": session_id or "anonymous"})
        log_agent_event(thread_id, "response", response)

        return {
            "thread_id": thread_id,
            "session_id": session_id,
            "ingest_state": ingest_state,
            "reasoning_state": response.get("reasoning_state"),
            "planning_state": response.get("planning_state"),
            "execution_state": response.get("execution_state"),
            "reflection_state": response.get("reflection_state"),
            "learning_state": response.get("learning_state"),
            "result": response["result"],
            "trace": response["trace"],
        }, 200
    except Exception as exc:
        app.logger.exception("Agent chat request failed")
        try:
            log_agent_event(thread_id, "error", {"error": str(exc)})
        except Exception:
            app.logger.exception("Failed to write agent error audit log")
        return {"thread_id": thread_id, "error": str(exc)}, 500


@app.route("/v1/agent/trace/<thread_id>", methods=["GET"])
def trace(thread_id: str) -> tuple[dict[str, Any], int]:
    rows = query(
        "SELECT event_type, payload, created_at FROM audit_zone.agent_logs WHERE thread_id = %s ORDER BY created_at",
        (thread_id,),
    )
    return {"thread_id": thread_id, "events": rows}, 200


@app.route("/v1/agent/checkpoints/<thread_id>", methods=["GET"])
def checkpoints(thread_id: str) -> tuple[dict[str, Any], int]:
    entries = checkpoint_store.list_checkpoints(thread_id)
    return {"thread_id": thread_id, "checkpoints": entries}, 200


@app.route("/v1/agent/replay/<thread_id>", methods=["GET"])
def replay(thread_id: str) -> tuple[dict[str, Any], int]:
    latest = checkpoint_store.get_latest_checkpoint(thread_id)
    if not latest:
        return {"thread_id": thread_id, "message": "No checkpoints found."}, 404
    return {
        "thread_id": thread_id,
        "latest_checkpoint": latest,
    }, 200


if __name__ == "__main__":
    port = int(os.getenv("API_PORT", 8000))
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=debug)
