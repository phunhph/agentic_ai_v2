from __future__ import annotations
import os
import re
from typing import Any

from .model_config import ALLOWED_TOOL_NAMES

SECRET_KEYS = [
    "OPENAI_API_KEY",
    "GEMINI_API_KEY",
    "GROQ_API_KEY",
    "OPENROUTER_API_KEY",
    "DB_PASSWORD",
    "LANGSMITH_API_KEY",
]

SQL_DENY_PATTERNS = [
    r"\bDROP\b",
    r"\bALTER\b",
    r"\bTRUNCATE\b",
    r"\bDELETE\b",
    r"\bCOPY\b",
    r"\b\;\b",
]

ALLOWED_SQL_COMMANDS = ["SELECT", "INSERT", "UPDATE"]


def is_tool_allowed(tool_name: str) -> bool:
    return tool_name in ALLOWED_TOOL_NAMES


def is_sql_safe(sql: str) -> bool:
    sql_upper = sql.upper().strip()
    # Deny patterns (DROP, ALTER, DELETE, etc.)
    for pattern in SQL_DENY_PATTERNS:
        if re.search(pattern, sql_upper):
            return False
    # Allow only SELECT, INSERT, UPDATE
    return any(sql_upper.startswith(cmd) for cmd in ALLOWED_SQL_COMMANDS)


def redact_secrets(payload: dict[str, Any]) -> dict[str, Any]:
    redacted = {}
    for key, value in payload.items():
        if any(secret in key.upper() for secret in SECRET_KEYS):
            redacted[key] = "[REDACTED]"
        else:
            redacted[key] = value
    return redacted
