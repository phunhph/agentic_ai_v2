from typing import TypedDict, List, Annotated, Dict, Any
import operator

class AgentState(TypedDict):
    # User input
    query: str
    query_clean: str
    
    # Session
    thread_id: str

    # Intent classification
    intent: str

    # BabyAGI execution plan
    plan: List[str]

    # Completed tasks
    steps_completed: List[str]

    # Final SQL generated
    sql_query: str
    cached_sql: str # Phase 9: SQL from semantic cache
    
    # Database results
    results: List

    # Accumulated trace logs (simple strings)
    trace_log: Annotated[List[str], operator.add]
    
    # Structured trace details (In/Out per node)
    trace_details: Annotated[List[dict], operator.add]
    
    # Error handling
    error: str
    retry_count: int
