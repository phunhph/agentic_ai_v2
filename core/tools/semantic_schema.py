from __future__ import annotations
from typing import Any

from core.query import SchemaCatalog

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
    def __init__(self) -> None:
        self.catalog = SchemaCatalog()

    def retrieve_relevant(self, prompt: str) -> dict[str, Any]:
        prompt_lower = prompt.lower()
        matches = {key: view for keyword, key in KEYWORD_TABLE_MAP.items() if keyword in prompt_lower for view in [COMMON_SCHEMA[key]]}
        if any(token in prompt_lower for token in ["liên quan", "related", "contact", "liên hệ"]):
            matches["accounts"] = COMMON_SCHEMA["accounts"]
            matches["contacts"] = COMMON_SCHEMA["contacts"]
        if not matches:
            matches = {
                "accounts": COMMON_SCHEMA["accounts"],
                "contacts": COMMON_SCHEMA["contacts"],
            }
        views = list(dict.fromkeys(matches.values()))
        relation_cards = [
            relation.compact_card()
            for relation in self.catalog.search_relations(prompt)
            if relation.full_name in views or not views
        ]
        if not relation_cards:
            relation_cards = [relation.compact_card() for relation in self.catalog.search_relations(prompt)]
        return {
            "views": views,
            "details": [f"Using semantic view {view}" for view in views],
            "relation_cards": relation_cards,
        }
