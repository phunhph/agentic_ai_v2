from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from core.models import AgentState
import json

from core.agents.ingest_agent import run_ingest_agent
from core.tools.context.context_monitor import get_context_monitor
from core.tools.context.context_compressor import context_compressor_node
from core.agents.learning_agent import find_semantic_cache, run_learning_agent
from core.agents.reflector_agent import run_reflector_agent
from core.agents.reasoning_agent import run_reasoning_agent
from core.agents.planning_agent import run_planning_agent
from core.agents.execution_agent import run_execution_agent
from core.tools.db.db_tools import db_query_tool
from core.tools.formatters.result_formatter import format_results, create_answer

def ingest_node(state: AgentState):
    print("--- Ingesting (AI) ---")
    query = state.get("query", "")
    thread_id = state.get("thread_id", "default")
    
    context_monitor = get_context_monitor(thread_id)
    # Resolve coreferences (Phase 10)
    resolved_query = context_monitor.resolve_coreferences(query)
    
    print("--- Checking Semantic Cache ---")
    cache_hit = find_semantic_cache(resolved_query)
    if cache_hit:
        return {
            "intent": "CACHE_HIT",
            "query_clean": resolved_query,
            "cached_sql": cache_hit["sql"],
            "thread_id": thread_id,
            "trace_log": [f"🧠 [Cache] Tìm thấy pattern tương tự."],
            "trace_details": [{"node": "Cache", "input": {"query": resolved_query}, "output": cache_hit}]
        }

    entities_detected = context_monitor.extract_entities(resolved_query)
    analysis = run_ingest_agent(resolved_query)
    
    if analysis.get("security_status") in ["DANGEROUS", "PROBING"]:
        return {
            "intent": "SECURITY_VIOLATION",
            "error": "Truy vấn bị chặn bởi bảo mật.",
            "trace_log": ["🛑 [Ingest] Vi phạm bảo mật."],
            "trace_details": [{"node": "Ingest", "input": {"query": query}, "output": analysis}]
        }

    return {
        "intent": analysis.get("intent", "REPORT_QUERY"),
        "query_clean": analysis.get("refined_query", resolved_query),
        "thread_id": thread_id,
        "trace_log": [f"[Ingest] AI đã phân tích ý định."],
        "trace_details": [{"node": "Ingest", "input": {"query": query}, "output": analysis}]
    }

def reasoning_node(state: AgentState):
    print("--- Reasoning (AI) ---")
    query_clean = state.get("query_clean", "")
    # Fetch entities from context_monitor
    context_monitor = get_context_monitor(state.get("thread_id", "default"))
    entities = context_monitor.extract_entities(query_clean)
    
    analysis = run_reasoning_agent(query_clean, entities)
    
    return {
        "trace_log": [f"[Reasoning] AI đã lập luận xong."],
        "trace_details": [{"node": "Reasoning", "input": {"query": query_clean}, "output": analysis}]
    }

def planning_node(state: AgentState):
    print("--- Planning (AI) ---")
    reasoning_output = next((s["output"] for s in reversed(state.get("trace_details", [])) if s["node"] == "Reasoning"), {})
    
    logic_steps = reasoning_output.get("logic_steps", [])
    required_tables = reasoning_output.get("required_tables", [])
    
    previous_error = state.get("error")
    reflection_feedback = state.get("reflection_feedback")
    current_retry = state.get("retry_count", 0)
    
    # Kết hợp lỗi DB và feedback từ Reflector (Phase 13)
    combined_feedback = f"{previous_error if previous_error else ''} {reflection_feedback if reflection_feedback else ''}".strip()
    
    plan_data = run_planning_agent(logic_steps, required_tables, previous_error=combined_feedback)
    
    return {
        "plan": plan_data.get("tasks", []),
        "retry_count": current_retry + 1 if combined_feedback else current_retry,
        "error": None,
        "reflection_feedback": None,
        "trace_log": [f"[Planning] AI đã cập nhật kế hoạch."],
        "trace_details": [{"node": "Planning", "input": {"feedback": combined_feedback}, "output": plan_data}]
    }

def execution_node(state: AgentState):
    print("--- Execution ---")
    plan = state.get("plan", [])
    query_clean = state.get("query_clean", "")
    cached_sql = state.get("cached_sql")
    
    if cached_sql:
        sql, explanation = cached_sql, "Reused from cache"
    else:
        execution_data = run_execution_agent(plan, query_clean)
        sql, explanation = execution_data.get("sql"), execution_data.get("explanation", "")
    
    if not sql:
        return {"error": "Không tạo được SQL.", "trace_log": ["⚠️ Lỗi SQL."]}
    
    result = db_query_tool(sql)
    
    if result["status"] == "success":
        db_results = result.get("results", [])
        formatted_results = format_results(db_results, query_clean)
        user_answer = create_answer(query_clean, formatted_results, sql)
        
        context_monitor = get_context_monitor(state.get("thread_id", "default"))
        validation = context_monitor.validate_logic(query_clean, db_results, sql)
        
        return {
            "sql_query": sql, "results": db_results, "formatted_results": formatted_results,
            "user_answer": user_answer, "validation": validation,
            "trace_log": [f"[Execution] SQL thành công."],
            "trace_details": [{"node": "Execution", "output": {"status": "success", "rows": len(db_results)}}]
        }
    else:
        error_msg = result.get("message", "Unknown Error")
        return {
            "error": error_msg,
            "trace_log": [f"[Execution] ⚠️ LỖI: {error_msg}"],
            "trace_details": [{"node": "Execution", "output": {"status": "error", "reason": error_msg}}]
        }

def reflector_node(state: AgentState):
    """Phase 13: Reflector Node"""
    print("--- Reflecting (AI) ---")
    query = state.get("query_clean", "")
    sql = state.get("sql_query", "")
    results = state.get("results", [])
    
    # Lấy reasoning gần nhất từ trace_details
    reasoning_step = next((s for s in reversed(state.get("trace_details", [])) if s["node"] == "Reasoning"), {})
    reasoning_text = json.dumps(reasoning_step.get("output", {}))
    
    reflection = run_reflector_agent(query, sql, results, reasoning_text)
    
    return {
        "reflection_feedback": reflection.get("critique") if not reflection.get("is_correct") else None,
        "trace_log": [f"🔍 [Reflector] {'✅ Hợp lý' if reflection.get('is_correct') else '❌ ' + reflection.get('critique')}"],
        "trace_details": [{"node": "Reflector", "output": reflection}]
    }

def learning_node(state: AgentState):
    print("--- Learning (AI) ---")
    query, sql, results = state.get("query_clean"), state.get("sql_query"), state.get("results", [])
    
    validation = state.get("validation", {})
    if validation and not validation.get("is_valid", True):
        return {"trace_log": ["🧠 [Learning] Bỏ qua do rủi ro hallucination."]}

    learning_result = run_learning_agent(query, sql, True, results_count=len(results))
    return {"trace_log": [f"🧠 [Learning] {learning_result.get('message')}"]}

def should_retry(state: AgentState):
    # Retry nếu lỗi DB HOẶC Reflector phát hiện lỗi logic (Phase 13)
    if (state.get("error") or state.get("reflection_feedback")) and state.get("retry_count", 0) < 3:
        return "retry"
    return "end"

def build_graph():
    checkpointer = MemorySaver()
    builder = StateGraph(AgentState)
    
    builder.add_node("ingest", ingest_node)
    builder.add_node("compressor", context_compressor_node)
    builder.add_node("reasoning", reasoning_node)
    builder.add_node("planning", planning_node)
    builder.add_node("execution", execution_node)
    builder.add_node("reflector", reflector_node)
    builder.add_node("learning", learning_node)
    
    builder.add_edge(START, "ingest")
    builder.add_conditional_edges("ingest", lambda s: "execute" if s.get("intent")=="CACHE_HIT" else ("end" if s.get("intent")=="SECURITY_VIOLATION" else "continue"), {"continue": "compressor", "execute": "execution", "end": END})
    builder.add_edge("compressor", "reasoning")
    builder.add_edge("reasoning", "planning")
    builder.add_edge("planning", "execution")
    builder.add_edge("execution", "reflector")
    builder.add_conditional_edges("reflector", should_retry, {"retry": "planning", "end": "learning"})
    builder.add_edge("learning", END)
    
    return builder.compile(checkpointer=checkpointer)

graph = build_graph()

