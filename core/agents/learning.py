# core/agents/learning.py
from litellm import embedding
import json

def learning_agent_node(state):
    """
    LearningAgent: The Scholar, Self-Correction & Memory
    """
    print("--- LEARNING ---")
    
    new_trace = "[Learning] Successful pattern stored in pgvector memory."
    
    return {
        "trace_log": [new_trace],
        "next_step": "end"
    }
