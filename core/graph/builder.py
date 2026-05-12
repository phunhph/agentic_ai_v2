from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from core.graph.state import AgentState

from core.agents.ingest_agent import run_ingest_agent
from core.tools.context_monitor import get_context_monitor
from core.agents.learning_agent import find_semantic_cache, run_learning_agent

def ingest_node(state: AgentState):
    print("--- Ingesting (AI) ---")
    query = state.get("query", "")
    thread_id = state.get("thread_id", "default")
    
    # Phase 10: Resolve coreferences using context monitor
    context_monitor = get_context_monitor(thread_id)
    resolved_query = context_monitor.resolve_coreferences(query)
    
    if resolved_query != query:
        print(f"[Context] Resolved: {query} → {resolved_query}")
    
    # Phase 9: Semantic Cache check
    print("--- Checking Semantic Cache ---")
    cache_hit = find_semantic_cache(resolved_query)
    if cache_hit:
        print(f"--- [Cache Hit] Similarity: {cache_hit['similarity']:.2f} ---")
        return {
            "intent": "CACHE_HIT",
            "query_clean": resolved_query,
            "cached_sql": cache_hit["sql"],
            "thread_id": thread_id,
            "trace_log": [f"🧠 [Cache] Tìm thấy pattern tương tự ({cache_hit['similarity']:.2f}). Bỏ qua bước lập luận."],
            "trace_details": [{
                "node": "Cache",
                "input": {"query": resolved_query},
                "output": cache_hit
            }]
        }

    # Extract entities for context
    entities_detected = context_monitor.extract_entities(resolved_query)
    
    # Khởi tạo trạng thái cho Phase 7
    retry_count = 0
    error = None
    
    # Gọi AI Agent thực tế với resolved query
    analysis = run_ingest_agent(resolved_query)
    
    # Kiểm tra bảo mật từ AI
    if analysis.get("security_status") in ["DANGEROUS", "PROBING"]:
        return {
            "intent": "SECURITY_VIOLATION",
            "retry_count": 0,
            "error": "Truy vấn bị chặn bởi lớp bảo mật IngestAgent.",
            "trace_log": ["🛑 [Ingest] Phát hiện vi phạm bảo mật hoặc thăm dò hệ thống."],
            "trace_details": [{
                "node": "Ingest",
                "input": {"query": query, "resolved_query": resolved_query},
                "output": analysis
            }]
        }

    return {
        "intent": analysis.get("intent", "REPORT_QUERY"),
        "query_clean": analysis.get("refined_query", resolved_query),
        "thread_id": thread_id,
        "entities_detected": entities_detected,
        "context_monitor": context_monitor,
        "retry_count": 0,
        "error": None,
        "trace_log": [f"[Ingest] AI đã phân tích: {analysis.get('reasoning')}"],
        "trace_details": [{
            "node": "Ingest",
            "input": {"query": query},
            "output": analysis
        }]
    }

from core.agents.reasoning_agent import run_reasoning_agent

def reasoning_node(state: AgentState):
    print("--- Reasoning (AI) ---")
    
    # Lấy dữ liệu từ Ingest step
    ingest_output = {}
    if state.get("trace_details"):
        for step in state["trace_details"]:
            if step.get("node") == "Ingest":
                ingest_output = step.get("output", {})
                break
    
    query_clean = state.get("query_clean", state.get("query", ""))
    entities = ingest_output.get("entities", {})
    existing_trace_log = state.get("trace_log", [])
    existing_trace_details = state.get("trace_details", [])
    
    # Gọi AI Reasoning
    analysis = run_reasoning_agent(query_clean, entities)
    
    return {
        "trace_log": existing_trace_log + [f"[Reasoning] AI đã lập luận: {analysis.get('thought_process', '')[:100]}..."],
        "trace_details": existing_trace_details + [{
            "node": "Reasoning",
            "input": {"query": query_clean, "entities": entities},
            "output": analysis
        }]
    }

from core.agents.planning_agent import run_planning_agent

def planning_node(state: AgentState):
    print("--- Planning (AI) ---")
    
    # Lấy dữ liệu từ Reasoning step
    reasoning_output = {}
    if state.get("trace_details"):
        for step in state["trace_details"]:
            if step.get("node") == "Reasoning":
                reasoning_output = step.get("output", {})
                break
    
    logic_steps = reasoning_output.get("logic_steps", [])
    required_tables = reasoning_output.get("required_tables", [])
    
    # Lấy lỗi cũ nếu có (Phase 7: Recursive Planning)
    previous_error = state.get("error")
    current_retry = state.get("retry_count", 0)
    
    # Gọi AI Planning (có kèm context lỗi nếu là retry)
    plan_data = run_planning_agent(logic_steps, required_tables, previous_error=previous_error)
    existing_trace_log = state.get("trace_log", [])
    existing_trace_details = state.get("trace_details", [])
    
    new_retry_count = current_retry + 1 if previous_error else current_retry
    
    return {
        "plan": plan_data.get("tasks", []),
        "retry_count": new_retry_count,
        "error": None, # Reset error sau khi đã lập lại kế hoạch
        "trace_log": existing_trace_log + [f"[Planning] AI đã lập kế hoạch: {plan_data.get('plan_name', '')}" + (f" (Retry #{new_retry_count})" if previous_error else "")],
        "trace_details": existing_trace_details + [{
            "node": "Planning",
            "input": {"logic_steps": logic_steps, "tables": required_tables, "previous_error": previous_error},
            "output": plan_data
        }]
    }

from core.tools.db_tools import db_query_tool
from core.tools.result_formatter import format_results, create_answer

from core.agents.execution_agent import run_execution_agent

def execution_node(state: AgentState):
    print("--- Execution ---")
    
    plan = state.get("plan", [])
    query_clean = state.get("query_clean", state.get("query", ""))
    cached_sql = state.get("cached_sql")
    existing_trace_log = state.get("trace_log", [])
    existing_trace_details = state.get("trace_details", [])
    
    # 1. Lấy SQL từ Cache hoặc Sinh từ Plan
    if cached_sql:
        print("--- Using Cached SQL ---")
        sql = cached_sql
        explanation = "Reused from semantic cache"
    else:
        print("--- Generating SQL (AI) ---")
        execution_data = run_execution_agent(plan, query_clean)
        sql = execution_data.get("sql")
        explanation = execution_data.get("explanation", "")
    
    if not sql:
        return {
            "error": "Không thể tạo mã SQL hợp lệ.",
            "trace_log": existing_trace_log + ["⚠️ [Execution] Lỗi: Không có SQL được tạo ra."],
            "trace_details": existing_trace_details + [{
                "node": "Execution",
                "input": {"plan": plan, "cached": bool(cached_sql)},
                "output": {"status": "error"}
            }]
        }
    
    # 2. Thực thi thông qua Tool an toàn
    result = db_query_tool(sql)
    existing_trace_log = state.get("trace_log", [])
    existing_trace_details = state.get("trace_details", [])
    
    if result["status"] == "success":
        # 3. Format kết quả cho người dùng
        db_results = result.get("results", [])
        formatted_results = format_results(db_results, query_clean)
        user_answer = create_answer(query_clean, formatted_results, sql)
        
        validation = None
        schema_validation = None
        context_monitor = state.get("context_monitor")
        if context_monitor:
            validation = context_monitor.validate_logic(query_clean, db_results, sql)
            schema_validation = context_monitor.validate_schema_usage(sql)
            if validation and not validation.get("is_valid", True):
                user_answer += "\n\n⚠️ Chú ý: Kết quả có thể không hoàn toàn chính xác. " + \
                    "Vui lòng kiểm tra lại các trường dữ liệu và câu truy vấn."

        return {
            "sql_query": sql,
            "results": db_results,
            "formatted_results": formatted_results,
            "user_answer": user_answer,
            "validation": validation,
            "schema_validation": schema_validation,
            "error": None,
            "trace_log": existing_trace_log + [f"[Execution] SQL đã chạy thành công: {execution_data.get('explanation', '')[:100] if not cached_sql else 'Reused from cache'}..."],
            "trace_details": existing_trace_details + [{
                "node": "Execution",
                "input": {"sql": sql, "plan": plan},
                "output": {
                    "status": "success",
                    "rows": result.get("row_count", 0),
                    "explanation": execution_data.get("explanation"),
                    "validation": validation,
                    "schema_validation": schema_validation
                }
            }]
        }
    else:
        # Trường hợp bị chặn bởi Security hoặc lỗi DB (Kích hoạt Self-healing)
        error_msg = result.get("message", "Unknown Error")
        return {
            "sql_query": sql,
            "error": error_msg,
            "results": [],
            "formatted_results": {"status": "error", "message": error_msg},
            "user_answer": f"⚠️ Lỗi: {error_msg}",
            "trace_log": existing_trace_log + [f"[Execution] ⚠️ LỖI TRUY VẤN: {error_msg}"],
            "trace_details": existing_trace_details + [{
                "node": "Execution",
                "input": {"sql": sql},
                "output": {"status": "error", "reason": error_msg}
            }]
        }

def learning_node(state: AgentState):
    print("--- Learning (AI) ---")
    query = state.get("query_clean")
    sql = state.get("sql_query")
    results = state.get("results", [])
    existing_trace_log = state.get("trace_log", [])
    existing_trace_details = state.get("trace_details", [])
    
    if not query or not sql:
        return {
            "trace_log": existing_trace_log + ["[Learning] Bỏ qua vì thiếu thông tin query/sql."]
        }

    # Thực hiện học từ query thành công
    learning_result = run_learning_agent(
        query=query,
        sql_generated=sql,
        success=True,
        results_count=len(results)
    )
    
    msg = learning_result.get("message", "Đã cập nhật query pattern.")
    
    # Merge trace data thay vì replace
    return {
        "trace_log": existing_trace_log + [f"🧠 [Learning] {msg}"],
        "trace_details": existing_trace_details + [{
            "node": "Learning",
            "input": {"query": query, "results_count": len(results)},
            "output": learning_result
        }]
    }

def should_continue(state: AgentState):
    if state.get("intent") == "SECURITY_VIOLATION":
        return "end"
    if state.get("intent") == "CACHE_HIT":
        return "execute"
    return "continue"

def should_retry(state: AgentState):
    # Nếu có lỗi và chưa vượt quá 3 lần thử lại (Phase 7)
    if state.get("error") and state.get("retry_count", 0) < 3:
        print(f"--- Self-Healing: Trở lại bước Planning (Lần {state.get('retry_count')}) ---")
        return "retry"
    return "end"

def build_graph():
    # Configure checkpointer for session persistence
    checkpointer = MemorySaver()
    
    builder = StateGraph(AgentState)
    
    builder.add_node("ingest", ingest_node)
    builder.add_node("reasoning", reasoning_node)
    builder.add_node("planning", planning_node)
    builder.add_node("execution", execution_node)
    builder.add_node("learning", learning_node)
    
    builder.add_edge(START, "ingest")
    
    # Conditional route after Ingest
    builder.add_conditional_edges(
        "ingest",
        should_continue,
        {
            "continue": "reasoning",
            "execute": "execution",
            "end": END
        }
    )
    
    builder.add_edge("reasoning", "planning")
    builder.add_edge("planning", "execution")
    
    # Loop back logic after Execution (Phase 7)
    builder.add_conditional_edges(
        "execution",
        should_retry,
        {
            "retry": "planning",
            "end": "learning"
        }
    )
    
    builder.add_edge("learning", END)
    
    return builder.compile(checkpointer=checkpointer)

# Compile the graph
graph = build_graph()
