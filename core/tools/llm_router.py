from __future__ import annotations
from typing import Any

from .model_config import FALLBACK_ORDER, MODEL_POLICY


class LLMRouter:
    def __init__(self) -> None:
        self.policy = MODEL_POLICY
        self.fallback_order = FALLBACK_ORDER

    def route(self, prompt: str) -> dict[str, Any]:
        prompt_lower = prompt.lower()
        if any(token in prompt_lower for token in ["sql", "query", "database", "schema"]):
            selected = self.policy["reasoning"]
        elif any(token in prompt_lower for token in ["analysis", "summarize", "plan"]):
            selected = self.policy["high_accuracy"]
        else:
            selected = self.policy["default"]

        return {
            "selected": selected,
            "fallback": [self.policy[name] for name in self.fallback_order if self.policy[name] != selected],
        }

    def choose_model(self, prompt: str) -> str:
        route = self.route(prompt)
        return route["selected"]["model"]
