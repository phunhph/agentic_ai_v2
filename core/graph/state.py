from typing import TypedDict, List, Annotated
import operator

class AgentState(TypedDict):
    # User input
    query: str
    
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

    # Database results
    results: List

    # Accumulated trace logs (simple strings)
    trace_log: Annotated[List[str], operator.add]
    
    # Structured trace details (In/Out per node)
    trace_details: Annotated[List[dict], operator.add]
    
    # Error handling
    error: str
