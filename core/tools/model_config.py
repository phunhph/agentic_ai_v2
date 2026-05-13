from __future__ import annotations
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")


def _env_model(key: str, default: str) -> str:
    return os.getenv(key, default)


def _map_provider(model_choice: str) -> str:
    normalized = model_choice.lower()
    if normalized in {"grok", "groq"}:
        return "groq"
    if normalized in {"gemini"}:
        return "gemini"
    if normalized in {"openrouter"}:
        return "openrouter"
    return "openai"


GEMINI_MODEL = _env_model("GEMINI_MODEL", "gemini/gemini-flash-latest")
GROQ_MODEL = _env_model("GROQ_MODEL", "groq/llama-3.3-70b-versatile")
OPENROUTER_MODEL = _env_model("OPENROUTER_MODEL", "openrouter/openai/gpt-oss-20b:free")
OPENAI_MODEL = _env_model("OPENAI_MODEL", "gpt-4o")
OPENAI_MINI_MODEL = _env_model("OPENAI_MINI_MODEL", "gpt-4o-mini")

CHAT_MODEL = os.getenv("CHAT_MODEL", "grok").lower()
REASONING_MODEL = os.getenv("REASONING_MODEL", "gemini").lower()
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "openrouter").lower()


def _resolve_model(selection: str) -> str:
    if selection == "gemini":
        return GEMINI_MODEL
    if selection in {"grok", "groq"}:
        return GROQ_MODEL
    if selection == "openrouter":
        return OPENROUTER_MODEL
    if selection == "openai":
        return OPENAI_MODEL
    return selection


MODEL_POLICY = {
    "default": {
        "provider": _map_provider(CHAT_MODEL),
        "model": _resolve_model(CHAT_MODEL),
        "max_tokens": 512,
        "temperature": 0.2,
    },
    "reasoning": {
        "provider": _map_provider(REASONING_MODEL),
        "model": _resolve_model(REASONING_MODEL),
        "max_tokens": 768,
        "temperature": 0.3,
    },
    "high_accuracy": {
        "provider": "openai",
        "model": OPENAI_MODEL,
        "max_tokens": 1024,
        "temperature": 0.1,
    },
}

FALLBACK_ORDER = ["reasoning", "default"]

ALLOWED_TOOL_NAMES = ["mcp_execute", "schema_retrieve", "audit_log"]
