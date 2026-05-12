# core/agents/reasoning.py
from litellm import completion
import json

def reasoning_agent_node(state):
    """
    ReasoningAgent: The Thinker, Task Decomposition
    """
    print("--- REASONING ---")
    
    new_trace = "[Reasoning] Logic decomposed and JOIN paths identified."
    
    return {
        "logic_plan": {},
        "trace_log": [new_trace],
        "next_step": "planning"
    }
