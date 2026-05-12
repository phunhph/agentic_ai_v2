from typing import TypedDict, List, Annotated, Dict, Any, Optional
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
    plan: List[Dict[str, Any]] # Changed to list of dicts for more flexibility

    # Completed tasks
    steps_completed: List[str]

    # Final SQL generated
    sql_query: Optional[str]
    cached_sql: Optional[str] # Phase 9: SQL from semantic cache
    
    # Database results
    results: List[Dict[str, Any]]

    # Accumulated trace logs (simple strings)
    trace_log: Annotated[List[str], operator.add]
    
    # Structured trace details (In/Out per node)
    trace_details: Annotated[List[Dict[str, Any]], operator.add]
    
    # Logic Validation (Phase 10)
    validation: Optional[Dict[str, Any]]

    # Reflection Feedback (Phase 13)
    reflection_feedback: Optional[str]

    # Error handling
    error: Optional[str]
    retry_count: int
