from __future__ import annotations
from typing import Any

COMMON_SCHEMA = {
    "accounts": "business_zone.v_hbl_accounts",
    "contacts": "business_zone.v_hbl_contacts",
    "embeddings": "knowledge_zone.agent_embeddings",
    "logs": "audit_zone.agent_logs",
}

KEYWORD_TABLE_MAP: dict[str, str] = {
    "account": "accounts",
    "contact": "contacts",
    "customer": "accounts",
    "lead": "contacts",
    "embedding": "embeddings",
    "log": "logs",
    "audit": "logs",
    "trace": "logs",
}


class SemanticSchemaRetriever:
    def retrieve_relevant(self, prompt: str) -> dict[str, Any]:
        prompt_lower = prompt.lower()
        matches = {key: view for keyword, key in KEYWORD_TABLE_MAP.items() if keyword in prompt_lower for view in [COMMON_SCHEMA[key]]}
        if not matches:
            matches = {
                "accounts": COMMON_SCHEMA["accounts"],
                "contacts": COMMON_SCHEMA["contacts"],
            }
        return {
            "views": list(dict.fromkeys(matches.values())),
            "details": [f"Using semantic view {view}" for view in list(dict.fromkeys(matches.values()))],
        }
