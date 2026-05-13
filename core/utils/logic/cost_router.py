from __future__ import annotations
from typing import Any, Dict

from core.tools.model_config import MODEL_POLICY


class CostRouter:
    def __init__(self) -> None:
        self.policy = MODEL_POLICY

    def route(self, prompt: str, complexity: str = "standard") -> Dict[str, Any]:
        prompt_lower = prompt.lower()

        if complexity == "simple":
            selected = self._select_low_cost_model(prompt_lower)
        elif complexity == "complex":
            selected = self.policy["high_accuracy"]
        else:
            selected = self.policy["reasoning"]

        fallback = [
            self.policy[name]
            for name in ["default", "reasoning", "high_accuracy"]
            if self.policy[name] != selected
        ]

        return {"selected": selected, "fallback": fallback}

    def _select_low_cost_model(self, prompt_lower: str) -> Dict[str, Any]:
        if any(token in prompt_lower for token in ["summarize", "define", "simple", "list"]):
            return self.policy["default"]
        return self.policy["reasoning"]

    def estimate_cost(self, token_count: int, model_key: str) -> float:
        model_rate = {
            "default": 0.0005,
            "reasoning": 0.0010,
            "high_accuracy": 0.0025,
        }
        return model_rate.get(model_key, 0.001) * token_count
