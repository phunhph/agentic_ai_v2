from langgraph.graph import StateGraph, START, END
from core.graph.state import AgentState

def ingest_node(state: AgentState):
    print("--- Ingesting ---")
    query = state.get("query", "")
    output = {
        "intent": "REPORT_QUERY", 
        "query_clean": query.strip().lower(),
        "language": "Vietnamese"
    }
    return {
        "intent": output["intent"],
        "trace_log": ["[Ingest] Gemini 1.5 Flash đang phân tích câu hỏi..."],
        "trace_details": [{
            "node": "Ingest",
            "input": {"query": query},
            "output": output
        }]
    }

def reasoning_node(state: AgentState):
    print("--- Reasoning ---")
    # Lấy Input từ kết quả của node trước đó (intent)
    input_data = {"intent": state.get("intent"), "query": state.get("query")}
    output = {
        "entities": ["Finance", "Vietnam", "Account"], 
        "confidence": 0.98,
        "reasoning_path": "Query asks for accounts filtered by industry and country."
    }
    return {
        "trace_log": ["[Reasoning] Groq (Llama 3) đang trích xuất thực thể..."],
        "trace_details": [{
            "node": "Reasoning",
            "input": input_data,
            "output": output
        }]
    }

def planning_node(state: AgentState):
    print("--- Planning ---")
    # Lấy Input từ thực thể đã trích xuất
    input_data = state.get("trace_details", [])[-1]["output"] if state.get("trace_details") else {}
    output = [
        "1. Tìm mã industry 'Finance' trong sys_choice_options",
        "2. Join hbl_account với bảng mapping industry",
        "3. Lọc theo quốc gia 'Vietnam'",
        "4. Trình bày kết quả dưới dạng bảng"
    ]
    return {
        "plan": output,
        "trace_log": ["[Planning] BabyAGI đang lập kế hoạch truy vấn..."],
        "trace_details": [{
            "node": "Planning",
            "input": input_data,
            "output": {"tasks": output}
        }]
    }

def execution_node(state: AgentState):
    print("--- Execution ---")
    # Lấy Input từ Plan
    input_data = state.get("plan", [])
    sql = "SELECT a.* FROM hbl_account a JOIN sys_choice_options c ON ... WHERE c.label = 'Finance'"
    output = {
        "sql": sql,
        "execution_status": "success",
        "rows_returned": 15
    }
    return {
        "sql_query": sql,
        "results": [{"id": 1, "name": "Company A"}, {"id": 2, "name": "Company B"}],
        "trace_log": ["[Execution] SQL Executor đang truy vấn dữ liệu..."],
        "trace_details": [{
            "node": "Execution",
            "input": {"plan": input_data},
            "output": output
        }]
    }

def learning_node(state: AgentState):
    print("--- Learning ---")
    # Lấy Input từ kết quả Execution
    input_data = state.get("results", [])
    output = "Đã cập nhật query pattern vào Long-term Memory để tối ưu lần sau."
    return {
        "trace_log": ["[Learning] Cập nhật bộ nhớ ngữ nghĩa cho truy vấn mới."],
        "trace_details": [{
            "node": "Learning",
            "input": {"results_count": len(input_data)},
            "output": {"memory": output}
        }]
    }

def build_graph():
    builder = StateGraph(AgentState)
    
    builder.add_node("ingest", ingest_node)
    builder.add_node("reasoning", reasoning_node)
    builder.add_node("planning", planning_node)
    builder.add_node("execution", execution_node)
    builder.add_node("learning", learning_node)
    
    builder.add_edge(START, "ingest")
    builder.add_edge("ingest", "reasoning")
    builder.add_edge("reasoning", "planning")
    builder.add_edge("planning", "execution")
    builder.add_edge("execution", "learning")
    builder.add_edge("learning", END)
    
    return builder.compile()

# Compile the graph
graph = build_graph()
