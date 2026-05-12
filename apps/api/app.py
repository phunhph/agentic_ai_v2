import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from flask import Flask, request, jsonify
import uuid
import time
import os
import psycopg2
from psycopg2.extras import Json
from dotenv import load_dotenv

load_dotenv()

from core.utils.infra.db import db_manager

from core.utils.logic.json_helper import AgenticJSONEncoder

app = Flask(__name__)
# Cấu hình JSON Encoder cho Flask 2.2+ / 3.x
from flask.json.provider import DefaultJSONProvider

class AgenticJSONProvider(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)

from decimal import Decimal
from datetime import datetime, date
app.json = AgenticJSONProvider(app)

def log_to_audit(session_id, node, provider, input_p, output_p, latency):
    """Lưu vết thực thi sử dụng db_manager"""
    usage = {"total_cost": 0.0, "total_tokens": 0} 
    db_manager.log_agent_interaction(session_id, node, input_p, output_p, usage)

from core.graph.builder import graph

from core.utils.infra.security import is_jailbreak_attempt

@app.route("/v1/agent/chat", methods=["POST"])
def chat():
    start_time = time.time()
    data = request.json
    query = data.get("query", "")
    thread_id = data.get("thread_id", str(uuid.uuid4()))

    # Check for Jailbreak or dangerous patterns
    if is_jailbreak_attempt(query):
        return jsonify({
            "status": "security_error",
            "thread_id": thread_id,
            "answer": "⚠️ Cảnh báo bảo mật: Câu hỏi của bạn chứa các từ khóa hoặc mẫu câu bị hạn chế để đảm bảo an toàn hệ thống.",
            "trace_log": ["🛑 [Security] Chặn truy vấn có dấu hiệu Jailbreak/Tấn công."],
            "latency_ms": 0
        })

    # Khởi tạo trạng thái ban đầu
    initial_state = {
        "query": query,
        "thread_id": thread_id,
        "trace_log": []
    }

    # Thực thi LangGraph
    final_state = graph.invoke(initial_state, config={"configurable": {"thread_id": thread_id}})  # type: ignore
    
    trace_log = final_state.get("trace_log", [])
    trace_details = final_state.get("trace_details", [])
    sql_query = final_state.get("sql_query", None)
    results = final_state.get("results", [])
    formatted_results = final_state.get("formatted_results", {})
    user_answer = final_state.get("user_answer", None)
    error = final_state.get("error", None)
    
    # Nếu có lỗi, tạo answer từ error message
    if error and not user_answer:
        user_answer = f"⚠️ Lỗi: {error}"
    
    # Nếu không có user_answer (e.g., incomplete flow), tạo default
    if not user_answer:
        if results:
            user_answer = f"Tìm thấy {len(results)} kết quả."
        else:
            user_answer = f"Xử lý thành công câu hỏi: '{query}'. Hệ thống đã đi qua {len(trace_log)} bước suy luận."

    latency = int((time.time() - start_time) * 1000)
    
    # Log to Database
    log_to_audit(
        thread_id, 
        "LangGraph_Orchestrator", 
        "Multi-Model", 
        {"query": query}, 
        {
            "answer": user_answer, 
            "sql": sql_query, 
            "results": formatted_results,
            "trace_details": trace_details
        }, 
        latency
    )

    return jsonify({
        "status": "success" if not error else "error",
        "thread_id": thread_id,
        "answer": user_answer,
        "results": formatted_results,  # Kết quả formatted cho người dùng
        "trace_log": trace_log,
        "trace_details": trace_details,
        "sql_query": sql_query,
        "error": error,
        "latency_ms": latency
    })

@app.route("/v1/agent/trace/<thread_id>", methods=["GET"])
def get_trace(thread_id):
    # Sau này sẽ lấy từ Database hoặc Cache
    return jsonify({
        "thread_id": thread_id,
        "status": "completed",
        "active_node": "learning",
        "progress": 100
    })

@app.route("/v1/agent/health")
def health():
    return jsonify({"status": "ok", "service": "agentic-crm-api"})

if __name__ == "__main__":
    # Tắt reloader để tránh lỗi [WinError 10038] trên Windows khi chạy qua subprocess
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
