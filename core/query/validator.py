from __future__ import annotations

from dataclasses import dataclass

import sqlglot

from core.utils.infra.db import execute_statement


@dataclass
class ValidationResult:
    ok: bool
    stage: str
    message: str = ""
    skipped: bool = False


class DryRunValidator:
    """Validates compiled SQL before real execution.

    The validator performs a parser check locally and, when Postgres is
    reachable, runs EXPLAIN to catch missing columns, invalid joins, and syntax
    errors without executing the query.
    """

    def validate(self, sql: str, tenant_id: str | None = None) -> ValidationResult:
        try:
            parsed = sqlglot.parse_one(sql, read="postgres")
        except Exception as exc:
            return ValidationResult(ok=False, stage="parse", message=str(exc))

        if parsed.key.upper() != "SELECT":
            return ValidationResult(ok=False, stage="policy", message="Only SELECT statements are allowed")

        try:
            execute_statement(f"EXPLAIN {sql}", tenant_id=tenant_id)
        except Exception as exc:
            message = str(exc)
            if self._is_connectivity_error(message):
                return ValidationResult(ok=True, stage="dry_run", message=message, skipped=True)
            return ValidationResult(ok=False, stage="dry_run", message=message)

        return ValidationResult(ok=True, stage="dry_run")

    def _is_connectivity_error(self, message: str) -> bool:
        lowered = message.lower()
        return any(
            token in lowered
            for token in [
                "connection refused",
                "could not connect",
                "connection timed out",
                "server closed the connection",
                "no route to host",
            ]
        )
