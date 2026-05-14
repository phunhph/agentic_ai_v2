from __future__ import annotations
import os
import re
import logging
from typing import Any

from .model_config import ALLOWED_TOOL_NAMES

logger = logging.getLogger(__name__)

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
    r"\bINSERT\b",
    r"\bUPDATE\b",
    r"\bMERGE\b",
    r"\bGRANT\b",
    r"\bREVOKE\b",
]

ALLOWED_SQL_COMMANDS = ["SELECT"]


def is_tool_allowed(tool_name: str) -> bool:
    return tool_name in ALLOWED_TOOL_NAMES


def is_sql_safe(sql: str) -> bool:
    sql_upper = sql.upper().strip()
    if ";" in sql_upper.rstrip(";"):
        logger.error(f"[SECURITY] SQL Denied - Multiple statements are not allowed | SQL: {sql}")
        return False
    # Deny patterns (DROP, ALTER, DELETE, etc.)
    for pattern in SQL_DENY_PATTERNS:
        if re.search(pattern, sql_upper):
            logger.error(f"[SECURITY] SQL Denied - Pattern matched: {pattern} | SQL: {sql}")
            return False
    # Allow only SELECT, INSERT, UPDATE
    allowed = any(sql_upper.startswith(cmd) for cmd in ALLOWED_SQL_COMMANDS)
    if not allowed:
        logger.error(f"[SECURITY] SQL Denied - Command not allowed | SQL: {sql}")
    return allowed


def redact_secrets(payload: dict[str, Any]) -> dict[str, Any]:
    redacted = {}
    for key, value in payload.items():
        if any(secret in key.upper() for secret in SECRET_KEYS):
            redacted[key] = "[REDACTED]"
        else:
            redacted[key] = value
    return redacted
