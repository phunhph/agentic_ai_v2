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

from core.utils.db import db_manager

app = Flask(__name__)

def log_to_audit(trace_id, agent_name, provider, input_p, output_p, latency):
    """Lưu vết vào audit_zone.agent_trace_logs sử dụng db_manager"""
    try:
        with db_manager.get_cursor() as cur:
            cur.execute("""
                INSERT INTO audit_zone.agent_trace_logs 
                (trace_id, agent_name, model_provider, input_payload, output_response, latency_ms)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (trace_id, agent_name, provider, Json(input_p), Json(output_p), latency))
    except Exception as e:
        print(f"Audit Log Error: {e}")

from core.graph.builder import graph

from core.utils.security import is_jailbreak_attempt

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
    final_state = graph.invoke(initial_state)  # type: ignore
    
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
    # Chạy trên port 5000 như yêu cầu
    app.run(host="0.0.0.0", port=5000, debug=True)
