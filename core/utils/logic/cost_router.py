from __future__ import annotations
import time
import logging
from typing import Any, Dict

from core.tools.model_config import MODEL_POLICY

logger = logging.getLogger(__name__)

class CostRouter:
    _total_cost_spent = 0.0
    _consecutive_failures = 0
    _circuit_open_until = 0.0

    def __init__(self, daily_budget: float = 1.0, max_failures: int = 3, reset_timeout: int = 60) -> None:
        self.policy = MODEL_POLICY
        self.daily_budget = daily_budget
        self.max_failures = max_failures
        self.reset_timeout = reset_timeout

    def route(self, prompt: str, complexity: str = "standard") -> Dict[str, Any]:
        prompt_lower = prompt.lower()
        
        # Check budget
        if self.__class__._total_cost_spent >= self.daily_budget:
            logger.warning("Daily budget exceeded. Enforcing graceful degradation.")
            return {"selected": self.policy["default"], "fallback": [], "degraded": True}

        # Check circuit breaker
        if time.time() < self.__class__._circuit_open_until:
            logger.warning("Circuit breaker is OPEN. Fast failing or returning degraded model.")
            return {"selected": self.policy["default"], "fallback": [], "degraded": True}

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

        return {"selected": selected, "fallback": fallback, "degraded": False}

    def record_cost(self, cost: float) -> None:
        self.__class__._total_cost_spent += cost

    def record_success(self) -> None:
        self.__class__._consecutive_failures = 0
        self.__class__._circuit_open_until = 0.0

    def record_failure(self) -> None:
        self.__class__._consecutive_failures += 1
        if self.__class__._consecutive_failures >= self.max_failures:
            logger.error(f"Circuit breaker TRIPPED! Opening circuit for {self.reset_timeout}s.")
            self.__class__._circuit_open_until = time.time() + self.reset_timeout

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

