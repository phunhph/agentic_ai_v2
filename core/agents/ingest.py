# core/agents/ingest.py
from litellm import completion
import json

def ingest_agent_node(state):
    """
    IngestAgent: Gatekeeper, Intent Classifier, Entity Extractor
    """
    print("--- INGESTING ---")
    user_input = state["query"]
    
    # Prompt Hardening: Chống injection/jailbreak
    malicious_keywords = ["ignore previous", "system prompt", "drop table", "delete from"]
    if any(keyword in user_input.lower() for keyword in malicious_keywords):
        return {
            "intent": "security_violation",
            "trace_log": ["[Ingest] ⚠️ Chặn hành vi nghi ngờ prompt injection."],
            "next_step": "end"
        }

    # Skeleton logic
    new_trace = "[Ingest] Request validated and intent classified."
    
    return {
        "intent": "query",
        "trace_log": [new_trace],
        "next_step": "reasoning"
    }
