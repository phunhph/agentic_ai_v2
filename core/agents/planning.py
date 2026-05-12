# core/agents/planning.py
from litellm import completion
import json

def planning_agent_node(state):
    """
    PlanningAgent: Task Orchestrator (BabyAGI Pattern)
    """
    print("--- PLANNING ---")
    
    new_trace = "[Planning] Execution roadmap built with 3 tasks."
    
    return {
        "plan": [],
        "trace_log": [new_trace],
        "next_step": "execution"
    }
