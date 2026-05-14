import json
import logging
import os
import time
from typing import Any, Type, TypeVar

import litellm
from pydantic import BaseModel

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

# Multi-provider configuration for automatic fallback
PROVIDER_MODELS = [
    {
        "name": "groq",
        "model": os.getenv("GROQ_MODEL", "groq/llama-3.3-70b-versatile"),
        "api_key_env": "GROQ_API_KEY",
    },
    {
        "name": "openrouter",
        "model": os.getenv("OPENROUTER_MODEL", "openrouter/openai/gpt-oss-20b:free"),
        "api_key_env": "OPENROUTER_API_KEY",
    },
    {
        "name": "gemini",
        "model": os.getenv("GEMINI_MODEL", "gemini/gemini-flash-latest"),
        "api_key_env": "GEMINI_API_KEY",
    },
]


def get_chat_model() -> str:
    model_key = os.getenv("CHAT_MODEL", "grok").lower()
    return os.getenv(f"{model_key.upper()}_MODEL", "groq/llama-3.3-70b-versatile")


def get_reasoning_model() -> str:
    model_key = os.getenv("REASONING_MODEL", "grok").lower()
    return os.getenv(f"{model_key.upper()}_MODEL", "groq/llama-3.3-70b-versatile")


def get_fallback_model() -> str:
    """Return a fallback LLM model when the primary model is unavailable.
    Reads FALLBACK_MODEL env var, defaults to a cheap OpenAI model.
    """
    return os.getenv("FALLBACK_MODEL", "openai/gpt-3.5-turbo")


class LLMClient:
    """A thin wrapper around LiteLLM that handles model selection, retries
    and intelligent fallback logic across multiple providers (Groq, OpenRouter, Gemini).
    """

    def __init__(self) -> None:
        self.chat_model = get_chat_model()
        self.reasoning_model = get_reasoning_model()
        self.fallback_model = get_fallback_model()
        self.max_retries = int(os.getenv("MAX_RETRY_ATTEMPTS", "3"))
        self.backoff_seconds = int(os.getenv("RETRY_BACKOFF_SECONDS", "2"))
        self.exhausted_providers = set()  # Track which providers hit rate limits
        self.provider_index = 0  # Current provider index for rotation

    def _is_rate_limit_error(self, error: Exception) -> bool:
        """Check if error is a rate limit / quota exceeded error."""
        error_str = str(error).lower()
        error_type = type(error).__name__
        return (
            "ratelimiterror" in error_type
            or "quota" in error_str
            or "429" in error_str
            or "resource_exhausted" in error_str
            or "exceeded" in error_str
        )

    def _get_next_provider_model(self) -> str | None:
        """Get next available provider model, skipping exhausted ones.
        Returns None if all providers are exhausted.
        """
        available_providers = [
            p for p in PROVIDER_MODELS
            if p["name"] not in self.exhausted_providers
            and os.getenv(p["api_key_env"])
        ]
        
        if not available_providers:
            return None
        
        # Cycle through available providers
        self.provider_index = (self.provider_index + 1) % len(available_providers)
        selected = available_providers[self.provider_index]
        logger.info(f"Switching to provider: {selected['name']}")
        return selected["model"]

    def _retry(self, func, *args, **kwargs):
        """Retry with intelligent provider fallback on rate limit errors."""
        attempt = 0
        original_model = kwargs.get("model", self.reasoning_model)
        
        while True:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_msg = str(e)
                is_rate_limit = self._is_rate_limit_error(e)
                
                if is_rate_limit:
                    # Extract provider name from current model
                    current_model = kwargs.get("model", original_model)
                    for provider in PROVIDER_MODELS:
                        if provider["model"] == current_model:
                            self.exhausted_providers.add(provider["name"])
                            logger.warning(
                                f"Provider '{provider['name']}' hit rate limit: {error_msg}"
                            )
                            break
                    
                    # Try next available provider
                    next_model = self._get_next_provider_model()
                    if next_model:
                        kwargs["model"] = next_model
                        continue  # Retry with new provider immediately
                    else:
                        # All providers exhausted
                        exhausted_list = ", ".join(sorted(self.exhausted_providers))
                        error_msg = (
                            f"All LLM providers have exhausted their quotas: {exhausted_list}. "
                            f"Please wait before retrying or upgrade your API plans."
                        )
                        logger.error(error_msg)
                        raise Exception(error_msg) from e
                
                # Non-rate-limit errors: retry with backoff
                attempt += 1
                logger.warning(f"LLM call failed (attempt {attempt}/{self.max_retries}): {e}")
                
                if attempt >= self.max_retries:
                    # Try fallback model
                    if kwargs.get("model") != self.fallback_model:
                        logger.info("Switching to fallback model (openai/gpt-3.5-turbo)")
                        kwargs["model"] = self.fallback_model
                        continue
                    raise
                
                time.sleep(self.backoff_seconds)

    def completion(self, *, model: str | None = None, messages: list[dict[str, Any]], response_format: dict | None = None, temperature: float = 0.1):
        """Run a LiteLLM completion with intelligent provider fallback.
        ``model`` defaults to the reasoning model.
        """
        model = model or self.reasoning_model
        return self._retry(
            litellm.completion,
            model=model,
            messages=messages,
            response_format=response_format,
            temperature=temperature,
        )

    def structured_completion(self, prompt: str, schema: Type[T]) -> T:
        """Generate a structured JSON response adhering to ``schema``.
        Attempts JSON‑object response first; on failure falls back to plain text parsing.
        """
        schema_json = schema.model_json_schema()
        messages = [
            {"role": "system", "content": f"You are an expert AI agent. You must respond ONLY with a valid JSON object that strictly adhers to this schema:\n{json.dumps(schema_json)}"},
            {"role": "user", "content": prompt},
        ]
        try:
            response = self.completion(messages=messages, response_format={"type": "json_object"})
            content = response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM structured call failed: {e}")
            # Fallback without response_format (some models don't support it)
            response = self.completion(messages=messages)
            content = response.choices[0].message.content
        # Extract JSON payload from possible markdown wrappers
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].strip()
        return schema.model_validate_json(content)


def generate_structured_output(prompt: str, schema: Type[T], model: str | None = None) -> T:
    """Thin wrapper kept for backward compatibility.
    Delegates to ``LLMClient.structured_completion``.
    """
    client = LLMClient()
    # If a specific model is forced, temporarily override the client’s reasoning model
    if model:
        client.reasoning_model = model
    return client.structured_completion(prompt, schema)
