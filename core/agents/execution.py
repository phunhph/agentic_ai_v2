from core.tools.sql_executor import execute_business_query

def execution_agent_node(state):
    """
    ExecutionAgent: The Doer, SQL Generation & Tool Calling
    """
    print("--- EXECUTING ---")
    
    # Example generated query (in reality would be LLM output)
    sql_query = "SELECT * FROM hbl_account LIMIT 5"
    
    execution_result = execute_business_query(sql_query)
    
    if execution_result["status"] == "success":
        new_trace = f"[Execution] SQL executed successfully. Latency: {execution_result['latency']}ms"
        results = execution_result["results"]
    else:
        new_trace = f"[Execution] ❌ Lỗi: {execution_result['message']}"
        results = "error"
    
    return {
        "results": results,
        "sql_query": sql_query,
        "trace_log": [new_trace],
        "next_step": "learning"
    }
