from langgraph.graph import StateGraph, END
from core.graph.state import AgentState
from core.agents.ingest import ingest_agent_node
from core.agents.reasoning import reasoning_agent_node
from core.agents.planning import planning_agent_node
from core.agents.execution import execution_agent_node
from core.agents.learning import learning_agent_node

def build_graph():
    # 1. Initialize Graph
    workflow = StateGraph(AgentState)

    # 2. Add Nodes
    workflow.add_node("ingest", ingest_agent_node)
    workflow.add_node("reasoning", reasoning_agent_node)
    workflow.add_node("planning", planning_agent_node)
    workflow.add_node("execution", execution_agent_node)
    workflow.add_node("learning", learning_agent_node)

    # 3. Define Edges (Static for now, can be conditional for retry)
    workflow.set_entry_point("ingest")
    
    workflow.add_edge("ingest", "reasoning")
    workflow.add_edge("reasoning", "planning")
    workflow.add_edge("planning", "execution")
    
    # Conditional edge for retry logic (example)
    workflow.add_conditional_edges(
        "execution",
        lambda x: "planning" if x.get("retry_count", 0) < 3 and x.get("results") == "error" else "learning",
        {
            "planning": "planning",
            "learning": "learning"
        }
    )
    
    workflow.add_edge("learning", END)

    # 4. Compile
    return workflow.compile()

# Singleton instance
graph = build_graph()
